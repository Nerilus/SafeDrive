"""Eye closure detection.

Uses MediaPipe Face Mesh landmarks to compute the vertical distance
between the upper and lower eyelid.
"""

from safedrive.constants import (
    LEFT_EYE_TOP, LEFT_EYE_BOTTOM,
    RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM,
)


def calculate_eye_opening(landmarks, top_idx: int, bottom_idx: int) -> float:
    """Return the vertical distance between two eyelid landmarks.

    Bug #2 fix: removed the unused *image_height* parameter.
    """
    top = landmarks[top_idx]
    bottom = landmarks[bottom_idx]
    return abs(top.y - bottom.y)


def detect_eyes_closed(landmarks, threshold: float) -> bool:
    """Return ``True`` when both eyes are below *threshold*."""
    left = calculate_eye_opening(landmarks, LEFT_EYE_TOP, LEFT_EYE_BOTTOM)
    right = calculate_eye_opening(landmarks, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM)
    return left < threshold and right < threshold
