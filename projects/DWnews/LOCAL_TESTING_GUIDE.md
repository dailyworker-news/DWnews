# Local Testing Guide - Automated Journalism Pipeline

**Status:** Ready for API credentials and testing
**Date:** 2025-12-31
**Purpose:** Test the complete journalism pipeline with live data before cloud deployment

---

## Prerequisites

### 1. API Credentials Required

You need to obtain credentials for:

1. **Twitter API v2** - For monitoring labor-related tweets
2. **Reddit API** - For discovering worker stories and discussions
3. **LLM API** (Optional) - Claude, OpenAI, or Google Gemini

**See `API_CREDENTIALS_SETUP.md` for step-by-step instructions.**

### 2. Configuration File

Create `.env.local` in the project root with your credentials:

```env
# Twitter API v2
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DailyWorker/1.0 (by /u/your_username)

# LLM API (Optional - choose one)
CLAUDE_API_KEY=sk-ant-your_key_here
# OR
OPENAI_API_KEY=sk-your_key_here
# OR
GOOGLE_API_KEY=AIzaSy_your_key_here
```

**Template available at:** `/tmp/credentials_template.env`

---

## Testing Workflow

### Step 1: Install Dependencies

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
pip install -r backend/requirements.txt
```

All required libraries are included:
- ✅ `requests` - HTTP client
- ✅ `feedparser` - RSS parsing
- ✅ `tweepy` - Twitter API (alternative client)
- ✅ `praw` - Reddit API (alternative client)
- ✅ `anthropic` - Claude API
- ✅ `openai` - OpenAI API
- ✅ `google-generativeai` - Google Gemini API

### Step 2: Verify API Connections

Test that all API credentials work correctly:

```bash
python scripts/test_api_connections.py
```

**Expected output:**
```
✅ Twitter API connection successful
✅ Reddit API connection successful
✅ RSS Feeds: All feeds accessible
✅ LLM API connection successful (optional)

🎉 ALL REQUIRED API CONNECTIONS SUCCESSFUL!
```

**What this tests:**
- Twitter: Fetches 10 tweets about "labor unions"
- Reddit: Fetches 10 posts from r/antiwork
- RSS: Fetches latest from Labor Notes, ProPublica, Reuters
- LLM: Sends test prompt to configured API

### Step 3: Discover Live Events

Run signal intake to discover newsworthy events:

```bash
python scripts/test_signal_intake.py
```

**Expected output:**
```
TOTAL SIGNALS DISCOVERED: 60-90
  Twitter: 30 tweets
  Reddit: 30 posts
  RSS: 30 articles

TOP 15 NEWSWORTHY SIGNALS
[1] Score: 0.85 | Worker Relevance: 0.92 | Source: Twitter
    @labororganizer ✓
    Breaking: 500 workers at Amazon warehouse vote to unionize...
    Engagement: 1,245 likes, 423 retweets

[2] Score: 0.82 | Worker Relevance: 0.88 | Source: Reddit
    r/antiwork by u/worker123
    Our entire department walked out today after company cut benefits
    Engagement: 3,421 upvotes, 892 comments

[3] Score: 0.79 | Worker Relevance: 0.95 | Source: RSS
    Labor Notes (labor_focused)
    Teamsters Win Major Contract After 3-Week Strike
    Link: https://labornotes.org/...
