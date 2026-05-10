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

Build a presentation:

```bash
python3 -m project_india.cli build-presentation "Topic Name" --slug topic-slug --category sectors
```

Run incremental research:

```bash
OPENAI_API_KEY=... python3 -m project_india.cli research-increment "Topic Name" --slug topic-slug --category sectors --strategy rotate
```

Run the dashboard locally after installing Streamlit dependencies:

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
