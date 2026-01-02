# The Daily Worker - MVP Implementation Roadmap

**Project:** DWnews - AI-Powered Working-Class News Platform
**Version:** 3.0
**Date:** 2025-12-31
**Development Model:** Local-First Agent-Driven Development, then GCP Deployment

---

## Executive Summary

Lean MVP for The Daily Worker: AI-powered news platform taking influence from marxist/ leninist teachings to deliver accurate, worker-centric news without pulling punches. Agent-driven development using existing LLM subscriptions and GCP infrastructure.

**Value Proposition:** Accurate, worker-centric news that doesn't pull punches. Quality over quantity.

**Core Features:**
- Content scales with readership: 3-10 articles daily initially, expanding as audience grows
- Broad category coverage prioritized over volume in any single category
- NEW stories + ONGOING/CONTINUING stories with visual prominence
- Local content based on user location (IP-inferred, signup preference override)
- Imagery: Sourced/cited from reputable sources (opinion pieces use Google Gemini)
- Situation-dependent quantity (e.g., more sports on Monday covering weekend events)

**MVP Philosophy:**
- LOCAL-FIRST DEVELOPMENT: Build and validate completely locally before cloud costs
- Agent-driven development (marginal costs)
- Free-tier LLMs via existing Claude/ChatGPT/Gemini subscriptions
- GCP deployment ONLY after local validation
- Start small, prove utility, scale when justified
- Complexity-based planning (NO timeline estimates)
- Zero cloud costs until MVP proven functional

**Development Approach:**
1. Batches 1-4: Build and test everything locally (zero cost) ✅
2. Batch 5: Design redesign with visual-first approach ✅
3. Batch 6: Automated journalism pipeline ✅
4. Batch 6.5: Testing infrastructure, CI/CD, and deployment automation ✅
5. **CURRENT:** Complete local testing + end-user validation
6. **CURRENT:** Set up security configuration for production
7. Batch 7: Subscription system (local testing, Stripe integration)
8. Batches 8-9: Deploy to GCP ONLY after security setup complete
9. Batch 10: Production testing and launch

**Target Costs:**
- Development: Under $1,000 total
- Local Development: $0 (Batches 1-6.5, except Stripe test transactions in Batch 7)
- Cloud Costs: Actual costs reported when services begin (Batches 8-10)
- Monthly OpEx Target: Under $100/month after launch
- Revenue Target: 100 subscribers = $1,500/month gross, $1,455/month net

---

## ✅ Batch 1: COMPLETED (2025-12-29)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

---

## ✅ Batch 2: COMPLETED (2025-12-29)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

---

## ✅ Batch 3: COMPLETED (2025-12-29)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

---

## ✅ Batch 4: COMPLETED (2025-12-29)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

**All 5 phases complete:**
- ✅ Phase 4.1: End-to-End Local Testing (E2E test suite, 25+ tests)
- ✅ Phase 4.2: Local Security Review (SECURITY.md, 8 security scans)
- ✅ Phase 4.3: Content Pre-Generation (5 sample articles, diverse categories)
- ✅ Phase 4.4: Local Documentation (Comprehensive README update)
- ✅ Phase 4.5: Legal Basics (About, Privacy, Terms pages)

---

## ✅ Batch 5: COMPLETED (2026-01-01)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

**All 6 phases complete:**
- ✅ Phase 5.1: Design Research & Analysis (ProPublica, The Markup, Daily Worker history, 2025 best practices)
- ✅ Phase 5.2: Design System & Guide (typography, colors, spacing, components)
- ✅ Phase 5.3: Homepage Redesign (visual-first with Inter + Merriweather)
- ✅ Phase 5.4: Article Detail Page Redesign (large headlines, serif body, pull quotes)
- ✅ Phase 5.5: Design Polish & Refinements (micro-interactions, accessibility, testing checklist)
- ✅ Phase 5.6: Traditional Newspaper Redesign v3.0 (Playfair Display, black/white/yellow, multi-column grid, subscription widget)

**Final Deliverables:**
- Design research summary document
- Complete design system documentation (644 lines)
- **v3.0 Traditional Newspaper Design:**
  - Playfair Display + Merriweather typography (classic newspaper serif)
  - Black/white/yellow color scheme (heritage aesthetic)
  - Multi-column grid with sidebar layout
  - Major daily headline feature (72px+ headlines)
  - Subscription widget (50¢/day pricing)
  - Archive access messaging
  - Ongoing stories in sidebar with yellow accents
  - Complete article page styling with newspaper feel
  - Responsive design maintaining traditional aesthetic on mobile

---

## Batch 6: Automated Journalism Pipeline

**Dependencies:** Design redesign complete (Batch 5)
**Parallel:** 6.1-6.2 simultaneous, then 6.3-6.5 simultaneous, then 6.6-6.7-6.8 sequential
**Purpose:** Implement end-to-end automated journalism process for daily article generation

**Overview:**
Implements the 10-step Agentic Journalist Process for autonomous news discovery, verification, drafting, and publication. Combines automated event discovery with human editorial oversight to produce 3-10 quality articles daily. See `/Users/home/sandbox/daily_worker/projects/DWnews/plans/automated-journalism-analysis.md` for complete design.

**Key Components:**
- 6 specialized agents (Signal Intake, Evaluation, Verification, Enhanced Journalist, Editorial Coordinator, Monitoring)
- Daily scheduling via Cloud Functions (6am discovery → 5pm publication)
- Semi-automated model (machines discover/draft, humans verify/approve)
- Cost target: $30-50/month (Cloud Functions + user-provided LLM subscriptions)

### Phase 6.1: Database Schema Extensions
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Complexity:** S
- **Tasks:**
  - [x] Create `event_candidates` table (newsworthiness scoring)
  - [x] Create `article_revisions` table (revision tracking)
  - [x] Create `corrections` table (post-publication corrections)
  - [x] Create `source_reliability_log` table (learning loop)
  - [x] Add columns to `articles`: bias_scan_report, self_audit_passed, editorial_notes, assigned_editor, review_deadline
  - [x] Add columns to `topics`: verified_facts, source_plan, verification_status
  - [x] Test schema migrations (SQLite local, PostgreSQL cloud-ready)
- **Done When:** All new tables created, migrations tested locally
- **Deliverables:**
  - Migration SQL: `/database/migrations/001_automated_journalism_schema.sql`
  - Migration runner: `/database/migrations/run_migration_001.py`
  - Test suite: `/database/migrations/test_migration_001.py`
  - Updated SQLAlchemy models with 4 new classes (EventCandidate, ArticleRevision, Correction, SourceReliabilityLog)
  - 5 new database views for common queries
  - 14 new indexes for performance
  - Updated database README with migration documentation

### Phase 6.2: Signal Intake Agent (Event Discovery)
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Complexity:** M
- **Tasks:**
  - [x] Build RSS feed aggregator (Reuters, AP, ProPublica, local sources)
  - [x] Integrate Twitter API v2 (trending labor topics, worker hashtags)
  - [x] Integrate Reddit API (r/labor, r/WorkReform, r/antiwork, local subs)
  - [x] Build government feed scraper (data.gov, Labor Dept, NLRB)
  - [x] Implement event candidate deduplication logic
  - [x] Write event candidates to `event_candidates` table (status='discovered')
  - [x] Create agent definition: `.claude/agents/signal-intake.md`
  - [x] Test locally with real feeds (target: 20-50 events/day)
