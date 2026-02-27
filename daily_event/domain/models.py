from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class DailyEvent(Base):
    __tablename__ = "daily_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    is_archived: Mapped[bool] = mapped_column(default=False)
    recurrence_rule: Mapped[str] = mapped_column(String(30), default="daily")

    completions: Mapped[list[DailyCompletion]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class DailyCompletion(Base):
    __tablename__ = "daily_completions"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("daily_events.id", ondelete="CASCADE")
    )
    completed_date: Mapped[date] = mapped_column(nullable=False)

    event: Mapped[DailyEvent] = relationship(back_populates="completions")

    __table_args__ = (UniqueConstraint("event_id", "completed_date"),)


class WorkEvent(Base):
    __tablename__ = "work_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, default="")
    color_index: Mapped[int] = mapped_column(default=0)
    is_completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(200), default="")
    mode: Mapped[str] = mapped_column(String(20))
    target_time: Mapped[datetime] = mapped_column(nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(default=None)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sound_enabled: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)


class SchemaVersion(Base):
    __tablename__ = "schema_version"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(default=1)
    applied_at: Mapped[datetime] = mapped_column(default=datetime.now)
