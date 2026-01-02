"""
Timeliness Scorer

Scores events based on how timely/urgent they are.
Breaking news = higher score, old news = lower score.

Scoring factors:
- How recent is the event (days since event)
- Breaking news indicators
- Upcoming events (future votes, deadlines)
- Temporal urgency keywords
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional
from dateutil import parser as dateparser


class TimelinessScorer:
    """Evaluates how timely/urgent an event is"""

    # Breaking news indicators (score boost)
    BREAKING_KEYWORDS = [
        'breaking', 'just announced', 'just now', 'happening now',
        'live', 'ongoing', 'currently', 'today', 'this morning',
        'this afternoon', 'tonight', 'just in', 'developing'
    ]

    # Urgent/immediate keywords
    URGENT_KEYWORDS = [
        'emergency', 'urgent', 'immediate', 'crisis',
        'breaking news', 'alert', 'critical'
    ]

    # Future event indicators
    FUTURE_KEYWORDS = [
        'upcoming', 'scheduled', 'will be', 'next week',
        'next month', 'planned', 'vote on', 'deadline',
        'anticipated', 'expected to'
    ]

    # Past event indicators (negative for score)
    PAST_KEYWORDS = [
        'last year', 'years ago', 'months ago',
        'historical', 'anniversary', 'commemorat'
    ]

    # Time indicators for parsing
    TIME_PATTERNS = [
        r'(\d{1,2})\s*(?:days?|hrs?|hours?|minutes?)\s*ago',
        r'yesterday',
        r'last\s+(?:week|month|monday|tuesday|wednesday|thursday|friday)',
        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?'
    ]

    def __init__(self):
        """Initialize the timeliness scorer"""
        pass

    def score(self, event: Dict) -> float:
        """
        Score an event's timeliness (0-10)

        Args:
            event: Dict with keys: title, description, event_date, discovery_date

        Returns:
            float: Score from 0-10, where 10 = maximum timeliness (breaking news)
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        score = 5.0  # Start at middle

        # 1. Check for breaking news indicators (0-3 points)
        if any(keyword in combined_text for keyword in self.BREAKING_KEYWORDS):
            score += 3.0

        # 2. Check for urgent keywords (0-2 points)
        if any(keyword in combined_text for keyword in self.URGENT_KEYWORDS):
            score += 2.0

        # 3. Calculate recency score based on event date (0-4 points)
        recency_score = self._score_recency(event)
        score += recency_score

        # 4. Check for future events (upcoming votes, etc.) (0-2 points)
        future_score = self._score_future_events(combined_text)
        score += future_score

        # 5. Penalize for historical/old content (-1 to -3 points)
        if any(keyword in combined_text for keyword in self.PAST_KEYWORDS):
            score -= 2.0

        # 6. Try to extract and score specific time references
        time_ref_score = self._score_time_references(combined_text)
        score += time_ref_score

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

    def _score_recency(self, event: Dict) -> float:
        """
        Score based on how recent the event is

        Scoring:
        - 0-1 days ago: +4 points
        - 1-3 days ago: +3 points
        - 3-7 days ago: +2 points
        - 7-14 days ago: +1 point
        - 14-30 days ago: 0 points
        - >30 days ago: -1 to -3 points
        """
        event_date = event.get('event_date')
        discovery_date = event.get('discovery_date')

        # Try to determine event date
        reference_date = None
        if event_date:
            if isinstance(event_date, datetime):
                reference_date = event_date
            elif isinstance(event_date, str):
                try:
                    reference_date = dateparser.parse(event_date)
                except:
                    pass

        # Fallback to discovery date if event date not available
        if not reference_date and discovery_date:
            if isinstance(discovery_date, datetime):
                reference_date = discovery_date
            elif isinstance(discovery_date, str):
                try:
                    reference_date = dateparser.parse(discovery_date)
                except:
                    pass

        # If we still don't have a date, assume recent (neutral score)
        if not reference_date:
            return 0.0

        # Calculate days since event
        now = datetime.utcnow()
        if reference_date.tzinfo:
            # Make now timezone-aware if reference_date is
            from datetime import timezone
            now = datetime.now(timezone.utc)

        days_ago = (now - reference_date).days

        # Score based on recency
        if days_ago < 0:
            # Future event
            return 0.0  # Will be scored separately in future events
        elif days_ago <= 1:
            return 4.0
        elif days_ago <= 3:
            return 3.0
        elif days_ago <= 7:
            return 2.0
        elif days_ago <= 14:
            return 1.0
        elif days_ago <= 30:
            return 0.0
        elif days_ago <= 90:
            return -1.0
        elif days_ago <= 180:
            return -2.0
        else:
            return -3.0

    def _score_future_events(self, text: str) -> float:
        """Score for upcoming events (votes, deadlines, etc.)"""
        # Check for future event indicators
        has_future = any(keyword in text for keyword in self.FUTURE_KEYWORDS)

        if not has_future:
            return 0.0

        # Try to extract when the future event is
        # "next week", "in 2 days", etc.
        near_future_pattern = r'(?:next|in)\s+(?:few|couple|1|2|3|one|two|three)\s+(?:days?|weeks?)'
        if re.search(near_future_pattern, text):
            return 2.0  # Soon = more timely

        # Generic future event
        return 1.0

    def _score_time_references(self, text: str) -> float:
        """Extract and score specific time references in text"""
        # Look for "X days ago" patterns
        days_ago_pattern = r'(\d{1,2})\s*days?\s*ago'
        match = re.search(days_ago_pattern, text)

        if match:
            try:
                days = int(match.group(1))
                if days <= 1:
                    return 1.0
                elif days <= 3:
                    return 0.5
                elif days <= 7:
                    return 0.0
                else:
                    return -0.5
            except (ValueError, IndexError):
                pass

        # Look for "yesterday"
        if 'yesterday' in text:
            return 1.0

        # Look for "today"
        if 'today' in text or 'this morning' in text or 'this afternoon' in text:
            return 1.5

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
        combined_text = f"{title} {description}"

        explanation = {
            'final_score': self.score(event),
            'breakdown': {
                'has_breaking_keywords': any(k in combined_text for k in self.BREAKING_KEYWORDS),
                'has_urgent_keywords': any(k in combined_text for k in self.URGENT_KEYWORDS),
                'has_future_keywords': any(k in combined_text for k in self.FUTURE_KEYWORDS),
                'has_past_keywords': any(k in combined_text for k in self.PAST_KEYWORDS),
                'recency_score': self._score_recency(event),
                'future_events_score': self._score_future_events(combined_text),
                'time_ref_score': self._score_time_references(combined_text)
            },
            'event_date': str(event.get('event_date')) if event.get('event_date') else None
        }

        return explanation
