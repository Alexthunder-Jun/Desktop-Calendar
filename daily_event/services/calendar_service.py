"""Calendar rendering utilities — date range to grid segments."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from daily_event.domain.models import WorkEvent


@dataclass
class EventSegment:
    """A single horizontal bar segment on the calendar grid."""
    row: int
    start_col: int
    end_col: int
    color_hex: str
    event_id: int
    title: str
    slot: int = 0


class CalendarService:
    @staticmethod
    def split_range_to_segments(
        start_date: date,
        end_date: date,
        grid_start: date,
        color_hex: str,
        event_id: int,
        title: str,
    ) -> list[EventSegment]:
        """Split a date range into per-week row segments for calendar rendering.

        grid_start: the Sunday that begins the calendar grid (row 0, col 0).
        Returns segments clipped to the 6-row grid (rows 0-5).
        """
        segments: list[EventSegment] = []
        if start_date > end_date:
            return segments

        grid_end = grid_start + timedelta(days=41)
        clipped_start = max(start_date, grid_start)
        clipped_end = min(end_date, grid_end)
        if clipped_start > clipped_end:
            return segments

        current = clipped_start
        while current <= clipped_end:
            days_offset = (current - grid_start).days
            row = days_offset // 7
            start_col = days_offset % 7

            week_end = grid_start + timedelta(days=row * 7 + 6)
            seg_end = min(clipped_end, week_end)
            end_col = (seg_end - grid_start).days % 7

            segments.append(EventSegment(
                row=row,
                start_col=start_col,
                end_col=end_col,
                color_hex=color_hex,
                event_id=event_id,
                title=title,
            ))
            current = seg_end + timedelta(days=1)

        return segments

    @staticmethod
    def assign_slots(segments: list[EventSegment]) -> None:
        """Assign vertical slot indices so overlapping segments stack."""
        from collections import defaultdict

        by_row: dict[int, list[EventSegment]] = defaultdict(list)
        for seg in segments:
            by_row[seg.row].append(seg)

        for row_segs in by_row.values():
            row_segs.sort(key=lambda s: (s.start_col, s.event_id))
            occupied: list[tuple[int, int]] = []  # (end_col, slot)
            for seg in row_segs:
                used_slots = {
                    slot for end_col, slot in occupied if end_col >= seg.start_col
                }
                slot = 0
                while slot in used_slots:
                    slot += 1
                seg.slot = slot
                occupied.append((seg.end_col, slot))
