"""
Source Ranker

Ranks sources by credibility using a hierarchical system:
Tier 1 - Named Primary Sources (government docs, academic papers, official statements)
Tier 2 - Organizational Sources (reputable news agencies, investigative outlets)
Tier 3 - Documentary Evidence (public records, verified social media)
Tier 4 - Anonymous/Unverified (anonymous sources, unverified social media)
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RankedSource:
    """Source with credibility ranking"""
    name: str
    url: str
    source_type: str
    credibility_tier: int  # 1-4 (1 is highest)
    credibility_score: float  # 0-100
    rank: int  # Overall rank in list
    reasoning: str  # Explanation for ranking


class SourceRanker:
    """
    Ranks sources by credibility using a hierarchical system
    """

    # Tier 1: Named Primary Sources (credibility: 90-100)
    TIER1_DOMAINS = [
        # Government domains
        '.gov', 'nlrb.gov', 'osha.gov', 'dol.gov', 'sec.gov', 'ftc.gov',
        'uscourts.gov', 'bls.gov', 'census.gov',

        # Academic/Research
        'scholar.google', 'arxiv.org', 'jstor.org', '.edu',
        'sciencedirect.com', 'springer.com', 'nature.com', 'science.org'
    ]

    # Tier 2: Organizational Sources (credibility: 70-89)
    TIER2_DOMAINS = [
        # Major news agencies
        'reuters.com', 'apnews.com', 'bloomberg.com',

        # Investigative journalism
        'propublica.org', 'themarkup.org', 'theintercept.com',

        # Major newspapers
        'nytimes.com', 'washingtonpost.com', 'wsj.com',

        # Broadcast news
        'npr.org', 'pbs.org', 'bbc.com',

        # Labor news specialists
        'labornotes.org', 'inthesetimes.com'
    ]

    # Tier 3: Documentary Evidence (credibility: 50-69)
    TIER3_DOMAINS = [
        # Other news outlets
        'theguardian.com', 'cnn.com', 'foxnews.com', 'msnbc.com',
        'politico.com', 'axios.com', 'thehill.com',

        # Business news
        'forbes.com', 'businessinsider.com', 'cnbc.com',

        # Regional outlets
        'latimes.com', 'chicagotribune.com', 'bostonglobe.com'
    ]

    # Tier 4: Anonymous/Unverified (credibility: 0-49)
    TIER4_INDICATORS = [
        'twitter.com', 'facebook.com', 'reddit.com',
        'medium.com', 'substack.com', 'blog', 'wordpress'
    ]

    def __init__(self):
        """Initialize the source ranker"""
        pass

    def rank_sources(self, sources: List[Dict]) -> List[RankedSource]:
        """
        Rank sources by credibility

        Args:
            sources: List of source dicts (must have 'url', 'name', 'source_type')

        Returns:
            List of RankedSource objects, sorted by credibility (highest first)
        """
        ranked_sources = []

        for source in sources:
            url = source.get('url', '')
            name = source.get('name', 'Unknown')
            source_type = source.get('source_type', 'unknown')

            # Determine credibility tier
            tier, score, reasoning = self._determine_tier(url, source_type, name)

            ranked_source = RankedSource(
                name=name,
                url=url,
                source_type=source_type,
                credibility_tier=tier,
                credibility_score=score,
                rank=0,  # Will be set after sorting
                reasoning=reasoning
            )

            ranked_sources.append(ranked_source)

        # Sort by credibility score (highest first)
        ranked_sources.sort(key=lambda x: x.credibility_score, reverse=True)

        # Assign ranks
        for i, source in enumerate(ranked_sources):
            source.rank = i + 1

        return ranked_sources

    def _determine_tier(self, url: str, source_type: str, name: str) -> tuple[int, float, str]:
        """
        Determine credibility tier, score, and reasoning

        Args:
            url: Source URL
            source_type: Type of source
            name: Source name

        Returns:
            Tuple of (tier, score, reasoning)
        """
        url_lower = url.lower()
        name_lower = name.lower()

        # Tier 1: Named Primary Sources
        if self._is_tier1(url_lower, source_type):
            if source_type == 'government_document':
                return (1, 100, "Official government document")
            elif source_type == 'court_document':
                return (1, 98, "Official court filing")
            elif source_type == 'academic':
                return (1, 95, "Peer-reviewed academic source")
            elif source_type == 'organization_statement':
                return (1, 92, "Official organization statement")
            else:
                return (1, 90, "Tier 1 primary source")

        # Tier 2: Organizational Sources
        elif self._is_tier2(url_lower, source_type, name_lower):
            if 'reuters' in url_lower or 'ap' in name_lower:
                return (2, 89, "Major news wire service")
            elif 'propublica' in url_lower or 'themarkup' in url_lower:
                return (2, 87, "Investigative journalism outlet")
            elif 'nytimes' in url_lower or 'washingtonpost' in url_lower:
                return (2, 85, "Major national newspaper")
            elif 'labornotes' in url_lower:
                return (2, 83, "Labor news specialist")
            else:
                return (2, 80, "Reputable news organization")

        # Tier 3: Documentary Evidence
        elif self._is_tier3(url_lower, source_type):
            if source_type == 'news_agency':
                return (3, 65, "Established news outlet")
            elif 'verified' in name_lower or 'official' in name_lower:
                return (3, 60, "Verified account/source")
            else:
                return (3, 55, "Documentary evidence")

        # Tier 4: Anonymous/Unverified
        else:
            if source_type == 'social_media':
                return (4, 40, "Social media source (unverified)")
            elif 'blog' in url_lower or 'medium' in url_lower:
                return (4, 35, "Blog/personal publication")
            else:
                return (4, 30, "Unverified or anonymous source")

    def _is_tier1(self, url: str, source_type: str) -> bool:
        """Check if source belongs to Tier 1"""
        # Check source type
        if source_type in ['government_document', 'court_document', 'academic', 'official_record']:
            return True

        # Check URL
        return any(domain in url for domain in self.TIER1_DOMAINS)

    def _is_tier2(self, url: str, source_type: str, name: str) -> bool:
        """Check if source belongs to Tier 2"""
        # Check URL domains
        for domain in self.TIER2_DOMAINS:
            if domain in url:
                return True

        # Check source type
        if source_type in ['news_wire', 'investigative']:
            return True

        # Check name for known outlets
        tier2_names = [
            'reuters', 'associated press', 'bloomberg', 'propublica',
            'new york times', 'washington post', 'npr', 'bbc'
        ]
        return any(outlet in name for outlet in tier2_names)

    def _is_tier3(self, url: str, source_type: str) -> bool:
        """Check if source belongs to Tier 3"""
        # Check URL domains
        for domain in self.TIER3_DOMAINS:
            if domain in url:
                return True

        # Check source type
        if source_type in ['news_agency', 'local_news']:
            return True

        return False

    def filter_by_tier(self, ranked_sources: List[RankedSource], max_tier: int) -> List[RankedSource]:
        """
        Filter sources to only include up to a certain tier

        Args:
            ranked_sources: List of ranked sources
            max_tier: Maximum tier to include (1-4)

        Returns:
            Filtered list of sources
        """
        return [source for source in ranked_sources if source.credibility_tier <= max_tier]

    def get_credible_sources(self, ranked_sources: List[RankedSource], min_score: float = 70.0) -> List[RankedSource]:
        """
        Get sources above a minimum credibility score

        Args:
            ranked_sources: List of ranked sources
            min_score: Minimum credibility score

        Returns:
            Filtered list of credible sources
        """
        return [source for source in ranked_sources if source.credibility_score >= min_score]

    def validate_source_threshold(self, ranked_sources: List[RankedSource]) -> Dict:
        """
        Check if sources meet verification threshold:
        - ≥3 credible sources (Tier 1 or Tier 2), OR
        - ≥2 academic citations

        Args:
            ranked_sources: List of ranked sources

        Returns:
            Dict with validation results
        """
        # Count credible sources (Tier 1 or Tier 2)
        credible_sources = [s for s in ranked_sources if s.credibility_tier <= 2]

        # Count academic sources specifically
        academic_sources = [
            s for s in ranked_sources
            if s.source_type == 'academic' or 'academic' in s.reasoning.lower()
        ]

        meets_threshold = (len(credible_sources) >= 3) or (len(academic_sources) >= 2)

        return {
            'meets_threshold': meets_threshold,
            'credible_sources_count': len(credible_sources),
            'academic_sources_count': len(academic_sources),
            'tier1_count': len([s for s in ranked_sources if s.credibility_tier == 1]),
            'tier2_count': len([s for s in ranked_sources if s.credibility_tier == 2]),
            'tier3_count': len([s for s in ranked_sources if s.credibility_tier == 3]),
            'tier4_count': len([s for s in ranked_sources if s.credibility_tier == 4]),
            'threshold_met_by': 'credible_sources' if len(credible_sources) >= 3
                               else 'academic_citations' if len(academic_sources) >= 2
                               else None
        }

    def get_ranking_summary(self, ranked_sources: List[RankedSource]) -> str:
        """
        Get human-readable summary of source rankings

        Args:
            ranked_sources: List of ranked sources

        Returns:
            Formatted summary string
        """
        lines = ["Source Rankings:"]
        lines.append("=" * 60)

        for source in ranked_sources:
            lines.append(
                f"{source.rank}. [{source.name}] "
                f"(Tier {source.credibility_tier}, Score: {source.credibility_score:.1f}) "
                f"- {source.reasoning}"
            )

        validation = self.validate_source_threshold(ranked_sources)
        lines.append("=" * 60)
        lines.append(f"Credible sources (Tier 1-2): {validation['credible_sources_count']}")
        lines.append(f"Academic citations: {validation['academic_sources_count']}")
        lines.append(f"Meets threshold: {'YES' if validation['meets_threshold'] else 'NO'}")

        return "\n".join(lines)
