# Vertex AI Imagen to Gemini 2.5 Flash Image - Migration Plan

**Document Version:** 1.0
**Date:** 2026-01-02
**Project:** The Daily Worker (DWnews)
**Purpose:** Complete migration plan from Vertex AI Imagen to Gemini 2.5 Flash Image with Claude enhancement

---

## Executive Summary

This document outlines the complete migration from Vertex AI Imagen (current implementation) to Gemini 2.5 Flash Image with Claude Sonnet prompt enhancement. The migration involves code changes, dependency updates, configuration changes, and database schema updates.

**Migration Complexity:** Medium
**Estimated Effort:** 3-4 hours implementation + 2 hours testing
**Risk Level:** Low (clean separation, good fallback options)
**Rollback Plan:** Revert commits, restore old dependencies

---

## Current State Analysis

### Existing Implementation

**File:** `/backend/agents/image_sourcing_agent.py`

**Current Gemini Integration (Lines 306-421):**
- Uses Vertex AI Imagen endpoint (deprecated approach)
- Endpoint format: `https://us-central1-aiplatform.googleapis.com/v1/projects/{project}/locations/us-central1/publishers/google/models/imagegeneration:predict`
- Authentication: Bearer token (service account)
- Response format: Base64 encoded image in JSON
- Prompt generation: Simple template-based (`generate_gemini_prompt` method)

**Problems with Current Implementation:**
1. **Poor image quality:** Generic prompts produce uninspiring results
2. **Complex authentication:** Requires GCP project setup and service accounts
3. **Heavyweight dependencies:** `google-cloud-aiplatform` adds significant complexity
4. **Slow generation:** 20-30 seconds typical (vs. 10-15s for Gemini 2.5 Flash)
5. **Poor prompt adherence:** Images often don't match article themes well

### Dependencies to Remove

**requirements.txt:**
```
google-cloud-aiplatform>=1.38.0  # REMOVE
```

### Dependencies to Add

**requirements.txt:**
```
google-genai>=1.0.0              # ADD for Gemini 2.5 Flash Image
anthropic>=0.18.0                # ADD for Claude prompt enhancement (may already exist)
```

---

## Migration Strategy

### Phase-by-Phase Approach

**Phase 1: Add New Implementation (Parallel)**
- Install new dependencies
- Create new image generation service alongside old one
- Implement Claude prompt enhancement service
- Test new implementation independently

**Phase 2: Update Configuration**
- Update `.env.example` with new API key variables
- Update `backend/config.py` with new settings
- Add database migrations for concept storage

**Phase 3: Switch Over**
- Update `image_sourcing_agent.py` to use new implementation
- Remove old Vertex AI code
- Update tests

**Phase 4: Cleanup**
- Remove old dependencies
- Delete deprecated code
- Update documentation

**Benefit:** Can test new implementation before removing old one (safety)

---

## Code Changes Required

### 1. Create New Service Module

**New file:** `/backend/services/image_generation.py`

