# Automated Journalism Pipeline - Executive Summary

**Date:** 2025-12-31
**Project:** The Daily Worker (DWnews)
**Status:** Designed and planned, awaiting user approval

---

## What Was Delivered

1. **Comprehensive Analysis Document** (`automated-journalism-analysis.md` - 12 sections, 400+ lines)
   - Gap analysis (current infrastructure vs. 10-step Agentic Journalist Process)
   - System architecture design (agents, data flow, scheduling)
   - Database schema additions (4 new tables, column additions)
   - Cost breakdown ($44/month estimated)
   - Risk mitigation strategies
   - Implementation phases

2. **Updated Roadmap** (`roadmap.md` - Batch 6 added)
   - 8 new phases with detailed tasks
   - Dependency mapping
   - Complexity ratings (2 Small, 6 Medium)
   - Clear success criteria

3. **6 New Agent Definitions Specified** (to be created in `.claude/agents/`)
   - Signal Intake Agent (event discovery)
   - Evaluation Agent (newsworthiness scoring)
   - Verification Agent (source verification)
   - Enhanced Journalist Agent (article drafting + self-audit)
   - Editorial Coordinator Agent (workflow orchestration)
   - Monitoring Agent (post-publication tracking)

---

## How It Works (Daily Cadence)

```
06:00 AM → Signal Intake Agent discovers 20-50 events (RSS, Twitter, Reddit, govt feeds)
06:30 AM → Evaluation Agent scores events, approves 10-20% (≥60/100 score)
07:00 AM → Verification Agent verifies ≥3 sources per approved event
08:00 AM → Journalist Agent drafts articles with self-audit + bias scan
09:00 AM → Editorial Coordinator assigns drafts to human editors
09:00 AM - 5:00 PM → Human editors review, approve, or request revisions
05:00 PM → Auto-publish approved articles
Every 6 Hours → Monitoring Agent tracks mentions, corrections, source reliability
```

**Output:** 3-10 quality articles published daily

---

## Semi-Automated Model

**Machines Do:**
- Event discovery (RSS aggregation, social monitoring)
- Newsworthiness scoring (objective criteria)
- Source research and verification
- Article drafting (inverted pyramid, 5W+H, attribution)
- Self-audit (10-point checklist)
- Bias detection (hallucination, propaganda scans)
- Post-publication monitoring (social mentions, corrections)

**Humans Do:**
- Final editorial review (approve/reject/revise)
- Legal risk assessment
- Correction decisions
- Quality oversight
- Anonymous source justification

**Critical:** No article publishes without human approval (mandatory quality gate)

---

## Key Success Metrics

**Pipeline Efficiency:**
- Event discovery: 20-50 candidates/day
- Approval rate: 10-20% (2-10 topics advance)
- Generation rate: 80% of topics → published articles
- Rejection rate: <20% of drafts killed by editors
- Revision rate: <30% require editor-requested changes

**Quality Gates (All Must Pass):**
1. Newsworthiness score ≥60/100
2. Worker relevance score ≥50/100
3. ≥3 credible sources OR ≥2 academic citations
4. 10-point self-audit checklist (100% pass)
5. Bias scan clean (no hallucinations, propaganda)
6. Reading level 7.5-8.5 Flesch-Kincaid
7. Human editorial approval

**Quality Metrics:**
- Source compliance: 100% (≥3 sources)
- Reading level: 95% within target
- Attribution: 100% of factual claims attributed
- 5W+H coverage: 100% in first 3-4 paragraphs
- Correction rate: <5% of published articles

---

## Cost Breakdown (Estimated $44/month)

**Cloud Functions (Daily Automation):** $34.50/month
- Signal Intake: $3.00
- Evaluation: $1.50
- Verification: $9.00
- Article Generation: $12.00
- Editorial Coordination: $0.30
- Revision Handler: $6.00
- Auto-Publish: $0.30
- Monitoring: $2.40

**Cloud SQL (PostgreSQL):** $9.37/month (or $0 with free tier)
**Cloud Storage (Images):** $0.60/month
**APIs (Twitter, Reddit, RSS):** $0/month (all free tiers)
**LLM API (Article Generation):** $0/month (user-provided subscriptions)
**Monitoring & Email:** $0/month (free tiers)

**Total:** $44.47/month (within $30-100 target)

---

## Database Schema Additions

**New Tables:**
1. `event_candidates` - Stores discovered events with newsworthiness scores
2. `article_revisions` - Tracks revision history (editor feedback loop)
3. `corrections` - Post-publication correction notices
4. `source_reliability_log` - Learning loop for source credibility

**Table Enhancements:**
- `articles` table: +5 columns (bias_scan_report, self_audit_passed, editorial_notes, assigned_editor, review_deadline)
- `topics` table: +3 columns (verified_facts, source_plan, verification_status)

---

## Implementation Phases (Batch 6)

