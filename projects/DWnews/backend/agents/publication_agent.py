"""
Publication Agent - Auto-Publishing System

Handles auto-publishing of approved articles and triggering monitoring workflows.

Publishing Logic:
1. Query articles with status='approved'
2. Update status to 'published' and set published_at timestamp
3. Optionally post to social media (manual for MVP)
4. Trigger Monitoring Agent for 7-day watch
5. Log publication event

Publishing Schedule:
- Production: Publish approved articles at 5pm daily (via cron)
- Can also publish immediately via admin action
- Respect publication calendar (don't publish on certain dates if configured)
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Article
from backend.logging_config import get_logger

logger = get_logger(__name__)


class PublicationAgent:
    """
    Auto-publishing agent for approved articles
    """

    def __init__(self, session: Session):
        """
        Initialize the Publication Agent

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def publish_approved_articles(self, limit: Optional[int] = None) -> Dict:
        """
        Publish all approved articles

        Args:
            limit: Optional limit on number of articles to publish

        Returns:
            Dict with publication statistics
        """
        logger.info("Starting auto-publication of approved articles")

        # Query articles with status='approved'
        query = self.session.query(Article).filter(
            Article.status == 'approved',
            Article.published_at.is_(None)  # Not already published
        ).order_by(Article.created_at.asc())  # Oldest first

        if limit:
            query = query.limit(limit)

        articles = query.all()

        if not articles:
            logger.info("No approved articles to publish")
            return {
                'total_published': 0,
                'article_ids': [],
                'errors': []
            }

        published_ids = []
        errors = []

        for article in articles:
            try:
                success = self.publish_article(article.id)
                if success:
                    published_ids.append(article.id)
                    logger.info(f"Published article {article.id}: {article.title}")
                else:
                    errors.append({
                        'article_id': article.id,
                        'error': 'Publication failed'
                    })
            except Exception as e:
                logger.error(f"Error publishing article {article.id}: {e}")
                errors.append({
                    'article_id': article.id,
                    'error': str(e)
                })

        logger.info(f"Published {len(published_ids)} articles")

        return {
            'total_published': len(published_ids),
            'article_ids': published_ids,
            'errors': errors
        }

    def publish_article(self, article_id: int) -> bool:
        """
        Publish single article

        Args:
            article_id: Article ID to publish

        Returns:
            True if successful, False otherwise
        """
        try:
            article = self.session.query(Article).filter(
                Article.id == article_id
            ).first()

            if not article:
                logger.error(f"Article {article_id} not found")
                return False

            # Verify article is approved
            if article.status != 'approved':
                logger.error(f"Article {article_id} status is '{article.status}', not 'approved'")
                return False

            # Check if already published
            if article.published_at is not None:
                logger.warning(f"Article {article_id} already published at {article.published_at}")
                return False

            # Update article status
            article.status = 'published'
            article.published_at = datetime.utcnow()

            self.session.commit()

            logger.info(f"Successfully published article {article_id}: {article.title}")

            # Optionally post to social media (manual for MVP)
            # self._post_to_social_media(article)

            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error publishing article {article_id}: {e}")
            return False

    def schedule_publication(
        self,
        article_id: int,
        publish_at: datetime
    ) -> bool:
        """
        Schedule future publication (placeholder for future enhancement)

        Args:
            article_id: Article ID to schedule
            publish_at: Datetime to publish at

        Returns:
            True if scheduled successfully

        Note:
            For MVP, this just validates the request.
            Full implementation would use a job queue (Celery, etc.)
        """
        logger.info(f"Schedule publication requested for article {article_id} at {publish_at}")

        article = self.session.query(Article).filter(
            Article.id == article_id
        ).first()

        if not article:
            logger.error(f"Article {article_id} not found")
            return False

        if article.status != 'approved':
            logger.error(f"Article {article_id} must be approved to schedule publication")
            return False

        # For MVP, log the request but don't implement scheduling
        logger.warning("Scheduled publication not yet implemented. Publish manually at scheduled time.")
        return False

    def unpublish_article(self, article_id: int, reason: str) -> bool:
        """
        Unpublish an article (use sparingly - prefer corrections)

        Args:
            article_id: Article ID to unpublish
            reason: Reason for unpublishing

        Returns:
            True if successful

        Note:
            This should only be used in extreme cases (legal issues, major errors).
            Prefer using the correction workflow for normal corrections.
        """
        try:
            article = self.session.query(Article).filter(
                Article.id == article_id
            ).first()

            if not article:
                logger.error(f"Article {article_id} not found")
                return False

            if article.status != 'published':
                logger.error(f"Article {article_id} is not published (status: {article.status})")
                return False

            # Move to archived status
            article.status = 'archived'

            # Log the reason
            if article.editorial_notes:
                article.editorial_notes += f"\n\nUNPUBLISHED {datetime.utcnow()}: {reason}"
            else:
                article.editorial_notes = f"UNPUBLISHED {datetime.utcnow()}: {reason}"

            self.session.commit()

            logger.warning(f"Unpublished article {article_id}: {reason}")
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error unpublishing article {article_id}: {e}")
            return False

    def get_publication_stats(self) -> Dict:
        """
        Get publication statistics

        Returns:
            Dict with publication stats
        """
        from sqlalchemy import func

        # Count published articles
        total_published = self.session.query(Article).filter(
            Article.status == 'published'
        ).count()

        # Count approved but not published
        approved_pending = self.session.query(Article).filter(
            Article.status == 'approved',
            Article.published_at.is_(None)
        ).count()

        # Get recent publications (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_published = self.session.query(Article).filter(
            Article.status == 'published',
            Article.published_at >= seven_days_ago
        ).count()

        # Average time from creation to publication
        avg_time = self.session.query(
            func.avg(
                func.extract('epoch', Article.published_at - Article.created_at)
            )
        ).filter(
            Article.status == 'published',
            Article.published_at.isnot(None)
        ).scalar()

        avg_hours = round(avg_time / 3600, 1) if avg_time else 0

        return {
            'total_published': total_published,
            'approved_pending': approved_pending,
            'recent_published_7d': recent_published,
            'avg_creation_to_publication_hours': avg_hours
        }

    def _post_to_social_media(self, article: Article) -> Dict:
        """
        Post article to social media (placeholder for future enhancement)

        Args:
            article: Article instance to post

        Returns:
            Dict with posting results

        Note:
            For MVP, this is manual. Future implementation would use Twitter/Reddit APIs.
        """
        logger.info(f"Social media posting requested for article {article.id}")

        # Placeholder for Twitter posting
        # twitter_url = self._post_to_twitter(article)

        # Placeholder for Reddit posting
        # reddit_url = self._post_to_reddit(article)

        logger.warning("Social media posting not yet implemented. Post manually.")

        return {
            'twitter': None,
            'reddit': None,
            'manual_posting_required': True
        }

    def _post_to_twitter(self, article: Article) -> Optional[str]:
        """
        Post article to Twitter (future enhancement)

        Args:
            article: Article to post

        Returns:
            Tweet URL if successful, None otherwise
        """
        # TODO: Implement Twitter posting using tweepy
        # import tweepy
        # client = tweepy.Client(...)
        # tweet_text = f"{article.title}\n\n{article.url}"
        # response = client.create_tweet(text=tweet_text)
        pass

    def _post_to_reddit(self, article: Article) -> Optional[str]:
        """
        Post article to Reddit (future enhancement)

        Args:
            article: Article to post

        Returns:
            Reddit submission URL if successful, None otherwise
        """
        # TODO: Implement Reddit posting using praw
        # import praw
        # reddit = praw.Reddit(...)
        # submission = reddit.subreddit('news').submit(title=article.title, url=article.url)
        pass


