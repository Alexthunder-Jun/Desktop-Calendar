"""Daily Event cumulative statistics page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from daily_event.services.daily_event_service import DailyStats


class StatsPage(QDialog):
    delete_requested = Signal(int)

    def __init__(self, stats: list[DailyStats] | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("累计统计")
        self.setMinimumSize(480, 360)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self._stats: list[DailyStats] = stats or []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        heading = QLabel("每日事项 · 累计统计")
        heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 8px;")
        root.addWidget(heading)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_lo = QVBoxLayout(self._inner)
        self._inner_lo.setContentsMargins(0, 0, 0, 0)
        self._inner_lo.setSpacing(8)
        self._scroll.setWidget(self._inner)
        root.addWidget(self._scroll)
        self.set_stats(self._stats)

    def set_stats(self, stats: list[DailyStats]) -> None:
        self._stats = stats
        while self._inner_lo.count() > 0:
            item = self._inner_lo.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not self._stats:
            hint = QLabel("暂无统计数据，请先添加每日事项并打卡")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._inner_lo.addWidget(hint)
            self._inner_lo.addStretch()
            return

        for s in self._stats:
            self._inner_lo.addWidget(self._build_card(s))
        self._inner_lo.addStretch()

    def _build_card(self, s: DailyStats) -> QWidget:
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
        del_btn = QPushButton("删除")
        del_btn.setFixedHeight(26)
        del_btn.setStyleSheet(
            "font-size:11px; color:#c42b1c; border:1px solid #e0b4b0; border-radius:4px; padding:2px 10px;"
        )
        del_btn.clicked.connect(lambda checked=False, eid=s.event_id: self._confirm_delete(eid))
        row.addWidget(del_btn)
        lo.addLayout(row)
        return card

    def _confirm_delete(self, event_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定删除该累计事项吗？删除后不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(event_id)


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
