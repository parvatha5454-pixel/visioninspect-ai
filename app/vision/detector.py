"""
Defect detection engine for VisionInspect AI (Milestone 2).

Approach: classical anomaly detection, not deep learning. For each product
category we build a "reference profile" from the MVTec AD 'good' training
images: a pixel-wise mean and std-dev image. A new image is preprocessed
the same way and compared against the reference using a normalized
pixel-difference score. Large deviation from the learned normal appearance
=> higher anomaly score => more likely defective.

This mirrors the project's severity levels (Critical/High/Medium/Low) so
results plug directly into the existing `defects` table.
"""

import json
import os
from pathlib import Path

import numpy as np

from .preprocessing import preprocess_path

ARTIFACTS_DIR = Path("model_artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# Anomaly score (0-100) at/above which a unit is flagged defective
DEFECT_THRESHOLD = 40


def _reference_path(category_name: str) -> Path:
    return ARTIFACTS_DIR / f"{category_name}_reference.npz"


def build_reference(category_name: str, good_image_paths: list[str]) -> dict:
    """
    Computes and saves the mean + std reference image for a category from
    a list of 'good' (non-defective) training image paths.
    """
    stack = np.stack([preprocess_path(p) for p in good_image_paths])
    mean_img = stack.mean(axis=0)
    std_img = stack.std(axis=0) + 1e-6  # avoid divide-by-zero later

    np.savez(_reference_path(category_name), mean=mean_img, std=std_img)

    return {
        "category": category_name,
        "images_used": len(good_image_paths),
    }


def has_reference(category_name: str) -> bool:
    return _reference_path(category_name).exists()


def predict(image_path: str, category_name: str) -> dict:
    """
    Scores a single image against its category's reference profile.
    Returns a dict with result, confidence/anomaly score, and severity —
    ready to be written into the `inspections` / `defects` tables.
    """
    ref_path = _reference_path(category_name)
    if not ref_path.exists():
        raise FileNotFoundError(
            f"No reference profile for category '{category_name}'. "
            f"Run build_references.py first."
        )

    data = np.load(ref_path)
    mean_img, std_img = data["mean"], data["std"]

    test_img = preprocess_path(image_path)

    # z-score style deviation, averaged over the image
    deviation = np.abs(test_img - mean_img) / std_img
    raw_score = float(np.mean(deviation))

    # squash into a stable 0-100 range for storage/display
    anomaly_score = float(min(100, round(raw_score * 20, 2)))

    is_defective = anomaly_score >= DEFECT_THRESHOLD

    if anomaly_score >= 80:
        severity = "critical"
    elif anomaly_score >= 60:
        severity = "high"
    elif anomaly_score >= 40:
        severity = "medium"
    else:
        severity = "low"

    return {
        "result": "defective" if is_defective else "normal",
        "anomaly_score": anomaly_score,
        "severity": severity,
    }
