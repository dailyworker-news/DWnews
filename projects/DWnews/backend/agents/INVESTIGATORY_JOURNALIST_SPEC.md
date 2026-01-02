# Investigatory Journalist Agent - Technical Specification

**Version:** 1.0
**Status:** Draft
**Created:** 2026-01-02
**Purpose:** Deep research agent for verifying articles when standard fact-checking fails

---

## Overview

The Investigatory Journalist Agent is a specialized research agent that conducts deep investigations into article origins, source credibility, and event legitimacy when the standard Verification Agent cannot find sufficient sources (unverified status).

### Key Responsibilities

1. **Origin Research** - Trace articles back to their original source
2. **Deep Source Discovery** - Find sources using multiple search strategies beyond standard WebSearch
3. **Credibility Assessment** - Evaluate source authority and reliability
4. **Context Gathering** - Build historical and situational context around events
5. **Verification Upgrade** - Attempt to upgrade "unverified" articles to "verified" or "certified"

---

## Architecture

### Agent Position in Pipeline

```
Signal Intake → Evaluation → Verification Agent
                                    ↓
                           [0-2 sources found]
                                    ↓
                         Investigatory Journalist ← (This agent)
                                    ↓
                         [Re-assessment of verification level]
                                    ↓
                         Enhanced Journalist Agent → Publication
```

### Integration Points

- **Triggered By:** Verification Agent when source_count < 3
- **Works With:** Verification Agent (provides additional sources)
- **Updates:** Topic.source_plan, Topic.verified_facts, Topic.verification_status
- **Outputs To:** Enhanced Journalist Agent (enriched source material)

---

## Core Capabilities

### 1. Multi-Engine Search Strategy

**Objective:** Find sources that single WebSearch queries miss

**Methods:**
- **Primary Search Engines**
  - Google Search (via WebSearch)
  - DuckDuckGo (privacy-focused alternative)
  - Bing Search

- **Specialized Search**
  - News aggregators (Google News, Bing News)
  - Academic search (Google Scholar via CrossRef API)
  - Social media search (Twitter API v2, Reddit API)
  - Archived content (Wayback Machine API)

- **Query Strategies**
  - Exact phrase matching
  - Date-range filtering
  - Domain-specific searches
  - Related keyword expansion

**Implementation:**
```python
class MultiEngineSearcher:
    def search_all_engines(self, query: str, date_range: Optional[tuple]) -> List[SearchResult]:
        """Search across multiple engines and aggregate results"""

    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate URLs and near-duplicate content"""

    def rank_by_relevance(self, results: List[SearchResult], topic: Topic) -> List[SearchResult]:
        """Score results by relevance to topic"""
```

---

### 2. Social Media Investigation

**Objective:** Find grassroots evidence and eyewitness accounts

**Twitter Investigation:**
- Search hashtags related to event
- Find original tweets about event
- Identify verified accounts discussing event
- Build timeline of mentions
- Assess engagement patterns (retweets, replies)

**Reddit Investigation:**
- Search relevant subreddits (r/labor, r/news, r/politics)
- Find discussion threads
- Identify community reactions
- Check for local/eyewitness accounts
- Verify poster credibility (account age, karma, history)

**Implementation:**
```python
class SocialMediaInvestigator:
    def investigate_twitter(self, topic: Topic) -> Dict:
        """Search Twitter for mentions, original sources, verified accounts"""

    def investigate_reddit(self, topic: Topic) -> Dict:
        """Search Reddit for discussions, local reports, community reaction"""

    def assess_social_credibility(self, social_sources: List) -> float:
        """Score credibility of social media sources (0-100)"""
```

---

### 3. Origin Tracing

**Objective:** Find the original source that first reported the event

**Methods:**

1. **Reverse Chronological Search**
   - Search with date filters, starting from event_date backwards
   - Identify earliest mention of event
   - Map propagation through news cycle

2. **Source Attribution Analysis**
   - Parse articles for "according to..." references
   - Extract cited sources
   - Follow citation chains back to origin

3. **Domain Authority Check**
   - Identify if original source is credible
   - Check domain age, reputation, bias ratings
   - Verify if source specializes in this topic area

**Implementation:**
```python
class OriginTracer:
    def find_earliest_mention(self, topic: Topic) -> Optional[Source]:
        """Find the earliest credible mention of event"""

    def trace_citation_chain(self, article_url: str) -> List[Source]:
        """Follow 'according to' references to find original source"""

    def verify_origin_credibility(self, source: Source) -> CredibilityReport:
        """Assess if origin source is credible"""
```

