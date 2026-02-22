import os
from dataclasses import dataclass, field
from typing import Dict, Tuple

import yaml


@dataclass
class DetectionConfig:
    eye_closed_threshold: float = 0.02
    mouth_open_threshold: float = 0.4
    mouth_aspect_ratio_threshold: float = 0.6
    head_rotation_threshold: float = 0.2
    head_tilt_threshold: float = 0.1
    eyes_closed_time_threshold: float = 20.0
    phone_detection_threshold: float = 5.0


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 0
    height: int = 0


@dataclass
class AlertConfig:
    levels: Dict[str, Dict] = field(default_factory=lambda: {
        "NORMAL": {"color": [0, 255, 0], "sound": False},
        "WARNING": {"color": [0, 255, 255], "sound": False},
        "DANGER": {"color": [0, 0, 255], "sound": True},
    })
    alarm_path: str = "data/alarm.wav"


@dataclass
class AppConfig:
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    alert: AlertConfig = field(default_factory=AlertConfig)


def _resolve_path(path: str, project_root: str) -> str:
    """Resolve a relative path against the project root."""
    if os.path.isabs(path):
        return path
    return os.path.join(project_root, path)


def load_config(yaml_path: str | None = None, project_root: str | None = None) -> AppConfig:
    """Load configuration from an optional YAML file, falling back to defaults.

    Parameters
    ----------
    yaml_path : str | None
        Path to a YAML config file. If ``None``, only defaults are used.
    project_root : str | None
        Root directory of the project, used to resolve relative paths.
        Defaults to the parent of the ``safedrive`` package.
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cfg = AppConfig()

    if yaml_path is not None:
        resolved = _resolve_path(yaml_path, project_root)
        with open(resolved, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        # Detection overrides
        det = data.get("detection", {})
        for key, value in det.items():
            if hasattr(cfg.detection, key):
                setattr(cfg.detection, key, value)

        # Camera overrides
        cam = data.get("camera", {})
        for key, value in cam.items():
            if hasattr(cfg.camera, key):
                setattr(cfg.camera, key, value)

        # Alert overrides
        alert = data.get("alert", {})
        if "alarm_path" in alert:
            cfg.alert.alarm_path = alert["alarm_path"]
        if "levels" in alert:
            cfg.alert.levels.update(alert["levels"])

    # Resolve alarm_path to absolute
    cfg.alert.alarm_path = _resolve_path(cfg.alert.alarm_path, project_root)

    return cfg
