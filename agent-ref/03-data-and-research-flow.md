# Data And Research Flow

The preferred working store is local Postgres.

For local development:

1. Start Postgres with `docker compose up -d postgres`.
2. Initialize schema with `python3 -m project_india.cli db-init`.
3. Import committed archive data with `python3 -m project_india.cli db-import-repo`.
4. Inspect table counts with `python3 -m project_india.cli db-status`.

Postgres should hold:

- topics
- source logs and source entries
- briefs
- topic notes
- metrics
- comparisons
- timelines
- tables
- data gaps
- research runs
- archive artifacts

The committed repo can still act as a curated archive when exports exist:

- `docs/` for project-level documentation and future polished topic notes
- `sources/` for source logs
- `analyses/reports/` for briefs
- `data/processed/topic_data/` for archived structured evidence
- `data/processed/research_index.json` for the archived topic index
- `data/processed/research_runs/` for archived run metadata

No topic archive data is committed right now. Treat Postgres as the source of truth until a topic is intentionally exported.

Dashboard insight pages should be informative and visual. They should use:

- metrics
- comparisons
- timelines
- tables
- data gaps
- source notes

Avoid hollow headline-only pages.

Next architecture step:

```text
dashboard reads Postgres first -> falls back to committed archive files
```

The legacy GitHub Actions research runtime and archive-first API research commands have been removed. Do not rebuild the old workflow-dispatch path unless the project deliberately chooses a hosted worker strategy.
