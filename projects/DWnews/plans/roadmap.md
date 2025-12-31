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
2. Batch 5: Design redesign with visual-first approach
3. Batch 6: Article content improvements (TBD based on user feedback)
4. Batches 7-8: Deploy to GCP only after local validation
5. Batch 9: Production testing and launch

**Target Costs:**
- Development: Under $1,000 total
- Local Development: $0 (Batches 1-6)
- Cloud Costs: Actual costs reported when services begin (Batches 7-9)
- Monthly OpEx Target: Under $100/month after launch

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

## Batch 5: Design Redesign

**Dependencies:** MVP functional locally (Batches 1-4 complete)
**Parallel:** 5.1-5.2 simultaneous, then 5.3-5.5 simultaneous
**Purpose:** Transform functional design into visual-first storytelling experience inspired by award-winning news sites while paying homage to original Daily Worker newspaper aesthetic

### Phase 5.1: Design Research & Analysis
- **Status:** ⚪ Not Started
- **Complexity:** S
- **Tasks:**
  - [ ] Analyze The Washington Post homepage and article layouts (screenshot + analysis)
  - [ ] Analyze ProPublica's visual storytelling approach (screenshot + analysis)
  - [ ] Analyze The Telegraph's modern design elements (screenshot + analysis)
  - [ ] Analyze The Markup's data journalism presentation (screenshot + analysis)
  - [ ] Research historical Daily Worker newspaper aesthetic (typography, layout, voice)
  - [ ] Document key design patterns: typography, spacing, color, visual hierarchy
  - [ ] Create findings document: "Design Research Summary"
- **Done When:** Research document completed with screenshots, analysis, and design patterns identified

### Phase 5.2: Design System & Guide
- **Status:** ⚪ Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Define typography system (headers, body, quotes, captions)
  - [ ] Create color palette (inspired by Daily Worker + modern news design)
  - [ ] Define spacing and grid system
  - [ ] Document visual hierarchy rules
  - [ ] Create component library (cards, buttons, navigation, article elements)
  - [ ] Define mobile-first responsive breakpoints
  - [ ] Create design-system.md documentation
- **Done When:** Complete design system documented, ready for implementation

### Phase 5.3: Homepage Redesign
- **Status:** 🔴 Blocked
- **Depends On:** Phase 5.2
- **Complexity:** M
- **Tasks:**
  - [ ] Redesign hero section with visual-first approach
  - [ ] Implement ongoing stories section with stronger visual prominence
  - [ ] Redesign article cards with better imagery, typography, and spacing
  - [ ] Improve category and region filtering UI
  - [ ] Add visual storytelling elements (pull quotes, imagery, data viz foundations)
  - [ ] Implement design system typography and colors
  - [ ] Mobile-responsive refinements
  - [ ] Update index.html with new design
- **Done When:** Homepage reflects award-winning design inspiration, visually impactful

### Phase 5.4: Article Detail Page Redesign
- **Status:** 🔴 Blocked
- **Depends On:** Phase 5.2
- **Complexity:** M
- **Tasks:**
  - [ ] Redesign article header with stronger visual impact
  - [ ] Improve body typography for better readability
  - [ ] Add pull quotes styling
  - [ ] Redesign metadata display (category, region, reading level, etc.)
  - [ ] Improve image presentation and captions
  - [ ] Add "What This Means For Workers" visual callout section
  - [ ] Redesign share buttons with better visual integration
  - [ ] Update article.html with new design
- **Done When:** Article pages have visual-first storytelling approach, strong readability

### Phase 5.5: Design Polish & Refinements
- **Status:** 🔴 Blocked
- **Depends On:** Phase 5.3, Phase 5.4
- **Complexity:** S
- **Tasks:**
  - [ ] Refine spacing and alignment across all pages
  - [ ] Add micro-interactions and transitions
  - [ ] Optimize font loading and performance
  - [ ] Cross-browser testing (Chrome, Firefox, Safari)
  - [ ] Mobile device testing (iOS, Android)
  - [ ] Accessibility review (contrast, focus states, ARIA)
  - [ ] Performance optimization (CSS minification, critical CSS)
