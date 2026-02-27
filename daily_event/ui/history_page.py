"""Work Event history page for completed items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from daily_event.domain.models import WorkEvent


class HistoryPage(QDialog):
    delete_requested = Signal(int)

    def __init__(self, events: list[WorkEvent] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("历史")
        self.setMinimumSize(480, 360)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self._events: list[WorkEvent] = events or []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(8)

        heading = QLabel("Work Event · 历史")
        heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a;")
        root.addWidget(heading)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_lo = QVBoxLayout(self._inner)
        self._inner_lo.setContentsMargins(0, 0, 0, 0)
        self._inner_lo.setSpacing(8)
        self._scroll.setWidget(self._inner)
        root.addWidget(self._scroll, stretch=1)
        self.set_events(self._events)

    def set_events(self, events: list[WorkEvent]) -> None:
        self._events = events
        while self._inner_lo.count() > 0:
            item = self._inner_lo.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._events:
            hint = QLabel("暂无历史记录")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._inner_lo.addWidget(hint)
            self._inner_lo.addStretch()
            return

        for ev in self._events:
            self._inner_lo.addWidget(self._build_card(ev))
        self._inner_lo.addStretch()

    def _build_card(self, ev: WorkEvent) -> QWidget:
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
        del_btn = QPushButton("删除")
        del_btn.setFixedHeight(26)
        del_btn.setStyleSheet(
            "font-size:11px; color:#c42b1c; border:1px solid #e0b4b0; border-radius:4px; padding:2px 10px;"
        )
        del_btn.clicked.connect(lambda checked=False, eid=ev.id: self.delete_requested.emit(eid))
        row.addWidget(del_btn)
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
