from __future__ import annotations

from project_india.cli import build_parser


def test_parser_accepts_database_commands() -> None:
    parser = build_parser()

    for command in ["db-init", "db-import-repo", "db-status"]:
        args = parser.parse_args([command])
        assert args.command == command
