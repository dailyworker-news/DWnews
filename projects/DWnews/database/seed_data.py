#!/usr/bin/env python3
"""
The Daily Worker - Seed Data
Populates database with initial credible sources, regions, and categories
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Source, Region, Category
from backend.config import settings


def seed_database():
    """Seed database with initial data"""

    print("=" * 60)
    print("The Daily Worker - Seeding Database")
    print("=" * 60)

    # Create engine and session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Seed credible news sources
        print("\nSeeding news sources...")
        sources = [
            # News Wires (5/5 credibility)
            Source(
                name="Associated Press",
                url="https://apnews.com",
                rss_feed="https://apnews.com/rss",
                credibility_score=5,
                source_type="news_wire",
                political_lean="center"
            ),
            Source(
                name="Reuters",
                url="https://www.reuters.com",
                rss_feed="https://www.reuters.com/rssFeed",
                credibility_score=5,
                source_type="news_wire",
                political_lean="center"
            ),
            Source(
                name="AFP - Agence France-Presse",
                url="https://www.afp.com",
                rss_feed="https://www.afp.com/en/rss",
                credibility_score=5,
                source_type="news_wire",
                political_lean="center"
            ),

            # Investigative Journalism (5/5 credibility)
            Source(
                name="ProPublica",
                url="https://www.propublica.org",
                rss_feed="https://www.propublica.org/feeds/propublica/main",
                credibility_score=5,
                source_type="investigative",
                political_lean="center-left"
            ),
            Source(
                name="The Intercept",
                url="https://theintercept.com",
                rss_feed="https://theintercept.com/feed/",
                credibility_score=5,
                source_type="investigative",
                political_lean="left"
            ),

            # Labor & Working Class Focused (4-5/5 credibility)
            Source(
                name="Labor Notes",
                url="https://labornotes.org",
                rss_feed="https://labornotes.org/rss.xml",
                credibility_score=4,
                source_type="investigative",
                political_lean="left"
            ),
            Source(
                name="In These Times",
                url="https://inthesetimes.com",
                rss_feed="https://inthesetimes.com/feed",
                credibility_score=4,
                source_type="investigative",
                political_lean="left"
            ),

            # Academic & Research (5/5 credibility)
            Source(
                name="Economic Policy Institute",
                url="https://www.epi.org",
                rss_feed="https://www.epi.org/feed/",
                credibility_score=5,
                source_type="academic",
                political_lean="center-left"
            ),
            Source(
                name="Brookings Institution",
                url="https://www.brookings.edu",
                rss_feed="https://www.brookings.edu/feed/",
                credibility_score=5,
                source_type="academic",
                political_lean="center"
            ),
            Source(
                name="Center for American Progress",
                url="https://www.americanprogress.org",
                rss_feed="https://www.americanprogress.org/feed/",
                credibility_score=4,
                source_type="academic",
                political_lean="center-left"
            ),

            # National News (4/5 credibility)
            Source(
                name="NPR",
                url="https://www.npr.org",
                rss_feed="https://feeds.npr.org/1001/rss.xml",
                credibility_score=4,
                source_type="news_wire",
                political_lean="center-left"
            ),
            Source(
                name="BBC News",
                url="https://www.bbc.com/news",
                rss_feed="http://feeds.bbci.co.uk/news/rss.xml",
                credibility_score=5,
                source_type="news_wire",
                political_lean="center"
            ),

            # Social/Trending Sources (3/5 credibility - verification required)
            Source(
                name="Twitter/X Trending",
                url="https://twitter.com",
                credibility_score=3,
                source_type="social",
                political_lean="center",
                is_active=True
            ),
            Source(
                name="Reddit - r/news",
                url="https://reddit.com/r/news",
                credibility_score=3,
                source_type="social",
                political_lean="center",
                is_active=True
            ),
            Source(
                name="Reddit - r/WorkReform",
                url="https://reddit.com/r/WorkReform",
                credibility_score=3,
                source_type="social",
                political_lean="left",
                is_active=True
            ),
        ]

        # Add sources (skip if already exists)
        added_sources = 0
        for source in sources:
            existing = session.query(Source).filter_by(name=source.name).first()
            if not existing:
                session.add(source)
                added_sources += 1

        session.commit()
        print(f"✓ Added {added_sources} news sources (total: {session.query(Source).count()})")

        # Seed categories
        print("\nSeeding categories...")
        categories = [
            Category(name="Labor", slug="labor", description="Workers' rights, unions, strikes, workplace issues", sort_order=1),
            Category(name="Tech", slug="tech", description="Technology impacting workers and society", sort_order=2),
            Category(name="Politics", slug="politics", description="Political news affecting working-class Americans", sort_order=3),
            Category(name="Economics", slug="economics", description="Economic policy, inequality, cost of living", sort_order=4),
            Category(name="Current Affairs", slug="current-affairs", description="General news and current events", sort_order=5),
            Category(name="Art & Culture", slug="art-culture", description="Arts, culture, and entertainment", sort_order=6),
            Category(name="Sport", slug="sport", description="Sports news and analysis", sort_order=7),
            Category(name="Good News", slug="good-news", description="Positive developments and victories", sort_order=8),
            Category(name="Environment", slug="environment", description="Climate, environment, and sustainability", sort_order=9),
        ]

        added_categories = 0
        for category in categories:
            existing = session.query(Category).filter_by(slug=category.slug).first()
            if not existing:
                session.add(category)
                added_categories += 1

        session.commit()
        print(f"✓ Added {added_categories} categories (total: {session.query(Category).count()})")

        # Seed regions
        print("\nSeeding regions...")
        regions = [
            Region(name="National", region_type="national"),
            Region(name="California", region_type="state", state_code="CA", population=39_000_000),
            Region(name="New York", region_type="state", state_code="NY", population=19_500_000),
            Region(name="Texas", region_type="state", state_code="TX", population=30_000_000),
            Region(name="Florida", region_type="state", state_code="FL", population=22_000_000),
            Region(name="Midwest", region_type="metro", population=68_000_000),
            Region(name="Test Region", region_type="metro", population=1_000_000, is_active=True),
        ]

        added_regions = 0
        for region in regions:
            existing = session.query(Region).filter_by(name=region.name).first()
            if not existing:
                session.add(region)
                added_regions += 1

        session.commit()
        print(f"✓ Added {added_regions} regions (total: {session.query(Region).count()})")

        print("\n" + "=" * 60)
        print("✓ Database seeded successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - News Sources: {session.query(Source).count()}")
        print(f"  - Categories: {session.query(Category).count()}")
        print(f"  - Regions: {session.query(Region).count()}")

    except Exception as e:
        session.rollback()
        print(f"\n✗ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        seed_database()
        print("\nNext step: Run test_data.py to generate test articles")
    except Exception as e:
        print(f"\n✗ Failed to seed database: {e}")
        sys.exit(1)
