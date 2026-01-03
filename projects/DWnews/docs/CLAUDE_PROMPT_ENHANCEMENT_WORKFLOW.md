# Claude Prompt Enhancement Workflow - Design Specification

**Document Version:** 1.0
**Date:** 2026-01-02
**Project:** The Daily Worker (DWnews)
**Purpose:** Design specification for Claude Sonnet-powered image prompt enhancement

---

## Overview

The Claude Prompt Enhancement system uses Claude Sonnet 4.5 to generate 3-5 diverse, detailed artistic image concepts for each article. This two-step approach (Claude → Gemini) produces significantly higher-quality images than simple prompt wrapping.

**Problem Statement:**
Current approach generates generic prompts like "Workers in professional setting related to: {article_title}", resulting in uninspiring, low-quality images.

**Solution:**
Claude Sonnet analyzes article content and generates multiple artistic interpretations, each with:
- Detailed, specific prompt (style, composition, mood, technical specs)
- Confidence score (0.0-1.0) indicating suitability
- Rationale explaining artistic choices

**Proven Success:**
This exact approach used successfully in a-team project with excellent image quality results.

---

## Architecture

### System Flow

```
Article Data (headline, summary, category)
    ↓
Claude Sonnet API
    ↓
3-5 Artistic Concepts (prompts + confidence + rationale)
    ↓
Concept Selection (highest confidence score)
    ↓
Gemini 2.5 Flash Image API
    ↓
High-Quality Generated Image
    ↓
Storage + Database Recording
```

### Component Breakdown

1. **Input Preparation:** Extract article metadata (headline, summary, category, is_opinion)
2. **Claude Enhancement:** Generate 3-5 artistic concepts with detailed prompts
3. **Concept Selection:** Choose concept with highest confidence score
4. **Image Generation:** Pass selected prompt to Gemini 2.5 Flash Image
5. **Metadata Storage:** Store all concepts and selected concept details
6. **Quality Tracking:** Log concept performance for future optimization

---

## Claude Prompt Design

### Input Template

```python
CLAUDE_ENHANCEMENT_PROMPT = """You are an expert art director for a working-class news publication. Generate 3-5 diverse artistic image concepts for the following article.

**Article Details:**
- Headline: {headline}
- Summary: {summary}
- Category: {category}
- Is Opinion Piece: {is_opinion}

**Requirements:**
1. Generate 3-5 DISTINCT artistic concepts (different visual approaches)
2. Each concept should include:
   - Detailed image prompt (50-300 words, optimized for AI image generation)
   - Confidence score (0.0-1.0, higher = better fit for article)
   - Rationale (1-2 sentences explaining artistic choice)
3. Prioritize diversity: try different styles (photorealistic, editorial illustration, documentary, graphic, etc.)
4. Working-class perspective: dignified, empowering, authentic representation
5. Technical specs: horizontal 16:9 aspect ratio, professional quality

**Visual Style Options:**
- Documentary photography (authentic, photojournalistic)
- Editorial illustration (bold, graphic, metaphorical)
- Photorealistic rendering (detailed, realistic)
- Graphic novel aesthetic (stylized, high contrast)
- Historical photography style (black & white, archival feel)
- Modern digital art (clean, professional, contemporary)

**Output Format (JSON):**
{{
  "concepts": [
    {{
      "prompt": "Detailed image generation prompt here...",
      "confidence": 0.9,
      "rationale": "Explanation of why this concept fits the article..."
    }},
    // ... 2-4 more concepts
  ]
}}

Generate concepts now:"""
```

### Prompt Engineering Principles

**1. Specificity**
- Bad: "Image of workers"
- Good: "Documentary-style photograph showing diverse warehouse workers (Black, Latino, Asian, ages 25-55) organizing a union meeting in industrial break room, warm overhead lighting, authentic facial expressions showing determination and solidarity"

**2. Style Guidance**
- Always include artistic style (documentary, editorial, photorealistic, etc.)
- Specify mood/tone (dignified, empowering, hopeful, urgent)
- Include technical requirements (16:9, professional quality, specific lighting)

**3. Working-Class Perspective**
- Emphasize dignity and agency (not victimhood)
- Diverse representation (race, age, gender)
- Authentic settings (actual workplaces, communities)
- Avoid corporate stock photo aesthetics

