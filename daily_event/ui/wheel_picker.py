"""Custom wheel picker widget for time selection."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QWheelEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WheelPicker(QWidget):
    valueChanged = Signal(int)

    def __init__(
        self,
        min_val: int,
        max_val: int,
        initial: int = 0,
        fmt: str = "{:02d}",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._val = initial
        self._fmt = fmt

        self.setFixedWidth(60)
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Previous value label (smaller, lighter)
        self._prev_lbl = QLabel()
        self._prev_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prev_lbl.setStyleSheet("color: rgba(0,0,0,0.3); font-size: 14px;")
        layout.addWidget(self._prev_lbl)

        # Current value label (large, bold)
        self._curr_lbl = QLabel()
        self._curr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._curr_lbl.setStyleSheet("color: #0067c0; font-size: 32px; font-weight: bold;")
        layout.addWidget(self._curr_lbl)

        # Next value label (smaller, lighter)
        self._next_lbl = QLabel()
        self._next_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._next_lbl.setStyleSheet("color: rgba(0,0,0,0.3); font-size: 14px;")
        layout.addWidget(self._next_lbl)

        self._update_labels()

    @property
    def value(self) -> int:
        return self._val

    def set_value(self, val: int) -> None:
        self._val = max(self._min, min(self._max, val))
        self._update_labels()
        self.valueChanged.emit(self._val)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        delta = event.angleDelta().y()
        if delta > 0:
            self._change_value(-1)
        elif delta < 0:
            self._change_value(1)
        event.accept()

    def _change_value(self, delta: int) -> None:
        new_val = self._val + delta
        # Wrap around logic
        if new_val > self._max:
            new_val = self._min
        elif new_val < self._min:
            new_val = self._max
        
        self._val = new_val
        self._update_labels()
        self.valueChanged.emit(self._val)

    def _update_labels(self) -> None:
        prev_val = self._val - 1
        if prev_val < self._min:
            prev_val = self._max
            
        next_val = self._val + 1
        if next_val > self._max:
            next_val = self._min

        self._prev_lbl.setText(self._fmt.format(prev_val))
        self._curr_lbl.setText(self._fmt.format(self._val))
        self._next_lbl.setText(self._fmt.format(next_val))
