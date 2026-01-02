# Enhanced Journalist Agent - Phase 6.5

Automated article generation with self-audit, bias detection, and quality validation.

## Overview

The Enhanced Journalist Agent generates quality news articles from verified topics with:
- **10-point self-audit checklist** (all must pass)
- **Bias detection** (hallucination & propaganda checks)
- **Reading level validation** (7.5-8.5 Flesch-Kincaid)
- **Proper source attribution** using verified facts and source plan

## Architecture

```
enhanced_journalist_agent.py (Orchestrator)
├── self_audit.py              # 10-point checklist validation
├── bias_detector.py           # Hallucination & propaganda detection
├── readability_checker.py     # Flesch-Kincaid scoring
└── attribution_engine.py      # Source attribution strategy
```

## Modules

### 1. Self-Audit (`self_audit.py`)

Validates articles against 10 quality criteria:

1. **Factual Accuracy**: All facts sourced from verified_facts JSON
2. **Source Attribution**: All claims properly attributed using source_plan
3. **Reading Level**: Flesch-Kincaid score between 7.5-8.5
4. **Worker-Centric Framing**: Presents labor perspective, avoids capital bias
5. **No Hallucinations**: All information traceable to source material
6. **Proper Context**: Includes relevant background, avoids misleading framing
7. **Active Voice**: Uses active voice for clarity (80%+ of sentences)
8. **Specific Details**: Includes concrete numbers, dates, names from sources
9. **Balanced Representation**: Presents multiple perspectives when sources provide them
10. **Editorial Standards**: Meets DWnews style (punchy, accurate, doesn't pull punches)

**Usage:**
```python
from backend.agents.journalist.self_audit import SelfAudit

audit = SelfAudit()
result = audit.audit_article(
    article_text=article_text,
    verified_facts=verified_facts_json,
    source_plan=source_plan_json,
    reading_level=8.0
)

if result.passed:
    print("Article passed all 10 criteria")
else:
    print(f"Failed criteria: {[k for k, v in result.checklist.items() if not v]}")
```

### 2. Bias Detector (`bias_detector.py`)

Detects bias, hallucinations, and propaganda patterns:

**Hallucination Checks:**
- Claims not present in source material
- Numbers/dates/names that don't match sources
- Invented quotes or paraphrases
- Conclusions not supported by facts

**Propaganda Checks:**
- Corporate PR language uncritically repeated
- Capital-biased framing (e.g., "labor costs" instead of "worker wages")
- Victim-blaming narratives
- False balance (e.g., equating worker complaints with employer denials)

**Bias Indicators:**
- Passive voice hiding accountability
- Euphemisms for exploitation (e.g., "gig economy" for precarious labor)
- Missing worker voices when available
- Overemphasis on employer perspective

**Usage:**
```python
from backend.agents.journalist.bias_detector import BiasDetector

detector = BiasDetector()
report = detector.scan_article(
    article_text=article_text,
    verified_facts=verified_facts_json,
    source_plan=source_plan_json
)

print(f"Overall Score: {report.overall_score}")  # PASS, WARNING, FAIL
print(f"Hallucinations: {len(report.hallucination_details)}")
print(f"Propaganda: {len(report.propaganda_flags)}")
```

### 3. Readability Checker (`readability_checker.py`)

Validates article reading level using Flesch-Kincaid Grade Level formula.

**Target:** 7.5-8.5 (high school freshman, accessible to working class)

**Usage:**
```python
from backend.agents.journalist.readability_checker import ReadabilityChecker

checker = ReadabilityChecker()
score = checker.check_reading_level(article_text)

if checker.is_within_target_range(score):
    print(f"Reading level {score:.1f} within target range")
else:
    suggestion = checker.get_adjustment_suggestion(score)
    print(f"Reading level {score:.1f} outside range. {suggestion}")
```

### 4. Attribution Engine (`attribution_engine.py`)

Generates properly attributed article content using source plan.

**Features:**
- Extracts high-confidence facts from verified_facts
- Applies attribution strategy from source_plan
- Generates LLM prompts with proper attribution instructions
- Validates primary source citation coverage

**Usage:**
```python
from backend.agents.journalist.attribution_engine import AttributionEngine

engine = AttributionEngine()
prompt = engine.generate_attribution_prompt(
    topic_title="Union Strike at Factory",
    verified_facts=verified_facts_json,
    source_plan=source_plan_json
)

# Use prompt with LLM to generate article
```

## Enhanced Journalist Agent

Main orchestrator that coordinates all modules.

**Usage:**
```python
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from backend.database import SessionLocal

db = SessionLocal()
agent = EnhancedJournalistAgent(db)

# Generate article from verified topic
article = agent.generate_article(topic_id=123)

if article:
    print(f"Article: {article.title}")
    print(f"Reading Level: {article.reading_level}")
    print(f"Self-Audit Passed: {article.self_audit_passed}")
```

## Article Generation Workflow

1. **Load Verified Topic**: Read topic with verified_facts and source_plan from database
2. **Validate Data**: Ensure topic has required JSON data
3. **Generate Draft**: Use LLM (Claude) to generate article with attribution instructions
4. **Calculate Reading Level**: Use Flesch-Kincaid formula
5. **Run Self-Audit**: Validate against 10-point checklist
6. **Run Bias Detection**: Scan for hallucinations and propaganda
7. **Regenerate if Needed**: Up to 3 attempts if quality checks fail
8. **Store Article**: Save to database with bias_scan_report and self_audit_passed
9. **Create Revision**: Track generation in article_revisions table

## Database Integration

**Reads from `topics` table:**
- `verified_facts` (JSON): Verified facts from verification agent
- `source_plan` (JSON): Source attribution strategy

**Writes to `articles` table:**
- `bias_scan_report` (JSON): Bias detection results
- `self_audit_passed` (boolean): Whether 10-point audit passed
- `reading_level` (float): Flesch-Kincaid score
- `editorial_notes` (text): Generation metadata

**Writes to `article_revisions` table:**
- Tracks each generation attempt
- Records reading level changes
- Stores bias check results

## Quality Standards

**All articles must:**
- Pass all 10 self-audit criteria (100%)
- Have reading level between 7.5-8.5
- Pass bias detection scan (overall_score="PASS")
- Include proper source attribution
- Be worker-centric in framing

**Regeneration policy:**
- Maximum 3 generation attempts per topic
- Failed articles flagged for human review
- All attempts logged in article_revisions table

## Testing

Run test suite:
```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
python3 scripts/test_journalist.py
```

Test specific article:
```bash
python3 scripts/test_journalist.py --article 123
```

Generate article from topic:
```bash
python3 -m backend.agents.enhanced_journalist_agent 123
```

## Requirements

- Python 3.9+
- Claude API key (CLAUDE_API_KEY environment variable)
- Database with verified topics (Phase 6.4)
- Required packages:
  - anthropic (Claude API)
  - textstat (readability scoring)
  - sqlalchemy (database)

## Configuration

Set API key in `.env` file:
```bash
CLAUDE_API_KEY=sk-ant-...
```

Or export environment variable:
```bash
export CLAUDE_API_KEY=sk-ant-...
```

## Success Criteria

Phase 6.5 is complete when:
- All 4 journalist modules implemented and tested
- Enhanced journalist agent generates articles from verified topics
- 100% of articles pass 10-point self-audit
- All articles have reading level 7.5-8.5
- Bias detection identifies and flags issues
- Test script validates quality standards

## Notes

- Article generation requires Claude API access (uses Sonnet 4.5)
- Readability checker can use textstat library or manual calculation
- Self-audit uses heuristic checks (NLP-lite approach)
- Bias detection focuses on worker-centric journalism values
- Failed articles are stored for human review (not discarded)
- All quality checks are logged and auditable
