from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from project_india import paths


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


@dataclass(frozen=True)
class TopicFiles:
    topic: Path
    sources: Path
    brief: Path
    presentation: Path


def topic_template(title: str) -> str:
    return f"""# {title}

## One-Line Summary

TBD.

## Why This Matters

TBD.

## Current State

TBD.

## Historical Context

TBD.

## Key Actors and Institutions

- TBD

## Relevant Policies, Laws, and Programs

- TBD

## Data and Indicators

- TBD

## Strengths

- TBD

## Bottlenecks

- TBD

## Global Comparison

TBD.

## Opportunities

- TBD

## Risks

- TBD

## Future Scenarios

- TBD

## What India Should Do Next

- TBD

## Open Questions

- TBD

## Sources

- See source log in `sources/`.
"""


def source_template(title: str) -> str:
    return f"""# Source Log: {title}

Use this file to track sources before turning them into structured notes.

## Primary Sources

| Date | Source | Link | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Secondary Sources

| Date | Source | Link | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Datasets

| Date | Dataset | Link | Notes |
| --- | --- | --- | --- |
| TBD | TBD | TBD | TBD |

## Claims To Verify

- TBD
"""


def brief_template(title: str) -> str:
    return f"""# Brief: {title}

## Bottom Line

TBD.

## Key Takeaways

- TBD
- TBD
- TBD

## Strategic Context

TBD.

## Evidence

- TBD

## Implications

- TBD

## Recommended Next Research

- TBD
"""


def presentation_template(title: str) -> str:
    return f"""# Presentation Outline: {title}

## Audience

TBD.

## Core Message

TBD.

## Slide Outline

1. Title: {title}
2. Why this matters now
3. Current state
4. Timeline and turning points
5. Key actors and institutions
6. Data view
7. India's strengths
8. Bottlenecks and risks
9. Global comparison
10. Scenarios
11. What India should do next
12. Questions for discussion

## Visual Ideas

- Timeline
- Actor map
- Sector value chain
- Data chart
- Scenario matrix
"""


TOPIC_FOLDERS = {
    "sectors": paths.SECTORS,
    "geopolitics": paths.GEOPOLITICS,
    "internal-growth": paths.INTERNAL_GROWTH,
    "research-notes": paths.RESEARCH_NOTES,
}


def create_topic(
    title: str,
    slug: str | None = None,
    overwrite: bool = False,
    category: str = "sectors",
) -> TopicFiles:
    topic_slug = slugify(slug or title)
    topic_folder = TOPIC_FOLDERS[category]

    files = TopicFiles(
        topic=topic_folder / f"{topic_slug}.md",
        sources=paths.SOURCES / f"{topic_slug}-sources.md",
        brief=paths.REPORTS / f"{topic_slug}-brief.md",
        presentation=paths.PRESENTATIONS / f"{topic_slug}-outline.md",
    )

    for directory in {
        files.topic.parent,
        files.sources.parent,
        files.brief.parent,
        files.presentation.parent,
    }:
        directory.mkdir(parents=True, exist_ok=True)

    writes = {
        files.topic: topic_template(title),
        files.sources: source_template(title),
        files.brief: brief_template(title),
        files.presentation: presentation_template(title),
    }

    for file_path, content in writes.items():
        if file_path.exists() and not overwrite:
            continue
        file_path.write_text(content, encoding="utf-8")

    return files
