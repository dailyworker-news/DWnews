# Automated Journalism Pipeline - Technical Architecture

**Project:** The Daily Worker (DWnews)
**Date:** 2025-12-31
**Purpose:** Visual architecture diagrams for the automated journalism system

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DAILY JOURNALISM PIPELINE                         │
│                    (3-10 Articles Published Daily)                   │
└─────────────────────────────────────────────────────────────────────┘

                              EXTERNAL SOURCES
┌────────────────────────────────────────────────────────────────────┐
│  RSS Feeds          Twitter API        Reddit API    Government    │
│  (Reuters, AP,      (Labor topics,     (r/labor,     (data.gov,    │
│  ProPublica,        worker hashtags)   r/antiwork)   Labor Dept)   │
│  local sources)                                                     │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 1: EVENT DISCOVERY (Signal Intake Agent)                     │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (6:00 AM daily)                          │
│  Duration: ~30 minutes                                              │
│  Tasks:                                                             │
│    • Aggregate RSS feeds                                            │
│    • Monitor social media (Twitter, Reddit)                         │
│    • Scrape government feeds                                        │
│    • Deduplicate events                                             │
│  Output: 20-50 event candidates → event_candidates table            │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 2: NEWSWORTHINESS EVALUATION (Evaluation Agent)              │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (6:30 AM daily)                          │
│  Duration: ~20 minutes                                              │
│  Scoring Model (0-100 total):                                       │
│    • Impact: 0-20 (worker economic/safety impact)                   │
│    • Timeliness: 0-20 (recency and urgency)                         │
│    • Proximity: 0-15 (geographic relevance)                         │
│    • Conflict: 0-15 (power dynamics, labor vs. capital)             │
│    • Novelty: 0-15 (new vs. recurring story)                        │
│    • Verifiability: 0-15 (source availability)                      │
│  Thresholds:                                                        │
│    • <30: Reject                                                    │
│    • 30-59: Hold (future consideration)                             │
│    • ≥60: Approve for article generation                            │
│  Output: 2-10 approved topics → topics table                        │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 3-4: VERIFICATION & SOURCING (Verification Agent)            │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (7:00 AM daily)                          │
│  Duration: ~45 minutes per topic (parallel processing)              │
│  Tasks:                                                             │
│    • Identify ≥3 credible sources OR ≥2 academic citations          │
│    • Cross-reference contentious claims (independent corroboration) │
│    • Classify facts: observed, claimed, interpreted                 │
│    • Plan attribution hierarchy: named > org > docs > anon          │
│  Output: verified_facts + source_plan (JSON) in topics table       │
│                                                                     │
│  QUALITY GATE 1: Reject topic if <3 sources found                  │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 5-7: ARTICLE DRAFTING (Enhanced Journalist Agent)            │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (8:00 AM daily)                          │
│  Duration: ~30 minutes per article (parallel processing)            │
│  Tasks:                                                             │
│    • Generate article using verified_facts (inverted pyramid)       │
│    • Ensure 5W+H in first 3-4 paragraphs                            │
│    • Add nut graf (why it matters)                                  │
│    • Proper attribution (use source_plan)                           │
│    • Self-audit checklist (10-point validation):                    │
│       1. Event understandable in 10 seconds?                        │
│       2. 5W+H answered early?                                       │
│       3. All facts attributed?                                      │
│       4. ≥3 sources verified?                                       │
│       5. Quotes add value (not filler)?                             │
│       6. Nut graf present?                                          │
│       7. Worker relevance clear?                                    │
│       8. Reading level 7.5-8.5 FK?                                  │
│       9. "Why This Matters" section?                                │
│      10. Neutral tone maintained?                                   │
│    • Bias detection scan (hallucinations, propaganda, errors)       │
│    • Reading level validation (Flesch-Kincaid scoring)              │
│  Output: Draft articles → articles table (status='pending_review')  │
│                                                                     │
│  QUALITY GATE 2: 100% of articles must pass 10-point self-audit    │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 8: HUMAN EDITORIAL REVIEW (Manual Gate)                      │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Editorial Coordinator Agent assigns (9:00 AM)             │
│  Duration: Variable (editor reviews throughout day)                 │
│  Review Interface (Admin Portal):                                   │
│    • Display article draft                                          │
│    • Show bias scan report                                          │
│    • List verified sources                                          │
│    • Display self-audit results                                     │
│  Editor Actions:                                                    │
│    1. Approve → status='approved' (ready for publication)           │
│    2. Request Revision → add editorial_notes, status='draft'        │
│    3. Kill → status='rejected', add rejection_reason               │
│    4. Escalate → assign to senior editor                            │
│  Revision Loop:                                                     │
│    • Journalist Agent rewrites based on editorial_notes             │
│    • Log revision in article_revisions table                        │
│    • Return to editor (status='pending_review')                     │
│    • Max revisions: 2 (configurable)                                │
│                                                                     │
│  QUALITY GATE 3: MANDATORY - No article publishes without human OK │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  PUBLICATION (Automated)                                            │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (5:00 PM daily)                           │
│  Duration: ~5 minutes                                               │
│  Tasks:                                                             │
│    • Query articles (status='approved')                             │
│    • Update status='published', set published_at timestamp          │
│    • Generate social sharing copy (stored for manual posting)       │
│    • Trigger CDN cache refresh (if using CDN)                       │
│  Output: 3-10 articles published to live site                       │
└────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│  STEP 9-10: POST-PUBLICATION MONITORING (Monitoring Agent)         │
│  ─────────────────────────────────────────────────────────────────  │
│  Trigger: Cloud Scheduler (every 6 hours: 12am, 6am, 12pm, 6pm)    │
│  Duration: ~15 minutes                                              │
│  Scope: Articles published in last 7 days                           │
│  Tasks:                                                             │
│    • Monitor Twitter/Reddit for mentions and responses              │
│    • Detect potential corrections (new contradictory facts)         │
│    • Flag articles needing corrections → human editor review        │
│    • Update source_reliability_log:                                 │
│       - 'claim_verified' → +5 impact                                │
│       - 'claim_false' → -10 impact                                  │
│       - 'correction_needed' → -5 impact                             │
│    • Track patterns (recurring false positives)                     │
│  Output: Correction flags, source credibility updates               │
│                                                                     │
│  QUALITY GATE 4: Human editor approves correction before publish   │
└────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
[Event Sources] → [event_candidates] → [topics] → [articles] → [Published]
                         ↓                  ↓          ↓            ↓
                   (discovered)       (approved)  (pending)   (published)
                                                     ↓
                                            [article_revisions]
                                                     ↓
                                              [corrections]
                                                     ↓
                                          [source_reliability_log]
