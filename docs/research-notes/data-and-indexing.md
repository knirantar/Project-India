# Data And Indexing

Project India is designed to use existing repository memory before spending OpenAI API credits.

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

Presentation outlines and decks:

- `docs/presentations/<topic-slug>-outline.md`
- `docs/presentations/<topic-slug>-generated-deck.pptx`

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

## How Existing Data Is Used

The workflow is repo-memory first.

1. `project-india index-research`

   Rebuilds `data/processed/research_index.json` from existing topic notes, source logs, briefs, outlines, decks, and topic data.

2. `project-india plan-research "<Topic>" --slug <topic-slug> --category <category>`

   Audits existing repository material before any API call.

   It checks:

   - topic note
   - source log
   - brief
   - presentation outline
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

4. `project-india build-presentation`

   Uses `data/processed/topic_data/<topic-slug>.json` before prose. This creates more informative presentations with metrics, comparisons, timelines, tables, and data gaps.

## How API Spending Is Minimized

- The planner checks local files first.
- If topic notes, source logs, briefs, outlines, and structured data are already strong enough, the API call can be skipped.
- `force_research=false` in GitHub Actions avoids unnecessary calls.
- `force_research=true` should be used only when freshness, missing data, or a new analytical angle is needed.
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

This file is the main bridge between research and presentation.

