"""Work Event history page for completed items."""

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
    from daily_event.domain.models import WorkEvent


class HistoryPage(QDialog):
    def __init__(self, events: list[WorkEvent] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("历史")
        self.setMinimumSize(480, 360)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(8)

        heading = QLabel("Work Event · 历史")
        heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a;")
        root.addWidget(heading)

        if not events:
            hint = QLabel("暂无历史记录")
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

        for ev in events:
            inner_lo.addWidget(self._build_card(ev))
        inner_lo.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

    @staticmethod
    def _build_card(ev: WorkEvent) -> QWidget:
        card = QWidget()
        card.setStyleSheet("background: #f5f5f5; border-radius: 8px; padding: 10px;")
        lo = QVBoxLayout(card)
        lo.setContentsMargins(12, 8, 12, 8)
        lo.setSpacing(6)

        title = QLabel(ev.title)
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")
        lo.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(_metric("区间", f"{ev.start_date} ~ {ev.end_date}"))
        row.addWidget(_metric("完成时间", str(ev.completed_at) if ev.completed_at else "—"))
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
