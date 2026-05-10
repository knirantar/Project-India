from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from project_india import paths
from project_india.research_plan import plan_research
from project_india.topics import TOPIC_FOLDERS, TopicFiles, create_topic, slugify


TAG_NAMES = [
    "TOPIC_NOTE",
    "SOURCE_LOG",
    "BRIEF",
    "TOPIC_DATA",
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
    data_path: str
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
    )


def _existing_context(files: TopicFiles) -> str:
    parts = []
    for label, path in [
        ("topic note", files.topic),
        ("source log", files.sources),
        ("brief", files.brief),
        ("topic data", paths.TOPIC_DATA / f"{files.topic.stem}.json"),
    ]:
        if path.exists():
            parts.append(f"--- Existing {label}: {path.relative_to(paths.ROOT)} ---\n")
            parts.append(path.read_text(encoding="utf-8")[:16000])
            parts.append("\n")
    return "\n".join(parts)


def _prompt(
    title: str,
    category: str,
    depth: str,
    existing_context: str,
    planning_context: str,
) -> str:
    return f"""
You are building Project India, a rigorous research system about India's
geopolitics and internal growth.

Research topic: {title}
Category: {category}
Depth: {depth}

Your task is to perform real source-backed research before writing, but first
use the repository memory below. Do not spend search effort repeating what is
already known. Use web search only for missing sources, current facts, datasets,
conflicting claims, and unexplored subtopics identified in the research plan.

Prefer primary sources first: official government sites, Election
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
- Extract concrete numbers, dates, comparisons, timelines, and tables into
  TOPIC_DATA. The Streamlit dashboard depends on this structured evidence.
- Include at least 5 metrics, 1 comparison with numeric values, 5 timeline
  events, 1 table, and explicit data gaps unless the topic genuinely lacks
  public data. If data is missing, say what source would be needed.
- Return exactly the four XML-like blocks below and nothing outside them.

Existing repository context to improve, replace, or build on:
{planning_context}

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

<TOPIC_DATA>
{{
  "topic": "{title}",
  "status": "researched",
  "metrics": [
    {{
      "label": "Example metric name",
      "value": 0,
      "unit": "example unit",
      "date": "YYYY-MM-DD or year",
      "context": "Why the metric matters",
      "source": "Source name and URL",
      "confidence": "high|medium|low"
    }}
  ],
  "comparisons": [
    {{
      "title": "Comparison title",
      "unit": "unit",
      "source": "Source name and URL",
      "items": [
        {{"label": "A", "value": 0}},
        {{"label": "B", "value": 0}}
      ]
    }}
  ],
  "timeline": [
    {{
      "date": "YYYY-MM-DD or year",
      "event": "Event",
      "significance": "Why it matters",
      "source": "Source name and URL"
    }}
  ],
  "tables": [
    {{
      "title": "Table title",
      "columns": ["Column A", "Column B"],
      "rows": [["A", "B"]],
      "source": "Source name and URL"
    }}
  ],
  "data_gaps": [
    "Specific missing dataset, official confirmation, or unresolved metric"
  ]
}}
</TOPIC_DATA>
""".strip()


def _openai_retry_count() -> int:
    raw_value = os.environ.get("PROJECT_INDIA_OPENAI_RETRIES", "4")
    try:
        return max(1, int(raw_value))
    except ValueError:
        return 4


def _create_response_with_retries(client: object, **kwargs: object) -> object:
    """Call OpenAI Responses API with backoff for transient transport failures."""
    try:
        from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError
    except ImportError as error:
        raise SystemExit(
            "openai is required. Install with: python3 -m pip install -e '.[research]'"
        ) from error

    retryable_errors = (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError)
    attempts = _openai_retry_count()
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return client.responses.create(**kwargs)  # type: ignore[attr-defined]
        except retryable_errors as error:
            last_error = error
            if attempt == attempts:
                break

            delay = min(90, 5 * (2 ** (attempt - 1)))
            print(
                f"OpenAI request failed with {type(error).__name__}; "
                f"retrying in {delay}s ({attempt}/{attempts}).",
                flush=True,
            )
            time.sleep(delay)

    raise SystemExit(
        "OpenAI request failed after "
        f"{attempts} attempts: {type(last_error).__name__}: {last_error}"
    )


