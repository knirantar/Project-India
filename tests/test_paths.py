from __future__ import annotations

from pathlib import Path

from project_india.paths import repo_root


def test_repo_root_finds_pyproject(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'example'\n", encoding="utf-8")

    assert repo_root(nested) == root
