# Automated Journalism Pipeline - Implementation Analysis

**Document Version:** 1.0
**Date:** 2025-12-31
**Project:** The Daily Worker (DWnews)
**Purpose:** Analyze 10-step Agentic Journalist Process and design implementation strategy

---

## Executive Summary

The user has provided a comprehensive 10-step **Agentic Journalist Process** that defines a rigorous, end-to-end pipeline for autonomous news article generation. This document analyzes the process against current Daily Worker infrastructure, identifies gaps, designs the automated execution structure, and creates a phased roadmap for implementation.

**Key Findings:**
- Current infrastructure provides foundational elements (database schema, basic content pipeline, web portal)
- Significant gaps exist in automated discovery, verification, and monitoring systems
- Implementation requires 6 new specialized agents + enhanced infrastructure
- Daily cadence achievable through scheduled Cloud Functions + agent coordination
- Cost target ($30-100/month) constrains automation approach
- Human oversight remains critical at key quality gates

**Recommended Approach:**
- Implement as **Batch 6** (after design improvements in Batch 5)
- Build incrementally: Discovery → Verification → Drafting → Editorial → Publication → Monitoring
- Semi-automated model: Machines discover and draft, humans verify and approve
- Daily scheduling via Cloud Scheduler (GCP) triggering agent workflows

---

## 1. Current Infrastructure Assessment

### 1.1 What Exists (Batches 1-4 Complete)

**Database Schema:**
- ✅ `articles` table with comprehensive metadata
- ✅ `sources` table with credibility scoring
- ✅ `categories` table (9 categories defined)
- ✅ `regions` table for national/local differentiation
- ✅ `topics` table for content discovery tracking
- ✅ `article_sources` junction table for source attribution

**Backend Services:**
- ✅ FastAPI application with article CRUD endpoints
- ✅ SQLite database (local) with PostgreSQL migration path
- ✅ Authentication system for admin/editor access
- ✅ Logging and error tracking

**Frontend Portal:**
- ✅ Article display with filtering (category, region, ongoing/new)
- ✅ Admin interface for content review
- ✅ Responsive design (mobile-first)

**Agent Definitions:**
- ✅ Journalist agent (general article generation)
- ✅ Project manager agent (roadmap management)
- ✅ Business analyst agent (prioritization)
- ✅ Requirements reviewer agent

**Standards & Guidelines:**
- ✅ Professional journalism standards document
- ✅ Editorial workflow defined (draft → AI review → human review → publish)
- ✅ Reading level requirements (7.5-8.5 Flesch-Kincaid)
- ✅ Source verification rules (≥3 credible OR ≥2 academic)

### 1.2 What's Missing (Implementation Gaps)

**Step 0-1: Event Discovery (Signal Intake)**
- ❌ Automated monitoring of government/institutional feeds
- ❌ Document change detection systems
- ❌ RSS feed aggregation and parsing
- ❌ Social media monitoring (Twitter/Reddit API integration)
- ❌ Beat-specific signal processors
- ❌ Secure whistleblower submission system
- ❌ Event candidate record schema

**Step 2: Newsworthiness Evaluation**
- ❌ Scoring algorithm (Impact, Timeliness, Proximity, Conflict, Novelty, Verifiability)
- ❌ Threshold configuration (Discard, Hold, Advance)
- ❌ Worker-relevance scoring model
- ❌ Automated topic prioritization

**Step 3: Verification & Corroboration**
- ❌ Primary source identification automation
- ❌ Cross-reference verification system
- ❌ Fact distinction logic (observed vs. claimed vs. interpreted)
- ❌ Automated credibility checking
- ❌ Verified fact set schema

**Step 4: Sourcing & Attribution Planning**
- ❌ Source hierarchy enforcement
- ❌ Anonymous source justification workflow
- ❌ Attribution plan templates
- ❌ Source contact management

**Step 5-7: Article Framing, Drafting, Editorial Review**
- ⚠️ **Partially exists:** Journalist agent can draft
- ❌ Structure selection automation
- ❌ Bias detection tooling (mentioned in requirements, not implemented)
- ❌ Self-audit checklist automation
- ❌ Revision workflow (feedback loop to agent)

**Step 8: Publication Readiness Decision**
- ❌ Multi-criteria decision framework (Publish, Hold, Kill, Escalate)
- ❌ Accuracy validation gates
- ❌ Legal risk assessment

**Step 9: Post-Publication Monitoring**
- ❌ Correction tracking system
- ❌ Response monitoring (social media, reader feedback)
- ❌ Update workflow for published articles
- ❌ Transparent correction mechanism

**Step 10: Learning & Beat Memory**
- ❌ Source reliability scoring updates
- ❌ Pattern recognition across articles
- ❌ False positive tracking
- ❌ Editorial feedback integration
- ❌ Agent performance improvement loop

---

