# Monitoring Agent

**Agent Type:** Post-Publication Monitoring & Quality Control

**Purpose:** Monitor published articles for 7 days post-publication to track social mentions, detect correction needs, and update source reliability scores.

## Overview

The Monitoring Agent is the final agent in the automated journalism pipeline (Batch 6). It ensures published articles maintain accuracy by monitoring social media feedback, detecting when corrections are needed, and learning from real-world performance to improve source reliability scoring.

## Core Responsibilities

### 1. Social Mention Tracking
- **Twitter Monitoring:** Track mentions of article URLs and titles using Twitter API v2
- **Reddit Monitoring:** Track submissions and discussions using Reddit API (PRAW)
- **Engagement Metrics:** Collect retweets, likes, comments, upvotes, etc.
- **Duration:** Monitor for 7 days post-publication
- **Output:** Social mention logs for analytics and engagement tracking

### 2. Correction Detection
- **Source Retraction Monitoring:** Check if original sources issue corrections/retractions
- **Social Feedback Analysis:** Monitor social mentions for factual disputes
- **Flagging Workflow:** Create correction candidates in `corrections` table
- **Editor Notification:** Alert editors to potential accuracy issues within 24 hours
- **Severity Classification:** Categorize corrections as minor, moderate, major, or critical

### 3. Source Reliability Updates
- **Accuracy Confirmation:** Award +5 points to sources when articles remain accurate for 7 days
- **Correction Penalty:** Deduct -10 points when source requires correction
- **Retraction Penalty:** Deduct -30 points for complete retractions
- **Learning Loop:** Update `source_reliability_log` table to inform future verification
- **Score Range:** Maintain scores on 0-100 scale, mapped to 1-5 credibility score

## Technical Implementation

### Location
- **Main Agent:** `/Users/home/sandbox/daily_worker/projects/DWnews/backend/agents/monitoring_agent.py`
- **Publication Agent:** `/Users/home/sandbox/daily_worker/projects/DWnews/backend/agents/publication_agent.py`
- **Correction Workflow:** `/Users/home/sandbox/daily_worker/projects/DWnews/backend/agents/correction_workflow.py`
- **Source Reliability:** `/Users/home/sandbox/daily_worker/projects/DWnews/backend/agents/source_reliability.py`
- **API Routes:** `/Users/home/sandbox/daily_worker/projects/DWnews/backend/routes/monitoring.py`

### Database Tables Used
- **articles:** Track published_at timestamp, status
- **corrections:** Store correction notices (status: pending, verified, published, rejected)
- **source_reliability_log:** Log source performance events
- **sources:** Update credibility_score based on performance

