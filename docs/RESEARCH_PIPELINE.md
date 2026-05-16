# Research Pipeline

Project India uses a file-first research intelligence workflow.

```text
topic
  -> discover sources
  -> collect heterogeneous data
  -> extract clean text
  -> extract structured intelligence
  -> store normalized evidence
  -> generate dashboards / timelines / insights
```

## Data Types

The workflow is designed to collect and classify:

- News articles
- Government documents
- Research papers
- Books
- PDFs
- RSS feed content
- Structured datasets
- Websites / HTML pages
- Blogs
- Social media content
- Video content
- Video transcripts
- Audio content
- Images
- OCR text
- Legal / judicial records
- Financial data
- Scientific / technical data
- Geospatial / mapping data
- Event data
- Timeline data
- Entity data
- Relationship data
- Metrics / numerical data
- Metadata
- Community discussions
- Archived / historical content
- Open source intelligence
- Web archives / cached content
- AI-generated summaries / derived intelligence

## Normalized Objects

Regardless of source type, OpenAI normalization should extract:

- Documents
- Claims
- Entities
- Events
- Metrics
- Relationships
- Timelines
- Citations
- Evidence snippets
- Source credibility
- Tags / topics
- Geolocation
- Timestamps

## Current Storage

No database is required for the current milestone.

```text
project_india/topics/<topic-slug>/config.yaml
data/<topic-slug>/raw/<sha>.<raw-extension>
data/<topic-slug>/raw/<sha>.txt
data/<topic-slug>/raw/<sha>.json
data/<topic-slug>/raw/<sha>.analysis.json
```

The `.json` file stores collection metadata. The `.analysis.json` file stores normalized intelligence.
