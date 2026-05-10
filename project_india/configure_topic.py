"""Configure tracked topic scheduling for incremental research."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from project_india import paths
from project_india.scheduling import next_run_date


@dataclass(frozen=True)
class TopicScheduleUpdate:
    slug: str
    frequency: str
    enabled: bool
    time_utc: str
    day_of_week: str | None
    day_of_month: int | None
    strategies: list[str]


def _load_config() -> dict:
    config_path = paths.ROOT / "research_config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


def _write_config(config: dict) -> Path:
    config_path = paths.ROOT / "research_config.json"
    config_path.write_text(json.dumps(config, indent=4) + "\n", encoding="utf-8")
    return config_path


def update_topic_schedule(update: TopicScheduleUpdate) -> Path:
    config = _load_config()
    valid_frequencies = {"manual", "daily", "weekly", "monthly"}
    if update.frequency not in valid_frequencies:
        raise ValueError(f"Unsupported frequency: {update.frequency}")

    valid_strategies = {"developments", "gaps", "factcheck"}
    strategies = [strategy for strategy in update.strategies if strategy in valid_strategies]
    if not strategies:
        strategies = ["developments"]

    for topic in config.get("topics", []):
        if topic.get("slug") != update.slug:
            continue

        schedule = {
            "frequency": update.frequency,
            "time_utc": update.time_utc if update.frequency != "manual" else None,
            "last_run_date": topic.get("schedule", {}).get("last_run_date"),
            "next_scheduled_run": None,
        }
        if update.frequency == "weekly":
            schedule["day_of_week"] = update.day_of_week or "monday"
        if update.frequency == "monthly":
            schedule["day_of_month"] = update.day_of_month or 1

        topic["enabled"] = update.enabled and update.frequency != "manual"
        topic["schedule"] = schedule
        topic["schedule"]["next_scheduled_run"] = next_run_date(schedule)
        topic["strategy"] = {
            "rotation": strategies,
            "current_index": 0,
            "description": "Incremental research schedule configured from the Streamlit Operations page.",
        }
        topic.setdefault("metadata", {})["development_status"] = (
            "tracking" if topic["enabled"] else "manual"
        )
        return _write_config(config)

    raise ValueError(f"No topic found for slug: {update.slug}")
