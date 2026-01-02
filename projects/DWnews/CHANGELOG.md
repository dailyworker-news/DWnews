# Changelog

All notable changes to The Daily Worker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Known Issues
- Integration debugging in progress (module path issues)
- End-to-end pipeline not yet validated

## [0.6.5] - 2026-01-01

### Added - Batch 6.5: Testing Infrastructure & CI/CD
- **Backend Testing Infrastructure** (Phase 6.5.1)
  - 39 unit tests with complete API endpoint coverage
  - Test isolation with fresh databases per test
  - Multi-version Python testing (3.9, 3.10, 3.11)
  - Code quality enforcement: Black, isort, Flake8, Pylint
  - Security scanning: Bandit, Safety
  - Coverage reporting integration

- **Frontend Testing Infrastructure** (Phase 6.5.2)
  - 50+ tests (unit, integration, E2E)
  - Multi-browser testing (Chromium, Firefox, WebKit)
  - Playwright E2E automation
  - Multi-version Node testing (18.x, 20.x)
  - Code quality enforcement: ESLint, Prettier
  - Security scanning: npm audit

- **CI/CD Pipeline** (Phase 6.5.3)
  - 5 GitHub Actions workflows
  - Automated testing on push/PR
  - Multi-platform testing (Ubuntu, macOS, Windows)
  - Coverage reporting to Codecov
  - Artifact uploads for test results
  - Security and code quality checks

### Changed
- Improved test isolation and reliability
- Enhanced code quality standards
- Automated quality gate enforcement

## [0.6.0] - 2026-01-01

### Added - Batch 6: Automated Journalism Pipeline
- **Database Schema Extensions** (Phase 6.1)
  - 4 new tables: event_candidates, article_revisions, corrections, source_reliability_log
  - 5 new database views for common queries
  - 14 new indexes for performance optimization
  - Complete migration system with rollback support

- **Signal Intake Agent** (Phase 6.2)
  - RSS feed aggregator (8 labor news sources)
  - Twitter API v2 integration (12 hashtags, 10 queries, 10 union accounts)
  - Reddit API integration (9 labor subreddits)
  - Government feed scraper (DOL, OSHA, BLS)
  - 3-layer deduplication logic (URL, title hash, fuzzy matching)
  - Agent definition: `.claude/agents/signal-intake.md`

- **Evaluation Agent** (Phase 6.3)
  - 6-dimension newsworthiness scoring (impact, timeliness, proximity, conflict, novelty, verifiability)
  - Worker-relevance scoring ($45k-$350k income bracket impact)
  - Quality threshold: 65/100 for approval
  - 10-20% approval rate achieved in testing
  - Agent definition: `.claude/agents/evaluation.md`

- **Verification Agent** (Phase 6.4)
  - Primary source identification (WebSearch, document analysis)
  - Cross-reference verification with conflict detection
  - Fact classification (observed/claimed/interpreted)
  - 4-tier source credibility hierarchy (Tier 1: 90-100, Tier 2: 70-89, Tier 3: 50-69, Tier 4: 0-49)
  - JSON storage of verified_facts and source_plan
  - Agent definition: `.claude/agents/verification.md`

- **Enhanced Journalist Agent** (Phase 6.5)
  - 10-point self-audit checklist
  - Bias detection (hallucination/propaganda checks)
  - Reading level validation (Flesch-Kincaid 7.5-8.5)
  - Attribution engine with proper source citation
  - Regeneration loop (max 3 attempts with LLM feedback)
  - Complete database integration
  - Updated agent definition: `.claude/agents/journalist.md`

- **Editorial Workflow Integration** (Phase 6.6)
  - Editorial Coordinator Agent (479 lines, smart assignment, SLA management)
  - Email notification system (381 lines, 3 templates: assignment, approval, revision)
  - Editorial API routes (438 lines, 10 endpoints)
  - Review interface (684 lines, full-featured UI)
  - Revision control (max 2 revisions per article)
  - Complete audit trail in article_revisions table
  - Agent definition: `.claude/agents/editorial-coordinator.md`

