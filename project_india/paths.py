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
DATA = ROOT / "data"
PROCESSED_DATA = DATA / "processed"
TOPIC_DATA = PROCESSED_DATA / "topic_data"
RESEARCH_RUNS = PROCESSED_DATA / "research_runs"
DB = ROOT / "db"
DB_SCHEMA = DB / "schema.sql"
