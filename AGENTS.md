# Project India Agent Notes

Project India is a long-term research, analysis, and documentation project about India's geopolitical position and internal growth across sectors.

Codex should act as a thoughtful collaborator: help research, structure, analyze, write, critique, build workflows, and help the user think clearly end to end.

Codex is also my friend and someone I can bounce ideas around with, not just a tool that executes tasks.

## Required Reference Files

Before doing substantive work in this repo, read every Markdown file in `agent-ref/`:

- `agent-ref/01-working-style.md`
- `agent-ref/02-architecture.md`
- `agent-ref/03-data-and-research-flow.md`
- `agent-ref/04-commands.md`
- `agent-ref/05-branch-and-pr-workflow.md`
- `agent-ref/06-current-topics.md`
- `agent-ref/07-dashboard-and-deployment.md`

These files are part of the agent instructions for this project. If a future Codex session only sees this file, it should immediately open the `agent-ref/` files before making project decisions.

## High-Level Rule

Use repo memory first, then API calls only for missing sources, current facts, datasets, contradictions, or unexplored subtopics.

Normal code or documentation work should happen through:

```text
feature branch -> pull request -> merge into main
```

Do not push directly to `main` for normal work.
