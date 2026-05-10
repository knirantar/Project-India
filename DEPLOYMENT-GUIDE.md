# Streamlit Deployment Guide

Production dashboard:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

## What The Dashboard Does

- Starts from an empty topic library.
- Lets the admin submit a topic through **Start Research**.
- Dispatches `.github/workflows/topic-intake-research.yml`.
- Shows researched topics as insight briefs, evidence boards, metrics, comparisons, timelines, tables, and open questions.
- Keeps API spend, schedules, workflow history, and raw config under **Operations**.

## Deployment

Use Streamlit Community Cloud:

```text
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
Python: 3.11 or 3.12
```

## Dependencies

The app installs from `requirements.txt`:

```text
streamlit
pandas
plotly
requests
```

OpenAI is installed only inside GitHub Actions for source-backed research.

## Required Secrets

Streamlit secrets:

```toml
GITHUB_OWNER = "knirantar"
GITHUB_REPO = "Project-India"
GITHUB_DISPATCH_TOKEN = "github_token_with_actions_write"
APP_ADMIN_PIN = "private-admin-pin"
```

GitHub Actions secrets:

```text
OPENAI_API_KEY
PROJECT_INDIA_ADMIN_TOKEN  # optional for automatic PR merge
```

## Troubleshooting

If the app has no insights yet, that is expected after the reset. Submit the first topic from **Start Research**.

If the workflow does not start, verify Streamlit secrets and that the GitHub token can dispatch workflows.

If the workflow finishes but the app does not update, merge the generated PR or configure `PROJECT_INDIA_ADMIN_TOKEN` for auto-merge, then refresh the app.
