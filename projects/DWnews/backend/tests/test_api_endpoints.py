"""
Comprehensive Unit Tests for The Daily Worker Backend API

Tests all endpoints with database setup and teardown.
Run with: pytest backend/tests/test_api_endpoints.py -v
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.main import app
from backend.database import get_db
from database.models import (
    Base, Article, Category, Region, Source, ArticleRevision,
    Correction, EventCandidate, Topic
)


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_dwnews.db"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test.
    Sets up tables, yields the session, then tears down.
    """
    # Create test engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        # Remove test database file
        if os.path.exists("test_dwnews.db"):
            os.remove("test_dwnews.db")


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a test client with dependency override for database.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_data(test_db):
    """
    Create sample data for testing.
    Returns dict with created objects.
    """
    # Create categories
    labor_category = Category(
        name="Labor & Unions",
        slug="labor-unions",
        description="Coverage of labor organizing and workers' rights",
        sort_order=1,
        is_active=True
    )
    politics_category = Category(
        name="Politics",
        slug="politics",
        description="Political coverage from a working-class perspective",
        sort_order=2,
        is_active=True
    )
    test_db.add(labor_category)
    test_db.add(politics_category)
    test_db.commit()

    # Create regions
    national_region = Region(
        name="National",
        region_type="national",
        is_active=True
    )
    midwest_region = Region(
        name="Midwest",
        region_type="metro",
        state_code="IL",
        population=9000000,
        is_active=True
    )
    test_db.add(national_region)
    test_db.add(midwest_region)
    test_db.commit()

    # Create sources
    ap_source = Source(
        name="Associated Press",
        url="https://apnews.com",
        rss_feed="https://apnews.com/rss",
        credibility_score=5,
        source_type="news_wire",
        political_lean="center",
        is_active=True
    )
    propublica_source = Source(
        name="ProPublica",
        url="https://www.propublica.org",
        rss_feed="https://www.propublica.org/feeds/propublica/main",
        credibility_score=5,
        source_type="investigative",
        political_lean="center-left",
        is_active=True
    )
    test_db.add(ap_source)
    test_db.add(propublica_source)
    test_db.commit()

    # Create articles
    published_article = Article(
        title="Workers Win Major Victory in Amazon Union Drive",
        slug="workers-win-amazon-union",
        body="In a historic victory, Amazon warehouse workers in Staten Island voted to form the company's first union...",
        summary="Amazon workers in Staten Island successfully unionize in historic vote.",
        category_id=labor_category.id,
        author="The Daily Worker Editorial Team",
        is_national=True,
        is_local=False,
        region_id=national_region.id,
        is_ongoing=True,
        is_new=False,
        reading_level=8.2,
        word_count=1200,
        image_url="https://example.com/amazon-union.jpg",
        image_attribution="Photo by Worker Solidarity News",
        why_this_matters="This represents a major breakthrough in organizing tech sector workers.",
        what_you_can_do="Support union organizing efforts in your workplace.",
        status="published",
        published_at=datetime.utcnow() - timedelta(days=1),
        created_at=datetime.utcnow() - timedelta(days=2),
        self_audit_passed=True,
        bias_scan_report=json.dumps({
            "bias_score": 0.2,
            "flags": [],
            "self_audit": [
                {"criterion": "Sources verified", "passed": True, "notes": "3 credible sources"},
                {"criterion": "Reading level appropriate", "passed": True, "notes": "8.2 grade level"}
            ]
        })
    )

    draft_article = Article(
        title="New Study Shows Wage Theft Costs Workers Billions",
        slug="wage-theft-study-billions",
        body="A comprehensive new study reveals that wage theft costs American workers over $15 billion annually...",
        summary="New research quantifies massive scale of wage theft in America.",
        category_id=labor_category.id,
        author="The Daily Worker Editorial Team",
        is_national=True,
        is_local=False,
        region_id=national_region.id,
        is_ongoing=False,
        is_new=True,
        reading_level=7.8,
        word_count=950,
        status="draft",
        created_at=datetime.utcnow() - timedelta(hours=6),
        self_audit_passed=True,
        assigned_editor="editor@example.com",
        review_deadline=datetime.utcnow() + timedelta(hours=18)
    )

    under_review_article = Article(
        title="Healthcare Workers Demand Better Protections",
        slug="healthcare-workers-protections",
        body="Healthcare workers across the nation are demanding improved safety protections...",
        summary="Healthcare workers organize for better workplace safety.",
        category_id=labor_category.id,
        author="The Daily Worker Editorial Team",
        is_national=False,
        is_local=True,
        region_id=midwest_region.id,
        is_ongoing=True,
        is_new=True,
        reading_level=8.0,
        word_count=850,
        status="under_review",
        created_at=datetime.utcnow() - timedelta(hours=12),
        self_audit_passed=True,
        assigned_editor="editor@example.com",
        review_deadline=datetime.utcnow() + timedelta(hours=12)
    )

    test_db.add(published_article)
    test_db.add(draft_article)
    test_db.add(under_review_article)
    test_db.commit()

    # Add sources to published article
    published_article.sources.append(ap_source)
    published_article.sources.append(propublica_source)
    test_db.commit()

    # Create a revision for the draft article
    revision = ArticleRevision(
        article_id=draft_article.id,
        revision_number=1,
        revised_by="journalist-agent",
        revision_type="ai_edit",
        title_before="Old Title",
        title_after=draft_article.title,
        change_summary="Initial draft creation",
        change_reason="New article generation",
        sources_verified=True,
        bias_check_passed=True,
        reading_level_after=7.8
    )
    test_db.add(revision)
    test_db.commit()

    return {
        "categories": {
            "labor": labor_category,
            "politics": politics_category
        },
        "regions": {
            "national": national_region,
            "midwest": midwest_region
        },
        "sources": {
            "ap": ap_source,
            "propublica": propublica_source
        },
        "articles": {
            "published": published_article,
            "draft": draft_article,
            "under_review": under_review_article
        },
        "revisions": {
            "draft_revision": revision
        }
    }


