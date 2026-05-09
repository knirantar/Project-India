from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TimelineEvent:
    date: str
    event: str
    significance: str
    source: str = "TBD"


def render_markdown(title: str, events: list[TimelineEvent]) -> str:
    lines = [
        f"# Timeline: {title}",
        "",
        "| Date | Event | Significance | Source |",
        "| --- | --- | --- | --- |",
    ]

    for event in events:
        lines.append(
            f"| {event.date} | {event.event} | {event.significance} | {event.source} |"
        )

    return "\n".join(lines) + "\n"


def write_timeline(path: Path, title: str, events: list[TimelineEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(title, events), encoding="utf-8")

