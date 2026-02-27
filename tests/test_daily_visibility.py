"""Tests for daily event visibility — completed today hidden, next day visible."""

from datetime import date, timedelta

import pytest

from daily_event.infra.database import Database
from daily_event.services.daily_event_service import DailyEventService


@pytest.fixture()
def service(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    return DailyEventService(db)


def test_new_event_is_visible(service):
    today = date(2026, 2, 27)
    service.create("健身")
    visible = service.get_visible(today)
    assert len(visible) == 1
    assert visible[0][1] == "健身"


def test_completed_today_hidden(service):
    today = date(2026, 2, 27)
    eid = service.create("健身")
    service.complete_today(eid, today)
    visible = service.get_visible(today)
    assert len(visible) == 0


def test_completed_yesterday_visible_today(service):
    yesterday = date(2026, 2, 26)
    today = date(2026, 2, 27)
    eid = service.create("阅读")
    service.complete_today(eid, yesterday)
    visible = service.get_visible(today)
    assert len(visible) == 1
    assert visible[0][1] == "阅读"


def test_streak_shown_for_visible_item(service):
    day1 = date(2026, 2, 25)
    day2 = date(2026, 2, 26)
    today = date(2026, 2, 27)
    eid = service.create("冥想")
    service.complete_today(eid, day1)
    service.complete_today(eid, day2)
    visible = service.get_visible(today)
    assert len(visible) == 1
    assert visible[0][2] == 2  # streak = 2 (day1 + day2)


def test_multiple_events_independent(service):
    today = date(2026, 2, 27)
    e1 = service.create("A")
    e2 = service.create("B")
    service.complete_today(e1, today)
    visible = service.get_visible(today)
    assert len(visible) == 1
    assert visible[0][1] == "B"


def test_delete_removes_event(service):
    today = date(2026, 2, 27)
    eid = service.create("临时")
    service.delete(eid)
    visible = service.get_visible(today)
    assert len(visible) == 0
