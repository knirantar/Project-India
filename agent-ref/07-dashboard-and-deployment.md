# Dashboard And Deployment

Project India has a Streamlit dashboard in `dashboard.py`.

Production URL:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

The dashboard is the public presentation surface for research. Its first screen should prioritize insight, evidence, and topic interpretation.

Current behavior:

- prefers Postgres data
- has temporary legacy archive-oriented fallback paths
- shows public insight briefs
- shows structured evidence boards
- shows metrics, comparisons, timelines, tables, and research gaps
- includes an Operations page with local Postgres setup guidance

Next behavior:

```text
dashboard reads Postgres -> clean empty state when no research exists
```

The old app-triggered GitHub Actions controls have been removed. Do not add Streamlit secrets for GitHub dispatch unless the project intentionally reintroduces a hosted worker.

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

No topic archive data is committed right now. The dashboard should render an empty state until Postgres-backed or exported research exists.

Actual Streamlit deployment requires the user to sign in to Streamlit with GitHub and authorize the app. Codex can prepare, test, commit, push, and guide deployment, but cannot complete the user's external OAuth/browser approval without the user's active login.

For normal repo changes, use a feature branch, open a PR, and merge it as one continuous delivery flow. Do not repeatedly stop to ask the user about each mechanical Git step when the requested outcome is clearly to ship the change.
