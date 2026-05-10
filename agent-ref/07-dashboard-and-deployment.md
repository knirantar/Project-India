# Dashboard And Deployment

Project India now has a Streamlit dashboard in `dashboard.py`.

Production URL:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

The dashboard is meant to be the public presentation surface for the research system. Its first screen should prioritize insight, evidence, and topic interpretation, not API costs or workflow mechanics. Operational details belong under the Operations page.

The dashboard also has a **Start Research** intake page. The intake form collects a topic title, category, starting context, questions, and source leads. When Streamlit secrets are configured, it dispatches `.github/workflows/topic-intake-research.yml`.
The intake workflow should generate dashboard-ready research data, not a separate PPTX deck.

It shows:

- topic inventory and status
- public insight briefs
- structured evidence boards
- metrics, comparisons, timelines, tables, and research gaps
- category views for geopolitics, internal growth, and sectors
- structured topic data from `data/processed/topic_data/`
- incremental research history from `data/processed/research_runs/`
- operations/admin reference views for schedules, budget, and configuration

Required Streamlit secrets for app-triggered research:

```toml
GITHUB_OWNER = "knirantar"
GITHUB_REPO = "Project-India"
GITHUB_DISPATCH_TOKEN = "github_token_with_actions_write"
APP_ADMIN_PIN = "private-admin-pin"
```

Required GitHub Actions secret:

```text
OPENAI_API_KEY
```

Optional GitHub Actions secret for automatic PR merge:

```text
PROJECT_INDIA_ADMIN_TOKEN
```

Deployment target:

```text
Streamlit Community Cloud
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
Python: choose 3.11 or any supported 3.11+ version in Streamlit advanced settings
```

Streamlit Cloud expects the app entrypoint and dependencies to be committed to GitHub. This repo uses:

- `dashboard.py`
- `requirements.txt`
- `.streamlit/config.toml`
- committed local data under `data/processed/`

Actual Streamlit deployment requires the user to sign in to Streamlit with GitHub and authorize the app. Codex can prepare, test, commit, push, and guide deployment, but cannot complete the user's external OAuth/browser approval without the user's active login.

After deployment, GitHub Actions should update research data through pull requests because `main` is protected.

For normal repo changes, use a feature branch, open a PR, and merge it as one continuous delivery flow. Do not repeatedly stop to ask the user about each mechanical Git step when the requested outcome is clearly to ship the change.
