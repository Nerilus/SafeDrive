from tests.conftest import make_landmark
from safedrive.constants import LEFT_EYE_TOP, LEFT_EYE_BOTTOM, RIGHT_EYE_TOP, RIGHT_EYE_BOTTOM
from safedrive.detectors.eye_detector import calculate_eye_opening, detect_eyes_closed


class TestCalculateEyeOpening:
    def test_open_eyes(self, fake_landmarks):
        fake_landmarks[LEFT_EYE_TOP] = make_landmark(y=0.3)
        fake_landmarks[LEFT_EYE_BOTTOM] = make_landmark(y=0.4)
        result = calculate_eye_opening(fake_landmarks, LEFT_EYE_TOP, LEFT_EYE_BOTTOM)
        assert abs(result - 0.1) < 1e-9

    def test_closed_eyes(self, fake_landmarks):
        fake_landmarks[LEFT_EYE_TOP] = make_landmark(y=0.50)
        fake_landmarks[LEFT_EYE_BOTTOM] = make_landmark(y=0.51)
        result = calculate_eye_opening(fake_landmarks, LEFT_EYE_TOP, LEFT_EYE_BOTTOM)
        assert result < 0.02

    def test_no_image_height_param(self):
        """Bug #2 regression: function must NOT accept image_height."""
        import inspect
        sig = inspect.signature(calculate_eye_opening)
        assert "image_height" not in sig.parameters


class TestDetectEyesClosed:
    def test_both_open(self, fake_landmarks):
        fake_landmarks[LEFT_EYE_TOP] = make_landmark(y=0.3)
        fake_landmarks[LEFT_EYE_BOTTOM] = make_landmark(y=0.5)
        fake_landmarks[RIGHT_EYE_TOP] = make_landmark(y=0.3)
        fake_landmarks[RIGHT_EYE_BOTTOM] = make_landmark(y=0.5)
        assert detect_eyes_closed(fake_landmarks, threshold=0.02) is False

    def test_both_closed(self, fake_landmarks):
        fake_landmarks[LEFT_EYE_TOP] = make_landmark(y=0.500)
        fake_landmarks[LEFT_EYE_BOTTOM] = make_landmark(y=0.505)
        fake_landmarks[RIGHT_EYE_TOP] = make_landmark(y=0.500)
        fake_landmarks[RIGHT_EYE_BOTTOM] = make_landmark(y=0.505)
        assert detect_eyes_closed(fake_landmarks, threshold=0.02) is True

    def test_one_open_one_closed(self, fake_landmarks):
        fake_landmarks[LEFT_EYE_TOP] = make_landmark(y=0.3)
        fake_landmarks[LEFT_EYE_BOTTOM] = make_landmark(y=0.5)
        fake_landmarks[RIGHT_EYE_TOP] = make_landmark(y=0.500)
        fake_landmarks[RIGHT_EYE_BOTTOM] = make_landmark(y=0.505)
        assert detect_eyes_closed(fake_landmarks, threshold=0.02) is False
