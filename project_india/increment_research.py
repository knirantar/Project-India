"""Incremental research: developments tracking, gap exploration, fact-checking."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from project_india import paths
from project_india.deep_research import _existing_context, _files_for, _extract_tag, TAG_NAMES
from project_india.research_plan import plan_research
from project_india.topics import TOPIC_FOLDERS

try:
    import openai
except ImportError:
    openai = None  # type: ignore


StrategyType = Literal["developments", "gaps", "factcheck", "rotate"]


@dataclass(frozen=True)
class IncrementResearchOutputs:
    topic: str
    slug: str
    category: str
    strategy: str
    model: str
    topic_path: str
    source_path: str
    brief_path: str
    run_path: str
    api_cost_usd: float
    summary: str


def _load_config() -> dict:
    """Load research_config.json."""
    config_path = paths.ROOT / "research_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"research_config.json not found at {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def _write_config(config: dict) -> None:
    """Write research_config.json."""
    config_path = paths.ROOT / "research_config.json"
    config_path.write_text(json.dumps(config, indent=4), encoding="utf-8")


def _find_topic_config(slug: str) -> dict | None:
    """Find topic in config by slug."""
    config = _load_config()
    for topic in config.get("topics", []):
        if topic.get("slug") == slug:
            return topic
    return None


def _estimate_strategy_cost(strategy: str) -> float:
    """Return configured estimated API cost for a strategy."""
    config = _load_config()
    strategy_config = config.get("strategies", {}).get(strategy, {})
    return float(strategy_config.get("api_cost_estimate_usd", 0.30))


def _get_next_strategy(slug: str) -> str:
    """Get next strategy in rotation for a topic."""
    topic = _find_topic_config(slug)
    if not topic:
        return "developments"
    
    strategies = topic.get("strategy", {}).get("rotation", ["developments"])
    current_index = topic.get("strategy", {}).get("current_index", 0)
    return strategies[current_index % len(strategies)]


def _next_scheduled_run(schedule: dict, now: datetime) -> str | None:
    """Compute the next scheduled run date for dashboard metadata."""
    frequency = schedule.get("frequency")

    if frequency == "daily":
        return (now.date() + timedelta(days=1)).isoformat()

    if frequency == "weekly":
        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        target_weekday = weekdays.get(str(schedule.get("day_of_week", "monday")).lower(), 0)
        days_ahead = (target_weekday - now.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (now.date() + timedelta(days=days_ahead)).isoformat()

    if frequency == "monthly":
        raw_day = schedule.get("day_of_month") or schedule.get("day_of_week") or 1
        try:
            day = max(1, min(int(raw_day), 28))
        except (TypeError, ValueError):
            day = 1

        year = now.year
        month = now.month
        if now.day >= day:
            month += 1
            if month > 12:
                month = 1
                year += 1
        return datetime(year, month, day, tzinfo=UTC).date().isoformat()

    return None


def _update_config_after_run(slug: str, strategy: str, api_cost_usd: float) -> None:
    """Update budget, schedule, and strategy metadata after a successful run."""
    config = _load_config()
    now = datetime.now(UTC)

    for topic in config.get("topics", []):
        if topic.get("slug") != slug:
            continue

        strategy_config = topic.setdefault("strategy", {})
        rotation = strategy_config.get("rotation", [strategy])
        if rotation:
            try:
                completed_index = rotation.index(strategy)
            except ValueError:
                completed_index = int(strategy_config.get("current_index", 0))
            strategy_config["current_index"] = (completed_index + 1) % len(rotation)

        schedule = topic.setdefault("schedule", {})
        schedule["last_run_date"] = now.date().isoformat()
        schedule["next_scheduled_run"] = _next_scheduled_run(schedule, now)

        metadata = topic.setdefault("metadata", {})
        metadata["api_calls_month"] = int(metadata.get("api_calls_month", 0)) + 1
        metadata["last_cost_usd"] = api_cost_usd
        metadata["total_cost_month"] = round(
            float(metadata.get("total_cost_month", 0)) + api_cost_usd,
            4,
        )

        budget = config.setdefault("budget", {})
        budget["current_month_spent_usd"] = round(
            float(budget.get("current_month_spent_usd", 0)) + api_cost_usd,
            4,
        )
        break

    _write_config(config)


def _build_increment_prompt(
    title: str,
    category: str,
    strategy: str,
    existing_context: str,
    planning_context: str,
) -> str:
    """Build prompt for incremental research based on strategy."""
    config = _load_config()
    strategy_config = config.get("strategies", {}).get(strategy, {})
    modifier = strategy_config.get("prompt_modifier", "")
    
    base_prompt = f"""You are helping with incremental research for Project India.

Topic: {title}
Category: {category}
Research Strategy: {strategy}
Current Date: {datetime.now(UTC).strftime('%Y-%m-%d')}

=== EXISTING CONTEXT ===
{existing_context[:12000]}

=== PLANNING CONTEXT ===
{planning_context[:3000]}

=== RESEARCH STRATEGY ===
{modifier}

=== INSTRUCTIONS ===
1. Research ONLY the specific aspect indicated by the strategy above
2. Be concise: focus on NEW insights, not repeating existing content
3. Cite sources inline with proper attribution
4. Use these XML tags for output:

<TOPIC_NOTE>
[Updated topic note section - only new/changed content]
[Include confidence levels and caveats]
</TOPIC_NOTE>

