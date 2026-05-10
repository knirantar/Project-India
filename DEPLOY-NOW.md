# Deploy And Use Project India

Production dashboard:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

## Streamlit App Settings

```text
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
Python: 3.11 or 3.12
```

## Required Secrets

Streamlit secrets:

```toml
GITHUB_OWNER = "knirantar"
GITHUB_REPO = "Project-India"
GITHUB_DISPATCH_TOKEN = "github_token_with_actions_write"
APP_ADMIN_PIN = "private-admin-pin"
```

GitHub Actions secret:

```text
OPENAI_API_KEY
```

Optional GitHub Actions secret for one-step workflow PR auto-merge:

```text
PROJECT_INDIA_ADMIN_TOKEN
```

## First Research Run

1. Open the production dashboard.
2. Go to **Start Research**.
3. Enter the topic title, category, context, questions, and source leads.
4. Enter the admin PIN.
5. Click **Start GitHub research workflow**.
6. Watch the `Topic Intake Research` workflow in GitHub Actions.
7. After the workflow PR merges, refresh the app.

The app is the presentation surface. The intake workflow does not create PPTX decks.

## Incremental Research Cadence

Use this after the first deep research run:

1. Open **Operations**.
2. Go to **Schedules**.
3. Choose the topic.
4. Set `manual`, `daily`, `weekly`, or `monthly`.
5. Pick the UTC run time and strategy rotation.
6. Enter the admin PIN and save.

The app dispatches `Configure Topic Schedule`, which opens and auto-merges a PR when `PROJECT_INDIA_ADMIN_TOKEN` is configured.

The `Incremental Research` workflow checks every hour. It only researches topics that are due and uses focused strategies instead of full deep research.
