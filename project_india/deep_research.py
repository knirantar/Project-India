from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from project_india import paths
from project_india.topics import TOPIC_FOLDERS, TopicFiles, create_topic, slugify


TAG_NAMES = [
    "TOPIC_NOTE",
    "SOURCE_LOG",
    "BRIEF",
    "PRESENTATION_OUTLINE",
]


@dataclass(frozen=True)
class ResearchOutputs:
    topic: str
    slug: str
    category: str
    model: str
    depth: str
    topic_path: str
    source_path: str
    brief_path: str
    presentation_path: str
    run_path: str


def _extract_tag(text: str, tag: str) -> str:
    start = f"<{tag}>"
    end = f"</{tag}>"
    if start not in text or end not in text:
        raise ValueError(f"Model output did not include required {start}...{end} block.")
    return text.split(start, 1)[1].split(end, 1)[0].strip() + "\n"


def _files_for(title: str, slug: str, category: str) -> TopicFiles:
    create_topic(title, slug=slug, category=category)
    return TopicFiles(
        topic=TOPIC_FOLDERS[category] / f"{slug}.md",
        sources=paths.SOURCES / f"{slug}-sources.md",
        brief=paths.REPORTS / f"{slug}-brief.md",
        presentation=paths.PRESENTATIONS / f"{slug}-outline.md",
    )


def _existing_context(files: TopicFiles) -> str:
    parts = []
    for label, path in [
        ("topic note", files.topic),
        ("source log", files.sources),
        ("brief", files.brief),
        ("presentation outline", files.presentation),
    ]:
        if path.exists():
            parts.append(f"--- Existing {label}: {path.relative_to(paths.ROOT)} ---\n")
            parts.append(path.read_text(encoding="utf-8")[:16000])
            parts.append("\n")
    return "\n".join(parts)


def _prompt(title: str, category: str, depth: str, existing_context: str) -> str:
    return f"""
You are building Project India, a rigorous research system about India's
geopolitics and internal growth.

Research topic: {title}
Category: {category}
Depth: {depth}

Your task is to perform real source-backed research before writing. Use web
search. Prefer primary sources first: official government sites, Election
Commission, RBI, PIB, ministries, parliament, courts, budgets, official
statistics, multilateral datasets, and original policy documents. Then use
credible secondary sources: serious newspapers, think tanks, universities,
industry bodies, and books/reports. Avoid unsupported claims.

Rules:
- Use concrete dates and distinguish current facts from historical background.
- Put citations or source links next to important claims.
- Do not invent statistics. If data is missing, mark it as a data gap.
- Separate facts, interpretation, hypotheses, and open questions.
- For elections or current affairs, mark early reporting as provisional until
  official data is available.
- Make the presentation outline specific enough to become an actual deck, not a
  generic template.
- Return exactly the four XML-like blocks below and nothing outside them.

Existing repository context to improve, replace, or build on:
{existing_context}

Output format:

<TOPIC_NOTE>
# {title}

## One-Line Summary
...

## Why This Matters
...

## Current State
...

## Historical Context
...

## Key Actors and Institutions
...

## Relevant Policies, Laws, and Programs
...

## Data and Indicators
...

## Strengths
...

## Bottlenecks
...

## Global Comparison
...

## Opportunities
...

## Risks
...

## Future Scenarios
...

## What India Should Watch Next
...

## Open Questions
...

## Sources
...
</TOPIC_NOTE>

<SOURCE_LOG>
# Source Log: {title}

## Primary Sources
| Date | Source | Link | Notes |
| --- | --- | --- | --- |

## Secondary Sources
| Date | Source | Link | Notes |
| --- | --- | --- | --- |

## Datasets
| Date | Dataset | Link | Notes |
| --- | --- | --- | --- |

## Claims To Verify
...
</SOURCE_LOG>

<BRIEF>
# Brief: {title}

## Bottom Line
...

## Key Takeaways
...

## Strategic Context
...

## Evidence
...

## Implications
...

## Recommended Next Research
...
</BRIEF>

<PRESENTATION_OUTLINE>
# Presentation Outline: {title}

## Audience
...

## Core Message
...

## Slide Outline
For each slide, write:
1. Claim title
   - Proof object:
   - Evidence:
   - Source:

## Visual Ideas
...

## Speaker Notes To Build
...
</PRESENTATION_OUTLINE>
""".strip()


def run_deep_research(
    title: str,
    slug: str | None = None,
    category: str = "sectors",
    model: str = "gpt-5",
    depth: str = "deep",
) -> ResearchOutputs:
    if category not in TOPIC_FOLDERS:
        raise ValueError(f"Unknown category: {category}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is required for deep research. Add it as a GitHub Actions secret."
        )

    try:
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit(
            "openai is required. Install with: python3 -m pip install -e '.[research]'"
        ) from error

    topic_slug = slugify(slug or title)
    files = _files_for(title, topic_slug, category)
    context = _existing_context(files)
    client = OpenAI()

    response = client.responses.create(
        model=model,
        reasoning={"effort": "high" if depth == "deep" else "low"},
        tools=[{"type": "web_search"}],
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input=_prompt(title, category, depth, context),
    )

    output_text = response.output_text
    topic_note = _extract_tag(output_text, "TOPIC_NOTE")
    source_log = _extract_tag(output_text, "SOURCE_LOG")
    brief = _extract_tag(output_text, "BRIEF")
    presentation = _extract_tag(output_text, "PRESENTATION_OUTLINE")

    files.topic.write_text(topic_note, encoding="utf-8")
    files.sources.write_text(source_log, encoding="utf-8")
    files.brief.write_text(brief, encoding="utf-8")
    files.presentation.write_text(presentation, encoding="utf-8")

    run_dir = paths.PROCESSED_DATA / "research_runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"{topic_slug}.json"
    response_dump = response.model_dump() if hasattr(response, "model_dump") else {}
    run_payload = {
        "title": title,
        "slug": topic_slug,
        "category": category,
        "model": model,
        "depth": depth,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "response_id": getattr(response, "id", None),
        "response": response_dump,
    }
    run_path.write_text(json.dumps(run_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    outputs = ResearchOutputs(
        topic=title,
        slug=topic_slug,
        category=category,
        model=model,
        depth=depth,
        topic_path=str(files.topic.relative_to(paths.ROOT)),
        source_path=str(files.sources.relative_to(paths.ROOT)),
        brief_path=str(files.brief.relative_to(paths.ROOT)),
        presentation_path=str(files.presentation.relative_to(paths.ROOT)),
        run_path=str(run_path.relative_to(paths.ROOT)),
    )
    return outputs


def run_deep_research_json(**kwargs: str) -> str:
    return json.dumps(asdict(run_deep_research(**kwargs)), indent=2, sort_keys=True)
