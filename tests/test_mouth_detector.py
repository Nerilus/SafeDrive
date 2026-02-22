from tests.conftest import make_landmark
from safedrive.constants import MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT
from safedrive.detectors.mouth_detector import calculate_mouth_opening, detect_yawning


class TestCalculateMouthOpening:
    def test_returns_tuple(self, fake_landmarks):
        """Bug #1 regression: must always return a tuple (float, float)."""
        fake_landmarks[MOUTH_INNER_TOP] = make_landmark(y=0.4)
        fake_landmarks[MOUTH_INNER_BOTTOM] = make_landmark(y=0.6)
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.3)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.7)
        result = calculate_mouth_opening(
            fake_landmarks, MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT
        )
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_zero_horizontal_returns_tuple(self, fake_landmarks):
        """Bug #1 regression: zero horizontal distance must return (0.0, 0.0)."""
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.5)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.5)
        result = calculate_mouth_opening(
            fake_landmarks, MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT
        )
        assert result == (0.0, 0.0)

    def test_closed_mouth(self, fake_landmarks):
        fake_landmarks[MOUTH_INNER_TOP] = make_landmark(y=0.50)
        fake_landmarks[MOUTH_INNER_BOTTOM] = make_landmark(y=0.51)
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.3)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.7)
        mar, vdist = calculate_mouth_opening(
            fake_landmarks, MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT
        )
        assert mar < 0.1
        assert vdist < 0.05

    def test_wide_open_mouth(self, fake_landmarks):
        fake_landmarks[MOUTH_INNER_TOP] = make_landmark(y=0.3)
        fake_landmarks[MOUTH_INNER_BOTTOM] = make_landmark(y=0.7)
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.4)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.6)
        mar, vdist = calculate_mouth_opening(
            fake_landmarks, MOUTH_INNER_TOP, MOUTH_INNER_BOTTOM, MOUTH_LEFT, MOUTH_RIGHT
        )
        assert mar > 1.0
        assert vdist > 0.3


class TestDetectYawning:
    def test_yawning_detected(self, fake_landmarks):
        fake_landmarks[MOUTH_INNER_TOP] = make_landmark(y=0.2)
        fake_landmarks[MOUTH_INNER_BOTTOM] = make_landmark(y=0.8)
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.4)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.6)
        assert detect_yawning(fake_landmarks, mar_threshold=0.6, open_threshold=0.4) is True

    def test_no_yawning(self, fake_landmarks):
        fake_landmarks[MOUTH_INNER_TOP] = make_landmark(y=0.49)
        fake_landmarks[MOUTH_INNER_BOTTOM] = make_landmark(y=0.51)
        fake_landmarks[MOUTH_LEFT] = make_landmark(x=0.3)
        fake_landmarks[MOUTH_RIGHT] = make_landmark(x=0.7)
        assert detect_yawning(fake_landmarks, mar_threshold=0.6, open_threshold=0.4) is False
