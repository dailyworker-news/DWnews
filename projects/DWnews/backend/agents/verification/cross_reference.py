"""
Cross-Reference Verifier

Compares claims across multiple sources to verify consistency and detect conflicts.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Fact:
    """Represents a factual claim"""
    claim: str
    sources: List[str]  # URLs that mention this fact
    confidence: str  # high, medium, low
    conflicting_info: Optional[str] = None


@dataclass
class VerificationResult:
    """Result of cross-reference verification"""
    verified_facts: List[Fact]
    conflicting_claims: List[Dict]
    source_agreement_score: float  # 0-1 (how much sources agree)
    total_sources_checked: int


class CrossReferenceVerifier:
    """
    Verifies claims by comparing information across multiple sources
    """

    def __init__(self):
        """Initialize the cross-reference verifier"""
        pass

    def verify_claims(self, facts: List[str], sources: List[Dict]) -> VerificationResult:
        """
        Verify a list of factual claims by cross-referencing sources

        Args:
            facts: List of factual claims to verify
            sources: List of source dicts (must have 'url' and 'content' or 'snippet')

        Returns:
            VerificationResult with verified facts and conflicts
        """
        verified_facts = []
        conflicting_claims = []

        # Extract claims from each source
        source_claims = self._extract_claims_from_sources(sources)

        # For each fact, check how many sources support it
        for fact in facts:
            supporting_sources = self._find_supporting_sources(fact, source_claims)
            conflicting = self._find_conflicting_info(fact, source_claims)

            confidence = self._calculate_confidence(supporting_sources, len(sources))

            verified_fact = Fact(
                claim=fact,
                sources=[s['url'] for s in supporting_sources],
                confidence=confidence,
                conflicting_info=conflicting if conflicting else None
            )

            verified_facts.append(verified_fact)

            if conflicting:
                conflicting_claims.append({
                    'claim': fact,
                    'conflict': conflicting,
                    'sources': [s['url'] for s in supporting_sources]
                })

        # Calculate overall source agreement
        agreement_score = self._calculate_agreement_score(verified_facts, len(sources))

        return VerificationResult(
            verified_facts=verified_facts,
            conflicting_claims=conflicting_claims,
            source_agreement_score=agreement_score,
            total_sources_checked=len(sources)
        )

    def _extract_claims_from_sources(self, sources: List[Dict]) -> List[Dict]:
        """
        Extract key claims from each source

        Args:
            sources: List of source dicts

        Returns:
            List of dicts with source info and extracted claims
        """
        source_claims = []

        for source in sources:
            content = source.get('content') or source.get('snippet', '')

            # Extract structured information
            claims = {
                'url': source.get('url', ''),
                'name': source.get('name', ''),
                'text': content,
                'numbers': self._extract_numbers(content),
                'dates': self._extract_dates(content),
                'names': self._extract_proper_nouns(content),
                'organizations': self._extract_organizations(content)
            }

            source_claims.append(claims)

        return source_claims

    def _find_supporting_sources(self, fact: str, source_claims: List[Dict]) -> List[Dict]:
        """
        Find sources that support a given fact

        Args:
            fact: Claim to verify
            source_claims: Extracted claims from sources

        Returns:
            List of sources that support the fact
        """
        supporting_sources = []

        # Extract key information from the fact
        fact_numbers = self._extract_numbers(fact)
        fact_dates = self._extract_dates(fact)
        fact_keywords = self._extract_keywords(fact)

        for source in source_claims:
            # Check if source text contains similar information
            text_similarity = self._calculate_text_similarity(fact, source['text'])

            # Check for matching numbers
            number_match = bool(fact_numbers and any(num in source['numbers'] for num in fact_numbers))

            # Check for matching dates
            date_match = bool(fact_dates and any(date in source['dates'] for date in fact_dates))

            # Check for keyword overlap
            keyword_match = len(fact_keywords & self._extract_keywords(source['text'])) >= 2

            # If source supports the fact (multiple signals)
            if (text_similarity > 0.5 or
                (number_match and keyword_match) or
                (date_match and keyword_match)):
                supporting_sources.append(source)

        return supporting_sources

    def _find_conflicting_info(self, fact: str, source_claims: List[Dict]) -> Optional[str]:
        """
        Find conflicting information about a fact

        Args:
            fact: Claim to check
            source_claims: Extracted claims from sources

        Returns:
            Description of conflict if found, None otherwise
        """
        # Extract numbers from fact
        fact_numbers = self._extract_numbers(fact)

        if not fact_numbers:
            return None

        # Look for different numbers in sources discussing same topic
        fact_keywords = self._extract_keywords(fact)

        for source in source_claims:
            source_keywords = self._extract_keywords(source['text'])

            # If source discusses same topic (keyword overlap)
            if len(fact_keywords & source_keywords) >= 2:
                # Check for different numbers
                conflicting_numbers = [num for num in source['numbers'] if num not in fact_numbers]

                if conflicting_numbers:
                    return f"Source {source['name']} reports different figures: {', '.join(conflicting_numbers)}"

        return None

    def _calculate_confidence(self, supporting_sources: List[Dict], total_sources: int) -> str:
        """
        Calculate confidence level based on source support

        Args:
            supporting_sources: Sources that support the claim
            total_sources: Total sources checked

        Returns:
            'high', 'medium', or 'low'
        """
        support_ratio = len(supporting_sources) / max(total_sources, 1)

        if support_ratio >= 0.6 and len(supporting_sources) >= 2:
            return 'high'
        elif support_ratio >= 0.4 or len(supporting_sources) >= 2:
            return 'medium'
        else:
            return 'low'

    def _calculate_agreement_score(self, verified_facts: List[Fact], total_sources: int) -> float:
        """
        Calculate overall agreement score across all facts

        Args:
            verified_facts: List of verified facts
            total_sources: Total sources checked

        Returns:
            Agreement score (0-1)
        """
        if not verified_facts:
            return 0.0

        # Calculate average confidence
        confidence_scores = {
            'high': 1.0,
            'medium': 0.6,
            'low': 0.3
        }

        total_score = sum(confidence_scores[fact.confidence] for fact in verified_facts)
        return total_score / len(verified_facts)

    def _extract_numbers(self, text: str) -> Set[str]:
        """Extract numbers from text"""
        # Match integers, decimals, percentages, currency
        patterns = [
            r'\$?\d+\.?\d*\s*(?:billion|million|thousand|%)?',
            r'\d+\.?\d*%',
            r'\d{1,3}(?:,\d{3})*(?:\.\d+)?'
        ]

        numbers = set()
        for pattern in patterns:
            numbers.update(re.findall(pattern, text.lower()))

        return numbers

    def _extract_dates(self, text: str) -> Set[str]:
        """Extract dates from text"""
        # Match various date formats
        patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # M/D/YY or M/D/YYYY
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}'
        ]

        dates = set()
        for pattern in patterns:
            dates.update(re.findall(pattern, text, re.IGNORECASE))

        return dates

    def _extract_proper_nouns(self, text: str) -> Set[str]:
        """Extract proper nouns (capitalized words)"""
        # Simple heuristic: words that are always capitalized
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return set(words)

    def _extract_organizations(self, text: str) -> Set[str]:
        """Extract organization names"""
        patterns = [
            r'\b([A-Z][A-Za-z]+ (?:Inc|Corp|LLC|Company|Corporation|Association|Union))\b',
            r'\b(Amazon|Google|Apple|Microsoft|Meta|Tesla|Walmart|Starbucks)\b',
            r'\b([A-Z]{2,})\b'  # Acronyms
        ]

        orgs = set()
        for pattern in patterns:
            orgs.update(re.findall(pattern, text))

        return orgs

    def _extract_keywords(self, text: str) -> Set[str]:
        """
        Extract significant keywords from text

        Args:
            text: Text to extract from

        Returns:
            Set of keywords
        """
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'this', 'that', 'these', 'those', 'their', 'them', 'they'
        }

        # Extract words (lowercase, alphanumeric)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())

        # Filter out stop words
        keywords = {word for word in words if word not in stop_words}

        return keywords

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using keyword overlap

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)

        if not keywords1 or not keywords2:
            return 0.0

        # Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)

        return intersection / union if union > 0 else 0.0
