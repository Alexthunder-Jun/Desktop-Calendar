"""Daily Event cumulative statistics page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from daily_event.services.daily_event_service import DailyStats


class StatsPage(QDialog):
    def __init__(self, stats: list[DailyStats] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("累计统计")
        self.setMinimumSize(480, 360)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        heading = QLabel("每日事项 · 累计统计")
        heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 8px;")
        root.addWidget(heading)

        if not stats:
            hint = QLabel("暂无统计数据，请先添加每日事项并打卡")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(hint, stretch=1)
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        inner_lo = QVBoxLayout(inner)
        inner_lo.setContentsMargins(0, 0, 0, 0)
        inner_lo.setSpacing(8)

        for s in stats:
            inner_lo.addWidget(self._build_card(s))

        inner_lo.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll)

    @staticmethod
    def _build_card(s: DailyStats) -> QWidget:
        card = QWidget()
        card.setStyleSheet(
            "background: #f5f5f5; border-radius: 8px; padding: 10px;"
        )
        lo = QVBoxLayout(card)
        lo.setContentsMargins(12, 8, 12, 8)
        lo.setSpacing(6)

        title = QLabel(s.title)
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")
        lo.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(_metric("累计", f"{s.total_done} 天"))
        row.addWidget(_metric("连续", f"{s.current_streak} 天"))
        row.addWidget(_metric("创建", str(s.created_at)))
        row.addWidget(_metric("最近完成", str(s.last_done_date) if s.last_done_date else "—"))
        row.addStretch()
        lo.addLayout(row)
        return card


def _metric(label: str, value: str) -> QWidget:
    w = QWidget()
    lo = QVBoxLayout(w)
    lo.setContentsMargins(0, 0, 0, 0)
    lo.setSpacing(1)
    vl = QLabel(value)
    vl.setStyleSheet("font-size: 13px; font-weight: 600; color: #0067c0;")
    lo.addWidget(vl)
    ll = QLabel(label)
    ll.setStyleSheet("font-size: 10px; color: #888;")
    lo.addWidget(ll)
    return w
