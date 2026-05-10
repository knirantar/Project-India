from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from project_india import paths


@dataclass(frozen=True)
class ResearchRecord:
    slug: str
    title: str
    category: str
    topic_path: str
    source_path: str | None
    brief_path: str | None
    presentation_outline_path: str | None
    presentation_deck_path: str | None
    topic_data_path: str | None
    updated_at: str


def _title_from_markdown(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def _relative(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    return str(path.relative_to(paths.ROOT))


def _git_timestamp(path: Path) -> str:
    relative = str(path.relative_to(paths.ROOT))
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", relative],
            cwd=paths.ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "uncommitted"

    timestamp = result.stdout.strip()
    return timestamp or "uncommitted"


def _record_for_topic(topic_path: Path) -> ResearchRecord:
    slug = topic_path.stem
    category = str(topic_path.parent.relative_to(paths.DOCS))
    title = _title_from_markdown(topic_path)

    return ResearchRecord(
        slug=slug,
        title=title,
        category=category,
        topic_path=str(topic_path.relative_to(paths.ROOT)),
        source_path=_relative(paths.SOURCES / f"{slug}-sources.md"),
        brief_path=_relative(paths.REPORTS / f"{slug}-brief.md"),
        presentation_outline_path=_relative(paths.PRESENTATIONS / f"{slug}-outline.md"),
        presentation_deck_path=_find_deck(slug),
        topic_data_path=_relative(paths.TOPIC_DATA / f"{slug}.json"),
        updated_at=_git_timestamp(topic_path),
    )


def _find_deck(slug: str) -> str | None:
    candidates = sorted(paths.PRESENTATIONS.glob(f"{slug}*.pptx"))
    if not candidates and slug.startswith("west-bengal-assembly-"):
        candidates = sorted(paths.PRESENTATIONS.glob("west-bengal-election-2026*.pptx"))
    return _relative(candidates[0]) if candidates else None


def build_index() -> list[ResearchRecord]:
    records: list[ResearchRecord] = []
    topic_roots = [
        paths.GEOPOLITICS,
        paths.INTERNAL_GROWTH,
        paths.RESEARCH_NOTES,
        paths.SECTORS,
    ]

    for root in topic_roots:
        if not root.exists():
            continue
        for topic_path in sorted(root.glob("*.md")):
            if topic_path.name.startswith("."):
                continue
            records.append(_record_for_topic(topic_path))

    return records


def write_index(output_path: Path | None = None) -> Path:
    output = output_path or (paths.PROCESSED_DATA / "research_index.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    records = [asdict(record) for record in build_index()]
    output.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
