# The Daily Worker - MVP Implementation Roadmap

**Project:** DWnews - AI-Powered Working-Class News Platform
**Version:** 2.0
**Date:** 2025-12-29
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
1. Batches 1-4: Build and test everything locally (zero cost)
2. Batch 4: Validate complete MVP works locally
3. Batches 5-6: Deploy to GCP only after local validation
4. Batch 7: Production testing and launch

**Target Costs:**
- Development: Under $1,000 total
- Local Development: $0 (Batches 1-4)
- Cloud Costs: Actual costs reported when services begin (Batches 5-7)
- Monthly OpEx Target: Under $100/month after launch

---

## Batch 1: Local Development Setup

**Dependencies:** None
**Parallel:** All phases simultaneous
**Purpose:** Validate MVP functionality locally before cloud costs begin

### Phase 1.1: Local Database Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Schema design: articles (national/local flag, ongoing flag), sources, regions
  - [ ] Local PostgreSQL or SQLite setup
  - [ ] Seed data: 10 credible sources (AP, Reuters, ProPublica, etc.)
  - [ ] Create test articles (national/local/ongoing mix)
  - [ ] Indexes for national/local/ongoing queries
- **Cost:** $0
- **Done When:** Database schema complete, seed data loaded, queries < 500ms locally

### Phase 1.2: Local Development Environment
- **Complexity:** Low
- **Tasks:**
  - [ ] Project structure: backend API, frontend web portal
  - [ ] Local environment configuration (.env file)
  - [ ] Package management (requirements.txt / package.json)
  - [ ] Local file storage for images (instead of Cloud Storage)
  - [ ] Basic logging to console/files
  - [ ] Local secrets management (environment variables)
- **Cost:** $0
- **Done When:** Development environment runs locally on localhost

### Phase 1.3: Version Control Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] GitHub repo (free tier)
  - [ ] .gitignore (exclude .env, local images, etc.)
  - [ ] README with local setup instructions
  - [ ] Branching strategy (main + development)
- **Cost:** $0
- **Done When:** Repo created, initial commit pushed

---

## Batch 2: Local Content Pipeline

**Dependencies:** Local development environment ready
**Parallel:** All phases simultaneous
**Purpose:** Build and test content generation locally

### Phase 2.1: Content Discovery (Local)
- **Complexity:** Medium
- **Tasks:**
  - [ ] RSS feed aggregation (AP, Reuters, ProPublica, local news)
  - [ ] Twitter API v2 free tier (500K tweets/month) for trending
  - [ ] Reddit API free tier for community topics
  - [ ] Topic deduplication (keyword matching)
  - [ ] Manual trigger for discovery (instead of Cloud Scheduler)
  - [ ] Flag national vs. local topics
  - [ ] Category diversity tracking (ensure all 9 categories represented)
- **Cost:** $0 (free API tiers)
- **Done When:** Can discover topics locally, manual run produces diverse topics

### Phase 2.2: Viability Filtering (Local)
- **Complexity:** Medium
- **Tasks:**
  - [ ] Factual check: ≥3 credible sources OR ≥2 academic citations (per REQ-001)
  - [ ] Worker relevance check: Direct impact on working-class Americans
  - [ ] Engagement potential: Evidence of social interest
  - [ ] Category balance: Ensure minimum 1 from each category
  - [ ] Rejection logging to local files
- **Cost:** $0
- **Done When:** Quality topics pass all viability criteria locally

### Phase 2.3: Article Generation (Local LLM)
- **Complexity:** Medium
- **Tasks:**
  - [ ] Generation prompts (Joe Sugarman format, 8th-grade level, working-class lens)
  - [ ] Agent workflow: Topic → Claude/ChatGPT/Gemini web UI → Copy to local DB
  - [ ] Flesch-Kincaid checker (textstat library)
  - [ ] National/local categorization
  - [ ] Ongoing story tagging (manual initially)
  - [ ] Category diversity enforcement
  - [ ] Quality-first approach: 3-10 test articles
