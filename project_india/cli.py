from __future__ import annotations

import argparse
from pathlib import Path

from project_india.configure_topic import TopicScheduleUpdate, update_topic_schedule
from project_india.deep_research import run_deep_research
from project_india.increment_research import run_incremental_research
from project_india.research_db import write_index
from project_india.research_plan import write_plan
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

    research_parser = subparsers.add_parser(
        "deep-research",
        help="Run AI-assisted web research and write topic, source, brief, and topic-data files.",
    )
    research_parser.add_argument("title", help="Human-readable topic title.")
    research_parser.add_argument("--slug", help="Optional file slug.")
    research_parser.add_argument(
        "--category",
        choices=sorted(TOPIC_FOLDERS),
        default="sectors",
        help="Destination docs category for the topic note.",
    )
    research_parser.add_argument(
        "--model",
        default="gpt-5",
        help="OpenAI model to use for research.",
    )
    research_parser.add_argument(
        "--depth",
        choices=["standard", "deep"],
        default="deep",
        help="Research depth.",
    )
    research_parser.add_argument(
        "--force-api",
        action="store_true",
        help="Call the OpenAI API even when the local research plan says existing context is sufficient.",
    )

    plan_parser = subparsers.add_parser(
        "plan-research",
        help="Audit local docs/data/index and write a research plan before API calls.",
    )
    plan_parser.add_argument("title", help="Human-readable topic title.")
    plan_parser.add_argument("--slug", help="Optional file slug.")
    plan_parser.add_argument(
        "--category",
        choices=sorted(TOPIC_FOLDERS),
        default="sectors",
        help="Destination docs category for the topic note.",
    )
    plan_parser.add_argument(
        "--force-api",
        action="store_true",
        help="Mark the plan as requiring API research even if local context is strong.",
    )
    plan_parser.add_argument("--output", help="Optional research plan output path.")

    increment_parser = subparsers.add_parser(
        "research-increment",
        help="Run incremental research on a topic (developments, gaps, or fact-checking).",
    )
    increment_parser.add_argument("title", help="Human-readable topic title.")
    increment_parser.add_argument("--slug", help="Optional file slug.")
    increment_parser.add_argument(
        "--category",
        choices=sorted(TOPIC_FOLDERS),
        default="sectors",
        help="Destination docs category for the topic note.",
    )
    increment_parser.add_argument(
        "--strategy",
        choices=["developments", "gaps", "factcheck", "rotate"],
        default="rotate",
        help="Research strategy: developments (new changes), gaps (explore unexplored subtopic), factcheck (verify facts), or rotate (use next in config).",
    )
    increment_parser.add_argument(
        "--model",
        default="gpt-5",
        help="OpenAI model to use for research.",
    )

    schedule_parser = subparsers.add_parser(
        "configure-schedule",
        help="Configure a topic for scheduled incremental research.",
    )
    schedule_parser.add_argument("--slug", required=True, help="Topic slug to configure.")
    schedule_parser.add_argument(
        "--frequency",
        choices=["manual", "daily", "weekly", "monthly"],
        default="manual",
        help="Incremental research frequency.",
    )
    schedule_parser.add_argument(
        "--enabled",
        action="store_true",
        help="Enable scheduled incremental research for this topic.",
    )
    schedule_parser.add_argument(
        "--time-utc",
        default="06:00",
        help="UTC time in HH:MM for scheduled runs.",
    )
    schedule_parser.add_argument(
        "--day-of-week",
        default="monday",
        help="Weekly run day.",
    )
    schedule_parser.add_argument(
        "--day-of-month",
        type=int,
        default=1,
        help="Monthly run day, clamped to 1-28.",
    )
    schedule_parser.add_argument(
        "--strategies",
        default="developments,gaps,factcheck",
        help="Comma-separated rotation of developments,gaps,factcheck.",
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

    if args.command == "index-research":
        output = write_index(Path(args.output) if args.output else None)
        print(f"Wrote research index: {output}")

    if args.command == "deep-research":
        outputs = run_deep_research(
            args.title,
            slug=args.slug,
            category=args.category,
            model=args.model,
            depth=args.depth,
            force_api=args.force_api,
        )
        print("Wrote deep research outputs:")
        print(f"- topic: {outputs.topic_path}")
        print(f"- sources: {outputs.source_path}")
        print(f"- brief: {outputs.brief_path}")
        print(f"- topic data: {outputs.data_path}")
        print(f"- run record: {outputs.run_path}")

    if args.command == "plan-research":
        output = write_plan(
            args.title,
            slug=args.slug,
            category=args.category,
            force_api=args.force_api,
            output_path=Path(args.output) if args.output else None,
        )
        print(f"Wrote research plan: {output}")

    if args.command == "research-increment":
        outputs = run_incremental_research(
            args.title,
            slug=args.slug,
            category=args.category,
            strategy=args.strategy,
            model=args.model,
        )
        print("Incremental research completed:")
        print(f"- strategy: {outputs.strategy}")
        print(f"- topic: {outputs.topic_path}")
        print(f"- sources: {outputs.source_path}")
        print(f"- brief: {outputs.brief_path}")
        print(f"- run record: {outputs.run_path}")
        print(f"- API cost: ${outputs.api_cost_usd}")
        print(f"- changes: {outputs.summary[:200]}...")

    if args.command == "configure-schedule":
        output = update_topic_schedule(
            TopicScheduleUpdate(
                slug=args.slug,
                frequency=args.frequency,
                enabled=args.enabled,
                time_utc=args.time_utc,
                day_of_week=args.day_of_week,
                day_of_month=args.day_of_month,
                strategies=[
                    strategy.strip()
                    for strategy in args.strategies.split(",")
                    if strategy.strip()
                ],
            )
        )
        print(f"Updated topic schedule: {output}")


if __name__ == "__main__":
    main()