## 2. System Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DAILY JOURNALISM PIPELINE                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Cloud Scheduler │  ← Daily 6am trigger
│   (GCP/Cron)     │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 0-1: EVENT DISCOVERY (Signal Intake Agent)                 │
│ ─────────────────────────────────────────────────────────────────│
│ • RSS Feed Aggregator (Reuters, AP, ProPublica, local sources)  │
│ • Social Monitor (Twitter API, Reddit API)                       │
│ • Government Feed Watcher (Press releases, data.gov)            │
│ • Beat-Specific Scrapers (Labor Dept, NLRB, local govt)         │
│ Output: Event candidates → topics table (status='discovered')   │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: NEWSWORTHINESS EVALUATION (Evaluation Agent)            │
│ ─────────────────────────────────────────────────────────────────│
│ • Score: Impact, Timeliness, Proximity, Conflict, Novelty       │
│ • Worker-Relevance Scoring (income bracket $45k-$350k impact)   │
│ • Verifiability Check (source count, academic citations)        │
│ • Decision: Discard (<30), Hold (30-60), Advance (>60)          │
│ Output: topics table updated (status='approved'/'rejected')     │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3-4: VERIFICATION & SOURCING (Verification Agent)          │
│ ─────────────────────────────────────────────────────────────────│
│ • Primary Source Identification (WebSearch, document analysis)  │
│ • Independent Corroboration (cross-reference verification)      │
│ • Fact Classification (observed, claimed, interpreted)          │
│ • Source Attribution Planning (hierarchy enforcement)           │
│ Output: Verified fact set + source plan in topics.description   │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5-7: ARTICLE DRAFTING (Journalist Agent - Enhanced)        │
│ ─────────────────────────────────────────────────────────────────│
│ • Structure Selection (inverted pyramid default)                │
│ • Article Generation (5W+H, nut graf, attribution)              │
│ • Self-Audit Checklist (10-point validation)                    │
│ • Bias Detection (hallucination scan, propaganda check)         │
│ Output: articles table (status='pending_review')                │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: HUMAN EDITORIAL REVIEW (Manual Gate)                    │
│ ─────────────────────────────────────────────────────────────────│
│ • Human editor reviews draft via admin portal                   │
│ • Decision: Publish / Request Revision / Kill / Escalate        │
│ • Revision loop: Journalist agent rewrites based on notes       │
│ Output: articles table (status='approved' or back to draft)     │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ PUBLICATION (Automated)                                          │
│ ─────────────────────────────────────────────────────────────────│
│ • Update status='published', set published_at timestamp         │
│ • Generate social sharing copy (manual posting for MVP)         │
│ • Trigger CDN cache refresh                                     │
└────────┬─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9-10: POST-PUBLICATION (Monitoring Agent)                  │
│ ─────────────────────────────────────────────────────────────────│
│ • Monitor social responses (Twitter, Reddit mentions)           │
│ • Track corrections needed (new facts, errors)                  │
│ • Update article transparently (correction notices)             │
│ • Learning Loop: Update source reliability, pattern tracking    │
│ Output: Corrections logged, source scores updated               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent Definitions (New)

**1. Signal Intake Agent**
- **Responsibility:** Steps 0-1 (Event Discovery)
- **Triggers:** Daily at 6am via Cloud Scheduler
- **Inputs:** RSS feeds, Twitter API, Reddit API, government sites
- **Outputs:** Event candidates written to `topics` table (status='discovered')
- **Tools:** WebFetch, WebSearch, RSS parsers, API clients
- **Complexity:** Medium (API integration, parsing logic)

**2. Evaluation Agent**
- **Responsibility:** Step 2 (Newsworthiness Scoring)
- **Triggers:** After Signal Intake completes (topics.status='discovered')
- **Inputs:** Event candidates from `topics` table
- **Outputs:** Scored topics (status='approved'/'rejected'/'hold')
- **Scoring Model:**
  - Impact (0-20): Worker economic/safety impact
  - Timeliness (0-20): Recency and urgency
  - Proximity (0-15): Geographic relevance (national vs. local)
  - Conflict (0-15): Power dynamics, labor vs. capital
  - Novelty (0-15): New vs. recurring story
  - Verifiability (0-15): Source availability
  - **Total:** 0-100, threshold: <30 reject, 30-59 hold, ≥60 approve
- **Tools:** WebSearch (source counting), LLM reasoning
- **Complexity:** Medium (scoring logic, thresholds)

**3. Verification Agent**
- **Responsibility:** Steps 3-4 (Source Verification & Attribution Planning)
- **Triggers:** After evaluation (topics.status='approved')
- **Inputs:** Approved topics
- **Outputs:** Verified fact sets + source plans (stored in topics.description as JSON)
- **Verification Tasks:**
  - Identify ≥3 credible sources OR ≥2 academic citations
  - Cross-reference contentious claims
  - Classify facts (observed, claimed, interpreted)
  - Plan attribution hierarchy (named > org > docs > anon)
- **Tools:** WebSearch, WebFetch, document analysis
- **Complexity:** High (research depth, fact classification)

**4. Enhanced Journalist Agent**
- **Responsibility:** Steps 5-7 (Article Drafting + Self-Audit)
- **Triggers:** After verification complete
- **Inputs:** Verified fact sets from `topics` table
- **Outputs:** Draft articles in `articles` table (status='pending_review')
- **Enhancements Over Current Agent:**
  - Self-audit checklist automation (10-point validation)
  - Bias detection integration (hallucination scan, propaganda check)
  - Reading level validation (Flesch-Kincaid scoring)
  - Structure selection logic (inverted pyramid enforcement)
- **Tools:** WebFetch (quote gathering), Write (article output)
- **Complexity:** High (already partially exists, needs enhancement)

**5. Editorial Coordinator Agent**
- **Responsibility:** Step 8 orchestration (not decision-making)
- **Triggers:** When articles.status='pending_review'
- **Inputs:** Draft articles
- **Outputs:** Email notifications to human editors, workflow tracking
- **Tasks:**
  - Assign articles to human editors (round-robin or by beat)
  - Send review notifications
  - Track review status and SLA
  - Route revision requests back to Journalist Agent
- **Tools:** Email/notification systems, database updates
- **Complexity:** Low (orchestration only, humans decide)

**6. Monitoring Agent**
- **Responsibility:** Steps 9-10 (Post-Publication Monitoring + Learning)
- **Triggers:** Continuous (every 6 hours for published articles)
- **Inputs:** Published articles from last 7 days
- **Outputs:** Correction notices, source reliability updates
- **Monitoring Tasks:**
  - Social media mention tracking (Twitter/Reddit API)
  - Correction detection (new facts contradicting article)
  - Source reliability scoring (did claims hold up?)
  - Pattern recognition (recurring false positives)
  - Editorial feedback integration (human corrections logged)
- **Tools:** Twitter API, Reddit API, WebSearch, database updates
- **Complexity:** Medium (continuous monitoring, learning loop)

### 2.3 Data Flow Diagram (Text Format)

