"""Daily Event business logic — CRUD, streak calculation, visibility."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from daily_event.domain.models import DailyCompletion, DailyEvent
from daily_event.infra.database import Database


@dataclass
class DailyStats:
    event_id: int
    title: str
    current_streak: int
    total_done: int
    created_at: date
    last_done_date: Optional[date]


def calc_streak(completed_dates: set[date], today: date) -> tuple[int, int]:
    """Pure function: (current_streak, total_done) from completion dates.

    If today is not completed, streak is counted from yesterday backwards.
    If neither today nor yesterday is completed, streak resets to 0.
    """
    total = len(completed_dates)
    if not completed_dates:
        return 0, 0

    streak = 0
    check = today
    if check not in completed_dates:
        check = today - timedelta(days=1)
    while check in completed_dates:
        streak += 1
        check -= timedelta(days=1)
    return streak, total


class DailyEventService:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(self, title: str) -> int:
        with self._db.session_scope() as session:
            event = DailyEvent(title=title)
            session.add(event)
            session.flush()
            return event.id

    def delete(self, event_id: int) -> None:
        with self._db.session_scope() as session:
            event = session.get(DailyEvent, event_id)
            if event:
                session.delete(event)

    def complete_today(self, event_id: int, today: date | None = None) -> None:
        if today is None:
            today = date.today()
        with self._db.session_scope() as session:
            exists = session.execute(
                select(DailyCompletion).where(
                    DailyCompletion.event_id == event_id,
                    DailyCompletion.completed_date == today,
                )
            ).scalar_one_or_none()
            if not exists:
                session.add(
                    DailyCompletion(event_id=event_id, completed_date=today)
                )

    def uncomplete_today(self, event_id: int, today: date | None = None) -> None:
        if today is None:
            today = date.today()
        with self._db.session_scope() as session:
            comp = session.execute(
                select(DailyCompletion).where(
                    DailyCompletion.event_id == event_id,
                    DailyCompletion.completed_date == today,
                )
            ).scalar_one_or_none()
            if comp:
                session.delete(comp)

    def get_visible(self, today: date | None = None) -> list[tuple[int, str, int]]:
        """Return (event_id, title, current_streak) for dailies not completed on *today*."""
        if today is None:
            today = date.today()
        with self._db.session_scope() as session:
            events = (
                session.execute(
                    select(DailyEvent)
                    .where(DailyEvent.is_archived == False)  # noqa: E712
                    .options(joinedload(DailyEvent.completions))
                )
                .unique()
                .scalars()
                .all()
            )
            result: list[tuple[int, str, int]] = []
            for ev in events:
                dates_set = {c.completed_date for c in ev.completions}
                if today in dates_set:
                    continue
                streak, _ = calc_streak(dates_set, today)
                result.append((ev.id, ev.title, streak))
            return result

    def get_all_stats(self) -> list[DailyStats]:
        today = date.today()
        with self._db.session_scope() as session:
            events = (
                session.execute(
                    select(DailyEvent)
                    .where(DailyEvent.is_archived == False)  # noqa: E712
                    .options(joinedload(DailyEvent.completions))
                )
                .unique()
                .scalars()
                .all()
            )
            stats: list[DailyStats] = []
            for ev in events:
                dates_set = {c.completed_date for c in ev.completions}
                streak, total = calc_streak(dates_set, today)
                last_done = max(dates_set) if dates_set else None
                created = (
                    ev.created_at.date()
                    if isinstance(ev.created_at, datetime)
                    else ev.created_at
                )
                stats.append(
                    DailyStats(
                        event_id=ev.id,
                        title=ev.title,
                        current_streak=streak,
                        total_done=total,
                        created_at=created,
                        last_done_date=last_done,
                    )
                )
            return stats
