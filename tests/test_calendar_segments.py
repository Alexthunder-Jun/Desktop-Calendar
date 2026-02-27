"""Tests for work event date-range to calendar grid segment splitting."""

from datetime import date, timedelta

from daily_event.services.calendar_service import CalendarService, EventSegment


def _gs(year, month):
    """Compute grid_start for a given month (Sunday before or on 1st)."""
    first = date(year, month, 1)
    offset = (first.weekday() + 1) % 7
    return first - timedelta(days=offset)


def test_single_week_segment():
    grid_start = _gs(2026, 2)  # Feb 1 2026 is Sunday
    segs = CalendarService.split_range_to_segments(
        date(2026, 2, 2), date(2026, 2, 5),  # Mon-Thu
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 1
    assert segs[0].row == 0
    assert segs[0].start_col == 1  # Mon
    assert segs[0].end_col == 4    # Thu


def test_cross_week_two_segments():
    grid_start = _gs(2026, 2)
    segs = CalendarService.split_range_to_segments(
        date(2026, 2, 5), date(2026, 2, 10),  # Thu-Tue
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 2
    assert (segs[0].row, segs[0].start_col, segs[0].end_col) == (0, 4, 6)
    assert (segs[1].row, segs[1].start_col, segs[1].end_col) == (1, 0, 2)


def test_full_week_segment():
    grid_start = _gs(2026, 2)
    segs = CalendarService.split_range_to_segments(
        date(2026, 2, 1), date(2026, 2, 7),  # Sun-Sat (full week)
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 1
    assert segs[0].start_col == 0
    assert segs[0].end_col == 6


def test_single_day():
    grid_start = _gs(2026, 2)
    segs = CalendarService.split_range_to_segments(
        date(2026, 2, 15), date(2026, 2, 15),
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 1
    assert segs[0].start_col == segs[0].end_col


def test_outside_grid_clipped():
    grid_start = _gs(2026, 2)
    grid_end = grid_start + timedelta(days=41)
    segs = CalendarService.split_range_to_segments(
        date(2026, 1, 1), date(2026, 1, 20),  # entirely before grid
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 0


def test_partially_overlapping_clipped():
    grid_start = _gs(2026, 2)
    segs = CalendarService.split_range_to_segments(
        date(2026, 1, 28), date(2026, 2, 3),  # starts before grid
        grid_start, "#000", 1, "T",
    )
    assert len(segs) >= 1
    assert segs[0].row == 0
    assert segs[0].start_col == 0  # clipped to grid start


def test_slot_assignment_no_overlap():
    s1 = EventSegment(row=0, start_col=0, end_col=2, color_hex="#a", event_id=1, title="A")
    s2 = EventSegment(row=0, start_col=4, end_col=6, color_hex="#b", event_id=2, title="B")
    CalendarService.assign_slots([s1, s2])
    assert s1.slot == 0
    assert s2.slot == 0


def test_slot_assignment_overlapping():
    s1 = EventSegment(row=0, start_col=0, end_col=4, color_hex="#a", event_id=1, title="A")
    s2 = EventSegment(row=0, start_col=2, end_col=6, color_hex="#b", event_id=2, title="B")
    CalendarService.assign_slots([s1, s2])
    assert s1.slot == 0
    assert s2.slot == 1


def test_three_weeks_span():
    grid_start = _gs(2026, 2)
    segs = CalendarService.split_range_to_segments(
        date(2026, 2, 5), date(2026, 2, 18),  # Thu week0 to Wed week2
        grid_start, "#000", 1, "T",
    )
    assert len(segs) == 3