**Phase 6.1:** Database Schema Extensions (S complexity)
**Phase 6.2:** Signal Intake Agent (M complexity)
**Phase 6.3:** Evaluation Agent (M complexity) - Blocked by 6.1
**Phase 6.4:** Verification Agent (M complexity) - Blocked by 6.1, 6.3
**Phase 6.5:** Enhanced Journalist Agent (M complexity) - Blocked by 6.1, 6.4
**Phase 6.6:** Editorial Workflow Integration (S complexity) - Blocked by 6.5
**Phase 6.7:** Publication & Monitoring (S complexity) - Blocked by 6.6
**Phase 6.8:** Local Testing & Integration (S complexity) - Blocked by all prior phases

**Parallelization:**
- Phases 6.1-6.2 can run simultaneously
- Phases 6.3-6.5 can run simultaneously (after 6.1 complete)
- Phases 6.6-6.8 must run sequentially

**Estimated Timeline:** 4-6 weeks of agent work (no calendar deadlines)

---

## What Happens Next

**User Actions Required:**
1. **Review Analysis Document** (`automated-journalism-analysis.md`)
2. **Answer Open Questions** (Section 10.2):
   - Human editor availability (hours/day for review)
   - Beat priorities (which categories first?)
   - Source credibility thresholds (same for all categories?)
   - Revision loop limits (max revisions before kill?)
   - Monitoring scope (which social platforms?)
   - Local vs. national priority (start national-only or both?)
3. **Approve/Modify Roadmap** (Batch 6 in `roadmap.md`)
4. **Confirm Recommendations** (Section 10.3):
   - Start national-only, add local later?
   - Manual social posting for MVP?
   - Move Phase 6.8 to Batch 7 (cloud deployment)?

**After Approval:**
1. Create 6 agent definition files (`.claude/agents/*.md`)
2. Begin Phase 6.1 (Database Schema Extensions)
3. Coordinate agent assignments via agent-chat system (`#coordination` channel)

---

## Key Design Decisions

1. **Semi-Automated Model:** Balances efficiency (AI) with quality (human oversight)
2. **Daily Cadence:** Cloud Scheduler triggers pipeline at 6am daily
3. **Mandatory Human Gate:** No article publishes without editor approval
4. **Cost-Conscious:** GCP free tier + user-provided LLM subscriptions = $44/month
5. **Start Small:** 3-5 articles/day initially, scale with editor capacity
6. **Local-First:** Build and test all agents locally before cloud deployment
7. **Quality Over Quantity:** Better 3 excellent articles than 10 mediocre

---

## Risks & Mitigations

**Top Risks:**
1. LLM API rate limits → Use user subscriptions (higher limits), queue if exceeded
2. Source verification failures → Human editorial review catches gaps (mandatory gate)
3. Hallucinations in articles → Bias scan + human review + post-publication monitoring
4. Editor review bottleneck → Start small (3-5 articles/day), scale gradually
5. Cost overruns → GCP billing alerts, monthly cost review, reduce scope if needed

**Critical Safeguards:**
- Human editorial approval mandatory (no auto-publish without review)
- ≥3 credible sources required (fail-safe: reject topic if <3 sources)
- Post-publication monitoring (corrections within 12 hours if errors found)
- Source reliability tracking (learning loop improves over time)

---

## Success Criteria (Batch 6 Complete)

- [ ] All 8 phases complete
- [ ] Full pipeline runs locally (signal intake → publication)
- [ ] 3-5 quality articles generated daily in test environment
- [ ] Human editorial workflow functional (review → approve → publish)
- [ ] All quality gates pass (newsworthiness, verification, bias scan, editorial)
- [ ] Post-publication monitoring operational (corrections, source reliability)
- [ ] Documentation complete (agent definitions, operational procedures)
- [ ] Ready for cloud deployment (Batch 7)

---

## Files Created/Updated

**Created:**
- `/Users/home/sandbox/daily_worker/projects/DWnews/plans/automated-journalism-analysis.md` (comprehensive design document)
- `/Users/home/sandbox/daily_worker/projects/DWnews/plans/automated-journalism-summary.md` (this file)

**Updated:**
- `/Users/home/sandbox/daily_worker/projects/DWnews/plans/roadmap.md` (Batch 6 added with 8 phases)

**To Be Created (After User Approval):**
- `.claude/agents/signal-intake.md`
- `.claude/agents/evaluation.md`
- `.claude/agents/verification.md`
- `.claude/agents/editorial-coordinator.md`
- `.claude/agents/monitoring.md`
- Update `.claude/agents/journalist.md` (enhancements)

---

## Questions for User

1. **Editor Availability:** How many hours/day can editors dedicate to article review? (Determines daily article target)
2. **Beat Priorities:** Which categories should we prioritize for automated discovery first?
3. **National vs. Local:** Start national-only (simpler) or implement local from day 1 (more complex)?
4. **Revision Limits:** Maximum revisions before article is killed? (Suggest: 2)
5. **Monitoring Scope:** Track all social platforms or just Twitter/Reddit initially?
6. **Source Thresholds:** Same ≥3 sources for all categories, or higher for investigative?

---

**Prepared By:** Project Manager Agent
**Analysis Depth:** 12 sections, 400+ lines, complete system design
**Next Action:** User reviews analysis, answers questions, approves Batch 6 roadmap

---

**End of Summary**
