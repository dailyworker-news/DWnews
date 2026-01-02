# The Daily Worker - Requirements Specification

## Document Information

**Version:** 1.2
**Date:** 2026-01-02
**Project:** The Daily Worker (Project Code: DWnews)
**Status:** Active
**Philosophy:** Bare Bones MVP - Ship Fast, Iterate

**MANDATORY COMPLIANCE DOCUMENTS:**
- **LEGAL.md** - Legal guidelines for attribution, commentary, and platform positioning (v1.0, 2026-01-02)
- **journalism-standards.md** - Professional journalism standards and best practices
- **SECURITY.md** - Security requirements and implementation guidelines

All content generation, agent instructions, and editorial workflows MUST comply with these documents.

---

## 1. Mission

Deliver accurate, worker-centric news that doesn't pull punches. Materialist perspective on politics, economics, labor, technology, culture, and current affairs. Quality over quantity.

**Legal Positioning:** The Daily Worker is a news aggregation and commentary platform that amplifies worker-centric perspectives on current events. We aggregate news from external sources with proper attribution and provide AI-generated editorial commentary and analysis. We are NOT an independent fact-checking service or verification authority. All content links to original source material for reader verification.

---

## 2. Core Features

### 2.1 Front Page
- **NEW Stories:** Latest articles, chronological order
- **CONTINUING Stories:** Ongoing events with visual prominence (disasters, elections, worker issues)
- Visual hierarchy: Blend recency with significance using card size, color accents, badges

### 2.2 Content Requirements
- **National News:** Minimum 5 stories
- **Local News:** Minimum 5 stories
  - User signup: Select state preferences
  - No signup: Infer state from IP address
  - Default: National news
- **Reading Level:** 8th grade (Flesch-Kincaid 7.5-8.5)
- **Writing Style:** Joe Sugarman format (compelling headlines, engaging flow, clear benefits, "so-what" explanations)

### 2.3 Imagery
- **News Articles:** Reputable sources (AP, Reuters, Creative Commons) with proper citations
- **Opinion Pieces:** Google Gemini generated images via user's GCP API
- **Free Stock:** Unsplash, Pexels as fallback

### 2.4 Categories
- Labor Issues
- Technology
- Politics
- Economics
- Current Affairs
- Art & Culture
- Celebrity Gossip (Opinion/Commentary)
- Sport
- Good News (minimum 10% of content)

---

## 3. Content Generation Pipeline

### 3.1 Discovery
- Monitor X.com, Reddit for trending topics
- RSS feeds from credible sources
- Manual curation acceptable

### 3.2 Viability Filtering
Topics MUST pass all three criteria:
1. **Factual Accuracy:** ≥3 credible sources OR ≥2 academic citations
2. **Worker Relevance:** Direct impact on working-class Americans ($45k-$350k income)
3. **Engagement Potential:** Evidence of social interest

