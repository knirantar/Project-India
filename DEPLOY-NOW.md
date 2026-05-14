# Deploy And Use Project India

Production dashboard:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

## Streamlit App Settings

```text
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
Python: 3.11 or 3.12
```

The public Streamlit app currently reads committed archive files from the repo. GitHub Actions research dispatch has been removed as part of the Postgres-first cleanup.

## Local Postgres

Start the database:

```bash
docker compose up -d postgres
```

Install dependencies:

```bash
python3 -m pip install -e ".[db]"
```

Initialize and import the repo archive:

```bash
python3 -m project_india.cli db-init
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

Default local database URL:

```text
postgresql://project_india:project_india_local@localhost:5433/project_india
```

## Current Direction

Postgres is the living data layer. Git is the curated archive.

Next, migrate the dashboard to read Postgres first, then fall back to committed files when no database is configured.
