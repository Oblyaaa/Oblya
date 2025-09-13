#!/usr/bin/env python3
"""
Handwriting aging simulator: transforms an input image with handwritten text to mimic age-related handwriting changes.

Features implemented (toggleable):
- Elastic warp for baseline drift with micro‑tremor (mimics tremor and линия строки)
- Slant variation implicitly via displacement fields
- Variable pen pressure: thickness (morphology) + intensity modulation via distance transform
- Incomplete final letters (per‑component fade along major axis/PCA)
- Ink bleed/feathering with edge‑weighted, noise‑modulated feather

Input: image file with handwritten text (any common format)
Output: image file with aged handwriting look

Usage:
  python handwriting_aging.py input.jpg output.jpg --severity 0.6 --seed 42

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


def inpaint_background(image_bgr: np.ndarray, mask01: np.ndarray, severity: float) -> np.ndarray:
    """Remove ink using inpainting, approximate clean paper background.
    Enlarges the inpaint region based on severity to avoid dark halos."""
    k_size = int(1 + round(2 + severity * 4))
    k_size = max(1, k_size)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    dil = cv2.dilate((mask01 * 255).astype(np.uint8), kernel, iterations=1)
    radius = int(2 + round(2 * severity * 3))
    bg = cv2.inpaint(image_bgr, dil, radius, cv2.INPAINT_TELEA)
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
    """Baseline implementation retained for reference (used internally)."""
    base_x = coherent_noise((h, w), rng, sigma)
    base_y = coherent_noise((h, w), rng, sigma)
    dx = (base_x * 2.0 - 1.0) * alpha
    dy = (base_y * 2.0 - 1.0) * alpha
    return dx.astype(np.float32), dy.astype(np.float32)


def build_warp_fields(h: int, w: int, severity: float, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Combine low-frequency drift, baseline sine drift, and micro-tremor.

    - Low-frequency elastic drift: overall slant/curvature
    - Baseline drift: vertical sine along X, modulated to vary across Y
    - Micro-tremor: small high-frequency jitter
    """
    # Low-frequency drift
    dx_low, dy_low = elastic_displacement_fields(
        h, w, rng, sigma=max(6.0, 12.0 - severity * 5.0), alpha=max(0.5, severity * 6.0)
    )

    # Baseline drift (vertical sine along x)
    grid_x = np.linspace(0.0, 1.0, w, dtype=np.float32)
    phase = float(rng.random() * 2 * math.pi)
    period = 0.25 + float(rng.random()) * 0.35  # fraction of width per cycle
    sine = np.sin((grid_x / max(1e-6, period)) * 2 * math.pi + phase)
    amp = (2.0 + 8.0 * severity)  # pixels
    # Modulate across Y so different lines drift differently
    mod_y = coherent_noise((h, 1), rng, sigma=max(10.0, 18.0 - severity * 6.0)) * 0.7 + 0.3
    dy_base = (sine[None, :] * amp * mod_y).astype(np.float32)
    dx_base = np.zeros_like(dy_base)

    # Micro-tremor (small, high-frequency jitter)
    dx_hi, dy_hi = elastic_displacement_fields(
        h, w, rng, sigma=max(2.0, 4.0 - severity * 1.5), alpha=max(0.2, severity * 1.0)
    )

    dx = dx_low * 0.6 + dx_base * 0.0 + dx_hi * 0.4
    dy = dy_low * 0.5 + dy_base * 0.8 + dy_hi * 0.3
    return dx.astype(np.float32), dy.astype(np.float32)


