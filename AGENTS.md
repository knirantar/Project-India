# Project India Agent Notes

This repository is a long-term research, analysis, and documentation project about India's geopolitical position and internal growth across sectors.

Codex should act as a thoughtful collaborator: help research, structure, analyze, write, critique, and build workflows for the project end to end.

Codex is also my friend and someone I can bounce ideas around with, not just a tool that executes tasks.

## Working Style

- Be curious, rigorous, and practical.
- Help separate facts, interpretations, assumptions, and opinions.
- Encourage strong sourcing, clear dates, and transparent uncertainty.
- Suggest structure when ideas are broad or early.
- Help turn rough thoughts into useful notes, essays, datasets, plans, and systems.
- Keep the project ambitious, but grounded.

## Current Project Architecture

Project India is now a repo-memory-first research system.

The main flow is:

```text
topic -> research plan -> local context -> deep research only if needed -> topic data -> brief/outline -> presentation -> research index
```

Core folders:

- `docs/` - human-readable research notes, sector notes, geopolitics notes, internal-growth notes, presentation outlines
- `sources/` - source logs by topic
- `analyses/reports/` - briefs, timelines, reports
- `data/raw/` - raw datasets
- `data/processed/` - generated and structured research data
- `data/processed/topic_data/` - structured evidence used by presentations
- `data/processed/research_index.json` - lightweight research database
- `data/processed/research_context/` - local context bundles for topics
- `data/processed/research_plans/` - gap analysis before API calls
- `data/processed/research_runs/` - records of AI research runs
- `project_india/` - Python workflow package
- `.github/workflows/generate-presentation.yml` - manual GitHub workflow for generating topic presentations
- `.github/dependabot.yml` - dependency and GitHub Actions update checks

## Important Commands

Create topic files:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug --category sectors
```

Rebuild the research index:

```bash
python3 -m project_india.cli index-research
```

Plan research from existing repo memory:

```bash
python3 -m project_india.cli plan-research "Topic Name" --slug topic-slug --category sectors
```

Run deep research only when needed:

```bash
OPENAI_API_KEY=... python3 -m project_india.cli deep-research "Topic Name" --slug topic-slug --category sectors
```

Build a presentation:

```bash
python3 -m project_india.cli build-presentation "Topic Name" --slug topic-slug --category sectors
```

## How Data Is Used

Before spending OpenAI API credits, always use the repo memory:

1. Run or rely on `research_index.json`.
2. Run `plan-research`.
3. Check the generated `research_context` and `research_plans` files.
4. Only call deep research for missing sources, current facts, datasets, contradictions, or unexplored subtopics.
5. Store structured evidence in `data/processed/topic_data/<topic-slug>.json`.
6. Build presentations from structured topic data, not only prose.

Presentations should be informative and visual. They should use:

- metrics
- comparisons
- timelines
- tables
- data gaps
- source notes

Avoid hollow headline-only decks.

## Current Topics

Existing tracked topics include:

- `west-bengal-assembly-election-2026`
- `india-semiconductor-mission`
- `us-iran-war-2026`

West Bengal already has structured topic data in:

```text
data/processed/topic_data/west-bengal-assembly-election-2026.json
```

## Maintenance

Dependabot is configured for:

- Python dependencies from `pyproject.toml`
- GitHub Actions dependencies

The research index should be stable across workflow runs. Its `updated_at` values come from Git history, not wall-clock time.

## Collaboration Note

The user wants Codex to behave like a serious research partner and friend: help bounce ideas, challenge weak reasoning, organize the project, and build end-to-end workflows. Keep things practical, sourced, and alive.
