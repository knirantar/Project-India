# Contributing to Project India

Thank you for your interest in contributing to Project India! This is a collaborative research, analysis, and documentation project about India's geopolitical position and internal growth.

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
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

Run the dashboard locally:

```bash
python3 -m pip install -r requirements.txt
streamlit run dashboard.py
```

## How to Pick Issues

Start with issues labeled `good first issue`, `documentation`, or `help wanted`. If an issue affects research claims, data models, or architecture, read the relevant files in `agent-ref/` before proposing changes.

For new research topics, prefer the Postgres-first flow. The repo currently has no committed topic archive data; publish exports only when a topic is ready to become part of the curated archive.

## Contribution Types

- **Research & Analysis**: Contribute original research, data analysis, or policy insights
- **Documentation**: Improve existing docs or add new documentation
- **Data**: Provide verified datasets or sources for analysis
- **Code**: Enhance tools, dashboards, or data pipelines
- **Review**: Peer review research and analysis for accuracy

## Branch Naming

Use short, descriptive branch names:

- `docs/architecture-overview`
- `fix/ci-dev-dependencies`
- `feature/dashboard-filters`
- `research/india-energy-imports`

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

## Research Standards

- Use credible primary and secondary sources.
- Include source names, URLs, publication dates, and access dates when relevant.
- Distinguish facts, interpretation, assumptions, and opinion.
- Be explicit about uncertainty and data gaps.
- Do not overstate conclusions from thin evidence.
- Prefer current sources for time-sensitive claims.
- Preserve enough context for another contributor to audit the reasoning.

## Dashboard Work

The Streamlit dashboard is the public presentation surface. It currently reads committed archive files and should move toward reading Postgres first with archive files as fallback.

Run it with:

```bash
streamlit run dashboard.py
```

## Questions?

Open an issue for scoped work. Use GitHub Discussions for broader project direction, research framing, and early ideas.

Thank you for contributing to Project India!
