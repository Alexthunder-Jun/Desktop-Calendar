"""Tests for daily streak calculation — pure function, no DB needed."""

from datetime import date, timedelta

from daily_event.services.daily_event_service import calc_streak


def test_streak_all_consecutive_including_today():
    today = date(2026, 2, 27)
    dates = {today, today - timedelta(1), today - timedelta(2)}
    streak, total = calc_streak(dates, today)
    assert streak == 3
    assert total == 3


def test_streak_today_only():
    today = date(2026, 2, 27)
    streak, total = calc_streak({today}, today)
    assert streak == 1
    assert total == 1


def test_streak_gap_resets():
    today = date(2026, 2, 27)
    dates = {today, today - timedelta(1), today - timedelta(3)}
    streak, total = calc_streak(dates, today)
    assert streak == 2
    assert total == 3


def test_streak_not_done_today_counts_from_yesterday():
    today = date(2026, 2, 27)
    dates = {today - timedelta(1), today - timedelta(2), today - timedelta(3)}
    streak, total = calc_streak(dates, today)
    assert streak == 3
    assert total == 3


def test_streak_not_done_today_or_yesterday_resets():
    today = date(2026, 2, 27)
    dates = {today - timedelta(2), today - timedelta(3)}
    streak, total = calc_streak(dates, today)
    assert streak == 0
    assert total == 2


def test_streak_empty():
    streak, total = calc_streak(set(), date(2026, 2, 27))
    assert streak == 0
    assert total == 0


def test_streak_single_day_yesterday():
    today = date(2026, 2, 27)
    streak, total = calc_streak({today - timedelta(1)}, today)
    assert streak == 1
    assert total == 1


def test_streak_long_run():
    today = date(2026, 2, 27)
    dates = {today - timedelta(i) for i in range(30)}
    streak, total = calc_streak(dates, today)
    assert streak == 30
    assert total == 30
