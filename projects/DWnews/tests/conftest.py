"""
Pytest configuration and shared fixtures
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Base, Source, Region, Category, Article, Topic
from backend.config import settings


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Create test database session for each test"""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_source(db_session):
    """Create a sample news source"""
    source = Source(
        name="Test News Wire",
        url="https://test.example.com",
        rss_feed="https://test.example.com/rss",
        credibility_score=5,
        source_type="news_wire",
        political_lean="center",
        is_active=True
    )
    db_session.add(source)
    db_session.commit()
    return source


@pytest.fixture
def sample_category(db_session):
    """Create a sample category"""
    category = Category(
        name="Labor",
        slug="labor",
        description="Workers' rights and labor issues",
        sort_order=1,
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_region(db_session):
    """Create a sample region"""
    region = Region(
        name="National",
        region_type="national",
        is_active=True
    )
    db_session.add(region)
    db_session.commit()
    return region


@pytest.fixture
def sample_topic(db_session, sample_category):
    """Create a sample topic"""
    topic = Topic(
        title="Amazon Workers Win Union Vote",
        description="Historic union victory at Amazon warehouse",
        keywords="amazon,union,labor,victory",
        discovered_from="RSS:Test Source",
        category_id=sample_category.id,
        status="discovered"
    )
    db_session.add(topic)
    db_session.commit()
    return topic


@pytest.fixture
def sample_article(db_session, sample_category):
    """Create a sample article"""
    article = Article(
        title="Test Article Title",
        slug="test-article-title",
        body="This is a test article body with sufficient content for testing.",
        summary="Test summary",
        category_id=sample_category.id,
        is_national=True,
        reading_level=8.0,
        word_count=100,
        status="draft"
    )
    db_session.add(article)
    db_session.commit()
    return article
