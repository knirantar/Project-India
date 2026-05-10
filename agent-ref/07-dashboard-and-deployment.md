# Dashboard And Deployment

Project India now has a Streamlit dashboard in `dashboard.py`.

The dashboard is meant to be the public presentation surface for the research system. It shows:

- topic inventory and status
- budget and estimated API spend
- category views for geopolitics, internal growth, and sectors
- structured topic data from `data/processed/topic_data/`
- incremental research history from `data/processed/research_runs/`
- admin/reference views for schedules and configuration

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
