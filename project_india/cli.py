from __future__ import annotations

import argparse

from project_india.postgres_db import count_tables, import_repo_data, init_db


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-india",
        description="Manage the Project India local Postgres research store.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "db-init",
        help="Create or update the local Postgres schema.",
    )

    subparsers.add_parser(
        "db-import-repo",
        help="Import committed repo research files into local Postgres.",
    )

    subparsers.add_parser(
        "db-status",
        help="Show local Postgres table counts.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "db-init":
        init_db()
        print("Initialized local Postgres schema.")

    if args.command == "db-import-repo":
        summary = import_repo_data()
        print("Imported repo research into local Postgres:")
        for field, value in summary.__dict__.items():
            print(f"- {field}: {value}")

    if args.command == "db-status":
        counts = count_tables()
        print("Local Postgres table counts:")
        for table, count in counts.items():
            print(f"- {table}: {count}")


if __name__ == "__main__":
    main()