- **Done When:** Design polished, accessible, performant across all devices and browsers

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
- **Status:** ⚪ Not Started
- **Complexity:** S
- **Tasks:**
  - [ ] Create `event_candidates` table (newsworthiness scoring)
  - [ ] Create `article_revisions` table (revision tracking)
  - [ ] Create `corrections` table (post-publication corrections)
  - [ ] Create `source_reliability_log` table (learning loop)
  - [ ] Add columns to `articles`: bias_scan_report, self_audit_passed, editorial_notes, assigned_editor, review_deadline
  - [ ] Add columns to `topics`: verified_facts, source_plan, verification_status
  - [ ] Test schema migrations (SQLite local, PostgreSQL cloud-ready)
- **Done When:** All new tables created, migrations tested locally

### Phase 6.2: Signal Intake Agent (Event Discovery)
- **Status:** ⚪ Not Started
- **Complexity:** M
- **Tasks:**
  - [ ] Build RSS feed aggregator (Reuters, AP, ProPublica, local sources)
  - [ ] Integrate Twitter API v2 (trending labor topics, worker hashtags)
  - [ ] Integrate Reddit API (r/labor, r/WorkReform, r/antiwork, local subs)
  - [ ] Build government feed scraper (data.gov, Labor Dept, NLRB)
  - [ ] Implement event candidate deduplication logic
  - [ ] Write event candidates to `event_candidates` table (status='discovered')
  - [ ] Create agent definition: `.claude/agents/signal-intake.md`
  - [ ] Test locally with real feeds (target: 20-50 events/day)
- **Done When:** Agent discovers events from multiple sources, writes to database

### Phase 6.3: Evaluation Agent (Newsworthiness Scoring)
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1
- **Complexity:** M
- **Tasks:**
  - [ ] Implement newsworthiness scoring (Impact, Timeliness, Proximity, Conflict, Novelty, Verifiability)
  - [ ] Build worker-relevance scoring model ($45k-$350k income bracket impact)
  - [ ] Configure thresholds (reject <30, hold 30-59, approve ≥60)
  - [ ] Query event_candidates, score each on 6 dimensions (0-100 total)
  - [ ] Update status: 'approved'/'rejected'/'hold'
  - [ ] Create topic records for approved events
  - [ ] Create agent definition: `.claude/agents/evaluation.md`
  - [ ] Test with sample event candidates (target: 10-20% approval rate)
- **Done When:** Agent scores events, approves 10-20% for article generation

### Phase 6.4: Verification Agent (Source Verification & Attribution)
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1, Phase 6.3
- **Complexity:** M
- **Tasks:**
  - [ ] Build primary source identification (WebSearch, document analysis)
  - [ ] Implement cross-reference verification (compare claims across sources)
  - [ ] Build fact classification engine (observed vs. claimed vs. interpreted)
  - [ ] Implement source hierarchy enforcement (named > org > docs > anon)
  - [ ] Verify ≥3 credible sources OR ≥2 academic citations per topic
  - [ ] Store verified_facts and source_plan in topics table (JSON format)
  - [ ] Create agent definition: `.claude/agents/verification.md`
  - [ ] Test with approved topics (verify source count, attribution plan)
- **Done When:** Agent verifies ≥3 sources per topic, creates attribution plans

### Phase 6.5: Enhanced Journalist Agent (Article Drafting + Self-Audit)
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.1, Phase 6.4
- **Complexity:** M
- **Tasks:**
  - [ ] Enhance existing journalist agent with self-audit checklist (10-point validation)
  - [ ] Implement bias detection scan (hallucination, propaganda checks)
  - [ ] Add reading level validation (Flesch-Kincaid 7.5-8.5 scoring)
  - [ ] Integrate with verified_facts from topics table
  - [ ] Generate articles with proper attribution (use source_plan)
  - [ ] Store bias_scan_report in articles table (JSON format)
  - [ ] Update agent definition: `.claude/agents/journalist.md` (enhancements)
  - [ ] Test with verified topics (generate articles passing self-audit)
- **Done When:** Agent generates quality articles, 100% pass 10-point self-audit

### Phase 6.6: Editorial Workflow Integration
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.5
- **Complexity:** S
- **Tasks:**
  - [ ] Build Editorial Coordinator Agent (assign articles, notify editors, track SLA)
  - [ ] Update admin portal with review interface (display bias scan, source list, self-audit results)
  - [ ] Implement revision request workflow (editorial_notes → Journalist Agent rewrites)
  - [ ] Add revision logging to `article_revisions` table
  - [ ] Configure email notifications (SendGrid integration for editor alerts)
  - [ ] Test complete editorial loop (draft → review → revise → approve → publish)
  - [ ] Create agent definition: `.claude/agents/editorial-coordinator.md`
