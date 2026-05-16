# Roadmap

Project India is moving toward a Postgres-first research system with a public dashboard. GitHub holds the app and workflow; Postgres holds the research.

## Phase 1: Contributor Setup

- Stabilize GitHub issue templates, pull request templates, labels, and CI.
- Document local setup, contribution workflow, architecture, and good first issues.
- Keep `main` mergeable through a simple CI workflow.

## Phase 2: Postgres-First Dashboard

- Make the Streamlit dashboard read from Postgres.
- Handle empty database tables with a clear first-run state.
- Add dashboard filters, evidence views, and clearer empty states.

## Phase 3: Postgres Research Ingestion

- Build repeatable ingestion flows for sources, briefs, metrics, timelines, and data gaps.
- Add sample seed data for local development.
- Document source logging and evidence standards inside the database workflow.

## Phase 4: AI Insights

- Add AI-assisted synthesis for topic briefs, source comparison, and gap detection.
- Keep human review responsible for conclusions and publication.
- Preserve citations, dates, uncertainty, and reasoning trails.

## Phase 5: Cloud Deployment

- Add deployment only after CI and the dashboard data path are stable.
- Prepare hosted Postgres or another managed data backend.
- Deploy the dashboard through Streamlit Community Cloud or a future app/API stack.
- Keep production secrets and research data out of GitHub.
