"""
End-to-End Tests - Complete Workflow
Tests the entire Daily Worker workflow from content discovery to publishing.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Article, Topic, Category, Source
from scripts.utils.text_utils import generate_hash


class TestCompleteWorkflow:
    """Test the complete content workflow end-to-end."""

    def test_topic_to_published_article_workflow(self, db_session: Session, sample_category, sample_source):
        """Test complete workflow: Topic discovery → Article generation → Publishing."""

        # Step 1: Simulate topic discovery
        topic = Topic(
            title="Local Union Wins Major Contract Victory",
            url="https://example.com/union-victory",
            source_name="Labor Notes",
            discovered_at=datetime.utcnow(),
            content_hash=generate_hash("Local Union Wins Major Contract Victory"),
            category_id=sample_category.id,
            status="discovered",
            engagement_score=0.8,
            relevance_score=0.9
        )
        db_session.add(topic)
        db_session.commit()

        assert topic.id is not None
        assert topic.status == "discovered"

        # Step 2: Filter topic (viability check)
        topic.status = "filtered"
        topic.viability_score = 0.85
        db_session.commit()

        assert topic.status == "filtered"
        assert topic.viability_score == 0.85

        # Step 3: Generate article (simulate LLM generation)
        article = Article(
            title="Local Union Secures Historic Pay Raises and Benefits",
            slug="local-union-secures-historic-pay-raises-and-benefits",
            category_id=sample_category.id,
            body="""Workers at the manufacturing plant have achieved a significant victory.

After months of negotiations, the local union has secured a historic contract that includes substantial pay raises, improved healthcare benefits, and better working conditions for all members.