- **Done When:** Human editors can review, request revisions, approve articles via admin portal

### Phase 6.7: Publication & Monitoring
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.6
- **Complexity:** S
- **Tasks:**
  - [ ] Build auto-publish function (articles.status='approved' → 'published')
  - [ ] Build Monitoring Agent (social mention tracking, correction detection, source reliability updates)
  - [ ] Implement correction workflow (flag → editor review → publish correction notice)
  - [ ] Add correction notices to article display (frontend update)
  - [ ] Build source reliability scoring updates (`source_reliability_log` table)
  - [ ] Test post-publication monitoring (Twitter/Reddit mention tracking)
  - [ ] Create agent definition: `.claude/agents/monitoring.md`
- **Done When:** Published articles monitored for 7 days, corrections tracked, source scores updated

### Phase 6.8: Local Testing & Integration
- **Status:** 🔴 Blocked
- **Depends On:** Phase 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
- **Complexity:** S
- **Tasks:**
  - [ ] Test end-to-end pipeline locally (signal intake → evaluation → verification → drafting → editorial → publication)
  - [ ] Validate daily cadence simulation (run all agents sequentially)
  - [ ] Test revision loop (editor requests changes, agent rewrites)
  - [ ] Test correction workflow (monitoring flags issue, editor approves correction)
  - [ ] Verify all quality gates (newsworthiness ≥60, ≥3 sources, 10-point self-audit, editorial approval)
  - [ ] Generate 3-5 test articles end-to-end
  - [ ] Document operational procedures (troubleshooting, manual overrides, escalation)
- **Done When:** Full pipeline runs locally, produces 3-5 quality articles, all quality gates pass

**Batch 6 Success Criteria:**
- [ ] 3-5 quality articles generated daily in test environment
- [ ] All 6 agents operational (Signal Intake, Evaluation, Verification, Journalist, Editorial Coordinator, Monitoring)
- [ ] Human editorial workflow functional (review → approve → publish)
- [ ] All quality gates pass (newsworthiness scoring, source verification, bias scan, editorial approval)
- [ ] Post-publication monitoring operational (corrections, source reliability tracking)
- [ ] Ready for cloud deployment (Cloud Functions defined, tested locally)

---

## Batch 7: GCP Infrastructure & Deployment

**Dependencies:** MVP validated locally with improved design and content
**Parallel:** 7.1-7.4 simultaneous, then 7.5
**Purpose:** Deploy validated application to cloud

### Phase 7.1: GCP Project Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP project creation with free tier resources
  - [ ] Service accounts and permissions
  - [ ] Billing alerts configured
  - [ ] Resource quotas set
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** GCP project ready, billing monitored

### Phase 7.2: Cloud Database Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud SQL free tier OR Supabase/PlanetScale
  - [ ] Migrate schema from local to cloud
  - [ ] Import seed data (sources)
  - [ ] Automated backups enabled
  - [ ] Connection security configured
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Cloud database operational, migration tested

### Phase 7.3: Cloud Storage & CDN
- **Complexity:** Low
- **Tasks:**
  - [ ] Configure Cloud Storage for images
  - [ ] Migrate local images to cloud storage
  - [ ] Set up Cloudflare free CDN
  - [ ] Configure public access policies
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Images accessible via CDN

### Phase 7.4: Security & Secrets
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

### Phase 7.5: Application Deployment
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

## Batch 8: Cloud Operations Setup

**Dependencies:** Application deployed to GCP
**Parallel:** All phases simultaneous

### Phase 8.1: CI/CD Pipeline
- **Complexity:** Low
- **Tasks:**
  - [ ] GitHub Actions → deploy to GCP
  - [ ] Security scanning in pipeline
  - [ ] Automated testing
  - [ ] Deployment rollback capability
- **Cost:** $0
- **Done When:** Git push triggers deployment to GCP

### Phase 8.2: Monitoring & Alerting
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP Monitoring/Logging (free tier)
  - [ ] UptimeRobot free tier
  - [ ] Health check endpoints
  - [ ] Email alerts for critical errors
  - [ ] Cost monitoring dashboard
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Uptime monitored, errors logged, costs tracked

### Phase 8.3: Scheduled Jobs
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud Scheduler for content discovery
  - [ ] Daily topic discovery automation
  - [ ] Database maintenance jobs
  - [ ] Backup verification
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Automated discovery runs daily