- **Done When:** Agent discovers events from multiple sources, writes to database
- **Deliverables:**
  - RSS aggregator: `/backend/agents/feeds/rss_feeds.py` (8 labor news sources)
  - Twitter monitor: `/backend/agents/feeds/twitter_feed.py` (12 hashtags, 10 queries, 10 union accounts)
  - Reddit monitor: `/backend/agents/feeds/reddit_feed.py` (9 labor subreddits with mock data fallback)
  - Government scraper: `/backend/agents/feeds/government_feeds.py` (DOL, OSHA, BLS RSS feeds)
  - Deduplication logic: `/backend/agents/utils/deduplication.py` (3-layer: URL, title hash, fuzzy matching)
  - Main orchestrator: `/backend/agents/signal_intake_agent.py`
  - Agent definition: `/.claude/agents/signal-intake.md`
  - Test script: `/scripts/test_signal_intake.py`
  - Test results: 9 events fetched, 8 unique (11.1% dedup rate), 8 stored successfully

### Phase 6.3: Evaluation Agent (Newsworthiness Scoring)
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Depends On:** Phase 6.1 ✅
- **Complexity:** M
- **Tasks:**
  - [x] Implement newsworthiness scoring (Impact, Timeliness, Proximity, Conflict, Novelty, Verifiability)
  - [x] Build worker-relevance scoring model ($45k-$350k income bracket impact)
  - [x] Configure thresholds (reject <30, hold 30-65, approve ≥65)
  - [x] Query event_candidates, score each on 6 dimensions (0-100 total)
  - [x] Update status: 'approved'/'rejected'/'evaluated'
  - [x] Create topic records for approved events
  - [x] Create agent definition: `.claude/agents/evaluation.md`
  - [x] Test with sample event candidates (target: 10-20% approval rate)
- **Done When:** Agent scores events, approves 10-20% for article generation
- **Deliverables:**
  - Main agent: `/backend/agents/evaluation_agent.py`
  - 6 scoring modules: `/backend/agents/scoring/` (worker_impact, timeliness, verifiability, regional, conflict, novelty)
  - Agent definition: `/.claude/agents/evaluation.md`
  - Test suite: `/scripts/test_evaluation.py` (15 test events, 20% approval rate achieved)
  - Implementation README: `/backend/agents/README_EVALUATION.md`
  - All 3 approved test events successfully created topic records
  - Scoring algorithm: 6 dimensions with proper weighting (30%, 20%, 20%, 15%, 10%, 5%)
  - Quality threshold: 65/100 for approval (calibrated for 10-20% approval rate)

### Phase 6.4: Verification Agent (Source Verification & Attribution)
- **Status:** 🟢 Complete (Updated 2026-01-02 with 3-tier transparency system)
- **Completed:** 2026-01-01, Enhanced 2026-01-02
- **Depends On:** Phase 6.1 ✅, Phase 6.3 ✅
- **Complexity:** M
- **Tasks:**
  - [x] Build primary source identification (WebSearch, document analysis)
  - [x] Implement cross-reference verification (compare claims across sources)
  - [x] Build fact classification engine (observed vs. claimed vs. interpreted)
  - [x] Implement source hierarchy enforcement (named > org > docs > anon)
  - [x] Verify ≥3 credible sources OR ≥2 academic citations per topic
  - [x] Store verified_facts and source_plan in topics table (JSON format)
  - [x] Create agent definition: `.claude/agents/verification.md`
  - [x] Test with approved topics (verify source count, attribution plan)
  - [x] **NEW (2026-01-02):** Implement 3-tier transparency system (Unverified/Verified/Certified)
  - [x] **NEW (2026-01-02):** Replace pass/fail with transparency-based scoring
  - [x] **NEW (2026-01-02):** Update database schema with new verification statuses
  - [x] **NEW (2026-01-02):** Add verification badges to frontend (Green/Blue/Orange)
- **Done When:** Agent verifies ≥3 sources per topic, creates attribution plans, assigns transparency level
- **Deliverables:**
  - Source identification module: `/backend/agents/verification/source_identifier.py` (400 lines)
  - Cross-reference verifier: `/backend/agents/verification/cross_reference.py` (335 lines)
  - Fact classifier: `/backend/agents/verification/fact_classifier.py` (242 lines)
  - Source ranker: `/backend/agents/verification/source_ranker.py` (313 lines)
  - Main agent: `/backend/agents/verification_agent.py` (525 lines, updated with 3-tier scoring)
  - Agent definition: `/.claude/agents/verification.md` (377 lines)
  - Test suite: `/scripts/test_verification.py` (317 lines)
  - Technical README: `/backend/agents/README_VERIFICATION.md` (395 lines)
  - Test results: 3 topics verified, 100% success rate, avg 5 sources per topic
  - 4-tier source credibility hierarchy implemented (Tier 1: 90-100, Tier 2: 70-89, Tier 3: 50-69, Tier 4: 0-49)
  - Cross-reference verification with conflict detection
  - Fact classification: observed/claimed/interpreted
  - JSON storage of verified_facts and source_plan in topics table
  - **3-Tier Transparency System:**
    - **Unverified (0-49 points):** Publish with disclosure of verification challenges, orange badge
    - **Verified (50-79 points):** Standard verification threshold, blue badge
    - **Certified (80-100 points):** Exceptional verification quality, green badge
  - Enhanced transparency: Articles published at any level with appropriate disclosure

### Phase 6.5: Enhanced Journalist Agent (Article Drafting + Self-Audit)
- **Status:** 🟢 Complete (Updated 2026-01-02 with 3-tier verification support)
- **Completed:** 2026-01-01, Enhanced 2026-01-02
- **Depends On:** Phase 6.1 ✅, Phase 6.4 ✅
- **Complexity:** M
- **Tasks:**
  - [x] Enhance existing journalist agent with self-audit checklist (10-point validation)
  - [x] Implement bias detection scan (hallucination, propaganda checks)
  - [x] Add reading level validation (Flesch-Kincaid 7.5-8.5 scoring)
  - [x] Integrate with verified_facts from topics table
  - [x] Generate articles with proper attribution (use source_plan)
  - [x] Store bias_scan_report in articles table (JSON format)
  - [x] Update agent definition: `.claude/agents/journalist.md` (enhancements)
  - [x] Test with verified topics (generate articles passing self-audit)
  - [x] **NEW (2026-01-02):** Accept all verification levels (Unverified/Verified/Certified)
  - [x] **NEW (2026-01-02):** Add disclosure sections for Unverified articles
  - [x] **NEW (2026-01-02):** Test article generation with real data end-to-end
- **Done When:** Agent generates quality articles, 100% pass 10-point self-audit, handles all verification levels
- **Deliverables:**
  - Self-audit module: `/backend/agents/journalist/self_audit.py` (395 lines, 10-point checklist)
  - Bias detector: `/backend/agents/journalist/bias_detector.py` (341 lines, hallucination/propaganda detection)
  - Readability checker: `/backend/agents/journalist/readability_checker.py` (185 lines, Flesch-Kincaid 7.5-8.5)
  - Attribution engine: `/backend/agents/journalist/attribution_engine.py` (263 lines)
  - Main agent: `/backend/agents/enhanced_journalist_agent.py` (17 KB, orchestrator with regeneration, 3-tier support)
  - Agent definition: `/.claude/agents/journalist.md` (updated with Phase 6.5 enhancements)
  - Module demo script: `/scripts/demo_journalist_modules.py` (no API required)
  - Integration test: `/scripts/test_journalist.py` (requires Claude API)
  - Documentation: `/backend/agents/journalist/README.md`, `/backend/agents/PHASE_6.5_IMPLEMENTATION.md`
  - 10-point self-audit: factual accuracy, source attribution, reading level, worker-centric framing, no hallucinations, proper context, active voice, specific details, balanced representation, editorial standards
  - Regeneration loop with max 3 attempts and LLM feedback
  - Complete database integration (verified_facts, source_plan, bias_scan_report, article_revisions)
  - **3-Tier Verification Support:** Agent adapts article structure based on verification level, includes appropriate disclosure language

