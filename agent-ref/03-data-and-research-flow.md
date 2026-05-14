# Data And Research Flow

Before spending OpenAI API credits, always use repo memory first:

1. Run or rely on `data/processed/research_index.json`.
2. Run `plan-research`.
3. Check generated `research_context` and `research_plans` files.
4. Only call deep research for missing sources, current facts, datasets, contradictions, or unexplored subtopics.
5. Store structured evidence in `data/processed/topic_data/<topic-slug>.json`.
6. Build dashboard views from structured topic data, not only prose.

Local Postgres is the next preferred working store. For local development, import repo memory into Postgres with `db-import-repo` and use the database as the place to query topics, evidence, sources, gaps, and run history.

Dashboard insight pages should be informative and visual. They should use:

- metrics
- comparisons
- timelines
- tables
- data gaps
- source notes

Avoid hollow headline-only pages.

The research index should be stable across workflow runs. Its `updated_at` values come from Git history, not wall-clock time.

Incremental scheduled research is controlled by `research_config.json` and implemented by `project_india/increment_research.py`.
It should keep costs low by rotating focused strategies: `developments`, `gaps`, and `factcheck`.
Scheduled runs should write research updates and run records, then open a pull request instead of pushing directly to protected `main`.

The Streamlit dashboard reads committed repo data only:

- `research_config.json` for topics, schedules, and budget metadata
- `data/processed/research_index.json` for repository memory
- `data/processed/topic_data/*.json` for visual topic evidence
- `data/processed/research_runs/*.json` for research history and cost trends

This is transitional. The next architecture should make the dashboard read Postgres first, then fall back to committed repo data when no database is configured.

New user-provided topics should start in the Streamlit dashboard's **Start Research** form.
The app dispatches `.github/workflows/topic-intake-research.yml` through GitHub's workflow API when Streamlit secrets are configured.
Because the app is public, workflow dispatch must be protected by an admin PIN and a server-side GitHub token in Streamlit secrets.
The intake workflow should not generate a PPTX deck or presentation outline by default; the Streamlit dashboard is the presentation mechanism.

Frequency is configured after the first deep research run. Use the dashboard's **Operations -> Schedules** page to dispatch `.github/workflows/configure-topic-schedule.yml` and set a topic to `manual`, `daily`, `weekly`, or `monthly`.
The hourly `.github/workflows/incremental-research.yml` check should only run topics that are due at their configured UTC hour.
Incremental updates must stay focused and lower cost: use existing repo context first, then run web-backed API research only for the selected strategy (`developments`, `gaps`, or `factcheck`).