```
[RSS Feeds] ──┐
[Twitter API]─┤
[Reddit API]─ ├──→ [Signal Intake Agent] ──→ topics (status='discovered')
[Gov Sites]───┤                                        │
[Documents]──┘                                         ▼
                                          [Evaluation Agent] ──→ topics (status='approved'/'rejected')
                                                       │
                                                       ▼
                                          [Verification Agent] ──→ topics (verified facts + sources)
                                                       │
                                                       ▼
                                          [Journalist Agent] ──→ articles (status='pending_review')
                                                       │
                                                       ▼
                                          [Editorial Coordinator] ──→ [Human Editor]
                                                       │                     │
                                                       ▼                     ▼
                                              (if approved)        (if revision needed)
                                                       │                     │
                                                       ▼                     ▼
                                          articles (status='published')   [Back to Journalist]
                                                       │
                                                       ▼
                                          [Monitoring Agent] ──→ Corrections, Source Updates
```

### 2.4 Database Schema Additions Required

**New Table: `event_candidates`**
```sql
CREATE TABLE event_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT NOT NULL,
    discovered_from TEXT NOT NULL, -- 'rss', 'twitter', 'reddit', 'government', 'manual'
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Newsworthiness scores
    impact_score INTEGER DEFAULT 0,
    timeliness_score INTEGER DEFAULT 0,
    proximity_score INTEGER DEFAULT 0,
    conflict_score INTEGER DEFAULT 0,
    novelty_score INTEGER DEFAULT 0,
    verifiability_score INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,

    -- Processing status
    status TEXT DEFAULT 'discovered' CHECK(status IN ('discovered', 'evaluated', 'approved', 'rejected', 'hold', 'generated')),
    rejection_reason TEXT,

    -- Relationships
    topic_id INTEGER,
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);
```

**New Table: `article_revisions`**
```sql
CREATE TABLE article_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    revision_number INTEGER NOT NULL,
    body TEXT NOT NULL,
    revised_by TEXT NOT NULL, -- 'journalist_agent' or editor email
    revision_reason TEXT,
    revised_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);
```

**New Table: `corrections`**
```sql
CREATE TABLE corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    correction_text TEXT NOT NULL,
    what_changed TEXT NOT NULL,
    reason TEXT NOT NULL,
    corrected_by TEXT NOT NULL,
    corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);
```

**New Table: `source_reliability_log`**
```sql
CREATE TABLE source_reliability_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    article_id INTEGER,
    event TEXT NOT NULL, -- 'claim_verified', 'claim_false', 'correction_needed', 'no_issue'
    impact INTEGER DEFAULT 0, -- positive for good, negative for bad
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (article_id) REFERENCES articles(id)
);
```

**Additions to Existing `articles` Table:**
```sql
ALTER TABLE articles ADD COLUMN bias_scan_report TEXT; -- JSON blob from AI bias scan
ALTER TABLE articles ADD COLUMN self_audit_passed BOOLEAN DEFAULT 0;
ALTER TABLE articles ADD COLUMN editorial_notes TEXT;
ALTER TABLE articles ADD COLUMN assigned_editor TEXT;
ALTER TABLE articles ADD COLUMN review_deadline TIMESTAMP;
```

**Additions to Existing `topics` Table:**
```sql
ALTER TABLE topics ADD COLUMN verified_facts TEXT; -- JSON blob of verified fact set
ALTER TABLE topics ADD COLUMN source_plan TEXT; -- JSON blob of attribution plan
ALTER TABLE topics ADD COLUMN verification_status TEXT DEFAULT 'pending';
```

---

## 3. Daily Cadence Implementation

### 3.1 Scheduled Workflow (Cloud Scheduler + Cloud Functions)

**Daily Schedule:**

```
06:00 AM - Signal Intake Agent (Cloud Function 1)
│ Duration: ~30 minutes
│ Tasks:
│  - Fetch RSS feeds (Reuters, AP, ProPublica, local sources)
│  - Monitor Twitter API (trending labor topics, worker hashtags)
│  - Monitor Reddit API (r/labor, r/WorkReform, r/antiwork, local city subs)
│  - Scrape government feeds (Labor Dept, NLRB, data.gov)
│  - Write event candidates to `event_candidates` table
│
▼
06:30 AM - Evaluation Agent (Cloud Function 2)
│ Duration: ~20 minutes
│ Tasks:
│  - Query event_candidates (status='discovered')
│  - Score each on 6 dimensions (Impact, Timeliness, Proximity, etc.)
│  - Update status: 'approved' (≥60), 'hold' (30-59), 'rejected' (<30)
│  - Create topic records for approved events
│
▼
07:00 AM - Verification Agent (Cloud Function 3)
│ Duration: ~45 minutes per topic (parallel for multiple topics)
│ Tasks:
│  - Query topics (status='approved', verification_status='pending')
│  - Research ≥3 credible sources per topic
│  - Cross-reference contentious claims
│  - Classify facts (observed, claimed, interpreted)
│  - Store verified_facts and source_plan in topics table
│
▼
08:00 AM - Journalist Agent (Cloud Function 4)
│ Duration: ~30 minutes per article (parallel for multiple articles)
│ Tasks:
│  - Query topics (verification_status='complete', status='approved')
│  - Generate article draft using verified facts
│  - Run self-audit checklist (10-point validation)
│  - Run bias scan (hallucination, propaganda detection)
│  - Check reading level (Flesch-Kincaid 7.5-8.5)
│  - Write to articles table (status='pending_review')
│
▼
09:00 AM - Editorial Coordinator Agent (Cloud Function 5)
│ Duration: ~5 minutes
│ Tasks:
│  - Query articles (status='pending_review', assigned_editor IS NULL)
│  - Assign to human editors (round-robin by beat)
│  - Send email notifications with review links
│  - Set review_deadline (24 hours from now)
│
▼
09:00 AM - 5:00 PM - HUMAN EDITORIAL REVIEW
│ Duration: Variable (editor reviews drafts)
│ Tasks:
│  - Editors log into admin portal
│  - Review articles, check bias scan, verify sources
│  - Decision: Approve, Request Revision, Kill
│  - If revision: add editorial_notes, status='draft'
│
▼
Throughout Day - Revision Loop (Cloud Function 6)
│ Trigger: When articles.status='draft' AND editorial_notes IS NOT NULL
│ Tasks:
│  - Journalist Agent rewrites based on editorial_notes
│  - Increment revision_number
│  - Log revision in article_revisions table
│  - Reset status='pending_review'
│
▼
5:00 PM - Auto-Publish Approved Articles (Cloud Function 7)
│ Duration: ~5 minutes
│ Tasks:
│  - Query articles (status='approved')
│  - Update status='published', set published_at timestamp
│  - Generate social sharing copy (stored for manual posting)
│  - Trigger CDN cache refresh (if using CDN)
│
▼
Every 6 Hours - Monitoring Agent (Cloud Function 8)
│ Duration: ~15 minutes
│ Tasks:
│  - Query articles (published_at > NOW() - 7 days)
│  - Check Twitter/Reddit for mentions and responses
│  - Detect potential corrections (new contradictory facts)
│  - Update source_reliability_log based on claims holding up
│  - Flag articles needing corrections
```