**4. Diversity Across Concepts**
- Concept 1: Documentary photography
- Concept 2: Editorial illustration
- Concept 3: Photorealistic scene
- Concept 4: Graphic/stylized approach
- Concept 5: Historical or archival style

---

## Claude API Integration

### Request Format

```python
import anthropic

def enhance_prompt_with_claude(
    headline: str,
    summary: str,
    category: str,
    is_opinion: bool
) -> List[Dict]:
    """
    Generate 3-5 artistic image concepts using Claude Sonnet.

    Args:
        headline: Article headline
        summary: Article summary (first 2-3 paragraphs)
        category: Article category (labor, politics, etc.)
        is_opinion: Whether this is an opinion piece

    Returns:
        List of dicts with keys: prompt, confidence, rationale
    """

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    # Prepare prompt
    prompt = CLAUDE_ENHANCEMENT_PROMPT.format(
        headline=headline,
        summary=summary[:500],  # Limit summary length
        category=category,
        is_opinion=is_opinion
    )

    # Call Claude API
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        temperature=0.7,  # Moderate creativity
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    # Parse JSON response
    response_text = response.content[0].text

    # Extract JSON from markdown code block if present
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    concepts = json.loads(response_text)

    return concepts['concepts']
```

### Response Format

```json
{
  "concepts": [
    {
      "prompt": "Documentary-style photograph showing diverse warehouse workers (Black, Latino, Asian, ages 25-55) organizing a union meeting in industrial break room with fluorescent lighting, union pamphlets on table, workers leaning forward engaged in discussion, warm color palette emphasizing solidarity, horizontal 16:9 composition, photojournalistic quality, authentic facial expressions showing determination and hope",
      "confidence": 0.92,
      "rationale": "Documentary photography provides authenticity and credibility for union organizing story. Warm lighting and engaged body language convey solidarity without being heavy-handed. Diverse representation reflects real warehouse demographics."
    },
    {
      "prompt": "Bold editorial illustration featuring stylized workers holding raised fists and union signs, high-contrast red black and yellow color scheme, graphic novel aesthetic with clean lines and strong shapes, workers shown from low angle emphasizing power and dignity, horizontal 16:9 format, reminiscent of 1930s labor movement posters but with modern clean design",
      "confidence": 0.87,
      "rationale": "Editorial illustration allows for more dramatic visual impact and clearer messaging about worker power. Color palette evokes traditional labor movement aesthetics while modern clean style keeps it contemporary and accessible."
    },
    {
      "prompt": "Photorealistic rendering of union organizers meeting with warehouse workers during shift break, industrial warehouse background with high ceilings and equipment, workers in safety vests and work clothes, natural expressions of interest and cautious optimism, daylight streaming through loading dock doors creating dramatic side lighting, horizontal 16:9 professional photography quality",
      "confidence": 0.85,
      "rationale": "Photorealistic approach grounds the story in tangible reality. Industrial setting and work attire emphasize this is about real working people. Natural lighting and genuine expressions avoid staged stock photo feel."
    },
    {
      "prompt": "Split-composition graphic showing contrast between isolated worker (left side, muted colors, alone at workstation) and united workers (right side, vibrant colors, standing together), modern digital art style with clean vector-like aesthetic, symbolic representation of collective action, horizontal 16:9 format, professional illustration quality",
      "confidence": 0.78,
      "rationale": "Metaphorical split-composition clearly illustrates the article's core message about strength in unity. More conceptual approach works well for opinion pieces or analysis articles. Risk: might be too abstract for some readers."
    },
    {
      "prompt": "Black and white archival-style photograph reminiscent of 1960s labor movement documentation, workers gathered outside factory gates at dawn, hand-painted union signs, grainy film texture, strong contrast and dramatic shadows, horizontal 16:9 format, documentary photography aesthetic that evokes historical labor struggles while showing contemporary workers",
      "confidence": 0.73,
      "rationale": "Historical aesthetic connects current organizing to proud labor movement tradition. Black and white treatment adds gravitas and timelessness. Risk: might feel dated if execution is too literal; confidence score reflects this uncertainty."
    }
  ]
}
```

---

## Confidence Scoring Rubric

### Scoring Criteria (0.0-1.0 scale)

