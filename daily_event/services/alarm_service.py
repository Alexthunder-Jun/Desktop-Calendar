"""Alarm business logic — countdown, scheduled, fire and notify."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select

from daily_event.domain.enums import AlarmMode, AlarmStatus
from daily_event.domain.models import Alarm
from daily_event.infra.database import Database
from daily_event.infra.notification import NotificationService
from daily_event.infra.sound import SoundService


class AlarmService:
    def __init__(
        self,
        db: Database,
        notification: NotificationService,
        sound: SoundService,
    ) -> None:
        self._db = db
        self._notification = notification
        self._sound = sound

    def create_countdown(self, label: str, minutes: int) -> int:
        target = datetime.now() + timedelta(minutes=minutes)
        auto_label = label or f"{minutes} 分钟倒计时"
        with self._db.session_scope() as session:
            alarm = Alarm(
                label=auto_label,
                mode=AlarmMode.COUNTDOWN.value,
                target_time=target,
                duration_seconds=minutes * 60,
            )
            session.add(alarm)
            session.flush()
            return alarm.id

    def create_scheduled(self, label: str, hour: int, minute: int) -> int:
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        auto_label = label or f"{hour:02d}:{minute:02d} 定时提醒"
        with self._db.session_scope() as session:
            alarm = Alarm(
                label=auto_label,
                mode=AlarmMode.SCHEDULED.value,
                target_time=target,
            )
            session.add(alarm)
            session.flush()
            return alarm.id

    def cancel(self, alarm_id: int) -> None:
        with self._db.session_scope() as session:
            alarm = session.get(Alarm, alarm_id)
            if alarm and alarm.status == AlarmStatus.PENDING.value:
                alarm.status = AlarmStatus.CANCELLED.value

    def get_all(self) -> list[Alarm]:
        with self._db.session_scope() as session:
            return list(
                session.execute(
                    select(Alarm).order_by(Alarm.created_at.desc())
                )
                .scalars()
                .all()
            )

    def check_and_fire(self) -> list[Alarm]:
        """Check pending alarms; fire those past target_time. Returns newly fired."""
        now = datetime.now()
        with self._db.session_scope() as session:
            pending = list(
                session.execute(
                    select(Alarm).where(
                        Alarm.status == AlarmStatus.PENDING.value,
                        Alarm.target_time <= now,
                    )
                )
                .scalars()
                .all()
            )
            for alarm in pending:
                alarm.status = AlarmStatus.FIRED.value
                self._notification.notify("闹钟提醒", alarm.label)
                if alarm.sound_enabled:
                    self._sound.play_alarm()
            return pending
