"""Alert system wrapping pygame mixer.

Encapsulates alarm initialisation and playback so that pygame is not
initialised at module level (only imported).
"""

import logging
import os

import pygame  # import is fine; init() is deferred to start()

logger = logging.getLogger(__name__)


class AlertSystem:
    """Manages sound alerts via pygame.mixer."""

    def __init__(self, alarm_path: str, levels: dict):
        self._alarm_path = alarm_path
        self._levels = levels
        self._active = False
        self._mixer = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialise pygame mixer and load the alarm sound."""
        pygame.mixer.init()
        if os.path.isfile(self._alarm_path):
            pygame.mixer.music.load(self._alarm_path)
            logger.info("Alarm loaded: %s", self._alarm_path)
        else:
            logger.warning("Alarm file not found: %s", self._alarm_path)
        self._mixer = pygame.mixer

    def stop(self) -> None:
        """Stop playback and quit the mixer."""
        if self._mixer is not None:
            try:
                self._mixer.music.stop()
                self._mixer.quit()
            except Exception:
                pass
        self._active = False

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    def update(self, alert_level: str) -> None:
        """Start or stop the alarm based on *alert_level*."""
        if self._mixer is None:
            return

        should_sound = self._levels.get(alert_level, {}).get("sound", False)

        if should_sound and not self._active:
            self._mixer.music.play(-1)
            self._active = True
            logger.info("Alarm ON (%s)", alert_level)
        elif not should_sound and self._active:
            self._mixer.music.stop()
            self._active = False
            logger.info("Alarm OFF")

    def get_color(self, alert_level: str):
        """Return the ``(B, G, R)`` color tuple for *alert_level*."""
        return tuple(self._levels.get(alert_level, {}).get("color", [0, 255, 0]))

    @property
    def active(self) -> bool:
        return self._active
