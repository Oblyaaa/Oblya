#!/usr/bin/env python3
"""
Handwriting aging simulator: transforms an input image with handwritten text to mimic age-related handwriting changes.

Features implemented (toggleable):
- Elastic warp for baseline drift and local deformations (mimics tremor, line noncompliance)
- Slant variation implicitly via displacement fields
- Variable pen pressure (stroke thickness variation) via morphology blended with coherent noise
- Incomplete final letters (per-component right-edge fade)
- Optional strikethroughs and smudges
- Paper aging: warming/sepia tone, vignetting, stains/foxing, grain

Input: image file with handwritten text (any common format)
Output: image file with aged handwriting look

Usage:
  python handwriting_aging.py input.jpg output.jpg --severity 0.6 --seed 42 --smudges --strikethroughs

Notes:
- The pipeline removes original ink with inpainting, then re-renders modified strokes onto the reconstructed background.
- Keep severity modest for realism (0.3-0.7). Extreme values are for demonstration only.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter


# ------------------------------- Utilities -----------------------------------


def set_random_seed(seed: int | None) -> np.random.Generator:
    if seed is None:
        seed = random.randrange(0, 2**32 - 1)
    rng = np.random.default_rng(seed)
    return rng


def to_gray(image_bgr: np.ndarray) -> np.ndarray:
    if image_bgr.ndim == 2:
        gray = image_bgr
    else:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return gray


def ensure_uint8(img: np.ndarray) -> np.ndarray:
    img = np.clip(img, 0, 255)
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    return img


def adaptive_text_mask(gray_8u: np.ndarray) -> np.ndarray:
    """Return binary mask (1.0 for ink/foreground, 0.0 for background)."""
    # Adaptive threshold to handle uneven paper background
    thr = cv2.adaptiveThreshold(
        gray_8u, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 10
    )
    mask = (thr > 0).astype(np.float32)
    # Clean small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def inpaint_background(image_bgr: np.ndarray, mask01: np.ndarray) -> np.ndarray:
    """Remove ink using inpainting, approximate clean paper background."""
    mask8 = (mask01 * 255).astype(np.uint8)
    radius = 3
    bg = cv2.inpaint(image_bgr, mask8, radius, cv2.INPAINT_TELEA)
    return bg


def coherent_noise(shape: Tuple[int, int], rng: np.random.Generator, sigma: float) -> np.ndarray:
    """Generate smooth noise in [0, 1] by Gaussian filtering white noise."""
    h, w = shape
    noise = rng.random((h, w), dtype=np.float32)
    noise = gaussian_filter(noise, sigma=sigma, mode="reflect")
    noise -= noise.min()
    m = noise.max()
    if m > 1e-6:
        noise /= m
    return noise.astype(np.float32)


def elastic_displacement_fields(
    h: int,
    w: int,
    rng: np.random.Generator,
    sigma: float,
    alpha: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return dx, dy displacement fields with smooth, low-frequency variations."""
    base_x = coherent_noise((h, w), rng, sigma)
    base_y = coherent_noise((h, w), rng, sigma)
    dx = (base_x * 2.0 - 1.0) * alpha
    dy = (base_y * 2.0 - 1.0) * alpha
    return dx.astype(np.float32), dy.astype(np.float32)


