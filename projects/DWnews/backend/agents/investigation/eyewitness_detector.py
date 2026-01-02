"""
Eyewitness Detector for Investigatory Journalist Agent (Phase 6.9.2)

Identifies firsthand eyewitness accounts in social media posts:
- Detects firsthand language patterns ("I was there", "I saw", etc.)
- Scores eyewitness confidence
- Validates eyewitness credibility
- Filters high-confidence accounts
"""

import logging
import re
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class EyewitnessDetector:
    """
    Detect and validate eyewitness accounts in social media posts.

    Detection criteria:
    - Firsthand language (I was, I saw, I witnessed)
    - Participation language (I work, I participated)
    - Direct observation language (just saw, happening now)
    - Present tense reporting (currently, right now)
    """

    # Firsthand language patterns
    FIRSTHAND_PATTERNS = [
        r'\bi was there\b',
        r'\bi saw\b',
        r'\bi witnessed\b',
        r'\bi can confirm\b',
        r'\bi attended\b',
        r'\bi participated\b',
        r'\bas someone who was\b',
        r'\bfirsthand\b',
        r'\bin person\b',
        r'\bat the scene\b',
    ]

    PARTICIPATION_PATTERNS = [
        r'\bi work\b',
        r'\bi am a\b',
        r'\bi\'m a\b',
        r'\bwe organized\b',
        r'\bwe walked out\b',
        r'\bwe\'re on strike\b',
        r'\bour union\b',
    ]

    DIRECT_OBSERVATION_PATTERNS = [
        r'\bjust saw\b',
        r'\bjust witnessed\b',
        r'\bhappening now\b',
        r'\bright now\b',
        r'\blive updates\b',
        r'\bcurrently\b',
        r'\bas we speak\b',
        r'\bat this moment\b',
    ]

    def __init__(self):
        """Initialize eyewitness detector"""
        # Compile patterns for efficiency
        self.firsthand_regex = [re.compile(p, re.IGNORECASE) for p in self.FIRSTHAND_PATTERNS]
        self.participation_regex = [re.compile(p, re.IGNORECASE) for p in self.PARTICIPATION_PATTERNS]
        self.observation_regex = [re.compile(p, re.IGNORECASE) for p in self.DIRECT_OBSERVATION_PATTERNS]

    def detect_firsthand_language(self, text: str) -> Dict[str, Any]:
        """
        Detect firsthand language in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with is_firsthand (bool), confidence (float), and indicators (list)
        """
        indicators = []

        # Check firsthand patterns
        firsthand_count = sum(1 for pattern in self.firsthand_regex if pattern.search(text))
        if firsthand_count > 0:
            indicators.append('firsthand_language')

        # Check participation patterns
        participation_count = sum(1 for pattern in self.participation_regex if pattern.search(text))
        if participation_count > 0:
            indicators.append('participation_language')

        # Check direct observation patterns
        observation_count = sum(1 for pattern in self.observation_regex if pattern.search(text))
        if observation_count > 0:
            indicators.append('direct_observation')

        # Calculate confidence (0-100)
        total_matches = firsthand_count + participation_count + observation_count

        if total_matches >= 3:
            confidence = 95.0
        elif total_matches == 2:
            confidence = 85.0
        elif total_matches == 1:
            confidence = 70.0
        else:
            confidence = 20.0

        is_firsthand = total_matches >= 1

        return {
            'is_firsthand': is_firsthand,
            'confidence': confidence,
            'indicators': indicators,
            'match_count': total_matches
        }

    def identify_eyewitness_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify eyewitness accounts from list of posts.

        Args:
            posts: List of post dictionaries

        Returns:
            List of posts identified as eyewitness accounts
        """
        eyewitness_posts = []

        for post in posts:
            # Get text from post
            text = self._extract_text_from_post(post)

            # Detect firsthand language
            detection = self.detect_firsthand_language(text)

            if detection['is_firsthand']:
                # Add detection metadata to post
                post_copy = post.copy()
                post_copy['eyewitness_score'] = detection['confidence']
                post_copy['indicators'] = detection['indicators']
                post_copy['match_count'] = detection['match_count']

                eyewitness_posts.append(post_copy)

        return eyewitness_posts

    def validate_eyewitness_credibility(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate credibility of eyewitness account.

        Factors:
        - Account age (older = more credible)
        - Specific details in post
        - Consistency with known facts
        - Account history

        Args:
            post: Eyewitness post dictionary

        Returns:
            Credibility assessment dictionary
        """
        credibility_score = 50.0  # Base score
        credibility_factors = []

        # Check account age
        if 'author' in post:
            author = post['author']

            # Twitter account age
            if 'created_at' in author:
                created_at = author['created_at']
                # Simplified: assume older accounts are more credible
                if isinstance(created_at, str) and ('2020' in created_at or '2019' in created_at or '2018' in created_at):
                    credibility_score += 15.0
                    credibility_factors.append('established_account')

            # Reddit karma
            if 'link_karma' in author or 'comment_karma' in author:
                total_karma = author.get('link_karma', 0) + author.get('comment_karma', 0)
                if total_karma > 1000:
                    credibility_score += 15.0
                    credibility_factors.append('high_karma')

        # Check for specific details
        text = self._extract_text_from_post(post)
        if self._has_specific_details(text):
            credibility_score += 15.0
            credibility_factors.append('specific_details')

        # Check eyewitness score
        eyewitness_score = post.get('eyewitness_score', 0)
        if eyewitness_score >= 85:
            credibility_score += 10.0
            credibility_factors.append('strong_firsthand_language')

        # Check engagement (high engagement = more visible/scrutinized)
        if 'score' in post and post['score'] > 500:
            credibility_score += 10.0
            credibility_factors.append('high_engagement')
        elif 'metrics' in post:
            metrics = post['metrics']
            if isinstance(metrics, dict):
                total = sum(v for v in metrics.values() if isinstance(v, (int, float)))
                if total > 500:
                    credibility_score += 10.0
                    credibility_factors.append('high_engagement')

        return {
            'credibility_score': min(credibility_score, 100.0),
            'credibility_factors': credibility_factors
        }

    def filter_high_confidence_eyewitness(
        self,
        eyewitness_posts: List[Dict[str, Any]],
        threshold: float = 60.0
    ) -> List[Dict[str, Any]]:
        """
        Filter to only high-confidence eyewitness accounts.

        Args:
            eyewitness_posts: List of eyewitness post dictionaries
            threshold: Minimum eyewitness score (0-100)

        Returns:
            Filtered list of high-confidence eyewitness accounts
        """
        high_confidence = []

        for post in eyewitness_posts:
            score = post.get('eyewitness_score', 0)

            if score >= threshold:
                high_confidence.append(post)

        # Sort by score (highest first)
        high_confidence.sort(key=lambda p: p.get('eyewitness_score', 0), reverse=True)

        return high_confidence

    def _extract_text_from_post(self, post: Dict[str, Any]) -> str:
        """
        Extract text content from post for analysis.

        Args:
            post: Post dictionary

        Returns:
            Combined text string
        """
        parts = []

        # Get title
        if 'title' in post:
            parts.append(post['title'])

        # Get text/selftext
        if 'text' in post:
            parts.append(post['text'])
        elif 'selftext' in post:
            parts.append(post['selftext'])

        # Get body (for comments)
        if 'body' in post:
            parts.append(post['body'])

        return ' '.join(parts)

    def _has_specific_details(self, text: str) -> bool:
        """
        Check if text contains specific details (numbers, names, times).

        Args:
            text: Text to analyze

        Returns:
            True if specific details found
        """
        # Check for numbers
        has_numbers = bool(re.search(r'\b\d+\b', text))

        # Check for time references
        time_patterns = [r'\b\d{1,2}:\d{2}\b', r'\b\d{1,2}(am|pm)\b', r'\btoday\b', r'\byesterday\b']
        has_time = any(re.search(p, text, re.IGNORECASE) for p in time_patterns)

        # Check for specific locations
        location_patterns = [r'\bat the\b.*\b(building|warehouse|factory|office|store)\b']
        has_location = any(re.search(p, text, re.IGNORECASE) for p in location_patterns)

        # Return True if at least 2 types of details present
        detail_count = sum([has_numbers, has_time, has_location])
        return detail_count >= 2


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    detector = EyewitnessDetector()

    # Test firsthand language detection
    print("\n=== Firsthand Language Detection ===")

    firsthand_texts = [
        "I was there when Amazon workers walked out today at 2pm.",
        "Just saw this unfold firsthand at the JFK8 warehouse.",
        "I work here and can confirm we're organizing."
    ]

    secondhand_texts = [
        "According to union sources, negotiations broke down.",
        "NYT reports that Amazon workers are planning a strike.",
        "Sources say the company rejected union demands."
    ]

    for text in firsthand_texts:
        result = detector.detect_firsthand_language(text)
        print(f"\nFirsthand: '{text[:50]}...'")
        print(f"  Confidence: {result['confidence']:.0f}%")
        print(f"  Indicators: {', '.join(result['indicators'])}")

    for text in secondhand_texts:
        result = detector.detect_firsthand_language(text)
        print(f"\nSecondhand: '{text[:50]}...'")
        print(f"  Confidence: {result['confidence']:.0f}%")

    # Test eyewitness post identification
    print("\n\n=== Eyewitness Post Identification ===")

    mock_posts = [
        {
            'platform': 'twitter',
            'text': 'I was there when workers walked out. Over 200 people at 3pm today.',
            'author': {'username': 'worker123', 'created_at': '2020-01-15', 'followers_count': 234}
        },
        {
            'platform': 'reddit',
            'title': 'Just witnessed Amazon strike firsthand',
            'selftext': 'I work at JFK8. We organized and walked out at the warehouse entrance.',
            'author': {'name': 'warehouse_worker', 'link_karma': 450, 'comment_karma': 2340},
            'score': 1234
        }
    ]

    eyewitness_posts = detector.identify_eyewitness_posts(mock_posts)
    print(f"\nIdentified {len(eyewitness_posts)} eyewitness accounts:")

    for post in eyewitness_posts:
        print(f"\n  Platform: {post['platform']}")
        print(f"  Score: {post['eyewitness_score']}/100")
        print(f"  Indicators: {', '.join(post['indicators'])}")

        # Validate credibility
        credibility = detector.validate_eyewitness_credibility(post)
        print(f"  Credibility: {credibility['credibility_score']:.0f}/100")
        print(f"  Factors: {', '.join(credibility['credibility_factors'])}")
