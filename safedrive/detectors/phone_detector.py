"""Phone-usage detection (heuristic).

Detects whether a hand is likely holding a phone based on finger-tip
proximity and alignment.  This is a rough heuristic — it can produce
false positives when the hand is in a similar posture without a phone.
"""

import numpy as np


def detect_phone_usage(hand_landmarks, image_height: int, image_width: int) -> bool:
    """Return ``True`` when finger tips are close and aligned.

    Parameters
    ----------
    hand_landmarks
        A MediaPipe ``NormalizedLandmarkList`` for a single hand.
    image_height, image_width
        Frame dimensions in pixels (used to convert normalised coords).
    """
    if not hand_landmarks:
        return False

    lm = hand_landmarks.landmark
    thumb = np.array([lm[4].x * image_width, lm[4].y * image_height])
    index = np.array([lm[8].x * image_width, lm[8].y * image_height])
    middle = np.array([lm[12].x * image_width, lm[12].y * image_height])
    ring = np.array([lm[16].x * image_width, lm[16].y * image_height])
    pinky = np.array([lm[20].x * image_width, lm[20].y * image_height])

    distances = [
        np.linalg.norm(thumb - index),
        np.linalg.norm(index - middle),
        np.linalg.norm(middle - ring),
        np.linalg.norm(ring - pinky),
    ]

    avg_distance = np.mean(distances)
    max_distance = np.max(distances)

    fingers_close = avg_distance < image_width * 0.15
    fingers_aligned = max_distance < image_width * 0.25

    return bool(fingers_close and fingers_aligned)