def run_deep_research(
    title: str,
    slug: str | None = None,
    category: str = "sectors",
    model: str = "gpt-5",
    depth: str = "deep",
    force_api: bool = False,
) -> ResearchOutputs:
    if category not in TOPIC_FOLDERS:
        raise ValueError(f"Unknown category: {category}")

    topic_slug = slugify(slug or title)
    files = _files_for(title, topic_slug, category)
    data_path = paths.TOPIC_DATA / f"{topic_slug}.json"
    plan = plan_research(title, slug=topic_slug, category=category, force_api=force_api)
    context = _existing_context(files)
    planning_context = json.dumps(asdict(plan), indent=2, sort_keys=True)

    if not plan.should_call_api:
        run_path = _write_run_record(
            title=title,
            slug=topic_slug,
            category=category,
            model=model,
            depth=depth,
            plan=plan,
            response_id=None,
            response={},
            skipped=True,
        )
        return ResearchOutputs(
            topic=title,
            slug=topic_slug,
            category=category,
            model=model,
            depth=depth,
            topic_path=str(files.topic.relative_to(paths.ROOT)),
            source_path=str(files.sources.relative_to(paths.ROOT)),
            brief_path=str(files.brief.relative_to(paths.ROOT)),
            data_path=str(data_path.relative_to(paths.ROOT)),
            run_path=str(run_path.relative_to(paths.ROOT)),
        )

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

    client = OpenAI()

    response = _create_response_with_retries(
        client,
        model=model,
        reasoning={"effort": "high" if depth == "deep" else "low"},
        tools=[{"type": "web_search"}],
        tool_choice="auto",
        include=["web_search_call.action.sources"],
        input=_prompt(title, category, depth, context, planning_context),
    )

    output_text = response.output_text
    topic_note = _extract_tag(output_text, "TOPIC_NOTE")
    source_log = _extract_tag(output_text, "SOURCE_LOG")
    brief = _extract_tag(output_text, "BRIEF")
    topic_data = _extract_tag(output_text, "TOPIC_DATA")

    files.topic.write_text(topic_note, encoding="utf-8")
    files.sources.write_text(source_log, encoding="utf-8")
    files.brief.write_text(brief, encoding="utf-8")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(
        json.dumps(_parse_topic_data(topic_data), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    response_dump = response.model_dump() if hasattr(response, "model_dump") else {}
    run_path = _write_run_record(
        title=title,
        slug=topic_slug,
        category=category,
        model=model,
        depth=depth,
        plan=plan,
        response_id=getattr(response, "id", None),
        response=response_dump,
        skipped=False,
    )

    outputs = ResearchOutputs(
        topic=title,
        slug=topic_slug,
        category=category,
        model=model,
        depth=depth,
        topic_path=str(files.topic.relative_to(paths.ROOT)),
        source_path=str(files.sources.relative_to(paths.ROOT)),
        brief_path=str(files.brief.relative_to(paths.ROOT)),
        data_path=str(data_path.relative_to(paths.ROOT)),
        run_path=str(run_path.relative_to(paths.ROOT)),
    )
    return outputs


def _write_run_record(
    title: str,
    slug: str,
    category: str,
    model: str,
    depth: str,
    plan: object,
    response_id: str | None,
    response: dict,
    skipped: bool,
) -> Path:
    run_dir = paths.PROCESSED_DATA / "research_runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    run_path = run_dir / f"{slug}.json"
    run_payload = {
        "title": title,
        "slug": slug,
        "category": category,
        "model": model,
        "depth": depth,
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "response_id": response_id,
        "skipped_api_call": skipped,
        "research_plan": asdict(plan),
        "response": response,
    }
    run_path.write_text(json.dumps(run_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_path


def _parse_topic_data(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)


def run_deep_research_json(**kwargs: str) -> str:
    return json.dumps(asdict(run_deep_research(**kwargs)), indent=2, sort_keys=True)