### 3.3 Generation
- LLM-powered article creation (user's Claude, ChatGPT, or Gemini subscriptions)
- Specialized AI journalist agents by beat (investigative, sports, gossip, economics, tech, culture)
- **ALL articles MUST comply with professional journalism standards** (see `journalism-standards.md`)
- **ALL articles MUST comply with legal guidelines** (see `LEGAL.md`) **[MANDATORY]**
- AI bias detection and copy editing
- Human final review and approval

**Mandatory Compliance Documents:**
All journalist agents must follow professional standards and legal guidelines defined in:
- `plans/LEGAL.md` **[MANDATORY]** - Legal guidelines for attribution, commentary vs. fact, verification language, platform positioning
- `plans/journalism-standards.md` - Professional newsroom standards (inverted pyramid, 5W+H, attribution, sources, nut graf, etc.)
- `.claude/agents/journalist.md` - Journalist agent instructions and checklist

**Key Standards:**
- Inverted pyramid structure (most important information first)
- 5W+H coverage (Who, What, When, Where, Why, How) in first 3-4 paragraphs
- Attribution for all non-observable facts
- Multiple independent sources (≥3 credible OR ≥2 academic)
- Functional quotes that add value
- Nut graf explaining why the event matters
- Neutral tone with emotion conveyed through facts/quotes, not author voice
- Clear separation of fact and opinion

**Legal Compliance Requirements (LEGAL.md):**
- **Attribution:** All facts must be attributed to sources ("According to [Source]...", "As reported by [Source]...")
- **Commentary vs. Fact:** Facts are attributed; commentary is clearly marked with signal phrases ("suggests", "raises questions", "critics argue")
- **Verification Language:** Use only "aggregated/corroborated/multi-sourced" (NEVER "verified/certified/confirmed")
- **Platform Positioning:** Aggregator + commentary, NOT independent fact-checking or verification authority
- **Source Links:** All original sources must be linked in references section
- **Editorial Notes:** Must include sourcing level (aggregated/corroborated/multi-sourced)

### 3.4 Editorial Workflow
1. AI journalist agent generates draft following journalism standards AND legal guidelines (LEGAL.md)
2. AI bias scan and initial edit
3. Self-check against journalism standards checklist
4. **Legal compliance check** (attribution, verification language, commentary distinction)
5. Human editor reviews and approves (journalism + legal compliance)
6. Graphics sourcing/generation
7. Publication

**Legal Compliance Checkpoints:**
- Pre-generation: Review LEGAL.md requirements before writing
- Post-generation: Validate attribution, sourcing level, commentary distinction
- Pre-publication: Editor verifies legal compliance checklist completed

---

## 4. Infrastructure

### 4.1 Hosting Platform
- **MUST deploy on Google Cloud Platform (GCP)**
- Single instance deployment (scale as needed)
- Target: $30-100/month hosting costs

### 4.2 Technology Stack
**Backend:**
- Python 3.11+ or Node.js
- FastAPI or Express.js
- PostgreSQL (self-hosted or managed)

**Frontend:**
- React/Next.js
- Tailwind CSS
- Mobile-first responsive design

**AI/LLM:**
- User's Google Cloud API for Gemini (primary)
- User's existing Claude/ChatGPT subscriptions
- Free-tier rotation for cost optimization

**Storage & CDN:**
- Google Cloud Storage or Cloudflare R2
- Cloudflare free tier CDN (global, zero cost)

**Authentication:**
- Admin/editor only (password-based)
- No user registration for MVP

### 4.3 External APIs
- Reddit API (free tier)
- X.com API (free tier or manual monitoring)
- Unsplash/Pexels APIs (free)
- **Manual social posting** (deferred automation)

---

## 5. Deferred Features

### 5.1 Post-MVP Automation
- Facebook auto-posting
- X.com auto-posting
- Instagram/TikTok faceless vlog content
- Output level: caitlinjohnstone.com quality

### 5.2 Native Mobile Apps
- iOS/Android apps determined by business analyst after MVP
- Responsive web sufficient initially

### 5.3 User Features
- User profiles and personalization
- Comments and community engagement
- Saved articles and reading history

---

## 6. Functional Requirements

### REQ-001: Article Production
**Priority:** High
The system MUST generate 3-10 articles daily, scaling as readership grows.

### REQ-002: Local News Integration
**Priority:** High
The system MUST provide state-specific local news:
- User signup: State selection
- No signup: IP-based state inference
- Minimum 1 local stories per state 
- Minimum 1 national stories
- Minimum 1 of each other story category

### REQ-003: Story Classification
**Priority:** High
The system MUST classify stories as NEW or CONTINUING with appropriate visual treatment.

### REQ-004: Image Attribution
**Priority:** High
All images MUST include proper source citations (photographer, license, source).

### REQ-005: Google Gemini Integration
**Priority:** High
The system MUST use user's GCP API for Gemini image generation on opinion pieces or articles that don't have available imagery from places like Reuters, the AP etc.

### REQ-006: Reading Level Validation
**Priority:** High
All articles MUST meet Flesch-Kincaid 7.5-8.5 reading level (automated validation).

### REQ-007: Bias Detection
**Priority:** High
AI agents MUST scan for LLM hallucinations, corporate propaganda, factual errors before human review.

### REQ-008: Manual Social Posting
**Priority:** High
Social media distribution via manual posting until satisfactory MVP achieved.

### REQ-009: Content Minimum
**Priority:** High
Daily content MUST include minimum 1 national + 1 local stories + 1 from another category. Quantity of articles will change situation dependent, i.e. Monday will contain more sporting stories from the previous Saturday + Sunday when sport is typically played. 

### REQ-010: Responsive Design
**Priority:** High
Web application MUST work on mobile, tablet, desktop without native apps.

---

## 7. Non-Functional Requirements

### 7.1 Performance
- Page load: <2 seconds (broadband)
- Article load: <1.5 seconds
- Support 100-1,000 concurrent users (scale as needed)

### 7.2 Security
- HTTPS required
- Input validation and sanitization
- XSS/CSRF protection
- Password hashing (bcrypt)
- AI agent code reviews for vulnerabilities
- Cloud provider security (GCP)

### 7.3 Reliability
- 99% uptime target
- Daily backups
- Single instance acceptable for MVP
- Graceful degradation if services fail

### 7.4 Accessibility
- WCAG 2.1 Level AA compliance
- Keyboard navigation
- Screen reader support
- Alt text for all images
- Semantic HTML

---

## 8. Success Criteria

**Remove traditional metrics.** Focus on:

### 8.1 Quality
- Articles are accurate and well-sourced
- Writing is clear and accessible
- Worker-centric perspective is authentic
- Content doesn't pull punches

### 8.2 Functionality
- System generates satisfactory articles consistently
- User experience is smooth and bug-free
- Local news integration works correctly
- Visual hierarchy effectively highlights continuing stories

### 8.3 Deployment
- Soft launch after working prototype demonstrated
- Satisfactory article quality verified
- Major UX bugs resolved
- Editorial workflow validated

---

## 9. Cost Constraints

### 9.1 Development Budget
**Maximum: $5,000 total**
- Domain, SSL, setup: $0-500
- Development tools: $0-1,000
- Design/branding support: $0-1,500
- Contingency: $0-2,000

### 9.2 Monthly Operating Budget
**Target: <$500/month**

**Projected Costs:**
- GCP hosting: $30-100
- Domain/DNS: $1-3
- APIs: $0-50 (prefer free tiers)
- Monitoring: $0-20
- Backups: $0-10

**Cost Rule:** Only use paid services if <$50/month and justified.

### 9.3 API Costs
- Gemini: User's GCP API
- LLMs: User's existing Claude/ChatGPT/Gemini subscriptions
- Images: Free (Unsplash, Pexels)
- Social APIs: Free tiers
- News sources: RSS feeds, web scraping (legal/ToS compliant)

---

## 10. Development Approach

### 10.1 Agent-Driven Development
- Primary development: AI agents (Claude, ChatGPT, Gemini)
- Human oversight: Strategy, decisions, final approval
- Cost: $0 marginal (existing subscriptions)

### 10.2 Manual Processes
Manual acceptable for MVP:
- Social media posting
- Content curation
- Editorial review
- Deployment

### 10.3 Automation Priority
Automate when:
- Manual process becomes bottleneck
- Volume justifies automation cost
- MVP quality demonstrated

---

## 11. Design Considerations

### 11.1 Visual Design
- Inspiration: dailymail.co.uk layout style
- Bold headlines, image-heavy
- Grid layout with thumbnails
- Clear category navigation
- Distinct working-class brand identity

### 11.2 Story Visual Hierarchy
**NEW Stories:**
- Standard card size
- Chronological order
- Recent timestamp visible

**CONTINUING Stories (last 'n' days):**
- Enhanced visual prominence
- Larger cards for high-severity
- Color-coded borders (red: critical, orange: ongoing)
- Status badges (Breaking, Developing, Ongoing)
- Elevated position despite age

### 11.3 Local News UX
- State selector on signup
- IP-based state detection (with user override)
- "Local News" section on homepage
- State indicator on local articles

---

## 12. Content Guidelines

### 12.1 Editorial Standards
- Factual accuracy paramount
- Multiple source verification
- Clear opinion vs. news distinction
- Working-class perspective maintained
- Humor appropriate to subject
- No corporate propaganda
- Challenge power, support workers

### 12.2 Article Structure (Joe Sugarman)
1. Compelling headline
2. Engaging opening hook
3. Logical flow building interest
4. Feature-benefit presentation
5. "So-What" explanation (why readers care)
6. Address objections
7. Actionable steps (labor articles)
8. Clear conclusion

### 12.3 Fact-Checking
- ≥3 credible sources for factual claims
- Academic citations where appropriate
- Source credibility assessment
- Cross-reference verification
- Opinion pieces clearly labeled

---

## 13. Technical Specifications

### 13.1 Database Schema

**articles**
```sql
id: SERIAL PRIMARY KEY
slug: VARCHAR(255) UNIQUE NOT NULL
headline: VARCHAR(255) NOT NULL
subheadline: VARCHAR(255)
body: TEXT NOT NULL
category_id: INTEGER REFERENCES categories(id)
story_type: ENUM('NEW', 'CONTINUING') DEFAULT 'NEW'
is_opinion: BOOLEAN DEFAULT FALSE
severity_score: INTEGER (0-100, 0=normal, 50=significant, 100=critical)
state_id: INTEGER REFERENCES states(id) NULL (NULL = national)
publication_date: TIMESTAMP NOT NULL
last_updated: TIMESTAMP DEFAULT NOW()
continuing_until: TIMESTAMP NULL (when CONTINUING status expires)
reading_level_score: DECIMAL(3,1) (Flesch-Kincaid)
source_urls: TEXT[] (array of source URLs)
author_agent_type: VARCHAR(50) (investigative, sports, gossip, etc.)
human_editor_id: INTEGER REFERENCES users(id)
image_id: INTEGER REFERENCES images(id)
status: ENUM('draft', 'ai_review', 'human_review', 'approved', 'published')
view_count: INTEGER DEFAULT 0
created_at: TIMESTAMP DEFAULT NOW()
INDEX(story_type, publication_date)
INDEX(state_id, publication_date)
INDEX(status)
```

**images**
```sql
id: SERIAL PRIMARY KEY
url: VARCHAR(500) NOT NULL
cdn_url: VARCHAR(500)
source: VARCHAR(100) (unsplash, pexels, gemini, ap, reuters)
photographer: VARCHAR(255)
attribution: TEXT NOT NULL
license: VARCHAR(100) (cc0, cc-by, proprietary, etc.)
generated_by_gemini: BOOLEAN DEFAULT FALSE
gemini_prompt: TEXT NULL
created_at: TIMESTAMP DEFAULT NOW()
```

**users**
```sql
id: SERIAL PRIMARY KEY
email: VARCHAR(255) UNIQUE NOT NULL
password_hash: VARCHAR(255) NOT NULL
role: ENUM('admin', 'editor') DEFAULT 'editor'
preferred_state_id: INTEGER REFERENCES states(id) NULL
created_at: TIMESTAMP DEFAULT NOW()
last_login: TIMESTAMP
```

**states**
```sql
id: SERIAL PRIMARY KEY
code: CHAR(2) UNIQUE NOT NULL (AL, AK, AZ, etc.)
name: VARCHAR(50) NOT NULL
region: VARCHAR(50) (Northeast, South, Midwest, West)
```

**categories**
```sql
id: SERIAL PRIMARY KEY
name: VARCHAR(50) UNIQUE NOT NULL
slug: VARCHAR(50) UNIQUE NOT NULL
display_order: INTEGER
```

**sources**
```sql
id: SERIAL PRIMARY KEY
article_id: INTEGER REFERENCES articles(id)
url: TEXT NOT NULL
title: VARCHAR(500)
credibility_score: INTEGER (0-100)
fetch_date: TIMESTAMP DEFAULT NOW()
```

**editorial_queue**
```sql
id: SERIAL PRIMARY KEY
article_id: INTEGER REFERENCES articles(id)
status: ENUM('pending_ai_review', 'ai_review_complete', 'pending_human', 'revision_requested', 'approved', 'rejected')
ai_bias_report: JSONB (hallucinations, propaganda, errors)
editor_notes: TEXT
assigned_editor_id: INTEGER REFERENCES users(id)
created_at: TIMESTAMP DEFAULT NOW()
updated_at: TIMESTAMP DEFAULT NOW()
INDEX(status, created_at)
```

**social_posts**
```sql
id: SERIAL PRIMARY KEY
article_id: INTEGER REFERENCES articles(id)
platform: ENUM('facebook', 'x', 'instagram', 'tiktok')
posted_at: TIMESTAMP
post_url: VARCHAR(500)
engagement: JSONB (likes, shares, comments)
```

### 13.2 Front Page Display Algorithm

**Homepage Query Logic:**
```
1. Determine user's state:
   - IF user logged in: Use users.preferred_state_id
   - ELSE: IP geolocation lookup → infer state
   - ELSE: Default to NULL (national news)

2. Fetch articles:
   a) CONTINUING stories (story_type='CONTINUING' AND continuing_until > NOW())
      - Order by severity_score DESC, last_updated DESC
      - Limit to top 10

   b) NEW national stories (state_id IS NULL)
      - Order by publication_date DESC
      - Limit 15

   c) NEW local stories (state_id = user_state_id)
      - Order by publication_date DESC
      - Limit 10

3. Merge and layout:
   - Grid: 3 columns desktop, 2 columns tablet, 1 column mobile
   - First 2 rows: CONTINUING stories (severity-based sizing)
   - Remaining rows: Mix NEW national and NEW local, alternating
   - Total front page: ~25 articles visible without scroll
```

**Card Layout Specifications:**
- Grid container: CSS Grid, gap 20px
- Standard card: 300px × 400px (image 300×200, text 200px)
- Significant card (1.5 span): 470px × 400px
- Critical card (2 span): 640px × 500px
- Mobile: All cards full width, maintain aspect ratio

### 13.3 IP Geolocation Implementation

**Service:** IPinfo.io or IP2Location
- **Free tier**: 50,000 requests/month (sufficient for MVP)
- **Endpoint**: `GET https://ipinfo.io/{ip_address}/json?token={api_key}`
- **Response**: `{ "ip": "8.8.8.8", "city": "Mountain View", "region": "California", "country": "US" }`
- **Fallback**: If API fails, serve national news only

**Lookup Logic:**
```
1. Extract client IP from request headers (X-Forwarded-For or REMOTE_ADDR)
2. Check local cache (Redis/memory) for IP → state mapping (TTL: 24 hours)
3. If cache miss, call IPinfo.io API
4. Extract "region" field, map to states.code
5. Store in cache
6. If API error or non-US IP: Default to NULL (national)
```

**State Mapping:**
- "California" → "CA"
- "New York" → "NY"
- Maintain mapping table of full state names to 2-letter codes

**Privacy:**
- Do NOT store IP addresses in database
- Only store inferred state_id in session/cookie
- GDPR-compliant (no PII storage)

### 13.4 Google Gemini API Integration

**Use Case:** Generate images for opinion pieces (is_opinion=TRUE)

**API Specifications:**
- **Service**: Google Cloud Vertex AI Image Generation
- **Endpoint**: `POST https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/imagegeneration:predict`
- **Authentication**: User's GCP service account key (provided)
- **Request Format**:
```json
{
  "instances": [{
    "prompt": "Editorial cartoon style: [article headline], worker perspective, bold colors"
  }],
  "parameters": {
    "sampleCount": 1,
    "aspectRatio": "16:9"
  }
}
```
- **Response**: Base64 encoded image
- **Cost**: ~$0.02-0.04 per image (user's GCP billing)

**Workflow:**
1. Article created with is_opinion=TRUE
2. Generate prompt: "Editorial cartoon: {headline}, worker-centric theme"
3. Call Gemini API
4. Upload image to Cloud Storage
5. Store URL in images table with generated_by_gemini=TRUE, gemini_prompt=prompt
6. Attach to article

**Error Handling:**
- API failure → Fallback to Unsplash API (search: "editorial, newspaper")
- Invalid API key → Alert admin, use fallback
- Retry: 3 attempts with exponential backoff

### 13.5 APIs and Integrations Summary
- Google Cloud Gemini API (user-provided GCP key)
- IPinfo.io or IP2Location (free tier, 50k requests/month)
- LLM APIs (user's Claude, ChatGPT, Gemini subscriptions)
- Unsplash API (free tier, 50 requests/hour)
- Pexels API (free tier, 200 requests/hour)
- Social media APIs (deferred for manual posting)
- RSS feed parsers (feedparser library)

### 13.6 Editorial Workflow State Machine

**States and Transitions:**
```
draft → ai_review → human_review → approved → published
                  ↓
              revision_requested → draft
                  ↓
              rejected (terminal)
```

**State Definitions:**
1. **draft**: AI agent creates initial article
2. **ai_review**: Automated bias scan, fact-check, reading level check
3. **human_review**: Assigned to editor for manual review
4. **revision_requested**: Editor requests changes, returns to draft
5. **approved**: Editor approves, ready for publication
6. **published**: Live on website
7. **rejected**: Article rejected, not published

**editorial_queue Table Updates:**
- Create entry when article enters ai_review
- Update status as workflow progresses
- Store ai_bias_report JSON with findings
- Assign editor when entering human_review

**Editor Actions:**
- Approve: status → approved
- Request Revision: status → revision_requested, add editor_notes
- Reject: status → rejected

### 13.7 GCP Infrastructure Specifications

**Compute:**
- **Option 1 (Recommended)**: Cloud Run (serverless)
  - Container: Node.js or Python app
  - Auto-scaling: 0-10 instances
  - Memory: 512MB-1GB per instance
  - CPU: 1 vCPU
  - Cost: ~$0-30/month (generous free tier)

- **Option 2**: Compute Engine e2-micro
  - 1 vCPU, 1GB RAM
  - Always free tier eligible
  - Ubuntu 22.04 LTS
  - Cost: $0/month if in free tier region

**Database:**
- **Cloud SQL PostgreSQL 14**
  - Tier: db-f1-micro (free tier eligible)
  - Storage: 10GB SSD
  - Backups: Daily automated
  - Cost: $0-15/month

**Storage:**
- **Cloud Storage**
  - Bucket: daily-worker-images
  - Region: us-central1
  - Standard storage class
  - Cost: ~$0.02/GB/month

**Networking:**
- VPC: Default VPC acceptable for MVP
- Firewall: Allow HTTPS (443), HTTP (80), SSH (22) from allowed IPs
- Load Balancer: Not needed for Cloud Run (built-in)
- CDN: Cloudflare (external, free)

**IAM:**
- Service account for Cloud Run → Cloud SQL connection
- Service account for Gemini API access
- Editor access for deployment automation

**Monitoring:**
- Cloud Logging (free tier: 50GB/month)
- Cloud Monitoring (basic metrics)
- Uptime checks (free)

### 13.8 Deployment

**Status:** Deployment automation complete, ON HOLD pending security setup

**CI/CD Infrastructure:**
- GitHub Actions workflows (8 total):
  - 5 CI/CD workflows: backend tests, frontend tests, code quality, dependency updates, main CI
  - 3 deployment workflows: staging deployment, production deployment, manual rollback
- Multi-version testing: Python 3.9-3.11, Node 18.x-20.x
- Multi-browser E2E testing: Chromium, Firefox, WebKit
- Automated quality checks and security scanning

**Production Infrastructure (Ready, Not Deployed):**
- GCP Cloud Run (serverless container deployment)
- PostgreSQL (Cloud SQL with private IP only)
- Cloud Storage for images (with Cloud CDN)
- Cloudflare CDN (external, free tier)
- Environments: Development (local) + Staging (GCP) + Production (GCP)

**Deployment Prerequisites (MUST COMPLETE FIRST):**
1. Complete all functional and end-user testing locally
2. Set up new GCP project with different root account
3. Implement ALL security requirements from CLOUD_SECURITY_CONFIG.md:
   - API key scoping (restrict to required services only)
   - Service account setup with minimal permissions
   - Secret Manager for all credentials
   - VPC with private subnets, Cloud SQL Private IP
   - Cloud Armor for DDoS protection
   - Monitoring, alerting, and audit logging
   - Container security hardening
   - Compliance configuration (GDPR, CCPA)
4. Test deployment to staging environment
5. Verify rollback procedures work

**Security-First Approach:**
- NO deployment to production until security configuration complete
- Unrestricted API keys MUST be scoped before cloud deployment
- Service accounts MUST use principle of least privilege
- All secrets MUST be stored in Secret Manager (not environment variables)
- Network isolation required (private IPs, VPC, firewall rules)

**Reference Documents:**
- Security: `/plans/CLOUD_SECURITY_CONFIG.md` (comprehensive security requirements)
- Deployment Status: `/plans/roadmap.md` (current deployment hold status)
- Testing: Backend tests, frontend tests, CI/CD workflows in `.github/workflows/`

---

## 14. Security

### 14.1 Essential Protections
- HTTPS/TLS encryption
- Input validation/sanitization
- XSS/CSRF protection
- SQL injection prevention
- Secure password hashing
- API key security (env vars)
- AI agent security reviews

### 14.2 Authentication
- Admin/editor password authentication
- No user registration for MVP
- Public content access (no login)

### 14.3 Vulnerability Management
- Dependency scanning (GitHub Dependabot)
- Monitor security advisories
- Apply critical patches within 30 days
- AI agent code reviews

---

## 15. Testing & Quality

### 15.1 Testing Approach
- AI agent code reviews
- Manual testing of critical flows
- Reading level automated validation
- Bias detection automated
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile responsive testing

### 15.2 Quality Gates
- Article accuracy verified
- Reading level in range
- Bias scan passed
- Human editor approved
- UX bugs resolved
- Performance acceptable

---

## 16. Deployment & Launch

**Current Status:** Deployment infrastructure ready, ON HOLD pending security and testing

### 16.1 Pre-Deployment Requirements (MUST COMPLETE)

**Local Testing:**
- [ ] All 99+ automated tests passing
- [ ] Functional testing complete (all features working)
- [ ] End-user testing complete (realistic user workflows validated)
- [ ] Performance testing passed (< 2s page load times)
- [ ] Accessibility audit passed (WCAG 2.1 AA compliance)
- [ ] Mobile responsiveness validated on real devices

**Security Configuration:**
- [ ] New GCP project created with different root account
- [ ] API keys scoped to minimum required services
- [ ] Service accounts configured with least privilege
- [ ] All secrets migrated to GCP Secret Manager
- [ ] VPC and network security configured (private IPs, firewall rules)
- [ ] Cloud Armor enabled for DDoS protection
- [ ] Monitoring and alerting configured
- [ ] Container images hardened and scanned
- [ ] Compliance requirements implemented (GDPR, CCPA)
- [ ] Complete security checklist from CLOUD_SECURITY_CONFIG.md

**Deployment Readiness:**
- [ ] Staging environment deployment tested
- [ ] Production deployment workflow tested
- [ ] Rollback procedure verified
- [ ] All GitHub Actions secrets configured
- [ ] Documentation updated and accurate

### 16.2 MVP Launch Criteria
- Working prototype demonstrated locally
- Satisfactory article quality achieved
- Major UX bugs fixed
- Editorial workflow validated
- Local news integration working
- Visual hierarchy effective
- **ALL security requirements implemented** (CRITICAL)
- **Complete testing completed** (functional + end-user)
- **New GCP infrastructure ready** (different account, proper security)

### 16.3 Soft Launch (After Prerequisites Complete)
- Deploy to staging environment first
- Verify all functionality in staging
- Deploy to production via approved workflow
- Generate initial articles
- Monitor quality, UX, and security
- Monitor costs and performance
- Iterate and fix issues
- Expand when satisfactory

### 16.4 Post-Launch
- Monitor costs daily (first week), then weekly
- Monitor security logs daily (first month)
- Track content quality continuously
- Fix bugs as discovered
- Iterate based on usage and feedback
- Scale infrastructure only when justified
- Rotate secrets per security schedule
- Conduct monthly security reviews

### 16.5 Deployment Timeline
1. **CURRENT:** Complete local testing (functional + end-user)
2. **CURRENT:** Implement security configuration (CLOUD_SECURITY_CONFIG.md)
3. **PARALLEL:** Batch 7 - Subscription System (can proceed with security setup)
4. **NEXT:** Set up new GCP project with proper security controls
5. **NEXT:** Deploy to staging and test
6. **FINAL:** Production deployment (only after ALL prerequisites complete)

**No Rush Policy:** Quality and security take absolute priority over speed to production. The deployment automation is ready and tested. Take the time needed to get security right.

---

## 17. Future Enhancements

### 17.1 Determined by Business Analyst
- Native iOS/Android apps (timing TBD)
- User profiles and personalization
- Comments and community features
- Email newsletters

### 17.2 Post-MVP Automation
- Automated Facebook posting
- Automated X.com posting
- Instagram/TikTok faceless vlogs
- Advanced social analytics
- Push notifications

### 17.3 Scaling Features
- Multi-region deployment
- Database replication
- Horizontal scaling
- Advanced caching
- CDN optimization

---

## Appendix A: Credible News Sources

- Associated Press (AP)
- Reuters
- ProPublica
- Current Affairs
- Democracy Now!
- The Empire Files
- The Grayzone
- Jacobin
- The Nation
- Revolutionary Blackout Network
- Glenn Greenwald - System Update
- Declassified UK
- The Guardian
- Washington Post
- New York Times
- Local news outlets (state-specific)

---

## Appendix B: Story Classification Logic

### Classification Algorithm

**NEW Story (story_type='NEW'):**
- Published within last 48 hours
- Breaking news or fresh development
- No ongoing updates expected
- Editor manually sets story_type='NEW' at creation

**CONTINUING Story (story_type='CONTINUING'):**
- Ongoing event requiring updates (disasters, strikes, elections)
- Editor manually sets story_type='CONTINUING' at creation
- Editor sets continuing_until timestamp (defaults to 7 days from publication)
- Automatically reverts to standard treatment after continuing_until expires

### Severity Scoring

**severity_score (0-100):**
- **0-30 (Standard)**: Regular news, no special urgency
- **31-70 (Significant)**: Important worker impact, moderate urgency
- **71-100 (Critical)**: Major disasters, critical worker issues, elections

Editor manually assigns severity_score based on:
- Worker impact (job security, safety, economic impact)
- Geographic scope (local=lower, national=higher)
- Immediacy (ongoing crisis=higher)

### Story Transitions

1. **Creation**: Editor creates article, sets story_type and severity_score
2. **Publication**: Article published with initial classification
3. **Updates**: If new developments, update last_updated timestamp
4. **Expiration**: After continuing_until date, CONTINUING stories display as standard (severity_score still used for archive sorting)
5. **Manual Override**: Editor can change story_type or severity_score anytime

### Visual Treatment Rules

**NEW Stories:**
- Card size: Standard (300px wide)
- Border: None
- Badge: None (or "NEW" if <24 hours old)
- Sort: publication_date DESC

**CONTINUING Stories (within continuing_until window):**
- Card size based on severity_score:
  - Critical (71-100): 600px wide, 2-column span
  - Significant (31-70): 450px wide, 1.5-column span
  - Standard (0-30): 300px wide, standard
- Border color:
  - Critical: Red (#DC2626)
  - Significant: Orange (#EA580C)
  - Standard: Gray (#6B7280)
- Badge: "ONGOING" or "DEVELOPING"
- Sort: Elevated to top positions despite age

---

## Appendix C: Cost Breakdown

### One-Time Development
- Domain (1 year): $12-15
- GCP setup: $0
- Development: $0 (agent-driven)
- Design/branding: $0-1,500 (if needed)
- **Total: $12-1,515**

### Monthly Operating
- GCP Compute: $20-50
- PostgreSQL: $15-30 (or $0 self-hosted)
- Cloud Storage: $0-10
- Cloudflare CDN: $0
- Domain: $1/month
- Monitoring: $0-10
- Backup storage: $0-5
- APIs: $0-20
- **Total: $36-126/month**

---

## 18. Edge Cases and Error Handling

### 18.1 Content Edge Cases

**No local news available for user's state:**
- Display national news only
- Show message: "Local news for {state} coming soon"
- Suggest user check national news or other states

**Article doesn't fit any category:**
- Default to "Current Affairs"
- Flag for human review

**Reading level check fails (score outside 7.5-8.5):**
- Block publication
- Return to draft with note: "Reading level: {score}, target: 7.5-8.5"
- AI agent rewrites to target level

**All image sources fail:**
- Use placeholder image with newspaper icon
- Flag article for manual image selection
- Publish without blocking (text-only acceptable)

**Story is both time-sensitive and ongoing:**
- Editor decides: Set story_type='CONTINUING' if updates expected
- Use severity_score to indicate urgency

**Non-US IP address:**
- Serve national news only
- No local news displayed
- Do not attempt state inference

**Duplicate article detection:**
- Check headline similarity (Levenshtein distance)
- If >80% similar to existing article, alert editor
- Allow override if intentional update

### 18.2 Technical Edge Cases

**IP geolocation API failure:**
- Cache last successful lookup for 24 hours
- If cache miss and API down: Serve national news
- Log error for investigation

**Gemini API failure:**
- Retry 3 times with exponential backoff
- Fallback to Unsplash API (search: headline keywords)
- If all fail: Use placeholder, flag for manual review

**Database connection failure:**
- Display cached homepage (Redis/static)
- Show error page if no cache
- Alert monitoring system

**LLM API rate limit exceeded:**
- Queue article generation
- Process when rate limit resets
- Notify editor of delay

**Invalid GCP API key:**
- Alert admin immediately
- Disable Gemini integration
- Use Unsplash/Pexels exclusively until resolved

**Cloud Storage upload failure:**
- Retry 3 times
- Store image locally as temp fallback
- Alert admin for manual intervention

### 18.3 User Experience Edge Cases

**User in state with no local news:**
- Show national news
- Display: "We're working on bringing local {state_name} news to you"

**Mobile user with slow connection:**
- Lazy load images below fold
- Show text immediately, load images progressively
- Provide "text-only mode" toggle

**User's preferred state doesn't match IP location:**
- Honor user preference (preferred_state_id takes precedence)
- Allow state override in settings

**Article published mid-read:**
- Do not interrupt reading experience
- Show "New articles available" banner at top
- Refresh on next navigation

---

## 19. User Experience Flows

### 19.1 Anonymous User - National News
```
1. User visits https://dailyworker.com
2. System extracts IP from request
3. IP geolocation lookup (cache check → API call)
4. State inferred (or NULL if non-US/failure)
5. Query: CONTINUING stories + NEW national + NEW local (if state found)
6. Render homepage with mixed layout
7. User clicks article → Read full article
8. User can manually select state via dropdown
```

### 19.2 User Signup and State Selection
```
1. User clicks "Sign Up" (optional, not required for reading)
2. Form: email, password, preferred state
3. State dropdown: All 50 states + DC
4. Submit → Create user record
5. Session stores preferred_state_id
6. Homepage refreshes with personalized local news
```

### 19.3 Article Reading Flow
```
1. User clicks article card on homepage
2. Navigate to /article/{slug}
3. Load article: headline, image, body, metadata
4. Display related articles (same category)
5. Share buttons: Facebook, X, copy link
6. View count increments
```

### 19.4 Editor - Article Approval Flow
```
1. Editor logs in (/admin/login)
2. Dashboard shows editorial_queue (status='human_review')
3. Click article to review
4. Read article, check AI bias report
5. Decision:
   - Approve → Status: approved, schedule publication
   - Request Revision → Add editor_notes, status: revision_requested
   - Reject → Status: rejected
6. Article updated, editor notified
```

### 19.5 Image Selection Flow
```
1. Article created (draft)
2. System checks: is_opinion field
3. IF is_opinion=TRUE:
   - Generate prompt from headline
   - Call Gemini API
   - Upload to Cloud Storage
   - Attach to article
4. ELSE:
   - Search Unsplash API (headline keywords)
   - Present top 5 results to editor
   - Editor selects best fit
   - Store with attribution
5. IF all sources fail:
   - Use placeholder
   - Flag for manual selection
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-29 | Product Team | Complete rewrite for streamlined MVP. Removed all timeline references. Added NEW/CONTINUING story classification. Specified GCP deployment. Added local news with state preferences/IP inference. Clarified imagery sources (reputable + citations for news, Gemini for opinion). Deferred social auto-posting and native apps. Removed traditional metrics, focus on satisfactory utility and quality. Reduced verbosity significantly. |
| 1.1 | 2025-12-29 | Product Team | Added critical development details: Complete database schema with all tables (articles, images, users, states, categories, sources, editorial_queue, social_posts). Front page display algorithm with query logic and card layout specs. IP geolocation implementation (IPinfo.io, state mapping, privacy). Google Gemini API integration (Vertex AI specs, workflow, error handling). Editorial workflow state machine. GCP infrastructure specifications (Cloud Run, Cloud SQL, Cloud Storage, networking, IAM). Edge cases and error handling (18 scenarios). User experience flows (5 complete flows). Document increased from 553 to 1,013 lines with development-ready specifications. |

---

**End of Requirements Document**
