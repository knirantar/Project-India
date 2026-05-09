# Project India

Project India is a research and analysis repository for documenting, decoding, and contributing to India's geopolitical position and internal growth across sectors.

The aim is to build a living knowledge base that combines structured research, data analysis, policy understanding, sector-by-sector tracking, and AI-assisted workflows.

## Focus Areas

- Geopolitics and foreign policy
- Economy, trade, and industry
- Infrastructure and urban development
- Energy, climate, and natural resources
- Agriculture and food systems
- Defense, security, and strategic affairs
- Technology, AI, and digital public infrastructure
- Education, healthcare, and human development
- Governance, law, and institutions
- Culture, society, and demographic change

## Repository Structure

- `docs/geopolitics/` - geopolitical notes, country relationships, global strategy
- `docs/sectors/` - sector-wise documentation and analysis
- `docs/internal-growth/` - domestic development, governance, and social indicators
- `docs/research-notes/` - raw notes, reading summaries, open questions
- `docs/ai-workflows/` - prompts, research methods, automation workflows
- `docs/briefs/` - polished policy and strategy briefs
- `docs/presentations/` - presentation outlines and future deck material
- `data/` - datasets, cleaned data, and derived tables
- `sources/` - source lists, citations, and reference material
- `analyses/` - deeper essays, models, dashboards, and reports
- `project_india/` - Python helpers for repeatable research workflows
- `workflows/` - documented research and presentation processes

## Integrated Workflow

Project India uses three connected layers:

- Markdown is the knowledge base.
- Python is the workflow engine.
- Presentations, briefs, dashboards, and essays are the communication layer.

Create a new topic workflow with:

```bash
python3 -m project_india.cli new-topic "India's Semiconductor Mission" --slug india-semiconductor-mission
```

For topics outside sectors, pass a category:

```bash
python3 -m project_india.cli new-topic "West Bengal Assembly Election 2026" --slug west-bengal-assembly-election-2026 --category internal-growth
```

## Working Principles

- Use credible primary and secondary sources.
- Separate facts, interpretation, and opinion.
- Preserve citations and dates for time-sensitive claims.
- Track assumptions and uncertainty clearly.
- Use AI to accelerate research, analysis, synthesis, and publication, while keeping human judgment responsible for conclusions.

## Status

This project is just beginning.
