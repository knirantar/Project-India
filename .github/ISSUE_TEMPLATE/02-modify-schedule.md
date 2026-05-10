---
name: Modify Research Schedule
about: Change schedule, frequency, or strategy for an existing topic
title: "Schedule: [Topic Name]"
labels: ["schedule", "research"]
---

## Topic to Modify

**Topic Slug:**
<!-- Example: west-bengal-assembly-election-2026 -->

**Current Schedule:**
<!-- Example: daily at 06:00 UTC -->

## Schedule Changes

**New Frequency:**
- [ ] daily
- [ ] weekly
- [ ] monthly
- [ ] custom (specify cron below)
- [ ] disable (pause research on this topic)

**New Time (UTC):**
<!-- e.g., 09:00 -->

**New Day (if weekly/monthly):**
<!-- e.g., monday, 15th -->

## Strategy Changes

**Current Strategy Rotation:**
<!-- List current strategies, e.g., ["developments", "gaps", "factcheck"] -->

**New Strategy Rotation:**
- [ ] developments (track new events and changes)
- [ ] gaps (explore unexplored subtopics)
- [ ] factcheck (verify existing facts)
- [ ] rotate (cycle through all strategies)

**Reason for change:**
<!-- Why are we modifying this schedule? E.g., "US-Iran conflict is active, increase tracking frequency" -->

## Budget Considerations

**Current monthly cost for this topic:** 
<!-- Check research_config.json -->

**Expected new monthly cost:**
<!-- Estimate based on frequency change -->

---

## For Maintainers

This will:
1. Update `research_config.json` with new schedule
2. Re-trigger GitHub Actions cron schedule
3. Log the change in research history
