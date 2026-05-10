# Project India

Project India is a research and analysis repository for documenting, decoding, and contributing to India's geopolitical position and internal growth across sectors.

The aim is to build a living knowledge base that combines structured research, data analysis, policy understanding, sector-by-sector tracking, and AI-assisted workflows.

Live dashboard: https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/

## Focus Areas

- Geopolitics and foreign policy
- Economy, trade, and industry
- Infrastructure and urban development
- Energy, climate, and natural resources
- Agriculture and food systems
- Defense, security, and strategic affairs
- Technology, AI, and digital public infrastructure
- Education, healthcare, and human development
- Governance, law, and institutions
- Culture, society, and demographic change

## Repository Structure

- `docs/geopolitics/` - geopolitical notes, country relationships, global strategy
- `docs/sectors/` - sector-wise documentation and analysis
- `docs/internal-growth/` - domestic development, governance, and social indicators
- `docs/research-notes/` - raw notes, reading summaries, open questions
- `docs/ai-workflows/` - prompts, research methods, automation workflows
- `docs/briefs/` - polished policy and strategy briefs
- The production Streamlit app is the main presentation surface.
- `data/` - datasets, cleaned data, and derived tables
- `sources/` - source lists, citations, and reference material
- `analyses/` - deeper essays, models, dashboards, and reports
- `project_india/` - Python helpers for repeatable research workflows
- `workflows/` - documented research and app workflow processes

## Integrated Workflow

Project India uses three connected layers:

- Markdown is the knowledge base.
- Python is the workflow engine.
- Briefs, dashboards, and essays are the communication layer.

Key reference files:

- `docs/research-notes/project-roadmap.md` - overall roadmap
- `docs/research-notes/data-and-indexing.md` - how repo memory, data, and API calls work
- `docs/research-notes/dependency-graph.md` - code, data, and maintenance dependency graph
- `AGENTS.md` - guidance for future Codex sessions

Create a new topic workflow manually with:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug
```

For topics outside sectors, pass a category:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug --category internal-growth
```

Build a reusable research index:

```bash
python3 -m project_india.cli index-research
```

The index is written to `data/processed/research_index.json` and acts as the project's lightweight research database. It links topic notes, source logs, briefs, structured topic data, and dashboard-ready outputs by slug.

Structured evidence for each topic belongs in:

```text
data/processed/topic_data/<topic-slug>.json
```

This is where metrics, comparisons, timelines, tables, sources, and data gaps live. The Streamlit dashboard uses this file for charts and evidence boards.

Plan research from local repo memory before spending API calls:

```bash
python3 -m project_india.cli plan-research "Topic Name" --slug topic-slug --category sectors
```

This writes a plan under `data/processed/research_plans/` and a local context bundle under `data/processed/research_context/`.

Run source-backed AI research before building outputs:

```bash
python3 -m pip install -e ".[research]"
OPENAI_API_KEY=... python3 -m project_india.cli deep-research "Topic Name" --slug topic-slug --category sectors
```

The current production workflow uses the Streamlit dashboard as the presentation surface. New app-submitted topics run through the GitHub Actions workflow `Topic Intake Research`, which creates research notes, source logs, briefs, structured topic data, and the research index for the dashboard.

## Working Principles

- Use credible primary and secondary sources.
- Separate facts, interpretation, and opinion.
- Preserve citations and dates for time-sensitive claims.
- Track assumptions and uncertainty clearly.
- Use AI to accelerate research, analysis, synthesis, and publication, while keeping human judgment responsible for conclusions.

## Status

This project is just beginning.