---

### 4. Historical Context Research

**Objective:** Understand event within broader context

**Research Areas:**

1. **Related Events**
   - Find similar events in past (e.g., previous union strikes at same company)
   - Identify patterns and precedents
   - Build historical timeline

2. **Key Actors**
   - Research organizations involved (unions, companies)
   - Find their previous public statements
   - Check their track record

3. **Geographic Context**
   - Local news sources for area where event occurred
   - Regional political/economic factors
   - Community history

**Implementation:**
```python
class ContextResearcher:
    def find_related_events(self, topic: Topic) -> List[Event]:
        """Find similar historical events"""

    def research_key_actors(self, entities: List[str]) -> Dict[str, ActorProfile]:
        """Build profiles of involved organizations/people"""

    def gather_local_context(self, location: str) -> LocalContext:
        """Research local conditions, news, politics"""
```

---

### 5. Cross-Reference Validation

**Objective:** Validate event details across multiple independent sources

**Methods:**

1. **Fact Cross-Checking**
   - Extract key claims from original article
   - Search for each claim independently
   - Count how many sources confirm each claim

2. **Date/Time Validation**
   - Verify event timing across sources
   - Check for consistency in dates
   - Flag discrepancies

3. **Detail Consistency**
   - Compare numbers (attendance, costs, etc.) across sources
   - Check location details
   - Identify contradictions

**Implementation:**
```python
class CrossReferenceValidator:
    def extract_verifiable_claims(self, article_text: str) -> List[Claim]:
        """Extract factual claims that can be verified"""

    def validate_claim(self, claim: Claim) -> ValidationResult:
        """Search for evidence supporting/refuting claim"""

    def build_consistency_report(self, validations: List[ValidationResult]) -> ConsistencyReport:
        """Report on which facts are confirmed vs. disputed"""
```

---

## Data Models

### InvestigationResult

```python
@dataclass
class InvestigationResult:
    """Result of investigatory journalism research"""

    topic_id: int
    investigation_date: datetime

    # Sources discovered
    additional_sources: List[Source]
    social_media_evidence: List[SocialSource]
    original_source: Optional[Source]

    # Analysis
    credibility_assessment: float  # 0-100
    consistency_score: float  # How consistent are sources
    context_richness: float  # How much context was found

    # Findings
    verified_claims: List[str]
    disputed_claims: List[str]
    additional_context: str

    # Recommendations
    recommended_verification_level: str  # unverified/verified/certified
    confidence_level: float  # How confident in recommendation
    investigation_notes: str  # Human-readable summary

    # Flag for editorial review
    requires_human_review: bool
    review_reason: Optional[str]
```

### SocialSource

```python
@dataclass
class SocialSource:
    """Source from social media"""

    platform: str  # twitter, reddit, etc.
    url: str
    author: str
    author_credibility: float  # 0-100
    timestamp: datetime
    content: str
    engagement_metrics: Dict  # likes, shares, etc.
    verification_status: str  # verified_account, community_member, anonymous
```

---

## Processing Pipeline

### Step 1: Initial Assessment

```python
def should_investigate(topic: Topic) -> bool:
    """Determine if topic needs investigatory journalism"""

    # Criteria:
    # - verification_status = 'unverified'
    # - source_count < 3
    # - topic is important enough (newsworthiness_score >= 50)
    # - not already investigated

    return (
        topic.verification_status == 'unverified' and
        (topic.source_count or 0) < 3 and
        topic.newsworthiness_score >= 50 and
        not topic.investigated
    )
```

### Step 2: Multi-Strategy Search

```python
def conduct_investigation(topic: Topic) -> InvestigationResult:
    """Main investigation workflow"""

    # 1. Multi-engine search
    search_results = multi_engine_searcher.search_all_engines(
        query=topic.title,
        date_range=(topic.discovery_date - timedelta(days=30), datetime.now())
    )

    # 2. Social media investigation
    social_evidence = social_media_investigator.investigate(topic)

    # 3. Origin tracing
    origin_source = origin_tracer.find_earliest_mention(topic)

    # 4. Context research
    context = context_researcher.gather_context(topic)

    # 5. Cross-reference validation
    validation_report = cross_reference_validator.validate(topic, search_results)

    # 6. Synthesize findings
    result = synthesize_investigation_result(
        search_results,
        social_evidence,
        origin_source,
        context,
        validation_report
    )

    return result
```

