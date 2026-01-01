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
3. Batch 6: Automated journalism pipeline (still zero cost)
4. Batch 7: Subscription system (local testing, Stripe integration)
5. Batches 8-9: Deploy to GCP only after local validation
6. Batch 10: Production testing and launch

**Target Costs:**
- Development: Under $1,000 total
- Local Development: $0 (Batches 1-7, except Stripe test transactions)
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

## Batch 7: Subscription System

**Dependencies:** Automated journalism pipeline complete (Batch 6)
**Parallel:** 7.1-7.2 simultaneous, then 7.3-7.4 simultaneous, then 7.5-7.6 sequential
**Purpose:** Implement subscription-based revenue system at 50 cents per day ($15/month)

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
  - [ ] Add columns to `users`: subscription_status, subscriber_since, free_article_count, last_article_reset
  - [ ] Add column to `articles`: is_premium (boolean, default false for public articles)
  - [ ] Test schema migrations locally
- **Done When:** All subscription tables created, migrations tested, ready for Stripe integration

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

**Batch 7 Success Criteria:**
- [ ] Users can subscribe for $15/month via Stripe Checkout
- [ ] Subscribers have unlimited article access, free users limited to 3 articles/month or previews
- [ ] Subscriber dashboard displays subscription status, billing info, and invoice history
- [ ] Users can cancel, pause, reactivate subscriptions
- [ ] Email notifications sent for all subscription events
- [ ] Stripe webhooks correctly update database
- [ ] Grace period for failed payments functional (3-day access retention)
- [ ] Ready for production deployment with subscription features

---

## Batch 8: GCP Infrastructure & Deployment

**Dependencies:** Subscription system complete (Batch 7), MVP validated locally with improved design and content
**Parallel:** 8.1-8.4 simultaneous, then 8.5
**Purpose:** Deploy validated application to cloud

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

**Cloud Deployment Readiness (Before Batch 7):**
- [x] **MVP fully validated in local environment** ✅ Batch 4.1
- [x] **5 quality articles pre-generated** ✅ Batch 4.3
- [x] **Complete end-to-end testing passed locally** ✅ Batch 4.1
- [x] **Security scan clean** ✅ Batch 4.2
- [x] **Legal pages drafted** ✅ Batch 4.5
- [x] **Design redesigned with visual-first approach** ✅ Batch 5
- [ ] **Automated journalism pipeline implemented** (Batch 6 in progress)
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

**Local Development (Batches 1-7):** $0 (except minimal Stripe test transactions)
- All development and testing done locally
- Batches 1-4: Complete ✅
- Batch 5: Design redesign (local CSS/HTML/JS work) ✅
- Batch 6: Automated journalism pipeline (local agent work)
- Batch 7: Subscription system (Stripe integration, local testing)
- No cloud services required
- Uses existing LLM subscriptions (Claude/ChatGPT/Gemini)
- Uses free API tiers (Twitter, Reddit, RSS feeds)
- Stripe test mode (no real charges during development)

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
**Batch 5 (Design Redesign):** 2-3 agents (research, design system, implementation) ✅
**Batch 6 (Automated Journalism):** 6 agents (signal intake, evaluation, verification, journalist, editorial, monitoring)
**Batch 7 (Subscriptions):** 3-4 agents (database, Stripe integration, access control, dashboard, notifications)
**Batch 8 (GCP Deploy):** 5 agents (GCP setup, cloud DB, storage/CDN, security, deployment)
**Batch 9 (Cloud Ops):** 4 agents (CI/CD, monitoring, scheduling, performance)
**Batch 10 (Production):** 5 agents (production testing, security scan, social, soft launch, iteration)

**Peak: 6 concurrent agents (Batch 6)**
**Zero Cloud Costs: Batches 1-7**
**Cloud Costs Begin: Batch 8**

---

## Next Steps

1. ✅ Set up local development environment (Batch 1) COMPLETE
2. ✅ Build and test content pipeline locally (Batch 2) COMPLETE
3. ✅ Build and test web portal locally (Batch 3) COMPLETE
4. ✅ Validate complete MVP works locally (Batch 4) COMPLETE
5. ✅ Design redesign for visual-first storytelling (Batch 5) COMPLETE
6. **CURRENT:** Automated Journalism Pipeline (Batch 6)
7. **NEXT:** Subscription System (Batch 7)
8. Deploy to GCP (Batch 8 - cloud costs begin)
9. Cloud operations setup (Batch 9)
10. Production testing and soft launch (Batch 10)

---

**Roadmap Owner:** Agent-Driven PM
**Version:** 3.1
**Last Updated:** 2026-01-01
**Philosophy:** Marxist/Leninist influenced, accurate, worker-centric news that doesn't pull punches. LOCAL-FIRST: Prove utility locally before spending on cloud. Scale when justified.

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

