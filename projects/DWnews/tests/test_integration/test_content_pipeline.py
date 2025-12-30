"""
Integration tests for content pipeline
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Topic, Article, Category
from scripts.content.filter_topics import TopicFilter


class TestContentPipelineIntegration:
    """Integration tests for full content pipeline"""

    def test_topic_to_article_workflow(self, db_session, sample_category):
        """Test complete workflow from topic discovery to article generation"""

        # Step 1: Create discovered topic
        topic = Topic(
            title="Amazon Workers Strike for Better Conditions",
            description="Workers demand improved working conditions and better pay",
            keywords="amazon,workers,strike,labor,wages",
            discovered_from="RSS:AP News",
            category_id=sample_category.id,
            status="discovered"
        )
        db_session.add(topic)
        db_session.commit()

        assert topic.status == "discovered"

        # Step 2: Filter topic
        filter_service = TopicFilter(db_session)
        passed = filter_service.filter_topic(topic)

        if passed:
            assert topic.status == "filtered"
            assert topic.worker_relevance_score > 0

            # Step 3: Simulate article generation
            article = Article(
                title=topic.title,
                slug="amazon-workers-strike",
                body="Article content generated from topic...",
                category_id=topic.category_id,
                reading_level=8.0,
                word_count=250,
                status="draft"
            )
            db_session.add(article)

            # Link topic to article
            topic.article_id = article.id
            topic.status = "generated"
            db_session.commit()

            # Verify workflow completion
            assert article.status == "draft"
            assert topic.status == "generated"
            assert topic.article_id == article.id

    def test_category_article_distribution(self, db_session):
        """Test that articles are distributed across categories"""

        # Create multiple categories
        categories = []
        for name in ["Labor", "Tech", "Politics"]:
            cat = Category(
                name=name,
                slug=name.lower(),
                is_active=True
            )
            db_session.add(cat)
            categories.append(cat)
        db_session.commit()

        # Create articles in each category
        for i, category in enumerate(categories):
            article = Article(
                title=f"Test Article {i}",
                slug=f"test-article-{i}",
                body="Test content",
                category_id=category.id,
                status="published"
            )
            db_session.add(article)
        db_session.commit()

        # Verify distribution
        for category in categories:
            count = db_session.query(Article).filter_by(
                category_id=category.id
            ).count()
            assert count > 0

    def test_national_local_filtering(self, db_session, sample_category, sample_region):
        """Test national vs local article filtering"""

        # Create national article
        national = Article(
            title="National News",
            slug="national-news",
            body="National content",
            category_id=sample_category.id,
            is_national=True,
            is_local=False,
            status="published"
        )
        db_session.add(national)

        # Create local article
        local = Article(
            title="Local News",
            slug="local-news",
            body="Local content",
            category_id=sample_category.id,
            is_national=False,
            is_local=True,
            region_id=sample_region.id,
            status="published"
        )
        db_session.add(local)
        db_session.commit()

        # Query national articles
        national_articles = db_session.query(Article).filter_by(
            is_national=True,
            status="published"
        ).all()
        assert len(national_articles) > 0
        assert national_articles[0].is_national is True

        # Query local articles
        local_articles = db_session.query(Article).filter_by(
            is_local=True,
            status="published"
        ).all()
        assert len(local_articles) > 0
        assert local_articles[0].is_local is True

    def test_ongoing_story_tracking(self, db_session, sample_category):
        """Test ongoing story flagging"""

        # Create ongoing story
        ongoing = Article(
            title="Union Negotiations Continue",
            slug="union-negotiations",
            body="Ongoing story content",
            category_id=sample_category.id,
            is_ongoing=True,
            status="published"
        )
        db_session.add(ongoing)
        db_session.commit()

        # Query ongoing stories
        ongoing_stories = db_session.query(Article).filter_by(
            is_ongoing=True
        ).all()

        assert len(ongoing_stories) > 0
        assert ongoing_stories[0].is_ongoing is True

    def test_article_status_workflow(self, db_session, sample_category):
        """Test article status progression"""

        article = Article(
            title="Test Workflow",
            slug="test-workflow",
            body="Content",
            category_id=sample_category.id,
            status="draft"
        )
        db_session.add(article)
        db_session.commit()

        # Draft -> Pending Review
        assert article.status == "draft"

        article.status = "pending_review"
        db_session.commit()
        assert article.status == "pending_review"

        # Pending Review -> Approved
        article.status = "approved"
        db_session.commit()
        assert article.status == "approved"

        # Approved -> Published
        article.status = "published"
        db_session.commit()
        assert article.status == "published"
