# Social Media Investigation Module (Phase 6.9.2)

## Overview

This module implements deep social media investigation capabilities for the Investigatory Journalist Agent. It extends Phase 1's core investigation with specialized social media research tools.

## Features

### 1. Twitter Investigation Monitor
**File:** `twitter_investigation.py`

Extended Twitter search and analysis:
- **Extended Search**: Multi-query search with date filtering
- **Hashtag Tracking**: Find all mentions of specific hashtags
- **Original Tweet Filtering**: Exclude retweets and replies for original content
- **Verified Account Filtering**: Prioritize verified sources
- **Timeline Construction**: Build chronological event timelines

**Usage:**
```python
from backend.agents.investigation.twitter_investigation import TwitterInvestigationMonitor

monitor = TwitterInvestigationMonitor(use_mock_data=True)
results = monitor.search_extended("Amazon workers strike", max_results=50)
timeline = monitor.construct_timeline(results)
```

### 2. Reddit Investigation Monitor
**File:** `reddit_investigation.py`

Extended Reddit search and analysis:
- **Extended Search**: Multi-subreddit search
- **Discussion Thread Analysis**: Analyze comment quality and sentiment
- **Eyewitness Identification**: Find firsthand reports
- **Original Content Filtering**: Prioritize OC over news links
- **Timeline Construction**: Build event timelines from posts

**Usage:**
```python
from backend.agents.investigation.reddit_investigation import RedditInvestigationMonitor

monitor = RedditInvestigationMonitor(use_mock_data=True)
results = monitor.search_extended("strike", subreddits=['labor', 'WorkReform'])
eyewitness = monitor.identify_eyewitness_accounts(results)
```

### 3. Social Source Credibility Scorer
**File:** `social_credibility.py`

Scores social media sources for credibility:

**Twitter Scoring (0-100):**
- Verification status: 20 points
- Account age: 0-30 points
- Follower count: 0-30 points
- Has description: 10 points

**Reddit Scoring (0-100):**
- Account exists: 20 points
- Account age: 0-30 points
- Combined karma: 0-40 points

**Engagement Scoring:**
- High engagement = higher visibility/scrutiny

**Usage:**
```python
from backend.agents.investigation.social_credibility import SocialSourceCredibility

scorer = SocialSourceCredibility()
twitter_account = {
    'platform': 'twitter',
    'username': 'reuters',
    'verified': True,
    'followers_count': 28000000
}
score = scorer.score_source(twitter_account)  # Returns ~90/100
```

### 4. Timeline Constructor
**File:** `timeline_constructor.py`

Constructs chronological timelines from social media:
- **Chronological Sorting**: Sort events by timestamp
- **Event Clustering**: Group related events within time windows
- **Key Moment Identification**: Find significant events (>70 significance score)
- **Duration Calculation**: Calculate event timespan

**Usage:**
```python
from backend.agents.investigation.timeline_constructor import TimelineConstructor

constructor = TimelineConstructor()
timeline = constructor.construct_timeline(mixed_sources)
clusters = constructor.cluster_related_events(timeline['events'])
key_moments = constructor.identify_key_moments(timeline)
```

### 5. Eyewitness Detector
**File:** `eyewitness_detector.py`

Identifies firsthand eyewitness accounts:

**Detection Patterns:**
- Firsthand language: "I was there", "I saw", "I witnessed"
- Participation language: "I work", "we organized"
- Direct observation: "just saw", "happening now"
- Present tense: "currently", "as we speak"

**Confidence Levels:**
- 95%: 3+ pattern matches
- 85%: 2 pattern matches
- 70%: 1 pattern match

**Usage:**
```python
from backend.agents.investigation.eyewitness_detector import EyewitnessDetector

detector = EyewitnessDetector()
detection = detector.detect_firsthand_language("I was there when workers walked out")
# Returns: {'is_firsthand': True, 'confidence': 70.0, 'indicators': [...]}
```

## Integration with Investigatory Journalist Agent

The social media investigation is automatically integrated when enabled:

```python
from backend.agents.investigatory_journalist_agent import InvestigatoryJournalistAgent
from backend.database import SessionLocal

db = SessionLocal()
agent = InvestigatoryJournalistAgent(db, enable_social_media=True)

result = agent.investigate(topic_id=123)

if result and result.social_media_findings:
    print(f"Twitter posts: {result.social_media_findings.twitter_post_count}")
    print(f"Reddit posts: {result.social_media_findings.reddit_post_count}")
    print(f"Eyewitness accounts: {len(result.social_media_findings.eyewitness_accounts)}")
    print(f"Timeline events: {len(result.social_media_findings.timeline_events)}")
    print(f"Social credibility: {result.social_media_findings.social_credibility_score}/100")
```

