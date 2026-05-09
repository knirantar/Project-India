from __future__ import annotations

import argparse
from pathlib import Path

from project_india.presentation_builder import build_presentation
from project_india.research_db import write_index
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

    index_parser = subparsers.add_parser(
        "index-research",
        help="Build data/processed/research_index.json from current research files.",
    )
    index_parser.add_argument("--output", help="Optional output path for the JSON index.")

    deck_parser = subparsers.add_parser(
        "build-presentation",
        help="Create a draft PPTX presentation for a topic.",
    )
    deck_parser.add_argument("title", help="Human-readable topic title.")
    deck_parser.add_argument("--slug", help="Optional file slug.")
    deck_parser.add_argument(
        "--category",
        choices=sorted(TOPIC_FOLDERS),
        default="sectors",
        help="Docs category for the source topic note.",
    )
    deck_parser.add_argument("--output", help="Optional PPTX output path.")

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

    if args.command == "index-research":
        output = write_index(Path(args.output) if args.output else None)
        print(f"Wrote research index: {output}")

    if args.command == "build-presentation":
        output = build_presentation(
            args.title,
            slug=args.slug,
            category=args.category,
            output_path=Path(args.output) if args.output else None,
        )
        print(f"Wrote presentation: {output}")


if __name__ == "__main__":
    main()
