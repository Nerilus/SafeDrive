from tests.conftest import make_landmark
from safedrive.constants import (
    NOSE_TIP, LEFT_EAR, RIGHT_EAR,
    FOREHEAD, CHIN, LEFT_TEMPLE, RIGHT_TEMPLE,
)
from safedrive.detectors.head_detector import check_head_position


class TestCheckHeadPosition:
    def _set_neutral(self, lm):
        """Configure landmarks for a neutral, forward-facing head."""
        lm[NOSE_TIP] = make_landmark(x=0.5, y=0.5)
        lm[LEFT_EAR] = make_landmark(x=0.55, y=0.5)
        lm[RIGHT_EAR] = make_landmark(x=0.45, y=0.5)
        lm[FOREHEAD] = make_landmark(x=0.5, y=0.47)
        lm[CHIN] = make_landmark(x=0.5, y=0.53)
        lm[LEFT_TEMPLE] = make_landmark(x=0.55, y=0.48)
        lm[RIGHT_TEMPLE] = make_landmark(x=0.45, y=0.48)

    def test_neutral_position(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        state = check_head_position(fake_landmarks, rotation_threshold=0.2, tilt_threshold=0.1)
        assert state["turned"] is False
        assert state["tilted"] is False
        assert state["direction_h"] is None
        assert state["direction_v"] is None

    def test_turned_left(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        # Large horizontal spread -> turned
        fake_landmarks[LEFT_EAR] = make_landmark(x=0.9, y=0.5)
        fake_landmarks[RIGHT_EAR] = make_landmark(x=0.1, y=0.5)
        fake_landmarks[LEFT_TEMPLE] = make_landmark(x=0.85, y=0.45)
        fake_landmarks[RIGHT_TEMPLE] = make_landmark(x=0.15, y=0.45)
        state = check_head_position(fake_landmarks, rotation_threshold=0.2, tilt_threshold=0.1)
        assert state["turned"] is True
        assert state["direction_h"] == "gauche"

    def test_turned_right(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        fake_landmarks[LEFT_EAR] = make_landmark(x=0.1, y=0.5)
        fake_landmarks[RIGHT_EAR] = make_landmark(x=0.9, y=0.5)
        fake_landmarks[LEFT_TEMPLE] = make_landmark(x=0.15, y=0.45)
        fake_landmarks[RIGHT_TEMPLE] = make_landmark(x=0.85, y=0.45)
        state = check_head_position(fake_landmarks, rotation_threshold=0.2, tilt_threshold=0.1)
        assert state["turned"] is True
        assert state["direction_h"] == "droite"

    def test_tilted_down(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        # Keep rotation small
        fake_landmarks[LEFT_EAR] = make_landmark(x=0.55, y=0.5)
        fake_landmarks[RIGHT_EAR] = make_landmark(x=0.45, y=0.5)
        fake_landmarks[LEFT_TEMPLE] = make_landmark(x=0.55, y=0.45)
        fake_landmarks[RIGHT_TEMPLE] = make_landmark(x=0.45, y=0.45)
        # Large vertical spread -> tilted
        fake_landmarks[FOREHEAD] = make_landmark(x=0.5, y=0.1)
        fake_landmarks[CHIN] = make_landmark(x=0.5, y=0.9)
        fake_landmarks[NOSE_TIP] = make_landmark(x=0.5, y=0.6)
        state = check_head_position(fake_landmarks, rotation_threshold=0.2, tilt_threshold=0.1)
        assert state["tilted"] is True
        assert state["direction_v"] == "bas"

    def test_tilted_up(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        fake_landmarks[LEFT_EAR] = make_landmark(x=0.55, y=0.5)
        fake_landmarks[RIGHT_EAR] = make_landmark(x=0.45, y=0.5)
        fake_landmarks[LEFT_TEMPLE] = make_landmark(x=0.55, y=0.45)
        fake_landmarks[RIGHT_TEMPLE] = make_landmark(x=0.45, y=0.45)
        fake_landmarks[FOREHEAD] = make_landmark(x=0.5, y=0.1)
        fake_landmarks[CHIN] = make_landmark(x=0.5, y=0.9)
        fake_landmarks[NOSE_TIP] = make_landmark(x=0.5, y=0.4)
        state = check_head_position(fake_landmarks, rotation_threshold=0.2, tilt_threshold=0.1)
        assert state["tilted"] is True
        assert state["direction_v"] == "haut"

    def test_configurable_thresholds(self, fake_landmarks):
        self._set_neutral(fake_landmarks)
        # With very low thresholds, even a neutral pose triggers
        state = check_head_position(fake_landmarks, rotation_threshold=0.01, tilt_threshold=0.01)
        assert state["turned"] is True or state["tilted"] is True
