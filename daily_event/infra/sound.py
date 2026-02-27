"""Alarm sound playback service."""

from __future__ import annotations

from pathlib import Path


class SoundService:
    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    def play_alarm(self) -> None:
        if not self._enabled:
            return
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
