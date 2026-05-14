# Important Commands

Create topic files:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug --category sectors
```

Rebuild the research index:

```bash
python3 -m project_india.cli index-research
```

Plan research from existing repo memory:

```bash
python3 -m project_india.cli plan-research "Topic Name" --slug topic-slug --category sectors
```

Run deep research only when needed:

```bash
OPENAI_API_KEY=... python3 -m project_india.cli deep-research "Topic Name" --slug topic-slug --category sectors
```

Run incremental research:

```bash
OPENAI_API_KEY=... python3 -m project_india.cli research-increment "Topic Name" --slug topic-slug --category sectors --strategy rotate
```

Configure an existing topic for incremental scheduling:

```bash
python3 -m project_india.cli configure-schedule \
  --slug topic-slug \
  --frequency weekly \
  --enabled \
  --time-utc 06:00 \
  --day-of-week monday \
  --strategies developments,gaps,factcheck
```

Run the dashboard locally after installing Streamlit dependencies:

```bash
python3 -m pip install -r requirements.txt
streamlit run dashboard.py
```

Start local Postgres:

```bash
docker compose up -d postgres
```

Initialize and import repo research into Postgres:

```bash
python3 -m pip install -e ".[db]"
python3 -m project_india.cli db-init
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

Deploy on Streamlit Community Cloud with:

```text
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
```

Manually run the topic-intake workflow:

```bash
gh workflow run topic-intake-research.yml \
  -f title="Topic Name" \
  -f slug="topic-name" \
  -f category="sectors" \
  -f context="Starting context" \
  -f questions="Questions to answer" \
  -f sources="Source leads" \
  -f research_model="gpt-5" \
  -f depth="deep"
```

Manually run an incremental update workflow:

```bash
gh workflow run incremental-research.yml \
  -f topic_slug="topic-slug" \
  -f strategy="rotate" \
  -f model="gpt-5"
```
