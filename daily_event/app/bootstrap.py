"""Application bootstrap — creates container, services, and launches UI."""

from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from daily_event.app.container import Container
from daily_event.infra.color_allocator import ColorAllocator
from daily_event.infra.database import Database
from daily_event.infra.notification import NotificationService
from daily_event.infra.sound import SoundService
from daily_event.services.alarm_service import AlarmService
from daily_event.services.calendar_service import CalendarService
from daily_event.services.config_service import ConfigService
from daily_event.services.daily_event_service import DailyEventService
from daily_event.services.work_event_service import WorkEventService
from daily_event.ui.main_window import MainWindow


def create_container() -> Container:
    container = Container()

    config = ConfigService()
    container.register("config", config)

    db = Database(config.get("db_path", ""))
    container.register("db", db)

    color_allocator = ColorAllocator()
    container.register("color_allocator", color_allocator)

    notification = NotificationService()
    sound = SoundService(enabled=config.get("sound_enabled", True))

    container.register("daily_service", DailyEventService(db))
    container.register("work_service", WorkEventService(db, color_allocator))
    container.register("alarm_service", AlarmService(db, notification, sound))
    container.register("calendar_service", CalendarService())

    return container


def run() -> None:
    app = QApplication(sys.argv)

    font = QFont()
    if sys.platform == "win32":
        font.setFamilies(["Segoe UI", "Microsoft YaHei"])
    else:
        font.setFamilies(["PingFang SC", "Noto Sans SC"])
    font.setPointSize(10)
    app.setFont(font)

    container = create_container()
    window = MainWindow(container)
    window.show()

    sys.exit(app.exec())
