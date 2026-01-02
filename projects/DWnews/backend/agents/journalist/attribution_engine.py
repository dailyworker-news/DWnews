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

STRUCTURE:
1. Headline (compelling, worker-impact focused)
2. Lead paragraph (Who/What/When/Where - cite primary source)
3. Nut graf (Why it matters to workers)
4. Body (Details with proper attribution)
5. "Why This Matters" section (worker impact)
6. "What You Can Do" section (actionable steps)

Generate the complete article now."""

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

            source_names = ", ".join([s.get("name", "Unknown") for s in sources])

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
