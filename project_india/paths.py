from __future__ import annotations

from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Return the repository root by walking upward from the current directory."""
    current = (start or Path.cwd()).resolve()

    for path in [current, *current.parents]:
        if (path / ".git").exists() or (path / "pyproject.toml").exists():
            return path

    return current


ROOT = repo_root()
DOCS = ROOT / "docs"
SECTORS = DOCS / "sectors"
GEOPOLITICS = DOCS / "geopolitics"
INTERNAL_GROWTH = DOCS / "internal-growth"
RESEARCH_NOTES = DOCS / "research-notes"
BRIEFS = DOCS / "briefs"
PRESENTATIONS = DOCS / "presentations"
SOURCES = ROOT / "sources"
ANALYSES = ROOT / "analyses"
REPORTS = ANALYSES / "reports"
DATA = ROOT / "data"
RAW_DATA = DATA / "raw"
PROCESSED_DATA = DATA / "processed"
TOPIC_DATA = PROCESSED_DATA / "topic_data"
