import os
import tempfile

import yaml
import pytest

from safedrive.config import AppConfig, DetectionConfig, CameraConfig, AlertConfig, load_config


class TestDefaults:
    def test_detection_defaults(self):
        cfg = DetectionConfig()
        assert cfg.eye_closed_threshold == 0.02
        assert cfg.mouth_open_threshold == 0.4
        assert cfg.mouth_aspect_ratio_threshold == 0.6
        assert cfg.head_rotation_threshold == 0.2
        assert cfg.head_tilt_threshold == 0.1
        assert cfg.eyes_closed_time_threshold == 20.0
        assert cfg.phone_detection_threshold == 5.0

    def test_camera_defaults(self):
        cfg = CameraConfig()
        assert cfg.index == 0

    def test_alert_defaults(self):
        cfg = AlertConfig()
        assert "NORMAL" in cfg.levels
        assert "WARNING" in cfg.levels
        assert "DANGER" in cfg.levels
        assert cfg.levels["DANGER"]["sound"] is True

    def test_app_config_defaults(self):
        cfg = AppConfig()
        assert isinstance(cfg.detection, DetectionConfig)
        assert isinstance(cfg.camera, CameraConfig)
        assert isinstance(cfg.alert, AlertConfig)


class TestLoadConfig:
    def test_load_without_yaml(self):
        cfg = load_config()
        assert cfg.detection.eye_closed_threshold == 0.02
        assert cfg.camera.index == 0

    def test_load_with_partial_yaml(self, tmp_path):
        yaml_content = {"detection": {"eye_closed_threshold": 0.05}}
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(yaml_content), encoding="utf-8")

        cfg = load_config(str(yaml_file))
        assert cfg.detection.eye_closed_threshold == 0.05
        # Other defaults preserved
        assert cfg.detection.mouth_open_threshold == 0.4

    def test_load_with_full_yaml(self, tmp_path):
        yaml_content = {
            "detection": {
                "eye_closed_threshold": 0.03,
                "mouth_open_threshold": 0.5,
                "mouth_aspect_ratio_threshold": 0.7,
                "head_rotation_threshold": 0.3,
                "head_tilt_threshold": 0.15,
                "eyes_closed_time_threshold": 15.0,
                "phone_detection_threshold": 3.0,
            },
            "camera": {"index": 2},
            "alert": {"alarm_path": "custom/alarm.wav"},
        }
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(yaml_content), encoding="utf-8")

        cfg = load_config(str(yaml_file))
        assert cfg.detection.eye_closed_threshold == 0.03
        assert cfg.camera.index == 2
        assert cfg.alert.alarm_path.endswith("custom/alarm.wav") or \
               cfg.alert.alarm_path.endswith("custom\\alarm.wav")

    def test_alarm_path_resolved_to_absolute(self):
        cfg = load_config()
        assert os.path.isabs(cfg.alert.alarm_path)

    def test_empty_yaml_uses_defaults(self, tmp_path):
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("", encoding="utf-8")

        cfg = load_config(str(yaml_file))
        assert cfg.detection.eye_closed_threshold == 0.02