- **Cost:** $0 (existing subscriptions)
- **Done When:** Can generate quality articles locally, reading level 7.5-8.5

### Phase 2.4: Image Sourcing (Local)
- **Complexity:** Low
- **Tasks:**
  - [ ] News articles: Download images from reputable sources with citation
  - [ ] Opinion pieces: Google Gemini image generation (user provides API key)
  - [ ] Unsplash/Pexels API fallback (free)
  - [ ] Image optimization (sharp/Pillow)
  - [ ] Local file storage
  - [ ] Attribution metadata
- **Cost:** $0 (user-provided Gemini key)
- **Done When:** All test articles have images stored locally

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

## Batch 5: GCP Infrastructure & Deployment

**Dependencies:** MVP validated locally, ready for cloud deployment
**Parallel:** 5.1-5.4 simultaneous, then 5.5
**Purpose:** Deploy validated application to cloud

### Phase 5.1: GCP Project Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP project creation with free tier resources
  - [ ] Service accounts and permissions
  - [ ] Billing alerts configured
  - [ ] Resource quotas set
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** GCP project ready, billing monitored

### Phase 5.2: Cloud Database Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud SQL free tier OR Supabase/PlanetScale
  - [ ] Migrate schema from local to cloud
  - [ ] Import seed data (sources)
  - [ ] Automated backups enabled
  - [ ] Connection security configured
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Cloud database operational, migration tested

### Phase 5.3: Cloud Storage & CDN
- **Complexity:** Low
- **Tasks:**
  - [ ] Configure Cloud Storage for images
  - [ ] Migrate local images to cloud storage
  - [ ] Set up Cloudflare free CDN
  - [ ] Configure public access policies
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Images accessible via CDN

### Phase 5.4: Security & Secrets
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

### Phase 5.5: Application Deployment
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

## Batch 6: Cloud Operations Setup

**Dependencies:** Application deployed to GCP
**Parallel:** All phases simultaneous

### Phase 6.1: CI/CD Pipeline
- **Complexity:** Low
- **Tasks:**
  - [ ] GitHub Actions → deploy to GCP
  - [ ] Security scanning in pipeline
  - [ ] Automated testing
  - [ ] Deployment rollback capability
- **Cost:** $0
- **Done When:** Git push triggers deployment to GCP

### Phase 6.2: Monitoring & Alerting
- **Complexity:** Low
- **Tasks:**
  - [ ] GCP Monitoring/Logging (free tier)
  - [ ] UptimeRobot free tier
  - [ ] Health check endpoints
  - [ ] Email alerts for critical errors
  - [ ] Cost monitoring dashboard
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Uptime monitored, errors logged, costs tracked

### Phase 6.3: Scheduled Jobs
- **Complexity:** Low
- **Tasks:**
  - [ ] Cloud Scheduler for content discovery
  - [ ] Daily topic discovery automation
  - [ ] Database maintenance jobs
  - [ ] Backup verification
- **Cost:** Provide real-world cost estimates before execution
- **Done When:** Automated discovery runs daily

### Phase 6.4: Performance Optimization
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

## Batch 7: Production Testing & Launch

**Dependencies:** Cloud infrastructure operational
**Parallel:** 7.1-7.3 simultaneous, then 7.4
**Sequential:** 7.4 must complete before 7.5

### Phase 7.1: Production Testing
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

### Phase 7.2: Production Security Scan
- **Complexity:** Low
- **Tasks:**
  - [ ] Security scan on production URLs
  - [ ] Verify HTTPS and SSL configuration
  - [ ] Test rate limiting
  - [ ] Verify WAF rules
  - [ ] Check for exposed secrets
- **Cost:** $0
- **Done When:** No critical vulnerabilities in production

### Phase 7.3: Social Media Setup
- **Complexity:** Low
- **Tasks:**
  - [ ] Create accounts: Facebook, X/Twitter, Reddit
  - [ ] Agent drafts posts (headline, link, hashtags)
  - [ ] Manual posting workflow documentation
  - [ ] Post to relevant subreddits manually
