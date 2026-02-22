"""Head position / rotation detection.

Uses MediaPipe Face Mesh landmarks around the ears, temples, forehead, chin
and nose to estimate horizontal rotation and vertical tilt.
"""

from typing import Dict, Optional

from safedrive.constants import (
    NOSE_TIP, LEFT_EAR, RIGHT_EAR,
    FOREHEAD, CHIN, LEFT_TEMPLE, RIGHT_TEMPLE,
)


def check_head_position(
    landmarks,
    rotation_threshold: float,
    tilt_threshold: float,
) -> Dict[str, object]:
    """Return a dict describing the head state.

    Keys:
        turned (bool), tilted (bool),
        direction_h (str | None), direction_v (str | None)
    """
    nose = landmarks[NOSE_TIP]
    left_ear = landmarks[LEFT_EAR]
    right_ear = landmarks[RIGHT_EAR]
    forehead = landmarks[FOREHEAD]
    chin = landmarks[CHIN]
    left_temple = landmarks[LEFT_TEMPLE]
    right_temple = landmarks[RIGHT_TEMPLE]

    # Horizontal rotation
    ear_diff = abs(left_ear.x - right_ear.x)
    temple_diff = abs(left_temple.x - right_temple.x)
    rotation = (ear_diff + temple_diff) / 2

    # Vertical tilt
    vertical_angle = abs(forehead.y - chin.y)

    head_state: Dict[str, object] = {
        "turned": False,
        "tilted": False,
        "direction_h": None,
        "direction_v": None,
    }

    if rotation > rotation_threshold:
        head_state["turned"] = True
        head_state["direction_h"] = "gauche" if left_ear.x > right_ear.x else "droite"

    if vertical_angle > tilt_threshold:
        head_state["tilted"] = True
        head_state["direction_v"] = "bas" if nose.y > (forehead.y + chin.y) / 2 else "haut"

    return head_state
