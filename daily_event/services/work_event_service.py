"""Work Event business logic — CRUD and queries."""

from __future__ import annotations

import calendar as cal_mod
from datetime import date
from typing import Any, Optional

from sqlalchemy import select

from daily_event.domain.models import WorkEvent
from daily_event.infra.color_allocator import ColorAllocator
from daily_event.infra.database import Database


class WorkEventService:
    def __init__(self, db: Database, color_allocator: ColorAllocator) -> None:
        self._db = db
        self._colors = color_allocator

    def create(
        self,
        title: str,
        start_date: date,
        end_date: date,
        note: str = "",
    ) -> int:
        with self._db.session_scope() as session:
            event = WorkEvent(
                title=title,
                start_date=start_date,
                end_date=end_date,
                note=note,
            )
            session.add(event)
            session.flush()
            event.color_index = event.id % self._colors.palette_size
            return event.id

    def update(self, event_id: int, **kwargs: Any) -> None:
        with self._db.session_scope() as session:
            event = session.get(WorkEvent, event_id)
            if not event:
                return
            for key, val in kwargs.items():
                if hasattr(event, key) and key not in ("id", "created_at", "color_index"):
                    setattr(event, key, val)

    def delete(self, event_id: int) -> None:
        with self._db.session_scope() as session:
            event = session.get(WorkEvent, event_id)
            if event:
                session.delete(event)

    def get_all(self) -> list[WorkEvent]:
        with self._db.session_scope() as session:
            return list(
                session.execute(
                    select(WorkEvent).order_by(
                        WorkEvent.is_completed.asc(),
                        WorkEvent.start_date,
                    )
                )
                .scalars()
                .all()
            )

    def get_for_month(self, year: int, month: int) -> list[WorkEvent]:
        first = date(year, month, 1)
        last = date(year, month, cal_mod.monthrange(year, month)[1])
        with self._db.session_scope() as session:
            return list(
                session.execute(
                    select(WorkEvent)
                    .where(WorkEvent.start_date <= last, WorkEvent.end_date >= first)
                    .order_by(WorkEvent.is_completed.asc(), WorkEvent.start_date)
                )
                .scalars()
                .all()
            )

    def get_for_date(self, d: date) -> list[WorkEvent]:
        with self._db.session_scope() as session:
            return list(
                session.execute(
                    select(WorkEvent)
                    .where(WorkEvent.start_date <= d, WorkEvent.end_date >= d)
                    .order_by(WorkEvent.is_completed.asc(), WorkEvent.start_date)
                )
                .scalars()
                .all()
            )

    def get_by_id(self, event_id: int) -> Optional[WorkEvent]:
        with self._db.session_scope() as session:
            return session.get(WorkEvent, event_id)

    def set_completed(self, event_id: int, completed: bool) -> None:
        with self._db.session_scope() as session:
            event = session.get(WorkEvent, event_id)
            if event:
                event.is_completed = completed