```

**What this does:**
- Monitors Twitter for labor keywords (union, strike, organizing, etc.)
- Checks Reddit communities (r/antiwork, r/WorkReform, r/union)
- Fetches RSS from Labor Notes, ProPublica, Reuters, AP
- Scores each signal for worker relevance and engagement
- Ranks by newsworthiness score
- Saves all signals to `test_output/discovered_signals_[timestamp].json`

### Step 4: Select Event for Testing

Review the top 15 signals and select 1 interesting event to test the full article generation pipeline.

**Selection criteria:**
- High newsworthiness score (>0.70)
- Multiple sources available
- Clear labor/worker angle
- Recent (within 24-48 hours)

**Example:**
"I'd like to test signal #3 - the Teamsters strike story from Labor Notes"

### Step 5: Generate Test Article

(Script to be created next)

```bash
python scripts/test_article_generation.py --signal 3
```

**This will:**
1. Extract event details from selected signal
2. Search for ≥3 credible sources
3. Verify facts across sources
4. Generate article following journalism standards
5. Run 10-point self-audit
6. Display article for editorial review

### Step 6: Editorial Review

Review the generated article and provide feedback:

**Quality checklist:**
- ✅ Inverted pyramid structure
- ✅ 5W+H answered in first 3 paragraphs
- ✅ Proper attribution to sources
- ✅ Nut graf explains why this matters
- ✅ Functional quotes add perspective
- ✅ Neutral narration tone
- ✅ Facts separated from analysis
- ✅ Reading level 7.5-8.5
- ✅ Worker-centric perspective maintained

**Possible outcomes:**
1. **Approve** → Article ready for publication
2. **Revise** → Request specific changes (max 2 revisions)
3. **Kill** → Story not viable, move to next signal

---

## Test Output Locations

All test outputs are saved to `test_output/` directory:

```
test_output/
├── discovered_signals_20251231_143022.json  # All discovered signals
├── selected_event_003.json                   # Selected event details
├── verified_sources_003.json                 # Source verification results
└── generated_article_003.md                  # Draft article
```

---

## Success Criteria

### For Signal Intake Test
- ✅ Discover 60+ signals from all sources
- ✅ At least 10 signals with newsworthiness score >0.70
- ✅ Mix of sources (Twitter, Reddit, RSS)
- ✅ Clear worker relevance for top signals

### For Article Generation Test
- ✅ Find ≥3 credible sources for selected event
- ✅ Generate article following all journalism standards
- ✅ Pass 10-point self-audit (score ≥8/10)
- ✅ Reading level within 7.5-8.5 range
- ✅ Human editor approves (within 2 revisions)

---

## Troubleshooting

### API Connection Failures

**Twitter 429 Error (Rate Limited):**
- Free tier: 1,500 tweets/month (~50/day)
- Wait 15 minutes and try again
- Reduce keyword count in test

**Reddit 401 Error (Unauthorized):**
- Check client ID and secret are correct
- Verify user agent format: `AppName/Version (by /u/username)`
- Regenerate credentials if needed

**RSS Feed Timeout:**
- Some feeds may be temporarily down
- Test will continue with available feeds
- Try again later if all feeds fail

### No High-Scoring Signals

If all signals score <0.50:
- Labor keywords may not match current events
- Try expanding to broader keywords (worker, employee, job)
- Check different subreddits (r/politics, r/news)
- RSS feeds may have non-labor content today

### Article Generation Issues

If article quality is poor:
- Event may lack sufficient sources
- Try different signal with more mainstream coverage
- Check LLM API is working correctly
- Review journalism standards prompt

---

## Cost Tracking

### During Testing (Single Test Run)
- **Twitter:** $0 (free tier)
- **Reddit:** $0 (free tier)
- **RSS:** $0 (always free)
- **LLM:** ~$0.10-0.50 per article (depends on API)

**Total per test:** ~$0.10-0.50

### Daily Production Estimates
- **APIs:** $0 (under free tier limits)
- **LLM:** ~$1.50-2.00/day (3-5 articles)
- **Monthly:** ~$45-60

**Within budget target:** ✅ $30-100/month

---

## Next Steps After Successful Test

1. ✅ Validate pipeline works end-to-end
2. ✅ Identify any quality issues
3. ✅ Refine prompts if needed
4. Begin Batch 6 implementation:
   - Phase 6.1: Database Schema Extensions
   - Phase 6.2: Signal Intake Agent
   - Phase 6.3: Evaluation Agent
   - Phase 6.4: Verification Agent
   - Phase 6.5: Enhanced Journalist Agent
   - Phase 6.6: Editorial Workflow Integration
   - Phase 6.7: Publication & Monitoring
   - Phase 6.8: Local Testing & Integration

---

## Support

**Issues with credentials:**
See `API_CREDENTIALS_SETUP.md` for detailed instructions

**Issues with testing:**
Check test script output for specific error messages

**Architecture questions:**
See `plans/automated-journalism-analysis.md` for full pipeline design

**Requirements questions:**
See `plans/pipeline-decisions.md` for approved decisions
