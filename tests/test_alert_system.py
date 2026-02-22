"""Tests for AlertSystem (no real pygame — we mock the mixer)."""

from unittest.mock import MagicMock, patch

import pytest

from safedrive.alert_system import AlertSystem


@pytest.fixture
def levels():
    return {
        "NORMAL": {"color": [0, 255, 0], "sound": False},
        "WARNING": {"color": [0, 255, 255], "sound": False},
        "DANGER": {"color": [0, 0, 255], "sound": True},
    }


@pytest.fixture
def alert(levels, tmp_path):
    alarm_file = tmp_path / "alarm.wav"
    alarm_file.write_bytes(b"\x00")  # dummy file
    return AlertSystem(str(alarm_file), levels)


class TestAlertSystem:
    def test_initial_state(self, alert):
        assert alert.active is False

    @patch("safedrive.alert_system.pygame")
    def test_start_loads_alarm(self, mock_pygame, levels, tmp_path):
        alarm_file = tmp_path / "alarm.wav"
        alarm_file.write_bytes(b"\x00")
        a = AlertSystem(str(alarm_file), levels)
        a.start()
        mock_pygame.mixer.init.assert_called_once()
        mock_pygame.mixer.music.load.assert_called_once_with(str(alarm_file))

    @patch("safedrive.alert_system.pygame")
    def test_update_danger_activates(self, mock_pygame, levels, tmp_path):
        alarm_file = tmp_path / "alarm.wav"
        alarm_file.write_bytes(b"\x00")
        a = AlertSystem(str(alarm_file), levels)
        a.start()
        a.update("DANGER")
        assert a.active is True
        mock_pygame.mixer.music.play.assert_called_once_with(-1)

    @patch("safedrive.alert_system.pygame")
    def test_update_normal_deactivates(self, mock_pygame, levels, tmp_path):
        alarm_file = tmp_path / "alarm.wav"
        alarm_file.write_bytes(b"\x00")
        a = AlertSystem(str(alarm_file), levels)
        a.start()
        a.update("DANGER")
        a.update("NORMAL")
        assert a.active is False

    def test_get_color(self, alert, levels):
        assert alert.get_color("DANGER") == (0, 0, 255)
        assert alert.get_color("NORMAL") == (0, 255, 0)

    def test_stop_without_start(self, alert):
        # Should not raise
        alert.stop()