```

**Detailed Data Flow:**

1. **Signal Intake Agent** writes to `event_candidates` (status='discovered')
2. **Evaluation Agent** reads `event_candidates`, creates `topics` (status='approved'/'rejected')
3. **Verification Agent** reads `topics` (status='approved'), updates with verified_facts + source_plan
4. **Journalist Agent** reads `topics` (verified), writes to `articles` (status='pending_review')
5. **Editorial Coordinator** assigns `articles` to human editors (assigned_editor field)
6. **Human Editor** reviews via admin portal, updates status ('approved'/'draft'/'rejected')
7. **Revision Loop** (if needed): Journalist Agent reads editorial_notes, rewrites, logs to `article_revisions`
8. **Auto-Publish** updates `articles` (status='published', published_at timestamp)
9. **Monitoring Agent** reads published `articles`, writes to `corrections` and `source_reliability_log`

---

## Agent Interaction Matrix

```
Agent                    Reads From                Writes To                  Triggers
─────────────────────────────────────────────────────────────────────────────────────
Signal Intake            External APIs             event_candidates           Daily 6am
Evaluation               event_candidates          topics, event_candidates   Daily 6:30am
Verification             topics                    topics                     Daily 7am
Enhanced Journalist      topics                    articles                   Daily 8am
Editorial Coordinator    articles                  articles                   Daily 9am
Revision Handler         articles, editorial_notes articles, revisions        On-demand
Auto-Publish             articles                  articles                   Daily 5pm
Monitoring               articles (published)      corrections, reliability   Every 6 hrs
```

---

## Database Schema Relationships

```
┌─────────────────┐
│ event_candidates│
│ ────────────────│
│ id              │
│ title           │
│ source_url      │───┐
│ discovered_from │   │
│ impact_score    │   │
│ total_score     │   │
│ status          │   │ (1 event → 0-1 topic)
│ topic_id        │───┘
└─────────────────┘
         │
         │ (creates)
         ▼
┌─────────────────┐         ┌──────────────┐
│     topics      │         │  categories  │
│ ────────────────│         │──────────────│
│ id              │◄────────│ id           │
│ title           │         │ name         │
│ category_id     │         │ slug         │
│ verified_facts  │         └──────────────┘
│ source_plan     │
│ status          │         ┌──────────────┐
│ article_id      │────────►│   regions    │
│ region_id       │         │──────────────│
└─────────────────┘         │ id           │
         │                  │ name         │
         │ (generates)      │ state_code   │
         ▼                  └──────────────┘
┌─────────────────┐
│    articles     │
│ ────────────────│
│ id              │
│ title           │
│ body            │
│ category_id     │───┐
│ region_id       │───┤
│ status          │   │
│ bias_scan_report│   │
│ editorial_notes │   │
│ assigned_editor │   │
│ published_at    │   │
└─────────────────┘   │
         │            │
         ├────────────┤
         │            │
         ▼            ▼