### 3.2 Cloud Functions Architecture (GCP)

**Function 1: signal-intake**
- **Trigger:** Cloud Scheduler (cron: `0 6 * * *`)
- **Runtime:** Python 3.11
- **Memory:** 512MB
- **Timeout:** 30 minutes
- **Environment Variables:** TWITTER_API_KEY, REDDIT_API_KEY, RSS_FEED_URLS
- **Estimated Cost:** $0.10/day (30 min execution, 512MB)

**Function 2: evaluate-newsworthiness**
- **Trigger:** Cloud Scheduler (cron: `30 6 * * *`) OR Pub/Sub message from Function 1
- **Runtime:** Python 3.11
- **Memory:** 256MB
- **Timeout:** 20 minutes
- **Estimated Cost:** $0.05/day

**Function 3: verify-sources**
- **Trigger:** Cloud Scheduler (cron: `0 7 * * *`) OR Pub/Sub
- **Runtime:** Python 3.11
- **Memory:** 1GB (for LLM calls)
- **Timeout:** 60 minutes
- **Estimated Cost:** $0.30/day (LLM API calls included)

**Function 4: generate-articles**
- **Trigger:** Cloud Scheduler (cron: `0 8 * * *`) OR Pub/Sub
- **Runtime:** Python 3.11
- **Memory:** 1GB
- **Timeout:** 60 minutes
- **Estimated Cost:** $0.40/day (LLM API calls for article generation)

**Function 5: editorial-coordination**
- **Trigger:** Cloud Scheduler (cron: `0 9 * * *`)
- **Runtime:** Python 3.11
- **Memory:** 128MB
- **Timeout:** 5 minutes
- **Estimated Cost:** $0.01/day

**Function 6: revision-handler**
- **Trigger:** Cloud Firestore/Cloud SQL database trigger (status='draft')
- **Runtime:** Python 3.11
- **Memory:** 1GB
- **Timeout:** 30 minutes
- **Estimated Cost:** $0.20/day (on-demand, only when revisions needed)

**Function 7: auto-publish**
- **Trigger:** Cloud Scheduler (cron: `0 17 * * *`)
- **Runtime:** Python 3.11
- **Memory:** 128MB
- **Timeout:** 5 minutes
- **Estimated Cost:** $0.01/day

**Function 8: post-publication-monitor**
- **Trigger:** Cloud Scheduler (cron: `0 */6 * * *` - every 6 hours)
- **Runtime:** Python 3.11
- **Memory:** 256MB
- **Timeout:** 15 minutes
- **Estimated Cost:** $0.02/execution x 4/day = $0.08/day

**Total Daily Cloud Function Cost:** ~$1.15/day = $34.50/month

---

## 4. Automation vs. Human Oversight

### 4.1 What Should Be Automated

**Fully Automated (No Human in Loop):**
- Step 1: Event discovery (RSS aggregation, social monitoring)
- Step 2: Newsworthiness scoring (objective criteria)
- Step 3: Initial source identification (web research)
- Step 5: Structure selection (inverted pyramid default)
- Step 6: Article drafting (LLM generation)
- Step 7: Self-audit checklist (automated validation)
- Step 9: Social mention monitoring
- Step 10: Source reliability tracking

**Semi-Automated (Machine Proposes, Human Approves):**
- Step 4: Attribution planning (agent suggests hierarchy, editor approves)
- Step 8: Publication decision (agent drafts, editor approves/rejects/revises)
- Step 9: Correction decisions (agent flags, editor decides)

**Manual (Human Required):**
- Step 8: Final editorial judgment (publish, kill, escalate)
- Step 8: Legal risk assessment (libel, defamation review)
- Step 9: Correction writing (transparency and accuracy)
- Anonymous source justification (ethical decision)

### 4.2 Human Oversight Points (Quality Gates)

**Gate 1: Editorial Review (Step 8)**
- **Who:** Human editor (admin portal)
- **Frequency:** Every draft article
- **Decision:** Approve / Request Revision / Kill / Escalate
- **SLA:** 24 hours from draft generation
- **Fallback:** Articles not reviewed within 48 hours flagged for escalation

**Gate 2: Correction Approval (Step 9)**
- **Who:** Human editor
- **Frequency:** As flagged by Monitoring Agent
- **Decision:** Approve correction / Investigate further / Dismiss flag
- **SLA:** 12 hours for critical corrections

**Gate 3: Source Reliability Override (Step 10)**
- **Who:** Senior editor
- **Frequency:** Monthly review
- **Decision:** Override automated source scores if needed
- **Purpose:** Catch edge cases where algorithm misjudges source

### 4.3 Escalation Triggers

**Escalate to Senior Editor When:**
- Legal risk detected (keywords: lawsuit, defamation, libel)
- Anonymous source used without justification
- Conflicting sources with no clear resolution
- Article rejected twice by human editors (pattern issue)
- Source credibility score drops below threshold

---

## 5. Success Metrics & Quality Gates

