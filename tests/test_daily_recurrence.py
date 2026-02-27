"""Tests for daily event recurrence rules."""

from datetime import date

import pytest

from daily_event.infra.database import Database
from daily_event.services.daily_event_service import DailyEventService, is_due_today


@pytest.fixture()
def service(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    return DailyEventService(db)


def test_is_due_today_workday_and_weekend():
    fri = date(2026, 2, 27)
    sat = date(2026, 2, 28)
    created = date(2026, 2, 20)
    assert is_due_today("workday", created, fri) is True
    assert is_due_today("workday", created, sat) is False
    assert is_due_today("weekend", created, fri) is False
    assert is_due_today("weekend", created, sat) is True


def test_is_due_today_interval_rules():
    created = date(2026, 2, 27)
    assert is_due_today("every_2_days", created, date(2026, 2, 27)) is True
    assert is_due_today("every_2_days", created, date(2026, 2, 28)) is False
    assert is_due_today("every_2_days", created, date(2026, 3, 1)) is True

    assert is_due_today("every_3_days", created, date(2026, 3, 2)) is True
    assert is_due_today("every_3_days", created, date(2026, 3, 1)) is False

    assert is_due_today("weekly", created, date(2026, 3, 6)) is True
    assert is_due_today("weekly", created, date(2026, 3, 5)) is False


def test_get_visible_applies_recurrence_rule(service):
    today = date(2026, 3, 1)  # Sunday
    eid = service.create("慢跑")
    service.set_recurrence_rule(eid, "workday")
    visible = service.get_visible(today)
    assert len(visible) == 0

    service.set_recurrence_rule(eid, "weekend")
    visible = service.get_visible(today)
    assert len(visible) == 1
    assert visible[0][1] == "慢跑"
