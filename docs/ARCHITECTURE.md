# Architecture

Project India is a Postgres-first research and analysis system for India's geopolitical position and internal growth.

## Current Architecture

The current repo contains:

- `dashboard.py` - Streamlit dashboard and public presentation surface
- `project_india/cli.py` - command-line entrypoint for local database operations
- `project_india/postgres_db.py` - Postgres initialization, import, and status helpers
- `db/schema.sql` - schema for topics, sources, evidence, briefs, metrics, and run records
- `compose.yaml` - local Postgres service
- `agent-ref/` - project memory and operating guidance for Codex sessions

No topic archive data is committed right now. Project-level documentation may live in `docs/`, but published topic archive folders such as `sources/`, `analyses/`, and `data/processed/` should be created only when research is ready to publish.

## Postgres-First Direction

The intended direction is:

```text
local Postgres -> evidence and source store -> dashboard -> curated archive exports
```

Postgres is the living research workspace. Git remains the curated archive and codebase.

Postgres should hold:

- topics
- source logs and source entries
- briefs and topic notes
- metrics, comparisons, timelines, and tables
- data gaps
- research runs
- exported artifact metadata

## Streamlit Dashboard Role

The Streamlit dashboard is the current user-facing surface. It should present research clearly with insight, evidence, charts, tables, timelines, and data gaps.

Current behavior:

- Reads committed archive files.
- Shows an empty state when no topic archive data exists.
- Includes local Postgres setup guidance.

Target behavior:

- Read from Postgres first.
- Fall back to committed archive files for published research.
- Make evidence easier to inspect and compare.

## CLI Role

The CLI supports local research operations:

```bash
python3 -m project_india.cli db-init
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

It should stay practical and scriptable. New commands should support repeatable local workflows rather than one-off manual steps.

## Future FastAPI/API Layer

A FastAPI or similar API layer may be added later when the project needs:

- shared access to hosted research data
- authenticated contributor workflows
- dashboard/API separation
- background ingestion or AI analysis jobs
- integrations with external tools

Until then, the repo should keep the architecture simple: local Postgres, CLI helpers, and Streamlit.

## Data Flow

Local development flow:

```text
docker compose up -d postgres
  -> project-india db-init
  -> project-india db-import-repo
  -> project-india db-status
  -> streamlit run dashboard.py
```

Research publication flow:

```text
research sources and evidence
  -> store and normalize in Postgres
  -> review facts, assumptions, and uncertainty
  -> publish curated archive exports
  -> dashboard presents published insights
```