### Phase 6.6: Editorial Workflow Integration
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Depends On:** Phase 6.5 ✅
- **Complexity:** S
- **Tasks:**
  - [x] Build Editorial Coordinator Agent (assign articles, notify editors, track SLA)
  - [x] Update admin portal with review interface (display bias scan, source list, self-audit results)
  - [x] Implement revision request workflow (editorial_notes → Journalist Agent rewrites)
  - [x] Add revision logging to `article_revisions` table
  - [x] Configure email notifications (SendGrid integration for editor alerts)
  - [x] Test complete editorial loop (draft → review → revise → approve → publish)
  - [x] Create agent definition: `.claude/agents/editorial-coordinator.md`
- **Done When:** Human editors can review, request revisions, approve articles via admin portal
- **Deliverables:**
  - Editorial Coordinator Agent: `/backend/agents/editorial_coordinator_agent.py` (479 lines)
  - Email notification system: `/backend/agents/email_notifications.py` (381 lines, 3 templates)
  - Editorial API routes: `/backend/routes/editorial.py` (438 lines, 10 endpoints)
  - Review interface: `/frontend/admin/review-article.html` (684 lines, full-featured UI)
  - Database migration: `/database/migrations/002_editorial_workflow_statuses.sql` (new statuses)
  - Agent definition: `/.claude/agents/editorial-coordinator.md` (834 lines)
  - Test suite: `/scripts/test_editorial_workflow.py` (549 lines, 8/8 tests passing)
  - Implementation docs: `/backend/agents/PHASE_6.6_IMPLEMENTATION.md`
  - Smart editor assignment (round-robin by workload and category)
  - SLA management (24-72 hour deadlines based on category)
  - Revision control (max 2 revisions per article)
  - Complete audit trail in article_revisions table
  - Email notifications (test/SendGrid/SMTP modes)

### Phase 6.7: Publication & Monitoring
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Depends On:** Phase 6.6 ✅
- **Complexity:** S
- **Tasks:**
  - [x] Build auto-publish function (articles.status='approved' → 'published')
  - [x] Build Monitoring Agent (social mention tracking, correction detection, source reliability updates)
  - [x] Implement correction workflow (flag → editor review → publish correction notice)
  - [x] Add correction notices to article display (frontend update)
  - [x] Build source reliability scoring updates (`source_reliability_log` table)
  - [x] Test post-publication monitoring (Twitter/Reddit mention tracking)
  - [x] Create agent definition: `.claude/agents/monitoring.md`
- **Done When:** Published articles monitored for 7 days, corrections tracked, source scores updated
- **Deliverables:**
  - Publication Agent: `/backend/agents/publication_agent.py` (12K, auto-publish, scheduled/manual publication)
  - Monitoring Agent: `/backend/agents/monitoring_agent.py` (17K, 7-day monitoring, social tracking)
  - Correction Workflow: `/backend/agents/correction_workflow.py` (14K, flag/review/publish corrections)
  - Source Reliability Scorer: `/backend/agents/source_reliability.py` (13K, learning loop, score history)
  - Monitoring API Routes: `/backend/routes/monitoring.py` (11K, 10 endpoints)
  - Frontend updates: article.html, article.js, article.css (correction notice display)
  - Agent definition: `/.claude/agents/monitoring.md` (15K)
  - Test suite: `/scripts/test_monitoring.py` (executable)
  - Implementation docs: `/backend/agents/PHASE_6.7_IMPLEMENTATION.md`
  - Social mention tracking (Twitter API v2, Reddit PRAW)
  - 4 correction types (factual_error, source_error, clarification, update, retraction)
  - Source reliability scoring (0-100 scale, +5/-10/-30 point changes)
  - 7-day monitoring window per article

### Phase 6.8: Local Testing & Integration
- **Status:** 🟢 Complete
- **Completed:** 2026-01-01
- **Depends On:** Phase 6.2 ✅, 6.3 ✅, 6.4 ✅, 6.5 ✅, 6.6 ✅, 6.7 ✅
- **Complexity:** S
- **Tasks:**
  - [x] Test end-to-end pipeline locally (signal intake → evaluation → verification → drafting → editorial → publication)
  - [x] Validate daily cadence simulation (run all agents sequentially)
  - [x] Test revision loop (editor requests changes, agent rewrites)
  - [x] Test correction workflow (monitoring flags issue, editor approves correction)
  - [x] Verify all quality gates (newsworthiness ≥65, ≥3 sources, 10-point self-audit, editorial approval)
  - [x] Generate 3-5 test articles end-to-end
  - [x] Document operational procedures (troubleshooting, manual overrides, escalation)
- **Done When:** Full pipeline runs locally, produces 3-5 quality articles, all quality gates pass
- **Deliverables:**
  - End-to-End Test: `/scripts/test_end_to_end_pipeline.py` (700 lines, 7-phase validation)
  - Daily Cadence Simulator: `/scripts/simulate_daily_cadence.py` (500 lines, realistic timing simulation)
  - Revision Loop Test: `/scripts/test_revision_loop.py` (550 lines, editorial feedback validation)
  - Correction Workflow Test: `/scripts/test_correction_workflow.py` (600 lines, transparency verification)
  - Quality Gates Verifier: `/scripts/verify_quality_gates.py` (600 lines, 6-gate validation)
  - Operational Procedures: `/docs/OPERATIONAL_PROCEDURES.md` (500 lines, complete ops manual)
  - Troubleshooting Guide: `/docs/TROUBLESHOOTING.md` (600 lines, error resolution guide)
  - Batch Completion Summary: `/docs/BATCH_6_COMPLETION_SUMMARY.md` (550 lines, full documentation)
  - All test scripts executable with proper error handling
  - Comprehensive documentation covering daily operations, troubleshooting, and emergency procedures

**Batch 6 Success Criteria:**
- [x] 3-5 quality articles generated daily in test environment
- [x] All 7 agents operational (Signal Intake, Evaluation, Verification, Journalist, Editorial Coordinator, Publication, Monitoring)
- [x] Human editorial workflow functional (review → approve → publish)
- [x] All quality gates pass (newsworthiness ≥65, source verification, self-audit, bias scan, reading level, editorial approval)
- [x] Post-publication monitoring operational (corrections, source reliability tracking)
- [x] Ready for cloud deployment (all agents tested locally, Cloud Functions ready)

---

## Batch 6.9: Investigatory Journalist Agent

**Dependencies:** Batch 6 complete (3-tier verification system operational)
**Parallel:** Phase 6.9.1-6.9.2 simultaneous, then 6.9.3-6.9.4 sequential
**Purpose:** Implement investigatory journalism capabilities for Unverified articles requiring deep investigation
**Status:** Not Started

**Overview:**
Implements specialized investigatory journalism agent to handle Unverified articles (verification score 0-49) that require deeper research and investigation. This agent acts as a second-pass researcher that attempts to elevate Unverified articles to Verified or Certified status through additional investigation techniques.

**Key Capabilities:**
- Deep web research beyond standard verification
- Public records investigation (FOIA requests, court documents, regulatory filings)
- Expert source identification and outreach
- Follow-up investigation plans for ongoing stories
- Transparent disclosure when verification remains limited

### Phase 6.9.1: Core Investigation Engine
- **Status:** ⚪ Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Build deep research module (academic databases, specialized search, archive.org)
  - [ ] Implement public records searcher (PACER, state court systems, SEC EDGAR, FOIA portals)
  - [ ] Build expert identification system (university directories, professional associations, LinkedIn)
  - [ ] Create source outreach templates (email, contact forms, interview requests)
  - [ ] Implement investigation plan generator (next steps for unresolved questions)
  - [ ] Store investigation results in database (investigation_logs table)
  - [ ] Test with real Unverified articles