- **Cost:** $0
- **Done When:** Social accounts ready, posting workflow documented

### Phase 7.4: Soft Launch
- **Complexity:** Low
- **Tasks:**
  - [ ] Launch to small audience (friends, community)
  - [ ] Share on personal social media
  - [ ] Relevant subreddit posts
  - [ ] Monitor site performance
  - [ ] Monitor costs in real-time
- **Cost:** Track actual costs during soft launch
- **Done When:** First 50-100 readers reached, site stable

### Phase 7.5: Iterate on Feedback
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

**Cloud Deployment Readiness (Before Batch 5):**
- [x] **MVP fully validated in local environment** ✅ Batch 4.1
- [x] **5 quality articles pre-generated** ✅ Batch 4.3
- [x] **Complete end-to-end testing passed locally** ✅ Batch 4.1
- [x] **Security scan clean** ✅ Batch 4.2
- [x] **Legal pages drafted** ✅ Batch 4.5
- [x] **Ready to begin cloud costs** ✅ All Batch 4 phases complete

**Production Launch (Batch 7):**
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

**Local Development (Batches 1-4):** $0
- All development and testing done locally
- No cloud services required
- Uses existing LLM subscriptions (Claude/ChatGPT/Gemini)
- Uses free API tiers (Twitter, Reddit, RSS feeds)

**Cloud Deployment (Batches 5-7):** Real-world costs TBD
- Costs begin only when GCP deployment starts (Batch 5)
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

**Batch 1 (Local Setup):** 3 agents (database, dev environment, version control)
**Batch 2 (Local Content):** 4 agents (discovery, filtering, generation, images)
**Batch 3 (Local Portal):** 5 agents (admin, homepage, articles, navigation, sharing)
**Batch 4 (Local Testing):** 5 agents (end-to-end testing, security, content, docs, legal)
**Batch 5 (GCP Deploy):** 5 agents (GCP setup, cloud DB, storage/CDN, security, deployment)
**Batch 6 (Cloud Ops):** 4 agents (CI/CD, monitoring, scheduling, performance)
**Batch 7 (Production):** 5 agents (production testing, security scan, social, soft launch, iteration)

**Peak: 5 concurrent agents**
**Zero Cloud Costs: Batches 1-4**
**Cloud Costs Begin: Batch 5**

---

## Next Steps (Updated for Local-First Approach)

1. Approve local-first MVP approach
2. Set up local development environment (Batch 1)
3. Build and test content pipeline locally (Batch 2)
4. Build and test web portal locally (Batch 3)
5. Validate complete MVP works locally (Batch 4)
6. ONLY THEN: Deploy to GCP (Batch 5)
7. Monitor actual cloud costs from deployment onward

---

**Roadmap Owner:** Agent-Driven PM
**Version:** 2.0
**Last Updated:** 2025-12-29
**Philosophy:** Marxist/Leninist influenced, accurate, worker-centric news that doesn't pull punches. LOCAL-FIRST: Prove utility locally before spending on cloud. Scale when justified.

---

## Key Changes in Version 2.0

**What Changed:**
- Restructured to prioritize local development and testing (Batches 1-4)
- GCP infrastructure moved to Batch 5 (only after local validation)
- All features built and tested locally before cloud deployment
- Zero cloud costs until MVP proven functional in local environment
- Cost estimates deferred to actual cloud deployment phase

**Why:**
- Validate complete MVP functionality without cloud costs
- Catch issues early in local environment
- Only pay for cloud services after confirming the application works
- Reduce financial risk during development
- Enable faster iteration without cloud deployment overhead

**Development Sequence:**
1. Batch 1: Local dev environment, database, version control
2. Batch 2: Local content pipeline (discovery, filtering, generation, images)
3. Batch 3: Local web portal and admin interface
4. Batch 4: Complete local testing and validation
5. Batch 5: GCP infrastructure and cloud deployment (costs begin here)
6. Batch 6: Cloud operations (CI/CD, monitoring, automation)
7. Batch 7: Production testing and soft launch

