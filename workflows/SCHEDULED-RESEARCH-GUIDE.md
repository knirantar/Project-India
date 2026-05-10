# Scheduled Incremental Research System

Project India now supports **automated, budget-friendly incremental research** with GitHub Actions scheduling, strategy rotation, and cost tracking.

## Quick Start

### 1. View Current Schedules
```bash
cat research_config.json | jq '.topics[] | {title, slug, schedule, strategy}'
```

### 2. Run Incremental Research Manually
```bash
# Research developments since last run
python -m project_india.cli research-increment "US-Iran War 2026" \
  --slug us-iran-war-2026 \
  --category geopolitics \
  --strategy developments

# Research one unexplored gap
python -m project_india.cli research-increment "West Bengal Assembly Election 2026" \
  --slug west-bengal-assembly-election-2026 \
  --category internal-growth \
  --strategy gaps

# Rotate to next strategy in config (automatic for scheduled runs)
python -m project_india.cli research-increment "India's Semiconductor Mission" \
  --slug india-semiconductor-mission \
  --category sectors \
  --strategy rotate
```

### 3. Add a New Topic (via GitHub Issue)
1. Go to **Issues** tab
2. Click **New Issue**
3. Select template: **Add New Research Topic**
4. Fill in topic details, schedule, and strategies
5. GitHub Actions will automatically:
   - Create topic files
   - Add to `research_config.json`
   - Schedule first research run

### 4. Modify a Topic's Schedule (via GitHub Issue)
1. Create issue with template: **Modify Research Schedule**
2. Specify new frequency, time, and strategies
3. GitHub Actions updates config and reschedules

## How It Works

### Research Strategies

Each topic rotates through one or more strategies to minimize API costs:

#### **developments**
- **What:** Find NEW developments since last run
- **When:** Good for active topics (breaking news, elections, conflicts)
- **Cost:** ~$0.25 per run
- **Output:** New facts added to topic file with timestamps

#### **gaps**
- **What:** Explore ONE unexplored subtopic from the gaps list
- **When:** Good for expanding coverage
- **Cost:** ~$0.35 per run
- **Output:** New section in topic file with gap exploration

#### **factcheck**
- **What:** Verify existing facts, update confidence scores, check for contradictions
- **When:** Good for validating and strengthening existing content
- **Cost:** ~$0.30 per run
- **Output:** Updated existing sections with new confidence scores

#### **rotate**
- **What:** Automatically use next strategy in the topic's rotation
- **When:** Default for scheduled runs; ensures balanced coverage
- **Cost:** Depends on strategy (avg ~$0.30)
- **Output:** Varies per strategy

### File Structure

**research_config.json** tracks:
```json
{
  "budget": {
    "monthly_limit_usd": 50,
    "tracked_start_date": "2026-05-10",
    "current_month_spent_usd": 0.00
  },
  "topics": [
    {
      "title": "Topic Name",
      "slug": "topic-slug",
      "schedule": {
        "frequency": "daily" | "weekly" | "monthly",
        "time_utc": "09:00",
        "day_of_week": "monday" (if weekly),
        "last_run_date": "2026-05-10",
        "next_scheduled_run": "2026-05-11"
      },
      "strategy": {
        "rotation": ["developments", "gaps", "factcheck"],
        "current_index": 0
      },
      "metadata": {
        "api_calls_month": 1,
        "last_cost_usd": 0.25,
        "development_status": "active"
      }
    }
  ]
}
```

### Incremental Research Output

When you run `research-increment`, the system:

1. **Loads existing context** from topic files
2. **Determines gaps** using research_plan.py
3. **Builds a lightweight prompt** focused on the strategy
4. **Calls OpenAI** (only if gaps exist)
5. **Updates files incrementally** (APPENDS to topics, overwrites brief)
6. **Logs the run** in `data/processed/research_runs/<slug>-increment-*.json`

Files updated:
- ✅ `docs/<category>/<slug>.md` — appends new findings with timestamp
- ✅ `sources/<slug>-sources.md` — appends new sources
- ✅ `analyses/reports/<slug>-brief.md` — replaces with latest version
- ✅ `data/processed/research_runs/<slug>-*.json` — run record

