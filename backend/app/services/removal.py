"""Pretrained-model image text/object removal pipeline.

Text detection: PaddleOCR PP-OCRv5 mobile detector (CPU-friendly pretrained model).
Inpainting: LaMa (pretrained large-mask inpainting model), running on CPU when no GPU exists.
Object removal accepts an explicit binary mask so users can remove arbitrary objects without
training a segmentation model locally.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter

from ..config import settings


@lru_cache(maxsize=1)
def get_ocr_detector():
    try:
        from paddleocr import TextDetection
    except ImportError as exc:
        raise RuntimeError(
            "Text removal requires PaddleOCR and PaddlePaddle. "
            "Install backend/requirements.txt and the CPU PaddlePaddle wheel."
        ) from exc

    return TextDetection(
        model_name=settings.ocr_model_name,
        device=settings.ocr_device,
    )


@lru_cache(maxsize=1)
def get_lama():
    try:
        from simple_lama_inpainting import SimpleLama
    except ImportError as exc:
        raise RuntimeError(
            "Image removal requires simple-lama-inpainting. "
            "Install backend/requirements.txt."
        ) from exc
    import torch
    device = torch.device("cuda" if settings.removal_device.lower() == "cuda" and torch.cuda.is_available() else "cpu")
    return SimpleLama(device=device)


def _result_dict(result: Any) -> dict[str, Any]:
    if hasattr(result, "json"):
        try:
            value = result.json
            if callable(value):
                value = value()
            if isinstance(value, dict):
                return value.get("res", value)
        except Exception:
            pass
    if isinstance(result, dict):
        return result.get("res", result)
    return {}


def detect_text_regions(path: str, min_score: float = 0.50) -> list[dict[str, Any]]:
    detector = get_ocr_detector()
    outputs = detector.predict(path, batch_size=1)
    regions: list[dict[str, Any]] = []
    for output in outputs:
        data = _result_dict(output)
        polys = data.get("dt_polys") or []
        scores = data.get("dt_scores") or []
        for index, poly in enumerate(polys):
            score = float(scores[index]) if index < len(scores) else 1.0
            if score < min_score:
                continue
            points = [[int(point[0]), int(point[1])] for point in np.asarray(poly).tolist()]
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            regions.append({
                "region_id": f"text-{len(regions)+1}",
                "polygon": points,
                "bbox": {
                    "x": min(xs), "y": min(ys),
                    "width": max(xs) - min(xs),
                    "height": max(ys) - min(ys),
                },
                "confidence": round(score, 4),
            })
    return regions


def _prepare_image(path: str) -> tuple[Image.Image, float]:
    image = Image.open(path).convert("RGB")
    original_w, original_h = image.size
    max_dim = max(1, int(settings.removal_max_dimension))
    scale = min(1.0, max_dim / max(original_w, original_h))
    if scale < 1.0:
        image = image.resize((round(original_w * scale), round(original_h * scale)), Image.Resampling.LANCZOS)
    return image, scale


def _restore_size(image: Image.Image, original_size: tuple[int, int]) -> Image.Image:
    if image.size != original_size:
        return image.resize(original_size, Image.Resampling.LANCZOS)
    return image


def make_text_mask(path: str, regions: list[dict[str, Any]], scale: float) -> Image.Image:
    from PIL import ImageDraw

    with Image.open(path) as source:
        original_size = source.size
    mask = Image.new("L", (
        round(original_size[0] * scale),
        round(original_size[1] * scale),
    ), 0)
    draw = ImageDraw.Draw(mask)
    for region in regions:
        polygon = [(round(x * scale), round(y * scale)) for x, y in region["polygon"]]
        draw.polygon(polygon, fill=255)
    # Slight dilation protects against text-edge remnants while staying local.
    return mask.filter(ImageFilter.MaxFilter(7))


def inpaint(path: str, mask: Image.Image, output_path: str) -> dict[str, Any]:
    original = Image.open(path).convert("RGB")
    original_size = original.size
    work, scale = _prepare_image(path)
    if mask.size != work.size:
        mask = mask.resize(work.size, Image.Resampling.NEAREST)
    result = get_lama()(work, mask.convert("L"))
    result = _restore_size(result.convert("RGB"), original_size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, format="PNG")
    return {
        "model": settings.removal_model,
        "device": "CPU",
        "input_size": list(original_size),
        "working_size": list(work.size),
        "output_path": output_path,
    }


def remove_text(path: str, output_path: str, min_score: float = 0.50) -> dict[str, Any]:
    regions = detect_text_regions(path, min_score=min_score)
    if not regions:
        raise RuntimeError("No text regions were detected with sufficient confidence.")
    _, scale = _prepare_image(path)
    mask = make_text_mask(path, regions, scale)
    meta = inpaint(path, mask, output_path)
    meta.update({"mode": "AUTO_TEXT", "regions": regions, "region_count": len(regions)})
    return meta


def remove_masked_object(path: str, mask_path: str, output_path: str) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    mask = Image.open(mask_path).convert("L")
    if mask.size != image.size:
        mask = mask.resize(image.size, Image.Resampling.NEAREST)
    # Normalize any non-zero user-painted pixels to the inpainting mask contract.
    mask = mask.point(lambda value: 255 if value > 8 else 0)
    meta = inpaint(path, mask, output_path)
    meta.update({"mode": "MANUAL_OBJECT"})
    return meta
