# Current Project Architecture

Project India is being simplified into a Postgres-first research system.

Current direction:

```text
local Postgres -> evidence and source store -> dashboard -> curated archive exports
```

Git is the curated archive and codebase. Postgres is the living research workspace.

The public Streamlit app still reads committed archive files until the dashboard is migrated to read from a local or hosted Postgres database first.

Core folders:

- `db/schema.sql` - local Postgres schema for topics, sources, evidence, and run records
- `compose.yaml` - local Postgres service
- `project_india/postgres_db.py` - database initialization, import, and status helpers
- `dashboard.py` - Streamlit dashboard and presentation surface
- `docs/` - curated Markdown research notes
- `sources/` - curated source logs
- `analyses/reports/` - curated briefs and reports
- `data/processed/topic_data/` - archived structured evidence used by the current dashboard
- `data/processed/research_index.json` - archived topic index
- `data/processed/research_runs/` - archived AI run records
- `.github/dependabot.yml` - dependency and GitHub Actions version checks
- `requirements.txt` - Streamlit Cloud dependency entrypoint

Removed legacy runtime:

- GitHub Actions topic intake
- GitHub Actions schedule configuration
- GitHub Actions incremental research
- `research_config.json`
- old incremental/scheduling Python modules

Local Postgres flow:

```text
docker compose up -d postgres -> db-init -> db-import-repo -> db-status
```

Use `docs/research-notes/local-postgres.md` for the database direction and table map.