**High Confidence (0.85-1.0)**
- Perfect alignment with article theme and tone
- Strong visual impact and clarity
- Appropriate for target audience
- Technically achievable with AI generation
- Working-class perspective authentically represented

**Medium-High Confidence (0.75-0.84)**
- Good alignment with article
- Solid visual approach
- Minor concerns about execution or fit
- Generally appropriate for audience

**Medium Confidence (0.65-0.74)**
- Acceptable but not ideal fit
- Some artistic risk or uncertainty
- Might require fallback options
- Partial alignment with article themes

**Low Confidence (0.50-0.64)**
- Weak alignment or significant concerns
- High execution risk
- May not resonate with audience
- Should only use if other concepts fail

**Very Low Confidence (<0.50)**
- Poor fit for article
- Likely to produce unsatisfactory results
- Not recommended for use
- Include only for diversity/learning purposes

### Confidence Score Calculation Factors

Claude should consider:
1. **Thematic alignment** (35%): How well does concept match article message?
2. **Visual clarity** (25%): Will concept be immediately understandable?
3. **Technical feasibility** (20%): Can AI generate this effectively?
4. **Audience appropriateness** (15%): Right tone for working-class readers?
5. **Originality** (5%): Avoids clichés and stock photo aesthetics?

---

## Concept Selection Logic

### Primary Selection Rule

**Select concept with highest confidence score**

```python
def select_best_concept(concepts: List[Dict]) -> Dict:
    """Select concept with highest confidence score"""

    if not concepts:
        raise ValueError("No concepts provided")

    # Sort by confidence descending
    sorted_concepts = sorted(
        concepts,
        key=lambda c: c['confidence'],
        reverse=True
    )

    best_concept = sorted_concepts[0]

    logger.info(
        f"Selected concept with confidence {best_concept['confidence']:.2f}: "
        f"{best_concept['prompt'][:100]}..."
    )

    return best_concept
```

### Fallback Rules

**If all confidence scores < 0.70:**
- Log warning about low-confidence concepts
- Attempt generation with highest-scored concept anyway
- If generation fails, fall back to stock photos
- Flag article for manual image selection

**If Claude API fails:**
- Use simple prompt wrapping as fallback
- Log error for investigation
- Consider queuing for retry when API recovers

---

## Database Schema

### article_image_concepts Table

```sql
CREATE TABLE article_image_concepts (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    concept_number INTEGER NOT NULL,          -- 1-5 (order from Claude)
    prompt TEXT NOT NULL,                     -- Full image generation prompt
    confidence DECIMAL(3,2) NOT NULL,         -- 0.00-1.00
    rationale TEXT NOT NULL,                  -- Explanation of concept
    selected BOOLEAN DEFAULT FALSE,           -- True for chosen concept
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(article_id, concept_number),
    INDEX(article_id),
    INDEX(selected),
    INDEX(confidence)
);
```

### images Table Updates

Add columns to existing `images` table:

```sql
ALTER TABLE images ADD COLUMN concept_confidence DECIMAL(3,2);
ALTER TABLE images ADD COLUMN concept_rationale TEXT;
ALTER TABLE images ADD COLUMN claude_enhancement_used BOOLEAN DEFAULT FALSE;
```

### Storage Example

```python
def store_concepts(article_id: int, concepts: List[Dict], selected_index: int):
    """Store all concepts and mark selected one"""

    for i, concept in enumerate(concepts, start=1):
        db.execute("""
            INSERT INTO article_image_concepts
            (article_id, concept_number, prompt, confidence, rationale, selected)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            article_id,
            i,
            concept['prompt'],
            concept['confidence'],
            concept['rationale'],
            i == (selected_index + 1)  # Mark selected concept
        ))

    # Also store in images table for quick access
    selected_concept = concepts[selected_index]
    db.execute("""
        UPDATE images
        SET concept_confidence = ?,
            concept_rationale = ?,
            claude_enhancement_used = TRUE
        WHERE article_id = ?
    """, (
        selected_concept['confidence'],
        selected_concept['rationale'],
        article_id
    ))
```

---

## Cost Analysis

### Per-Article Cost Breakdown

**Claude API (Sonnet 4.5):**
- Input tokens: ~500-800 tokens (prompt + article data)
- Output tokens: ~800-1200 tokens (3-5 concepts with details)
- Cost: $0.01-0.02 per enhancement