```python
"""
The Daily Worker - Image Generation Service
Gemini 2.5 Flash Image with Claude Sonnet prompt enhancement
"""

import google.generativeai as genai
import anthropic
import json
from io import BytesIO
from typing import Optional, Dict, List
from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)


class ImageGenerationService:
    """
    Two-step image generation:
    1. Claude Sonnet generates 3-5 artistic concepts
    2. Gemini 2.5 Flash Image generates best concept
    """

    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash-image')

        # Configure Claude
        self.claude_client = anthropic.Anthropic(
            api_key=settings.claude_api_key
        )

    def enhance_prompt_with_claude(
        self,
        headline: str,
        summary: str,
        category: str,
        is_opinion: bool
    ) -> List[Dict]:
        """Generate 3-5 artistic concepts using Claude"""
        # Implementation from CLAUDE_PROMPT_ENHANCEMENT_WORKFLOW.md
        pass

    def select_best_concept(self, concepts: List[Dict]) -> Dict:
        """Select concept with highest confidence score"""
        # Implementation from CLAUDE_PROMPT_ENHANCEMENT_WORKFLOW.md
        pass

    def generate_with_gemini(self, prompt: str) -> Optional[bytes]:
        """Generate image using Gemini 2.5 Flash Image"""
        # Implementation from GEMINI_IMAGE_API_SPECS.md
        pass

    def generate_image(
        self,
        headline: str,
        summary: str,
        category: str,
        is_opinion: bool = False
    ) -> Dict:
        """
        Complete image generation workflow.

        Returns:
            Dict with keys:
                - image_data: bytes
                - concepts: List[Dict] (all concepts)
                - selected_concept: Dict
                - source_type: 'generated'
                - attribution: str
        """
        try:
            # Step 1: Claude prompt enhancement
            concepts = self.enhance_prompt_with_claude(
                headline, summary, category, is_opinion
            )

            # Step 2: Select best concept
            selected = self.select_best_concept(concepts)

            # Step 3: Generate with Gemini
            image_bytes = self.generate_with_gemini(selected['prompt'])

            if not image_bytes:
                logger.warning("Gemini generation failed, returning None")
                return None

            return {
                'image_data': image_bytes,
                'concepts': concepts,
                'selected_concept': selected,
                'source_type': 'generated',
                'attribution': 'AI-generated image via Google Gemini 2.5 Flash Image',
                'license': 'Generated content - Editorial use'
            }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None
```

### 2. Update image_sourcing_agent.py

**Changes to `/backend/agents/image_sourcing_agent.py`:**

**Replace method `generate_with_gemini` (lines 306-421):**

```python
# OLD CODE - DELETE LINES 306-421
def generate_with_gemini(self, prompt: str, ...) -> Optional[Dict]:
    # Vertex AI Imagen implementation
    # [DELETE ALL THIS CODE]

# NEW CODE - ADD
from backend.services.image_generation import ImageGenerationService

def __init__(self):
    # ... existing code ...

    # NEW: Initialize image generation service
    self.image_generator = ImageGenerationService()

def generate_with_gemini_enhanced(
    self,
    headline: str,
    summary: str,
    category: str,
    is_opinion: bool = False
) -> Optional[Dict]:
    """
    Generate image using Gemini 2.5 Flash Image with Claude enhancement.

    This replaces the old Vertex AI Imagen implementation.
    """
    try:
        result = self.image_generator.generate_image(
            headline=headline,
            summary=summary,
            category=category,
            is_opinion=is_opinion
        )

        if not result:
            logger.warning("Image generation failed")
            return None

        # Store concepts in database
        if hasattr(self, 'store_image_concepts'):
            self.store_image_concepts(
                article_id=None,  # Will be set later
                concepts=result['concepts'],
                selected=result['selected_concept']
            )

        return result

    except Exception as e:
        logger.error(f"Enhanced Gemini generation failed: {e}")
        return None
```

**Update method `source_image_cascading` (lines 532-609):**

```python
# Line 562-574: Update Gemini generation call
# OLD:
result = self.generate_with_gemini(prompt)

# NEW:
result = self.generate_with_gemini_enhanced(
    headline=article.get('title', article.get('headline', '')),
    summary=article.get('summary', ''),
    category=article.get('category', 'news'),
    is_opinion=article.get('is_opinion', False)
)
```

**Delete method `generate_gemini_prompt` (lines 246-304):**
- No longer needed (Claude generates prompts)
- Simple prompt generation moved to fallback

### 3. Update Configuration

**File:** `/backend/config.py`

