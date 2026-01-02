"""
Verifiability Scorer

Scores events based on how verifiable they are with credible sources.
More credible sources = higher score.

Scoring factors:
- Source credibility (Reuters, AP vs. social media)
- Specificity of facts (names, dates, numbers)
- Number of sources mentioned
- Type of evidence available
"""

import re
from typing import Dict, List


class VerifiabilityScorer:
    """Evaluates how verifiable an event is with credible sources"""

    # Tier 1: Highly credible sources (score: 3.0 each)
    TIER1_SOURCES = [
        'reuters', 'associated press', 'ap news', 'bloomberg',
        'propublica', 'the markup', 'the intercept',
        'new york times', 'washington post', 'wall street journal',
        'bbc', 'npr', 'pbs', 'cnn', 'abc news', 'cbs news',
        'labor department', 'nlrb', 'department of labor',
        'bureau of labor statistics', 'osha'
    ]

    # Tier 2: Credible regional/specialized sources (score: 2.0 each)
    TIER2_SOURCES = [
        'local news', 'city news', 'regional news',
        'guardian', 'politico', 'axios', 'the hill',
        'usa today', 'forbes', 'business insider',
        'labor notes', 'in these times', 'jacobin',
        'mother jones', 'the nation', 'slate'
    ]

    # Tier 3: Social/less formal sources (score: 1.0 each)
    TIER3_SOURCES = [
        'twitter', 'reddit', 'facebook', 'social media',
        'blog', 'newsletter', 'medium', 'substack'
    ]

    # Government/official sources (score: 2.5 each)
    OFFICIAL_SOURCES = [
        'government report', 'federal', 'state agency',
        'official statement', 'press release', 'court filing',
        'court documents', 'legal filing', 'lawsuit'
    ]

    # Academic/research sources (score: 2.5 each)
    ACADEMIC_SOURCES = [
        'study', 'research', 'academic', 'university',
        'peer-reviewed', 'journal', 'published in',
        'economist', 'researchers', 'professor', 'phd'
    ]

    # Specificity indicators (presence of specific facts)
    SPECIFIC_FACTS = {
        'names': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Person names
        'dates': r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?\b',
        'numbers': r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b',  # Numbers with formatting
        'locations': r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2})\b',  # City, State
        'quotes': r'"[^"]{10,}"',  # Direct quotes
    }

    # Vague/opinion indicators (reduce score)
    VAGUE_INDICATORS = [
        'allegedly', 'reportedly', 'claims', 'rumor', 'speculation',
        'anonymous', 'unnamed source', 'sources say', 'insider claims',
        'some say', 'many believe', 'it is believed'
    ]

    # Evidence type indicators
    EVIDENCE_KEYWORDS = [
        'document', 'documents', 'evidence', 'proof',
        'video', 'photo', 'photograph', 'recording',
        'transcript', 'email', 'letter', 'memo',
        'verified', 'confirmed', 'corroborated'
    ]

    def __init__(self):
        """Initialize the verifiability scorer"""
        pass

    def score(self, event: Dict) -> float:
        """
        Score an event's verifiability (0-10)

        Args:
            event: Dict with keys: title, description, source_url, discovered_from

        Returns:
            float: Score from 0-10, where 10 = highly verifiable
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        source_url = (event.get('source_url') or '').lower()
        discovered_from = (event.get('discovered_from') or '').lower()

        combined_text = f"{title} {description}"
        source_text = f"{source_url} {discovered_from}"

        score = 0.0

        # 1. Score based on source credibility (0-4 points)
        source_score = self._score_source_credibility(source_text, combined_text)
        score += min(4.0, source_score)

        # 2. Score based on fact specificity (0-3 points)
        specificity_score = self._score_specificity(combined_text)
        score += specificity_score

        # 3. Score based on evidence indicators (0-2 points)
        evidence_score = self._score_evidence(combined_text)
        score += evidence_score

        # 4. Check for multiple sources mentioned (0-2 points)
        multi_source_score = self._score_multiple_sources(combined_text)
        score += multi_source_score

        # 5. Penalize for vague/opinion indicators (-1 to -2 points)
        vague_count = sum(1 for indicator in self.VAGUE_INDICATORS if indicator in combined_text)
        if vague_count >= 3:
            score -= 2.0
        elif vague_count >= 1:
            score -= 1.0

        # 6. Bonus for official/academic sources (0-1 point)
        if any(src in combined_text for src in self.OFFICIAL_SOURCES):
            score += 0.5
        if any(src in combined_text for src in self.ACADEMIC_SOURCES):
            score += 0.5

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

    def _score_source_credibility(self, source_text: str, content_text: str) -> float:
        """Score based on source credibility tier"""
        score = 0.0

        # Check Tier 1 sources
        tier1_count = sum(1 for src in self.TIER1_SOURCES if src in source_text or src in content_text)
        score += min(4.0, tier1_count * 3.0)

        # If no Tier 1, check Tier 2
        if score == 0:
            tier2_count = sum(1 for src in self.TIER2_SOURCES if src in source_text or src in content_text)
            score += min(3.0, tier2_count * 2.0)

        # If no Tier 1 or 2, check Tier 3
        if score == 0:
            tier3_count = sum(1 for src in self.TIER3_SOURCES if src in source_text or src in content_text)
            score += min(1.5, tier3_count * 1.0)

        return score

    def _score_specificity(self, text: str) -> float:
        """Score based on presence of specific facts (names, dates, numbers)"""
        score = 0.0

        # Check for person names (proper nouns)
        names = re.findall(self.SPECIFIC_FACTS['names'], text)
        if len(names) >= 3:
            score += 1.0
        elif len(names) >= 1:
            score += 0.5

        # Check for dates
        dates = re.findall(self.SPECIFIC_FACTS['dates'], text, re.IGNORECASE)
        if dates:
            score += 0.5

        # Check for specific numbers
        numbers = re.findall(self.SPECIFIC_FACTS['numbers'], text)
        if len(numbers) >= 3:
            score += 1.0
        elif len(numbers) >= 1:
            score += 0.5

        # Check for direct quotes
        quotes = re.findall(self.SPECIFIC_FACTS['quotes'], text)
        if quotes:
            score += 0.5

        # Cap at 3.0
        return min(3.0, score)

    def _score_evidence(self, text: str) -> float:
        """Score based on evidence type mentions"""
        evidence_count = sum(1 for keyword in self.EVIDENCE_KEYWORDS if keyword in text)

        if evidence_count >= 3:
            return 2.0
        elif evidence_count >= 2:
            return 1.5
        elif evidence_count >= 1:
            return 1.0

        return 0.0

    def _score_multiple_sources(self, text: str) -> float:
        """Score based on mentions of multiple sources"""
        # Look for phrases indicating multiple sources
        multi_source_phrases = [
            'multiple sources', 'several sources', 'various sources',
            'according to', 'reports from', 'sources including',
            'confirmed by', 'corroborated by'
        ]

        count = sum(1 for phrase in multi_source_phrases if phrase in text)

        if count >= 2:
            return 2.0
        elif count >= 1:
            return 1.0

        return 0.0

    def explain_score(self, event: Dict) -> Dict:
        """
        Provide detailed explanation of how score was calculated

        Args:
            event: Event dictionary

        Returns:
            Dict with score breakdown
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        source_url = (event.get('source_url') or '').lower()
        discovered_from = (event.get('discovered_from') or '').lower()

        combined_text = f"{title} {description}"
        source_text = f"{source_url} {discovered_from}"

        explanation = {
            'final_score': self.score(event),
            'breakdown': {
                'source_credibility_score': self._score_source_credibility(source_text, combined_text),
                'specificity_score': self._score_specificity(combined_text),
                'evidence_score': self._score_evidence(combined_text),
                'multiple_sources_score': self._score_multiple_sources(combined_text),
                'vague_indicator_count': sum(1 for i in self.VAGUE_INDICATORS if i in combined_text),
                'has_official_source': any(src in combined_text for src in self.OFFICIAL_SOURCES),
                'has_academic_source': any(src in combined_text for src in self.ACADEMIC_SOURCES)
            },
            'source_url': event.get('source_url'),
            'discovered_from': event.get('discovered_from')
        }

        return explanation
