"""Scheduling helpers for Project India incremental research."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_time_hour(time_utc: str | None) -> int:
    if not time_utc:
        return 0
    try:
        return max(0, min(int(time_utc.split(":", 1)[0]), 23))
    except (TypeError, ValueError):
        return 0


def next_run_date(schedule: dict[str, Any], now: datetime | None = None) -> str | None:
    now = now or datetime.now(UTC)
    frequency = schedule.get("frequency")

    if frequency == "daily":
        return (now.date() + timedelta(days=1)).isoformat()

    if frequency == "weekly":
        target_weekday = WEEKDAYS.get(str(schedule.get("day_of_week", "monday")).lower(), 0)
        days_ahead = (target_weekday - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (now.date() + timedelta(days=days_ahead)).isoformat()

    if frequency == "monthly":
        raw_day = schedule.get("day_of_month") or 1
        try:
            day = max(1, min(int(raw_day), 28))
        except (TypeError, ValueError):
            day = 1

        year = now.year
        month = now.month
        if now.day >= day:
            month += 1
            if month > 12:
                month = 1
                year += 1
        return date(year, month, day).isoformat()

    return None


def topic_due(topic: dict[str, Any], now: datetime | None = None) -> bool:
    if not topic.get("enabled", False):
        return False

    now = now or datetime.now(UTC)
    schedule = topic.get("schedule", {})
    frequency = schedule.get("frequency")
    if frequency not in {"daily", "weekly", "monthly"}:
        return False

    if parse_time_hour(schedule.get("time_utc")) != now.hour:
        return False

    last_run = schedule.get("last_run_date")
    if last_run == now.date().isoformat():
        return False

    if frequency == "daily":
        return True

    if frequency == "weekly":
        target_weekday = WEEKDAYS.get(str(schedule.get("day_of_week", "monday")).lower(), 0)
        return now.weekday() == target_weekday

    if frequency == "monthly":
        try:
            day = max(1, min(int(schedule.get("day_of_month") or 1), 28))
        except (TypeError, ValueError):
            day = 1
        return now.day == day

    return False
