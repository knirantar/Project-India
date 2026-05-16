# Data And Research Flow

The preferred working store is local Postgres.

For local development:

1. Start Postgres with `docker compose up -d postgres`.
2. Initialize schema with `python3 -m project_india.cli db-init`.
3. Inspect table counts with `python3 -m project_india.cli db-status`.

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

The committed repo should not hold research archive data. Keep living and published research records in Postgres unless the project deliberately creates a separate export/publication system later.

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
    dashboard reads Postgres -> clean empty state when no research exists
```

The legacy GitHub Actions research runtime and archive-first API research commands have been removed. Do not rebuild the old workflow-dispatch path unless the project deliberately chooses a hosted worker strategy.