def main():
    """
    Main function for running the Publication Agent standalone
    """
    from database import get_session

    session = get_session()
    agent = PublicationAgent(session)

    print("=" * 60)
    print("PUBLICATION AGENT - Auto-Publishing System")
    print("=" * 60)

    # Get current stats
    stats = agent.get_publication_stats()
    print(f"\nCurrent Status:")
    print(f"  Total published: {stats['total_published']}")
    print(f"  Approved pending publication: {stats['approved_pending']}")
    print(f"  Published in last 7 days: {stats['recent_published_7d']}")
    print(f"  Avg creation to publication: {stats['avg_creation_to_publication_hours']} hours")

    if stats['approved_pending'] == 0:
        print("\nNo approved articles to publish.")
        session.close()
        return

    # Publish approved articles
    print(f"\nPublishing {stats['approved_pending']} approved articles...")
    results = agent.publish_approved_articles()

    print(f"\n{'=' * 60}")
    print("RESULTS:")
    print(f"{'=' * 60}")
    print(f"Total published: {results['total_published']}")

    if results['article_ids']:
        print(f"\nPublished article IDs: {results['article_ids']}")

    if results['errors']:
        print(f"\nErrors encountered:")
        for error in results['errors']:
            print(f"  Article {error['article_id']}: {error['error']}")

    # Show updated stats
    updated_stats = agent.get_publication_stats()
    print(f"\nUpdated Status:")
    print(f"  Total published: {updated_stats['total_published']}")
    print(f"  Approved pending publication: {updated_stats['approved_pending']}")

    session.close()


if __name__ == '__main__':
    main()