def remap_with_displacement(img: np.ndarray, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    map_x = grid_x + dx
    map_y = grid_y + dy
    return cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def apply_warp(image_bgr: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    # alpha controls amplitude in pixels; sigma controls smoothness of the field
    alpha = max(1.0, severity * 8.0)
    sigma = max(4.0, 12.0 - severity * 6.0)
    dx, dy = elastic_displacement_fields(h, w, rng, sigma=sigma, alpha=alpha)
    warped = remap_with_displacement(image_bgr, dx, dy)
    return warped


def variable_pressure(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    """Blend between eroded and dilated strokes using smooth noise as a proxy for pen pressure."""
    h, w = mask01.shape
    kernel_size = max(1, int(round(1 + severity * 2)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask_u8 = (mask01 * 255).astype(np.uint8)
    dil = cv2.dilate(mask_u8, kernel, iterations=1).astype(np.float32) / 255.0
    ero = cv2.erode(mask_u8, kernel, iterations=1).astype(np.float32) / 255.0
    pressure = coherent_noise((h, w), rng, sigma=max(6.0, 10.0 - severity * 4))
    blended = ero * (1.0 - pressure) + dil * pressure
    blended = np.clip(blended, 0.0, 1.0)
    return blended


def incomplete_endings(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    """Fade rightmost edge of random connected components to mimic undrawn final letters."""
    comp_mask = (mask01 > 0.5).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(comp_mask, connectivity=8)
    out = mask01.copy()
    fade_prob = 0.25 + 0.35 * severity
    fade_strength = 0.3 + 0.5 * severity
    for label in range(1, num_labels):
        if rng.random() > fade_prob:
            continue
        x, y, w, h, area = stats[label]
        if area < 20 or w < 5:
            continue
        roi = out[y : y + h, x : x + w]
        # Normalize x across the bounding box; fade last 20-35% from the right
        xs = np.linspace(0.0, 1.0, w, dtype=np.float32)
        start = 0.65 + 0.1 * rng.random()
        fade = np.clip((xs - start) / max(1e-6, (1.0 - start)), 0.0, 1.0)
        fade = fade ** 1.5
        fade = (1.0 - fade * fade_strength)
        roi *= fade[None, :]
        out[y : y + h, x : x + w] = roi
    return out


def stroke_bleed(mask01: np.ndarray, severity: float) -> np.ndarray:
    """Slight blur/bleed of strokes to mimic ink feathering."""
    sigma = 0.6 + severity * 0.9
    blurred = gaussian_filter(mask01, sigma=sigma)
    return np.clip(blurred, 0.0, 1.0)


def render_strokes(background_bgr: np.ndarray, stroke_alpha: np.ndarray, ink_rgb: Tuple[int, int, int]) -> np.ndarray:
    bg = background_bgr.astype(np.float32) / 255.0
    ink_color = np.array([[list(reversed(ink_rgb))]], dtype=np.float32) / 255.0  # convert RGB -> BGR
    # Expand alpha to 3 channels
    a = np.clip(stroke_alpha[..., None], 0.0, 1.0)
    out = bg * (1.0 - a) + ink_color * a
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return out


def add_strikethroughs(img_bgr: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    h, w = img_bgr.shape[:2]
    count = rng.integers(1, max(2, int(2 + severity * 4)))
    out = img_bgr.copy()
    for _ in range(count):
        y = int(rng.integers(int(h * 0.1), int(h * 0.9)))
        x0 = int(rng.integers(0, int(w * 0.3)))
        x1 = int(rng.integers(int(w * 0.6), w))
        thickness = int(max(1, rng.integers(1, 2 + int(severity * 2))))
        color = (rng.integers(5, 25), rng.integers(5, 25), rng.integers(5, 25))
        cv2.line(out, (x0, y), (x1, y + rng.integers(-3, 4)), color, thickness=thickness, lineType=cv2.LINE_AA)
    return out


def add_smudges(img_bgr: np.ndarray, stroke_alpha: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    """Blurred overlays around strokes to mimic finger smudges or ink transfers."""
    h, w = stroke_alpha.shape
    # Build smudge mask by dilating strokes and multiplying by low-freq noise
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(5 + severity * 8), int(5 + severity * 8)))
    dil = cv2.dilate((stroke_alpha * 255).astype(np.uint8), k, iterations=1) / 255.0
    noise = coherent_noise((h, w), rng, sigma=12.0)
    smudge = np.clip(dil * (0.2 + 0.8 * noise) * (0.15 + 0.35 * severity), 0.0, 1.0)
    blur_ksize = int(9 + severity * 10)
    if blur_ksize % 2 == 0:
        blur_ksize += 1
    smudge_blur = cv2.GaussianBlur(smudge, (blur_ksize, blur_ksize), 0)
    # Darken underlying image slightly where smudge is present
    out = img_bgr.astype(np.float32)
    for c in range(3):
        out[..., c] = out[..., c] * (1.0 - 0.25 * smudge_blur)
    return np.clip(out, 0, 255).astype(np.uint8)


def age_paper(img_bgr: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    out = img_bgr.astype(np.float32) / 255.0
    h, w = out.shape[:2]
    # Warm tone (sepia-like)
    warm = np.array([1.05, 1.0, 0.92], dtype=np.float32)  # BGR multipliers
    out = np.clip(out * warm, 0.0, 1.0)
    # Vignette
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt(((xx - cx) / max(w, 1)) ** 2 + ((yy - cy) / max(h, 1)) ** 2)
    vignette = 1.0 - np.clip(r * (1.2 + severity * 0.8), 0.0, 0.5)
    vignette = vignette ** (1.5 + 1.0 * severity)
    out *= vignette[..., None]
    # Stains/foxing: soft brownish spots
    num_stains = int(severity * 8 + rng.integers(0, 3))
    for _ in range(num_stains):
        cx = int(rng.integers(0, w))
        cy = int(rng.integers(0, h))
        rad = int(max(5, rng.integers(8, 25) + severity * 25))
        y, x = np.ogrid[:h, :w]
        dist2 = (x - cx) ** 2 + (y - cy) ** 2
        sigma2 = (rad * rad) / 2.0
        spot = np.exp(-dist2 / max(1.0, sigma2))
        color = np.array([0.95, 0.90, 0.80], dtype=np.float32)  # slightly brown paper
        for c in range(3):
            out[..., c] = out[..., c] * (1.0 - 0.15 * spot) + color[c] * (0.15 * spot)
    # Paper grain
    grain = coherent_noise((h, w), rng, sigma=3.0)
    out *= (0.96 + 0.08 * (grain - 0.5) * severity)
    return np.clip(out * 255.0, 0, 255).astype(np.uint8)


@dataclass
class PipelineConfig:
    severity: float = 0.6
    seed: int | None = None
    enable_warp: bool = True
    enable_pressure: bool = True
    enable_incomplete: bool = True
    enable_paper: bool = True
    enable_strikethroughs: bool = False
    enable_smudges: bool = False


def age_handwriting_image(input_path: str, output_path: str, config: PipelineConfig) -> None:
    rng = set_random_seed(config.seed)
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Failed to read input image: {input_path}")

    gray = to_gray(img)
    mask = adaptive_text_mask(gray)

    # Estimate background (paper) by removing ink
    background = inpaint_background(img, mask)

    # Optional warp applied to the stroke mask (and slightly to background to keep coherence)
    if config.enable_warp:
        # Warp mask and background with identical fields for consistency
        h, w = mask.shape
        dx, dy = elastic_displacement_fields(h, w, rng, sigma=max(6.0, 12.0 - config.severity * 6.0), alpha=max(1.0, config.severity * 10.0))
        mask = remap_with_displacement(mask, dx, dy)
        background = remap_with_displacement(background, dx, dy)

    # Variable pen pressure (thicker/thinner strokes)
    if config.enable_pressure:
        mask = variable_pressure(mask, config.severity, rng)

    # Incomplete final letters
    if config.enable_incomplete:
        mask = incomplete_endings(mask, config.severity, rng)

    # Bleed
    mask = stroke_bleed(mask, config.severity)

    # Render strokes onto background
    ink_rgb = (20, 20, 20)
    composed = render_strokes(background, mask, ink_rgb)

    # Smudges and strikethroughs operate on composed image
    if config.enable_smudges:
        composed = add_smudges(composed, mask, config.severity, rng)
    if config.enable_strikethroughs:
        composed = add_strikethroughs(composed, config.severity, rng)

    # Paper aging at end for global look
    if config.enable_paper:
        composed = age_paper(composed, config.severity, rng)

    cv2.imwrite(output_path, composed)


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Artificially age handwritten text in an image.")
    p.add_argument("input", help="Path to input image (handwritten text)")
    p.add_argument("output", help="Path to save output image")
    p.add_argument("--severity", type=float, default=0.6, help="Overall effect strength [0..1]")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--no-warp", dest="enable_warp", action="store_false", help="Disable geometric warp")
    p.add_argument("--no-pressure", dest="enable_pressure", action="store_false", help="Disable variable pressure")
    p.add_argument("--no-incomplete", dest="enable_incomplete", action="store_false", help="Disable incomplete endings")
    p.add_argument("--no-paper", dest="enable_paper", action="store_false", help="Disable paper aging")
    p.add_argument("--strikethroughs", dest="enable_strikethroughs", action="store_true", help="Add random strikethrough lines")
    p.add_argument("--smudges", dest="enable_smudges", action="store_true", help="Add smudges around strokes")
    return p


def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()
    args.severity = float(np.clip(args.severity, 0.0, 1.0))
    config = PipelineConfig(
        severity=args.severity,
        seed=args.seed,
        enable_warp=args.enable_warp,
        enable_pressure=args.enable_pressure,
        enable_incomplete=args.enable_incomplete,
        enable_paper=args.enable_paper,
        enable_strikethroughs=args.enable_strikethroughs,
        enable_smudges=args.enable_smudges,
    )
    age_handwriting_image(args.input, args.output, config)


if __name__ == "__main__":
    main()

