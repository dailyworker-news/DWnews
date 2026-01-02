"""
Monitoring Agent - Post-Publication Monitoring

Monitors published articles for 7 days to:
1. Track social media mentions (Twitter/Reddit)
2. Detect corrections needed (source retractions, factual disputes)
3. Update source reliability scores

Monitoring Schedule:
- Run daily for 7 days post-publication
- Stop monitoring after 7 days (or when article corrected/retracted)

Responsibilities:
- Social Mention Tracking: Track Twitter/Reddit mentions and engagement
- Correction Detection: Monitor for retractions, updates, factual disputes
- Source Reliability Updates: Update source credibility scores based on performance
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Article, Correction, Source, SourceReliabilityLog
from backend.logging_config import get_logger

logger = get_logger(__name__)


class MonitoringAgent:
    """
    Post-publication monitoring agent
    """

    # Monitoring period (days)
    MONITORING_PERIOD = 7

    def __init__(self, session: Session):
        """
        Initialize the Monitoring Agent

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

        # Check if social media APIs are configured
        self.twitter_enabled = self._check_twitter_config()
        self.reddit_enabled = self._check_reddit_config()

    def monitor_published_articles(self) -> Dict:
        """
        Monitor all articles published in last 7 days

        Returns:
            Dict with monitoring statistics
        """
        logger.info("Starting post-publication monitoring")

        # Get articles published in last 7 days
        monitoring_threshold = datetime.utcnow() - timedelta(days=self.MONITORING_PERIOD)

        articles = self.session.query(Article).filter(
            Article.status == 'published',
            Article.published_at >= monitoring_threshold,
            Article.published_at.isnot(None)
        ).all()

        if not articles:
            logger.info("No articles in monitoring window")
            return {
                'total_monitored': 0,
                'mentions_found': 0,
                'corrections_flagged': 0,
                'sources_updated': 0
            }

        total_mentions = 0
        total_corrections = 0
        total_sources_updated = 0

        for article in articles:
            try:
                # Check social mentions
                mentions = self.check_social_mentions(article)
                total_mentions += len(mentions)

                # Detect corrections needed
                correction_flag = self.detect_corrections_needed(article)
                if correction_flag:
                    total_corrections += 1

                # Update source reliability
                sources_updated = self.update_source_reliability(article)
                total_sources_updated += sources_updated

                logger.info(
                    f"Monitored article {article.id}: "
                    f"{len(mentions)} mentions, "
                    f"correction={'flagged' if correction_flag else 'none'}, "
                    f"{sources_updated} sources updated"
                )

            except Exception as e:
                logger.error(f"Error monitoring article {article.id}: {e}")
                continue

        return {
            'total_monitored': len(articles),
            'mentions_found': total_mentions,
            'corrections_flagged': total_corrections,
            'sources_updated': total_sources_updated
        }

    def check_social_mentions(self, article: Article) -> List[Dict]:
        """
        Check Twitter/Reddit for article mentions

        Args:
            article: Article instance

        Returns:
            List of mention dicts with platform, url, engagement metrics
        """
        mentions = []

        # Construct article URL (assuming slug-based URLs)
        article_url = f"https://thedailyworker.com/article/{article.slug}"

        # Check Twitter mentions
        if self.twitter_enabled:
            try:
                twitter_mentions = self._check_twitter_mentions(article_url, article.title)
                mentions.extend(twitter_mentions)
            except Exception as e:
                logger.error(f"Error checking Twitter mentions for article {article.id}: {e}")

        # Check Reddit mentions
        if self.reddit_enabled:
            try:
                reddit_mentions = self._check_reddit_mentions(article_url, article.title)
                mentions.extend(reddit_mentions)
            except Exception as e:
                logger.error(f"Error checking Reddit mentions for article {article.id}: {e}")

        return mentions

    def detect_corrections_needed(self, article: Article) -> Optional[Dict]:
        """
        Check if article needs correction

        Detection methods:
        1. Check if original sources have issued retractions/updates
        2. Monitor social feedback for factual disputes
        3. Check if verification sources have changed

        Args:
            article: Article instance

        Returns:
            Correction flag dict if issue detected, None otherwise
        """
        # Check if article already has pending corrections
        existing_corrections = self.session.query(Correction).filter(
            Correction.article_id == article.id,
            Correction.status.in_(['pending', 'verified'])
        ).count()

        if existing_corrections > 0:
            logger.info(f"Article {article.id} already has pending corrections")
            return None

        # For MVP, implement basic source retraction checking
        # Future: Add AI analysis of social feedback for factual disputes

        # Check article sources for updates/retractions
        correction_needed = self._check_source_updates(article)

        return correction_needed

    def update_source_reliability(self, article: Article) -> int:
        """
        Update source reliability scores based on article performance

        Scoring Logic:
        - Article remains accurate for 7 days: +5 points per source
        - Source issues correction: -10 points
        - Source retracts article: -30 points

        Args:
            article: Article instance

        Returns:
            Number of sources updated
        """
        # Check if article is at least 7 days old
        article_age = datetime.utcnow() - article.published_at
        if article_age < timedelta(days=7):
            return 0  # Not old enough to update reliability

        # Check if we've already updated reliability for this article
        existing_logs = self.session.query(SourceReliabilityLog).filter(
            SourceReliabilityLog.article_id == article.id,
            SourceReliabilityLog.event_type == 'article_published'
        ).count()

        if existing_logs > 0:
            return 0  # Already updated

        # Get article sources
        sources = article.sources
        if not sources:
            return 0

        sources_updated = 0

        for source in sources:
            try:
                # Check if article has corrections related to this source
                has_correction = self.session.query(Correction).filter(
                    Correction.article_id == article.id,
                    Correction.status == 'published'
                ).count() > 0

                if has_correction:
                    # Source had issues - decrease score
                    score_change = -10
                    event_type = 'correction_issued'
                else:
                    # Source remained accurate - increase score
                    score_change = +5
                    event_type = 'fact_check_pass'

                # Update source credibility score
                previous_score = source.credibility_score
                new_score = max(1, min(5, previous_score + (score_change / 20)))  # Keep in 1-5 range

                # Log the reliability update
                log_entry = SourceReliabilityLog(
                    source_id=source.id,
                    event_type=event_type,
                    reliability_delta=score_change / 20,  # Normalize to credibility_score scale
                    previous_score=previous_score,
                    new_score=int(round(new_score)),
                    article_id=article.id,
                    notes=f"Article {article.id} monitored for 7 days",
                    automated_adjustment=True,
                    logged_at=datetime.utcnow()
                )

                self.session.add(log_entry)
                source.credibility_score = int(round(new_score))
                sources_updated += 1

            except Exception as e:
                logger.error(f"Error updating reliability for source {source.id}: {e}")
                continue

        if sources_updated > 0:
            self.session.commit()
            logger.info(f"Updated reliability for {sources_updated} sources from article {article.id}")

        return sources_updated

    def _check_twitter_config(self) -> bool:
        """Check if Twitter API is configured"""
        twitter_bearer = os.getenv('TWITTER_BEARER_TOKEN')
        return twitter_bearer is not None

    def _check_reddit_config(self) -> bool:
        """Check if Reddit API is configured"""
        reddit_client = os.getenv('REDDIT_CLIENT_ID')
        reddit_secret = os.getenv('REDDIT_CLIENT_SECRET')
        return reddit_client is not None and reddit_secret is not None

    def _check_twitter_mentions(self, article_url: str, article_title: str) -> List[Dict]:
        """
        Check Twitter for article mentions

        Args:
            article_url: Full URL of the article
            article_title: Article title

        Returns:
            List of mention dicts
        """
        mentions = []

        try:
            import tweepy

            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if not bearer_token:
                logger.warning("Twitter API not configured")
                return mentions

            client = tweepy.Client(bearer_token=bearer_token)

            # Search for URL mentions
            url_query = f'url:"{article_url}"'
            url_tweets = client.search_recent_tweets(
                query=url_query,
                max_results=10,
                tweet_fields=['created_at', 'public_metrics']
            )

            if url_tweets.data:
                for tweet in url_tweets.data:
                    mentions.append({
                        'platform': 'twitter',
                        'mention_type': 'url',
                        'url': f"https://twitter.com/i/web/status/{tweet.id}",
                        'created_at': tweet.created_at,
                        'engagement': {
                            'retweets': tweet.public_metrics['retweet_count'],
                            'likes': tweet.public_metrics['like_count'],
                            'replies': tweet.public_metrics['reply_count']
                        }
                    })

            # Search for title mentions (first 50 chars to avoid query length issues)
            title_query = f'"{article_title[:50]}"'
            title_tweets = client.search_recent_tweets(
                query=title_query,
                max_results=10,
                tweet_fields=['created_at', 'public_metrics']
            )

            if title_tweets.data:
                for tweet in title_tweets.data:
                    # Avoid duplicates
                    if not any(m['url'] == f"https://twitter.com/i/web/status/{tweet.id}" for m in mentions):
                        mentions.append({
                            'platform': 'twitter',
                            'mention_type': 'title',
                            'url': f"https://twitter.com/i/web/status/{tweet.id}",
                            'created_at': tweet.created_at,
                            'engagement': {
                                'retweets': tweet.public_metrics['retweet_count'],
                                'likes': tweet.public_metrics['like_count'],
                                'replies': tweet.public_metrics['reply_count']
                            }
                        })

        except Exception as e:
            logger.error(f"Error checking Twitter mentions: {e}")

        return mentions

    def _check_reddit_mentions(self, article_url: str, article_title: str) -> List[Dict]:
        """
        Check Reddit for article mentions

        Args:
            article_url: Full URL of the article
            article_title: Article title

        Returns:
            List of mention dicts
        """
        mentions = []

        try:
            import praw

            client_id = os.getenv('REDDIT_CLIENT_ID')
            client_secret = os.getenv('REDDIT_CLIENT_SECRET')
            user_agent = os.getenv('REDDIT_USER_AGENT', 'DWnews Monitoring Agent v1.0')

            if not client_id or not client_secret:
                logger.warning("Reddit API not configured")
                return mentions

            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )

            # Search for URL submissions
            url_submissions = reddit.subreddit('all').search(article_url, limit=10)

            for submission in url_submissions:
                mentions.append({
                    'platform': 'reddit',
                    'mention_type': 'url',
                    'url': f"https://reddit.com{submission.permalink}",
                    'created_at': datetime.fromtimestamp(submission.created_utc),
                    'engagement': {
                        'upvotes': submission.score,
                        'comments': submission.num_comments,
                        'upvote_ratio': submission.upvote_ratio
                    }
                })

            # Search for title mentions
            title_submissions = reddit.subreddit('all').search(article_title, limit=10)

            for submission in title_submissions:
                # Avoid duplicates
                submission_url = f"https://reddit.com{submission.permalink}"
                if not any(m['url'] == submission_url for m in mentions):
                    mentions.append({
                        'platform': 'reddit',
                        'mention_type': 'title',
                        'url': submission_url,
                        'created_at': datetime.fromtimestamp(submission.created_utc),
                        'engagement': {
                            'upvotes': submission.score,
                            'comments': submission.num_comments,
                            'upvote_ratio': submission.upvote_ratio
                        }
                    })

        except Exception as e:
            logger.error(f"Error checking Reddit mentions: {e}")

        return mentions

    def _check_source_updates(self, article: Article) -> Optional[Dict]:
        """
        Check if article sources have issued updates or retractions

        Args:
            article: Article instance

        Returns:
            Correction flag dict if issue detected, None otherwise
        """
        # For MVP, this is a placeholder
        # Full implementation would:
        # 1. Re-fetch original source URLs
        # 2. Check for retraction notices
        # 3. Compare current source content with archived version
        # 4. Use AI to detect significant changes

        # Placeholder: Return None (no corrections needed)
        # In production, implement source re-checking logic here

        return None


def main():
    """
    Main function for running the Monitoring Agent standalone
    """
    from database import get_session

    session = get_session()
    agent = MonitoringAgent(session)

    print("=" * 60)
    print("MONITORING AGENT - Post-Publication Monitoring")
    print("=" * 60)

    # Check API configuration
    print(f"\nAPI Configuration:")
    print(f"  Twitter API: {'Enabled' if agent.twitter_enabled else 'Disabled (set TWITTER_BEARER_TOKEN)'}")
    print(f"  Reddit API: {'Enabled' if agent.reddit_enabled else 'Disabled (set REDDIT_CLIENT_ID/SECRET)'}")

    # Monitor published articles
    print(f"\nMonitoring articles published in last {agent.MONITORING_PERIOD} days...")
    results = agent.monitor_published_articles()

    print(f"\n{'=' * 60}")
    print("RESULTS:")
    print(f"{'=' * 60}")
    print(f"Total monitored: {results['total_monitored']}")
    print(f"Social mentions found: {results['mentions_found']}")
    print(f"Corrections flagged: {results['corrections_flagged']}")
    print(f"Sources updated: {results['sources_updated']}")

    session.close()


if __name__ == '__main__':
    main()
