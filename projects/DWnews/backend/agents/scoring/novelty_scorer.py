"""
Novelty Scorer

Scores events based on how novel/unique they are.
First-of-its-kind = higher score, repetitive = lower score.

Scoring factors:
- Novel/first-time indicators
- Similarity to recent events
- Routine/predictable events
- Unique developments
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class NoveltyScorer:
    """Evaluates how novel/unique an event is"""

    # First-time/novel indicators (score boost: +3-4)
    NOVEL_KEYWORDS = [
        'first time', 'first ever', 'unprecedented', 'historic',
        'landmark', 'groundbreaking', 'breakthrough', 'milestone',
        'never before', 'first in', 'pioneering', 'revolutionary',
        'new development', 'major development', 'significant development'
    ]

    # Unique/rare indicators (score boost: +2-3)
    UNIQUE_KEYWORDS = [
        'unique', 'rare', 'unusual', 'extraordinary',
        'remarkable', 'notable', 'significant', 'major',
        'unprecedented scale', 'largest ever', 'biggest'
    ]

    # Routine/predictable indicators (score reduction: -2 to -3)
    ROUTINE_KEYWORDS = [
        'annual', 'quarterly', 'monthly', 'regular',
        'routine', 'scheduled', 'expected', 'typical',
        'usual', 'normal', 'standard', 'traditional',
        'as expected', 'predictable', 'recurring'
    ]

    # Repetitive event indicators
    REPETITIVE_KEYWORDS = [
        'another', 'yet another', 'once again', 'again',
        'continues', 'ongoing', 'still', 'same',
        'similar to', 'like previous', 'as before'
    ]

    # Escalation/change indicators (score boost: +1-2)
    ESCALATION_KEYWORDS = [
        'escalate', 'escalating', 'intensify', 'intensifying',
        'growing', 'spreading', 'expanding', 'increase',
        'surge', 'spike', 'rise', 'uptick', 'trend'
    ]

    def __init__(self, db_session=None):
        """
        Initialize the novelty scorer

        Args:
            db_session: Optional SQLAlchemy session for checking recent events
        """
        self.db_session = db_session

    def score(self, event: Dict, recent_events: Optional[List[Dict]] = None) -> float:
        """
        Score an event's novelty (0-10)

        Args:
            event: Dict with keys: title, description
            recent_events: Optional list of recent approved events for similarity check

        Returns:
            float: Score from 0-10, where 10 = completely novel/unique
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        score = 5.0  # Start at middle

        # 1. Check for novel/first-time indicators (0-4 points)
        novel_count = sum(1 for keyword in self.NOVEL_KEYWORDS if keyword in combined_text)
        if novel_count >= 2:
            score += 4.0
        elif novel_count >= 1:
            score += 3.0

        # 2. Check for unique/rare indicators (0-3 points)
        unique_count = sum(1 for keyword in self.UNIQUE_KEYWORDS if keyword in combined_text)
        score += min(3.0, unique_count * 1.0)

        # 3. Check for escalation/change (0-2 points)
        escalation_count = sum(1 for keyword in self.ESCALATION_KEYWORDS if keyword in combined_text)
        score += min(2.0, escalation_count * 0.7)

        # 4. Penalize for routine/predictable (-2 to -3 points)
        routine_count = sum(1 for keyword in self.ROUTINE_KEYWORDS if keyword in combined_text)
        if routine_count >= 2:
            score -= 3.0
        elif routine_count >= 1:
            score -= 2.0

        # 5. Penalize for repetitive indicators (-1 to -2 points)
        repetitive_count = sum(1 for keyword in self.REPETITIVE_KEYWORDS if keyword in combined_text)
        if repetitive_count >= 2:
            score -= 2.0
        elif repetitive_count >= 1:
            score -= 1.0

        # 6. Check similarity to recent events (if provided)
        if recent_events:
            similarity_penalty = self._calculate_similarity_penalty(event, recent_events)
            score -= similarity_penalty

        # Cap at 10 and ensure minimum of 0
        final_score = max(0.0, min(10.0, score))

        return round(final_score, 2)

    def _calculate_similarity_penalty(self, event: Dict, recent_events: List[Dict]) -> float:
        """
        Calculate penalty based on similarity to recent events

        Args:
            event: Current event to score
            recent_events: List of recent approved events (last 7 days)

        Returns:
            float: Penalty amount (0-3 points)
        """
        if not recent_events:
            return 0.0

        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()

        max_similarity = 0.0

        for recent_event in recent_events:
            recent_title = (recent_event.get('title') or '').lower()
            recent_desc = (recent_event.get('description') or '').lower()

            # Simple keyword overlap similarity
            similarity = self._keyword_similarity(
                f"{title} {description}",
                f"{recent_title} {recent_desc}"
            )

            max_similarity = max(max_similarity, similarity)

        # Convert similarity to penalty
        if max_similarity >= 0.7:
            return 3.0  # Very similar to recent event
        elif max_similarity >= 0.5:
            return 2.0  # Moderately similar
        elif max_similarity >= 0.3:
            return 1.0  # Somewhat similar
        else:
            return 0.0  # Not similar

    def _keyword_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple keyword similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Similarity score (0-1)
        """
        # Extract keywords (words 4+ characters, excluding common words)
        common_words = {
            'that', 'this', 'with', 'from', 'have', 'they', 'were',
            'been', 'their', 'about', 'will', 'would', 'could', 'said',
            'what', 'which', 'when', 'where', 'there', 'these', 'those'
        }

        words1 = set([
            word for word in re.findall(r'\b\w{4,}\b', text1)
            if word not in common_words
        ])

        words2 = set([
            word for word in re.findall(r'\b\w{4,}\b', text2)
            if word not in common_words
        ])

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def fetch_recent_approved_events(self, days: int = 7) -> List[Dict]:
        """
        Fetch recent approved events from database for similarity check

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of event dictionaries
        """
        if not self.db_session:
            return []

        try:
            from database.models import EventCandidate
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            recent_events = self.db_session.query(EventCandidate).filter(
                EventCandidate.status == 'approved',
                EventCandidate.evaluated_at >= cutoff_date
            ).all()

            return [
                {
                    'title': event.title,
                    'description': event.description,
                    'evaluated_at': event.evaluated_at
                }
                for event in recent_events
            ]
        except Exception as e:
            # If database query fails, return empty list
            print(f"Error fetching recent events: {e}")
            return []

    def explain_score(self, event: Dict, recent_events: Optional[List[Dict]] = None) -> Dict:
        """
        Provide detailed explanation of how score was calculated

        Args:
            event: Event dictionary
            recent_events: Optional list of recent events

        Returns:
            Dict with score breakdown
        """
        title = (event.get('title') or '').lower()
        description = (event.get('description') or '').lower()
        combined_text = f"{title} {description}"

        explanation = {
            'final_score': self.score(event, recent_events),
            'breakdown': {
                'novel_keyword_count': sum(1 for k in self.NOVEL_KEYWORDS if k in combined_text),
                'unique_keyword_count': sum(1 for k in self.UNIQUE_KEYWORDS if k in combined_text),
                'escalation_keyword_count': sum(1 for k in self.ESCALATION_KEYWORDS if k in combined_text),
                'routine_keyword_count': sum(1 for k in self.ROUTINE_KEYWORDS if k in combined_text),
                'repetitive_keyword_count': sum(1 for k in self.REPETITIVE_KEYWORDS if k in combined_text),
                'similarity_penalty': self._calculate_similarity_penalty(event, recent_events) if recent_events else 0.0,
                'recent_events_checked': len(recent_events) if recent_events else 0
            }
        }

        return explanation
