---
name: Research Run Status / Issue Report
about: Report problems with a scheduled research run or request manual research
title: "Research Issue: [Topic Name]"
labels: ["research-issue", "bug"]
---

## Issue Details

**Topic:**
<!-- Which topic? -->

**Issue Type:**
- [ ] Scheduled run failed
- [ ] API cost exceeded budget
- [ ] Research output is low quality
- [ ] Need manual research run now
- [ ] Found factual error in existing research
- [ ] Other (describe below)

**Description:**
<!-- What happened? What's the problem? -->

## For Failed Runs

**Error message:**
<!-- If available, paste the GitHub Actions error log -->

**Last successful run:**
<!-- When was this topic last researched successfully? -->

**Logs:**
<!-- Link to GitHub Actions run or attach logs -->

## For Budget Issues

**Monthly spend so far:**
<!-- Check research_config.json -->

**Monthly budget limit:**
<!-- Should be < $50 -->

**Recommendation:**
- [ ] Reduce frequency for this topic
- [ ] Change to cheaper strategy (e.g., "gaps" instead of "developments")
- [ ] Disable this topic temporarily
- [ ] Increase budget

## For Quality Issues

**What's wrong with the research?**
<!-- Be specific: missing facts, poor sourcing, outdated info, etc. -->

**Suggested fix:**
<!-- Should we re-run with a different strategy? Get manual research? -->

---

## For Maintainers

**Actions:**
- [ ] Investigate and report findings
- [ ] Retry failed run
- [ ] Adjust schedule or strategy
- [ ] Update budget tracking in research_config.json