# ============================================================================
# ROOT AND HEALTH ENDPOINTS
# ============================================================================

class TestRootAndHealth:
    """Tests for root and health check endpoints"""

    def test_root_endpoint(self, client):
        """Test GET / returns basic API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "The Daily Worker API"
        assert data["version"] == "1.0.0"

    def test_health_check(self, client):
        """Test GET /api/health returns health status"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "environment" in data
        assert "database" in data
        assert "llm_apis" in data


# ============================================================================
# ARTICLES ENDPOINTS
# ============================================================================

class TestArticlesEndpoints:
    """Tests for /api/articles endpoints"""

    def test_get_all_articles(self, client, sample_data):
        """Test GET /api/articles/ returns all articles"""
        response = client.get("/api/articles/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in article for article in data)
        assert all("title" in article for article in data)

    def test_get_articles_by_status(self, client, sample_data):
        """Test GET /api/articles/?status=published filters by status"""
        response = client.get("/api/articles/?status=published")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "published"
        assert data[0]["title"] == "Workers Win Major Victory in Amazon Union Drive"

    def test_get_articles_by_category(self, client, sample_data):
        """Test GET /api/articles/?category=labor-unions filters by category"""
        response = client.get("/api/articles/?category=labor-unions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(article["category_name"] == "Labor & Unions" for article in data)

    def test_get_articles_by_region_national(self, client, sample_data):
        """Test GET /api/articles/?region=national filters national articles"""
        response = client.get("/api/articles/?region=national")
        assert response.status_code == 200
        data = response.json()
        assert all(article["is_national"] for article in data)

    def test_get_articles_by_region_local(self, client, sample_data):
        """Test GET /api/articles/?region=local filters local articles"""
        response = client.get("/api/articles/?region=local")
        assert response.status_code == 200
        data = response.json()
        assert all(article["is_local"] for article in data)

    def test_get_articles_ongoing(self, client, sample_data):
        """Test GET /api/articles/?ongoing=true filters ongoing stories"""
        response = client.get("/api/articles/?ongoing=true")
        assert response.status_code == 200
        data = response.json()
        assert all(article["is_ongoing"] for article in data)

    def test_get_articles_pagination(self, client, sample_data):
        """Test GET /api/articles/?limit=1&offset=1 paginates correctly"""
        response = client.get("/api/articles/?limit=1&offset=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_article_by_id(self, client, sample_data):
        """Test GET /api/articles/{id} returns full article"""
        article_id = sample_data["articles"]["published"].id
        response = client.get(f"/api/articles/{article_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == "Workers Win Major Victory in Amazon Union Drive"
        assert data["body"] is not None
        assert data["category_name"] == "Labor & Unions"
        assert data["why_this_matters"] is not None
        assert data["what_you_can_do"] is not None

    def test_get_article_by_id_not_found(self, client):
        """Test GET /api/articles/99999 returns 404"""
        response = client.get("/api/articles/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_article_by_slug(self, client, sample_data):
        """Test GET /api/articles/slug/{slug} returns article"""
        response = client.get("/api/articles/slug/workers-win-amazon-union")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "workers-win-amazon-union"
        assert data["title"] == "Workers Win Major Victory in Amazon Union Drive"

    def test_get_article_by_slug_not_found(self, client):
        """Test GET /api/articles/slug/nonexistent returns 404"""
        response = client.get("/api/articles/slug/nonexistent-slug")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_article_status(self, client, sample_data):
        """Test PATCH /api/articles/{id} updates status"""
        article_id = sample_data["articles"]["draft"].id
        response = client.patch(
            f"/api/articles/{article_id}",
            json={"status": "approved"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Article updated successfully"

        # Verify update
        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.json()["status"] == "approved"

    def test_update_article_publish(self, client, sample_data):
        """Test PATCH /api/articles/{id} with status=published sets published_at"""
        article_id = sample_data["articles"]["draft"].id
        response = client.patch(
            f"/api/articles/{article_id}",
            json={"status": "published"}
        )
        assert response.status_code == 200

        # Verify published_at is set
        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.json()["status"] == "published"
        assert get_response.json()["published_at"] is not None

    def test_update_article_title(self, client, sample_data):
        """Test PATCH /api/articles/{id} updates title"""
        article_id = sample_data["articles"]["draft"].id
        new_title = "Updated Article Title"
        response = client.patch(
            f"/api/articles/{article_id}",
            json={"title": new_title}
        )
        assert response.status_code == 200

        # Verify update
        get_response = client.get(f"/api/articles/{article_id}")
        assert get_response.json()["title"] == new_title

    def test_update_article_invalid_status(self, client, sample_data):
        """Test PATCH /api/articles/{id} with invalid status returns 400"""
        article_id = sample_data["articles"]["draft"].id
        response = client.patch(
            f"/api/articles/{article_id}",
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400
        assert "invalid status" in response.json()["detail"].lower()

    def test_update_article_not_found(self, client):
        """Test PATCH /api/articles/99999 returns 404"""
        response = client.patch(
            "/api/articles/99999",
            json={"status": "approved"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# EDITORIAL ENDPOINTS
# ============================================================================

class TestEditorialEndpoints:
    """Tests for /api/editorial endpoints"""

    def test_get_pending_articles_draft(self, client, sample_data):
        """Test GET /api/editorial/pending?status=draft returns draft articles"""
        response = client.get("/api/editorial/pending?status=draft")
        assert response.status_code == 200
        data = response.json()
        # Should return 1 draft article (that passed self-audit)
        assert len(data) == 1
        assert data[0]["status"] == "draft"
        assert data[0]["self_audit_passed"] is True

    def test_get_pending_articles_under_review(self, client, sample_data):
        """Test GET /api/editorial/pending?status=under_review"""
        response = client.get("/api/editorial/pending?status=under_review")
        assert response.status_code == 200
        data = response.json()
        assert all(article["status"] == "under_review" for article in data)

    def test_get_pending_articles_all(self, client, sample_data):
        """Test GET /api/editorial/pending?status=all_pending returns all pending"""
        response = client.get("/api/editorial/pending?status=all_pending")
        assert response.status_code == 200
        data = response.json()
        # Should return draft + under_review articles
        assert len(data) >= 2
        assert all(article["status"] in ["draft", "under_review", "revision_requested"] for article in data)

    def test_get_article_for_review(self, client, sample_data):
        """Test GET /api/editorial/review/{id} returns full review data"""
        article_id = sample_data["articles"]["draft"].id
        response = client.get(f"/api/editorial/review/{article_id}")
        assert response.status_code == 200
        data = response.json()

        # Verify basic fields
        assert data["id"] == article_id
        assert data["title"] is not None
        assert data["body"] is not None

        # Verify editorial fields
        assert "assigned_editor" in data
        assert "review_deadline" in data
        assert "self_audit_passed" in data

        # Verify quality check fields
        assert "bias_scan_report" in data
        assert "self_audit_details" in data

        # Verify sources
        assert "sources" in data
        assert isinstance(data["sources"], list)

        # Verify revision info
        assert data["revision_count"] == 1
        assert data["latest_revision_notes"] is not None

    def test_get_article_for_review_not_found(self, client):
        """Test GET /api/editorial/review/99999 returns 404"""
        response = client.get("/api/editorial/review/99999")
        assert response.status_code == 404

    def test_get_article_for_review_with_sources(self, client, sample_data):
        """Test review endpoint includes source information"""
        article_id = sample_data["articles"]["published"].id
        response = client.get(f"/api/editorial/review/{article_id}")
        assert response.status_code == 200
        data = response.json()

        # Should have sources
        assert len(data["sources"]) == 2
        source_names = [s["name"] for s in data["sources"]]
        assert "Associated Press" in source_names
        assert "ProPublica" in source_names

    def test_approve_article(self, client, sample_data, test_db):
        """Test POST /api/editorial/{id}/approve approves article"""
        article_id = sample_data["articles"]["draft"].id
        response = client.post(
            f"/api/editorial/{article_id}/approve",
            json={"approved_by": "editor@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "approved" in data["message"].lower()

        # Verify article status changed
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert article.status == "approved"

    def test_request_revision(self, client, sample_data, test_db):
        """Test POST /api/editorial/{id}/request-revision requests revision"""
        article_id = sample_data["articles"]["draft"].id
        response = client.post(
            f"/api/editorial/{article_id}/request-revision",
            json={
                "editorial_notes": "Please add more sources and clarify the timeline.",
                "requested_by": "senior-editor@example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "revision requested" in data["message"].lower()

        # Verify article status and notes
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert article.status == "revision_requested"
        assert "more sources" in article.editorial_notes
        assert article.assigned_editor == "senior-editor@example.com"

    def test_reject_article(self, client, sample_data, test_db):
        """Test POST /api/editorial/{id}/reject rejects article"""
        article_id = sample_data["articles"]["draft"].id
        response = client.post(
            f"/api/editorial/{article_id}/reject",
            json={
                "rejected_by": "editor@example.com",
                "reason": "Does not meet editorial standards"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rejected" in data["message"].lower()

        # Verify article status
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert article.status == "archived"

    def test_get_overdue_articles(self, client, sample_data, test_db):
        """Test GET /api/editorial/overdue returns overdue articles"""
        # Create an overdue article
        overdue_article = Article(
            title="Overdue Test Article",
            slug="overdue-test",
            body="Test content",
            category_id=sample_data["categories"]["labor"].id,
            status="under_review",
            self_audit_passed=True,
            assigned_editor="lazy-editor@example.com",
            review_deadline=datetime.utcnow() - timedelta(hours=24),  # 24 hours overdue
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        test_db.add(overdue_article)
        test_db.commit()

        response = client.get("/api/editorial/overdue")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1
        assert any(article["id"] == overdue_article.id for article in data["articles"])

        # Verify overdue calculation
        overdue_item = next(a for a in data["articles"] if a["id"] == overdue_article.id)
        assert overdue_item["hours_overdue"] > 20  # Should be ~24 hours

    def test_get_editor_workload(self, client, sample_data):
        """Test GET /api/editorial/workload/{email} returns editor's workload"""
        response = client.get("/api/editorial/workload/editor@example.com")
        assert response.status_code == 200
        data = response.json()

        assert data["editor"] == "editor@example.com"
        assert "workload" in data
        assert "articles" in data
        assert isinstance(data["articles"], list)

        # Should have at least 1 article assigned to this editor (under_review status)
        # Draft articles are not counted in workload (only under_review and revision_requested)
        assert len(data["articles"]) >= 1

    def test_auto_assign_articles(self, client, sample_data, test_db):
        """Test POST /api/editorial/auto-assign assigns pending articles"""
        # Create an unassigned draft article
        unassigned_article = Article(
            title="Unassigned Article",
            slug="unassigned-test",
            body="Test content",
            category_id=sample_data["categories"]["labor"].id,
            status="draft",
            self_audit_passed=True,
            assigned_editor=None,
            created_at=datetime.utcnow()
        )
        test_db.add(unassigned_article)
        test_db.commit()

        response = client.post("/api/editorial/auto-assign")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 0  # May be 0 if no editors configured in test

    def test_send_overdue_alerts(self, client, sample_data):
        """Test POST /api/editorial/send-overdue-alerts sends alerts"""
        response = client.post("/api/editorial/send-overdue-alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "count" in data


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_article_approval_workflow(self, client, sample_data, test_db):
        """Test complete article approval workflow"""
        article_id = sample_data["articles"]["draft"].id

        # 1. Get pending articles - should include our draft
        response = client.get("/api/editorial/pending?status=draft")
        assert response.status_code == 200
        assert any(a["id"] == article_id for a in response.json())

        # 2. Get full review data
        response = client.get(f"/api/editorial/review/{article_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "draft"

        # 3. Approve the article
        response = client.post(
            f"/api/editorial/{article_id}/approve",
            json={"approved_by": "editor@example.com"}
        )
        assert response.status_code == 200

        # 4. Verify no longer in pending
        response = client.get("/api/editorial/pending?status=draft")
        assert not any(a["id"] == article_id for a in response.json())

        # 5. Publish the article
        response = client.patch(
            f"/api/articles/{article_id}",
            json={"status": "published"}
        )
        assert response.status_code == 200

        # 6. Verify published article appears in listings
        response = client.get("/api/articles/?status=published")
        assert any(a["id"] == article_id for a in response.json())

    def test_article_revision_workflow(self, client, sample_data, test_db):
        """Test article revision request workflow"""
        article_id = sample_data["articles"]["under_review"].id

        # 1. Request revision
        response = client.post(
            f"/api/editorial/{article_id}/request-revision",
            json={
                "editorial_notes": "Please expand the local impact section.",
                "requested_by": "editor@example.com"
            }
        )
        assert response.status_code == 200

        # 2. Verify status changed to revision_requested
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert article.status == "revision_requested"
        assert "local impact" in article.editorial_notes

        # 3. Simulate journalist agent making revisions
        # Update content while keeping revision_requested status
        response = client.patch(
            f"/api/articles/{article_id}",
            json={
                "body": "Updated body with expanded local impact section...",
            }
        )
        assert response.status_code == 200

        # 4. Verify content was updated
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert "expanded local impact" in article.body

        # 5. Editor reviews and approves the revision
        # The approve function will handle status transitions from revision_requested
        response = client.post(
            f"/api/editorial/{article_id}/approve",
            json={"approved_by": "editor@example.com"}
        )
        assert response.status_code == 200

        # 6. Verify article is now approved
        article = test_db.query(Article).filter(Article.id == article_id).first()
        assert article.status == "approved"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Tests for error handling and edge cases"""

    def test_invalid_article_id_type(self, client):
        """Test that invalid ID types are handled"""
        response = client.get("/api/articles/invalid-id")
        # FastAPI will return 422 for invalid type
        assert response.status_code == 422

    def test_empty_database_queries(self, client, test_db):
        """Test queries on empty database return empty results"""
        response = client.get("/api/articles/")
        assert response.status_code == 200
        assert response.json() == []

    def test_malformed_json_request(self, client, sample_data):
        """Test malformed JSON in request body"""
        article_id = sample_data["articles"]["draft"].id
        # Send invalid JSON
        response = client.patch(
            f"/api/articles/{article_id}",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, client, sample_data):
        """Test requests with missing required fields"""
        article_id = sample_data["articles"]["draft"].id
        # Approve without required 'approved_by' field
        response = client.post(
            f"/api/editorial/{article_id}/approve",
            json={}
        )
        assert response.status_code == 422


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Basic performance and load tests"""

    def test_large_result_set_pagination(self, client, test_db, sample_data):
        """Test pagination works with larger datasets"""
        # Create 50 test articles
        category_id = sample_data["categories"]["labor"].id
        for i in range(50):
            article = Article(
                title=f"Test Article {i}",
                slug=f"test-article-{i}",
                body="Test content",
                category_id=category_id,
                status="published",
                published_at=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            test_db.add(article)
        test_db.commit()

        # Test pagination
        response = client.get("/api/articles/?limit=10&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 10

        response = client.get("/api/articles/?limit=10&offset=10")
        assert response.status_code == 200
        assert len(response.json()) == 10

    def test_complex_filter_combinations(self, client, sample_data):
        """Test multiple filters work together"""
        response = client.get(
            "/api/articles/?status=published&category=labor-unions&region=national&ongoing=true"
        )
        assert response.status_code == 200
        data = response.json()
        # Verify all filters applied
        for article in data:
            assert article["status"] == "published"
            assert article["category_name"] == "Labor & Unions"
            assert article["is_national"] is True
            assert article["is_ongoing"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