- **Publication & Monitoring** (Phase 6.7)
  - Publication Agent (12KB, auto-publish, scheduled/manual publication)
  - Monitoring Agent (17KB, 7-day monitoring, social tracking)
  - Correction Workflow (14KB, 4 correction types: factual_error, source_error, clarification, update)
  - Source Reliability Scorer (13KB, learning loop, 0-100 scale)
  - Monitoring API Routes (11KB, 10 endpoints)
  - Frontend correction notice display
  - Agent definition: `.claude/agents/monitoring.md`

- **Local Testing & Integration** (Phase 6.8)
  - End-to-end test script (700 lines, 7-phase validation)
  - Daily cadence simulator (500 lines, realistic timing simulation)
  - Revision loop test (550 lines, editorial feedback validation)
  - Correction workflow test (600 lines, transparency verification)
  - Quality gates verifier (600 lines, 6-gate validation)
  - Operational procedures (500 lines, complete ops manual)
  - Troubleshooting guide (600 lines, error resolution guide)
  - Batch completion summary (550 lines, full documentation)

### Changed
- Extended database schema with 4 new tables
- Enhanced journalist agent with self-audit capabilities
- Improved source verification with 4-tier credibility system
- Added comprehensive quality gates (newsworthiness, sources, self-audit, bias, reading level, editorial)

### Documentation
- Added `/docs/BATCH_6_COMPLETION_SUMMARY.md`
- Added `/docs/OPERATIONAL_PROCEDURES.md`
- Added `/docs/TROUBLESHOOTING.md`
- Added 7 agent definition files in `.claude/agents/`
- Added implementation documentation for phases 6.5-6.8

## [0.5.0] - 2026-01-01

### Added - Batch 5: Design Redesign
- **Design Research & Analysis** (Phase 5.1)
  - Research on ProPublica, The Markup, Daily Worker history
  - 2025 best practices analysis
  - Visual-first storytelling approach

- **Design System & Guide** (Phase 5.2)
  - Typography: Inter (headlines) + Merriweather (body)
  - Color system: Black/white/yellow heritage palette
  - Spacing and grid system
  - Component library

- **v3.0 Traditional Newspaper Design** (Phase 5.6)
  - Playfair Display + Merriweather typography (classic newspaper serif)
  - Black/white/yellow color scheme (heritage aesthetic)
  - Multi-column grid with sidebar layout
  - Major daily headline feature (72px+ headlines)
  - Subscription widget (50¢/day pricing)
  - Archive access messaging
  - Ongoing stories in sidebar with yellow accents
  - Complete article page styling with newspaper feel
  - Responsive design maintaining traditional aesthetic on mobile

### Changed
- Replaced modern sans-serif design with traditional newspaper aesthetic
- Updated homepage layout to multi-column grid
- Enhanced article pages with large serif headlines
- Improved mobile responsiveness while maintaining heritage feel

### Documentation
- Added `/plans/design-research-summary.md`
- Added `/plans/design-system.md` (v1-v2)
- Added `/plans/design-system-v3.md` (traditional newspaper design)

## [0.4.0] - 2025-12-29

### Added - Batch 4: Local Testing & Validation
- **End-to-End Local Testing** (Phase 4.1)
  - E2E test suite with 25+ tests
  - Complete user flow validation
  - Database operation verification
  - API endpoint testing

- **Local Security Review** (Phase 4.2)
  - SECURITY.md documentation
  - 8 security scans (SQL injection, XSS, CSRF, authentication, authorization, secrets, dependencies, headers)
  - Vulnerability assessment and remediation

- **Content Pre-Generation** (Phase 4.3)
  - 5 sample articles across diverse categories
  - Quality validation (reading level 7.5-8.5)
  - Attribution and source verification
  - Category coverage: national, local, labor, politics, economy

- **Local Documentation** (Phase 4.4)
  - Comprehensive README update
  - Development guide
  - API documentation
  - Deployment instructions

- **Legal Basics** (Phase 4.5)
  - About page
  - Privacy Policy
  - Terms of Service
  - Content disclaimer

### Changed
- Improved security posture with comprehensive scanning
- Enhanced documentation for developer onboarding
- Validated MVP functionality in local environment