```python
# Find existing gemini_api_key field (around line 33)
# UPDATE comments and add Claude requirement

class Settings(BaseSettings):
    # ... existing fields ...

    # Image Generation APIs
    gemini_api_key: Optional[str] = Field(
        default=None,
        alias="GEMINI_API_KEY",
        description="Google Gemini API key for image generation (Gemini 2.5 Flash Image)"
    )

    claude_api_key: Optional[str] = Field(
        default=None,
        alias="CLAUDE_API_KEY",
        description="Anthropic Claude API key for prompt enhancement and article generation"
    )

    # DEPRECATED (remove these or mark deprecated)
    # gemini_image_api_key: Optional[str] = Field(...)  # Old name, use GEMINI_API_KEY

    # ... rest of config ...
```

**File:** `/.env.example` (already updated in current codebase)**
- Already has correct configuration (lines 45-53)
- No changes needed

### 4. Database Migration

**New file:** `/database/migrations/006_image_concepts.sql`

```sql
-- Migration: Add Claude prompt enhancement concept storage
-- Date: 2026-01-02
-- Purpose: Store all Claude-generated concepts and metadata

-- Create article_image_concepts table
CREATE TABLE IF NOT EXISTS article_image_concepts (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    concept_number INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0.00 AND confidence <= 1.00),
    rationale TEXT NOT NULL,
    selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_article_concept UNIQUE(article_id, concept_number),
    CONSTRAINT one_selected_per_article UNIQUE(article_id, selected) WHERE selected = TRUE
);

-- Create indexes
CREATE INDEX idx_article_image_concepts_article_id ON article_image_concepts(article_id);
CREATE INDEX idx_article_image_concepts_selected ON article_image_concepts(selected);
CREATE INDEX idx_article_image_concepts_confidence ON article_image_concepts(confidence);

-- Add columns to images table
ALTER TABLE images ADD COLUMN IF NOT EXISTS concept_confidence DECIMAL(3,2);
ALTER TABLE images ADD COLUMN IF NOT EXISTS concept_rationale TEXT;
ALTER TABLE images ADD COLUMN IF NOT EXISTS claude_enhancement_used BOOLEAN DEFAULT FALSE;

-- Create view for quick access to selected concepts
CREATE OR REPLACE VIEW article_selected_concepts AS
SELECT
    a.id as article_id,
    a.headline,
    a.category_id,
    aic.prompt,
    aic.confidence,
    aic.rationale,
    i.url as image_url,
    i.attribution
FROM articles a
LEFT JOIN article_image_concepts aic ON a.id = aic.article_id AND aic.selected = TRUE
LEFT JOIN images i ON a.image_id = i.id
WHERE aic.id IS NOT NULL;

-- Add comment documentation
COMMENT ON TABLE article_image_concepts IS 'Stores Claude-generated image concepts for each article (3-5 concepts per article with confidence scores and rationales)';
COMMENT ON COLUMN article_image_concepts.concept_number IS 'Order of concept from Claude (1-5), 1 = first concept generated';
COMMENT ON COLUMN article_image_concepts.confidence IS 'Claude confidence score 0.00-1.00, higher = better fit for article';
COMMENT ON COLUMN article_image_concepts.selected IS 'TRUE for the concept that was used for image generation (one per article)';
```

**Migration runner:** `/database/migrations/run_migration_006.py`

```python
"""Run migration 006 - Image concepts table"""

import sqlite3
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)


def run_migration():
    """Execute migration 006"""

    db_path = settings.database_url.replace('sqlite:///', '')

    logger.info(f"Running migration 006 on database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Read migration SQL
        migration_file = Path(__file__).parent / '006_image_concepts.sql'
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        # Execute migration (split by semicolon for SQLite)
        for statement in migration_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)

        conn.commit()
        logger.info("✓ Migration 006 completed successfully")

        # Verify tables created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='article_image_concepts'")
        if cursor.fetchone():
            logger.info("✓ Table article_image_concepts created")
        else:
            raise Exception("Table article_image_concepts not created")

    except Exception as e:
        logger.error(f"Migration 006 failed: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == '__main__':
    run_migration()
```

### 5. Update Tests