### 5.1 Pipeline Health Metrics

**Daily Output Goals:**
- **Target:** 3-10 articles published daily
- **Minimum:** 1 national + 1 local + 1 other category
- **Quality Over Quantity:** Better 3 excellent articles than 10 mediocre

**Pipeline Efficiency:**
- **Event Discovery Rate:** 20-50 event candidates per day
- **Approval Rate:** 10-20% of discovered events advance (2-10 topics)
- **Generation Rate:** 80% of approved topics → published articles
- **Rejection Rate:** <20% of drafted articles killed by editors
- **Revision Rate:** <30% of articles require editor-requested revisions

**Quality Metrics:**
- **Source Compliance:** 100% of articles have ≥3 credible sources
- **Reading Level:** 95% within 7.5-8.5 Flesch-Kincaid
- **Attribution:** 100% of factual claims attributed
- **5W+H Coverage:** 100% answered in first 3-4 paragraphs
- **Correction Rate:** <5% of published articles require corrections

### 5.2 Quality Gates (Article Must Pass All)

**Gate 1: Newsworthiness (Evaluation Agent)**
- [ ] Total score ≥ 60 (out of 100)
- [ ] Worker relevance score ≥ 50 (out of 100)
- [ ] At least 3 potential sources identified

**Gate 2: Verification (Verification Agent)**
- [ ] ≥3 credible sources OR ≥2 academic citations
- [ ] Contentious claims independently corroborated
- [ ] Primary sources identified (not just aggregators)
- [ ] Source hierarchy plan created

**Gate 3: Article Quality (Journalist Agent Self-Audit)**
- [ ] Inverted pyramid structure used
- [ ] 5W+H answered in first 3-4 paragraphs
- [ ] Nut graf present (why it matters)
- [ ] All facts attributed
- [ ] Quotes add value (not filler)
- [ ] Reading level 7.5-8.5 Flesch-Kincaid
- [ ] "Why This Matters" section present
- [ ] "What You Can Do" section present
- [ ] Neutral tone (no loaded adjectives)
- [ ] Opinion separated from fact

**Gate 4: Bias Scan (Automated)**
- [ ] No LLM hallucinations detected
- [ ] No corporate propaganda detected
- [ ] No factual errors in verifiable claims
- [ ] No contradictions within article

**Gate 5: Human Editorial (Manual)**
- [ ] Editor verifies source credibility
- [ ] Editor confirms worker-centric perspective
- [ ] Editor approves legal safety (no libel/defamation)
- [ ] Editor confirms article doesn't pull punches
- [ ] Editor approves publication

### 5.3 Monitoring & Alerting

**Real-Time Alerts (Email/Slack):**
- Pipeline failure (any Cloud Function fails)
- Zero articles generated for 24 hours
- Article flagged for correction within 1 hour of publication
- Source credibility score drops below 2/5
- Editor review backlog exceeds 10 articles

**Daily Dashboard (Admin Portal):**
- Articles published today: [count]
- Articles pending review: [count]
- Event candidates discovered: [count]
- Topics approved: [count]
- Corrections needed: [count]
- Source reliability trends (chart)

**Weekly Report (Automated Email):**
- Total articles published (7-day)
- Category breakdown (chart)
- National vs. local split
- Average reading level
- Revision rate
- Correction rate
- Top sources used
- Pipeline bottlenecks

---

## 6. Cost Analysis & Constraints

### 6.1 Monthly Cost Breakdown (Estimated)

**Cloud Functions (Daily Automation):**
- Signal Intake: $0.10/day x 30 = $3.00
- Evaluation: $0.05/day x 30 = $1.50
- Verification: $0.30/day x 30 = $9.00
- Article Generation: $0.40/day x 30 = $12.00
- Editorial Coordination: $0.01/day x 30 = $0.30
- Revision Handler: $0.20/day x 30 = $6.00
- Auto-Publish: $0.01/day x 30 = $0.30
- Monitoring: $0.08/day x 30 = $2.40
- **Subtotal:** $34.50/month

**Cloud SQL (PostgreSQL):**
- db-f1-micro instance: $7.67/month (free tier eligible)
- Storage (10GB SSD): $1.70/month
- **Subtotal:** $9.37/month (or $0 if free tier)

**Cloud Storage (Images):**
- 5GB storage: $0.10/month
- Network egress: $0.50/month (via CDN)
- **Subtotal:** $0.60/month

**API Costs (External):**
- Twitter API v2: FREE (500K tweets/month limit)
- Reddit API: FREE (60 requests/min limit)
- RSS Feeds: FREE
- LLM API (Article Generation): **USER-PROVIDED** (Claude/ChatGPT/Gemini subscriptions)
- Google Gemini (Images): **USER-PROVIDED** (GCP API key)
- **Subtotal:** $0/month (all free or user-provided)

**Monitoring & Logging:**
- Cloud Logging: FREE (50GB/month limit)
- Cloud Monitoring: FREE (basic metrics)
- UptimeRobot: FREE tier (50 monitors)
- **Subtotal:** $0/month

**Email (Editorial Notifications):**
- SendGrid Free Tier: 100 emails/day = 3,000/month
- **Subtotal:** $0/month

**TOTAL ESTIMATED COST: $44.47/month**

### 6.2 Cost Optimization Strategies

**Stay Within $30-100/month Budget:**
1. **Use GCP Free Tier Aggressively:**
   - Cloud SQL db-f1-micro: $0/month (free tier)
   - Cloud Functions: 2M invocations/month free (we use ~240/month)
   - Cloud Storage: 5GB free

2. **Leverage User-Provided LLM Subscriptions:**
   - Article generation via user's Claude/ChatGPT/Gemini
   - Marginal cost = $0 (already paying for subscriptions)

3. **Batch Processing to Reduce Invocations:**
   - Signal Intake processes all feeds in one run (not per-feed)
   - Verification Agent handles multiple topics in parallel

4. **Cache Aggressively:**
   - RSS feed results cached for 6 hours (avoid redundant fetches)
   - Social media queries cached

