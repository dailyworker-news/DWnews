"""
End-to-End Tests - API Endpoints
Tests all API endpoints with real HTTP requests.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from sqlalchemy.orm import Session
from backend.main import app
from database.models import Article, Category
from backend.database import get_db


@pytest.fixture
def client(db_session):
    """Create test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test /api/health endpoint."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestArticlesEndpoints:
    """Test article CRUD endpoints."""

    def test_list_articles_empty(self, client):
        """Test GET /api/articles/ with no articles."""
        response = client.get("/api/articles/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_articles_with_data(self, client, db_session, sample_category):
        """Test GET /api/articles/ with published articles."""

        # Create test articles
        article1 = Article(
            title="Test Article 1",
            slug="test-article-1",
            category_id=sample_category.id,
            body="Content 1",
            reading_level=8.0,
            word_count=100,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        article2 = Article(
            title="Test Article 2",
            slug="test-article-2",
            category_id=sample_category.id,
            body="Content 2",
            reading_level=8.0,
            word_count=150,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add_all([article1, article2])
        db_session.commit()

        response = client.get("/api/articles/")

        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 2
        assert articles[0]["title"] == "Test Article 2"  # Ordered by published_at DESC
        assert articles[1]["title"] == "Test Article 1"

    def test_filter_articles_by_status(self, client, db_session, sample_category):
        """Test filtering articles by status."""

        # Create articles with different statuses
        draft = Article(
            title="Draft Article",
            slug="draft-article",
            category_id=sample_category.id,
            body="Draft content",
            reading_level=8.0,
            status="draft",
            created_at=datetime.utcnow()
        )
        published = Article(
            title="Published Article",
            slug="published-article",
            category_id=sample_category.id,
            body="Published content",
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add_all([draft, published])
        db_session.commit()

        # Filter by draft status
        response = client.get("/api/articles/?status=draft")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Draft Article"

        # Filter by published status
        response = client.get("/api/articles/?status=published")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Published Article"

    def test_filter_articles_by_ongoing(self, client, db_session, sample_category):
        """Test filtering articles by ongoing flag."""

        # Create ongoing and regular articles
        ongoing = Article(
            title="Ongoing Story",
            slug="ongoing-story",
            category_id=sample_category.id,
            body="Ongoing content",
            is_ongoing=True,
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        regular = Article(
            title="Regular Article",
            slug="regular-article",
            category_id=sample_category.id,
            body="Regular content",
            is_ongoing=False,
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add_all([ongoing, regular])
        db_session.commit()

        # Filter for ongoing stories
        response = client.get("/api/articles/?ongoing=true")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Ongoing Story"
        assert articles[0]["is_ongoing"] == True

        # Filter for non-ongoing stories
        response = client.get("/api/articles/?ongoing=false")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Regular Article"
        assert articles[0]["is_ongoing"] == False

    def test_pagination(self, client, db_session, sample_category):
        """Test pagination with limit and offset."""

        # Create 15 articles
        for i in range(15):
            article = Article(
                title=f"Article {i}",
                slug=f"article-{i}",
                category_id=sample_category.id,
                body=f"Content {i}",
                reading_level=8.0,
                status="published",
                published_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            db_session.add(article)
        db_session.commit()

        # Get first page (10 items)
        response = client.get("/api/articles/?limit=10&offset=0")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 10

        # Get second page (5 items)
        response = client.get("/api/articles/?limit=10&offset=10")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 5

    def test_get_single_article(self, client, db_session, sample_category):
        """Test GET /api/articles/{id}."""

        # Create article
        article = Article(
            title="Test Article",
            slug="test-article",
            category_id=sample_category.id,
            body="Test content with multiple paragraphs.\n\nThis is the second paragraph.",
            summary="Test summary",
            why_this_matters="This matters because...",
            what_you_can_do="You can help by...",
            reading_level=8.0,
            word_count=200,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Get article by ID
        response = client.get(f"/api/articles/{article.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == article.id
        assert data["title"] == "Test Article"
        assert data["body"] == article.body
        assert data["summary"] == "Test summary"
        assert data["why_this_matters"] == "This matters because..."
        assert data["what_you_can_do"] == "You can help by..."
        assert data["reading_level"] == 8.0
        assert data["word_count"] == 200
        assert data["status"] == "published"

    def test_get_nonexistent_article(self, client):
        """Test GET /api/articles/{id} with nonexistent ID."""
        response = client.get("/api/articles/99999")
        assert response.status_code == 404

    def test_update_article_status(self, client, db_session, sample_category):
        """Test PATCH /api/articles/{id} to update status."""

        # Create draft article
        article = Article(
            title="Draft Article",
            slug="draft-article",
            category_id=sample_category.id,
            body="Draft content",
            reading_level=8.0,
            status="draft",
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Update to published
        response = client.patch(
            f"/api/articles/{article.id}",
            json={"status": "published"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert data["published_at"] is not None

        # Verify in database
        db_session.refresh(article)
        assert article.status == "published"
        assert article.published_at is not None

    def test_update_article_ongoing_flag(self, client, db_session, sample_category):
        """Test PATCH /api/articles/{id} to mark as ongoing."""

        # Create published article
        article = Article(
            title="Regular Article",
            slug="regular-article",
            category_id=sample_category.id,
            body="Regular content",
            is_ongoing=False,
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Mark as ongoing
        response = client.patch(
            f"/api/articles/{article.id}",
            json={"is_ongoing": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_ongoing"] == True

        # Verify in database
        db_session.refresh(article)
        assert article.is_ongoing == True

    def test_archive_article(self, client, db_session, sample_category):
        """Test archiving an article."""

        # Create published article
        article = Article(
            title="Old Article",
            slug="old-article",
            category_id=sample_category.id,
            body="Old content",
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(article)
        db_session.commit()

        # Archive it
        response = client.patch(
            f"/api/articles/{article.id}",
            json={"status": "archived"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"

        # Verify it doesn't appear in published queries
        response = client.get("/api/articles/?status=published")
        articles = response.json()
        assert not any(a["id"] == article.id for a in articles)

        # But appears in archived queries
        response = client.get("/api/articles/?status=archived")
        articles = response.json()
        assert any(a["id"] == article.id for a in articles)

    def test_filter_by_category(self, client, db_session):
        """Test filtering articles by category."""

        # Create categories
        labor = Category(name="Labor", slug="labor")
        tech = Category(name="Tech", slug="tech")
        db_session.add_all([labor, tech])
        db_session.commit()

        # Create articles in different categories
        labor_article = Article(
            title="Labor Article",
            slug="labor-article",
            category_id=labor.id,
            body="Labor content",
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        tech_article = Article(
            title="Tech Article",
            slug="tech-article",
            category_id=tech.id,
            body="Tech content",
            reading_level=8.0,
            status="published",
            published_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add_all([labor_article, tech_article])
        db_session.commit()

        # Filter by labor category
        response = client.get("/api/articles/?category=labor")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Labor Article"

        # Filter by tech category
        response = client.get("/api/articles/?category=tech")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Tech Article"

    def test_combined_filters(self, client, db_session, sample_category):
        """Test combining multiple filters."""

        # Create various articles
        articles_data = [
            {"title": "Published Ongoing", "status": "published", "is_ongoing": True},
            {"title": "Published Regular", "status": "published", "is_ongoing": False},
            {"title": "Draft Ongoing", "status": "draft", "is_ongoing": True},
            {"title": "Draft Regular", "status": "draft", "is_ongoing": False},
        ]

        for data in articles_data:
            article = Article(
                title=data["title"],
                slug=data["title"].lower().replace(" ", "-"),
                category_id=sample_category.id,
                body="Content",
                is_ongoing=data["is_ongoing"],
                reading_level=8.0,
                status=data["status"],
                published_at=datetime.utcnow() if data["status"] == "published" else None,
                created_at=datetime.utcnow()
            )
            db_session.add(article)
        db_session.commit()

        # Filter: published + ongoing
        response = client.get("/api/articles/?status=published&ongoing=true")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Published Ongoing"

        # Filter: published + not ongoing
        response = client.get("/api/articles/?status=published&ongoing=false")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 1
        assert articles[0]["title"] == "Published Regular"
