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
