# Project India

Project India is a research and analysis system for documenting, decoding, and contributing to India's geopolitical position and internal growth across sectors.

Live dashboard: https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/

## Direction

The project is moving to a Postgres-first research architecture:

```text
local Postgres -> research evidence store -> dashboard -> curated archive exports
```

Git remains the curated project archive. Postgres is the living workspace for topics, sources, evidence, metrics, timelines, gaps, and research runs.

## Core Areas

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

- `db/schema.sql` - local Postgres schema
- `compose.yaml` - local Postgres service
- `project_india/postgres_db.py` - import/status helpers for Postgres
- `dashboard.py` - Streamlit presentation surface
- `docs/` - curated Markdown research archive
- `sources/` - source logs
- `analyses/reports/` - research briefs
- `data/processed/topic_data/` - structured archived evidence
- `data/processed/research_index.json` - archived topic index
- `data/processed/research_runs/` - archived run records
- `AGENTS.md` and `agent-ref/` - guidance for future Codex sessions

## Local Postgres

Start the local database:

```bash
docker compose up -d postgres
```

Install DB dependencies:

```bash
python3 -m pip install -e ".[db]"
```

Initialize and import the current archive:

```bash
python3 -m project_india.cli db-init
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

Default local database URL:

```text
postgresql://project_india:project_india_local@localhost:5433/project_india
```

## Archive Commands

Create archive files for a topic:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug --category sectors
```

Rebuild the committed archive index:

```bash
python3 -m project_india.cli index-research
```

Run the dashboard locally:

```bash
python3 -m pip install -r requirements.txt
streamlit run dashboard.py
```

## Working Principles

- Use credible primary and secondary sources.
- Separate facts, interpretation, and opinion.
- Preserve citations and dates for time-sensitive claims.
- Track assumptions and uncertainty clearly.
- Use AI to accelerate research, analysis, synthesis, and publication while keeping human judgment responsible for conclusions.

## Next Step

The next architectural step is to make `dashboard.py` read from Postgres first and use committed archive files only as fallback.