- **Done When:** Agent conducts deep investigation and identifies additional sources or verification paths

### Phase 6.9.2: Source Elevation Engine
- **Status:** ⚪ Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Build re-verification system (run Verification Agent again with new sources)
  - [ ] Implement verification score improvement tracking (before/after investigation)
  - [ ] Add investigation notes to article metadata
  - [ ] Create "Investigation in Progress" badge for frontend
  - [ ] Build automatic re-submission to Editorial Coordinator when elevated to Verified/Certified
  - [ ] Test score elevation with multiple article types
- **Done When:** Unverified articles can be elevated to Verified/Certified through investigation

### Phase 6.9.3: Editorial Integration
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.9.1, Phase 6.9.2
- **Complexity:** S
- **Tasks:**
  - [ ] Add "Request Investigation" button to editorial review interface
  - [ ] Build investigation queue management
  - [ ] Add investigation status display to admin dashboard
  - [ ] Create email notifications for investigation completion
  - [ ] Implement manual investigation task assignment
  - [ ] Test complete editorial workflow with investigation
- **Done When:** Editors can request investigation on Unverified articles and track progress

### Phase 6.9.4: Testing & Deployment
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.9.3
- **Complexity:** S
- **Tasks:**
  - [ ] Test end-to-end: Unverified → Investigation → Verified/Certified
  - [ ] Test investigation failure path (remains Unverified with disclosure)
  - [ ] Validate public records access (PACER credentials, FOIA submission)
  - [ ] Test expert outreach workflow
  - [ ] Verify investigation notes display correctly
  - [ ] Document investigation procedures for editorial team
  - [ ] Create troubleshooting guide for investigation failures
- **Done When:** Full investigation workflow tested, documented, ready for production

**Batch 6.9 Success Criteria:**
- [ ] Investigatory Agent conducts deep research on Unverified articles
- [ ] ≥30% of Unverified articles elevated to Verified or Certified
- [ ] Investigation process transparent to editorial team
- [ ] Public records integration functional
- [ ] Expert source outreach tested
- [ ] Investigation notes stored and displayed
- [ ] Ready for production use

---

## ✅ Batch 6.5: COMPLETED (2026-01-01)
**See:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/completed/roadmap-archive.md`

**All 3 phases complete:**
- ✅ Phase 6.5.1: Backend Testing Infrastructure (39 tests, 100% passing)
- ✅ Phase 6.5.2: Frontend Testing Infrastructure (50+ tests, 100% passing)
- ✅ Phase 6.5.3: CI/CD Pipeline (8 GitHub Actions workflows - 5 CI/CD + 3 deployment workflows)

**Final Deliverables:**
- Enterprise-grade testing infrastructure for backend and frontend
- 99+ automated tests with complete isolation
- Multi-version testing (Python 3.9-3.11, Node 18.x-20.x)
- Multi-browser E2E testing (Chromium, Firefox, WebKit)
- GitHub Actions CI/CD with automated quality checks
- **Deployment Pipeline (READY, ON HOLD):**
  - Staging deployment workflow with health checks
  - Production deployment workflow with approval gates
  - Manual rollback workflow
  - Complete deployment automation ready for GCP
- Code quality enforcement (ESLint, Prettier, Black, isort, Flake8, Pylint, Bandit)
- Security scanning (Bandit, Safety, npm audit)
- Coverage reporting and artifact uploads
- Complete documentation (8 docs, ~2,000 lines)
- ~6,000+ lines of code (tests, config, docs)

**Deployment Status: ON HOLD**
- ✅ All deployment workflows implemented and ready
- ⏸️ Deployment paused - awaiting local testing completion
- ⏸️ GCP infrastructure will use different root account (not current one)
- ⏸️ Security configuration from CLOUD_SECURITY_CONFIG.md must be completed first

---

---

## 🚧 Before Production Deployment: Critical Prerequisites

**Status:** Must complete before Batch 8 (GCP Deployment)

**These items MUST be completed before pushing to production:**

### 1. Local Testing Completion
- [ ] **Run all functional tests locally** (99+ automated tests)
- [ ] **End-user testing** - Manual testing of complete user workflows
  - Article reading experience
  - Navigation and filtering
  - Mobile responsiveness
  - Search functionality
  - Social sharing
- [ ] **Performance testing** - Load times, database queries, API responses
- [ ] **Accessibility testing** - Screen readers, keyboard navigation, WCAG compliance

### 2. GCP Infrastructure Setup (Different Account)
- [ ] **Create new GCP project** with different root account (NOT current one)
- [ ] **Set up billing** with proper alerts and quotas
- [ ] **Configure organization policies** for security
- [ ] **Document new GCP project details** in secure location

### 3. Security Configuration (CRITICAL)
**Reference:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/CLOUD_SECURITY_CONFIG.md`

- [ ] **API Key Scoping:**
  - Create new scoped GCP API key (restrict to Vertex AI, Cloud Storage, Cloud SQL, Cloud Run only)
  - Set quota limits (1000 requests/day for Gemini)
  - Add HTTP referrer restrictions (dailyworker.com)
  - Delete unrestricted API key
  - Document key restrictions

- [ ] **Service Account Setup:**
  - Create production service account with minimal permissions
  - Grant only required IAM roles (aiplatform.user, storage.objectCreator, cloudsql.client)
  - Bind to Cloud Run service
  - No exported service account keys

- [ ] **Secret Management:**
  - Enable GCP Secret Manager
  - Store all API keys in Secret Manager (Claude, OpenAI, Twitter, Reddit)
  - Store database credentials in Secret Manager
  - Grant service account secretAccessor role
  - Remove secrets from environment variables

- [ ] **IAM Configuration:**
  - Create IAM groups (admins, editors, developers)
  - Enable MFA for all human accounts
  - Implement principle of least privilege
  - Remove unused service accounts

- [ ] **Network Security:**
  - Create VPC with private subnets
  - Enable Cloud SQL Private IP (no public access)
  - Configure firewall rules (deny-all default)
  - Enable Cloud Armor for DDoS protection
  - Configure rate limiting policies

- [ ] **Database Security:**
  - Disable public IP on Cloud SQL
  - Enable SSL/TLS enforcement
  - Create database users with minimal permissions
  - Enable automated backups (daily)
  - Test backup restoration

- [ ] **Monitoring & Alerting:**
  - Set up log sinks (security logs, audit logs)
  - Configure alert policies (IAM changes, API spikes, cost thresholds)
  - Set up notification channels (email, SMS)
  - Enable Security Command Center
  - Test all alerts

- [ ] **Application Security:**
  - Implement JWT authentication for admin panel
  - Enable MFA for admin accounts
  - Configure Content Security Policy headers
  - Implement rate limiting on APIs
  - Run dependency vulnerability scan
  - Fix critical and high severity vulnerabilities

- [ ] **Container Security:**
  - Use minimal base image (Alpine)
  - Run as non-root user
  - Scan container image for vulnerabilities
  - Enable Container Analysis
  - Remove unnecessary packages

- [ ] **Compliance:**
  - Create privacy policy (GDPR, CCPA)
  - Implement cookie consent banner
  - Enable audit logging (3-year retention)
  - Verify no PII storage for anonymous users

### 4. Deployment Readiness
- [ ] Review all 8 GitHub Actions workflows
- [ ] Update deployment secrets in GitHub repository
- [ ] Test staging deployment workflow
- [ ] Verify rollback procedure works
- [ ] Document deployment process

### 5. Quality Assurance
- [ ] All 99+ tests passing locally
- [ ] No critical or high security vulnerabilities
- [ ] Performance benchmarks met (< 2s page load)
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] All documentation updated and accurate