┌─────────────────┐ ┌──────────────────┐
│article_revisions│ │  article_sources │
│─────────────────│ │──────────────────│
│ id              │ │ article_id       │
│ article_id      │ │ source_id        │───┐
│ revision_number │ │ citation_url     │   │
│ body            │ │ citation_text    │   │
│ revised_by      │ └──────────────────┘   │
│ revision_reason │                        │
└─────────────────┘                        ▼
         │                        ┌──────────────────────┐
         │                        │      sources         │
         │                        │──────────────────────│
         │                        │ id                   │
         │                        │ name                 │
         ▼                        │ credibility_score    │
┌─────────────────┐               │ source_type          │
│  corrections    │               │ is_active            │
│─────────────────│               └──────────────────────┘
│ id              │                        │
│ article_id      │                        │
│ correction_text │                        ▼
│ corrected_by    │               ┌──────────────────────┐
│ corrected_at    │               │source_reliability_log│
└─────────────────┘               │──────────────────────│
                                  │ id                   │
                                  │ source_id            │
                                  │ article_id           │
                                  │ event                │
                                  │ impact (+/- score)   │
                                  │ notes                │
                                  └──────────────────────┘
```

---

## Cloud Function Architecture (GCP)

```
┌────────────────────────────────────────────────────────────────┐
│                   CLOUD SCHEDULER (GCP)                         │
│ ────────────────────────────────────────────────────────────────│
│  Daily 6:00 AM  → signal-intake-function                        │
│  Daily 6:30 AM  → evaluate-newsworthiness-function              │
│  Daily 7:00 AM  → verify-sources-function                       │
│  Daily 8:00 AM  → generate-articles-function                    │
│  Daily 9:00 AM  → editorial-coordination-function               │
│  Daily 5:00 PM  → auto-publish-function                         │
│  Every 6 hours  → post-publication-monitor-function             │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                  CLOUD FUNCTIONS (Serverless)                   │
│ ────────────────────────────────────────────────────────────────│
│                                                                 │
│  signal-intake-function:                                        │
│    Runtime: Python 3.11, Memory: 512MB, Timeout: 30 min        │
│    Cost: ~$0.10/day                                             │
│                                                                 │
│  evaluate-newsworthiness-function:                              │
│    Runtime: Python 3.11, Memory: 256MB, Timeout: 20 min        │
│    Cost: ~$0.05/day                                             │
│                                                                 │
│  verify-sources-function:                                       │
│    Runtime: Python 3.11, Memory: 1GB, Timeout: 60 min          │
│    Cost: ~$0.30/day (includes LLM calls)                        │
│                                                                 │
│  generate-articles-function:                                    │
│    Runtime: Python 3.11, Memory: 1GB, Timeout: 60 min          │
│    Cost: ~$0.40/day (includes LLM calls)                        │
│                                                                 │
│  editorial-coordination-function:                               │
│    Runtime: Python 3.11, Memory: 128MB, Timeout: 5 min         │
│    Cost: ~$0.01/day                                             │
│                                                                 │
│  revision-handler-function:                                     │
│    Runtime: Python 3.11, Memory: 1GB, Timeout: 30 min          │
│    Trigger: Database trigger (status='draft')                   │
│    Cost: ~$0.20/day (on-demand)                                 │
│                                                                 │
│  auto-publish-function:                                         │
│    Runtime: Python 3.11, Memory: 128MB, Timeout: 5 min         │
│    Cost: ~$0.01/day                                             │
│                                                                 │
│  post-publication-monitor-function:                             │
│    Runtime: Python 3.11, Memory: 256MB, Timeout: 15 min        │
│    Cost: ~$0.08/day (4 executions)                              │
│                                                                 │
│  Total Cloud Functions Cost: $34.50/month                       │
└────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                  CLOUD SQL (PostgreSQL)                         │
│ ────────────────────────────────────────────────────────────────│
│  Instance: db-f1-micro (free tier eligible)                     │
│  Storage: 10GB SSD                                              │
│  Backups: Daily automated                                       │
│  Cost: $9.37/month (or $0 with free tier)                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Quality Gate Flow

