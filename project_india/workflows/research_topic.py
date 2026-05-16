#!/usr/bin/env python3
"""Run the complete file-based research workflow for one topic.

Example:
  .venv/bin/python project_india/workflows/research_topic.py --topic "India semiconductors"

Workflow:
  topic name
    -> topic folder + config.yaml
    -> RSS + configured URL + optional GDELT historical discovery
    -> data/<topic-slug>/raw/*.html|*.txt|*.json
    -> OpenAI normalization into *.analysis.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_india.collectors.normalize_topic import normalize_topic
from project_india.collectors.topic_collector import collect_topic, display_path, slugify, topic_slug
from project_india.research_taxonomy import DATA_TYPES, DEFAULT_SOURCE_PRIORITIES, NORMALIZED_OBJECTS

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None


DEFAULT_SEEDS = [
    "https://pib.gov.in/rssfeed",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://feeds.reuters.com/reuters/INtopNews",
    "https://www.thehindu.com/news/feeder/default.rss",
    "https://indianexpress.com/section/india/feed/",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "https://www.ndtv.com/rss",
    "https://www.livemint.com/rss/home",
    "https://www.livelaw.in/feed",
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://www.hindustantimes.com/rss/topnews/rssfeed.xml",
    "https://www.theguardian.com/world/rss",
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def topic_dir_for(slug: str) -> Path:
    return ROOT / "project_india" / "topics" / slug


def default_config(topic: str) -> dict[str, Any]:
    slug = slugify(topic)
    words = [word for word in topic.replace("-", " ").split() if len(word) > 2]
    keywords = [topic, topic.lower(), *words]
    queries = [
        topic,
        f"{topic} latest",
        f"{topic} policy",
        f"{topic} official",
        f"{topic} data",
    ]
    return {
        "title": topic,
        "slug": slug,
        "data_types": DATA_TYPES,
        "normalized_objects": NORMALIZED_OBJECTS,
        "keywords": sorted(set(keywords), key=str.lower),
        "entities": [],
        "source_priorities": DEFAULT_SOURCE_PRIORITIES,
        "seeds": DEFAULT_SEEDS,
        "queries": queries,
        "historical_queries": [topic, f"{topic} policy", f"{topic} data"],
        "urls": [],
    }


def build_config_with_openai(topic: str, model: str) -> dict[str, Any] | None:
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        return None

    client = OpenAI(timeout=60.0)
    prompt = f"""Create a machine-readable research topic config for Project India.

Topic: {topic}

Return ONLY valid JSON with keys:
- title: string
- slug: lowercase-kebab-case string
- keywords: 8-15 strings
- entities: 5-15 important people, institutions, places, companies, programs, communities, courts, ministries, or datasets
- source_priorities: list of source categories
- data_types: relevant data types to collect from the Project India taxonomy
- queries: 5-10 search/discovery queries
- historical_queries: 3-6 shorter historical discovery queries

The Project India data type taxonomy is:
{json.dumps(DATA_TYPES, indent=2)}

The normalized object taxonomy is:
{json.dumps(NORMALIZED_OBJECTS, indent=2)}

Do not include URLs unless you are certain they are stable official/source pages.
"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        generated = json.loads(content)
    except Exception as exc:
        print(f"openai config generation failed: {exc}")
        return None

    config = default_config(topic)
    for key in ("title", "slug", "data_types", "keywords", "entities", "source_priorities", "queries", "historical_queries", "urls"):
        if generated.get(key):
            config[key] = generated[key]
    config["slug"] = slugify(str(config.get("slug") or topic))
    config["normalized_objects"] = NORMALIZED_OBJECTS
    config["seeds"] = DEFAULT_SEEDS
    config.setdefault("urls", [])
    return config


