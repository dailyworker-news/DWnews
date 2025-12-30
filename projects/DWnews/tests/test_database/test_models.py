"""
Tests for database models
"""

import pytest
from datetime import datetime
from database.models import Source, Region, Category, Article, Topic


class TestSourceModel:
    """Test Source model"""

    def test_create_source(self, db_session):
        """Test creating a news source"""
        source = Source(
            name="Associated Press",
            url="https://apnews.com",
            rss_feed="https://apnews.com/rss",
            credibility_score=5,
            source_type="news_wire",
            political_lean="center"
        )
        db_session.add(source)
        db_session.commit()

        assert source.id is not None
        assert source.name == "Associated Press"
        assert source.is_active is True
        assert source.created_at is not None

    def test_source_credibility_validation(self, db_session):
        """Test credibility score constraint"""
        # Valid score
        source = Source(
            name="Test Source",
            url="https://test.com",
            credibility_score=5,
            source_type="news_wire"
        )
        db_session.add(source)
        db_session.commit()
        assert source.credibility_score == 5

    def test_source_type_validation(self, db_session):
        """Test source type validation"""
        valid_types = ['news_wire', 'investigative', 'academic', 'local', 'social']
        for source_type in valid_types:
            source = Source(
                name=f"Test {source_type}",
                url="https://test.com",
                source_type=source_type,
                credibility_score=4
            )
            db_session.add(source)
            db_session.commit()
            assert source.source_type == source_type


class TestCategoryModel:
    """Test Category model"""

    def test_create_category(self, db_session):
        """Test creating a category"""
        category = Category(
            name="Labor",
            slug="labor",
            description="Workers' rights and labor issues",
            sort_order=1
        )
        db_session.add(category)
        db_session.commit()

        assert category.id is not None
        assert category.name == "Labor"
        assert category.slug == "labor"
        assert category.is_active is True

    def test_category_slug_unique(self, db_session):
        """Test category slug uniqueness"""
        cat1 = Category(name="Environment", slug="environment")
        db_session.add(cat1)
        db_session.commit()

        # Try to create duplicate slug - should fail
        cat2 = Category(name="Climate", slug="environment")
        db_session.add(cat2)

        with pytest.raises(Exception):
            db_session.commit()


class TestRegionModel:
    """Test Region model"""

    def test_create_region(self, db_session):
        """Test creating a region"""
        region = Region(
            name="California",
            region_type="state",
            state_code="CA",
            population=39_000_000
        )
        db_session.add(region)
        db_session.commit()

        assert region.id is not None
        assert region.name == "California"
        assert region.state_code == "CA"
        assert region.is_active is True


class TestArticleModel:
    """Test Article model"""

    def test_create_article(self, db_session, sample_category):
        """Test creating an article"""
        article = Article(
            title="Amazon Workers Win Union Vote",
            slug="amazon-workers-union-vote",
            body="Full article text here...",
            summary="Summary text",
            category_id=sample_category.id,
            is_national=True,
            reading_level=8.0,
            word_count=150,
            status="draft"
        )
        db_session.add(article)
        db_session.commit()

        assert article.id is not None
        assert article.title == "Amazon Workers Win Union Vote"
        assert article.status == "draft"
        assert article.is_new is True

    def test_article_status_validation(self, db_session, sample_category):
        """Test article status constraint"""
        valid_statuses = ['draft', 'pending_review', 'approved', 'published', 'archived']

        for status in valid_statuses:
            article = Article(
                title=f"Test {status}",
                slug=f"test-{status}",
                body="Test body",
                category_id=sample_category.id,
                status=status
            )
            db_session.add(article)
            db_session.commit()
            assert article.status == status

    def test_article_category_relationship(self, db_session, sample_category):
        """Test article-category relationship"""
        article = Article(
            title="Test Article",
            slug="test-article",
            body="Test body",
            category_id=sample_category.id
        )
        db_session.add(article)
        db_session.commit()

        assert article.category is not None
        assert article.category.name == "Labor"

    def test_article_sources_relationship(self, db_session, sample_category, sample_source):
        """Test article-sources many-to-many relationship"""
        article = Article(
            title="Test Article",
            slug="test-article-sources",
            body="Test body",
            category_id=sample_category.id
        )
        article.sources.append(sample_source)
        db_session.add(article)
        db_session.commit()

        assert len(article.sources) == 1
        assert article.sources[0].name == "Test News Wire"


class TestTopicModel:
    """Test Topic model"""

    def test_create_topic(self, db_session, sample_category):
        """Test creating a topic"""
        topic = Topic(
            title="Amazon Union Vote",
            description="Workers vote to unionize",
            keywords="amazon,union,labor",
            discovered_from="RSS:AP News",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        assert topic.id is not None
        assert topic.status == "discovered"
        assert topic.discovery_date is not None

    def test_topic_status_workflow(self, db_session, sample_category):
        """Test topic status transitions"""
        topic = Topic(
            title="Test Topic",
            description="Test",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        # Update status
        topic.status = "filtered"
        db_session.commit()
        assert topic.status == "filtered"

        # Update to generated
        topic.status = "generated"
        db_session.commit()
        assert topic.status == "generated"

    def test_topic_viability_scores(self, db_session, sample_category):
        """Test topic viability scoring fields"""
        topic = Topic(
            title="Test Topic",
            description="Test",
            category_id=sample_category.id,
            source_count=3,
            academic_citation_count=1,
            worker_relevance_score=0.85,
            engagement_score=7.5
        )
        db_session.add(topic)
        db_session.commit()

        assert topic.source_count == 3
        assert topic.academic_citation_count == 1
        assert topic.worker_relevance_score == 0.85
        assert topic.engagement_score == 7.5