```
Event Candidate
     │
     ▼
[GATE 1: Newsworthiness Score]
     │
     ├─── Score <30: REJECT
     ├─── Score 30-59: HOLD (future consideration)
     └─── Score ≥60: APPROVE
              │
              ▼
[GATE 2: Source Verification]
     │
     ├─── <3 sources: REJECT TOPIC
     └─── ≥3 sources: APPROVE
              │
              ▼
[GATE 3: Self-Audit Checklist]
     │
     ├─── Any check fails: FLAG FOR REVIEW
     └─── All 10 checks pass: PROCEED
              │
              ▼
[GATE 4: Bias Detection Scan]
     │
     ├─── Hallucinations detected: FLAG
     ├─── Propaganda detected: FLAG
     └─── Clean scan: PROCEED
              │
              ▼
[GATE 5: Human Editorial Review] ← MANDATORY
     │
     ├─── Approve: PUBLISH
     ├─── Request Revision: RETURN TO JOURNALIST
     ├─── Kill: REJECT ARTICLE
     └─── Escalate: SENIOR EDITOR REVIEW
              │
              ▼
[GATE 6: Post-Publication Monitoring]
     │
     ├─── Correction needed: EDITOR APPROVAL → PUBLISH CORRECTION
     └─── No issues: CONTINUE MONITORING
```

---

## Cost Allocation by Component

```
Component                      Monthly Cost    Percentage    Free Tier?
───────────────────────────────────────────────────────────────────────
Cloud Functions                $34.50          77.6%         Partial
Cloud SQL (PostgreSQL)         $9.37           21.1%         Yes
Cloud Storage (Images)         $0.60           1.3%          Yes
APIs (Twitter, Reddit, RSS)    $0.00           0.0%          Yes
LLM (Article Generation)       $0.00           0.0%          User-provided
Monitoring & Logging           $0.00           0.0%          Yes (free tier)
Email (SendGrid)               $0.00           0.0%          Yes (free tier)
───────────────────────────────────────────────────────────────────────
TOTAL                          $44.47          100%
```

**Cost Optimization Opportunities:**
1. Use GCP free tier for Cloud SQL → Save $9.37/month
2. Cache RSS/social queries → Reduce Cloud Function runtime
3. Batch processing → Reduce Cloud Function invocations
4. Use Cloud Run instead of Cloud Functions for longer tasks → Lower cost

**Budget Compliance:**
- Target: $30-100/month
- Estimated: $44.47/month
- Status: ✅ Within budget (56% margin to upper limit)

---

## Agent Coordination (Agent Chat System)

**Channel Usage:**

```
#roadmap channel:
  - Batch 6 planning updates
  - Phase completion announcements
  - Agent definition creation notices

#coordination channel:
  - Phase assignments (which agent works on what)
  - File edit announcements (avoid conflicts)
  - Status updates (phase progress)

#errors channel:
  - Pipeline failures
  - Cloud Function errors
  - Database connection issues
  - API rate limit warnings
```

**Example Messages:**

```javascript
// Project Manager announces Batch 6 start
set_handle({ handle: "project-manager" })
publish_message({
  channel: "roadmap",
  message: "Starting Batch 6: Automated Journalism Pipeline. 8 phases defined. See roadmap.md"
})

// Backend Agent announces Phase 6.1 start
set_handle({ handle: "backend-dev-01" })
publish_message({
  channel: "coordination",
  message: "Starting Phase 6.1 (Database Schema). Editing: database/schema.sql, database/migrations/. ETA: 2 hours"
})

// Agent reports completion
publish_message({
  channel: "coordination",
  message: "Phase 6.1 complete. 4 new tables created, tested locally. Database ready for agents."
})
```

---

## Next Steps Checklist

**User Actions:**
- [ ] Review `automated-journalism-analysis.md` (full design)
- [ ] Review this architecture document
- [ ] Answer open questions (Section 10.2 of analysis)
- [ ] Approve Batch 6 roadmap phases
- [ ] Confirm recommendations (national-only first, manual social posting, etc.)

**Project Manager Actions (After Approval):**
- [ ] Create 6 agent definition files:
  - `.claude/agents/signal-intake.md`
  - `.claude/agents/evaluation.md`
  - `.claude/agents/verification.md`
  - `.claude/agents/editorial-coordinator.md`
  - `.claude/agents/monitoring.md`
  - Update `.claude/agents/journalist.md`
- [ ] Announce Batch 6 start in `#roadmap` channel
- [ ] Assign Phase 6.1 to backend agent

**Development Sequence:**
1. Phase 6.1: Database Schema Extensions (S)
2. Phase 6.2: Signal Intake Agent (M) - Parallel with 6.1
3. Phase 6.3: Evaluation Agent (M) - After 6.1
4. Phase 6.4: Verification Agent (M) - After 6.1, 6.3
5. Phase 6.5: Enhanced Journalist Agent (M) - After 6.1, 6.4
6. Phase 6.6: Editorial Workflow (S) - After 6.5
7. Phase 6.7: Monitoring (S) - After 6.6
8. Phase 6.8: Local Testing (S) - After all prior phases

---

**Document Prepared By:** Project Manager Agent
**Diagrams:** System architecture, data flow, agent interaction, database relationships, cloud functions, quality gates, cost allocation
**Status:** Ready for user review

---

**End of Architecture Document**
