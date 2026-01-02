# Verification Agent - Source Verification & Attribution

**Phase 6.4 of the DWnews Automated Journalism Pipeline**

## Overview

The Verification Agent ensures journalistic integrity by verifying sources and creating attribution plans for approved topics. It sits between the Evaluation Agent (which approves newsworthy events) and the Enhanced Journalist Agent (which drafts articles).

## Purpose

Before any article is generated, the Verification Agent:
1. Identifies primary sources (government documents, academic papers, news coverage)
2. Cross-references claims across multiple sources
3. Classifies facts as observed, claimed, or interpreted
4. Ranks sources by credibility (Tier 1-4)
5. Validates that topics meet minimum source requirements (≥3 credible sources OR ≥2 academic citations)
6. Creates structured attribution plans for journalists

## Architecture

### Module Structure

```
backend/agents/verification/
├── __init__.py                    # Module exports
├── source_identifier.py           # Finds primary sources via WebSearch
├── cross_reference.py             # Compares claims across sources
├── fact_classifier.py             # Classifies facts (observed/claimed/interpreted)
└── source_ranker.py               # Applies source credibility hierarchy

backend/agents/
└── verification_agent.py          # Main orchestrator
```

### Components

#### 1. SourceIdentifier (`source_identifier.py`)
**Purpose:** Find primary sources using WebSearch

**Strategies:**
- Official/government sources (NLRB, court filings, agency reports)
- Academic sources (Google Scholar, arXiv, JSTOR)
- News coverage (Reuters, AP, Bloomberg)
- Primary documents (press releases, reports)

**Output:** List of `Source` objects with URL, name, type, snippet

#### 2. CrossReferenceVerifier (`cross_reference.py`)
**Purpose:** Compare claims across sources to verify consistency

**Process:**
- Extract claims from each source (numbers, dates, names, organizations)
- Find supporting sources for each fact
- Detect conflicting information
- Calculate confidence levels (high/medium/low)
- Generate source agreement score (0-1)

**Output:** `VerificationResult` with verified facts and conflicts

#### 3. FactClassifier (`fact_classifier.py`)
**Purpose:** Classify facts into three categories

**Categories:**
- **Observed:** Firsthand documentation (court rulings, official counts, video evidence)
- **Claimed:** Secondhand reporting (news citing sources, official statements)
- **Interpreted:** Analysis or opinion (expert commentary, predictions)

**Output:** Fact type ('observed', 'claimed', or 'interpreted')

#### 4. SourceRanker (`source_ranker.py`)
**Purpose:** Rank sources by credibility using hierarchical system

**Tiers:**
- **Tier 1 (90-100):** Named primary sources (government docs, academic papers)
- **Tier 2 (70-89):** Organizational sources (Reuters, ProPublica, major newspapers)
- **Tier 3 (50-69):** Documentary evidence (public records, verified social media)
- **Tier 4 (0-49):** Anonymous/unverified (blogs, unverified social media)

**Output:** List of `RankedSource` objects with credibility scores

#### 5. VerificationAgent (`verification_agent.py`)
**Purpose:** Orchestrate the verification process

**Workflow:**
1. Query approved topics from database
2. Identify sources using SourceIdentifier
3. Rank sources using SourceRanker
4. Validate threshold (≥3 credible sources OR ≥2 academic citations)
5. Extract and verify facts using CrossReferenceVerifier
6. Classify facts using FactClassifier
7. Create attribution plan
8. Store results in database

**Output:** Updates topics table with `verified_facts` and `source_plan` JSON

## Data Flow

```
Topics (status='approved')
    ↓
SourceIdentifier → Find sources via WebSearch
    ↓
SourceRanker → Rank by credibility (Tier 1-4)
    ↓
Threshold Validation → Check ≥3 credible or ≥2 academic
    ↓
CrossReferenceVerifier → Verify facts across sources
    ↓
FactClassifier → Classify as observed/claimed/interpreted
    ↓
Create source_plan → Attribution strategy for journalist
    ↓
Store in database → verified_facts, source_plan JSON
    ↓
Topics (verification_status='verified')
```

