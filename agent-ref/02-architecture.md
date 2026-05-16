# Current Project Architecture

Project India is being simplified into a Postgres-first research system.

Current direction:

```text
Postgres -> evidence and source store -> dashboard
```

GitHub is the codebase, schema, CI, workflow, and documentation home. Postgres is the living research workspace and system of record.

The public Streamlit app now prefers Postgres data and has temporary legacy archive-oriented fallback paths until the hosted database is live.

Core files and folders:

- `db/schema.sql` - local Postgres schema for topics, sources, evidence, and run records
- `compose.yaml` - local Postgres service
- `project_india/postgres_db.py` - database initialization, import, and status helpers
- `dashboard.py` - Streamlit dashboard and presentation surface
- `docs/` - project documentation for contributors and collaborators
- `.github/dependabot.yml` - Python dependency update checks
- `requirements.txt` - Streamlit Cloud dependency entrypoint

No topic archive data should be committed. Project-level documentation may live in `docs/`. Topics, source logs, evidence, notes, briefs, metrics, and research runs belong in Postgres.

Removed legacy runtime:

- GitHub Actions topic intake
- GitHub Actions schedule configuration
- GitHub Actions incremental research
- `research_config.json`
- old incremental/scheduling Python modules
- old archive-first topic generation and API research modules

Local Postgres flow:

```text
docker compose up -d postgres -> db-init -> db-status
```

Use `agent-ref/03-data-and-research-flow.md` for the database direction and table map.
