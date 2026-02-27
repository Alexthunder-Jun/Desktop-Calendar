"""Lightweight dependency injection container."""

from __future__ import annotations

from typing import Any


class Container:
    def __init__(self) -> None:
        self._instances: dict[str, Any] = {}

    def register(self, key: str, instance: Any) -> None:
        self._instances[key] = instance

    def get(self, key: str, default: Any = None) -> Any:
        return self._instances.get(key, default)