## Database Schema

### Topics Table Fields Updated

```sql
verified_facts TEXT           -- JSON: Structured fact verification results
source_plan TEXT              -- JSON: Attribution plan for journalist
verification_status VARCHAR   -- 'pending', 'in_progress', 'verified', 'insufficient_sources', 'failed'
source_count INTEGER          -- Number of credible sources (Tier 1-2)
academic_citation_count INT   -- Number of academic citations
```

### verified_facts JSON Format

```json
{
  "facts": [
    {
      "claim": "Amazon warehouse workers in Staten Island voted to unionize",
      "type": "observed",
      "sources": ["https://nlrb.gov/...", "https://reuters.com/..."],
      "confidence": "high",
      "conflicting_info": null
    }
  ],
  "source_summary": {
    "total_sources": 7,
    "credible_sources": 5,
    "academic_citations": 1,
    "meets_threshold": true,
    "source_agreement_score": 0.85
  }
}
```

### source_plan JSON Format

```json
{
  "primary_sources": [
    {
      "name": "NLRB Election Results",
      "url": "https://nlrb.gov/case/...",
      "type": "government_document",
      "rank": 1,
      "credibility_tier": 1,
      "credibility_score": 100
    }
  ],
  "supporting_sources": [...],
  "attribution_strategy": "Lead with NLRB official results, corroborate with Amazon statement",
  "verification_notes": {
    "total_sources_found": 7,
    "credible_sources": 5,
    "academic_citations": 1,
    "threshold_met": true,
    "threshold_met_by": "credible_sources"
  }
}
```

## Usage

### Standalone Execution

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 backend/agents/verification_agent.py
```

### Programmatic Usage

```python
from backend.database import SessionLocal
from backend.agents.verification_agent import VerificationAgent

session = SessionLocal()
agent = VerificationAgent(session)

# Verify all pending topics
results = agent.verify_all_approved_topics()

# Verify specific topic
success = agent.verify_topic(topic_id=123)

# Get statistics
stats = agent.get_verification_stats()

session.close()
```

### Testing

```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 scripts/test_verification.py
```

## Source Credibility Hierarchy

### Tier 1: Named Primary Sources (90-100)
- **Government documents:** NLRB rulings, court filings, SEC reports
- **Academic papers:** Peer-reviewed research, university studies
- **Official statements:** Direct statements from involved organizations

**Why Tier 1?** Direct, authoritative, verifiable primary documentation

### Tier 2: Organizational Sources (70-89)
- **News wire services:** Reuters, Associated Press, Bloomberg
- **Investigative journalism:** ProPublica, The Markup, The Intercept
- **Major newspapers:** NYT, Washington Post, WSJ
- **Labor specialists:** Labor Notes

**Why Tier 2?** Professional editorial standards, fact-checking processes

### Tier 3: Documentary Evidence (50-69)
- **Public records:** Financial disclosures, meeting minutes
- **Verified social media:** Official organizational accounts
- **Regional news:** Local newspapers, city news sites

**Why Tier 3?** Useful context but less rigorous verification

### Tier 4: Anonymous/Unverified (0-49)
- **Anonymous sources:** Unnamed individuals
- **Unverified social media:** Personal accounts, blogs

**Why Tier 4?** Cannot be independently verified, use only with corroboration

## Verification Thresholds

### Minimum Requirements
- **Standard:** ≥3 credible sources (Tier 1 or Tier 2), OR
- **Academic:** ≥2 academic citations (peer-reviewed papers)

### Cross-Reference Requirements
- At least 2 sources must independently confirm key facts
- No single source can be sole basis for verification
- Conflicting information must be documented

### Quality Standards
- Numbers, dates, names must match across sources
- Contentious claims require 2+ independent confirmations
- Source disagreements flagged in verified_facts

## Fact Classification Rules

### Observed Facts
**Definition:** Firsthand documentation with direct evidence

**Examples:**
- "NLRB certified election results: 2,654 for, 2,131 against"
- "Court ruled on March 15, 2024"
- "Video shows workers picketing outside warehouse"

**Source Types:** Government docs, court records, official statistics

### Claimed Facts
**Definition:** Secondhand reporting with source attribution

**Examples:**
- "According to Reuters, Amazon spokesperson said..."
- "Union organizers told reporters..."
- "Sources say workers plan to strike"

**Source Types:** News articles, statements, testimony

### Interpreted Facts
**Definition:** Analysis, opinion, or prediction

**Examples:**
- "This could spark similar campaigns nationwide"
- "Experts say the ruling is significant"
- "Trend suggests growing labor movement"

**Source Types:** Analysis pieces, expert commentary, opinion

## Error Handling

### Insufficient Sources
**Status:** `verification_status = 'insufficient_sources'`
**Cause:** <3 credible sources AND <2 academic citations
**Action:** Topic flagged for human review

### Verification Failed
**Status:** `verification_status = 'failed'`
**Cause:** Technical error (network issues, database errors)
**Action:** Topic can be retried, error logged

### Conflicting Information
**Status:** `verification_status = 'verified'` (with notes)
**Storage:** Documented in `verified_facts.facts[].conflicting_info`
**Action:** Journalist must address conflicts with attribution

## Testing

### Test Script Features
- Tests all approved topics in database
- Validates source count and threshold compliance
- Displays verification results (verified_facts, source_plan)
- Shows success rate and average metrics

### Test Results Example
```
Total topics tested: 3
Successful: 3 (100.0%)
Failed: 0

