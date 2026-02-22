from types import SimpleNamespace

from tests.conftest import make_landmark
from safedrive.detectors.phone_detector import detect_phone_usage


def _hand(positions):
    """Build a fake hand_landmarks from a list of (x, y) tuples."""
    landmarks = [make_landmark(x=x, y=y) for x, y in positions]
    return SimpleNamespace(landmark=landmarks)


class TestDetectPhoneUsage:
    def test_no_landmarks(self):
        assert detect_phone_usage(None, 480, 640) is False

    def test_fingers_close_together(self):
        """Fingers clustered tightly -> phone detected."""
        positions = [(0.5, 0.5)] * 21
        # Tips close together
        positions[4] = (0.50, 0.50)
        positions[8] = (0.51, 0.50)
        positions[12] = (0.52, 0.50)
        positions[16] = (0.53, 0.50)
        positions[20] = (0.54, 0.50)
        hand = _hand(positions)
        assert detect_phone_usage(hand, 480, 640) is True

    def test_fingers_spread(self):
        """Fingers spread wide -> no phone."""
        positions = [(0.5, 0.5)] * 21
        positions[4] = (0.1, 0.5)
        positions[8] = (0.3, 0.5)
        positions[12] = (0.5, 0.5)
        positions[16] = (0.7, 0.5)
        positions[20] = (0.9, 0.5)
        hand = _hand(positions)
        assert detect_phone_usage(hand, 480, 640) is False

    def test_returns_bool(self):
        positions = [(0.5, 0.5)] * 21
        hand = _hand(positions)
        result = detect_phone_usage(hand, 480, 640)
        assert isinstance(result, bool)
