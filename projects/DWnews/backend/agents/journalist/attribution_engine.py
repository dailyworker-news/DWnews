"""
Attribution Engine - Proper Source Attribution
Generates properly attributed article text using source plan and verified facts
"""

import json
from typing import Dict, List, Any, Optional


class AttributionEngine:
    """
    Generates properly attributed article content.
    Uses source_plan to determine attribution strategy and verified_facts for content.
    """

    def __init__(self):
        """Initialize attribution engine"""
        pass

    def generate_attribution_prompt(
        self,
        topic_title: str,
        verified_facts: Dict[str, Any],
        source_plan: Dict[str, Any]
    ) -> str:
        """
        Generate LLM prompt with proper attribution instructions.

        Args:
            topic_title: Topic title from database
            verified_facts: JSON from topics.verified_facts
            source_plan: JSON from topics.source_plan

        Returns:
            str: Formatted prompt for LLM article generation
        """
        # Extract sources by tier
        sources = source_plan.get("sources", [])
        primary_sources = [s for s in sources if s.get("tier") == "primary"]
        supporting_sources = [s for s in sources if s.get("tier") == "supporting"]

        # Extract high-confidence facts
        facts = verified_facts.get("facts", [])
        high_confidence_facts = [f for f in facts if f.get("confidence") == "high"]

        # Extract attribution strategy
        attribution_strategy = source_plan.get("attribution_strategy", "Standard attribution")

        # Build fact list with attribution guidance
        fact_list = self._build_fact_list(high_confidence_facts)

        # Build source list
        source_list = self._build_source_list(primary_sources, supporting_sources)

        prompt = f"""Write a worker-centric news article about: {topic_title}

VERIFIED FACTS (use ONLY these facts):
{fact_list}

PRIMARY SOURCES (cite prominently):
{source_list['primary']}

SUPPORTING SOURCES (use for context):
{source_list['supporting']}

ATTRIBUTION STRATEGY:
{attribution_strategy}

ATTRIBUTION REQUIREMENTS:
1. Primary sources must be cited by name in the lead/opening paragraphs
2. All factual claims must be attributed using appropriate language:
   - Observed facts: "According to [source], X happened"
   - Claimed facts: "[Source] reported that X"
   - Interpreted facts: "[Source] analyzed that X suggests Y"
3. Use direct quotes when available in verified facts
4. Attribute statistics and numbers to specific sources
5. For conflicting information, present both perspectives with clear attribution
6. Avoid unsourced claims or speculation

ARTICLE REQUIREMENTS:
- Reading level: 7.5-8.5 Flesch-Kincaid (high school freshman)
- Word count: 400-800 words for news, 600-1200 for analysis
- Active voice (80%+ of sentences)
- Worker-centric framing throughout
- No corporate PR language or euphemisms
- Punchy, direct writing that doesn't pull punches
- Include specific details: numbers, dates, names from verified facts

CRITICAL ANALYSIS REQUIREMENTS (develop independent voice):
You are not a stenographer - you are an investigative journalist with an independent perspective. Your job is to question, contextualize, and analyze, not just report.

1. SCALE & PROPORTION ANALYSIS:
   - When numbers are cited (funding, jobs, wages), ask: Is this substantial given the scale of the problem?
   - Calculate per-person or per-worker impacts when relevant
   - Example: "$98M for youth training" → How many workers does this serve? What's the per-worker funding? How does this compare to the need?

2. POWER & BENEFICIARY ANALYSIS:
   - Who benefits from the current situation/problem?
   - Who has power in this story and how are they using it?
   - Follow the money: Who profits? Who pays?
   - Example: "Training gap" → Who benefits from inadequate worker training? Employers who can pay less?

3. HISTORICAL CONTEXT:
   - How does this compare to past efforts/funding/policies?
   - Is this a new problem or a recurring pattern?
   - What precedents exist?
   - Example: Compare current funding to historical levels (adjusted for inflation)

4. STRUCTURAL ANALYSIS:
   - What systemic issues does this reveal?
   - Is this addressing symptoms or root causes?
   - What power structures are being challenged or reinforced?
   - Example: "Job training program" → Why do workers lack skills in the first place? Failure of education system? Employer disinvestment in training?

5. QUESTION OFFICIAL NARRATIVES:
   - Government/corporate press releases are starting points, not endpoints
   - Challenge assumptions and PR framing
   - Ask "why now?" and "who benefits?"
   - Example: Press release says "investment in workforce" → Is this really investment, or cost-shifting from employers to taxpayers?

6. WORKER IMPACT FOCUS:
   - What does this mean for individual workers in concrete terms?
   - Move beyond statistics to real-world implications
   - Example: "$15/hour minimum wage" → What can workers actually afford with this? Compare to local rent, groceries, childcare costs

7. SKEPTICAL BUT FAIR:
   - Be critical without being cynical
   - Challenge claims with evidence, not speculation
   - Present counterarguments when relevant
   - Maintain fairness while centering worker perspective

INTEGRATE CRITICAL ANALYSIS INTO ARTICLE BODY:
- Don't add a separate "Analysis" section - weave critical perspective throughout
- Lead with facts, follow with context and critical questions
- Use phrases like: "That figure represents...", "To put this in perspective...", "Critics note...", "However, the deeper issue is..."
- Make connections between individual stories and systemic patterns

STRUCTURE:
1. Headline (compelling, worker-impact focused)
2. Lead paragraph (Who/What/When/Where - cite primary source)
3. Nut graf (Why it matters to workers - include critical context)
4. Body (Details with proper attribution AND critical analysis integrated throughout)
5. "Why This Matters" section (worker impact with structural analysis)
6. "What You Can Do" section (actionable steps)

Generate the complete article now with critical analysis integrated throughout."""

        return prompt

    def _build_fact_list(self, facts: List[Dict[str, Any]]) -> str:
        """Build formatted fact list with attribution guidance"""
        if not facts:
            return "(No high-confidence facts available)"

        fact_lines = []
        for i, fact in enumerate(facts, 1):
            fact_text = fact.get("fact", "")
            fact_type = fact.get("type", "observed")
            sources = fact.get("sources", [])

            # Handle both string URLs and dict sources
            source_names_list = []
            for s in sources:
                if isinstance(s, dict):
                    source_names_list.append(s.get("name", "Unknown"))
                elif isinstance(s, str):
                    # Extract domain from URL
                    from urllib.parse import urlparse
                    domain = urlparse(s).netloc.replace('www.', '')
                    source_names_list.append(domain or "Unknown")
            source_names = ", ".join(source_names_list) if source_names_list else "Unknown"

            attribution_style = self._get_attribution_style(fact_type)

            fact_lines.append(
                f"{i}. [{fact_type.upper()}] {fact_text}\n"
                f"   Sources: {source_names}\n"
                f"   Attribution style: {attribution_style}"
            )

        return "\n".join(fact_lines)

    def _get_attribution_style(self, fact_type: str) -> str:
        """Get attribution style based on fact type"""
        styles = {
            "observed": "According to [source], [fact]",
            "claimed": "[Source] reported that [fact]",
            "interpreted": "[Source] analyzed that [fact]",
            "statistical": "[Source] found that [fact]",
        }
        return styles.get(fact_type, "According to [source], [fact]")

    def _build_source_list(
        self,
        primary_sources: List[Dict[str, Any]],
        supporting_sources: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Build formatted source lists"""
        primary_list = []
        for source in primary_sources:
            name = source.get("name", "Unknown")
            credibility = source.get("credibility_tier", "unknown")
            url = source.get("url", "")

            primary_list.append(
                f"- {name} (credibility: {credibility})\n"
                f"  URL: {url}"
            )

        supporting_list = []
        for source in supporting_sources:
            name = source.get("name", "Unknown")
            credibility = source.get("credibility_tier", "unknown")

            supporting_list.append(f"- {name} (credibility: {credibility})")

        return {
            "primary": "\n".join(primary_list) if primary_list else "(None)",
            "supporting": "\n".join(supporting_list) if supporting_list else "(None)"
        }

    def extract_attributions(self, article_text: str) -> List[Dict[str, str]]:
        """
        Extract attribution phrases from generated article.
        Useful for validation.

        Returns:
            List of dicts with attribution phrases and sources
        """
        attributions = []

        # Common attribution patterns
        attribution_patterns = [
            r'according to ([^,]+)',
            r'([^,]+) reported that',
            r'([^,]+) said',
            r'([^,]+) stated',
            r'([^,]+) found that',
            r'([^,]+) analyzed that',
            r'data from ([^,]+)',
            r'([^,]+) disclosed',
        ]

        import re
        for pattern in attribution_patterns:
            matches = re.finditer(pattern, article_text, re.IGNORECASE)
            for match in matches:
                source = match.group(1).strip()
                context = match.group(0)
                attributions.append({
                    "source": source,
                    "phrase": context,
                    "position": match.start()
                })

        return attributions

    def validate_attribution_coverage(
        self,
        article_text: str,
        source_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that primary sources are properly cited in article.

        Returns:
            Dict with coverage stats and missing sources
        """
        sources = source_plan.get("sources", [])
        primary_sources = [s for s in sources if s.get("tier") == "primary"]

        cited_sources = []
        missing_sources = []

        for source in primary_sources:
            source_name = source.get("name", "").lower()
            if source_name in article_text.lower():
                cited_sources.append(source["name"])
            else:
                missing_sources.append(source["name"])

        coverage_percentage = (
            (len(cited_sources) / len(primary_sources) * 100)
            if primary_sources else 0
        )

        return {
            "total_primary_sources": len(primary_sources),
            "cited_sources": cited_sources,
            "missing_sources": missing_sources,
            "coverage_percentage": round(coverage_percentage, 1),
            "meets_standard": coverage_percentage >= 80  # 80% minimum
        }

    def format_source_citations(
        self,
        source_plan: Dict[str, Any]
    ) -> str:
        """
        Format source citations for article footer.

        Returns:
            Formatted source list for article
        """
        sources = source_plan.get("sources", [])

        if not sources:
            return ""

        citation_lines = ["## Sources\n"]

        for i, source in enumerate(sources, 1):
            name = source.get("name", "Unknown")
            url = source.get("url", "")
            tier = source.get("tier", "unknown")

            if url:
                citation_lines.append(f"{i}. {name} ({tier}) - {url}")
            else:
                citation_lines.append(f"{i}. {name} ({tier})")

        return "\n".join(citation_lines)