**Gemini 2.5 Flash Image:**
- Image generation: $0.02-0.04 per image (or free tier)
- Cost: $0.02-0.04 per image

**Total Cost per Image:**
- Claude + Gemini: $0.03-0.06 per image
- Stock photo (fallback): $0 (free tier APIs)
- **Average:** ~$0.04 per image

### Monthly Cost Projection (MVP)

**Scenario: 5 articles/day × 30 days = 150 articles/month**

| Component | Per Image | Monthly (150 images) |
|-----------|-----------|---------------------|
| Claude enhancement | $0.01-0.02 | $1.50-3.00 |
| Gemini generation | $0.02-0.04 | $3.00-6.00 |
| **Total** | **$0.03-0.06** | **$4.50-9.00** |

**Conclusion:** Well within $15/month image generation budget

---

## Performance Optimization

### Latency Breakdown

| Step | Time | Notes |
|------|------|-------|
| Claude API call | 3-7s | Generate 3-5 concepts |
| Concept selection | <0.1s | Local processing |
| Gemini API call | 10-15s | Image generation |
| Image optimization | 1-2s | Resize, convert to JPEG |
| **Total** | **14-24s** | End-to-end per image |

### Parallel Processing (Future Optimization)

For faster processing when generating multiple images:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def generate_images_parallel(articles: List[Dict]) -> List[Dict]:
    """Generate images for multiple articles in parallel"""

    with ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(
                executor,
                generate_with_claude_enhancement,
                article
            )
            for article in articles
        ]

        results = await asyncio.gather(*tasks)

    return results
```

**Benefit:** Process 3 articles simultaneously, reducing total time from 60s to 24s

---

## Quality Assurance

### Validation Checks

**1. Claude Response Validation**
```python
def validate_claude_response(concepts: List[Dict]) -> bool:
    """Validate Claude output meets requirements"""

    # Check minimum concepts
    if len(concepts) < 3:
        logger.warning(f"Only {len(concepts)} concepts generated, expected 3-5")
        return False

    # Validate each concept
    for i, concept in enumerate(concepts):
        # Required fields
        if not all(k in concept for k in ['prompt', 'confidence', 'rationale']):
            logger.error(f"Concept {i+1} missing required fields")
            return False

        # Confidence range
        if not 0.0 <= concept['confidence'] <= 1.0:
            logger.error(f"Concept {i+1} has invalid confidence: {concept['confidence']}")
            return False

        # Prompt length
        if len(concept['prompt']) < 50:
            logger.warning(f"Concept {i+1} has very short prompt (<50 chars)")

        if len(concept['prompt']) > 2000:
            logger.error(f"Concept {i+1} prompt too long (>2000 chars)")
            return False

    return True
```

**2. Concept Diversity Check**
```python
def check_concept_diversity(concepts: List[Dict]) -> float:
    """Measure diversity of concepts (0.0-1.0)"""

    prompts = [c['prompt'].lower() for c in concepts]

    # Check for keyword overlap
    style_keywords = {
        'documentary', 'editorial', 'photorealistic', 'illustration',
        'graphic', 'archival', 'modern', 'historical'
    }

    styles_used = set()
    for prompt in prompts:
        for keyword in style_keywords:
            if keyword in prompt:
                styles_used.add(keyword)

    # Diversity score = unique styles / total concepts
    diversity_score = len(styles_used) / len(concepts)

    if diversity_score < 0.5:
        logger.warning(f"Low concept diversity: {diversity_score:.2f}")

    return diversity_score
```

### Testing Strategy

**Unit Tests:**
- Claude API response parsing
- Confidence score validation
- Concept selection logic
- Database storage

**Integration Tests:**
- End-to-end workflow (article → concepts → image)
- Fallback handling (Claude fails → simple prompt)
- Database transaction integrity

**Quality Tests:**
- Generate images for 10 sample articles
- Human evaluation of concept quality
- Compare Claude-enhanced vs. simple prompts
- Measure improvement in image relevance/quality

---

## Error Handling & Fallbacks

### Error Scenarios

**1. Claude API Failure**
```python
def generate_concepts_with_fallback(article: Dict) -> List[Dict]:
    """Generate concepts with fallback to simple prompts"""

    try:
        # Attempt Claude enhancement
        concepts = enhance_prompt_with_claude(
            headline=article['headline'],
            summary=article['summary'],
            category=article['category'],
            is_opinion=article['is_opinion']
        )

        if validate_claude_response(concepts):
            return concepts
        else:
            logger.warning("Claude response validation failed, using fallback")

    except Exception as e:
        logger.error(f"Claude API failed: {e}")

    # Fallback: Generate simple concepts
    return generate_simple_concepts(article)