### Step 3: Verification Upgrade

```python
def upgrade_verification_level(topic: Topic, investigation: InvestigationResult):
    """Attempt to upgrade topic's verification status"""

    total_sources = len(investigation.additional_sources)
    credible_sources = [s for s in investigation.additional_sources if s.credibility_tier <= 2]

    # Update source plan with new sources
    source_plan = json.loads(topic.source_plan)
    source_plan['investigatory_sources'] = [
        {
            'url': s.url,
            'name': s.name,
            'credibility_tier': s.credibility_tier,
            'found_by': 'investigatory_journalist'
        }
        for s in investigation.additional_sources
    ]

    # Determine new verification level
    if len(credible_sources) >= 6:
        new_level = 'certified'
    elif len(credible_sources) >= 3:
        new_level = 'verified'
    elif len(credible_sources) >= 1:
        new_level = 'verified'  # Upgraded from unverified
    else:
        # Still unverified, but investigation attempted
        new_level = 'unverified'
        source_plan['investigation_attempted'] = True
        source_plan['investigation_notes'] = investigation.investigation_notes

    # Update topic
    topic.verification_status = new_level
    topic.source_count = len(credible_sources)
    topic.source_plan = json.dumps(source_plan)
    topic.investigated = True

    # Add investigation context to verified_facts
    verified_facts = json.loads(topic.verified_facts or '{}')
    verified_facts['investigation_context'] = investigation.additional_context
    verified_facts['investigation_date'] = investigation.investigation_date.isoformat()
    topic.verified_facts = json.dumps(verified_facts)
```

---

## Quality Gates

### Investigation Triggers

Only investigate topics that meet ALL criteria:

