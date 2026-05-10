# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment (5 minutes)

### Step 1: Go to Streamlit Cloud
1. Visit https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"Create app"** button

### Step 2: Configure the App
1. **Repository:** Select `knirantar/Project-India`
2. **Branch:** Select `main`
3. **Main file path:** Enter `dashboard.py`
4. Click **"Deploy"**

### Step 3: Wait for Deployment
- First deployment takes ~2-3 minutes
- Streamlit will install dependencies from `requirements.txt`
- You'll see logs in the terminal on the Streamlit Cloud interface

### Step 4: Access Your Dashboard
Once deployed, Streamlit will give you a public `*.streamlit.app` URL. If the custom subdomain is available, use:
```
https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/
```

This generated URL is the current production URL.

---

## What the Dashboard Shows

### 📊 Overview Tab
- Key metrics: Total topics, active research, monthly budget
- Topic cards with status, schedule, and cost
- Cost breakdown and pie charts
- API call distribution

### 🌍 Geopolitics Tab
- US-Iran War 2026 with detailed metrics and timeline
- Real-time conflict status
- Impact on India analysis
- Strategic implications

### 🏛️ Internal Growth Tab
- West Bengal Assembly Election 2026 results
- Electoral metrics and comparisons
- Political implications
- Governance analysis

### ⚙️ Sectors Tab
- India Semiconductor Mission analysis
- Industry metrics and benchmarks
- Strategic importance
- Implementation roadmap

### 📈 Research History Tab
- All incremental research runs logged
- Cost trends over time
- Strategy distribution
- Run details and summaries

### ⚙️ Admin Tab
- **Topics**: View and manage all topics
- **Schedules**: View all scheduled runs
- **Configuration**: Raw JSON config viewer
- Links to GitHub Issues for modifications

---

## Features & Capabilities

### Real-Time Data Sync
- Dashboard pulls latest data from GitHub repo
- Caches for 5 minutes (refresh button forces new load)
- Updates automatically when GitHub Actions runs research

### Cost Visualization
- Total budget tracking
- Cost breakdown by topic
- Monthly spend trends
- API call distribution

### Research Status
- Live schedule view
- Last run timestamp
- Next scheduled run
- Topic development status (mature, active, stub, disabled)

### Mobile Responsive
- Works on desktop, tablet, and mobile
- Sidebar collapses on small screens
- Touch-friendly buttons

---

## Advanced Configuration

### Custom Domain (Optional)
1. Go to your Streamlit Cloud app settings
2. Under "Custom domain", enter your domain
3. Follow DNS configuration steps

### Environment Variables (If Needed)
1. Go to app settings
2. Click "Secrets"
3. Add any environment variables (e.g., API keys)
4. These are available to your dashboard via `st.secrets`

### Auto-Rerun on GitHub Push
- Streamlit automatically redeploys on every GitHub push
- Check "Deploy on every push to main" in app settings

---

## Monitoring & Troubleshooting

### Check Deployment Status
- Go to app menu (top right) → Settings
- View deployment logs
- Check "Recent deployments" tab

### Common Issues

#### Dashboard shows "No configuration found"
**Cause:** `research_config.json` not found
**Fix:** 
```bash
git add research_config.json
git commit -m "add: research configuration"
git push
```

#### Data not updating
**Cause:** Cache not refreshed
**Fix:** 
- Click refresh button in browser
- Or check "Clear cache" in Streamlit app menu

#### App crashes on load
**Cause:** Missing dependencies
**Fix:**
1. Check that `requirements.txt` is in repo root
2. Verify all imports are listed:
   ```
   streamlit
   pandas
   plotly
   python-pptx
   openai
   ```
3. Trigger redeployment by pushing a small change to main

#### No research runs showing
**Cause:** GitHub Actions hasn't run yet
**Fix:**
1. Go to Actions tab in GitHub repo
2. Click "Scheduled Incremental Research"
3. Click "Run workflow"
4. Wait for completion (~5 minutes)
5. Refresh dashboard

---

## Performance Tips

### Optimize Load Time
1. Streamlit caches data for 5 minutes
2. First load may take 10-15 seconds (normal for free tier)
3. Subsequent loads are instant from cache

### Reduce Dashboard Size
- Archive old research runs: Keep only last 100
- Remove unused topics from research_config.json
- Delete old run files from `data/processed/research_runs/`

---

## Sharing Your Dashboard

### Share Public Link
```
https://project-india-research.streamlit.app
```

### Embed in Website
```html
<iframe 
  src="https://project-india-research.streamlit.app" 
  style="width:100%;height:800px;border:none;">
</iframe>
```

### Social Media
Share the link on:
- Twitter/X: "Automated research on India's geopolitics via @streamlit"
- LinkedIn: "Project India Research Dashboard - Live Analysis"
- GitHub: Add link to README.md

---

## Next Steps

### After Deployment

1. **Test the dashboard:**
   - Navigate all tabs
   - Check that data loads
   - Verify costs are tracked

2. **Set up GitHub Actions:**
   - Add `OPENAI_API_KEY` secret to repo
   - Verify scheduled runs trigger correctly
   - Monitor first automated research run

3. **Monitor costs:**
   - Check budget usage in Admin tab
   - Adjust schedules if needed
   - Monitor API spend

4. **Phase 3 Preparation:**
   - Instagram carousel automation
   - Social media integration
   - Automated posting

---

## Support & Help

### Dashboard Issues
- See `STREAMLIT-DEPLOYMENT.md` in repo
- Check Streamlit Cloud logs
- Review `dashboard.py` source code

### Scheduled Research Issues
- See `workflows/SCHEDULED-RESEARCH-GUIDE.md`
- Check GitHub Actions logs
- Verify `research_config.json` is valid

### General Questions
- Streamlit docs: https://docs.streamlit.io
- GitHub docs: https://docs.github.com
- Project India repo: https://github.com/knirantar/Project-India

---

## Deployment Checklist

- [ ] GitHub repo is public
- [ ] `research_config.json` is in repo root
- [ ] `dashboard.py` is in repo root
- [ ] `requirements.txt` lists all dependencies
- [ ] `.streamlit/config.toml` exists
- [ ] All files are committed and pushed to main
- [ ] Created Streamlit Cloud account
- [ ] Deployed app successfully
- [ ] Dashboard loads without errors
- [ ] Data displays correctly
- [ ] Admin panel is accessible

---

## Live Dashboard URL

Once deployed, your dashboard will be available at:

🌐 **https://project-india-nflujcnhq3f7xfj2d6q6sh.streamlit.app/**

(Or your custom domain if configured)

---

## Commands Reference

### Local Testing (Optional)
```bash
pip install streamlit pandas plotly python-pptx openai
streamlit run dashboard.py
```

Then open http://localhost:8501

### Force Redeployment
```bash
git commit --allow-empty -m "trigger: redeployment"
git push
```

---

Created: May 10, 2026 | Phase 2 Complete ✅