**Update file:** `/scripts/test_image_generation.py` (create if doesn't exist)

```python
"""
Test image generation with Gemini 2.5 Flash Image and Claude enhancement
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.services.image_generation import ImageGenerationService
from backend.logging_config import get_logger

logger = get_logger(__name__)


def test_claude_enhancement():
    """Test Claude prompt enhancement"""

    service = ImageGenerationService()

    # Test article
    headline = "Amazon Warehouse Workers Vote to Unionize in Historic Victory"
    summary = "Workers at Amazon's Staten Island warehouse voted to form the company's first U.S. union, marking a major victory for labor organizers."
    category = "labor"

    logger.info("Testing Claude prompt enhancement...")

    concepts = service.enhance_prompt_with_claude(
        headline=headline,
        summary=summary,
        category=category,
        is_opinion=False
    )

    assert len(concepts) >= 3, "Should generate at least 3 concepts"
    assert len(concepts) <= 5, "Should generate at most 5 concepts"

    for i, concept in enumerate(concepts):
        logger.info(f"\nConcept {i+1}:")
        logger.info(f"  Confidence: {concept['confidence']:.2f}")
        logger.info(f"  Prompt: {concept['prompt'][:100]}...")
        logger.info(f"  Rationale: {concept['rationale']}")

        assert 0.0 <= concept['confidence'] <= 1.0, "Confidence must be 0.0-1.0"
        assert len(concept['prompt']) >= 50, "Prompt too short"
        assert len(concept['rationale']) >= 20, "Rationale too short"

    logger.info("\n✓ Claude enhancement test passed")


def test_gemini_generation():
    """Test Gemini 2.5 Flash Image generation"""

    service = ImageGenerationService()

    prompt = "Documentary-style photograph of diverse warehouse workers organizing union meeting, warm lighting, horizontal 16:9 format"

    logger.info("Testing Gemini image generation...")

    image_bytes = service.generate_with_gemini(prompt)

    assert image_bytes is not None, "Image generation failed"
    assert len(image_bytes) > 1000, "Image data too small"

    logger.info(f"✓ Generated image: {len(image_bytes)} bytes")


def test_end_to_end():
    """Test complete workflow: Claude → Gemini"""

    service = ImageGenerationService()

    result = service.generate_image(
        headline="Teachers Strike for Better Pay and Working Conditions",
        summary="Public school teachers across three states walked off the job demanding higher wages and improved classroom resources.",
        category="labor",
        is_opinion=False
    )

    assert result is not None, "End-to-end generation failed"
    assert 'image_data' in result, "Missing image_data"
    assert 'concepts' in result, "Missing concepts"
    assert 'selected_concept' in result, "Missing selected_concept"

    logger.info(f"✓ End-to-end test passed")
    logger.info(f"  Generated {len(result['concepts'])} concepts")
    logger.info(f"  Selected confidence: {result['selected_concept']['confidence']:.2f}")
    logger.info(f"  Image size: {len(result['image_data'])} bytes")


if __name__ == '__main__':
    test_claude_enhancement()
    test_gemini_generation()
    test_end_to_end()
    logger.info("\n✓✓✓ All tests passed!")
```

---

## Configuration Changes

### Environment Variables

**Required additions to `.env`:**

```bash
# Already exists - verify these are set:
GEMINI_API_KEY=your_gemini_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

**Variables to remove (deprecated):**

```bash
# REMOVE or comment out:
# GEMINI_IMAGE_API_KEY=...  # Old name, replaced by GEMINI_API_KEY
# GCP_PROJECT_ID=...        # Not needed for Gemini 2.5 Flash Image
# VERTEX_AI_LOCATION=...    # Not needed
```

---

## Rollback Plan

### If Migration Fails

**Step 1: Revert code changes**
```bash
cd /Users/home/sandbox/daily_worker/projects/DWnews
git log --oneline -5  # Find commit before migration
git revert <commit-hash>  # Revert migration commit
```

**Step 2: Restore old dependencies**
```bash
pip uninstall google-genai
pip install google-cloud-aiplatform>=1.38.0
```

**Step 3: Revert database migration**
```sql
-- Rollback migration 006
DROP VIEW IF EXISTS article_selected_concepts;
DROP TABLE IF EXISTS article_image_concepts;
ALTER TABLE images DROP COLUMN IF EXISTS concept_confidence;
ALTER TABLE images DROP COLUMN IF EXISTS concept_rationale;
ALTER TABLE images DROP COLUMN IF EXISTS claude_enhancement_used;
```

**Step 4: Verify old implementation works**
```bash
python scripts/test_image_sourcing.py  # Test old Vertex AI approach
```

### Rollback Decision Criteria

Rollback if:
- [ ] Gemini 2.5 Flash Image generates significantly worse quality than Vertex AI
- [ ] Claude API costs exceed budget (>$10/month for 150 articles)
- [ ] Generation failures >20% (Vertex AI had ~10% failure rate)
- [ ] Generation time exceeds 45 seconds consistently (Vertex AI was 20-30s)
- [ ] Critical bugs discovered that block article publication

---

## Testing Plan

### Unit Tests

- [ ] Claude prompt enhancement generates 3-5 valid concepts
- [ ] Concept validation catches malformed responses
- [ ] Confidence scores are in valid range (0.0-1.0)
- [ ] Concept selection chooses highest confidence
- [ ] Gemini API integration handles auth, errors, retries
- [ ] Database storage of concepts works correctly

### Integration Tests

- [ ] End-to-end: Article → Concepts → Image → Storage
- [ ] Fallback cascade works (Claude fails → simple prompt → stock photos → placeholder)
- [ ] Cost tracking accurate
- [ ] Image optimization pipeline processes Gemini output
- [ ] Database transactions maintain integrity

### Quality Tests

**Test with 10 diverse articles:**
- [ ] 3 labor articles (union organizing, strikes, workplace safety)
- [ ] 2 politics articles (legislation, elections)
- [ ] 2 economy articles (wages, inflation, housing)
- [ ] 1 opinion piece
- [ ] 1 sports article
- [ ] 1 good news article

**Evaluation criteria:**
- Image relevance to article (1-5 scale)
- Visual quality (1-5 scale)
- Appropriate tone/mood (yes/no)
- Working-class perspective (yes/no)
- Would editor approve? (yes/no)

**Success criteria:**
- Average relevance ≥4.0
- Average quality ≥4.0
- Appropriate tone ≥80%
- Editor approval ≥70%

### Performance Tests

- [ ] Average latency ≤20 seconds (Claude + Gemini + processing)
- [ ] P95 latency ≤30 seconds
- [ ] Success rate ≥80%
- [ ] Fallback rate ≤15%
- [ ] Cost per image ≤$0.06

---

## Migration Checklist

### Pre-Migration

- [ ] Back up database
- [ ] Document current Vertex AI performance (success rate, latency, quality)
- [ ] Verify Claude API key has sufficient credits
- [ ] Verify Gemini API key works (test simple generation)
- [ ] Review migration plan with team

### Implementation (Phase 6.11.2)

- [ ] Install `google-genai` package
- [ ] Create `/backend/services/image_generation.py`
- [ ] Implement Claude enhancement service
- [ ] Implement Gemini generation service
- [ ] Write unit tests, verify all pass
- [ ] Test Claude + Gemini integration independently

### Implementation (Phase 6.11.3)

- [ ] Implement prompt enhancement workflow
- [ ] Create database migration 006
- [ ] Run migration on local database
- [ ] Verify tables created correctly
- [ ] Test concept storage and retrieval

### Implementation (Phase 6.11.4)

- [ ] Update `image_sourcing_agent.py` to use new service
- [ ] Remove old `generate_with_gemini` method
- [ ] Remove `generate_gemini_prompt` method
- [ ] Update `source_image_cascading` to call new method
- [ ] Test image sourcing agent end-to-end
- [ ] Verify fallback cascade works

### Implementation (Phase 6.11.5)

- [ ] Remove `google-cloud-aiplatform` dependency
- [ ] Clean up deprecated code
- [ ] Update documentation
- [ ] Run full test suite
- [ ] Generate 10 test images, evaluate quality
- [ ] Compare with old Vertex AI images (if available)
- [ ] Update agent instructions

### Post-Migration

- [ ] Monitor first 50 images for quality issues
- [ ] Track costs (Claude + Gemini)
- [ ] Collect editor feedback
- [ ] Adjust confidence scoring if needed
- [ ] Optimize prompts based on results
- [ ] Document lessons learned

---

## Risk Assessment

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Claude API costs exceed budget | Low | Medium | Monitor costs daily, implement rate limiting |
| Image quality worse than Vertex AI | Low | High | Quality tests before full switchover, keep rollback option |
| Generation failures increase | Medium | Medium | Robust retry logic, fallback cascade |
| Gemini rate limits hit frequently | Low | Medium | Implement request queuing, use free tier wisely |
| Database migration fails | Low | High | Test migration on copy first, have rollback SQL ready |
| Concept diversity too low | Medium | Low | Tune Claude prompt, validate diversity scores |

### Risk Mitigation Strategies

**Cost Overruns:**
- Set hard daily limit: $1/day for image generation
- Alert if Claude costs >$5/month
- Use simple prompts as fallback if budget exceeded

**Quality Issues:**
- Implement editor rating system for generated images
- A/B test Claude-enhanced vs. simple prompts
- Allow manual concept selection in admin portal

**Technical Failures:**
- Comprehensive retry logic with exponential backoff
- Multiple fallback levels (Claude → simple → stock → placeholder)
- Monitoring and alerting for API failures

---

## Success Metrics

### Definition of Success

Migration is successful if:

**Quality (Primary):**
- [ ] ≥70% of generated images meet editorial standards
- [ ] Average editor rating ≥4.0/5.0
- [ ] ≥80% of images used without manual replacement

**Performance:**
- [ ] Average generation time ≤20 seconds
- [ ] Success rate ≥80%
- [ ] System handles 10-15 articles/day without issues

**Cost:**
- [ ] Total cost ≤$10/month for 150 articles
- [ ] Cost per image ≤$0.06
- [ ] Within overall image generation budget ($15/month)

**Technical:**
- [ ] Zero critical bugs in first week
- [ ] Database integrity maintained
- [ ] Fallbacks work correctly
- [ ] Monitoring and alerting functional

---

## Timeline Estimate

| Phase | Estimated Time | Notes |
|-------|---------------|-------|
| 6.11.1 Research & Planning | 2-3 hours | Documentation (this document) |
| 6.11.2 Gemini Integration | 3-4 hours | New service, testing |
| 6.11.3 Claude Enhancement | 3-4 hours | Prompt enhancement, DB migration |
| 6.11.4 Update Pipeline | 2-3 hours | Integrate with existing agent |
| 6.11.5 Documentation & Testing | 2-3 hours | Quality tests, docs |
| **Total** | **12-17 hours** | ~2-3 days of focused work |

---

## Post-Migration Optimization

### Short-Term (First 2 Weeks)

- Collect editor ratings for 50+ images
- Analyze which concept types work best per category
- Tune confidence scoring based on results
- Optimize Claude prompt for better diversity

### Medium-Term (First Month)

- Implement concept diversity improvements
- Add editor-selectable concepts (choose from 3-5 options)
- Build analytics dashboard for concept performance
- A/B test different Claude prompts

### Long-Term (First Quarter)

- Fine-tune category-specific prompts
- Implement learning loop (successful concepts → better prompts)
- Explore Gemini Pro Image for highest-priority articles
- Consider caching popular concepts

---

**Document Status:** Complete
**Approval Required:** Yes (before executing migration)
**Review Date:** 2026-01-02
**Next Review:** After Phase 6.11.2 completion