1. ✓ `verification_status == 'unverified'`
2. ✓ `source_count < 3`
3. ✓ `newsworthiness_score >= 50` (important enough to investigate)
4. ✓ `status == 'approved'`
5. ✓ `not investigated` (don't re-investigate)

### Success Criteria

Investigation is successful if ANY of:

- Found 3+ credible sources (Tier 1-2)
- Found original authoritative source
- Built comprehensive context with 5+ supporting details
- Social media evidence from 10+ independent accounts

### Human Review Flags

Flag for human review if:

- Contradictory information found (sources disagree)
- Only suspicious/low-credibility sources found
- Event cannot be corroborated anywhere
- Topic involves serious allegations requiring extra care

---

## Implementation Phases

### Phase 1: Core Search Enhancement (MVP)

**Deliverables:**
- [ ] Multi-engine search integration (Google, DuckDuckGo, Bing)
- [ ] Basic origin tracing (find earliest mention)
- [ ] Cross-reference validation (confirm key facts)
- [ ] Upgrade verification level based on findings
- [ ] Integration with existing Verification Agent

**Effort:** Medium (S)
**Dependencies:** None
**Testing:** 10 real unverified topics from production

---

### Phase 2: Social Media Investigation

**Deliverables:**
- [ ] Twitter API v2 integration (extended search)
- [ ] Reddit API integration (subreddit searches)
- [ ] Social source credibility scoring
- [ ] Timeline construction from social mentions
- [ ] Eyewitness account identification

**Effort:** Medium (S)
**Dependencies:** Phase 1
**Testing:** Labor events with known Twitter/Reddit activity

---

### Phase 3: Deep Context Research

**Deliverables:**
- [ ] Historical event research (find precedents)
- [ ] Key actor profiling (organizations, people)
- [ ] Local news source aggregation
- [ ] Geographic context gathering
- [ ] Related event clustering

**Effort:** Large (M)
**Dependencies:** Phase 1, 2
**Testing:** Complex multi-faceted events

---

### Phase 4: Advanced Analysis

**Deliverables:**
- [ ] Claim extraction using LLM
- [ ] Automated fact-checking per claim
- [ ] Contradiction detection
- [ ] Bias analysis of sources
- [ ] Confidence scoring for recommendations

**Effort:** Large (M)
**Dependencies:** Phase 1, 2, 3
**Testing:** Disputed events, contradictory reporting

---

## Performance Requirements

### Speed
- Investigation should complete within 2-5 minutes per topic
- Don't block article generation (can run async)
- Cache search results for 24 hours

### Accuracy
- False positive rate (upgrading bad sources): < 5%
- False negative rate (missing good sources): < 15%
- Origin identification accuracy: > 80%

### Cost
- API costs per investigation: < $0.50
- Use rate limiting to avoid expensive searches
- Prioritize free search engines over paid

---

## Database Schema Changes

### New Fields for Topic Model

```python
# Add to Topic model
investigated: Mapped[bool] = mapped_column(Boolean, default=False)
investigation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
investigation_confidence: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
investigation_notes: Mapped[Optional[str]] = mapped_column(Text)
```

### New Table: Investigations

```python
class Investigation(Base):
    """Tracks investigatory journalism work"""
    __tablename__ = 'investigations'

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey('topics.id'))

    # Investigation details
    investigation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    investigator: Mapped[str] = mapped_column(String, default='investigatory_journalist_agent')

    # Sources found
    sources_found: Mapped[int] = mapped_column(Integer, default=0)
    social_sources_found: Mapped[int] = mapped_column(Integer, default=0)
    original_source_url: Mapped[Optional[str]] = mapped_column(String)

    # Analysis scores
    credibility_score: Mapped[float] = mapped_column(Float)
    consistency_score: Mapped[float] = mapped_column(Float)
    confidence_level: Mapped[float] = mapped_column(Float)

    # Results
    verification_level_before: Mapped[str] = mapped_column(String)
    verification_level_after: Mapped[str] = mapped_column(String)
    sources_json: Mapped[str] = mapped_column(Text)  # JSON array of found sources

    # Findings
    verified_claims: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    disputed_claims: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    context_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Review flags
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=False)
    review_reason: Mapped[Optional[str]] = mapped_column(String)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

---

## API Endpoints

### Trigger Investigation

```
POST /api/investigations/
Body: {
    "topic_id": 1,
    "priority": "high"  // optional: high/normal/low
}

Response: {
    "investigation_id": 123,
    "status": "started",
    "estimated_completion": "2026-01-02T12:35:00Z"
}
```

### Get Investigation Status

```
GET /api/investigations/123

Response: {
    "id": 123,
    "topic_id": 1,
    "status": "completed",
    "sources_found": 5,
    "verification_upgraded": true,
    "new_verification_level": "verified"
}
```

### List Topics Needing Investigation

```
GET /api/investigations/candidates?limit=20

Response: {
    "topics": [
        {
            "topic_id": 1,
            "title": "...",
            "current_verification": "unverified",
            "source_count": 0,
            "newsworthiness_score": 65
        }
    ]
}
```

---

## Testing Strategy

### Unit Tests

- [ ] Multi-engine search deduplication
- [ ] Origin tracing logic
- [ ] Cross-reference validation
- [ ] Verification level upgrade logic
- [ ] Social credibility scoring

### Integration Tests

- [ ] Full investigation pipeline on known events
- [ ] Verification Agent → Investigatory Journalist handoff
- [ ] Database updates (topics, investigations table)

### End-to-End Tests

- [ ] Real unverified topic → investigation → article generation
- [ ] Performance test (100 investigations, measure time/cost)
- [ ] Accuracy test (50 known events, measure upgrade correctness)

---

## Monitoring & Metrics

### Key Metrics

- **Investigation Success Rate:** % of investigations that find 3+ sources
- **Upgrade Rate:** % of unverified topics upgraded to verified/certified
- **Average Sources Found:** Mean sources per investigation
- **Investigation Time:** p50, p95, p99 completion times
- **Cost Per Investigation:** API costs per topic
- **False Upgrade Rate:** % of upgraded sources later flagged as unreliable

### Alerts

- Investigation taking > 10 minutes
- Cost per investigation > $1.00
- False upgrade rate > 10%
- API rate limit errors

---

## Open Questions

1. **API Costs:** Which paid search APIs are worth the cost?
2. **Social Media Access:** Can we get elevated API access for Twitter/Reddit?
3. **Archived Content:** Should we integrate Internet Archive API?
4. **Human Review Workflow:** How do editors review flagged investigations?
5. **Re-investigation:** Should we re-investigate topics after N days if new info available?

---

## References

- Verification Agent: `/backend/agents/verification_agent.py`
- Source Ranking: `/backend/agents/verification/source_ranker.py`
- Database Models: `/database/models.py`
- 3-Tier Verification System: See conversation context

---

## Approval Status

- [ ] Technical Lead Review
- [ ] Product Owner Approval
- [ ] Security Review (API key management)
- [ ] Privacy Review (social media data handling)
- [ ] Cost Approval (API budget allocation)

**Next Steps:** Begin Phase 1 implementation after approval
