"""
Social Source Credibility Scoring for Investigatory Journalist Agent (Phase 6.9.2)

Scores social media sources based on:
- Account age (older = more credible)
- Karma/followers (higher = more credible)
- Verification status (verified = highly credible)
- Engagement metrics (higher engagement = more visibility/credibility)
- Content indicators (firsthand language, specific details)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SocialSourceCredibility:
    """
    Score social media sources for credibility.

    Scoring factors:
    - Account age (0-30 points)
    - Karma/followers (0-30 points)
    - Verification status (0-20 points)
    - Engagement metrics (0-10 points)
    - Content quality (0-10 points)

    Total: 0-100 points
    """

    # Credibility thresholds
    TIER_1_THRESHOLD = 80  # Highly credible
    TIER_2_THRESHOLD = 60  # Credible
    TIER_3_THRESHOLD = 40  # Moderate credibility
    # Below 40 = Low credibility

    def __init__(self):
        """Initialize credibility scorer"""
        pass

    def score_source(self, source: Dict[str, Any]) -> float:
        """
        Score a social media source for credibility.

        Args:
            source: Source dictionary with platform, username, metadata

        Returns:
            Credibility score 0-100
        """
        platform = source.get('platform', 'unknown')

        if platform == 'twitter':
            return self._score_twitter_account(source)
        elif platform == 'reddit':
            return self._score_reddit_account(source)
        else:
            return 50.0  # Default neutral score

    def score_engagement(self, source: Dict[str, Any]) -> float:
        """
        Score engagement metrics.

        Args:
            source: Source with engagement_metrics

        Returns:
            Engagement score 0-100
        """
        metrics = source.get('engagement_metrics', {})

        if not metrics:
            return 0.0

        # Twitter engagement
        if 'retweet_count' in metrics:
            retweets = metrics.get('retweet_count', 0)
            likes = metrics.get('like_count', 0)
            replies = metrics.get('reply_count', 0)

            # Calculate total engagement
            total = retweets + likes + replies

            if total >= 1000:
                return 100.0
            elif total >= 500:
                return 80.0
            elif total >= 100:
                return 60.0
            elif total >= 50:
                return 40.0
            elif total >= 10:
                return 20.0
            else:
                return 10.0

        # Reddit engagement (score)
        if 'score' in source:
            score = source.get('score', 0)

            if score >= 5000:
                return 100.0
            elif score >= 1000:
                return 80.0
            elif score >= 500:
                return 60.0
            elif score >= 100:
                return 40.0
            elif score >= 50:
                return 20.0
            else:
                return 10.0

        return 0.0

    def score_combined(self, source: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate combined credibility score with breakdown.

        Args:
            source: Source dictionary

        Returns:
            Dictionary with total_score and component scores
        """
        account_score = self.score_source(source)
        engagement_score = self.score_engagement(source)
        content_score = self._score_content_quality(source)

        # Weighted average
        # Account: 50%, Engagement: 30%, Content: 20%
        total_score = (
            account_score * 0.5 +
            engagement_score * 0.3 +
            content_score * 0.2
        )

        return {
            'total_score': round(total_score, 1),
            'account_score': round(account_score, 1),
            'engagement_score': round(engagement_score, 1),
            'content_score': round(content_score, 1)
        }

    def _score_twitter_account(self, source: Dict[str, Any]) -> float:
        """
        Score Twitter account credibility.

        Factors:
        - Verified status (20 points if True)
        - Account age (0-30 points)
        - Follower count (0-30 points)
        - Description present (10 points)

        Args:
            source: Twitter source dict

        Returns:
            Credibility score 0-100
        """
        score = 0.0

        # Verification status (20 points)
        if source.get('verified', False):
            score += 20.0

        # Account age (30 points)
        created_at = source.get('created_at', '')
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_date = datetime.strptime(created_at, '%Y-%m-%d')
                else:
                    created_date = created_at

                age_days = (datetime.utcnow() - created_date).days

                if age_days >= 2555:  # 7+ years
                    score += 30.0
                elif age_days >= 1825:  # 5+ years
                    score += 25.0
                elif age_days >= 1095:  # 3+ years
                    score += 20.0
                elif age_days >= 730:  # 2+ years
                    score += 15.0
                elif age_days >= 365:  # 1+ year
                    score += 10.0
                else:  # < 1 year
                    score += 5.0
            except:
                score += 10.0  # Default if parsing fails

        # Follower count (30 points)
        followers = source.get('followers_count', 0)
        if followers >= 1000000:  # 1M+
            score += 30.0
        elif followers >= 100000:  # 100K+
            score += 25.0
        elif followers >= 10000:  # 10K+
            score += 20.0
        elif followers >= 1000:  # 1K+
            score += 15.0
        elif followers >= 500:
            score += 10.0
        else:
            score += 5.0

        # Has description (10 points)
        if source.get('description'):
            score += 10.0

        # Maximum 100 points
        return min(score, 100.0)

    def _score_reddit_account(self, source: Dict[str, Any]) -> float:
        """
        Score Reddit account credibility.

        Factors:
        - Account age (0-30 points)
        - Combined karma (0-40 points)
        - Account exists (20 points if not deleted)

        Args:
            source: Reddit source dict

        Returns:
            Credibility score 0-100
        """
        score = 0.0
        username = source.get('username', '')

        # Account exists (20 points)
        if username and username != '[deleted]':
            score += 20.0

        # Account age (30 points)
        account_age_days = source.get('account_age_days', 0)

        if account_age_days >= 2555:  # 7+ years
            score += 30.0
        elif account_age_days >= 1825:  # 5+ years
            score += 25.0
        elif account_age_days >= 1095:  # 3+ years
            score += 20.0
        elif account_age_days >= 730:  # 2+ years
            score += 15.0
        elif account_age_days >= 365:  # 1+ year
            score += 10.0
        else:  # < 1 year
            score += 5.0

        # Combined karma (40 points)
        link_karma = source.get('link_karma', 0)
        comment_karma = source.get('comment_karma', 0)
        total_karma = link_karma + comment_karma

        if total_karma >= 100000:
            score += 40.0
        elif total_karma >= 50000:
            score += 35.0
        elif total_karma >= 10000:
            score += 30.0
        elif total_karma >= 5000:
            score += 25.0
        elif total_karma >= 1000:
            score += 20.0
        elif total_karma >= 500:
            score += 15.0
        else:
            score += 10.0

        # Cap at 100
        return min(score, 100.0)

    def _score_content_quality(self, source: Dict[str, Any]) -> float:
        """
        Score content quality based on indicators.

        Args:
            source: Source with optional content_indicators

        Returns:
            Content quality score 0-100
        """
        indicators = source.get('content_indicators', {})

        if not indicators:
            return 50.0  # Neutral if no indicators

        score = 0.0

        # Firsthand language (+30)
        if indicators.get('firsthand_language'):
            score += 30.0

        # Specific details (+30)
        if indicators.get('specific_details'):
            score += 30.0

        # Moderate emotional tone (+20)
        if indicators.get('emotional_tone') == 'moderate':
            score += 20.0
        elif indicators.get('emotional_tone') == 'high':
            score += 10.0  # Too emotional = less credible

        # Cap at 100
        return min(score, 100.0)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scorer = SocialSourceCredibility()

    # Test Twitter account scoring
    print("\n=== Twitter Account Scoring ===")

    twitter_verified = {
        'platform': 'twitter',
        'username': 'reuters',
        'verified': True,
        'created_at': '2008-03-10',
        'followers_count': 28000000,
        'description': 'Breaking news from Reuters'
    }
    score1 = scorer.score_source(twitter_verified)
    print(f"Reuters (verified): {score1}/100")

    # Test Reddit account scoring
    print("\n=== Reddit Account Scoring ===")

    reddit_high_karma = {
        'platform': 'reddit',
        'username': 'power_user',
        'account_age_days': 2555,
        'link_karma': 125000,
        'comment_karma': 8900
    }
    score2 = scorer.score_source(reddit_high_karma)
    print(f"power_user (7 years, 133k karma): {score2}/100")

    # Test combined scoring
    print("\n=== Combined Scoring ===")

    combined_source = {
        'platform': 'twitter',
        'username': 'worker_advocate',
        'verified': False,
        'created_at': '2020-01-15',
        'followers_count': 5432,
        'engagement_metrics': {
            'retweet_count': 234,
            'like_count': 567,
            'reply_count': 45
        },
        'content_indicators': {
            'firsthand_language': True,
            'specific_details': True,
            'emotional_tone': 'moderate'
        }
    }
    combined = scorer.score_combined(combined_source)
    print(f"Combined score breakdown:")
    print(f"  Total: {combined['total_score']}/100")
    print(f"  Account: {combined['account_score']}/100")
    print(f"  Engagement: {combined['engagement_score']}/100")
    print(f"  Content: {combined['content_score']}/100")
