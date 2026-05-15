# Current Project Architecture

Project India is being simplified into a Postgres-first research system.

Current direction:

```text
local Postgres -> evidence and source store -> dashboard -> curated archive exports
```

Git is the curated archive and codebase. Postgres is the living research workspace.

The public Streamlit app still reads committed archive files until the dashboard is migrated to read from a local or hosted Postgres database first.

Core files and folders:

- `db/schema.sql` - local Postgres schema for topics, sources, evidence, and run records
- `compose.yaml` - local Postgres service
- `project_india/postgres_db.py` - database initialization, import, and status helpers
- `dashboard.py` - Streamlit dashboard and presentation surface
- `.github/dependabot.yml` - Python dependency update checks
- `requirements.txt` - Streamlit Cloud dependency entrypoint

No topic archive data is committed right now. Export folders such as `docs/`, `sources/`, `analyses/`, and `data/processed/` should be created only when a topic is ready to publish from Postgres.

Removed legacy runtime:

- GitHub Actions topic intake
- GitHub Actions schedule configuration
- GitHub Actions incremental research
- `research_config.json`
- old incremental/scheduling Python modules
- old archive-first topic generation and API research modules

Local Postgres flow:

```text
docker compose up -d postgres -> db-init -> db-import-repo -> db-status
```

Use `agent-ref/03-data-and-research-flow.md` for the database direction and table map.