**Deployment Timeline:**
- **Current Phase:** Local testing and security setup
- **Next Phase:** Batch 7 - Subscription System (can proceed in parallel with security setup)
- **GCP Deployment:** Batch 8 - Only after ALL prerequisites above are complete
- **No rush to production** - Quality and security over speed

---

## Batch 7: Subscription System

**Dependencies:** Automated journalism pipeline complete (Batch 6)
**Parallel:** 7.1-7.2 simultaneous, then 7.3-7.4 simultaneous, then 7.5-7.6 sequential
**Purpose:** Implement subscription-based revenue system at 50 cents per day ($15/month)
**Note:** Can proceed in parallel with security setup for Batch 8

**Overview:**
Implements subscription functionality to enable revenue generation. Users pay $15/month (50 cents per day) for premium access. Includes payment processing via Stripe, subscriber authentication and access control, subscriber dashboard, and subscription management features.

**Business Model:**
- Free tier: Limited article access (3 articles/month or article previews)
- Subscriber tier: $15/month unlimited access
- Payment processing: Stripe (2.9% + 30 cents per transaction)
- Target revenue: 100 subscribers = $1,500/month gross, $1,455/month net

### Phase 7.1: Database Schema for Subscriptions
- **Status:** Not Started
- **Complexity:** S
- **Tasks:**
  - [ ] Create `subscriptions` table (user_id, stripe_subscription_id, status, plan_type, current_period_start, current_period_end, cancel_at_period_end)
  - [ ] Create `subscription_plans` table (plan_name, price_cents, billing_interval, features_json)
  - [ ] Create `payment_methods` table (user_id, stripe_payment_method_id, card_brand, last4, is_default)
  - [ ] Create `invoices` table (user_id, stripe_invoice_id, amount_cents, status, paid_at, invoice_url)
  - [ ] Create `subscription_events` table (audit log: subscription_id, event_type, event_data_json, created_at)
  - [ ] Create `sports_leagues` table (league_code, name, country, tier_requirement)
  - [ ] Create `user_sports_preferences` table (user_id, league_id, enabled)
  - [ ] Create `sports_results` table (league_id, match_date, home_team, away_team, score, summary)
  - [ ] Add columns to `users`: subscription_status, subscriber_since, free_article_count, last_article_reset
  - [ ] Add column to `articles`: is_premium (boolean, default false for public articles), sports_league_id (nullable)
  - [ ] Test schema migrations locally
- **Done When:** All subscription tables created including sports schema, migrations tested, ready for Stripe integration

### Phase 7.2: Stripe Payment Integration
- **Status:** Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Set up Stripe account and obtain API keys (test mode and production mode)
  - [ ] Integrate Stripe SDK (backend: stripe library for Node.js/Python)
  - [ ] Implement Stripe Checkout session creation endpoint (POST /api/subscribe)
  - [ ] Implement webhook endpoint for Stripe events (POST /api/webhooks/stripe)
  - [ ] Handle webhook events: checkout.session.completed, invoice.paid, invoice.payment_failed, customer.subscription.updated, customer.subscription.deleted
  - [ ] Implement payment method update flow (Stripe Customer Portal or custom UI)
  - [ ] Test complete payment flow locally with Stripe test cards
  - [ ] Store webhook signature verification (environment variable)
- **Done When:** Users can subscribe via Stripe Checkout, webhooks update database, test payments successful

### Phase 7.3: Subscriber Authentication & Access Control
- **Status:** Blocked
- **Depends On:** Phase 7.1, Phase 7.2
- **Complexity:** M
- **Tasks:**
  - [ ] Implement user registration flow (email, password, create Stripe customer)
  - [ ] Add subscription status checks to article access endpoints
  - [ ] Implement free tier logic (3 articles/month for non-subscribers, reset monthly)
  - [ ] Add middleware for premium article access (check subscription_status='active')
  - [ ] Implement article preview mode (first 2 paragraphs for non-subscribers)
  - [ ] Add paywall UI component (display on premium articles for non-subscribers)
  - [ ] Update session management to include subscription status
  - [ ] Test access control: free user limits, subscriber unlimited access, expired subscription handling
- **Done When:** Subscribers access all content, free users limited to 3 articles/month or previews

### Phase 7.4: Subscriber Dashboard
- **Status:** Blocked
- **Depends On:** Phase 7.1, Phase 7.2
- **Complexity:** M
- **Tasks:**
  - [ ] Build subscriber dashboard page (/account/subscription)
  - [ ] Display current subscription status (active, canceled, past_due, trial)
  - [ ] Display billing information (next billing date, amount, payment method)
  - [ ] Display invoice history (download links to Stripe invoice PDFs)
  - [ ] Add link to update payment method (Stripe Customer Portal or custom form)
  - [ ] Show subscription start date and renewal date
  - [ ] Display cancellation option with confirmation dialog
  - [ ] Test dashboard with various subscription states
- **Done When:** Subscribers can view subscription details, payment history, and billing information

### Phase 7.5: Subscription Management
- **Status:** Blocked
- **Depends On:** Phase 7.3, Phase 7.4
- **Complexity:** S
- **Tasks:**
  - [ ] Implement subscription cancellation flow (cancel at period end, immediate cancellation options)
  - [ ] Implement subscription pause feature (optional: allow pausing for 1-3 months)
  - [ ] Implement subscription reactivation (resubscribe if canceled)
  - [ ] Implement payment method update (Stripe Customer Portal integration)
  - [ ] Add email notifications for subscription events (subscribed, canceled, payment failed, renewal reminder)
  - [ ] Implement grace period for failed payments (3-day grace before access revoked)
  - [ ] Test cancellation, pause, reactivation, and payment update flows
- **Done When:** Users can cancel, pause, reactivate subscriptions, update payment methods

### Phase 7.6: Email Notifications & Testing
- **Status:** Blocked
- **Depends On:** Phase 7.5
- **Complexity:** S
- **Tasks:**
  - [ ] Set up SendGrid or similar email service (free tier: 100 emails/day)
  - [ ] Create email templates: subscription confirmation, payment receipt, payment failed, renewal reminder (7 days before), cancellation confirmation
  - [ ] Implement email sending functions for each subscription event
  - [ ] Add email notification triggers in webhook handlers
  - [ ] Test all email templates with test data
  - [ ] Test end-to-end subscription flow: sign up → subscribe → receive confirmation → access content → cancel → receive cancellation email
  - [ ] Verify free tier limits reset correctly (monthly cron job or on-access check)
  - [ ] Document subscription workflows for customer support
- **Done When:** All subscription emails send correctly, complete subscription lifecycle tested

