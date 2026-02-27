"""Application bootstrap — creates container, services, and launches UI."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QLockFile
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

_app_lock: QLockFile | None = None


def _acquire_single_instance_lock() -> bool:
    """Prevent multiple app instances (and duplicated tray icons)."""
    global _app_lock
    app_dir = Path.home() / ".daily_event"
    app_dir.mkdir(parents=True, exist_ok=True)
    lock = QLockFile(str(app_dir / "app.lock"))
    lock.setStaleLockTime(0)
    if not lock.tryLock(100):
        return False
    _app_lock = lock
    return True


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
    if not _acquire_single_instance_lock():
        return

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
