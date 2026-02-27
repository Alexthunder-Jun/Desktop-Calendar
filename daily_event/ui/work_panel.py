"""Work Event panel — full implementation with event list and add button."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
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
    from daily_event.infra.color_allocator import ColorAllocator
    from daily_event.services.work_event_service import WorkEventService


class _WorkItemWidget(QWidget):
    """Single row: coloured dot + title + date range."""

    clicked = Signal(int)
    completed_toggled = Signal(int, bool)

    def __init__(
        self,
        event_id: int,
        title: str,
        start_date,
        end_date,
        color_hex: str,
        is_completed: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._eid = event_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lo = QHBoxLayout(self)
        lo.setContentsMargins(6, 4, 6, 4)
        lo.setSpacing(8)

        cb = QCheckBox()
        cb.setChecked(is_completed)
        cb.toggled.connect(self._on_toggled)
        lo.addWidget(cb)

        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color_hex}; border-radius: 4px;")
        lo.addWidget(dot)

        lbl = QLabel(title)
        if is_completed:
            lbl.setStyleSheet("font-size: 12px; color: #888; text-decoration: line-through;")
        else:
            lbl.setStyleSheet("font-size: 12px; color: #1a1a1a;")
        lo.addWidget(lbl, stretch=1)

        span = QLabel(f"{start_date.month}/{start_date.day}–{end_date.month}/{end_date.day}")
        span.setStyleSheet("font-size: 10px; color: #aaa;" if is_completed else "font-size: 10px; color: #888;")
        lo.addWidget(span)

    def _on_toggled(self, checked: bool) -> None:
        self.completed_toggled.emit(self._eid, checked)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._eid)
            event.accept()
        else:
            super().mousePressEvent(event)


class WorkPanel(QWidget):
    data_changed = Signal()
    event_clicked = Signal(int)

    def __init__(
        self,
        service: WorkEventService | None = None,
        color_allocator: ColorAllocator | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._colors = color_allocator
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("Work Event")
        title.setObjectName("panelTitle")
        header.addWidget(title)
        header.addStretch()
        self._add_btn = QPushButton("+")
        self._add_btn.setObjectName("addButton")
        self._add_btn.setFixedSize(28, 28)
        self._add_btn.clicked.connect(self._on_add)
        header.addWidget(self._add_btn)
        root.addLayout(header)

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

    def _on_add(self) -> None:
        if not self._service:
            return
        from daily_event.ui.dialogs import WorkEventDialog

        dlg = WorkEventDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted and isinstance(dlg.result, dict):
            r = dlg.result
            self._service.create(r["title"], r["start_date"], r["end_date"], r["note"])
            self.refresh()
            self.data_changed.emit()

    def _on_item_clicked(self, event_id: int) -> None:
        self.event_clicked.emit(event_id)

    def _on_item_toggled(self, event_id: int, checked: bool) -> None:
        if not self._service:
            return
        self._service.set_completed(event_id, checked)
        self.data_changed.emit()

    # -- data ---

    def refresh(self) -> None:
        if not self._service:
            return
        events = self._service.get_all()
        self.set_events(events)

    def set_events(self, events: list) -> None:
        self._clear_list()
        if not events:
            hint = QLabel("暂无工作事项")
            hint.setObjectName("emptyHint")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(hint)
        else:
            for ev in events:
                color = self._colors.get_color(ev.color_index) if self._colors else "#999"
                w = _WorkItemWidget(
                    ev.id,
                    ev.title,
                    ev.start_date,
                    ev.end_date,
                    color,
                    ev.is_completed,
                )
                w.clicked.connect(self._on_item_clicked)
                w.completed_toggled.connect(self._on_item_toggled)
                self._list_layout.addWidget(w)
        self._list_layout.addStretch()

    def _clear_list(self) -> None:
        while self._list_layout.count() > 0:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
