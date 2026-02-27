"""Hamburger menu popup."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Signal
from PySide6.QtWidgets import QMenu, QWidget


class MenuPanel(QWidget):
    stats_requested = Signal()
    alarm_requested = Signal()
    history_requested = Signal()
    daily_settings_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def show_at(self, global_pos: QPoint) -> None:
        menu = QMenu(self)
        menu.setObjectName("hamburgerMenu")
        stats_action = menu.addAction("累计")
        daily_settings_action = menu.addAction("每日事项设置")
        alarm_action = menu.addAction("闹钟")
        history_action = menu.addAction("历史")
        action = menu.exec(global_pos)
        if action == stats_action:
            self.stats_requested.emit()
        elif action == daily_settings_action:
            self.daily_settings_requested.emit()
        elif action == alarm_action:
            self.alarm_requested.emit()
        elif action == history_action:
            self.history_requested.emit()