5. **Start Small, Scale Up:**
   - Begin with 3-5 articles/day target
   - Only scale Cloud Functions if hitting limits

**If Budget Exceeded:**
- Reduce monitoring frequency (6 hours → 12 hours)
- Reduce event discovery scope (fewer social keywords)
- Use Cloud Run instead of Cloud Functions (cheaper for longer tasks)

---

## 7. Implementation Phases (Batch 6)

### 7.1 Batch Overview

**Batch 6: Automated Journalism Pipeline**
- **Dependencies:** Design redesign complete (Batch 5)
- **Parallel:** Phases 6.1-6.2 simultaneous, then 6.3-6.5 simultaneous, then 6.6-6.8 sequential
- **Purpose:** Implement end-to-end automated journalism process for daily article generation

### 7.2 Phase Definitions

**Phase 6.1: Database Schema Extensions**
- **Status:** ⚪ Not Started
- **Complexity:** S
- **Tasks:**
  - [ ] Create `event_candidates` table
  - [ ] Create `article_revisions` table
  - [ ] Create `corrections` table
  - [ ] Create `source_reliability_log` table
  - [ ] Add new columns to `articles` table (bias_scan_report, self_audit_passed, etc.)
  - [ ] Add new columns to `topics` table (verified_facts, source_plan, etc.)
  - [ ] Test schema migrations (SQLite local, PostgreSQL cloud)
- **Done When:** All new tables created, migrations tested

**Phase 6.2: Signal Intake Agent**
- **Status:** ⚪ Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Build RSS feed aggregator (feedparser library)
  - [ ] Integrate Twitter API v2 (trending topics, hashtag monitoring)
  - [ ] Integrate Reddit API (subreddit monitoring)
  - [ ] Build government feed scraper (data.gov, Labor Dept, NLRB)
  - [ ] Implement event candidate deduplication logic
  - [ ] Write event candidates to `event_candidates` table
  - [ ] Create Cloud Function deployment script
  - [ ] Test locally with real feeds
- **Done When:** Agent discovers 20-50 event candidates daily, writes to database

**Phase 6.3: Evaluation Agent**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1 (database schema)
- **Complexity:** M
- **Tasks:**
  - [ ] Implement newsworthiness scoring algorithm (6 dimensions)
  - [ ] Build worker-relevance scoring model (income bracket impact)
  - [ ] Configure thresholds (reject <30, hold 30-59, approve ≥60)
  - [ ] Query event_candidates, score, update status
  - [ ] Create topic records for approved events
  - [ ] Create Cloud Function deployment script
  - [ ] Test with sample event candidates
- **Done When:** Agent scores events, approves 10-20% for article generation

**Phase 6.4: Verification Agent**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1, Phase 6.3
- **Complexity:** M
- **Tasks:**
  - [ ] Build primary source identification logic (WebSearch integration)
  - [ ] Implement cross-reference verification (compare claims across sources)
  - [ ] Build fact classification engine (observed vs. claimed vs. interpreted)
  - [ ] Implement source hierarchy enforcement (named > org > docs > anon)
  - [ ] Store verified_facts and source_plan in topics table (JSON format)
  - [ ] Create Cloud Function deployment script
  - [ ] Test with approved topics
- **Done When:** Agent verifies ≥3 sources per topic, creates source plans

**Phase 6.5: Enhanced Journalist Agent**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1, Phase 6.4
- **Complexity:** M
- **Tasks:**
  - [ ] Enhance existing journalist agent with self-audit checklist
  - [ ] Implement bias detection scan (hallucination, propaganda checks)
  - [ ] Add reading level validation (Flesch-Kincaid scoring)
  - [ ] Integrate with verified_facts from topics table
  - [ ] Generate articles with proper attribution (source_plan)
  - [ ] Store bias_scan_report in articles table
  - [ ] Create Cloud Function deployment script
  - [ ] Test with verified topics
- **Done When:** Agent generates quality articles passing 10-point self-audit

**Phase 6.6: Editorial Workflow Integration**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.5
- **Complexity:** S
- **Tasks:**
  - [ ] Build Editorial Coordinator Agent (assign, notify, track)
  - [ ] Update admin portal with review interface (show bias scan, sources)
  - [ ] Implement revision request workflow (editorial_notes → Journalist Agent)
  - [ ] Add revision logging (article_revisions table)
  - [ ] Configure email notifications (SendGrid integration)
  - [ ] Test complete editorial loop (draft → review → revise → approve)
- **Done When:** Human editors can review, request revisions, approve articles via portal

**Phase 6.7: Publication & Monitoring**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.6
- **Complexity:** S
- **Tasks:**
  - [ ] Build auto-publish Cloud Function (approved → published)
  - [ ] Build Monitoring Agent (social mentions, corrections, source reliability)
  - [ ] Implement correction workflow (flag → editor review → publish correction)
  - [ ] Add correction notices to article display
  - [ ] Build source reliability scoring updates (source_reliability_log)
  - [ ] Test post-publication monitoring (Twitter/Reddit mention tracking)
- **Done When:** Published articles monitored, corrections tracked, source scores updated

**Phase 6.8: Daily Scheduling & Integration**
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
- **Complexity:** S
- **Tasks:**
  - [ ] Configure Cloud Scheduler (cron jobs for each agent)
  - [ ] Set up Pub/Sub messaging (agent-to-agent communication)
  - [ ] Configure environment variables (API keys, database URLs)
  - [ ] Deploy all Cloud Functions to GCP
  - [ ] Set up monitoring dashboard (Cloud Logging, admin portal)
  - [ ] Test end-to-end pipeline (6am discovery → 5pm publication)
  - [ ] Document operational procedures (troubleshooting, manual overrides)
- **Done When:** Full pipeline runs automatically daily, produces 3-10 articles

---

## 8. Risks & Mitigations

### 8.1 Technical Risks

