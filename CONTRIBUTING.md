# Contributing to Project India

Thank you for your interest in contributing to Project India! This repository contains the app, database schema, tests, workflow, and project documentation for a Postgres-first research system.

## Local Setup

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev,db]"
```

Start local Postgres when working on database-backed features:

```bash
docker compose up -d postgres
python3 -m project_india.cli db-init
python3 -m project_india.cli db-status
```

Run the dashboard locally:

```bash
python3 -m pip install -r requirements.txt
streamlit run dashboard.py
```

## How to Pick Issues

Start with issues labeled `good first issue`, `documentation`, or `help wanted`. If an issue affects data models, dashboard behavior, deployment, or architecture, read the relevant files in `agent-ref/` before proposing changes.

Research topics, source logs, evidence, notes, briefs, metrics, and research runs belong in Postgres, not GitHub issues or committed files.

## Contribution Types

- **Documentation**: Improve existing docs or add new documentation
- **Schema & Data Tools**: Improve the Postgres schema, import/export tooling, or database helpers
- **Code**: Enhance tools, dashboards, or data pipelines
- **Review**: Review code, documentation, workflows, and deployment changes

## Branch Naming

Use short, descriptive branch names:

- `docs/architecture-overview`
- `fix/ci-dev-dependencies`
- `feature/dashboard-filters`
- `infra/streamlit-postgres`

Do not push normal work directly to `main`.

## PR Process

1. Create a feature branch from the latest `main`
2. Make your changes following the repository structure
3. Run the relevant checks locally
4. Open a pull request with a clear summary and testing notes
5. Link related issues
6. Address review feedback
7. Merge through the PR after approval and passing CI

See [branch and PR workflow](agent-ref/05-branch-and-pr-workflow.md) for detailed guidelines.

## Code Style

- Write clear, maintainable Python code.
- Keep functions small enough to review.
- Prefer existing project patterns over new abstractions.
- Follow PEP 8 conventions.
- Add or update tests for behavior changes.
- Avoid committing secrets, generated local files, or one-off research scratchpads.

Run style checks:

```bash
flake8 project_india
```

## How to Run Tests

```bash
python3 -m pip install -e ".[dev]"
pytest tests/
```

Use coverage when changing shared code:

```bash
pytest tests/ --cov=project_india
```

## Research Data Boundary

- Do not commit research data, source logs, notes, briefs, metrics, or AI-generated analysis to GitHub.
- Keep living research records in Postgres.
- Keep only code, schema, tests, CI, app configuration, and project documentation in the repo.
- Use sample or synthetic data only when it is clearly marked as development data.

## Dashboard Work

The Streamlit dashboard is the public presentation surface. It should read from Postgres and handle empty tables cleanly.

Run it with:

```bash
streamlit run dashboard.py
```

## Questions?

Open an issue for scoped code, docs, schema, dashboard, CI, or deployment work. Keep research tasks and research records in Postgres.

Thank you for contributing to Project India!
