"""Main application window — frameless, draggable, topmost, edge-snapping."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from daily_event.services.calendar_service import CalendarService
from daily_event.services.config_service import ConfigService
from daily_event.infra.color_allocator import ColorAllocator
from daily_event.ui.alarm_page import AlarmPage
from daily_event.ui.calendar_widget import CalendarWidget
from daily_event.ui.daily_panel import DailyPanel
from daily_event.ui.menu_panel import MenuPanel
from daily_event.ui.stats_page import StatsPage
from daily_event.ui.styles import get_stylesheet
from daily_event.ui.work_panel import WorkPanel

if TYPE_CHECKING:
    from daily_event.app.container import Container

SHADOW_MARGIN = 12


class MainWindow(QWidget):
    def __init__(self, container: Container) -> None:
        super().__init__()
        self._container = container
        self._config: ConfigService = container.get("config")
        self._daily_service = container.get("daily_service")
        self._work_service = container.get("work_service")
        self._alarm_service = container.get("alarm_service")
        self._calendar_service: CalendarService = container.get("calendar_service")
        self._color_allocator: ColorAllocator = container.get("color_allocator")

        self._drag_pos: QPoint | None = None
        self._is_snapping = False
        self._snap_threshold: int = self._config.get("snap_threshold", 20)
        self._quit_requested = False
        self._stats_dialog: StatsPage | None = None
        self._alarm_dialog: AlarmPage | None = None

        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._restore_geometry()
        self._setup_timer()
        self._refresh_all()

    # -- window setup -------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(680, 460)

    def _setup_tray(self) -> None:
        tray_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(tray_icon)

        self._tray = QSystemTrayIcon(tray_icon, self)
        self._tray.setToolTip("桌面日历")

        menu = QMenu()
        show_action = QAction("显示窗口", self)
        hide_action = QAction("隐藏窗口", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self._show_from_tray)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._show_from_tray()

    def _show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _quit_app(self) -> None:
        self._quit_requested = True
        QApplication.instance().quit()

    # -- UI construction ----------------------------------------------------

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN)

        self._content = QWidget()
        self._content.setObjectName("contentFrame")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self._content.setGraphicsEffect(shadow)
        outer.addWidget(self._content)

        cl = QVBoxLayout(self._content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        self._calendar = CalendarWidget()
        self._calendar.month_changed.connect(self._on_month_changed)
        self._calendar.date_clicked.connect(self._on_date_clicked)
        self._calendar.event_clicked.connect(self._on_calendar_event_clicked)

        cl.addWidget(self._create_top_bar())

        body = QWidget()
        bl = QHBoxLayout(body)
        bl.setContentsMargins(12, 8, 12, 12)
        bl.setSpacing(16)

        bl.addWidget(self._calendar, stretch=1)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(10)

        self._daily_panel = DailyPanel(self._daily_service)
        self._daily_panel.data_changed.connect(self._refresh_all)
        rl.addWidget(self._daily_panel, stretch=1)

        self._work_panel = WorkPanel(self._work_service, self._color_allocator)
        self._work_panel.data_changed.connect(self._refresh_all)
        self._work_panel.event_clicked.connect(self._on_calendar_event_clicked)
        rl.addWidget(self._work_panel, stretch=1)

        bl.addWidget(right, stretch=1)
        cl.addWidget(body, stretch=1)

        self._menu_panel = MenuPanel(self)
        self._menu_panel.stats_requested.connect(self._show_stats)
        self._menu_panel.alarm_requested.connect(self._show_alarm)

        self.setStyleSheet(get_stylesheet())

    def _create_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("topBar")
        bar.setFixedHeight(44)

        lo = QHBoxLayout(bar)
        lo.setContentsMargins(12, 6, 8, 6)

        self._menu_btn = QPushButton("\u2261")
        self._menu_btn.setObjectName("menuButton")
        self._menu_btn.setFixedSize(32, 32)
        self._menu_btn.clicked.connect(self._on_menu_clicked)
        lo.addWidget(self._menu_btn)

        lo.addStretch()

        prev_btn = QPushButton("\u25C0")
        prev_btn.setObjectName("navButton")
        prev_btn.setFixedSize(28, 28)
        prev_btn.clicked.connect(lambda: self._calendar.prev_month())
        lo.addWidget(prev_btn)

        self._month_label = QLabel()
        self._month_label.setObjectName("monthLabel")
        lo.addWidget(self._month_label)

        next_btn = QPushButton("\u25B6")
        next_btn.setObjectName("navButton")
        next_btn.setFixedSize(28, 28)
        next_btn.clicked.connect(lambda: self._calendar.next_month())
        lo.addWidget(next_btn)

        lo.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        lo.addWidget(close_btn)

        self._update_month_label()
        return bar

    # -- data refresh -------------------------------------------------------

    def _update_month_label(self) -> None:
        self._month_label.setText(f"{self._calendar.month}月 {self._calendar.year}")

    def _refresh_all(self) -> None:
        self._daily_panel.refresh()
        self._refresh_work_data()

    def _refresh_work_data(self) -> None:
        events = self._work_service.get_for_month(
            self._calendar.year, self._calendar.month
        )
        self._work_panel.set_events(events)

        segments: list = []
        for ev in events:
            color = "#b8b8b8" if ev.is_completed else self._color_allocator.get_color(ev.color_index)
            segs = self._calendar_service.split_range_to_segments(
                ev.start_date,
                ev.end_date,
                self._calendar.grid_start,
                color,
                ev.id,
                ev.title,
            )
            segments.extend(segs)
        self._calendar_service.assign_slots(segments)
        self._calendar.set_work_segments(segments)

    # -- event handlers -----------------------------------------------------

    def _on_month_changed(self, year: int, month: int) -> None:
        self._update_month_label()
        self._refresh_work_data()

    def _on_date_clicked(self, d: date) -> None:
        events = self._work_service.get_for_date(d)
        self._work_panel.set_events(events)

    def _on_calendar_event_clicked(self, event_id: int) -> None:
        ev = self._work_service.get_by_id(event_id)
        if not ev:
            return
        from daily_event.ui.dialogs import WorkEventDialog

        dlg = WorkEventDialog(self, ev)
        if dlg.exec() == WorkEventDialog.DialogCode.Accepted:
            r = dlg.result
            if r == "DELETE":
                self._work_service.delete(event_id)
            elif isinstance(r, dict):
                self._work_service.update(event_id, **r)
            self._refresh_all()

    def _on_menu_clicked(self) -> None:
        pos = self._menu_btn.mapToGlobal(QPoint(0, self._menu_btn.height()))
        self._menu_panel.show_at(pos)

    def _show_stats(self) -> None:
        stats = self._daily_service.get_all_stats()
        if self._stats_dialog and self._stats_dialog.isVisible():
            self._stats_dialog.raise_()
            self._stats_dialog.activateWindow()
            return
        self._stats_dialog = StatsPage(stats, self)
        self._stats_dialog.setModal(False)
        self._stats_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._stats_dialog.destroyed.connect(lambda: setattr(self, "_stats_dialog", None))
        self._stats_dialog.show()
        self._stats_dialog.raise_()
        self._stats_dialog.activateWindow()

    def _show_alarm(self) -> None:
        if self._alarm_dialog and self._alarm_dialog.isVisible():
            self._alarm_dialog.raise_()
            self._alarm_dialog.activateWindow()
            return
        self._alarm_dialog = AlarmPage(self._alarm_service, self)
        self._alarm_dialog.setModal(False)
        self._alarm_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._alarm_dialog.destroyed.connect(lambda: setattr(self, "_alarm_dialog", None))
        self._alarm_dialog.show()
        self._alarm_dialog.raise_()
        self._alarm_dialog.activateWindow()

    # -- alarm timer --------------------------------------------------------

    def _setup_timer(self) -> None:
        self._alarm_timer = QTimer(self)
        self._alarm_timer.timeout.connect(self._check_alarms)
        self._alarm_timer.start(1000)

    def _check_alarms(self) -> None:
        self._alarm_service.check_and_fire()

    # -- drag handling ------------------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    # -- edge snapping ------------------------------------------------------

    def moveEvent(self, event) -> None:  # noqa: N802
        if self._is_snapping:
            return
        screen = self.screen()
        if not screen:
            return
        geo = screen.availableGeometry()
        x, y = self.x(), self.y()
        t = self._snap_threshold
        snap = False

        if abs(x - geo.left()) < t:
            x = geo.left(); snap = True
        elif abs(x + self.width() - geo.right()) < t:
            x = geo.right() - self.width(); snap = True

        if abs(y - geo.top()) < t:
            y = geo.top(); snap = True
        elif abs(y + self.height() - geo.bottom()) < t:
            y = geo.bottom() - self.height(); snap = True

        if snap:
            self._is_snapping = True
            self.move(x, y)
            self._is_snapping = False

    # -- geometry persistence -----------------------------------------------

    def _restore_geometry(self) -> None:
        w = self._config.get("window.width", 780)
        h = self._config.get("window.height", 520)
        initialized = self._config.get("window.initialized", False)
        if initialized:
            x = self._config.get("window.x", 100)
            y = self._config.get("window.y", 100)
        else:
            screen = self.screen() or QApplication.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                x = geo.right() - w - 24
                y = geo.top() + 80
            else:
                x, y = 100, 100
            self._config.set("window.initialized", True)
        self.setGeometry(x, y, w, h)

    def closeEvent(self, event) -> None:  # noqa: N802
        g = self.geometry()
        self._config.set("window.x", g.x())
        self._config.set("window.y", g.y())
        self._config.set("window.width", g.width())
        self._config.set("window.height", g.height())
        if self._quit_requested:
            super().closeEvent(event)
            return
        self.hide()
        event.ignore()
