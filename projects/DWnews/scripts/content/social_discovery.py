#!/usr/bin/env python3
"""
The Daily Worker - Social Media Discovery
Discovers trending topics from Twitter and Reddit
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from database.models import Topic, Category
from scripts.utils.text_utils import (
    clean_text, extract_keywords, categorize_by_keywords
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)


class TwitterDiscovery:
    """Twitter/X trending topics discovery"""

    def __init__(self, session):
        self.session = session
        self.client = None

        # Initialize Twitter client if credentials available
        if settings.twitter_bearer_token:
            try:
                import tweepy
                self.client = tweepy.Client(bearer_token=settings.twitter_bearer_token)
                logger.info("Twitter client initialized")
            except ImportError:
                logger.warning("tweepy not installed. Install: pip install tweepy")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")

    def discover_trending(self, country_code: str = "US", max_topics: int = 20) -> List[Dict]:
        """Discover trending topics on Twitter/X"""
        if not self.client:
            logger.warning("Twitter client not available")
            return []

        try:
            # Search for trending labor/worker related topics
            # Using Twitter API v2 free tier
            search_queries = [
                "union OR labor OR strike OR worker OR workplace",
                "inflation OR recession OR economy OR cost of living",
                "healthcare OR student debt OR housing crisis",
                "climate change OR environment OR renewable energy",
                "tech layoffs OR automation OR AI",
            ]

            topics = []
            for query in search_queries:
                try:
                    # Search recent tweets (last 7 days)
                    tweets = self.client.search_recent_tweets(
                        query=f"{query} -is:retweet lang:en",
                        max_results=20,
                        tweet_fields=['created_at', 'public_metrics', 'entities']
                    )

                    if not tweets.data:
                        continue

                    for tweet in tweets.data:
                        # Extract hashtags if available
                        hashtags = []
                        if hasattr(tweet, 'entities') and tweet.entities:
                            hashtags = [tag['tag'] for tag in tweet.entities.get('hashtags', [])]

                        # Calculate engagement score
                        metrics = tweet.public_metrics
                        engagement = (
                            metrics.get('like_count', 0) +
                            metrics.get('retweet_count', 0) * 2 +
                            metrics.get('reply_count', 0)
                        )

                        # Only include tweets with significant engagement
                        if engagement < 10:
                            continue

                        # Extract text
                        text = clean_text(tweet.text)
                        keywords = extract_keywords(text) + hashtags

                        # Auto-categorize
                        category_slug = categorize_by_keywords(text)
                        category = self.session.query(Category).filter_by(slug=category_slug).first()

                        topic_data = {
                            'title': text[:200],
                            'description': text[:500],
                            'keywords': ','.join(keywords[:10]),
                            'engagement_score': engagement / 100.0,  # Normalize
                            'category_id': category.id if category else None,
                            'discovered_from': 'Twitter',
                            'source_url': f"https://twitter.com/i/web/status/{tweet.id}"
                        }

                        topics.append(topic_data)

                except Exception as e:
                    logger.error(f"Error searching Twitter for '{query}': {e}")
                    continue

            # Remove duplicates and sort by engagement
            unique_topics = {t['title']: t for t in topics}.values()
            sorted_topics = sorted(unique_topics, key=lambda x: x['engagement_score'], reverse=True)

            logger.info(f"Discovered {len(sorted_topics)} topics from Twitter")
            return list(sorted_topics)[:max_topics]

        except Exception as e:
            logger.error(f"Twitter discovery failed: {e}")
            return []


class RedditDiscovery:
    """Reddit community topics discovery"""

    def __init__(self, session):
        self.session = session
        self.reddit = None

        # Initialize Reddit client if credentials available
        if settings.reddit_client_id and settings.reddit_client_secret:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=settings.reddit_client_id,
                    client_secret=settings.reddit_client_secret,
                    user_agent=settings.reddit_user_agent
                )
                logger.info("Reddit client initialized")
            except ImportError:
                logger.warning("praw not installed. Install: pip install praw")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit client: {e}")

    def discover_from_subreddit(self, subreddit_name: str, max_posts: int = 20) -> List[Dict]:
        """Discover topics from a specific subreddit"""
        if not self.reddit:
            logger.warning("Reddit client not available")
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            topics = []

            # Get hot posts from last week
            for post in subreddit.hot(limit=max_posts):
                # Skip stickied posts
                if post.stickied:
                    continue

                # Calculate engagement score
                engagement = post.score + post.num_comments * 2

                # Only include posts with significant engagement
                if engagement < 50:
                    continue

                # Extract text
                title = clean_text(post.title)
                description = clean_text(post.selftext[:500] if post.selftext else post.title)
                full_text = f"{title} {description}"

                # Extract keywords
                keywords = extract_keywords(full_text)

                # Auto-categorize
                category_slug = categorize_by_keywords(full_text)
                category = self.session.query(Category).filter_by(slug=category_slug).first()

                topic_data = {
                    'title': title,
                    'description': description,
                    'keywords': ','.join(keywords[:10]),
                    'engagement_score': engagement / 100.0,  # Normalize
                    'category_id': category.id if category else None,
                    'discovered_from': f'Reddit:r/{subreddit_name}',
                    'source_url': f"https://reddit.com{post.permalink}"
                }

                topics.append(topic_data)

            logger.info(f"Discovered {len(topics)} topics from r/{subreddit_name}")
            return topics

        except Exception as e:
            logger.error(f"Error discovering from r/{subreddit_name}: {e}")
            return []

    def discover_all_subreddits(self) -> List[Dict]:
        """Discover topics from multiple relevant subreddits"""
        subreddits = [
            'news',
            'politics',
            'WorkReform',
            'antiwork',
            'LateStageCapitalism',
            'economy',
            'labor',
            'socialism',
            'climate',
            'technology'
        ]

        all_topics = []
        for subreddit in subreddits:
            topics = self.discover_from_subreddit(subreddit, max_posts=10)
            all_topics.extend(topics)

        # Remove duplicates and sort by engagement
        unique_topics = {t['title']: t for t in all_topics}.values()
        sorted_topics = sorted(unique_topics, key=lambda x: x['engagement_score'], reverse=True)

        logger.info(f"Total topics discovered from Reddit: {len(sorted_topics)}")
        return list(sorted_topics)


def run_social_discovery(max_topics: int = 50) -> int:
    """Run social media discovery"""
    print("=" * 60)
    print("The Daily Worker - Social Media Discovery")
    print("=" * 60)

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        all_topics = []

        # Twitter discovery
        if settings.twitter_bearer_token:
            print("\nDiscovering from Twitter...")
            twitter = TwitterDiscovery(session)
            twitter_topics = twitter.discover_trending(max_topics=25)
            all_topics.extend(twitter_topics)
            print(f"  ✓ Found {len(twitter_topics)} topics")
        else:
            print("\n⚠ Twitter API not configured (skipping)")

        # Reddit discovery
        if settings.reddit_client_id:
            print("\nDiscovering from Reddit...")
            reddit = RedditDiscovery(session)
            reddit_topics = reddit.discover_all_subreddits()
            all_topics.extend(reddit_topics)
            print(f"  ✓ Found {len(reddit_topics)} topics")
        else:
            print("\n⚠ Reddit API not configured (skipping)")

        if not all_topics:
            print("\nNo topics discovered. Configure social media APIs in .env")
            return 0

        # Save topics to database
        saved_count = 0
        for topic_data in all_topics[:max_topics]:
            # Check for duplicates
            existing = session.query(Topic).filter_by(title=topic_data['title']).first()
            if existing:
                continue

            # Create topic
            topic = Topic(
                title=topic_data['title'],
                description=topic_data['description'],
                keywords=topic_data['keywords'],
                engagement_score=topic_data.get('engagement_score', 0),
                category_id=topic_data.get('category_id'),
                discovered_from=topic_data['discovered_from'],
                status='discovered'
            )

            session.add(topic)
            saved_count += 1

        session.commit()

        print("\n" + "=" * 60)
        print(f"✓ Social Media Discovery Complete")
        print("=" * 60)
        print(f"Topics discovered: {len(all_topics)}")
        print(f"Topics saved: {saved_count}")

        return saved_count

    except Exception as e:
        logger.error(f"Social discovery failed: {e}")
        print(f"\n✗ Error: {e}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    saved = run_social_discovery()

    if saved > 0:
        print(f"\nNext step: Run filter_topics.py to check viability")
