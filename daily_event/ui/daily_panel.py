"""Daily Event panel — full implementation with inline input and streak display."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from daily_event.services.daily_event_service import DailyEventService


class _DailyItemWidget(QWidget):
    """Single row: checkbox + title + streak badge."""

    checked = Signal(int)

    def __init__(self, event_id: int, title: str, streak: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._event_id = event_id

        lo = QHBoxLayout(self)
        lo.setContentsMargins(6, 3, 6, 3)
        lo.setSpacing(8)

        cb = QCheckBox()
        cb.stateChanged.connect(self._on_state)
        lo.addWidget(cb)

        lbl = QLabel(title)
        lbl.setStyleSheet("font-size: 12px; color: #1a1a1a;")
        lo.addWidget(lbl, stretch=1)

        if streak > 0:
            badge = QLabel(f"已坚持 {streak} 天")
            badge.setStyleSheet(
                "font-size: 10px; color: #0067c0; background: rgba(0,103,192,0.08);"
                "border-radius: 3px; padding: 1px 6px;"
            )
            lo.addWidget(badge)

    def _on_state(self, state: int) -> None:
        if state == Qt.CheckState.Checked.value:
            self.checked.emit(self._event_id)


class DailyPanel(QWidget):
    data_changed = Signal()

    def __init__(self, service: DailyEventService | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._input_visible = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("Daily Event")
        title.setObjectName("panelTitle")
        header.addWidget(title)
        header.addStretch()
        self._add_btn = QPushButton("+")
        self._add_btn.setObjectName("addButton")
        self._add_btn.setFixedSize(28, 28)
        self._add_btn.clicked.connect(self._toggle_input)
        header.addWidget(self._add_btn)
        root.addLayout(header)

        self._input_row = QWidget()
        ilo = QHBoxLayout(self._input_row)
        ilo.setContentsMargins(4, 0, 4, 4)
        ilo.setSpacing(4)
        self._title_input = QLineEdit()
        self._title_input.setObjectName("inlineInput")
        self._title_input.setPlaceholderText("输入事项名称，回车确认...")
        self._title_input.returnPressed.connect(self._on_create)
        ilo.addWidget(self._title_input)
        ok_btn = QPushButton("\u2713")
        ok_btn.setObjectName("addButton")
        ok_btn.setFixedSize(24, 24)
        ok_btn.clicked.connect(self._on_create)
        ilo.addWidget(ok_btn)
        self._input_row.hide()
        root.addWidget(self._input_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_widget = QWidget()
        self._list_widget.setObjectName("scrollInner")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        root.addWidget(scroll)

    # -- actions ---

    def _toggle_input(self) -> None:
        self._input_visible = not self._input_visible
        self._input_row.setVisible(self._input_visible)
        if self._input_visible:
            self._title_input.setFocus()

    def _on_create(self) -> None:
        title = self._title_input.text().strip()
        if not title or not self._service:
            return
        self._service.create(title)
        self._title_input.clear()
        self._input_row.hide()
        self._input_visible = False
        self.refresh()
        self.data_changed.emit()

    def _on_item_checked(self, event_id: int) -> None:
        if self._service:
            self._service.complete_today(event_id)
        self.refresh()
        self.data_changed.emit()

    # -- data ---

    def refresh(self) -> None:
        self._clear_list()
        if not self._service:
            return
        items = self._service.get_visible()
        if not items:
            hint = QLabel("暂无每日事项")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(hint)
        else:
            for event_id, title, streak in items:
                w = _DailyItemWidget(event_id, title, streak)
                w.checked.connect(self._on_item_checked)
                self._list_layout.addWidget(w)
        self._list_layout.addStretch()

    def set_items(self, items: list) -> None:
        self._clear_list()
        if not items:
            hint = QLabel("暂无每日事项")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(hint)
        else:
            for event_id, title, streak in items:
                w = _DailyItemWidget(event_id, title, streak)
                w.checked.connect(self._on_item_checked)
                self._list_layout.addWidget(w)
        self._list_layout.addStretch()

    def _clear_list(self) -> None:
        while self._list_layout.count() > 0:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
