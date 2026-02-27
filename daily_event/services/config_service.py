"""Centralized config management backed by config.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "window": {"x": 100, "y": 100, "width": 780, "height": 520, "initialized": False},
    "snap_threshold": 20,
    "sound_enabled": True,
    "db_path": "",
    "theme": "light",
}


class ConfigService:
    def __init__(self, config_path: str | Path = "") -> None:
        if not config_path:
            app_dir = Path.home() / ".daily_event"
            app_dir.mkdir(exist_ok=True)
            config_path = app_dir / "config.json"
        self._path = Path(config_path)
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with open(self._path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = json.loads(json.dumps(DEFAULT_CONFIG))
            self._save()

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Dot-notation key access: 'window.x' -> self._data['window']['x']."""
        keys = key.split(".")
        val: Any = self._data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self._save()