```

**2. Low Confidence Scores**
```python
def handle_low_confidence(concepts: List[Dict]) -> Dict:
    """Handle case where all concepts have low confidence"""

    best_concept = max(concepts, key=lambda c: c['confidence'])

    if best_concept['confidence'] < 0.70:
        logger.warning(
            f"All concepts have low confidence (best: {best_concept['confidence']:.2f}). "
            "Proceeding with best concept but flagging for manual review."
        )

        # Flag article for manual image selection
        db.execute("""
            UPDATE articles
            SET needs_manual_image_review = TRUE
            WHERE id = ?
        """, (article_id,))

    return best_concept
```

**3. Complete Generation Failure**
```python
def fallback_cascade(article: Dict) -> Dict:
    """Complete fallback cascade if all generation fails"""

    # Step 1: Try Claude + Gemini
    try:
        concepts = enhance_prompt_with_claude(article)
        selected = select_best_concept(concepts)
        image = generate_with_gemini(selected['prompt'])
        if image:
            return image
    except Exception as e:
        logger.error(f"Claude+Gemini failed: {e}")

    # Step 2: Try simple prompt + Gemini
    try:
        simple_prompt = generate_simple_prompt(article)
        image = generate_with_gemini(simple_prompt)
        if image:
            return image
    except Exception as e:
        logger.error(f"Simple+Gemini failed: {e}")

    # Step 3: Stock photos
    try:
        image = search_stock_photos(article['headline'])
        if image:
            return image
    except Exception as e:
        logger.error(f"Stock photos failed: {e}")

    # Step 4: Placeholder
    return get_category_placeholder(article['category'])
```

---

## Analytics & Continuous Improvement

### Metrics to Track

**Concept Performance:**
- Average confidence score per category
- Correlation between confidence score and image quality
- Most common selected concept position (1st, 2nd, 3rd, etc.)
- Diversity score distribution

**Cost Metrics:**
- Claude API cost per article
- Total enhancement cost per month
- Cost savings vs. simple prompting

**Quality Metrics:**
- Editor satisfaction ratings (manual review)
- Image usage rate (selected vs. manually replaced)
- Fallback rate (how often Claude fails)

### Learning Loop

```python
def analyze_concept_performance():
    """Analyze which concepts perform best"""

    query = """
        SELECT
            category,
            AVG(confidence) as avg_confidence,
            COUNT(*) as total_concepts,
            SUM(CASE WHEN selected = TRUE THEN 1 ELSE 0 END) as selected_count,
            AVG(CASE WHEN selected = TRUE THEN confidence END) as avg_selected_confidence
        FROM article_image_concepts
        JOIN articles ON articles.id = article_image_concepts.article_id
        GROUP BY category
        ORDER BY avg_selected_confidence DESC
    """

    results = db.execute(query)

    # Identify patterns
    # - Which categories need prompt tuning?
    # - Are high-confidence concepts actually selected?
    # - Should we adjust confidence scoring?

    return results
```

---

## Implementation Checklist

- [ ] Create `backend/services/prompt_enhancement.py`
- [ ] Implement Claude API integration
- [ ] Create concept validation logic
- [ ] Implement concept selection algorithm
- [ ] Create database migration for `article_image_concepts` table
- [ ] Update `images` table with new columns
- [ ] Write unit tests for prompt enhancement
- [ ] Write integration tests for full workflow
- [ ] Create analytics queries for performance tracking
- [ ] Document fallback procedures
- [ ] Test with 10 real articles
- [ ] Measure quality improvement vs. simple prompts
- [ ] Update agent instructions (journalist.md, editorial-coordinator.md)
- [ ] Create editor training materials

---

**Document Status:** Complete
**Next Steps:** See `IMAGEN_TO_GEMINI_MIGRATION.md` for migration implementation plan
