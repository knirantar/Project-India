# Dependency Graph

This file explains how the main parts of Project India depend on each other.

## Runtime Dependencies

Core Python package:

- `project_india/`
- Python `>=3.11`
- no required runtime dependencies for basic archive file creation and indexing

Optional dependency groups:

- `analysis`
  - `pandas`
  - `matplotlib`
  - `jupyter`
- `research`
  - `openai`
- `db`
  - `psycopg`

GitHub automation:

- `.github/dependabot.yml`

The old GitHub Actions research runtime has been removed. GitHub Actions should be reserved for maintenance and deployment checks unless a hosted worker is deliberately introduced.

## Code Dependency Graph

```text
project_india.cli
  -> project_india.topics
  -> project_india.research_db
  -> project_india.research_plan
  -> project_india.deep_research
  -> project_india.postgres_db

project_india.topics
  -> project_india.paths

project_india.research_db
  -> project_india.paths
  -> git history for stable updated_at values

project_india.research_plan
  -> project_india.paths
  -> project_india.research_db
  -> project_india.topics
  -> docs/
  -> sources/
  -> analyses/
  -> data/processed/topic_data/

project_india.deep_research
  -> project_india.paths
  -> project_india.research_plan
  -> project_india.topics
  -> OpenAI Responses API when needed

project_india.postgres_db
  -> project_india.paths
  -> db/schema.sql
  -> committed archive files
  -> local Postgres
```

## Data Dependency Graph

```text
docs/<category>/<topic>.md
  -> sources/<topic>-sources.md
  -> analyses/reports/<topic>-brief.md
  -> data/processed/topic_data/<topic>.json
  -> data/processed/research_runs/<topic>.json
  -> data/processed/research_index.json
  -> local Postgres import
  -> Streamlit dashboard
```

## Security And Maintenance

Dependabot is configured for:

- Python package updates from `pyproject.toml`

Security posture:

- Keep dependencies minimal.
- Prefer optional dependency groups over a large default install.
- Keep API keys out of the repo. Use local environment variables or hosted secrets.
- Generated research data should preserve source links and confidence levels.