def write_topic_files(topic_dir: Path, config: dict[str, Any], overwrite_config: bool) -> Path:
    topic_dir.mkdir(parents=True, exist_ok=True)
    config_path = topic_dir / "config.yaml"
    if overwrite_config or not config_path.exists():
        config_path.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")

    readme_path = topic_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(
            f"""# {config.get("title")}

This topic is generated for the generic Project India file-based research workflow.

Run:

```bash
.venv/bin/python project_india/workflows/research_topic.py --topic "{config.get("title")}"
```

Outputs go to:

```text
data/{topic_slug(config)}/raw/
```
""",
            encoding="utf-8",
        )
    return config_path


def count_outputs(raw_dir: Path) -> dict[str, int]:
    return {
        "html": len(list(raw_dir.glob("*.html"))),
        "txt": len(list(raw_dir.glob("*.txt"))),
        "metadata_json": len([p for p in raw_dir.glob("*.json") if not p.name.endswith(".analysis.json") and not p.name.startswith("_run_")]),
        "analysis_json": len(list(raw_dir.glob("*.analysis.json"))),
        "run_json": len(list(raw_dir.glob("_run_*.json"))),
    }


async def run_workflow(args: argparse.Namespace) -> dict[str, Any]:
    if args.env_file:
        load_env_file(Path(args.env_file).expanduser().resolve())

    base_config = build_config_with_openai(args.topic, args.model) if args.ai_config else None
    config = base_config or default_config(args.topic)
    topic_dir = topic_dir_for(topic_slug(config))
    config_path = write_topic_files(topic_dir, config, args.overwrite_config)

    output_root = Path(args.output_root).expanduser().resolve()
    await collect_topic(
        config_path=config_path,
        limit=args.limit,
        output_root=output_root,
        concurrency=args.concurrency,
        timeout=args.timeout,
        include_historical=args.historical,
        historical_days=args.historical_days,
        historical_max_records=args.historical_max_records,
    )

    if args.normalize:
        normalize_topic(
            config_path=config_path,
            output_root=output_root,
            model=args.model,
            limit=args.normalize_limit,
            sleep_seconds=args.sleep,
            max_chars=args.max_chars,
            overwrite=args.overwrite_analysis,
        )

    raw_dir = output_root / topic_slug(config) / "raw"
    summary = {
        "topic": args.topic,
        "topic_slug": topic_slug(config),
        "topic_dir": display_path(topic_dir),
        "config_path": display_path(config_path),
        "raw_dir": display_path(raw_dir),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "outputs": count_outputs(raw_dir),
    }
    raw_dir.mkdir(parents=True, exist_ok=True)
    summary_path = raw_dir / f"_workflow_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run end-to-end file-based research collection for a topic.")
    parser.add_argument("--topic", required=True, help="Topic name, for example: 'India semiconductors'.")
    parser.add_argument("--output-root", default=str(ROOT / "data"), help="Root folder for collected files.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum new documents to fetch.")
    parser.add_argument("--concurrency", type=int, default=5, help="Maximum concurrent page fetches.")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds.")
    parser.add_argument("--historical", action=argparse.BooleanOptionalAction, default=True, help="Use GDELT historical discovery.")
    parser.add_argument("--historical-days", type=int, default=3650, help="Historical lookback window.")
    parser.add_argument("--historical-max-records", type=int, default=100, help="Maximum GDELT URLs to discover.")
    parser.add_argument("--normalize", action=argparse.BooleanOptionalAction, default=True, help="Run OpenAI evidence extraction.")
    parser.add_argument("--normalize-limit", type=int, help="Maximum text files to normalize.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model for config generation and normalization.")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum source-text characters per OpenAI call.")
    parser.add_argument("--sleep", type=float, default=0.5, help="Delay between OpenAI calls.")
    parser.add_argument("--env-file", default=str(ROOT / ".env"), help="Env file containing OPENAI_API_KEY.")
    parser.add_argument("--ai-config", action=argparse.BooleanOptionalAction, default=True, help="Use OpenAI to create topic config.")
    parser.add_argument("--overwrite-config", action="store_true", help="Replace existing topic config.yaml.")
    parser.add_argument("--overwrite-analysis", action="store_true", help="Replace existing .analysis.json files.")
    args = parser.parse_args()

    asyncio.run(run_workflow(args))


if __name__ == "__main__":
    main()