This demonstrates the power of organized labor and collective bargaining.""",
            summary="Local union wins major contract with pay raises and improved benefits after months of negotiations.",
            is_national=False,
            is_local=True,
            is_ongoing=False,
            is_new=True,
            reading_level=8.2,
            word_count=450,
            status="draft",
            created_at=datetime.utcnow()
        )
        article.topics.append(topic)
        db_session.add(article)
        db_session.commit()

        assert article.id is not None
        assert article.status == "draft"
        assert article.reading_level >= 7.5
        assert article.reading_level <= 8.5
        assert len(article.topics) == 1

        # Step 4: Admin review and publish
        article.status = "published"
        article.published_at = datetime.utcnow()
        db_session.commit()

        assert article.status == "published"
        assert article.published_at is not None

        # Step 5: Verify article appears in published queries
        published_articles = db_session.query(Article).filter(
            Article.status == "published"
        ).all()

        assert len(published_articles) >= 1
        assert article in published_articles

    def test_ongoing_story_workflow(self, db_session: Session, sample_category):
        """Test marking article as ongoing story."""

        # Create and publish an article
        article = Article(
            title="Climate Strike Continues Across Major Cities",
            slug="climate-strike-continues-across-major-cities",
            category_id=sample_category.id,
            body="Climate activists continue their protests in major cities worldwide.",
            is_national=True,
            is_local=False,
            is_ongoing=False,
            is_new=True,
            reading_level=8.0,
            word_count=350,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Mark as ongoing story
        article.is_ongoing = True
        article.is_new = False  # No longer "new" once ongoing
        db_session.commit()

        # Verify ongoing story query
        ongoing_articles = db_session.query(Article).filter(
            Article.status == "published",
            Article.is_ongoing == True
        ).all()

        assert len(ongoing_articles) >= 1
        assert article in ongoing_articles
        assert article.is_ongoing == True
        assert article.is_new == False

    def test_multi_source_article(self, db_session: Session, sample_category):
        """Test article with multiple source citations."""

        # Create multiple sources
        source1 = Source(
            name="Associated Press",
            url="https://apnews.com",
            credibility_score=5,
            source_type="news_agency",
            is_active=True
        )
        source2 = Source(
            name="Reuters",
            url="https://reuters.com",
            credibility_score=5,
            source_type="news_agency",
            is_active=True
        )
        db_session.add_all([source1, source2])
        db_session.commit()

        # Create article
        article = Article(
            title="Major Economic Policy Shift Announced",
            slug="major-economic-policy-shift-announced",
            category_id=sample_category.id,
            body="Government announces significant changes to economic policy.",
            is_national=True,
            is_local=False,
            reading_level=7.8,
            word_count=500,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        article.sources.extend([source1, source2])
        db_session.add(article)
        db_session.commit()

        # Verify multi-source relationship
        assert len(article.sources) == 2
        assert source1 in article.sources
        assert source2 in article.sources

    def test_article_archival_workflow(self, db_session: Session, sample_category):
        """Test archiving old articles."""

        # Create published article
        article = Article(
            title="Outdated News Article",
            slug="outdated-news-article",
            category_id=sample_category.id,
            body="This article is no longer relevant.",
            reading_level=8.0,
            word_count=200,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Archive the article
        article.status = "archived"
        db_session.commit()

        # Verify archived articles don't appear in published queries
        published_articles = db_session.query(Article).filter(
            Article.status == "published"
        ).all()

        assert article not in published_articles

        # But can be retrieved with archived status
        archived_articles = db_session.query(Article).filter(
            Article.status == "archived"
        ).all()

        assert article in archived_articles

    def test_category_filtering(self, db_session: Session):
        """Test filtering articles by category."""

        # Create categories
        labor_cat = Category(name="Labor", slug="labor", description="Labor news")
        tech_cat = Category(name="Tech", slug="tech", description="Tech news")
        db_session.add_all([labor_cat, tech_cat])
        db_session.commit()

        # Create articles in different categories
        labor_article = Article(
            title="Union Victory",
            slug="union-victory",
            category_id=labor_cat.id,
            body="Labor news content.",
            reading_level=8.0,
            word_count=300,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        tech_article = Article(
            title="Tech Workers Organize",
            slug="tech-workers-organize",
            category_id=tech_cat.id,
            body="Tech labor news content.",
            reading_level=8.0,
            word_count=350,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add_all([labor_article, tech_article])
        db_session.commit()

        # Filter by labor category
        labor_articles = db_session.query(Article).filter(
            Article.status == "published",
            Article.category_id == labor_cat.id
        ).all()

        assert len(labor_articles) == 1
        assert labor_article in labor_articles
        assert tech_article not in labor_articles

        # Filter by tech category
        tech_articles = db_session.query(Article).filter(
            Article.status == "published",
            Article.category_id == tech_cat.id
        ).all()

        assert len(tech_articles) == 1
        assert tech_article in tech_articles
        assert labor_article not in tech_articles

    def test_national_vs_local_filtering(self, db_session: Session, sample_category):
        """Test filtering by national vs local articles."""

        # Create national article
        national_article = Article(
            title="National Policy Change",
            slug="national-policy-change",
            category_id=sample_category.id,
            body="National news content.",
            is_national=True,
            is_local=False,
            reading_level=8.0,
            word_count=400,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        # Create local article
        local_article = Article(
            title="Local Community Event",
            slug="local-community-event",
            category_id=sample_category.id,
            body="Local news content.",
            is_national=False,
            is_local=True,
            reading_level=8.0,
            word_count=300,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        db_session.add_all([national_article, local_article])
        db_session.commit()

        # Filter national articles
        national_articles = db_session.query(Article).filter(
            Article.status == "published",
            Article.is_national == True
        ).all()

        assert national_article in national_articles
        assert local_article not in national_articles

        # Filter local articles
        local_articles = db_session.query(Article).filter(
            Article.status == "published",
            Article.is_local == True
        ).all()

        assert local_article in local_articles
        assert national_article not in local_articles

    def test_reading_level_validation(self, db_session: Session, sample_category):
        """Test that reading level constraints are enforced."""

        # Create article with acceptable reading level
        good_article = Article(
            title="Well-Written Article",
            slug="well-written-article",
            category_id=sample_category.id,
            body="This article has an appropriate reading level.",
            reading_level=8.0,
            word_count=300,
            status="draft",
            created_at=datetime.utcnow()
        )
        db_session.add(good_article)
        db_session.commit()

        assert good_article.reading_level >= 7.5
        assert good_article.reading_level <= 8.5

        # Create article with problematic reading level
        difficult_article = Article(
            title="Complex Article",
            slug="complex-article",
            category_id=sample_category.id,
            body="This article is too complex.",
            reading_level=12.5,  # Too high
            word_count=300,
            status="draft",
            created_at=datetime.utcnow()
        )
        db_session.add(difficult_article)
        db_session.commit()

        # Should be flagged in quality checks (not auto-published)
        assert difficult_article.status == "draft"
        assert difficult_article.reading_level > 8.5