<SOURCE_LOG>
[New sources discovered, formatted as: source_name (URL), accessed YYYY-MM-DD - brief description]
</SOURCE_LOG>

<BRIEF>
[Updated executive summary - reflect new findings]
</BRIEF>

<CHANGES_SUMMARY>
[Bullet list of what changed: what was added, what confidence increased/decreased, what contradictions emerged]
</CHANGES_SUMMARY>

Start your response with <TOPIC_NOTE> and end with </CHANGES_SUMMARY>.
"""
    return base_prompt


def _call_openai_increment(
    prompt: str,
    model: str = "gpt-5",
) -> str:
    """Call OpenAI API for incremental research."""
    if not openai:
        raise ImportError("openai package not installed. Install with: pip install openai")
    
    client = openai.OpenAI()  # Uses OPENAI_API_KEY env var
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a rigorous research assistant for Project India, focused on incremental updates and verification.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=3000,
    )
    return response.choices[0].message.content or ""


def _update_files_incremental(
    title: str,
    slug: str,
    category: str,
    strategy: str,
    model_response: str,
    files_for: object,
) -> dict[str, Path]:
    """Update topic files with incremental research results."""
    outputs = {}
    
    # Extract tagged sections
    try:
        topic_update = _extract_tag(model_response, "TOPIC_NOTE")
        sources_update = _extract_tag(model_response, "SOURCE_LOG")
        brief_update = _extract_tag(model_response, "BRIEF")
        changes_summary = _extract_tag(model_response, "CHANGES_SUMMARY")
    except ValueError as e:
        raise ValueError(f"Model response missing required tags: {e}")
    
    # Append updates to existing files (not replacing)
    topic_path = paths.TOPIC_FOLDERS[category] / f"{slug}.md"
    if topic_path.exists():
        existing = topic_path.read_text(encoding="utf-8")
        # Add update section with timestamp
        update_section = f"\n\n### Update ({datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}) — Strategy: {strategy}\n{topic_update}"
        topic_path.write_text(existing + update_section, encoding="utf-8")
    outputs["topic"] = topic_path
    
    # Update sources (append)
    sources_path = paths.SOURCES / f"{slug}-sources.md"
    if sources_path.exists():
        existing = sources_path.read_text(encoding="utf-8")
        sources_section = f"\n\n## Update ({datetime.now(UTC).strftime('%Y-%m-%d')}) — {strategy}\n{sources_update}"
        sources_path.write_text(existing + sources_section, encoding="utf-8")
    outputs["sources"] = sources_path
    
    # Update brief (replace with latest version)
    brief_path = paths.REPORTS / f"{slug}-brief.md"
    brief_path.write_text(brief_update, encoding="utf-8")
    outputs["brief"] = brief_path
    
    return outputs


def run_incremental_research(
    title: str,
    slug: str,
    category: str,
    model: str = "gpt-5",
    strategy: StrategyType = "developments",
) -> IncrementResearchOutputs:
    """
    Run incremental research on a topic.
    
    Strategies:
    - developments: Research new developments since last run
    - gaps: Explore one unexplored gap
    - factcheck: Verify and update existing facts
    - rotate: Use next strategy in config rotation
    """
    
    # Resolve strategy
    if strategy == "rotate":
        strategy = _get_next_strategy(slug)  # type: ignore
    
    # Get existing context
    files = _files_for(title, slug, category)
    existing_context = _existing_context(files)
    
    # Get planning context
    plan = plan_research(title, slug=slug, category=category)
    planning_context = f"""
Missing Questions: {', '.join(plan.missing_questions[:3])}
Unexplored Subtopics: {', '.join(plan.unexplored_subtopics[:3])}
Gaps: {plan.api_scope}
"""
    
    # Build and call API
    prompt = _build_increment_prompt(
        title=title,
        category=category,
        strategy=strategy,  # type: ignore
        existing_context=existing_context,
        planning_context=planning_context,
    )
    
    model_response = _call_openai_increment(prompt, model=model)
    
    # Update files
    updated_files = _update_files_incremental(
        title=title,
        slug=slug,
        category=category,
        strategy=strategy,  # type: ignore
        model_response=model_response,
        files_for=files,
    )
    
    # Extract changes summary
    try:
        summary = _extract_tag(model_response, "CHANGES_SUMMARY")
    except ValueError:
        summary = "Update completed."
    
    api_cost_usd = _estimate_strategy_cost(strategy)  # type: ignore[arg-type]
    _update_config_after_run(slug, strategy, api_cost_usd)  # type: ignore[arg-type]

    # Write run record
    run_path = paths.RESEARCH_RUNS / f"{slug}-increment-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.json"
    run_record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "title": title,
        "slug": slug,
        "category": category,
        "strategy": strategy,
        "model": model,
        "api_cost_usd": api_cost_usd,
        "summary": summary,
        "files_updated": {k: str(v) for k, v in updated_files.items()},
    }
    run_path.write_text(json.dumps(run_record, indent=2), encoding="utf-8")
    
    return IncrementResearchOutputs(
        topic=title,
        slug=slug,
        category=category,
        strategy=strategy,  # type: ignore
        model=model,
        topic_path=str(updated_files.get("topic", "")),
        source_path=str(updated_files.get("sources", "")),
        brief_path=str(updated_files.get("brief", "")),
        run_path=str(run_path),
        api_cost_usd=api_cost_usd,
        summary=summary,
    )
