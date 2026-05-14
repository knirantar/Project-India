# Important Commands

Start local Postgres:

```bash
docker compose up -d postgres
```

Initialize and import repo archive data into Postgres:

```bash
python3 -m pip install -e ".[db]"
python3 -m project_india.cli db-init
python3 -m project_india.cli db-import-repo
python3 -m project_india.cli db-status
```

Create curated archive files for a topic:

```bash
python3 -m project_india.cli new-topic "Topic Name" --slug topic-slug --category sectors
```

Rebuild the committed research index:

```bash
python3 -m project_india.cli index-research
```

Plan research from existing repo memory:

```bash
python3 -m project_india.cli plan-research "Topic Name" --slug topic-slug --category sectors
```

Run source-backed repo-archive research only when needed:

```bash
OPENAI_API_KEY=... python3 -m project_india.cli deep-research "Topic Name" --slug topic-slug --category sectors
```

Run the dashboard locally:

```bash
python3 -m pip install -r requirements.txt
streamlit run dashboard.py
```

Deploy on Streamlit Community Cloud with:

```text
Repository: knirantar/Project-India
Branch: main
Main file path: dashboard.py
```
