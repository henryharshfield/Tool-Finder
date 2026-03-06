from __future__ import annotations

from datetime import date, timedelta

from tool_finder.schemas import DeadlineStatus


def classify_deadline(today: date, needed_by_date: date, candidate_arrival_date: date) -> DeadlineStatus:
    if candidate_arrival_date <= needed_by_date:
        return DeadlineStatus.DEADLINE_FEASIBLE

    time_window = needed_by_date - today
    slight_miss_cutoff = today + timedelta(days=time_window.days * 1.25)

    if candidate_arrival_date <= slight_miss_cutoff:
        return DeadlineStatus.SLIGHT_MISS
    return DeadlineStatus.FUTURE_OPTION_ONLY
