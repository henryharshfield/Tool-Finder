from __future__ import annotations

from datetime import date, timedelta

from .schemas import DeadlineStatus


def classify_deadline(
    today: date,
    needed_by_date: date,
    candidate_arrival_date: date,
) -> DeadlineStatus:
    time_window_days = (needed_by_date - today).days
    slight_miss_cutoff = today + timedelta(days=round(time_window_days * 1.25))

    if candidate_arrival_date <= needed_by_date:
        return DeadlineStatus.DEADLINE_FEASIBLE
    if candidate_arrival_date <= slight_miss_cutoff:
        return DeadlineStatus.SLIGHT_MISS
    return DeadlineStatus.FUTURE_OPTION_ONLY