### Dependencies
- **Twitter API:** `tweepy` library (requires TWITTER_BEARER_TOKEN)
- **Reddit API:** `praw` library (requires REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
- **Schedule:** Daily monitoring cron job or triggered post-publication

## Monitoring Schedule

### Daily Monitoring
```bash
# Run monitoring agent daily (suggested cron: 9am daily)
cd /Users/home/sandbox/daily_worker/projects/DWnews
python -m backend.agents.monitoring_agent
```

### Publication Trigger
```python
# Auto-publish approved articles (suggested cron: 5pm daily)
from backend.agents.publication_agent import PublicationAgent
agent = PublicationAgent(session)
results = agent.publish_approved_articles()
```

### 7-Day Monitoring Window
- Articles published within last 7 days are actively monitored
- After 7 days, final source reliability scores are calculated
- Monitoring stops unless correction workflow is active

## Correction Workflow

### 1. Flag Correction
```python
from backend.agents.correction_workflow import CorrectionWorkflow

workflow = CorrectionWorkflow(session)
correction = workflow.flag_correction(
    article_id=123,
    correction_type='factual_error',
    incorrect_text='Amazon warehouse had 100 workers',
    correct_text='Amazon warehouse had 150 workers',
    description='Source updated with official count',
    severity='moderate',
    section_affected='body',
    reported_by='monitoring_agent'
)
```

### 2. Editor Review
```python
# Approve correction
workflow.review_correction(
    correction_id=correction.id,
    action='approve',
    reviewer='editor_username',
    notes='Verified with official statement'
)
```

### 3. Publish Correction
```python
# Publish correction notice
workflow.publish_correction(
    correction_id=correction.id,
    public_notice='An earlier version of this article stated the warehouse had 100 workers. The official count is 150 workers.',
    editor='editor_username'
)

# Optionally update article content
workflow.apply_correction_to_article(
    correction_id=correction.id,
    update_content=True
)
```

### 4. Display on Frontend
- Correction notices display at top of article (above headline)
- Yellow warning banner with clear formatting
- Shows: correction date, type, original text, corrected text, reason
- CSS classes: `.correction-notice`, `.correction-item`, `.correction-{severity}`

## Source Reliability Scoring

### Scoring Logic
```python
from backend.agents.source_reliability import SourceReliabilityScorer

scorer = SourceReliabilityScorer(session)

# Log accuracy confirmation (after 7 days)
scorer.log_event(
    source_id=source.id,
    event_type='accuracy_confirmed',
    article_id=article.id,
    notes='Article verified accurate for 7 days',
    automated=True
)

# Log correction event
scorer.log_event(
    source_id=source.id,
    event_type='correction_issued',
    article_id=article.id,
    correction_id=correction.id,
    notes='Source required correction',
    automated=True
)
```

### Score Deltas
- **accuracy_confirmed:** +5 points
- **minor_correction:** -5 points
- **correction_issued:** -10 points
- **retraction:** -30 points
- **fact_check_pass:** +3 points
- **fact_check_fail:** -8 points

### Score Mapping
- **95-100:** Credibility Score 5 (Tier 1 - Wire services)
- **82-94:** Credibility Score 4 (Tier 2 - Regional news)
- **67-81:** Credibility Score 3 (Tier 3 - Online outlets)
- **50-66:** Credibility Score 2 (Tier 4 - Blogs)
- **0-49:** Credibility Score 1 (Tier 5 - Social media)

## API Endpoints

### Social Mentions
```bash
# Get social mentions for article
GET /api/monitoring/mentions/<article_id>

Response:
{
  "article_id": 123,
  "article_title": "Amazon Workers Strike",
  "total_mentions": 15,
  "mentions": [
    {
      "platform": "twitter",
      "mention_type": "url",
      "url": "https://twitter.com/i/web/status/123",
      "created_at": "2025-01-01T10:00:00",
      "engagement": {
        "retweets": 45,
        "likes": 128,
        "replies": 12
      }
    }
  ]
}
```

### Corrections
```bash
# Get pending corrections
GET /api/monitoring/corrections/pending
Requires: Authentication

# Flag new correction
POST /api/monitoring/corrections/flag
Body: {
  "article_id": 123,
  "correction_type": "factual_error",
  "incorrect_text": "...",
  "correct_text": "...",
  "description": "...",
  "severity": "moderate"
}

# Review correction
POST /api/monitoring/corrections/<id>/review
Body: {
  "action": "approve",
  "reviewer": "editor_username",
  "notes": "Verified with source"
}

# Publish correction
POST /api/monitoring/corrections/<id>/publish
Body: {
  "public_notice": "Correction notice text",
  "editor": "editor_username",
  "update_content": true
}
```

### Source Reliability
```bash
# Get source stats
GET /api/monitoring/sources/<source_id>/stats

Response:
{
  "source_id": 5,
  "source_name": "The New York Times",
  "current_score": 95,
  "credibility_score": 5,
  "articles_citing": 42,
  "total_events": 15,
  "event_counts": {
    "accuracy_confirmed": 12,
    "correction_issued": 2,
    "fact_check_pass": 1
  }
}

# Get source history
GET /api/monitoring/sources/<source_id>/history?limit=50

# Get reliability trends
GET /api/monitoring/sources/trends
```

## Testing

### Test Script
```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python scripts/test_monitoring.py
```

### Test Scenarios
1. **Publication Test:** Create approved article → publish → verify status change
2. **Social Mention Test:** Mock Twitter/Reddit mentions → verify tracking
3. **Correction Workflow:** Flag correction → review → publish → verify display
4. **Source Reliability:** Publish article → wait 7 days (simulated) → verify score update

## Configuration

### Environment Variables
```bash
# Twitter API (optional, for social mention tracking)
TWITTER_BEARER_TOKEN=your_bearer_token

# Reddit API (optional, for social mention tracking)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DWnews Monitoring Agent v1.0
```

### Monitoring Settings
- **Monitoring Period:** 7 days (configurable in MonitoringAgent.MONITORING_PERIOD)
- **Score Deltas:** Defined in SourceReliabilityScorer.SCORE_DELTAS
- **Tier Scores:** Defined in SourceReliabilityScorer.TIER_SCORES

## Quality Standards

### Publishing Requirements
- Only `status='approved'` articles can be published
- Published articles cannot be un-published (use correction workflow)
- Publication timestamp recorded accurately

### Monitoring Standards
- Monitor for 7 days post-publication
- Check social mentions daily
- Flag corrections within 24 hours of detection
- Update source reliability scores within 48 hours

### Correction Standards
- All corrections must be editor-approved (no auto-corrections)
- Correction notices prominently displayed at top of article
- Original text preserved for transparency
- Reason for correction clearly stated
- Severity classified appropriately

## Operational Notes

### Manual Social Media Posting (MVP)
For MVP, social media posting is manual. Agent logs publication but does not auto-post.

Future enhancement would implement:
```python
# Twitter posting
def post_to_twitter(article):
    client = tweepy.Client(...)
    tweet_text = f"{article.title}\n\n{article.url}"
    response = client.create_tweet(text=tweet_text)
    return response.data['id']

# Reddit posting
def post_to_reddit(article):
    reddit = praw.Reddit(...)
    submission = reddit.subreddit('news').submit(
        title=article.title,
        url=article.url
    )
    return submission.url
```

### Error Handling
- Social API failures should not block monitoring
- Correction detection errors logged but don't halt workflow
- Source reliability updates are idempotent (safe to retry)

### Monitoring Metrics
- Track monitoring coverage (% of published articles monitored)
- Track correction rate (% of articles requiring corrections)
- Track average source reliability by tier
- Track social engagement trends

## Integration with Pipeline

### Position in Batch 6
The Monitoring Agent is **Phase 6.7** (final phase) in Batch 6: Editorial Workflow & Publication.

**Batch 6 Flow:**
1. Phase 6.1: Database schema (corrections, source_reliability_log)
2. Phase 6.2: Social media APIs (Twitter, Reddit)
3. Phase 6.3: Journalist agent enhancements
4. Phase 6.4: Source verification improvements
5. Phase 6.5: Editorial workflow
6. Phase 6.6: Email notifications
7. **Phase 6.7: Publication & Monitoring** ← THIS AGENT

### Dependencies
- **Requires:** Published articles (from editorial workflow)
- **Provides:** Correction notices, source reliability data
- **Triggers:** Publication agent (daily at 5pm)
- **Schedule:** Monitoring agent (daily at 9am)

### Next Steps
After Phase 6.7, the automated journalism pipeline is complete:
- Signal intake → Evaluation → Verification → Article generation → Editorial review → Publication → Monitoring

Future enhancements:
- AI-powered factual dispute detection from social feedback
- Automated source re-checking (fetch original URLs, compare content)
- Real-time correction flagging (webhook from social APIs)
- Analytics dashboard for monitoring metrics

## Success Criteria

**Phase 6.7 Complete When:**
- ✅ Publication Agent operational (auto-publishes approved articles)
- ✅ Monitoring Agent tracking social mentions for 7 days
- ✅ Correction workflow functional (flag → review → publish)
- ✅ Correction notices displaying on frontend
- ✅ Source reliability scoring updating in database
- ✅ Test suite passing (publication → monitoring → correction)
- ✅ Agent definition documented

## Files Created

1. `/backend/agents/publication_agent.py` - Auto-publish approved articles
2. `/backend/agents/monitoring_agent.py` - 7-day monitoring system
3. `/backend/agents/correction_workflow.py` - Correction management
4. `/backend/agents/source_reliability.py` - Source scoring system
5. `/backend/routes/monitoring.py` - Monitoring API endpoints
6. `/frontend/article.html` - Correction notice display (updated)
7. `/frontend/scripts/article.js` - Correction loading logic (updated)
8. `/frontend/styles/article.css` - Correction styling (updated)
9. `/.claude/agents/monitoring.md` - This agent definition
10. `/scripts/test_monitoring.py` - Test suite

## Contact

For questions about the Monitoring Agent, refer to:
- **Roadmap:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/roadmap.md`
- **Requirements:** `/Users/home/sandbox/daily_worker/projects/DWnews/plans/requirements.md`
- **Database Models:** `/Users/home/sandbox/daily_worker/projects/DWnews/database/models.py`