Average metrics (successful topics):
  Sources: 5.0
  Academic citations: 1.0
```

## Integration with Pipeline

### Upstream: Evaluation Agent
- **Input:** Topics with status='approved'
- **Trigger:** verification_status='pending'

### Downstream: Enhanced Journalist Agent
- **Output:** Topics with verification_status='verified'
- **Handoff:** Journalist uses verified_facts and source_plan

## Performance Considerations

- **WebSearch Rate Limiting:** Limit to 4-5 searches per topic
- **Source Deduplication:** Remove duplicate URLs
- **Batch Processing:** Process topics sequentially
- **Error Recovery:** Continue on individual failures

## Future Enhancements

1. **Live Source Fetching:** Web scraping for full article content
2. **LLM-Powered Analysis:** Use Claude/GPT to extract claims
3. **Source Reliability Learning:** Track accuracy over time
4. **Automated Fact Extraction:** NLP for claim extraction
5. **Citation Management:** Generate AP-style citations

## Files Created

```
backend/agents/verification/
├── __init__.py                    # 16 lines
├── source_identifier.py           # 399 lines
├── cross_reference.py             # 376 lines
├── fact_classifier.py             # 257 lines
└── source_ranker.py               # 327 lines

backend/agents/
└── verification_agent.py          # 458 lines

.claude/agents/
└── verification.md                # Complete agent definition

scripts/
└── test_verification.py           # 366 lines

Total: ~2,199 lines of production code
```

## Completion Criteria ✓

- [x] Build primary source identification (WebSearch, document analysis)
- [x] Implement cross-reference verification (compare claims across sources)
- [x] Build fact classification engine (observed vs. claimed vs. interpreted)
- [x] Implement source hierarchy enforcement (named > org > docs > anon)
- [x] Verify ≥3 credible sources OR ≥2 academic citations per topic
- [x] Store verified_facts and source_plan in topics table (JSON format)
- [x] Create agent definition: `.claude/agents/verification.md`
- [x] Test with approved topics (verify source count, attribution plan)

**Status:** Phase 6.4 complete. Agent verifies ≥3 sources per topic and creates attribution plans.

## Next Steps

**Phase 6.5:** Enhanced Journalist Agent
- Use verified_facts and source_plan to draft articles
- Implement proper attribution based on source hierarchy
- Generate fact-based journalism with transparent sourcing
