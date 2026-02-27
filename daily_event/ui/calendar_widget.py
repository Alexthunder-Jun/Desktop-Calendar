"""Custom-painted month calendar grid with work event segment rendering."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from daily_event.services.calendar_service import EventSegment


class CalendarWidget(QWidget):
    """Month calendar grid. Sunday = column 0."""

    date_clicked = Signal(object)
    month_changed = Signal(int, int)
    event_clicked = Signal(int)

    WEEKDAY_HEADERS = ["日", "一", "二", "三", "四", "五", "六"]
    HEADER_HEIGHT = 28

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        today = date.today()
        self._year = today.year
        self._month = today.month
        self._today = today
        self._selected: date | None = today
        self._hovered: date | None = None
        self._grid: list[list[date]] = []
        self._work_segments: list[EventSegment] = []

        self._rebuild_grid()
        self.setMinimumSize(280, 220)
        self.setMouseTracking(True)

    # -- public API --

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def selected_date(self) -> date | None:
        return self._selected

    @property
    def grid_start(self) -> date:
        return self._grid[0][0] if self._grid else date.today()

    def prev_month(self) -> None:
        if self._month == 1:
            self._year -= 1
            self._month = 12
        else:
            self._month -= 1
        self._rebuild_grid()
        self.month_changed.emit(self._year, self._month)
        self.update()

    def next_month(self) -> None:
        if self._month == 12:
            self._year += 1
            self._month = 1
        else:
            self._month += 1
        self._rebuild_grid()
        self.month_changed.emit(self._year, self._month)
        self.update()

    def go_to_today(self) -> None:
        self._today = date.today()
        self._year = self._today.year
        self._month = self._today.month
        self._selected = self._today
        self._rebuild_grid()
        self.month_changed.emit(self._year, self._month)
        self.update()

    def set_work_segments(self, segments: list[EventSegment]) -> None:
        self._work_segments = segments
        self.update()

    # -- grid computation --

    def _rebuild_grid(self) -> None:
        first_of_month = date(self._year, self._month, 1)
        start_offset = (first_of_month.weekday() + 1) % 7
        grid_start = first_of_month - timedelta(days=start_offset)

        self._grid = []
        for week in range(6):
            row: list[date] = []
            for day in range(7):
                d = grid_start + timedelta(days=week * 7 + day)
                row.append(d)
            self._grid.append(row)

    def _cell_rect(self, row: int, col: int) -> QRectF:
        w = self.width()
        h = self.height() - self.HEADER_HEIGHT
        cell_w = w / 7
        cell_h = h / 6
        return QRectF(col * cell_w, self.HEADER_HEIGHT + row * cell_h, cell_w, cell_h)

    # -- painting --

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_header(painter)
        self._paint_grid(painter)
        self._paint_work_segments(painter)
        painter.end()

    def _paint_header(self, p: QPainter) -> None:
        font = QFont(p.font())
        font.setPointSize(9)
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor(130, 130, 130))

        cell_w = self.width() / 7
        for i, hdr in enumerate(self.WEEKDAY_HEADERS):
            rect = QRectF(i * cell_w, 0, cell_w, self.HEADER_HEIGHT)
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, hdr)

    def _paint_grid(self, p: QPainter) -> None:
        font = QFont(p.font())
        font.setPointSize(10)
        font.setBold(False)
        p.setFont(font)

        for row_idx, row in enumerate(self._grid):
            for col_idx, d in enumerate(row):
                rect = self._cell_rect(row_idx, col_idx)
                is_cur = d.month == self._month
                is_today = d == self._today
                is_sel = d == self._selected and not is_today
                is_hover = d == self._hovered and not is_today and not is_sel

                size = min(rect.width(), rect.height()) * 0.62

                if is_today:
                    p.setBrush(QColor(0, 103, 192))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(rect.center(), size / 2, size / 2)
                    p.setPen(QColor(255, 255, 255))
                elif is_sel:
                    p.setBrush(QColor(0, 103, 192, 25))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(rect.center(), size / 2, size / 2)
                    p.setPen(QColor(0, 103, 192))
                elif is_hover:
                    p.setBrush(QColor(0, 0, 0, 12))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(rect.center(), size / 2, size / 2)
                    p.setPen(QColor(30, 30, 30) if is_cur else QColor(190, 190, 190))
                else:
                    p.setPen(QColor(30, 30, 30) if is_cur else QColor(190, 190, 190))

                text_rect = QRectF(rect.x(), rect.y() + 2, rect.width(), rect.height() * 0.45)
                p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(d.day))

    def _paint_work_segments(self, p: QPainter) -> None:
        if not self._work_segments:
            return
        line_h = 3.0
        gap = 1.5
        base_y_fraction = 0.50

        for seg in self._work_segments:
            s_rect = self._cell_rect(seg.row, seg.start_col)
            e_rect = self._cell_rect(seg.row, seg.end_col)

            x1 = s_rect.left() + 3
            x2 = e_rect.right() - 3
            base_y = s_rect.top() + s_rect.height() * base_y_fraction
            y = base_y + seg.slot * (line_h + gap)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(seg.color_hex))
            p.drawRoundedRect(QRectF(x1, y, x2 - x1, line_h), 1.5, 1.5)

    # -- mouse interaction --

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos = event.position()

        for seg in self._work_segments:
            sr = self._cell_rect(seg.row, seg.start_col)
            er = self._cell_rect(seg.row, seg.end_col)
            base_y = sr.top() + sr.height() * 0.50 + seg.slot * 4.5
            hit = QRectF(sr.left(), base_y - 2, er.right() - sr.left(), 7)
            if hit.contains(pos):
                self.event_clicked.emit(seg.event_id)
                event.accept()
                return

        for row_idx, row in enumerate(self._grid):
            for col_idx, d in enumerate(row):
                if self._cell_rect(row_idx, col_idx).contains(pos):
                    self._selected = d
                    self.date_clicked.emit(d)
                    self.update()
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        pos = event.position()
        old = self._hovered
        self._hovered = None
        for row_idx, row in enumerate(self._grid):
            for col_idx, d in enumerate(row):
                if self._cell_rect(row_idx, col_idx).contains(pos):
                    self._hovered = d
                    break
            if self._hovered:
                break
        if self._hovered != old:
            self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802
        if self._hovered:
            self._hovered = None
            self.update()
