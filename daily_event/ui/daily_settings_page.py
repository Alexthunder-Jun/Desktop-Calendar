"""Daily event settings page for recurrence and deletion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from daily_event.services.daily_event_service import RECURRENCE_RULE_OPTIONS

if TYPE_CHECKING:
    from daily_event.services.daily_event_service import DailySetting


class DailySettingsPage(QDialog):
    delete_requested = Signal(int)
    recurrence_changed = Signal(int, str)

    def __init__(
        self,
        items: list[DailySetting] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("每日事项设置")
        self.setMinimumSize(520, 420)
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self._items: list[DailySetting] = items or []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(8)

        heading = QLabel("Daily Event · 每日事项设置")
        heading.setStyleSheet("font-size: 16px; font-weight: 600; color: #1a1a1a;")
        root.addWidget(heading)

        desc = QLabel("可设置触发间隔或永久删除事项")
        desc.setStyleSheet("font-size: 12px; color: #888; margin-bottom: 6px;")
        root.addWidget(desc)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_lo = QVBoxLayout(self._inner)
        self._inner_lo.setContentsMargins(0, 0, 0, 0)
        self._inner_lo.setSpacing(8)
        self._scroll.setWidget(self._inner)
        root.addWidget(self._scroll, stretch=1)

        self.set_items(self._items)

    def set_items(self, items: list[DailySetting]) -> None:
        self._items = items
        while self._inner_lo.count() > 0:
            it = self._inner_lo.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        if not self._items:
            hint = QLabel("暂无每日事项")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._inner_lo.addWidget(hint)
            self._inner_lo.addStretch()
            return

        for item in self._items:
            self._inner_lo.addWidget(self._build_card(item))
        self._inner_lo.addStretch()

    def _build_card(self, item: DailySetting) -> QWidget:
        card = QWidget()
        card.setObjectName("itemCard")
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lo = QVBoxLayout(card)
        lo.setContentsMargins(12, 10, 12, 10)
        lo.setSpacing(8)

        title = QLabel(item.title)
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #1a1a1a;")
        lo.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(10)

        created = QLabel(f"创建于 {item.created_at}")
        created.setStyleSheet("font-size: 11px; color: #8a8a8a;")
        row.addWidget(created)

        row.addStretch()

        combo = QComboBox()
        combo.setMinimumWidth(130)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        for value, label in RECURRENCE_RULE_OPTIONS:
            combo.addItem(label, userData=value)
        idx = combo.findData(item.recurrence_rule)
        combo.setCurrentIndex(0 if idx < 0 else idx)
        combo.currentIndexChanged.connect(
            lambda _=0, eid=item.event_id, cb=combo: self.recurrence_changed.emit(
                eid, str(cb.currentData())
            )
        )
        row.addWidget(combo)

        delete_btn = QPushButton("删除")
        delete_btn.setFixedHeight(28)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet(
            "font-size:11px; color:#c42b1c; border:1px solid #e0b4b0;"
            "border-radius:6px; padding:2px 12px;"
        )
        delete_btn.clicked.connect(
            lambda checked=False, eid=item.event_id, title=item.title: self._confirm_delete(eid, title)
        )
        row.addWidget(delete_btn)

        lo.addLayout(row)
        return card

    def _confirm_delete(self, event_id: int, title: str) -> None:
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定永久删除「{title}」吗？删除后将不会再出现在 Daily Event 列表。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested.emit(event_id)
