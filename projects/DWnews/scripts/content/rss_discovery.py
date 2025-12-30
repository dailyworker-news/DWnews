#!/usr/bin/env python3
"""
The Daily Worker - RSS Feed Discovery
Discovers topics from RSS feeds of credible news sources
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import feedparser
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from database.models import Source, Topic, Category
from scripts.utils.text_utils import (
    clean_text, extract_keywords, generate_text_hash, categorize_by_keywords
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)


class RSSDiscovery:
    """RSS feed discovery service"""

    def __init__(self, session):
        self.session = session
        self.discovered_topics = []

    def discover_from_source(self, source: Source) -> List[Dict]:
        """Discover topics from a single RSS source"""
        if not source.rss_feed:
            logger.warning(f"No RSS feed configured for {source.name}")
            return []

        logger.info(f"Fetching RSS feed from {source.name}: {source.rss_feed}")

        try:
            # Parse RSS feed
            feed = feedparser.parse(source.rss_feed)

            if not feed.entries:
                logger.warning(f"No entries found in {source.name} feed")
                return []

            topics = []
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                # Extract entry data
                title = clean_text(entry.get('title', ''))
                description = clean_text(entry.get('description', '') or entry.get('summary', ''))
                link = entry.get('link', '')

                if not title:
                    continue

                # Generate content hash for deduplication
                content_hash = generate_text_hash(title + " " + description)

                # Extract keywords
                full_text = f"{title} {description}"
                keywords = extract_keywords(full_text, max_keywords=10)

                # Auto-categorize
                category_slug = categorize_by_keywords(full_text)
                category = self.session.query(Category).filter_by(slug=category_slug).first()

                # Published date
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    published_date = datetime(*published[:6])
                else:
                    published_date = datetime.utcnow()

                # Only include recent topics (last 7 days)
                if (datetime.utcnow() - published_date).days > 7:
                    continue

                topic_data = {
                    'title': title,
                    'description': description[:500],  # Truncate long descriptions
                    'keywords': ','.join(keywords),
                    'source_url': link,
                    'source_name': source.name,
                    'source_id': source.id,
                    'content_hash': content_hash,
                    'category_id': category.id if category else None,
                    'discovered_from': f'RSS:{source.name}',
                    'published_date': published_date
                }

                topics.append(topic_data)

            logger.info(f"Discovered {len(topics)} topics from {source.name}")
            return topics

        except Exception as e:
            logger.error(f"Error fetching RSS feed from {source.name}: {e}")
            return []

    def discover_all_rss(self) -> List[Dict]:
        """Discover topics from all active RSS sources"""
        logger.info("Starting RSS discovery from all sources")

        # Get all active sources with RSS feeds
        sources = self.session.query(Source).filter(
            Source.is_active == True,
            Source.rss_feed.isnot(None)
        ).all()

        logger.info(f"Found {len(sources)} active RSS sources")

        all_topics = []
        for source in sources:
            topics = self.discover_from_source(source)
            all_topics.extend(topics)

        logger.info(f"Total topics discovered: {len(all_topics)}")
        return all_topics

    def save_topics(self, topics: List[Dict]) -> int:
        """Save discovered topics to database (avoiding duplicates)"""
        saved_count = 0
        duplicate_count = 0

        for topic_data in topics:
            # Check if topic already exists (by content hash)
            existing = self.session.query(Topic).filter_by(
                title=topic_data['title']
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # Create new topic
            topic = Topic(
                title=topic_data['title'],
                description=topic_data['description'],
                keywords=topic_data['keywords'],
                discovered_from=topic_data['discovered_from'],
                category_id=topic_data.get('category_id'),
                status='discovered'
            )

            self.session.add(topic)
            saved_count += 1

        try:
            self.session.commit()
            logger.info(f"Saved {saved_count} new topics, skipped {duplicate_count} duplicates")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving topics: {e}")
            raise

        return saved_count


def run_discovery(max_topics: int = 100) -> int:
    """Run RSS discovery and save topics"""
    print("=" * 60)
    print("The Daily Worker - RSS Feed Discovery")
    print("=" * 60)

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Initialize discovery service
        discovery = RSSDiscovery(session)

        # Discover topics
        print("\nDiscovering topics from RSS feeds...")
        topics = discovery.discover_all_rss()

        if not topics:
            print("No topics discovered")
            return 0

        # Limit topics if needed
        if len(topics) > max_topics:
            print(f"Limiting to {max_topics} most recent topics")
            topics = topics[:max_topics]

        # Save topics
        print(f"\nSaving {len(topics)} topics to database...")
        saved_count = discovery.save_topics(topics)

        # Show summary
        print("\n" + "=" * 60)
        print(f"✓ RSS Discovery Complete")
        print("=" * 60)
        print(f"Topics discovered: {len(topics)}")
        print(f"Topics saved: {saved_count}")
        print(f"Duplicates skipped: {len(topics) - saved_count}")

        # Show category breakdown
        print("\nCategory breakdown:")
        for category in session.query(Category).all():
            count = session.query(Topic).filter_by(
                category_id=category.id,
                status='discovered'
            ).count()
            if count > 0:
                print(f"  - {category.name}: {count}")

        return saved_count

    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        print(f"\n✗ Error: {e}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    saved = run_discovery()

    if saved > 0:
        print(f"\nNext step: Run filter_topics.py to check viability")
    else:
        print("\nNo new topics discovered. Check your RSS feed sources.")
