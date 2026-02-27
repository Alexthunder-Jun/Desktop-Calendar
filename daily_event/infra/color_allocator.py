"""Stable color allocation for Work Events.

Uses a 12-color Fluent-style palette. Colors are assigned by event ID
so the same event always gets the same color.
"""

from __future__ import annotations

PALETTE: list[str] = [
    "#4A90D9",  # 蓝
    "#E57373",  # 红
    "#81C784",  # 绿
    "#FFB74D",  # 橙
    "#BA68C8",  # 紫
    "#4DD0E1",  # 青
    "#FF8A65",  # 珊瑚
    "#AED581",  # 黄绿
    "#9575CD",  # 蓝紫
    "#F06292",  # 粉
    "#FFD54F",  # 金
    "#7986CB",  # 靛蓝
]


class ColorAllocator:
    """Assigns colors to work events from a fixed palette."""

    def __init__(self, palette: list[str] | None = None) -> None:
        self._palette = palette or PALETTE

    @property
    def palette_size(self) -> int:
        return len(self._palette)

    def get_color(self, index: int) -> str:
        return self._palette[index % len(self._palette)]
