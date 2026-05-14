# Data And Indexing

Project India is moving toward a Postgres-first research system. Existing repository memory should still be used before spending OpenAI API credits.

## Data Locations

Topic notes:

- `docs/geopolitics/`
- `docs/internal-growth/`
- `docs/sectors/`
- `docs/research-notes/`

Source logs:

- `sources/<topic-slug>-sources.md`

Briefs and reports:

- `analyses/reports/<topic-slug>-brief.md`

Dashboard-ready structured evidence:

- `data/processed/topic_data/<topic-slug>.json`

Structured topic data:

- `data/processed/topic_data/<topic-slug>.json`

Research context bundles:

- `data/processed/research_context/<topic-slug>.md`

Research plans:

- `data/processed/research_plans/<topic-slug>.json`

Research run records:

- `data/processed/research_runs/<topic-slug>.json`

Global research index:

- `data/processed/research_index.json`

Local Postgres:

- `db/schema.sql`
- `topics`
- `source_entries`
- `topic_metrics`
- `timeline_events`
- `data_gaps`
- `research_runs`

## How Existing Data Is Used

The current archive flow is repo-memory first.

1. `project-india index-research`

   Rebuilds `data/processed/research_index.json` from existing topic notes, source logs, briefs, outlines, decks, and topic data.

2. `project-india plan-research "<Topic>" --slug <topic-slug> --category <category>`

   Audits existing repository material before any API call.

   It checks:

   - topic note
   - source log
   - brief
   - structured topic data
   - structured topic data
   - related records in the research index
   - relevant files in `data/raw/` and `data/processed/`

   It writes:

   - `data/processed/research_context/<topic-slug>.md`
   - `data/processed/research_plans/<topic-slug>.json`

3. `project-india deep-research`

   Uses the research plan and local context first. It calls OpenAI only when the plan says there are gaps, or when `--force-api` is used.

   It searches only for:

   - missing sources
   - current facts
   - datasets
   - conflicting claims
   - unexplored subtopics

4. Streamlit dashboard render

   Uses `data/processed/topic_data/<topic-slug>.json` before prose. This creates more informative app pages with metrics, comparisons, timelines, tables, and data gaps.

5. Postgres import

   `project-india db-import-repo` imports the committed archive into local Postgres for queryable development.

## How API Spending Is Minimized

- The planner checks local files first.
- If topic notes, source logs, briefs, outlines, and structured data are already strong enough, the API call can be skipped.
- `--force-api` should be used only when freshness, missing data, or a new analytical angle is needed.
- Generated context and plan files are deterministic where possible to reduce Git conflicts and repeated churn.

## Structured Topic Data Shape

Each serious topic should have:

```json
{
  "topic": "Topic name",
  "status": "provisional|researched|verified",
  "metrics": [],
  "comparisons": [],
  "timeline": [],
  "tables": [],
  "data_gaps": []
}
```

This file is the main bridge between research and the dashboard.
