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

No topic archive data is committed. Project-level documentation may live in `docs/`, but research topics, source logs, evidence, notes, briefs, and AI outputs belong in Postgres.

## Postgres-First Direction

The intended direction is:

```text
Postgres -> evidence and source store -> dashboard
```

Postgres is the living research workspace and system of record. GitHub is for code, schema, tests, CI, project documentation, and deployment workflow.

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

- Reads Postgres topics and structured evidence when available.
- Keeps temporary legacy file fallback paths during migration.
- Shows an empty state when no research rows exist.
- Includes local Postgres setup guidance.

Target behavior:

- Read from Postgres.
- Treat empty database tables as a normal first-run state.
- Remove legacy file fallback paths once the hosted database is live.
- Make evidence easier to inspect and compare.

Deployment details live in [DEPLOYMENT.md](DEPLOYMENT.md).

## CLI Role

The CLI supports local research operations:

```bash
python3 -m project_india.cli db-init
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
  -> project-india db-status
  -> streamlit run dashboard.py
```

Research publication flow:

```text
research sources and evidence
  -> store and normalize in Postgres
  -> review facts, assumptions, and uncertainty
  -> dashboard presents approved insights from Postgres
```
