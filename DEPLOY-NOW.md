# 🚀 STREAMLIT CLOUD DEPLOYMENT — STEP-BY-STEP

## Your 5-Minute Deployment Checklist

Everything is ready. Follow these exact steps to deploy:

---

## STEP 1: Go to Streamlit Cloud (30 seconds)
```
https://share.streamlit.io
```

## STEP 2: Sign In With GitHub (30 seconds)
- Click "Sign in with GitHub"
- Authorize Streamlit
- Accept terms

## STEP 3: Click "Create app" (30 seconds)

## STEP 4: Configure Your App (1 minute)

Fill in these exact values:

**Repository:** `knirantar/Project-India`
**Branch:** `main`
**Main file path:** `dashboard.py`

Optional but recommended: set **App URL / Custom subdomain** to `project-india-research` if Streamlit shows it as available.

Then click **"Deploy"**

## STEP 5: Wait for Deployment (2-3 minutes)

Watch the logs in Streamlit Cloud:
```
✓ Cloning repository
✓ Installing dependencies from requirements.txt
✓ Caching dependencies
✓ Building environment
✓ App is ready!
```

## STEP 6: Your Dashboard is LIVE! 🎉

Streamlit will give you a public `*.streamlit.app` URL. If the custom subdomain is available, use:

```
https://project-india-research.streamlit.app
```

---

## What You'll See After Deployment

When the app loads, you should see:

**Left Sidebar:**
- 🇮🇳 Project India logo
- Navigation menu (Overview, Geopolitics, Internal Growth, etc.)
- Budget Status card (showing $0 spent so far)

**Main Area:**
- 📊 Overview tab with metrics
- Topic cards with status
- Cost breakdown charts

---

## THEN: Set Up GitHub Secrets (1 minute)

For scheduled research to run, add your OpenAI API key:

1. Go to your GitHub repo: https://github.com/knirantar/Project-India
2. Click **Settings** (top right)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

**Name:** `OPENAI_API_KEY`
**Value:** `sk-...` (your OpenAI API key)

5. Click **Add secret**

After this, scheduled research will trigger automatically!

---

## VERIFY: Dashboard is Working

Check these tabs load without errors:

- [✓] **📊 Overview** — Shows 3 topics, budget, costs
- [✓] **🌍 Geopolitics** — Shows US-Iran War 2026
- [✓] **🏛️ Internal Growth** — Shows West Bengal Election 2026
- [✓] **⚙️ Sectors** — Shows India Semiconductor Mission
- [✓] **📈 Research History** — Empty for now (populates after first run)
- [✓] **⚙️ Admin** — Shows configuration

---

## After Deployment: First Research Run

To see the dashboard with data:

1. Go to https://github.com/knirantar/Project-India
2. Click **Actions** tab
3. Click **"Scheduled Incremental Research"**
4. Click **"Run workflow"** button
5. Click **"Run workflow"** again to confirm
6. Wait 2-5 minutes for completion

Then go back to your dashboard and refresh. You should see:
- Research history populated
- Cost updated
- Metrics displayed

---

## Your Dashboard URL (After Deployment)

```
https://project-india-research.streamlit.app
```

If Streamlit assigns a generated URL instead, use the URL shown on the app page.

Share this link with anyone!

---

## Troubleshooting

**"Build failed"?**
→ Check logs in Streamlit Cloud
→ Verify requirements.txt has all dependencies
→ Ensure dashboard.py is in repo root

**"No data showing"?**
→ Normal — wait for first research run
→ Go to GitHub Actions and manually trigger
→ Refresh dashboard after run completes

**"Configuration error"?**
→ Verify research_config.json is in repo root
→ Check JSON syntax: `jq . research_config.json`
→ Ensure data/processed/ folder exists

---

## Questions?

See these docs in your repo:
- `README-DEPLOYMENT.md` — Complete overview
- `DEPLOYMENT-GUIDE.md` — Detailed troubleshooting
- `SCHEDULED-RESEARCH-GUIDE.md` — Research commands

---

## Ready? Start Here:

1. Visit: https://share.streamlit.io
2. Sign in with GitHub
3. Click "Create app"
4. Repository: `knirantar/Project-India`
5. Branch: `main`
6. Main file: `dashboard.py`
7. Click "Deploy"
8. Wait 2-3 minutes
9. Your dashboard is live! 🎉

---

**Let me know when you've deployed and I can help verify it's working!**
