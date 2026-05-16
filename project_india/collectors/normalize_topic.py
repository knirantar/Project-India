#!/usr/bin/env python3
"""Normalize collected topic text files into evidence JSON using OpenAI.

Input:
  data/<topic-slug>/raw/*.txt

Output:
  data/<topic-slug>/raw/<sha>.analysis.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_india.collectors.topic_collector import ROOT, load_topic_config, resolve_config_path, topic_slug
from project_india.research_taxonomy import DATA_TYPES, NORMALIZED_OBJECTS

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None


def metadata_for_text(text_path: Path) -> dict:
    metadata_path = text_path.with_suffix(".json")
    if not metadata_path.exists():
        return {}
    try:
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_prompt(text: str, metadata: dict) -> str:
    source_url = metadata.get("url", "")
    title = metadata.get("title", "")
    published = metadata.get("published", "")
    data_type = metadata.get("data_type", "")
    return f"""You are a careful evidence extractor for a research intelligence system.

Return ONLY valid JSON with this structure:
{{
  "document": {{
    "source_url": "{source_url}",
    "source_title": "{title}",
    "published": "{published}",
    "data_type": "{data_type}",
    "author": "",
    "publisher": "",
    "language": "",
    "region": "",
    "summary": "",
    "tags_topics": []
  }},
  "claims": [{{"claim_text": "", "evidence_text": "", "source_url": "{source_url}", "confidence": "low|medium|high"}}],
  "entities": [{{"type": "", "name": "", "description": "", "evidence_text": ""}}],
  "events": [{{"date": "", "event": "", "location": "", "actors": [], "evidence_text": ""}}],
  "metrics": [{{"name": "", "value": "", "unit": "", "date": "", "location": "", "evidence_text": ""}}],
  "relationships": [{{"subject": "", "relationship": "", "object": "", "evidence_text": ""}}],
  "timelines": [{{"date": "", "milestone": "", "evidence_text": ""}}],
  "citations": [{{"source_url": "{source_url}", "title": "{title}", "published": "{published}", "evidence_text": ""}}],
  "evidence_snippets": [{{"text": "", "relevance": "", "source_url": "{source_url}"}}],
  "source_credibility": {{"level": "unknown|low|medium|high|official", "reason": ""}},
  "geolocation": [{{"name": "", "type": "", "latitude": null, "longitude": null, "evidence_text": ""}}],
  "timestamps": [{{"timestamp": "", "meaning": "", "evidence_text": ""}}]
}}

Rules:
- Do not invent facts.
- Use empty lists when the text does not support a field.
- Every claim, entity, event, metric, relationship, timeline item, geolocation, and timestamp must include short evidence_text from the source text.
- Prefer concrete dates, places, named institutions, people, groups, decisions, relationships, numbers, and status changes.
- Treat source type as one of these when possible: {", ".join(DATA_TYPES)}.
- Normalize into these object families: {", ".join(NORMALIZED_OBJECTS)}.

Source text:
{text}
"""


def normalize_text(client: OpenAI, *, model: str, text: str, metadata: dict, max_chars: int) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": build_prompt(text[:max_chars], metadata)}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def normalize_topic(
    *,
    config_path: Path,
    output_root: Path,
    model: str,
    limit: int | None,
    sleep_seconds: float,
    max_chars: int = 12000,
    overwrite: bool = False,
) -> int:
    if OpenAI is None:
        raise RuntimeError("openai package is not installed")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")

    cfg = load_topic_config(config_path)
    raw_dir = output_root / topic_slug(cfg) / "raw"
    text_files = sorted(raw_dir.glob("*.txt"))
    if limit is not None:
        text_files = text_files[:limit]

    client = OpenAI(timeout=60.0)
    written = 0
    for text_path in text_files:
        analysis_path = text_path.with_suffix(".analysis.json")
        if analysis_path.exists() and not overwrite:
            print(f"skipping {text_path.name}")
            continue

        metadata = metadata_for_text(text_path)
        text = text_path.read_text(encoding="utf-8", errors="replace")
        print(f"analyzing {text_path.name}")
        try:
            analysis = normalize_text(client, model=model, text=text, metadata=metadata, max_chars=max_chars)
            analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
            written += 1
        except Exception as exc:
            print(f"openai error for {text_path.name}: {exc}")
        time.sleep(sleep_seconds)

    print(f"wrote {written} analysis files in {raw_dir.relative_to(ROOT)}")
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize collected topic files with OpenAI.")
    parser.add_argument("--config", help="Path to a topic config.yaml file.")
    parser.add_argument("--topic-dir", help="Path to a topic folder containing config.yaml.")
    parser.add_argument("--output-root", default=str(ROOT / "data"), help="Root folder for collected files.")
    parser.add_argument("--model", default="gpt-4o-mini", help="OpenAI model for evidence extraction.")
    parser.add_argument("--limit", type=int, help="Maximum text files to analyze.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Delay between OpenAI calls.")
    parser.add_argument("--max-chars", type=int, default=12000, help="Maximum source-text characters per OpenAI call.")
    parser.add_argument("--overwrite", action="store_true", help="Recreate existing .analysis.json files.")
    args = parser.parse_args()

    normalize_topic(
        config_path=resolve_config_path(args.config, args.topic_dir),
        output_root=Path(args.output_root).expanduser().resolve(),
        model=args.model,
        limit=args.limit,
        sleep_seconds=args.sleep,
        max_chars=args.max_chars,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
