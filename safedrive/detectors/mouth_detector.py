"""Mouth / yawning detection.

Uses MediaPipe Face Mesh landmarks to compute the Mouth Aspect Ratio (MAR).
"""

from typing import Tuple

from safedrive.constants import MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT


def calculate_mouth_opening(
    landmarks,
    top_idx: int,
    bottom_idx: int,
    left_idx: int,
    right_idx: int,
) -> Tuple[float, float]:
    """Return ``(mar, vertical_distance)`` for the mouth.

    Bug #1 fix: always returns a tuple ``(float, float)`` even when
    ``horizontal_distance`` is zero (returns ``(0.0, 0.0)`` in that case).
    """
    top = landmarks[top_idx]
    bottom = landmarks[bottom_idx]
    left = landmarks[left_idx]
    right = landmarks[right_idx]

    vertical_distance = abs(top.y - bottom.y)
    horizontal_distance = abs(left.x - right.x)

    if horizontal_distance == 0:
        return (0.0, 0.0)

    mar = vertical_distance / horizontal_distance
    return (mar, vertical_distance)


def detect_yawning(
    landmarks,
    mar_threshold: float,
    open_threshold: float,
) -> bool:
    """Return ``True`` when the mouth opening exceeds both thresholds."""
    mar, height = calculate_mouth_opening(
        landmarks,
        MOUTH_INNER_TOP,
        MOUTH_INNER_BOTTOM,
        MOUTH_LEFT,
        MOUTH_RIGHT,
    )
    return mar > mar_threshold and height > open_threshold
