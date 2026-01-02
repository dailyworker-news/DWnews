"""
Regional Relevance Scorer

Scores events based on their regional relevance to target audience.
National events = higher score, local events scored based on city importance.

Scoring factors:
- National vs. local scope
- Major city mentions (NYC, LA, Chicago, etc.)
- State-level impact
- Regional keywords
"""

import re
from typing import Dict, List, Optional


class RegionalScorer:
    """Evaluates regional relevance of events"""

    # National scope indicators (score: high)
    NATIONAL_KEYWORDS = [
        'federal', 'nationwide', 'national', 'us ', 'u.s.', 'united states',
        'america', 'american', 'congress', 'senate', 'house of representatives',
        'president', 'white house', 'department of labor', 'nlrb',
        'supreme court', 'federal court', 'federal law'
    ]

    # Major metropolitan areas (high relevance)
    MAJOR_METROS = {
        # Format: city name -> (state code, population score)
        'new york': ('NY', 10),
        'nyc': ('NY', 10),
        'los angeles': ('CA', 9),
        'chicago': ('IL', 9),
        'houston': ('TX', 8),
        'phoenix': ('AZ', 7),
        'philadelphia': ('PA', 8),
        'san antonio': ('TX', 7),
        'san diego': ('CA', 7),
        'dallas': ('TX', 7),
        'san jose': ('CA', 7),
        'austin': ('TX', 7),
        'seattle': ('WA', 8),
        'san francisco': ('CA', 8),
        'boston': ('MA', 8),
        'washington dc': ('DC', 9),
        'washington d.c.': ('DC', 9),
        'detroit': ('MI', 7),
        'minneapolis': ('MN', 7),
        'atlanta': ('GA', 7),
        'miami': ('FL', 7),
        'denver': ('CO', 7),
        'portland': ('OR', 6),
        'las vegas': ('NV', 6),
        'baltimore': ('MD', 6),
        'milwaukee': ('WI', 6),
        'pittsburgh': ('PA', 6)
    }

    # Large states (state-level impact)
    LARGE_STATES = {
        'california': 10,
        'texas': 9,
        'florida': 8,
        'new york': 8,  # Note: also a city
        'pennsylvania': 7,
        'illinois': 7,
        'ohio': 7,
        'georgia': 6,
        'michigan': 6,
        'north carolina': 6
    }

    # Regional descriptors
    REGIONAL_TERMS = [
        'midwest', 'northeast', 'southeast', 'southwest',
        'west coast', 'east coast', 'south', 'north',
        'rust belt', 'bible belt', 'sun belt'
    ]

    # Multi-state/regional indicators
    MULTI_STATE_KEYWORDS = [
        'multiple states', 'several states', 'across states',
        'regional', 'multi-state', 'interstate'
    ]

    def __init__(self, db_session=None):
        """
        Initialize the regional scorer

        Args:
            db_session: Optional SQLAlchemy session for database lookups
        """
        self.db_session = db_session

    def score(self, event: Dict) -> float:
        """
        Score an event's regional relevance (0-10)

        Args:
            event: Dict with keys: title, description, is_national, is_local, region_id

        Returns:
            float: Score from 0-10, where 10 = maximum regional relevance
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        score = 0.0

        # 1. Check if explicitly marked as national (0-10 points)
        if event.get('is_national'):
            return 10.0

        # 2. Check for national keywords (0-10 points)
        if any(keyword in combined_text for keyword in self.NATIONAL_KEYWORDS):
            score += 10.0
            return min(10.0, score)  # National events max out immediately

        # 3. Check for multi-state/regional scope (0-8 points)
        if any(keyword in combined_text for keyword in self.MULTI_STATE_KEYWORDS):
            score += 8.0
            return min(10.0, score)

        # 4. Check for large states (0-7 points)
        state_score = self._score_state_mentions(combined_text)
        score += state_score

        # 5. Check for major metropolitan areas (0-6 points)
        metro_score = self._score_metro_mentions(combined_text)
        score += metro_score

        # 6. Check for regional terms (0-5 points)
        if any(term in combined_text for term in self.REGIONAL_TERMS):
            score += 5.0

        # 7. If marked as local, apply scoring based on city importance
        if event.get('is_local'):
            # Local events get moderate score unless in major metro
            if metro_score == 0:
                score = max(score, 4.0)  # Baseline for local events

        # 8. If no regional indicators found, default to low score
        if score == 0:
            score = 2.0  # Unknown region gets minimal score

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

    def _score_state_mentions(self, text: str) -> float:
        """Score based on state mentions"""
        max_score = 0.0

        for state, score in self.LARGE_STATES.items():
            if state in text:
                # Normalize score (10 -> 7 points max for state)
                normalized = (score / 10.0) * 7.0
                max_score = max(max_score, normalized)

        return max_score

    def _score_metro_mentions(self, text: str) -> float:
        """Score based on major metro area mentions"""
        max_score = 0.0

        for city, (state, pop_score) in self.MAJOR_METROS.items():
            if city in text:
                # Normalize score (10 -> 6 points max for metro)
                normalized = (pop_score / 10.0) * 6.0
                max_score = max(max_score, normalized)

        return max_score

    def infer_region_info(self, event: Dict) -> Dict:
        """
        Infer regional information from event text

        Args:
            event: Event dictionary

        Returns:
            Dict with: is_national, is_local, region_name, state_code
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        result = {
            'is_national': False,
            'is_local': False,
            'region_name': None,
            'state_code': None
        }

        # Check for national scope
        if any(keyword in combined_text for keyword in self.NATIONAL_KEYWORDS):
            result['is_national'] = True
            result['region_name'] = 'National'
            return result

        # Check for metro areas
        for city, (state, _) in self.MAJOR_METROS.items():
            if city in combined_text:
                result['is_local'] = True
                result['region_name'] = city.title()
                result['state_code'] = state
                return result

        # Check for states
        for state in self.LARGE_STATES.keys():
            if state in combined_text:
                result['is_local'] = True
                result['region_name'] = state.title()
                return result

        # Default to unknown local
        result['is_local'] = True
        result['region_name'] = 'Unknown'

        return result

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
        combined_text = f"{title} {description}"

        explanation = {
            'final_score': self.score(event),
            'breakdown': {
                'is_national_flag': event.get('is_national', False),
                'has_national_keywords': any(k in combined_text for k in self.NATIONAL_KEYWORDS),
                'has_multi_state_keywords': any(k in combined_text for k in self.MULTI_STATE_KEYWORDS),
                'state_score': self._score_state_mentions(combined_text),
                'metro_score': self._score_metro_mentions(combined_text),
                'has_regional_terms': any(t in combined_text for t in self.REGIONAL_TERMS),
                'is_local_flag': event.get('is_local', False)
            },
            'inferred_region': self.infer_region_info(event)
        }

        return explanation