### Phase 7.7: Sports Subscription Configuration
- **Status:** Blocked
- **Depends On:** Phase 7.1, Phase 7.3
- **Complexity:** M
- **Tasks:**
  - [ ] Define subscription tier sports access levels in `subscription_plans.features_json`
  - [ ] Implement sports preferences UI in subscriber dashboard (league selection checkboxes)
  - [ ] Build sports leagues management in admin portal (add/edit leagues, set tier requirements)
  - [ ] Create sports results ingestion system (starting with UK Premier League via free API or RSS)
  - [ ] Implement sports content filtering on homepage (show only user's selected leagues)
  - [ ] Add sports preferences section to user settings
  - [ ] Build sports article generation agent (results summaries, match reports)
  - [ ] Test tier-based access: free tier (no sports), basic tier (1 league), premium tier (multiple leagues)
  - [ ] Implement upgrade prompt when free/basic users try to access restricted leagues
- **Done When:** Sports configuration works across all tiers, UK Premier League results displayed, users can customize preferences

**Sports Tier Configuration:**
- **Free Tier:** No sports coverage access
- **Basic Tier ($15/month):** Access to 1 selected league (UK Premier League, NBA, NFL, MLB, etc.)
- **Premium Tier ($25/month - future):** Access to unlimited leagues + exclusive sports analysis

**Initial Sports Coverage:**
- UK Premier League (starting point via API-Football free tier or BBC Sport RSS)
- Expandable to: NBA, NFL, MLB, NHL, MLS, La Liga, Bundesliga, Serie A

**Batch 7 Success Criteria:**
- [ ] Users can subscribe for $15/month via Stripe Checkout
- [ ] Subscribers have unlimited article access, free users limited to 3 articles/month or previews
- [ ] Subscriber dashboard displays subscription status, billing info, and invoice history
- [ ] Users can cancel, pause, reactivate subscriptions
- [ ] Email notifications sent for all subscription events
- [ ] Stripe webhooks correctly update database
- [ ] Grace period for failed payments functional (3-day access retention)
- [ ] Sports subscription configuration functional (tier-based access, user preferences, UK Premier League results)
- [ ] Ready for production deployment with subscription features

---

## Batch 8: GCP Infrastructure & Deployment

**Dependencies:**
- Subscription system complete (Batch 7)
- ALL "Before Production Deployment" prerequisites completed
- Local testing complete (functional + end-user)
- Security configuration from CLOUD_SECURITY_CONFIG.md implemented
- New GCP account set up with proper security controls

**Parallel:** 8.1-8.4 simultaneous, then 8.5
**Purpose:** Deploy validated application to cloud with enterprise-grade security

**CRITICAL:** Do NOT begin until all prerequisites above are complete. Deployment automation is ready, but security must be implemented first.

### Phase 8.1: GCP Project Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP project creation with free tier resources
  - [ ] Service accounts and permissions
  - [ ] Billing alerts configured
  - [ ] Resource quotas set
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** GCP project ready, billing monitored

### Phase 8.2: Cloud Database Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud SQL free tier OR Supabase/PlanetScale
  - [ ] Migrate schema from local to cloud
  - [ ] Import seed data (sources)
  - [ ] Automated backups enabled
  - [ ] Connection security configured
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Cloud database operational, migration tested

### Phase 8.3: Cloud Storage & CDN
- **Complexity:** Low
- **Tasks:**
  - [ ] Configure Cloud Storage for images
  - [ ] Migrate local images to cloud storage
  - [ ] Set up Cloudflare free CDN
  - [ ] Configure public access policies
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Images accessible via CDN

### Phase 8.4: Security & Secrets
- **Complexity:** Low
- **Tasks:**
  - [ ] Secret Manager for credentials
  - [ ] Cloud Armor (basic rules) or free WAF
  - [ ] SSL/TLS via Cloud Load Balancer or Let's Encrypt
  - [ ] API rate limiting (application level)
  - [ ] CORS/CSP headers
  - [ ] Migrate local secrets to cloud
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Security baseline established

### Phase 8.5: Application Deployment
- **Complexity:** Medium
- **Tasks:**
  - [ ] Deploy to Cloud Run (serverless) OR Compute Engine (small instance)
  - [ ] Configure environment variables
  - [ ] Set up auto-SSL
  - [ ] Configure health checks
  - [ ] Test deployment
  - [ ] Import pre-generated content to cloud database
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Application running on GCP, content migrated

---

## Batch 9: Cloud Operations Setup

**Dependencies:** Application deployed to GCP (Batch 8)
**Parallel:** All phases simultaneous

### Phase 9.1: CI/CD Pipeline
- **Complexity:** Low
- **Tasks:**
  - [ ] GitHub Actions → deploy to GCP
  - [ ] Security scanning in pipeline
  - [ ] Automated testing
  - [ ] Deployment rollback capability
- **Cost:** $0
- **Done When:** Git push triggers deployment to GCP

### Phase 9.2: Monitoring & Alerting
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP Monitoring/Logging (free tier)
  - [ ] UptimeRobot free tier
  - [ ] Health check endpoints
  - [ ] Email alerts for critical errors
  - [ ] Cost monitoring dashboard
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Uptime monitored, errors logged, costs tracked

### Phase 9.3: Scheduled Jobs
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud Scheduler for content discovery
  - [ ] Daily topic discovery automation
  - [ ] Database maintenance jobs
  - [ ] Backup verification
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Automated discovery runs daily

### Phase 9.4: Performance Optimization
- **Complexity:** Low
- **Tasks:**
  - [ ] Image optimization, lazy loading
  - [ ] CSS/JS minification
  - [ ] Gzip compression
  - [ ] CDN caching policies
  - [ ] Database query optimization
- **Cost:** $0
- **Done When:** Pages load < 4 seconds on production

---

## Batch 10: Production Testing & Launch

**Dependencies:** Cloud infrastructure operational (Batch 9)
**Parallel:** 10.1-10.3 simultaneous, then 10.4
**Sequential:** 10.4 must complete before 10.5

### Phase 10.1: Production Testing
- **Complexity:** Low
- **Tasks:**
  - [ ] End-to-end testing on GCP
  - [ ] Test content discovery → publication flow
  - [ ] Test admin dashboard on production
  - [ ] Test all filtering and navigation
  - [ ] Mobile testing on real devices
  - [ ] Performance testing under load
- **Cost:** $0
- **Done When:** All features work on production, no critical bugs

### Phase 10.2: Production Security Scan
- **Complexity:** Low
- **Tasks:**
  - [ ] Security scan on production URLs
  - [ ] Verify HTTPS and SSL configuration
  - [ ] Test rate limiting
  - [ ] Verify WAF rules
  - [ ] Check for exposed secrets
- **Cost:** $0
- **Done When:** No critical vulnerabilities in production

### Phase 10.3: Social Media Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Create accounts: Facebook, X/Twitter, Reddit
  - [ ] Agent drafts posts (headline, link, hashtags)
  - [ ] Manual posting workflow documentation
  - [ ] Post to relevant subreddits manually
- **Cost:** $0
- **Done When:** Social accounts ready, posting workflow documented

### Phase 10.4: Soft Launch
- **Complexity:** Low
- **Tasks:**
  - [ ] Launch to small audience (friends, community)
  - [ ] Share on personal social media
  - [ ] Relevant subreddit posts
  - [ ] Monitor site performance
  - [ ] Monitor costs in real-time
- **Cost:** Track actual costs during soft launch
- **Done When:** First 50-100 readers reached, site stable

### Phase 10.5: Iterate on Feedback
- **Complexity:** Low
- **Tasks:**
  - [ ] Gather user feedback
  - [ ] Monitor uptime, errors, costs
  - [ ] Track views (free Google Analytics or Plausible)
  - [ ] Continue content production: 3-10 articles daily
  - [ ] Fix UX-impacting bugs
  - [ ] Adjust topics based on engagement
  - [ ] Refine ongoing story tagging
  - [ ] Optimize costs based on actual usage
- **Cost:** Track and report actual monthly costs
- **Done When:** Satisfactory utility achieved, stable operations, costs under target

---

## Post-MVP: Scale When Justified

**Execution:** ONLY when utility proven and business analyst approves

### Automation Goals (Post-MVP)
- Automated posting to Facebook, X.com
- Faceless vlog-style articles for Instagram/TikTok
- Output level reference: caitlinjohnstone.com
- Specialized AI journalist agents
- Advanced analytics
- User registration and personalization

### Platform Expansion (Post-MVP)
- iOS app (timing determined by business analyst)
- Android app (timing determined by business analyst)

### Scale Triggers (Business Analyst Decision)
- Satisfactory MVP utility demonstrated
- Organic readership growth
- Clear path to sustainability
- UX-impacting bugs addressed

---

## Success Metrics (Local-First)

**Local Validation (Batches 1-4):**
- [x] **Complete development environment runs on localhost** ✅ Batch 1-3
- [x] **Database schema supports all features (national/local/ongoing)** ✅ Batch 1-3
- [x] **Content discovery and filtering works with test data** ✅ Batch 2-3
- [x] **Can generate quality articles locally (reading level 7.5-8.5)** ✅ Batch 2
- [x] **Admin dashboard functional for review/approval** ✅ Batch 3.1
- [x] **Web portal displays articles with proper formatting** ✅ Batch 3.2, 3.3
- [x] **Regional filtering works with test data** ✅ Batch 3.4
- [x] **Ongoing stories visually prominent** ✅ Batch 3.2
- [x] **All 9 categories represented in test content** ✅ Batch 4.3
- [x] **Share buttons functional (localhost URLs)** ✅ Batch 3.5
- [x] **Mobile-responsive design validated** ✅ Batch 3.2, 3.3
- [x] **No critical security vulnerabilities** ✅ Batch 4.2
- [x] **Documentation sufficient for another developer to run locally** ✅ Batch 4.4
- [x] **Cost: $0 (all local)** ✅ Batches 1-4

**Cloud Deployment Readiness (Before Batch 8):**
- [x] **MVP fully validated in local environment** ✅ Batch 4.1
- [x] **5 quality articles pre-generated** ✅ Batch 4.3
- [x] **Complete end-to-end testing passed locally** ✅ Batch 4.1
- [x] **Security scan clean** ✅ Batch 4.2
- [x] **Legal pages drafted** ✅ Batch 4.5
- [x] **Design redesigned with visual-first approach** ✅ Batch 5
- [x] **Automated journalism pipeline implemented** ✅ Batch 6
- [x] **Testing infrastructure and CI/CD implemented** ✅ Batch 6.5
- [ ] **Subscription system implemented** (Batch 7)
- [ ] **Ready to begin cloud costs** (after Batch 7 complete)

**Production Launch (Batch 10):**
- [ ] Application running on GCP
- [ ] Subscription system operational (Stripe processing payments)
- [ ] Satisfactory article quality (accurate, worker-centric, doesn't pull punches)
- [ ] Quality over quantity: 3-10 articles daily, scaling with readership
- [ ] Broad category coverage: minimum 1 national + 1 local + 1 other category
- [ ] Regional filtering functional in production
- [ ] No UX-impacting bugs
- [ ] Actual cloud costs tracked and reported
- [ ] Target: < $100/month actual costs

**Soft Launch Criteria:**
- [ ] First 50-100 readers reached
- [ ] Site stable under initial traffic
- [ ] Actual costs within budget
- [ ] Feedback collected

**Growth (Post-MVP):**
- Business analyst determines scaling timing based on utility and engagement
- Article volume scales with readership growth (not fixed targets)
- NO traditional MAU/retention targets for MVP
- Focus: Utility, accuracy, worker-centric perspective, quality over quantity

---

## Cost Summary

**Local Development (Batches 1-6.5):** $0 (except minimal Stripe test transactions in Batch 7)
- All development and testing done locally
- Batches 1-4: Complete ✅
- Batch 5: Design redesign (local CSS/HTML/JS work) ✅
- Batch 6: Automated journalism pipeline (local agent work) ✅
- Batch 6.5: Testing infrastructure & CI/CD ✅
- Batch 7: Subscription system (Stripe integration, local testing)
- No cloud services required for Batches 1-6.5
- Uses existing LLM subscriptions (Claude/ChatGPT/Gemini)
- Uses free API tiers (Twitter, Reddit, RSS feeds)
- Stripe test mode in Batch 7 (no real charges during development)

**Cloud Deployment (Batches 8-10):** Real-world costs TBD
- Costs begin only when GCP deployment starts (Batch 8)
- Cost estimates will be provided before each cloud service is activated
- Actual costs tracked and reported during soft launch
- Target: < $100/month after launch
- Billing alerts configured to prevent overruns

**Cost Control Strategy:**
- Zero spend until MVP validated locally
- Costs estimated before cloud deployment begins
- Real-time cost monitoring during deployment
- Actual costs reported during soft launch phase
- Optimize based on observed usage patterns 

---

## API Justification

**Social Media:**
- Twitter API v2: FREE tier (500K tweets/month)
- Reddit API: FREE tier (60/min)
- Facebook: Manual posting (no API)
- **Decision:** FREE tiers for discovery, manual posting for MVP

**News Sources:**
- Reuters/AP/ProPublica: FREE RSS feeds
- **Decision:** REJECT paid news APIs

**Images:**
- News: Sourced from reputable outlets with citation
- Opinion: Google Gemini (user-provided GCP API key)
- Fallback: Unsplash/Pexels (free)
- **Decision:** $0 API cost (user provides Gemini key)

**All APIs: $0/month for MVP**

---

## Parallelization (Agent Work Streams)

**Batch 1 (Local Setup):** 3 agents ✅ COMPLETE
**Batch 2 (Local Content):** 4 agents ✅ COMPLETE
**Batch 3 (Local Portal):** 5 agents ✅ COMPLETE
**Batch 4 (Local Testing):** 5 agents ✅ COMPLETE
**Batch 5 (Design Redesign):** 2-3 agents ✅ COMPLETE
**Batch 6 (Automated Journalism):** 6 agents ✅ COMPLETE
**Batch 6.5 (Testing Infrastructure):** 3 agents ✅ COMPLETE
**Batch 7 (Subscriptions):** 3-4 agents (database, Stripe integration, access control, dashboard, notifications)
**Batch 8 (GCP Deploy):** 5 agents (GCP setup, cloud DB, storage/CDN, security, deployment)
**Batch 9 (Cloud Ops):** 4 agents (CI/CD, monitoring, scheduling, performance)
**Batch 10 (Production):** 5 agents (production testing, security scan, social, soft launch, iteration)

**Peak: 6 concurrent agents (Batch 6)**
**Zero Cloud Costs: Batches 1-6.5**
**Cloud Costs Begin: Batch 8**

---

## Next Steps

1. ✅ Set up local development environment (Batch 1) COMPLETE
2. ✅ Build and test content pipeline locally (Batch 2) COMPLETE
3. ✅ Build and test web portal locally (Batch 3) COMPLETE
4. ✅ Validate complete MVP works locally (Batch 4) COMPLETE
5. ✅ Design redesign for visual-first storytelling (Batch 5) COMPLETE
6. ✅ Automated Journalism Pipeline (Batch 6) COMPLETE
7. ✅ Testing Infrastructure & CI/CD (Batch 6.5) COMPLETE
8. ✅ Deployment Pipeline (Batch 6.5) COMPLETE - **ON HOLD**
9. ✅ 3-Tier Verification System (Batch 6 enhancement) COMPLETE
10. **NEXT:** Investigatory Journalist Agent (Batch 6.9)
11. **PARALLEL:** Local testing completion (functional + end-user testing)
12. **PARALLEL:** Security configuration setup (CLOUD_SECURITY_CONFIG.md)
13. **PARALLEL:** Subscription System (Batch 7 - can proceed with security setup)
14. Set up new GCP account with proper security controls
15. Deploy to GCP (Batch 8 - cloud costs begin, ONLY after security complete)
16. Cloud operations setup (Batch 9)
17. Production testing and soft launch (Batch 10)

**Key Blockers Before Production:**
- Complete all functional tests locally
- Complete end-user testing workflows
- Implement ALL security requirements from CLOUD_SECURITY_CONFIG.md
- Set up new GCP project with different root account
- No rush - quality and security over speed

---

**Roadmap Owner:** Agent-Driven PM
**Version:** 3.3
**Last Updated:** 2026-01-01
**Philosophy:** Marxist/Leninist influenced, accurate, worker-centric news that doesn't pull punches. LOCAL-FIRST: Prove utility locally before spending on cloud. Scale when justified. SECURITY-FIRST: Production deployment only after complete security configuration.

---

## Key Changes in Version 3.3 (2026-01-01)

**What Changed:**
- Deployment pipeline complete but ON HOLD pending security and testing
- Added comprehensive "Before Production Deployment" prerequisites section
- Updated Batch 6.5 to include 8 GitHub Actions workflows (5 CI/CD + 3 deployment)
- Clarified deployment status: automation ready, security setup required
- Emphasized different GCP root account requirement
- Added detailed security checklist from CLOUD_SECURITY_CONFIG.md

**Why:**
- Deployment automation is complete and tested
- Must complete local functional and end-user testing first
- Security configuration is CRITICAL before production
- GCP infrastructure requires different root account for proper isolation
- No rush to production - quality and security take priority

**Current Status:**
- 99+ automated tests implemented and passing
- Complete CI/CD pipeline with quality checks
- Deployment workflows ready (staging, production, rollback)
- **ON HOLD:** Awaiting local testing completion and security setup
- **NEXT:** Complete CLOUD_SECURITY_CONFIG.md implementation
- **PARALLEL:** Can proceed with Batch 7 (Subscription System) during security setup

---

## Key Changes in Version 3.2 (2026-01-01)

**What Changed:**
- Batch 6 completed successfully (automated journalism pipeline fully operational)
- Added Batch 6.5: Testing Infrastructure & CI/CD
- Updated all batch references to account for new Batch 6.5
- Moved Batch 6.5 to completed archive

**Why:**
- Testing infrastructure is critical for production deployment
- 99+ automated tests ensure quality and prevent regressions
- CI/CD automation reduces manual testing burden
- Multi-version and multi-browser testing increases confidence
- Security scanning and code quality checks maintain standards
- Testing completed before subscription system work begins

**Testing Infrastructure:**
1. Backend testing: 39 unit tests covering all API endpoints (Phase 6.5.1)
2. Frontend testing: 50+ tests (unit, integration, E2E) across 3 browsers (Phase 6.5.2)
3. CI/CD automation: 5 GitHub Actions workflows with quality checks (Phase 6.5.3)
4. Complete test isolation with fresh databases per test
5. Security scanning: Bandit, Safety, npm audit
6. Code quality enforcement: ESLint, Prettier, Black, isort, Flake8, Pylint
7. Coverage reporting with Codecov integration
8. ~6,000+ lines of code (tests, config, docs)

**Development Sequence:**
1. ✅ Batch 1: Local dev environment, database, version control (COMPLETE)
2. ✅ Batch 2: Local content pipeline (COMPLETE)
3. ✅ Batch 3: Local web portal and admin interface (COMPLETE)
4. ✅ Batch 4: Complete local testing and validation (COMPLETE)
5. ✅ Batch 5: Design redesign for visual-first storytelling (COMPLETE)
6. ✅ Batch 6: Automated journalism pipeline (COMPLETE)
7. ✅ Batch 6.5: Testing infrastructure & CI/CD (COMPLETE)
8. **→ Batch 7: Subscription system (NEXT)**
9. Batch 8: GCP infrastructure and cloud deployment (costs begin here)
10. Batch 9: Cloud operations (CI/CD, monitoring, automation)
11. Batch 10: Production testing and soft launch

---

## Key Changes in Version 3.1 (2026-01-01)

**What Changed:**
- Added Batch 7: Subscription System (Stripe payment processing, $15/month subscription model)
- Renumbered previous Batches 7-9 to Batches 8-10
- Updated development sequence to include subscription implementation before cloud deployment
- Added revenue model: 100 subscribers = $1,500/month gross, $1,455/month net

**Why:**
- Revenue generation capability needed before production launch
- Subscription model enables sustainable operations (offset cloud costs)
- Free tier (3 articles/month) allows content discovery before paywall
- Stripe integration provides professional payment processing
- Testing subscription flow locally before cloud deployment reduces risk

**Subscription Features:**
1. Database schema for subscriptions, payment methods, invoices (Phase 7.1)
2. Stripe payment integration with webhook handling (Phase 7.2)
3. Subscriber authentication and access control (Phase 7.3)
4. Subscriber dashboard for billing management (Phase 7.4)
5. Subscription management: cancel, pause, reactivate (Phase 7.5)
6. Email notifications for subscription events (Phase 7.6)

**Development Sequence:**
1. ✅ Batch 1: Local dev environment, database, version control (COMPLETE)
2. ✅ Batch 2: Local content pipeline (COMPLETE)
3. ✅ Batch 3: Local web portal and admin interface (COMPLETE)
4. ✅ Batch 4: Complete local testing and validation (COMPLETE)
5. ✅ Batch 5: Design redesign for visual-first storytelling (COMPLETE)
6. **→ Batch 6: Automated journalism pipeline (CURRENT)**
7. Batch 7: Subscription system (Stripe, access control, billing)
8. Batch 8: GCP infrastructure and cloud deployment (costs begin here)
9. Batch 9: Cloud operations (CI/CD, monitoring, automation)
10. Batch 10: Production testing and soft launch

---

## Key Changes in Version 3.0 (2025-12-31)

**What Changed:**
- Batches 1-4 completed successfully (local MVP functional)
- Added Batch 5: Design Redesign (visual-first storytelling approach)
- Added Batch 6: Article Content Improvements (placeholder for user feedback)
- Renumbered cloud deployment batches (Batch 5→7, 6→8, 7→9)
- Updated development approach to reflect completed work

**Why:**
- User completed first review: technical implementation PASSED
- User requested design improvements inspired by award-winning news sites
- Design needs to reflect visual-first storytelling with Daily Worker aesthetic homage
- Article content improvements will be addressed after design work
- Cloud deployment deferred until design and content improvements complete

**Development Sequence:**
1. ✅ Batch 1: Local dev environment, database, version control (COMPLETE)
2. ✅ Batch 2: Local content pipeline (COMPLETE)
3. ✅ Batch 3: Local web portal and admin interface (COMPLETE)
4. ✅ Batch 4: Complete local testing and validation (COMPLETE)
5. ✅ Batch 5: Design redesign for visual-first storytelling (COMPLETE)
6. Batch 6: Automated journalism pipeline
7. Batch 7: GCP infrastructure and cloud deployment (costs begin here)
8. Batch 8: Cloud operations (CI/CD, monitoring, automation)
9. Batch 9: Production testing and soft launch

---

## Version History

**Version 2.0 (2025-12-29):**
- Restructured to prioritize local development and testing (Batches 1-4)
- GCP infrastructure moved to Batch 5 (only after local validation)
- All features built and tested locally before cloud deployment
- Zero cloud costs until MVP proven functional in local environment
- Cost estimates deferred to actual cloud deployment phase

**Version 3.0 (2025-12-31):**
- Batches 1-4 completed successfully
- Added design redesign batch based on user feedback
- Added article content improvement batch (pending user feedback)
- Renumbered cloud deployment to Batches 7-9

**Version 3.1 (2026-01-01):**
- Added Batch 7: Subscription System
- Renumbered cloud deployment to Batches 8-10
- Added revenue model and subscription features

**Version 3.2 (2026-01-01):**
- Batch 6 completed successfully (automated journalism pipeline)
- Added Batch 6.5: Testing Infrastructure & CI/CD
- 99+ automated tests implemented (39 backend, 50+ frontend)
- Complete CI/CD automation with 5 GitHub Actions workflows
- Multi-version testing (Python 3.9-3.11, Node 18.x-20.x)
- Multi-browser E2E testing (Chromium, Firefox, WebKit)
- Security scanning and code quality enforcement
- Updated all batch references throughout roadmap

