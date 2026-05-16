# Project India

Project India is building a file-first research collection workflow before adding any database layer.

The current milestone is simple:

```text
topic config
  -> trusted RSS/source discovery
  -> configured historical URLs
  -> keyword/entity filtering
  -> raw local evidence files
  -> optional OpenAI evidence extraction
```

No Postgres is required for this step.

## Topic Folders

Each topic lives under:

```text
project_india/topics/<topic-slug>/config.yaml
```

The config defines the topic title, keywords, entities, source priorities, RSS seeds, and optional search queries.

The workflow is designed around heterogeneous research data:

```text
news, government documents, research papers, books, PDFs, RSS, datasets,
HTML pages, blogs, legal records, financial data, technical data, maps,
events, timelines, entities, relationships, metrics, archives, OSINT,
community discussions, media transcripts, and AI-derived intelligence
```

Each collected source is normalized into:

```text
documents, claims, entities, events, metrics, relationships, timelines,
citations, evidence snippets, source credibility, tags/topics,
geolocation, and timestamps
```

## Collect A Topic

Use the full workflow for any topic:

```bash
.venv/bin/python project_india/workflows/research_topic.py \
  --topic "India semiconductors"
```

That command:

```text
creates project_india/topics/<topic-slug>/config.yaml
collects RSS + historical discovery URLs
saves raw files under data/<topic-slug>/raw/
normalizes text into .analysis.json with OpenAI
```

You can also use the lower-level collector directly:

```bash
.venv/bin/python project_india/collectors/topic_collector.py \
  --topic-dir project_india/topics/india-semiconductors \
  --limit 20
```

Collected data is saved locally under:

```text
data/<topic-slug>/raw/
```

Runtime data is ignored by Git so the repository stays clean.

## Normalize Evidence

After collection, OpenAI can turn each text file into structured evidence JSON:

```bash
set -a
source .env
set +a
.venv/bin/python project_india/collectors/normalize_topic.py \
  --topic-dir project_india/topics/india-semiconductors
```

This writes one `.analysis.json` file beside each collected `.txt` file.
