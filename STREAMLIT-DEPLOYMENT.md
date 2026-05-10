# Streamlit Cloud Deployment Configuration

This dashboard is configured for deployment on Streamlit Cloud.

## Local Testing

```bash
streamlit run dashboard.py
```

Then open http://localhost:8501

## Deploy to Streamlit Cloud

1. **Push to GitHub** (this repo)
2. **Go to** https://share.streamlit.io
3. **Sign in** with GitHub
4. **Click** "Create app"
5. **Select:**
   - Repository: `knirantar/Project-India`
   - Branch: `main`
   - Main file path: `dashboard.py`
6. **Click "Deploy"**

Production URL:

```text
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

If the app is redeployed later, keep this URL as the canonical production URL unless Streamlit assigns a replacement.

## Features

- **📊 Overview**: Key metrics, budget tracking, cost breakdown
- **🌍 Geopolitics**: International relations and strategic analysis
- **🏛️ Internal Growth**: Domestic politics and governance
- **⚙️ Sectors**: Industry and economic analysis
- **📈 Research History**: All runs, costs, trends
- **⚙️ Admin**: Topic management and configuration

## Data Refresh

- Dashboard caches data for 5 minutes
- GitHub Actions updates research automatically on schedule
- Real-time sync on page reload

## Troubleshooting

If data isn't showing:
1. Ensure `research_config.json` is in the repo root
2. Check that `data/processed/` folder exists
3. Wait 5 minutes for Streamlit Cloud to sync latest code

For more info, see `workflows/SCHEDULED-RESEARCH-GUIDE.md`
