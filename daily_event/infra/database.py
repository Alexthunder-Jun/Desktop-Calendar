"""SQLAlchemy engine / session factory with schema migration support."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from daily_event.domain.models import Base, SchemaVersion

CURRENT_SCHEMA_VERSION = 4

MIGRATIONS: dict[int, list[str]] = {
    2: [
        "ALTER TABLE work_events ADD COLUMN is_completed BOOLEAN NOT NULL DEFAULT 0",
    ],
    3: [
        "ALTER TABLE work_events ADD COLUMN completed_at DATETIME",
    ],
    4: [
        "ALTER TABLE daily_events ADD COLUMN recurrence_rule VARCHAR(30) NOT NULL DEFAULT 'daily'",
    ],
}


class Database:
    def __init__(self, db_path: str = "") -> None:
        if not db_path:
            app_dir = Path.home() / ".daily_event"
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / "data.db")
        self._engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
        self._init_schema()

    def _init_schema(self) -> None:
        Base.metadata.create_all(self._engine)
        with self.session_scope() as session:
            ver = session.execute(select(SchemaVersion)).scalar_one_or_none()
            if ver is None:
                session.add(SchemaVersion(version=CURRENT_SCHEMA_VERSION))
            else:
                self._run_migrations(session, ver.version)

    def _run_migrations(self, session: Session, current: int) -> None:
        for version in range(current + 1, CURRENT_SCHEMA_VERSION + 1):
            if version in MIGRATIONS:
                for sql in MIGRATIONS[version]:
                    session.execute(text(sql))
                ver = session.execute(select(SchemaVersion)).scalar_one()
                ver.version = version

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
