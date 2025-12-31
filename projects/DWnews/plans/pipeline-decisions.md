# Automated Journalism Pipeline - Implementation Decisions

**Date:** 2025-12-31
**Status:** Approved for Implementation

---

## User Decisions on Open Questions

### 1. Editor Availability
**Decision:** 1 hour per day initially
**Rationale:** Until satisfied with output quality
**Impact:** Target 3-5 articles/day for review (12-15 min per article)

### 2. Beat Priorities
**Decision:** Labor, Politics, Economics (as recommended)
**Rationale:** Highest worker relevance
**Implementation:** Prioritize these categories in newsworthiness scoring

### 3. Scope Phasing
**Decision:** National-only first, local + international later
**Details:**
- **Phase 1 (Batch 6):** National U.S. news only
- **Phase 2 (Future):** Local U.S. news (state/city level)
- **Phase 3 (Future):** International - UK launch ("The Daily Worker UK")

**Impact:**
- Simplifies initial implementation
- Remove local/region logic from Batch 6
- Create separate batch for local news capability
- Create separate batch for international expansion

### 4. Revision Limits
**Decision:** Maximum 2 revisions per article
**Action:** After 2 failed revisions, escalate or kill story
**Implementation:** Add revision_count field to articles table

### 5. Social Media Monitoring
**Decision:** Twitter and Reddit only
**Rationale:** Lower API costs, sufficient signal
**APIs Required:**
- Twitter API v2 (free tier: 1,500 tweets/month)
- Reddit API (free: 100 requests/minute)
- RSS feeds (no auth required)

### 6. Source Requirements
**Decision:** ≥3 references for all articles, loosely enforced
**Interpretation:**
- Target 3+ credible sources
- Allow flexibility for breaking news or time-sensitive stories
- Quality of sources more important than quantity
- Enforcement through editorial review, not hard rejection

---

## Implementation Approach

### Testing Strategy
**Decision:** Test workflow locally with LIVE data before cloud deployment

**Requirements:**
1. Real event discovery from Twitter/Reddit/RSS
2. Real article generation from discovered events
3. Complete pipeline validation (discovery → publication)
4. Local execution (no GCP required for testing)

**Success Criteria:**
- Generate 1 complete, publishable article from live data
- Verify each pipeline step works correctly
- Human editor reviews and approves quality
- Identifies any gaps before cloud deployment

---

## API Connectivity Requirements

### Required Immediately (For Local Testing)

#### 1. Twitter API v2
**What we need:**
- Bearer Token OR (API Key + API Secret + Access Token + Access Token Secret)

**How to obtain:**
1. Go to https://developer.twitter.com/
2. Sign up for developer account (free)
3. Create a new app/project
4. Generate API credentials
5. Select "Read" permissions only

**Free Tier Limits:**
- 1,500 tweets/month (50/day)
- Sufficient for testing and initial production

**Cost:** $0 (free tier adequate)

#### 2. Reddit API
**What we need:**
- Client ID
- Client Secret
- User Agent (can be any string, e.g., "DailyWorker/1.0")

**How to obtain:**
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Fill in name: "The Daily Worker"
5. Redirect URI: http://localhost:8080
6. Copy Client ID and Secret

**Free Tier Limits:**
- 100 requests per minute
- More than sufficient

**Cost:** $0

#### 3. RSS Feeds (No Authentication)
**Pre-configured sources:**
- Associated Press
- Reuters
- BBC
- NPR
- ProPublica
- The Guardian
- Al Jazeera
- Labor Notes (worker focus)

**Cost:** $0

---

## Optional (Can Add Later)

### Government Data Sources (No Auth Required)
- NLRB.gov (labor cases)
- DOL.gov (wage/labor statistics)
- BLS.gov (economic data)
- SEC.gov (corporate filings)
- FEC.gov (campaign finance)

### News Aggregators (No Auth Required)
- Google News RSS
- Techmeme
- Hacker News API

---

## Configuration Storage

Credentials will be stored in:
```
/Users/home/sandbox/daily_worker/projects/DWnews/.env.local
```

**Format:**
```env
# Twitter API v2
TWITTER_BEARER_TOKEN=your_bearer_token_here
# OR (if using OAuth 1.0a)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DailyWorker/1.0

# LLM APIs (already configured or user-provided)
CLAUDE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

**Security:**
- File added to .gitignore
- Never committed to repository
- Loaded via python-dotenv

---

## Local Testing Workflow

### Phase 1: Manual Testing (This Session)
1. User provides Twitter + Reddit credentials
2. Run signal_intake_test.py
3. Discover 10-20 events from live feeds
4. Manually select 1 interesting event
5. Run verification_test.py on that event
6. Run article_generation_test.py
7. Human reviews generated article
8. Iterate if needed

### Phase 2: Automated Testing (Next Session)
1. Run full pipeline end-to-end
2. Discover → Score → Verify → Draft → Review
3. Test with 5-10 events
4. Validate quality gates work
5. Measure processing time
6. Identify bottlenecks

### Phase 3: Production Deployment (Future Batch)
1. Deploy to GCP Cloud Functions
2. Set up Cloud Scheduler (daily cron)
3. Integrate with admin portal
4. Monitor for 1 week
5. Adjust thresholds based on results

---

## Next Steps

### Immediate Actions
1. **User provides:** Twitter + Reddit API credentials
2. **We create:** Local test scripts for each pipeline step
3. **We run:** First live test with real data
4. **User reviews:** Generated test article
5. **We iterate:** Based on feedback

### After Successful Test
1. Update Batch 6 phases based on learnings
2. Remove local news logic (deferred to later batch)
3. Add UK expansion as future batch (Batch 10+)
4. Begin Phase 6.1: Database Schema Extensions

---

## Deferred to Future Batches

### Local News Capability (New Batch 7)
- Region detection
- State/city-specific feeds
- Local source verification
- Geolocation logic

### International Expansion - UK (New Batch 10+)
- UK-specific news sources
- British English style
- UK labor law context
- Separate deployment/domain
- Currency/measurement conversions

### Original Infrastructure Batches
- GCP Infrastructure (now Batch 8)
- Cloud Operations (now Batch 9)
- Production Launch (now Batch 10)

---

## Success Metrics (Updated)

### For Local Testing
- **Signal Quality:** 10-20 newsworthy events discovered per test
- **Source Coverage:** ≥3 sources found for 70%+ of events
- **Draft Quality:** 80%+ of drafted articles pass 10-point self-audit
- **Editorial Approval:** 60%+ of articles approved by human editor (after 2 revisions if needed)

### For Production (Daily)
- **Articles Published:** 3-5 per day (within 1-hour editorial window)
- **Quality Score:** 85%+ pass all quality gates
- **Correction Rate:** <5% require corrections post-publication
- **Cost:** <$50/month (within budget)

---

## Risk Mitigation

### API Rate Limits
- **Risk:** Exceed free tier limits
- **Mitigation:** Cache results, implement rate limiting, monitor usage
- **Escalation:** Upgrade to paid tier only if necessary (Twitter Basic: $100/month)

### Quality Failures
- **Risk:** Too many articles fail editorial review
- **Mitigation:** Adjust newsworthiness thresholds, improve self-audit prompts
- **Escalation:** Reduce daily target (3-5 → 1-2 until quality improves)

### Source Verification Gaps
- **Risk:** Unable to find ≥3 sources for many topics
- **Mitigation:** Expand source list, improve search strategies
- **Escalation:** Accept 2 sources temporarily for high-importance events

---

## Document History

- **2025-12-31:** Initial decisions documented
- **Next Update:** After first successful local test with live data
