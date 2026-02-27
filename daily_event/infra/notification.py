"""Desktop notification service using plyer with fallback."""

from __future__ import annotations


class NotificationService:
    def notify(self, title: str, message: str) -> None:
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="桌面日历",
                timeout=10,
            )
        except Exception:
            pass