## [0.3.0] - 2025-12-29

### Added - Batch 3: Local Web Portal
- **Admin Dashboard** (Phase 3.1)
  - Article review interface
  - Approval workflow
  - Content management system
  - Editorial tools

- **Public-Facing Web Portal** (Phase 3.2)
  - Homepage with article listings
  - Article detail pages
  - Category filtering
  - Search functionality
  - Mobile-responsive design

- **Regional Filtering** (Phase 3.4)
  - National content display
  - Local content by region
  - IP-based location detection
  - User preference override

- **Ongoing Story Highlighting** (Phase 3.2)
  - Visual prominence for ongoing stories
  - Timeline display
  - Related article linking
  - Story arc tracking

- **Social Sharing** (Phase 3.5)
  - Share buttons (Facebook, Twitter, Reddit)
  - Open Graph meta tags
  - Twitter Card support
  - Copy link functionality

### Changed
- Improved article display with better typography
- Enhanced navigation and filtering
- Optimized for mobile devices

## [0.2.0] - 2025-12-29

### Added - Batch 2: Local Content Pipeline
- **Topic Discovery Agent**
  - RSS feed integration
  - Social media monitoring
  - Event detection and filtering
  - Worker-relevance scoring

- **Journalist Agent**
  - GPT-4 integration for article generation
  - Reading level validation (Flesch-Kincaid 7.5-8.5)
  - Attribution system
  - Quality control checks

- **Source Verification**
  - Multi-source validation (≥3 credible sources)
  - Source credibility scoring
  - Attribution tracking
  - Fact-checking integration

- **Image Pipeline**
  - Image sourcing from reputable outlets
  - Google Gemini integration for opinion pieces
  - Unsplash/Pexels fallback
  - Proper citation and attribution

### Changed
- Implemented content quality validation
- Enhanced attribution system
- Improved source verification process

## [0.1.0] - 2025-12-29

### Added - Batch 1: Local Development Environment
- **Database Setup**
  - SQLite database with complete schema
  - 12 core tables: articles, topics, sources, categories, regions, tags, article_tags, ongoing_stories, story_timeline, users, user_preferences, admin_audit_log
  - SQLAlchemy ORM models
  - Migration system

- **Backend Framework**
  - Flask application structure
  - API endpoints for CRUD operations
  - Database connection management
  - Error handling and logging

- **Version Control**
  - Git repository initialization
  - Initial commit structure
  - .gitignore configuration
  - README documentation

- **Development Environment**
  - Python 3.9+ setup
  - Virtual environment configuration
  - Dependency management (requirements.txt)
  - Local testing framework

### Infrastructure
- Local SQLite database
- Flask development server
- Static file serving
- Basic logging system

---

## Version Numbering

- **Major version** (1.0.0): Production launch, breaking changes
- **Minor version** (0.X.0): New batches completed, feature additions
- **Patch version** (0.0.X): Bug fixes, minor improvements

Current status: **0.6.5** (Batch 6.5 complete, Batch 7 not started)

---

## Upcoming Releases

### [0.7.0] - Planned (Batch 7: Subscription System)
- Stripe payment integration
- Subscriber authentication and access control
- Subscriber dashboard
- Subscription management (cancel, pause, reactivate)
- Email notifications for subscription events
- Sports subscription configuration
- Free tier limits (3 articles/month)

### [0.8.0] - Planned (Batch 8: GCP Infrastructure)
- GCP project setup
- Cloud SQL database migration
- Cloud Storage and CDN configuration
- Security and secrets management
- Application deployment to Cloud Run

### [0.9.0] - Planned (Batch 9: Cloud Operations)
- CI/CD pipeline deployment
- Monitoring and alerting setup
- Scheduled jobs configuration
- Performance optimization

### [1.0.0] - Planned (Batch 10: Production Launch)
- Production testing
- Security audit
- Social media setup
- Soft launch (50-100 readers)
- Iterative improvements based on feedback

---

**Changelog Maintained By:** Project Manager Agent
**Format:** [Keep a Changelog](https://keepachangelog.com/)
**Versioning:** [Semantic Versioning](https://semver.org/)