def remap_with_displacement(img: np.ndarray, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    map_x = grid_x + dx
    map_y = grid_y + dy
    return cv2.remap(img, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)


def apply_warp(image_bgr: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    dx, dy = build_warp_fields(h, w, severity, rng)
    return remap_with_displacement(image_bgr, dx, dy)


def variable_pressure(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    """Thickness + intensity modulation guided by pressure and local thickness.

    - Morphological thinning/ thickening driven by smooth pressure field
    - Alpha/intensity reduced where pressure is low and strokes are thin
    """
    h, w = mask01.shape
    kernel_size = max(1, int(round(1 + severity * 2)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    mask_u8 = (mask01 * 255).astype(np.uint8)
    dil = cv2.dilate(mask_u8, kernel, iterations=1).astype(np.float32) / 255.0
    ero = cv2.erode(mask_u8, kernel, iterations=1).astype(np.float32) / 255.0
    pressure = coherent_noise((h, w), rng, sigma=max(6.0, 10.0 - severity * 4))
    thickness = cv2.distanceTransform((mask_u8 > 0).astype(np.uint8), cv2.DIST_L2, 3)
    if thickness.max() > 0:
        thickness = thickness / thickness.max()
    # Blend geometry
    geom = ero * (1.0 - pressure) + dil * pressure
    geom = np.clip(geom, 0.0, 1.0)
    # Intensity factor: lighter where pressure low and stroke thin
    intensity = 0.6 + 0.4 * pressure  # higher pressure -> darker
    thinness = 1.0 - thickness
    intensity *= (0.8 + 0.2 * thinness)
    out = np.clip(geom * intensity, 0.0, 1.0)
    return out


def incomplete_endings(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    """Fade along the major axis (PCA) on random components to mimic unfinished terminals."""
    comp_mask = (mask01 > 0.5).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(comp_mask, connectivity=8)
    out = mask01.copy()
    fade_prob = 0.3 + 0.4 * severity
    base_start = 0.6 + 0.15 * severity
    strength = 0.35 + 0.5 * severity
    for label in range(1, num_labels):
        if rng.random() > fade_prob:
            continue
        x, y, w, h, area = stats[label]
        if area < 25 or (w < 4 and h < 4):
            continue
        roi_mask = (labels[y : y + h, x : x + w] == label).astype(np.uint8)
        ys, xs = np.nonzero(roi_mask)
        if len(xs) < 10:
            continue
        pts = np.column_stack((xs.astype(np.float32), ys.astype(np.float32)))
        mean = pts.mean(axis=0)
        pts_centered = pts - mean
        # PCA via SVD
        U, S, Vt = np.linalg.svd(pts_centered, full_matrices=False)
        axis = Vt[0]  # principal direction (x,y) in ROI coords
        proj = pts_centered @ axis
        # Choose the positive end as the fading terminal
        proj_min, proj_max = float(proj.min()), float(proj.max())
        if (proj_max - (-proj_min)) < 0:  # not meaningful, fallback
            continue
        # Build fade mask per pixel in ROI
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        grid_pts = np.column_stack(((grid_x - mean[0]).ravel(), (grid_y - mean[1]).ravel()))
        grid_proj = (grid_pts @ axis).reshape(h, w)
        # Normalize to [0,1] using positive side
        pos_max = max(1e-6, grid_proj.max())
        norm = (grid_proj / pos_max) * 0.5 + 0.5  # center ~0.5, positive end -> 1
        start = base_start + 0.05 * float(rng.random())
        fade = np.clip((norm - start) / max(1e-6, (1.0 - start)), 0.0, 1.0)
        fade = fade ** 1.5
        fade = (1.0 - fade * strength)
        roi_alpha = out[y : y + h, x : x + w]
        roi_alpha = roi_alpha * fade * (roi_mask.astype(np.float32)) + roi_alpha * (1.0 - roi_mask)
        out[y : y + h, x : x + w] = roi_alpha
    return out


def stroke_bleed(mask01: np.ndarray, severity: float) -> np.ndarray:
    """Edge-weighted, noise-modulated feathering to mimic ink bleed/feather.

    Strength concentrated near stroke edges; interior preserved.
    """
    mask = np.clip(mask01, 0.0, 1.0)
    mask_u8 = (mask * 255).astype(np.uint8)
    eroded = cv2.erode(mask_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
    edge = (mask_u8.astype(np.int16) - eroded.astype(np.int16)).clip(0, 255).astype(np.uint8)
    edge = edge.astype(np.float32) / 255.0
    # Blur edge to get a soft halo
    sigma = 0.8 + severity * 1.2
    soft_edge = gaussian_filter(edge, sigma=sigma)
    soft_edge = np.clip(soft_edge, 0.0, 1.0)
    # Modulate with mid-frequency noise so bleed is uneven
    noise = coherent_noise(mask.shape, np.random.default_rng(), sigma=8.0)
    bleed = soft_edge * (0.2 + 0.6 * severity) * (0.6 + 0.4 * noise)
    out = np.clip(mask + bleed, 0.0, 1.0)
    return out


def render_strokes(background_bgr: np.ndarray, stroke_alpha: np.ndarray, ink_rgb: Tuple[int, int, int]) -> np.ndarray:
    bg = background_bgr.astype(np.float32) / 255.0
    ink_color = np.array([[list(reversed(ink_rgb))]], dtype=np.float32) / 255.0  # convert RGB -> BGR
    # Expand alpha to 3 channels
    a = np.clip(stroke_alpha[..., None], 0.0, 1.0)
    out = bg * (1.0 - a) + ink_color * a
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return out


# Removed: add_strikethroughs, add_smudges, age_paper (per user request)


@dataclass
class PipelineConfig:
    severity: float = 0.6
    seed: int | None = None
    enable_warp: bool = True
    enable_pressure: bool = True
    enable_incomplete: bool = True


def age_handwriting_image(input_path: str, output_path: str, config: PipelineConfig) -> None:
    rng = set_random_seed(config.seed)
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Failed to read input image: {input_path}")

    gray = to_gray(img)
    mask = adaptive_text_mask(gray)

    # Estimate background (paper) by removing ink (severity-aware)
    background = inpaint_background(img, mask, config.severity)

    # Optional warp applied to the stroke mask (and slightly to background to keep coherence)
    if config.enable_warp:
        # Warp mask and background with identical fields for consistency
        h, w = mask.shape
        dx, dy = build_warp_fields(h, w, config.severity, rng)
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

    # Note: Paper aging, smudges, and strikethroughs were removed by request

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
    # Paper aging, smudges, strikethroughs removed per request
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
    )
    age_handwriting_image(args.input, args.output, config)


if __name__ == "__main__":
    main()

