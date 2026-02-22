from types import SimpleNamespace

import pytest

from safedrive.config import AppConfig, DetectionConfig


@pytest.fixture
def default_config():
    """Return an AppConfig with all defaults."""
    return AppConfig()


@pytest.fixture
def detection_config():
    """Return a DetectionConfig with all defaults."""
    return DetectionConfig()


def _make_landmark(x=0.0, y=0.0, z=0.0):
    return SimpleNamespace(x=x, y=y, z=z)


@pytest.fixture
def fake_landmarks():
    """Return a list of 478 fake landmarks (MediaPipe Face Mesh count).

    All values default to (0.5, 0.5, 0.0). Tests can override specific
    indices as needed.
    """
    return [_make_landmark(0.5, 0.5) for _ in range(478)]


@pytest.fixture
def fake_hand_landmarks():
    """Return a fake hand_landmarks object with 21 landmarks."""
    landmarks = [_make_landmark(0.5, 0.5) for _ in range(21)]
    return SimpleNamespace(landmark=landmarks)


def make_landmark(x=0.0, y=0.0, z=0.0):
    """Public helper so tests can build custom landmarks."""
    return _make_landmark(x, y, z)