### Phase 8.4: Performance Optimization
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

## Batch 9: Production Testing & Launch

**Dependencies:** Cloud infrastructure operational
**Parallel:** 9.1-9.3 simultaneous, then 9.4
**Sequential:** 9.4 must complete before 9.5

### Phase 9.1: Production Testing
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

### Phase 9.2: Production Security Scan
- **Complexity:** Low
- **Tasks:**
  - [ ] Security scan on production URLs
  - [ ] Verify HTTPS and SSL configuration
  - [ ] Test rate limiting
  - [ ] Verify WAF rules
  - [ ] Check for exposed secrets
- **Cost:** $0
- **Done When:** No critical vulnerabilities in production

### Phase 9.3: Social Media Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Create accounts: Facebook, X/Twitter, Reddit
  - [ ] Agent drafts posts (headline, link, hashtags)
  - [ ] Manual posting workflow documentation
  - [ ] Post to relevant subreddits manually
- **Cost:** $0
- **Done When:** Social accounts ready, posting workflow documented

### Phase 9.4: Soft Launch
- **Complexity:** Low
- **Tasks:**
  - [ ] Launch to small audience (friends, community)
  - [ ] Share on personal social media
  - [ ] Relevant subreddit posts
  - [ ] Monitor site performance
  - [ ] Monitor costs in real-time
- **Cost:** Track actual costs during soft launch
- **Done When:** First 50-100 readers reached, site stable

### Phase 9.5: Iterate on Feedback
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

**Cloud Deployment Readiness (Before Batch 7):**
- [x] **MVP fully validated in local environment** ✅ Batch 4.1
- [x] **5 quality articles pre-generated** ✅ Batch 4.3
- [x] **Complete end-to-end testing passed locally** ✅ Batch 4.1
- [x] **Security scan clean** ✅ Batch 4.2
- [x] **Legal pages drafted** ✅ Batch 4.5
- [ ] **Design redesigned with visual-first approach** (Batch 5 in progress)
- [ ] **Article content improved based on user feedback** (Batch 6 pending)
- [ ] **Ready to begin cloud costs** (after Batches 5-6 complete)

**Production Launch (Batch 9):**
- [ ] Application running on GCP
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

**Local Development (Batches 1-6):** $0
- All development and testing done locally
- Batches 1-4: Complete ✅
- Batch 5: Design redesign (local CSS/HTML/JS work)
- Batch 6: Article content improvements (local content work)
- No cloud services required
- Uses existing LLM subscriptions (Claude/ChatGPT/Gemini)
- Uses free API tiers (Twitter, Reddit, RSS feeds)

**Cloud Deployment (Batches 7-9):** Real-world costs TBD
- Costs begin only when GCP deployment starts (Batch 7)
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
**Batch 5 (Design Redesign):** 2-3 agents (research, design system, implementation)
**Batch 6 (Content Improvements):** TBD based on user feedback
**Batch 7 (GCP Deploy):** 5 agents (GCP setup, cloud DB, storage/CDN, security, deployment)
**Batch 8 (Cloud Ops):** 4 agents (CI/CD, monitoring, scheduling, performance)
**Batch 9 (Production):** 5 agents (production testing, security scan, social, soft launch, iteration)

**Peak: 5 concurrent agents**
**Zero Cloud Costs: Batches 1-6**
**Cloud Costs Begin: Batch 7**

---

## Next Steps

1. ✅ Set up local development environment (Batch 1) COMPLETE
2. ✅ Build and test content pipeline locally (Batch 2) COMPLETE
3. ✅ Build and test web portal locally (Batch 3) COMPLETE
4. ✅ Validate complete MVP works locally (Batch 4) COMPLETE
5. **CURRENT:** Design redesign for visual-first storytelling (Batch 5)
6. **NEXT:** Article content improvements based on user feedback (Batch 6)
7. Deploy to GCP (Batch 7)
8. Cloud operations setup (Batch 8)
9. Production testing and soft launch (Batch 9)

---

**Roadmap Owner:** Agent-Driven PM
**Version:** 3.0
**Last Updated:** 2025-12-31
**Philosophy:** Marxist/Leninist influenced, accurate, worker-centric news that doesn't pull punches. LOCAL-FIRST: Prove utility locally before spending on cloud. Scale when justified.

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
5. **→ Batch 5: Design redesign for visual-first storytelling (CURRENT)**
6. Batch 6: Article content improvements based on user feedback
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

