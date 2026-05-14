# Local Postgres Research Store

Project India is moving toward a database-first research workflow.

The repo remains the durable archive, but local Postgres should become the living workspace for topic research, source capture, evidence extraction, and dashboard-ready insight data.

## Why This Exists

GitHub Actions and committed JSON files are useful for audit trails, but they are not ideal as the primary research runtime.

Local Postgres gives us:

- a queryable source and evidence store
- cleaner topic/run/source history
- faster local iteration
- a better path toward a research worker
- less dependence on GitHub commits for every research update

## Local Setup

Start Postgres:

```bash
docker compose up -d postgres
```

Set the local database URL:

```bash
export PROJECT_INDIA_DATABASE_URL="postgresql://project_india:project_india_local@localhost:5433/project_india"
```

Install database dependencies:

```bash
python3 -m pip install -e ".[db]"
```

Initialize the schema:

```bash
python3 -m project_india.cli db-init
```

Import current repo research files:

```bash
python3 -m project_india.cli db-import-repo
```

Check table counts:

```bash
python3 -m project_india.cli db-status
```

## Current Schema

The first local schema stores:

- `topics`
- `topic_documents`
- `briefs`
- `source_logs`
- `source_entries`
- `research_runs`
- `topic_metrics`
- `topic_comparisons`
- `comparison_items`
- `timeline_events`
- `topic_tables`
- `data_gaps`
- `research_artifacts`

## Intended Direction

Next refinement should move the Streamlit dashboard from reading only committed JSON/Markdown into reading Postgres first, with repo files as fallback.

After that, a research worker can write directly to Postgres:

```text
topic request -> source fetch -> extraction -> evidence tables -> synthesis -> dashboard
```

GitHub should then be used for code, tests, deployments, and curated exports rather than every live research update.
