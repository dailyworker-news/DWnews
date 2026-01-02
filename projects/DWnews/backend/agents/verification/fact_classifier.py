"""
Fact Classifier

Classifies facts into three categories:
- Observed: Firsthand documentation (court rulings, official counts, video evidence)
- Claimed: Secondhand reporting (news articles citing sources, official statements)
- Interpreted: Analysis or opinion (expert commentary, trend analysis, predictions)
"""

import re
from typing import Dict, List, Optional
from enum import Enum


class FactType(Enum):
    """Fact type enumeration"""
    OBSERVED = "observed"
    CLAIMED = "claimed"
    INTERPRETED = "interpreted"


class FactClassifier:
    """
    Classifies factual claims based on their nature and source type
    """

    # Indicators for each fact type
    OBSERVED_INDICATORS = [
        # Official documentation
        'official results', 'court ruled', 'ruling stated', 'official count',
        'government data', 'census shows', 'statistics show', 'data shows',
        'recorded', 'documented', 'filed', 'reported to',

        # Direct evidence
        'video shows', 'footage shows', 'audio recording', 'photograph shows',
        'document states', 'contract states', 'law states', 'regulation states',

        # Official processes
        'voted', 'ballot', 'election results', 'certified results',
        'official statement', 'press release', 'announcement',

        # Measurements and counts
        'measured', 'counted', 'calculated', 'tabulated'
    ]

    CLAIMED_INDICATORS = [
        # Attribution to sources
        'according to', 'reported by', 'said', 'stated', 'claimed',
        'spokesperson said', 'official said', 'sources say', 'sources told',
        'allegedly', 'reportedly', 'it is reported',

        # Indirect reporting
        'news reports', 'media reports', 'reports indicate', 'reports suggest',
        'witnesses said', 'employees said', 'workers said',

        # Quotations
        'quoted as saying', 'in a statement', 'in an interview',
        'testimony', 'told reporters'
    ]

    INTERPRETED_INDICATORS = [
        # Analysis and opinion
        'could', 'may', 'might', 'suggests', 'indicates', 'appears',
        'likely', 'unlikely', 'probably', 'possibly', 'potentially',

        # Predictions and forecasts
        'expected to', 'projected to', 'estimated to', 'forecast',
        'will likely', 'is expected', 'is projected',

        # Evaluations
        'significant', 'important', 'concerning', 'troubling', 'positive',
        'negative', 'beneficial', 'harmful', 'unprecedented',

        # Expert opinion
        'expert says', 'analyst says', 'economist says', 'researcher says',
        'believes', 'thinks', 'feels', 'opinion',

        # Trends and patterns
        'trend', 'pattern', 'tendency', 'increasing', 'decreasing',
        'growing', 'declining', 'rising', 'falling'
    ]

    def __init__(self):
        """Initialize the fact classifier"""
        pass

    def classify_fact(self, fact: str, source_type: str) -> str:
        """
        Classify a fact based on its content and source type

        Args:
            fact: The factual claim to classify
            source_type: Type of source (government_document, news_agency, academic, etc.)

        Returns:
            'observed', 'claimed', or 'interpreted'
        """
        # Source type influences classification
        if source_type in ['government_document', 'court_document', 'official_record']:
            # Government documents tend to report observed facts
            if self._has_indicators(fact, self.INTERPRETED_INDICATORS):
                return FactType.INTERPRETED.value
            elif self._has_indicators(fact, self.CLAIMED_INDICATORS):
                return FactType.CLAIMED.value
            else:
                return FactType.OBSERVED.value

        elif source_type == 'academic':
            # Academic sources: observed (data) or interpreted (analysis)
            if self._has_indicators(fact, self.OBSERVED_INDICATORS):
                return FactType.OBSERVED.value
            elif self._has_indicators(fact, self.INTERPRETED_INDICATORS):
                return FactType.INTERPRETED.value
            else:
                return FactType.CLAIMED.value

        elif source_type in ['news_agency', 'news_article']:
            # News articles: typically claimed or interpreted
            if self._has_indicators(fact, self.OBSERVED_INDICATORS) and \
               not self._has_indicators(fact, self.CLAIMED_INDICATORS):
                return FactType.OBSERVED.value
            elif self._has_indicators(fact, self.INTERPRETED_INDICATORS):
                return FactType.INTERPRETED.value
            else:
                return FactType.CLAIMED.value

        # Default classification based on content only
        return self._classify_by_content(fact)

    def _classify_by_content(self, fact: str) -> str:
        """
        Classify fact based on content alone

        Args:
            fact: The factual claim

        Returns:
            'observed', 'claimed', or 'interpreted'
        """
        fact_lower = fact.lower()

        # Count indicators for each type
        observed_score = sum(1 for indicator in self.OBSERVED_INDICATORS if indicator in fact_lower)
        claimed_score = sum(1 for indicator in self.CLAIMED_INDICATORS if indicator in fact_lower)
        interpreted_score = sum(1 for indicator in self.INTERPRETED_INDICATORS if indicator in fact_lower)

        # Check for specific patterns
        has_numbers = bool(re.search(r'\d+', fact))
        has_quotes = '"' in fact or "'" in fact
        has_modal_verbs = bool(re.search(r'\b(could|would|should|may|might|can)\b', fact_lower))
        has_attribution = bool(re.search(r'\b(according to|said|stated|claimed)\b', fact_lower))

        # Decision logic
        if interpreted_score > 0 or has_modal_verbs:
            return FactType.INTERPRETED.value

        if has_attribution or claimed_score > observed_score:
            return FactType.CLAIMED.value

        if observed_score > 0 or (has_numbers and not has_attribution):
            return FactType.OBSERVED.value

        # Default to claimed (safest assumption for unverified info)
        return FactType.CLAIMED.value

    def _has_indicators(self, text: str, indicators: List[str]) -> bool:
        """
        Check if text contains any of the given indicators

        Args:
            text: Text to check
            indicators: List of indicator phrases

        Returns:
            True if any indicator found
        """
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in indicators)

    def classify_multiple_facts(self, facts: List[Dict]) -> List[Dict]:
        """
        Classify multiple facts at once

        Args:
            facts: List of dicts with 'claim' and 'source_type' keys

        Returns:
            List of dicts with added 'fact_type' key
        """
        classified_facts = []

        for fact in facts:
            claim = fact.get('claim', '')
            source_type = fact.get('source_type', 'unknown')

            fact_type = self.classify_fact(claim, source_type)

            classified_fact = {
                **fact,
                'fact_type': fact_type
            }

            classified_facts.append(classified_fact)

        return classified_facts

    def get_classification_explanation(self, fact: str, source_type: str) -> Dict:
        """
        Get detailed explanation of how a fact was classified

        Args:
            fact: The factual claim
            source_type: Type of source

        Returns:
            Dict with classification and explanation
        """
        fact_type = self.classify_fact(fact, source_type)
        fact_lower = fact.lower()

        # Find matching indicators
        observed_matches = [ind for ind in self.OBSERVED_INDICATORS if ind in fact_lower]
        claimed_matches = [ind for ind in self.CLAIMED_INDICATORS if ind in fact_lower]
        interpreted_matches = [ind for ind in self.INTERPRETED_INDICATORS if ind in fact_lower]

        explanation = {
            'fact_type': fact_type,
            'source_type': source_type,
            'indicators_found': {
                'observed': observed_matches,
                'claimed': claimed_matches,
                'interpreted': interpreted_matches
            },
            'patterns': {
                'has_numbers': bool(re.search(r'\d+', fact)),
                'has_quotes': '"' in fact or "'" in fact,
                'has_modal_verbs': bool(re.search(r'\b(could|would|should|may|might|can)\b', fact_lower)),
                'has_attribution': bool(re.search(r'\b(according to|said|stated|claimed)\b', fact_lower))
            }
        }

        return explanation