## Investigation Workflow

When investigating an unverified topic, the agent now follows a 6-step process:

1. **Multi-engine web search** (Phase 1)
2. **Origin tracing** (Phase 1)
3. **Cross-reference validation** (Phase 1)
4. **Verification upgrade** (Phase 1)
5. **Social media investigation** (Phase 2 - NEW)
   - Search Twitter for mentions
   - Search Reddit for discussions
   - Identify eyewitness accounts
   - Construct event timeline
   - Calculate social credibility
6. **Final analysis and recommendation**

## Data Models

### SocialMediaFindings
```python
@dataclass
class SocialMediaFindings:
    twitter_post_count: int = 0
    reddit_post_count: int = 0
    eyewitness_accounts: List[Dict] = []
    timeline_events: List[Dict] = []
    social_credibility_score: float = 0.0
```

### InvestigationResult (Updated)
```python
@dataclass
class InvestigationResult:
    # Phase 1 fields...

    # Phase 2: Social media findings
    social_media_findings: Optional[SocialMediaFindings] = None
```

## Testing

Run the comprehensive test suite:

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 scripts/test_social_media_investigation.py
```

**Test Coverage:**
- TwitterInvestigationMonitor: Extended search, hashtag tracking, filtering, timeline construction
- RedditInvestigationMonitor: Extended search, thread analysis, eyewitness detection, filtering
- SocialSourceCredibility: Twitter/Reddit account scoring, engagement metrics, combined scoring
- TimelineConstructor: Timeline construction, event clustering, key moment identification
- EyewitnessDetector: Language detection, account identification, credibility validation
- Integration: Full integration with InvestigatoryJournalistAgent

## Configuration

### Twitter API v2
Set environment variables:
```bash
export TWITTER_BEARER_TOKEN="your_bearer_token"
```

Or the module will use mock data for testing.

### Reddit API
Set environment variables:
```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="DWnews/1.0"
```

Or the module will use mock data for testing.

## Mock Data Mode

All modules support mock data mode for testing without API credentials:

```python
# Twitter with mock data
twitter_monitor = TwitterInvestigationMonitor(use_mock_data=True)

# Reddit with mock data
reddit_monitor = RedditInvestigationMonitor(use_mock_data=True)
```

Mock data provides realistic test scenarios without requiring API access.

## Performance

**Target Metrics:**
- Investigation time: 2-5 minutes per topic
- Social media search: <30 seconds per platform
- Eyewitness detection: <10 seconds
- Timeline construction: <5 seconds
- Total Phase 2 overhead: ~1-2 minutes

**Cost:**
- Twitter API v2: Free tier (500K tweets/month)
- Reddit API: Free tier (60 requests/min)
- Total Phase 2 cost: $0/month (using free tiers)

## Future Enhancements (Phase 3-4)

### Phase 3: Deep Context Research
- Historical event research
- Key actor profiling
- Local news source aggregation
- Geographic context gathering

### Phase 4: Advanced Analysis
- Claim extraction using LLM
- Automated fact-checking per claim
- Contradiction detection
- Bias analysis
- Human review flagging

## Files Structure

```
backend/agents/investigation/
├── __init__.py                    # Module exports
├── twitter_investigation.py       # Twitter extended search
├── reddit_investigation.py        # Reddit extended search
├── social_credibility.py          # Source credibility scoring
├── timeline_constructor.py        # Timeline construction
├── eyewitness_detector.py         # Eyewitness identification
└── README.md                      # This file
```

## Success Criteria

Phase 6.9.2 is complete when:
- ✅ Twitter API v2 extended search implemented
- ✅ Reddit API extended search implemented
- ✅ Social source credibility scoring operational
- ✅ Timeline construction from social mentions working
- ✅ Eyewitness account identification functional
- ✅ All tests passing (6/6 tests)
- ✅ Integration with InvestigatoryJournalistAgent complete
- ✅ Documentation complete

## Contact

For questions or issues with the social media investigation module, see the main project documentation or raise an issue in the project repository.

## License

Part of The Daily Worker project. See main project LICENSE file.
