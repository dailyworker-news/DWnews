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

## Batch 3: Local Web Portal & Admin Interface

**Dependencies:** Content pipeline working locally
**Parallel:** All phases simultaneous
**Purpose:** Build and test frontend locally

### Phase 3.1: Local Admin Dashboard
- **Complexity:** Medium
- **Tasks:**
  - [ ] Simple admin panel (HTML/CSS/JS)
  - [ ] Article queue (national/local/ongoing flags)
  - [ ] Preview with formatting
  - [ ] Approve/reject buttons
  - [ ] Single admin user (local auth)
  - [ ] Connect to local database
- **Cost:** $0
- **Done When:** Human can review/approve articles locally

### Phase 3.2: Event-Based Homepage (Local)
- **Complexity:** Medium
- **Tasks:**
  - [ ] Layout: NEW stories + ONGOING stories blend
  - [ ] NEW stories: Chronological (newest first)
  - [ ] ONGOING stories: Visual prominence (larger cards, borders, "ONGOING" badge)
  - [ ] Regional view: National + Local mix
  - [ ] Location detection: Hardcoded for testing (no IP detection locally)
  - [ ] Responsive grid (mobile-first)
  - [ ] Article cards: headline, image, date, category, indicators
  - [ ] Simple pagination
- **Cost:** $0
- **Done When:** Homepage works locally, displays test articles correctly

### Phase 3.3: Article Pages (Local)
- **Complexity:** Low
- **Tasks:**
  - [ ] Article template: headline, image, date, category, body
  - [ ] "Why This Matters" section
  - [ ] "What You Can Do" section (labor articles)
  - [ ] Readable typography
  - [ ] Image attribution display
  - [ ] Load from local database
- **Cost:** $0
- **Done When:** Articles render correctly locally, mobile-responsive

### Phase 3.4: Category + Regional Navigation (Local)
- **Complexity:** Low
- **Tasks:**
  - [ ] Category menu: Labor, Tech, Politics, Economics, Current Affairs, Art, Sport, Good News
  - [ ] Regional selector: National, Test Region
  - [ ] Category + region combined filtering
  - [ ] Same event-centric layout
- **Cost:** $0
- **Done When:** Navigation works locally with test data

### Phase 3.5: Share Buttons (Local)
- **Complexity:** Low
- **Tasks:**
  - [ ] Share buttons: Facebook, Twitter, Reddit, Email, Copy Link
  - [ ] Native share URLs (localhost URLs for testing)
  - [ ] No share count tracking
- **Cost:** $0
- **Done When:** Share buttons functional locally

---

## Batch 4: Local Testing & Validation

**Dependencies:** All local features built
**Parallel:** All phases simultaneous
**Purpose:** Validate MVP works completely before cloud deployment

### Phase 4.1: End-to-End Local Testing
- **Complexity:** Low
- **Tasks:**
  - [ ] Manual testing: topic discovery → filtering → generation → admin review → publication → viewing
  - [ ] Test national/local filtering
  - [ ] Test ongoing story prominence
  - [ ] Test regional switching
  - [ ] Test share buttons
  - [ ] Mobile testing (responsive design)
  - [ ] Test all 9 categories
  - [ ] Test image display and attribution
- **Cost:** $0
- **Done When:** Complete pipeline works locally, no blocking bugs

### Phase 4.2: Local Security Review
- **Complexity:** Low
- **Tasks:**
  - [ ] Free scanners: OWASP ZAP, npm audit, pip audit
  - [ ] Agent code review
  - [ ] Test admin auth locally
  - [ ] Check security headers
  - [ ] Validate input sanitization
- **Cost:** $0
- **Done When:** No critical vulnerabilities in code

### Phase 4.3: Content Pre-Generation
- **Complexity:** Low
- **Tasks:**
  - [ ] Generate 10-15 quality articles locally
  - [ ] Include 2-3 ongoing stories
  - [ ] Human review/approve all via local admin
  - [ ] Ensure minimum 1 article from each category
  - [ ] Minimum 10% Good News content
  - [ ] Mix national and local stories
- **Cost:** $0
- **Done When:** Launch-ready content exists in local database

### Phase 4.4: Local Documentation
- **Complexity:** Low
- **Tasks:**
  - [ ] README: local setup, development workflow
  - [ ] Admin workflow guide
  - [ ] Content generation workflow
  - [ ] Troubleshooting basics
  - [ ] Environment configuration guide
- **Cost:** $0
- **Done When:** Another developer could run project locally

### Phase 4.5: Legal Basics (Draft)
- **Complexity:** Low
- **Tasks:**
  - [ ] Privacy Policy template (adapted)
  - [ ] Terms of Service template (adapted)
  - [ ] Copyright notice
  - [ ] Image attribution guidelines
- **Cost:** $0
- **Done When:** Legal pages drafted, ready for deployment

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
- [ ] Complete development environment runs on localhost
- [ ] Database schema supports all features (national/local/ongoing)
- [ ] Content discovery and filtering works with test data
- [ ] Can generate quality articles locally (reading level 7.5-8.5)
- [ ] Admin dashboard functional for review/approval
- [ ] Web portal displays articles with proper formatting
- [ ] Regional filtering works with test data
- [ ] Ongoing stories visually prominent
- [ ] All 9 categories represented in test content
- [ ] Share buttons functional (localhost URLs)
- [ ] Mobile-responsive design validated
- [ ] No critical security vulnerabilities
- [ ] Documentation sufficient for another developer to run locally
- [ ] Cost: $0 (all local)

**Cloud Deployment Readiness (Before Batch 5):**
- [ ] MVP fully validated in local environment
- [ ] 10-15 quality articles pre-generated
- [ ] Complete end-to-end testing passed locally
- [ ] Security scan clean
- [ ] Legal pages drafted
- [ ] Ready to begin cloud costs

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

