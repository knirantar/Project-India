# Current Topics

The repository topic corpus was reset after the Streamlit production dashboard went live.

Current active topic:

- `us-iran-war` (`geopolitics`) - created through Streamlit topic intake and available in the public dashboard.

New topics should enter through the Streamlit **Start Research** intake flow, which dispatches `.github/workflows/topic-intake-research.yml`.
That workflow creates the topic note, source log, brief, structured topic data, run record, and research index update for the dashboard.

After a topic exists, configure its ongoing cadence from **Operations -> Schedules**. Do not run deep research every time; use incremental strategies unless the topic needs a fresh full rebuild.

Relevant reference docs:

- `docs/research-notes/project-roadmap.md`
- `docs/research-notes/data-and-indexing.md`
- `docs/research-notes/dependency-graph.md`
