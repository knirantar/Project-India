# Dependency Graph

This file explains how the main parts of Project India depend on each other.

## Runtime Dependencies

Core Python package:

- `project_india/`
- Python `>=3.11`
- No required runtime dependencies for basic topic creation and indexing.

Optional dependency groups:

- `analysis`
  - `pandas`
  - `matplotlib`
  - `jupyter`
- `presentation`
  - `python-pptx`
- `research`
  - `openai`

GitHub automation:

- `.github/workflows/generate-presentation.yml`
- `.github/dependabot.yml`
- GitHub Actions:
  - `actions/checkout`
  - `actions/setup-python`
  - `actions/upload-artifact`
  - `stefanzweifel/git-auto-commit-action`

## Code Dependency Graph

```text
project_india.cli
  -> project_india.topics
  -> project_india.research_db
  -> project_india.research_plan
  -> project_india.deep_research
  -> project_india.presentation_builder

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

project_india.presentation_builder
  -> project_india.paths
  -> project_india.topics
  -> python-pptx
  -> data/processed/topic_data/
  -> docs/presentations/
```

## Data Dependency Graph

```text
docs/<category>/<topic>.md
  -> sources/<topic>-sources.md
  -> analyses/reports/<topic>-brief.md
  -> docs/presentations/<topic>-outline.md
  -> data/processed/topic_data/<topic>.json
  -> data/processed/research_context/<topic>.md
  -> data/processed/research_plans/<topic>.json
  -> data/processed/research_runs/<topic>.json
  -> data/processed/research_index.json
  -> docs/presentations/<topic>-generated-deck.pptx
```

## Security And Maintenance

Dependabot is configured for:

- Python package updates from `pyproject.toml`
- GitHub Actions updates from `.github/workflows/`

Security posture:

- Keep dependencies minimal.
- Prefer optional dependency groups over a large default install.
- Keep API keys out of the repo. Use GitHub Actions secrets such as `OPENAI_API_KEY`.
- Generated research data should preserve source links and confidence levels.

