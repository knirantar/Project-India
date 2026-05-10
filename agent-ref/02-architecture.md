# Current Project Architecture

Project India is a repo-memory-first research system.

The main public-app flow is:

```text
topic intake -> research plan -> local context -> deep research -> topic data -> brief -> research index -> Streamlit dashboard
```

Core folders:

- `docs/` - human-readable research notes, sector notes, geopolitics notes, and internal-growth notes
- `sources/` - source logs by topic
- `analyses/reports/` - briefs, timelines, reports
- `data/raw/` - raw datasets
- `data/processed/` - generated and structured research data
- `data/processed/topic_data/` - structured evidence used by dashboard insight pages
- `data/processed/research_index.json` - lightweight research database
- `data/processed/research_context/` - local context bundles for topics
- `data/processed/research_plans/` - gap analysis before API calls
- `data/processed/research_runs/` - records of AI research runs
- `project_india/` - Python workflow package
- `.github/workflows/topic-intake-research.yml` - app-triggered workflow for researching new topics
- `.github/workflows/scheduled-research.yml` - scheduled and manual incremental research workflow
- `.github/dependabot.yml` - dependency and GitHub Actions update checks
- `dashboard.py` - Streamlit dashboard for topic status, budget, research history, and structured evidence
- `research_config.json` - topic schedule, strategy, and budget configuration
- `.streamlit/config.toml` - Streamlit Cloud theme and server configuration
- `requirements.txt` - Streamlit Cloud dependency entrypoint
