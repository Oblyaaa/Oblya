from __future__ import annotations
import argparse
import math
import random
from dataclasses import dataclass
from typing import Tuple
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.restoration import inpaint_biharmonic

def set_random_seed(seed: int | None) -> np.random.Generator:
    if seed is None:
        seed = random.randrange(0, 2**32 - 1)
    rng = np.random.default_rng(seed)
    return rng

def to_gray(image_bgr: np.ndarray) -> np.ndarray:
    if image_bgr.ndim == 2:
        return image_bgr
    else:
        return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

def ensure_uint8(img: np.ndarray) -> np.ndarray:
    img = np.clip(img, 0, 255)
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    return img

def adaptive_text_mask(gray_8u: np.ndarray) -> np.ndarray:
    thr = cv2.adaptiveThreshold(
        gray_8u, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 35, 10
    )
    mask = (thr > 0).astype(np.float32)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask

def inpaint_background(image_bgr: np.ndarray, mask01: np.ndarray, severity: float) -> np.ndarray:
    k_size = int(1 + round(2 + severity * 8)) 
    k_size = max(1, k_size)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    dil = cv2.dilate((mask01 * 255).astype(np.uint8), kernel, iterations=1)
    
    radius = int(2 + round(2 * severity * 6)) 
    
    
    bg = cv2.inpaint(image_bgr, dil, radius, cv2.INPAINT_NS)
    
    return bg

def coherent_noise(shape: Tuple[int, int], rng: np.random.Generator, sigma: float) -> np.ndarray:
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
    base_x = coherent_noise((h, w), rng, sigma)
    base_y = coherent_noise((h, w), rng, sigma)
    dx = (base_x * 2.0 - 1.0) * alpha
    dy = (base_y * 2.0 - 1.0) * alpha
    return dx.astype(np.float32), dy.astype(np.float32)

def build_warp_fields(h: int, w: int, severity: float, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    dx_low, dy_low = elastic_displacement_fields(
        h, w, rng, sigma=max(6.0, 12.0 - severity * 5.0), alpha=max(0.5, severity * 6.0)
    )
    grid_x = np.linspace(0.0, 1.0, w, dtype=np.float32)
    phase = float(rng.random() * 2 * math.pi)
    period = 0.25 + float(rng.random()) * 0.35
    sine = np.sin((grid_x / max(1e-6, period)) * 2 * math.pi + phase)
    amp = (2.0 + 8.0 * severity)
    mod_y = coherent_noise((h, 1), rng, sigma=max(10.0, 18.0 - severity * 6.0)) * 0.7 + 0.3
    dy_base = (sine[None, :] * amp * mod_y).astype(np.float32)
    dx_base = np.zeros_like(dy_base)
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

def variable_pressure(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
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
    geom = ero * (1.0 - pressure) + dil * pressure
    geom = np.clip(geom, 0.0, 1.0)
    thinness = 1.0 - thickness
    intensity = (0.85 + 0.15 * thinness)
    out = np.clip(geom * intensity, 0.0, 1.0)
    return out

def incomplete_endings(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
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
        _, _, Vt = np.linalg.svd(pts_centered, full_matrices=False)
        axis = Vt[0]
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        grid_pts = np.column_stack(((grid_x - mean[0]).ravel(), (grid_y - mean[1]).ravel()))
        grid_proj = (grid_pts @ axis).reshape(h, w)
        pos_max = max(1e-6, grid_proj.max())
        norm = (grid_proj / pos_max) * 0.5 + 0.5
        start = base_start + 0.05 * float(rng.random())
        fade = np.clip((norm - start) / max(1e-6, (1.0 - start)), 0.0, 1.0)
        fade = fade ** 1.5
        fade = (1.0 - fade * strength)
        min_f = 0.10 + 0.10 * (1.0 - severity)
        fade = fade * (1.0 - min_f) + min_f
        roi_alpha = out[y : y + h, x : x + w]
        roi_alpha = roi_alpha * fade * (roi_mask.astype(np.float32)) + roi_alpha * (1.0 - roi_mask)
        out[y : y + h, x : x + w] = roi_alpha
    return out

"""def stroke_bleed(mask01: np.ndarray, severity: float, rng: np.random.Generator) -> np.ndarray:
    mask = np.clip(mask01, 0.0, 1.0)
    mask_u8 = (mask * 255).astype(np.uint8)
    eroded = cv2.erode(mask_u8, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=1)
    edge = (mask_u8.astype(np.int16) - eroded.astype(np.int16)).clip(0, 255).astype(np.uint8)
    edge = edge.astype(np.float32) / 255.0
    sigma = 0.8 + severity * 1.2
    soft_edge = gaussian_filter(edge, sigma=sigma)
    soft_edge = np.clip(soft_edge, 0.0, 1.0)
    noise = coherent_noise(mask.shape, rng, sigma=8.0)
    bleed = soft_edge * (0.2 + 0.6 * severity) * (0.6 + 0.4 * noise)
    out = np.clip(mask + bleed, 0.0, 1.0)
    return out"""

def compose_scaled_darkening(
    original_bgr: np.ndarray,
    background_bgr: np.ndarray,
    base_alpha: np.ndarray,
    modified_alpha: np.ndarray,
    readability_floor: float = 0.08,
) -> np.ndarray:
    eps = 1e-6
    orig = original_bgr.astype(np.float32) / 255.0
    bg = background_bgr.astype(np.float32) / 255.0
    bg_safe = np.maximum(bg, eps)
    s = 1.0 - (orig / bg_safe)
    s = np.clip(s, 0.0, 1.0)
    base = np.clip(base_alpha, 0.0, 1.0)
    mod = np.clip(modified_alpha, 0.0, 1.0)
    r = mod / (base + eps)
    r = np.clip(r, readability_floor, 1.8)
    s_prime = s * r[..., None]
    s_prime = np.clip(s_prime, 0.0, 1.0)
    base_mask = (base > 0.1).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    gate = cv2.dilate(base_mask, k, iterations=1).astype(bool) | (mod > 0.05)
    gate = gate.astype(np.float32)[..., None]
    out = bg * (1.0 - s_prime) * gate + bg * (1.0 - gate)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    return out

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
    background = inpaint_background(img, mask, config.severity)
    if config.enable_warp:
        h, w = mask.shape
        dx, dy = build_warp_fields(h, w, config.severity, rng)
        mask = remap_with_displacement(mask, dx, dy)
    base_alpha = cv2.GaussianBlur(np.clip(mask, 0.0, 1.0), (0, 0), sigmaX=0.8, sigmaY=0.8)
    if config.enable_pressure:
        mask = variable_pressure(mask, config.severity, rng)
    if config.enable_incomplete:
        mask = incomplete_endings(mask, config.severity, rng)
    # mask = stroke_bleed(mask, config.severity, rng) Эти пятна — добавленный эффект «старения бумаги». Пока не очень хорошо.
    composed = compose_scaled_darkening(img, background, base_alpha, mask, readability_floor=0.06 + 0.06 * (1.0 - config.severity))
    cv2.imwrite(output_path, composed)

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Artificially age handwritten text in an image.")
    p.add_argument("input", help="Path to input image (handwritten text)")
    p.add_argument("output", help="Path to save output image")
    p.add_argument("--severity", type=float, default=0.6, help="Overall effect strength [0..1]")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--no-warp", dest="enable_warp", action="store_false", help="Disable geometric warp (baseline drift & tremor)")
    p.add_argument("--no-pressure", dest="enable_pressure", action="store_false", help="Disable variable pressure")
    p.add_argument("--no-incomplete", dest="enable_incomplete", action="store_false", help="Disable incomplete endings")
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