### GitHub Actions Scheduling

**File:** `.github/workflows/scheduled-research.yml`

**Automatic Triggers:**
- **West Bengal Elections:** Weekly Monday 9 AM UTC
- **US-Iran War:** Daily 6 AM UTC
- **Other topics:** As configured in `research_config.json`

**Manual Trigger:**
```bash
# Go to Actions tab → Scheduled Incremental Research → Run workflow
# Or use GitHub CLI:
gh workflow run scheduled-research.yml \
  -f topic_slug=west-bengal-assembly-election-2026 \
  -f strategy=developments
```

### Cost Tracking

Every run updates `research_config.json`:
```json
"metadata": {
  "api_calls_month": 5,           // Total calls this month
  "last_cost_usd": 0.25,          // Cost of last run
  "total_cost_month": 1.25        // Total cost this month
}
```

**Budget Alert:** If monthly spend approaches $50 limit, GitHub Actions will:
1. Log a warning
2. Create an issue: "Research Run Status / Issue Report"
3. Skip lower-priority topics
4. Suggest strategy changes

## Examples

### Example 1: Track Active Geopolitical Event

Topic: US-Iran War 2026
```json
{
  "frequency": "daily",
  "time_utc": "06:00",
  "strategy": {
    "rotation": ["developments"],
    "current_index": 0
  }
}
```
**Effect:** Every day at 6 AM UTC, research looks for NEW developments (what changed since yesterday?). Cost: ~$0.25/day × 30 = $7.50/month.

### Example 2: Balanced Research with Strategy Rotation

Topic: West Bengal Elections
```json
{
  "frequency": "weekly",
  "day_of_week": "monday",
  "time_utc": "09:00",
  "strategy": {
    "rotation": ["developments", "gaps", "factcheck"],
    "current_index": 0
  }
}
```
**Effect:** Every Monday at 9 AM UTC, research rotates strategies:
- Week 1: Find developments
- Week 2: Explore one gap
- Week 3: Fact-check existing claims
- Week 4: Developments again...

Cost: ~$0.30/week × 4 = $1.20/month.

### Example 3: Low-Cost Quarterly Deep Dive

Topic: India Semiconductor Mission
```json
{
  "frequency": "monthly",
  "day_of_week": "15",
  "time_utc": "12:00",
  "strategy": {
    "rotation": ["gaps"],
    "current_index": 0
  }
}
```
**Effect:** Once a month, explore one gap in depth. Cost: ~$0.35/month.

## API Budget Strategy

**With $20-50/month budget:**
- ✅ 1-2 topics with daily updates (developments only)
- ✅ 3-4 topics with weekly rotating strategies
- ✅ 1-2 pilot topics with monthly updates

**NOT recommended:**
- ❌ More than 5 topics running daily
- ❌ Multiple topics using "gaps" strategy on same day
- ❌ Using deep research + incremental research on same topic same week

## Troubleshooting

### Research runs failing?
1. Check GitHub Actions logs: `.github/workflows/scheduled-research.yml`
2. Verify `OPENAI_API_KEY` secret is set in repo settings
3. Create issue: "Research Run Status / Issue Report"

### Budget exceeded?
1. Check `research_config.json` → budget.current_month_spent_usd
2. Options:
   - Switch high-frequency topics to "developments" strategy (cheaper)
   - Disable lower-priority topics temporarily
   - Increase budget
3. Create issue: "Modify Research Schedule"

### Topic not running on schedule?
1. Verify `enabled: true` in `research_config.json`
2. Check time/frequency settings match your timezone (note: times are UTC)
3. Run manual test via GitHub Actions UI

### OpenAI API key issues?
1. Verify secret is set: Repo Settings → Secrets and variables → Actions
2. Test locally: `OPENAI_API_KEY=your_key python -m project_india.cli research-increment ...`
3. Check API key hasn't expired or hit usage limits

## Next Steps

- Phase 2: Build Streamlit dashboard to visualize incremental research runs
- Phase 3: Add GitHub Pages integration for public research portal
- Phase 4: Instagram carousel generation from research outputs
