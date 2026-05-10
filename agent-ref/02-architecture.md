# Current Project Architecture

Project India is a repo-memory-first research system.

The main flow is:

```text
topic -> research plan -> local context -> deep research only if needed -> topic data -> brief/outline -> presentation -> research index
```

Core folders:

- `docs/` - human-readable research notes, sector notes, geopolitics notes, internal-growth notes, presentation outlines
- `sources/` - source logs by topic
- `analyses/reports/` - briefs, timelines, reports
- `data/raw/` - raw datasets
- `data/processed/` - generated and structured research data
- `data/processed/topic_data/` - structured evidence used by presentations
- `data/processed/research_index.json` - lightweight research database
- `data/processed/research_context/` - local context bundles for topics
- `data/processed/research_plans/` - gap analysis before API calls
- `data/processed/research_runs/` - records of AI research runs
- `project_india/` - Python workflow package
- `.github/workflows/generate-presentation.yml` - manual GitHub workflow for generating topic presentations
- `.github/workflows/scheduled-research.yml` - scheduled and manual incremental research workflow
- `.github/dependabot.yml` - dependency and GitHub Actions update checks
- `dashboard.py` - Streamlit dashboard for topic status, budget, research history, and structured evidence
- `research_config.json` - topic schedule, strategy, and budget configuration
- `.streamlit/config.toml` - Streamlit Cloud theme and server configuration
- `requirements.txt` - Streamlit Cloud dependency entrypoint
