from __future__ import annotations

import argparse

from project_india.topics import TOPIC_FOLDERS, create_topic


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-india",
        description="Create and manage Project India research workflow files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    topic_parser = subparsers.add_parser("new-topic", help="Create files for a new topic.")
    topic_parser.add_argument("title", help="Human-readable topic title.")
    topic_parser.add_argument("--slug", help="Optional file slug.")
    topic_parser.add_argument(
        "--category",
        choices=sorted(TOPIC_FOLDERS),
        default="sectors",
        help="Destination docs category for the topic note.",
    )
    topic_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated files for this topic.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "new-topic":
        files = create_topic(
            args.title,
            slug=args.slug,
            overwrite=args.overwrite,
            category=args.category,
        )
        print("Created topic workflow files:")
        print(f"- topic: {files.topic}")
        print(f"- sources: {files.sources}")
        print(f"- brief: {files.brief}")
        print(f"- presentation: {files.presentation}")


if __name__ == "__main__":
    main()
