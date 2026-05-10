from __future__ import annotations

import json
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from project_india import paths
from project_india.research_db import build_index, write_index
from project_india.topics import TOPIC_FOLDERS, create_topic, slugify

PLACEHOLDER_TOKENS = {"TBD", "TBD.", "...", "- TBD", "| TBD | TBD | TBD | TBD |"}


@dataclass(frozen=True)
class ExistingAsset:
    kind: str
    path: str
    bytes: int
    placeholder_score: int


@dataclass(frozen=True)
class ResearchPlan:
    title: str
    slug: str
    category: str
    content_hash: str
    existing_assets: list[ExistingAsset]
    related_records: list[dict[str, str | None]]
    local_context_path: str
    missing_questions: list[str]
    unexplored_subtopics: list[str]
    recommendation: str
    should_call_api: bool
    api_scope: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _placeholder_score(text: str) -> int:
    return sum(text.count(token) for token in PLACEHOLDER_TOKENS)


def _asset(kind: str, path: Path) -> ExistingAsset | None:
    if not path.exists():
        return None
    text = _read(path) if path.suffix.lower() in {".md", ".json", ".csv", ".txt"} else ""
    return ExistingAsset(
        kind=kind,
        path=str(path.relative_to(paths.ROOT)),
        bytes=path.stat().st_size,
        placeholder_score=_placeholder_score(text),
    )


def _topic_files(slug: str, category: str) -> list[tuple[str, Path]]:
    return [
        ("topic_note", TOPIC_FOLDERS[category] / f"{slug}.md"),
        ("source_log", paths.SOURCES / f"{slug}-sources.md"),
        ("brief", paths.REPORTS / f"{slug}-brief.md"),
        ("presentation_outline", paths.PRESENTATIONS / f"{slug}-outline.md"),
        ("generated_deck", paths.PRESENTATIONS / f"{slug}-generated-deck.pptx"),
    ]


def _data_assets(slug: str) -> list[tuple[str, Path]]:
    assets: list[tuple[str, Path]] = []
    for root in [paths.RAW_DATA, paths.PROCESSED_DATA]:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or slug not in path.name:
                continue
            relative_parts = path.relative_to(paths.PROCESSED_DATA).parts
            if relative_parts and relative_parts[0] in {
                "research_context",
                "research_plans",
                "research_runs",
            }:
                continue
            if path.name == "research_index.json":
                continue
            if path.suffix.lower() in {".pptx", ".png", ".jpg", ".jpeg", ".pdf"}:
                continue
            else:
                assets.append(("data", path))
    return assets


def _related_records(title: str, slug: str) -> list[dict[str, str | None]]:
    write_index()
    title_terms = {term.lower() for term in title.replace("-", " ").split() if len(term) > 3}
    related = []
    for record in build_index():
        overlap = title_terms.intersection(record.title.lower().replace("-", " ").split())
        if record.slug == slug or overlap:
            related.append(asdict(record))
    return related[:8]


def _local_context(slug: str, assets: list[ExistingAsset]) -> Path:
    context_dir = paths.PROCESSED_DATA / "research_context"
    context_dir.mkdir(parents=True, exist_ok=True)
    context_path = context_dir / f"{slug}.md"
    sections = [f"# Local Research Context: {slug}", ""]

    for asset in assets:
        path = paths.ROOT / asset.path
        if path.suffix.lower() not in {".md", ".json", ".csv", ".txt"}:
            continue
        sections.append(f"## {asset.kind}: `{asset.path}`")
        sections.append("")
        sections.append(_read(path)[:12000])
        sections.append("")

    context_path.write_text("\n".join(sections), encoding="utf-8")
    return context_path


def _content_hash(assets: list[ExistingAsset]) -> str:
    digest = hashlib.sha256()
    for asset in assets:
        path = paths.ROOT / asset.path
        digest.update(asset.path.encode("utf-8"))
        digest.update(b"\0")
        if path.exists() and path.is_file():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _missing_questions(asset_kinds: set[str]) -> list[str]:
    questions = []
    if "source_log" not in asset_kinds:
        questions.append("Which primary and secondary sources should anchor this topic?")
    if "brief" not in asset_kinds:
        questions.append("What is the bottom-line strategic brief for this topic?")
    if "presentation_outline" not in asset_kinds:
        questions.append("What claim-led slide outline best communicates this topic?")
    if "data" not in asset_kinds:
        questions.append("What datasets or quantitative indicators are required?")
    questions.append("Which claims remain time-sensitive or unverified?")
    return questions


def _unexplored_subtopics(title: str) -> list[str]:
    return [
        f"Historical background behind {title}",
        f"Key actors and institutions shaping {title}",
        f"Latest official data and primary-source evidence for {title}",
        f"Risks, bottlenecks, and second-order effects of {title}",
        f"Future scenarios and what India should watch next for {title}",
    ]


def plan_research(
    title: str,
    slug: str | None = None,
    category: str = "sectors",
    force_api: bool = False,
) -> ResearchPlan:
    topic_slug = slugify(slug or title)
    create_topic(title, slug=topic_slug, category=category)

    assets = []
    for kind, path in [*_topic_files(topic_slug, category), *_data_assets(topic_slug)]:
        item = _asset(kind, path)
        if item:
            assets.append(item)

    related = _related_records(title, topic_slug)
    context_path = _local_context(topic_slug, assets)
    asset_kinds = {asset.kind for asset in assets}
    placeholder_total = sum(asset.placeholder_score for asset in assets)
    content_bytes = sum(asset.bytes for asset in assets if asset.kind != "generated_deck")

    should_call_api = force_api or placeholder_total > 0 or content_bytes < 6000
    recommendation = "deep-research-required" if should_call_api else "use-local-context-first"
    api_scope = (
        "Use local context first, then search only for missing sources, current facts, datasets, and unexplored subtopics."
        if should_call_api
        else "Skip deep research unless the user asks for freshness or new angles; build from local docs/data."
    )

    return ResearchPlan(
        title=title,
        slug=topic_slug,
        category=category,
        content_hash=_content_hash(assets),
        existing_assets=assets,
        related_records=related,
        local_context_path=str(context_path.relative_to(paths.ROOT)),
        missing_questions=_missing_questions(asset_kinds),
        unexplored_subtopics=_unexplored_subtopics(title),
        recommendation=recommendation,
        should_call_api=should_call_api,
        api_scope=api_scope,
    )


def write_plan(
    title: str,
    slug: str | None = None,
    category: str = "sectors",
    force_api: bool = False,
    output_path: Path | None = None,
) -> Path:
    plan = plan_research(title, slug=slug, category=category, force_api=force_api)
    output = output_path or (paths.PROCESSED_DATA / "research_plans" / f"{plan.slug}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(plan), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output