**Risk 1: LLM API Rate Limits**
- **Probability:** Medium
- **Impact:** High (blocks article generation)
- **Mitigation:**
  - Use user's existing Claude/ChatGPT/Gemini subscriptions (higher limits)
  - Implement retry logic with exponential backoff
  - Queue articles for next run if limits hit
  - Alert editors when rate limits approached

**Risk 2: Cloud Function Timeouts**
- **Probability:** Medium
- **Impact:** Medium (pipeline delays)
- **Mitigation:**
  - Set generous timeouts (60 min for complex agents)
  - Implement checkpointing (resume from last state)
  - Use Cloud Run for long-running tasks (alternative to Functions)
  - Monitor execution times, optimize slow agents

**Risk 3: Source Verification Failures**
- **Probability:** High
- **Impact:** Critical (publish unverified claims)
- **Mitigation:**
  - **Human editorial review remains mandatory** (final quality gate)
  - Fail-safe: If <3 sources, reject topic (don't generate article)
  - Source credibility scoring (prioritize high-credibility sources)
  - Escalate to senior editor for ambiguous cases

**Risk 4: Database Connection Failures**
- **Probability:** Low
- **Impact:** High (pipeline halts)
- **Mitigation:**
  - Use Cloud SQL with automated backups
  - Implement connection pooling
  - Retry logic for transient failures
  - Alert on database errors immediately

### 8.2 Editorial Risks

**Risk 5: Bias in Automated Newsworthiness Scoring**
- **Probability:** Medium
- **Impact:** Medium (miss important stories)
- **Mitigation:**
  - Monthly review of rejected topics (senior editor spot-check)
  - Adjust scoring weights based on feedback
  - Manual topic submission workflow (editors can bypass scoring)
  - Track false negatives (important stories rejected)

**Risk 6: Hallucinations in Generated Articles**
- **Probability:** Medium
- **Impact:** Critical (publish false information)
- **Mitigation:**
  - **Human editorial review mandatory** (catches hallucinations)
  - Automated bias scan detects common patterns
  - Require explicit source attribution (harder to hallucinate with attribution)
  - Post-publication monitoring (corrections if needed)

**Risk 7: Worker-Centric Perspective Lost**
- **Probability:** Low
- **Impact:** High (defeats mission)
- **Mitigation:**
  - "Why This Matters" section required (forces worker impact analysis)
  - Journalist agent prompt emphasizes materialist perspective
  - Human editors trained on worker-centric framing
  - Monthly editorial review of published articles (perspective audit)

### 8.3 Operational Risks

**Risk 8: Editor Review Bottleneck**
- **Probability:** High
- **Impact:** Medium (delays publication)
- **Mitigation:**
  - Start with 3-5 articles/day (manageable review workload)
  - Scale generation only when review capacity increases
  - 24-hour review SLA (reasonable for editors)
  - Auto-escalate if backlog exceeds 10 articles

**Risk 9: Cost Overruns**
- **Probability:** Low
- **Impact:** Medium (budget constraints)
- **Mitigation:**
  - GCP billing alerts at $25, $50, $75 thresholds
  - Monthly cost review (actual vs. estimated)
  - Reduce automation scope if costs exceed $100/month
  - User-provided LLM subscriptions eliminate largest cost

**Risk 10: Legal Liability (Defamation, Libel)**
- **Probability:** Low
- **Impact:** Critical (lawsuits)
- **Mitigation:**
  - **Human editorial review mandatory** (legal judgment)
  - Escalate any article with legal keywords (lawsuit, defamation, libel)
  - Require ≥3 credible sources for contentious claims
  - Clear attribution (protects against libel)
  - Legal disclaimer on About page

---

## 9. Integration with Existing Roadmap

### 9.1 Batch Sequencing

**Current Roadmap:**
- ✅ **Batch 1-4:** Local MVP development (COMPLETE)
- **Batch 5:** Design Redesign (IN PROGRESS)
- **→ Batch 6:** Automated Journalism Pipeline (THIS PLAN)
- **Batch 7:** GCP Infrastructure & Deployment
- **Batch 8:** Cloud Operations Setup
- **Batch 9:** Production Testing & Launch

**Rationale for Batch 6 Placement:**
- **After Batch 5 (Design):** Visual-first storytelling design complete before automated content generation
- **Before Batch 7 (GCP Deployment):** Build pipeline locally, test thoroughly before cloud costs
- **Parallel to Batch 7 (Partial):** Some agents can be tested locally while infrastructure deploys

### 9.2 Dependencies

**Batch 6 Depends On:**
- ✅ Batch 1-4: Local MVP functional (database, backend, frontend)
- Batch 5: Design improvements (better article presentation)

**Batches That Depend On Batch 6:**
- Batch 7: GCP deployment (needs Cloud Functions defined)
- Batch 8: CI/CD pipeline (needs agent code to deploy)
- Batch 9: Production testing (needs full pipeline)

### 9.3 Parallel Work Opportunities

**Can Work in Parallel:**
- Phase 6.1 (Database schema) + Phase 6.2 (Signal Intake Agent)
- Phase 6.3 (Evaluation) + Phase 6.4 (Verification) + Phase 6.5 (Journalist enhancement)
- Batch 6 development (local) + Batch 7 GCP setup (cloud)

**Cannot Parallelize:**
- Phase 6.6 (Editorial workflow) requires 6.5 complete
- Phase 6.7 (Monitoring) requires 6.6 complete
- Phase 6.8 (Scheduling) requires all prior phases complete

---

## 10. Key Decisions & Open Questions

### 10.1 Decisions Made

1. **Semi-Automated Model:** Machines discover and draft, humans verify and approve
2. **Daily Cadence:** Cloud Scheduler triggers pipeline at 6am daily
3. **Human Editorial Gate Mandatory:** No article published without human approval
4. **Cost Target:** $30-100/month (achievable with GCP free tier + user LLM subscriptions)
5. **Start Small:** 3-5 articles/day initially, scale based on editor capacity
6. **Agent-to-Agent Communication:** Pub/Sub messaging (GCP native)
7. **Local Development First:** Build and test all agents locally before cloud deployment
8. **User-Provided LLMs:** Leverage existing Claude/ChatGPT/Gemini subscriptions

### 10.2 Open Questions for User

**Q1: Human Editor Availability**
- How many hours per day can editors dedicate to article review?
- Expected review time per article (estimate: 10-15 minutes)?
- **Decision needed:** Determines daily article generation target

**Q2: Beat Priorities**
- Which categories should be prioritized for automated discovery?
- Should we start with national-only, then add local later?
- **Decision needed:** Affects Signal Intake Agent scope

**Q3: Source Credibility Thresholds**
- Current requirements: ≥3 credible sources OR ≥2 academic citations
- Should we raise/lower thresholds for different categories (e.g., higher for investigative)?
- **Decision needed:** Affects Verification Agent logic

**Q4: Revision Loop Limits**
- Maximum revisions before article is killed (suggest: 2)?
- Auto-escalate after N rejections (suggest: 2)?
- **Decision needed:** Prevents infinite revision loops

**Q5: Monitoring Scope**
- Should Monitoring Agent track all social platforms or just Twitter/Reddit?
- Expand to Facebook, Instagram later?
- **Decision needed:** Affects API costs and complexity

**Q6: Local vs. National Priority**
- Start with national-only to simplify (fewer sources)?
- Or implement local from day 1 (more complex but full feature)?
- **Decision needed:** Affects Phase 6.2 (Signal Intake) scope

### 10.3 Recommendations

**Recommendation 1: Start with National-Only**
- **Rationale:** Simplifies signal intake (fewer sources), easier to verify (credible national sources)
- **Timeline:** Add local content after 2-4 weeks of stable national pipeline
- **Benefit:** Faster MVP, lower risk

**Recommendation 2: Manual Social Posting (MVP)**
- **Rationale:** Auto-posting deferred to Post-MVP (per requirements)
- **Agent Role:** Generate social sharing copy, store in database, editors post manually
- **Benefit:** Zero API costs, editorial control over social messaging

**Recommendation 3: Phase 6.8 as Batch 7 Integration**
- **Rationale:** Cloud Scheduler setup overlaps with GCP deployment (Batch 7)
- **Proposal:** Move Phase 6.8 to Batch 7, keep Batch 6 focused on agent development
- **Benefit:** Cleaner separation (local dev vs. cloud deployment)

---

## 11. Next Steps

### 11.1 Immediate Actions

1. **User Review & Approval:**
   - Review this analysis document
   - Answer open questions (Section 10.2)
   - Approve/modify recommendations (Section 10.3)

2. **Finalize Batch 6 Roadmap:**
   - Update `/Users/home/sandbox/daily_worker/projects/DWnews/plans/roadmap.md`
   - Add Batch 6 phases (6.1-6.8)
   - Set dependencies and parallel work streams

3. **Create Agent Definitions:**
   - Write `/Users/home/sandbox/daily_worker/.claude/agents/signal-intake.md`
   - Write `/Users/home/sandbox/daily_worker/.claude/agents/evaluation.md`
   - Write `/Users/home/sandbox/daily_worker/.claude/agents/verification.md`
   - Update `/Users/home/sandbox/daily_worker/.claude/agents/journalist.md` (enhancements)
   - Write `/Users/home/sandbox/daily_worker/.claude/agents/monitoring.md`

4. **Begin Phase 6.1 (Database Schema):**
   - Implement new tables (event_candidates, article_revisions, corrections, source_reliability_log)
   - Test migrations locally (SQLite)

### 11.2 Project Manager Coordination

**Agent Chat System Usage:**
- Use `#roadmap` channel for Batch 6 planning updates
- Use `#coordination` channel for phase assignments (which agent works on what)
- Use `#errors` channel for blocker reporting

**Example Messages:**
```
set_handle({ handle: "project-manager" })

publish_message({
  channel: "roadmap",
  message: "Batch 6 (Automated Journalism Pipeline) planned with 8 phases. Ready for user approval. See plans/automated-journalism-analysis.md"
})
```

### 11.3 Success Criteria for Batch 6

**Batch 6 Complete When:**
- [ ] All 8 phases complete
- [ ] Full pipeline runs locally (signal intake → publication)
- [ ] 3-5 quality articles generated daily in test environment
- [ ] Human editorial workflow functional (review → approve → publish)
- [ ] All quality gates pass (newsworthiness, verification, bias scan, editorial)
- [ ] Post-publication monitoring operational (corrections, source reliability)
- [ ] Documentation complete (agent definitions, operational procedures)
- [ ] Ready for cloud deployment (Batch 7)

**Timeline Estimate (Complexity-Based):**
- 8 phases: 2 Small (S), 6 Medium (M)
- Parallel work possible (up to 3 agents simultaneously)
- Estimated: 4-6 weeks of agent work (no calendar deadlines)

---

## 12. Conclusion

The **Agentic Journalist Process** provides a rigorous, professional framework for automated news generation. Implementation requires:

1. **6 New Specialized Agents** (Signal Intake, Evaluation, Verification, Enhanced Journalist, Editorial Coordinator, Monitoring)
2. **Database Schema Extensions** (4 new tables, column additions to existing tables)
3. **Daily Scheduling Infrastructure** (Cloud Scheduler, Cloud Functions, Pub/Sub messaging)
4. **Human Editorial Gates** (mandatory review before publication, correction approval)
5. **Cost-Conscious Design** (GCP free tier, user-provided LLMs, ~$45/month total)

**Key Success Factor:** Balance automation (efficiency) with human oversight (quality, legal safety, editorial judgment). The semi-automated model leverages AI for discovery, research, and drafting while preserving human judgment for publication decisions.

**Next Action:** User reviews this analysis, answers open questions, approves Batch 6 roadmap phases.

---

**Document Prepared By:** Project Manager Agent
**Analysis Framework:** 10-Step Agentic Journalist Process
**Integration:** Daily Worker requirements.md, journalism-standards.md, current infrastructure
**Status:** Awaiting user approval to proceed with Batch 6 implementation

---

**End of Analysis Document**
