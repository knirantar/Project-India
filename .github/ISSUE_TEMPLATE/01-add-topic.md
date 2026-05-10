---
name: Add New Research Topic
about: Create a new topic for Project India research system
title: "Topic: [Topic Name]"
labels: ["topic:new", "research"]
---

## Topic Details

**Topic Title:** 
<!-- Example: "India's Semiconductor Mission" -->

**Slug (URL-safe):**
<!-- Example: india-semiconductor-mission -->

**Category:** 
<!-- Choose one: geopolitics, internal-growth, sectors, research-notes -->

**Description:**
<!-- What is this topic about? Why is it important? 1-2 sentences. -->

## Research Configuration

**Research Schedule:**
- **Frequency:** <!-- daily, weekly, monthly, or custom cron -->
- **Time (UTC):** <!-- e.g., 09:00 -->
- **Day (if weekly/monthly):** <!-- e.g., monday, 15th -->

**Research Strategies:**
- [ ] developments (track new events and changes)
- [ ] gaps (explore unexplored subtopics)
- [ ] factcheck (verify existing facts)
- [ ] rotate (cycle through all strategies)

**Priority:**
<!-- low, medium, high, critical -->

## Initial Research Context

**Known facts/sources:**
<!-- What do we already know about this topic? Any URLs or references? -->

**Expected data points:**
<!-- What metrics, timelines, or comparisons should we track? -->

**Related topics:**
<!-- Link to other Project India topics this connects with -->

---

## For Maintainers

Once created, this topic will:
1. Be added to `research_config.json` with the above schedule
2. Create initial topic files (topic note, sources, brief outline)
3. Be scheduled in GitHub Actions for automatic research runs
4. Appear in the Streamlit dashboard

**GitHub Action will auto-populate these fields:**
- [ ] Topic files created
- [ ] research_config.json updated
- [ ] GitHub Actions workflow triggered
- [ ] Initial research run scheduled
