"""
The Daily Worker - Sports Preferences Implementation Tests
Phase 7.7: Sports Subscription Configuration
Full integration tests for sports features
"""

import pytest
import json
import os
import sqlite3
from datetime import datetime
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings

# Test database path
TEST_DB = "database/test_sports_impl.db"


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    """Set up test database with schema and seed data"""
    # Remove old test database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'subscriber',
            subscription_status TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE subscription_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_name TEXT NOT NULL UNIQUE,
            price_cents INTEGER NOT NULL,
            billing_interval TEXT NOT NULL,
            features_json TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE sports_leagues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            country TEXT,
            tier_requirement TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE user_sports_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            league_id INTEGER NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, league_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (league_id) REFERENCES sports_leagues(id)
        )
    """)

    # Insert test subscription plans
    cursor.execute("""
        INSERT INTO subscription_plans (id, plan_name, price_cents, billing_interval, features_json)
        VALUES
            (1, 'Free Tier', 0, 'monthly', '{"article_limit": 3, "sports_access": "none"}'),
            (2, 'Basic Subscriber', 1500, 'monthly', '{"article_limit": -1, "sports_access": "one_league"}'),
            (3, 'Premium Subscriber', 2500, 'monthly', '{"article_limit": -1, "sports_access": "unlimited"}')
    """)

    # Insert test leagues
    cursor.execute("""
        INSERT INTO sports_leagues (id, league_code, name, country, tier_requirement)
        VALUES
            (1, 'EPL', 'English Premier League', 'England', 'basic'),
            (2, 'NBA', 'National Basketball Association', 'USA', 'basic'),
            (3, 'NFL', 'National Football League', 'USA', 'basic'),
            (4, 'LA_LIGA', 'La Liga', 'Spain', 'premium'),
            (5, 'BUNDESLIGA', 'Bundesliga', 'Germany', 'premium')
    """)

    # Insert test users
    cursor.execute("""
        INSERT INTO users (id, email, password_hash, role, subscription_status)
        VALUES
            (1, 'free@test.com', 'hash', 'subscriber', 'free'),
            (2, 'basic@test.com', 'hash', 'subscriber', 'active'),
            (3, 'premium@test.com', 'hash', 'subscriber', 'active'),
            (4, 'admin@test.com', 'hash', 'admin', 'active')
    """)

    # Create subscriptions for active users
    cursor.execute("""
        INSERT INTO subscriptions (user_id, plan_id, status)
        VALUES
            (2, 2, 'active'),
            (3, 3, 'active'),
            (4, 3, 'active')
    """)

    conn.commit()
    conn.close()

    # Override database URL for testing
    original_db_url = settings.database_url
    settings.database_url = f"sqlite:///{TEST_DB}"

    yield

    # Cleanup
    settings.database_url = original_db_url
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def create_mock_user(user_id, email, role):
    """Create mock user dict"""
    return {"id": user_id, "email": email, "role": role}


@pytest.fixture
def client():
    """Test client with authentication override"""
    from backend.auth import require_user

    # Store original dependency
    original_require_user = None

    def override_require_user_factory(user_data):
        """Factory to create auth override for specific user"""
        async def override():
            return user_data
        return override

    test_client = TestClient(app)

    # Add method to switch users
    def set_auth_user(user_id, email, role):
        user_data = create_mock_user(user_id, email, role)
        app.dependency_overrides[require_user] = override_require_user_factory(user_data)

    test_client.set_auth_user = set_auth_user

    yield test_client

    # Cleanup
    app.dependency_overrides.clear()


class TestPublicLeaguesEndpoint:
    """Test GET /api/sports/leagues"""

    def test_get_all_leagues_unauthenticated(self, client):
        """Anyone can view available leagues"""
        response = client.get("/api/sports/leagues")
        assert response.status_code == 200
        leagues = response.json()
        assert len(leagues) == 5
        assert all('league_code' in league for league in leagues)


class TestUserPreferencesEndpoint:
    """Test sports preferences CRUD"""

    def test_free_user_cannot_access_preferences(self, client):
        """Free tier users get 403 when accessing preferences"""
        client.set_auth_user(1, "free@test.com", "subscriber")
        response = client.get("/api/sports/preferences")
        assert response.status_code == 403
        assert "Sports preferences require" in response.json()['detail']

    def test_basic_user_can_get_empty_preferences(self, client):
        """Basic tier users can view preferences (initially empty)"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.get("/api/sports/preferences")
        assert response.status_code == 200
        assert response.json() == []

    def test_basic_user_can_select_one_league(self, client):
        """Basic tier users can select exactly one league"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.post(
            "/api/sports/preferences",
            json={"league_ids": [1]}  # EPL
        )
        assert response.status_code == 200
        data = response.json()
        assert data['selected_leagues'] == 1
        assert data['user_tier'] == 'basic'

    def test_basic_user_cannot_select_multiple_leagues(self, client):
        """Basic tier users cannot select 2+ leagues"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.post(
            "/api/sports/preferences",
            json={"league_ids": [1, 2]}
        )
        assert response.status_code == 403
        assert "Basic tier allows selection of 1 league" in response.json()['detail']

    def test_premium_user_can_select_unlimited_leagues(self, client):
        """Premium tier users can select all leagues"""
        client.set_auth_user(3, "premium@test.com", "subscriber")
        response = client.post(
            "/api/sports/preferences",
            json={"league_ids": [1, 2, 3, 4, 5]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['selected_leagues'] == 5


class TestAccessibleLeaguesEndpoint:
    """Test GET /api/sports/accessible"""

    def test_free_user_no_accessible_leagues(self, client):
        """Free users get empty list"""
        client.set_auth_user(1, "free@test.com", "subscriber")
        response = client.get("/api/sports/accessible")
        assert response.status_code == 200
        assert response.json() == []

    def test_basic_user_gets_basic_leagues(self, client):
        """Basic users can access basic-tier leagues"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.get("/api/sports/accessible")
        assert response.status_code == 200
        leagues = response.json()
        assert len(leagues) == 3  # EPL, NBA, NFL
        assert all(league['tier_requirement'] == 'basic' for league in leagues)

    def test_premium_user_gets_all_leagues(self, client):
        """Premium users can access all leagues"""
        client.set_auth_user(3, "premium@test.com", "subscriber")
        response = client.get("/api/sports/accessible")
        assert response.status_code == 200
        leagues = response.json()
        assert len(leagues) == 5  # All leagues


class TestLeagueAccessCheck:
    """Test GET /api/sports/check-access/{league_code}"""

    def test_basic_user_can_access_basic_league(self, client):
        """Basic user has access to EPL"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.get("/api/sports/check-access/EPL")
        assert response.status_code == 200
        data = response.json()
        assert data['has_access'] is True
        assert data['requires_upgrade'] is False
        assert data['current_tier'] == 'basic'

    def test_basic_user_cannot_access_premium_league(self, client):
        """Basic user needs upgrade for La Liga"""
        client.set_auth_user(2, "basic@test.com", "subscriber")
        response = client.get("/api/sports/check-access/LA_LIGA")
        assert response.status_code == 200
        data = response.json()
        assert data['has_access'] is False
        assert data['requires_upgrade'] is True
        assert data['current_tier'] == 'basic'
        assert data['required_tier'] == 'premium'


class TestAdminLeagueManagement:
    """Test admin endpoints for league management"""

    def test_admin_can_create_league(self, client):
        """Admins can create new leagues"""
        client.set_auth_user(4, "admin@test.com", "admin")
        response = client.post(
            "/api/admin/sports/leagues",
            json={
                "league_code": "SERIE_A",
                "name": "Serie A",
                "country": "Italy",
                "tier_requirement": "premium"
            }
        )
        assert response.status_code == 201
        league = response.json()
        assert league['league_code'] == 'SERIE_A'
        assert league['tier_requirement'] == 'premium'

    def test_admin_can_update_league_tier(self, client):
        """Admins can change league tier requirement"""
        client.set_auth_user(4, "admin@test.com", "admin")
        response = client.put(
            "/api/admin/sports/leagues/1",
            json={"tier_requirement": "premium"}
        )
        assert response.status_code == 200
        league = response.json()
        assert league['tier_requirement'] == 'premium'

    def test_admin_can_deactivate_league(self, client):
        """Admins can soft-delete leagues"""
        client.set_auth_user(4, "admin@test.com", "admin")
        response = client.delete("/api/admin/sports/leagues/5")
        assert response.status_code == 200
        assert "deactivated successfully" in response.json()['message']

    def test_admin_list_includes_inactive_leagues(self, client):
        """Admin list shows all leagues including inactive"""
        client.set_auth_user(4, "admin@test.com", "admin")
        # First deactivate a league
        client.delete("/api/admin/sports/leagues/4")

        # Then list all
        response = client.get("/api/admin/sports/leagues")
        assert response.status_code == 200
        leagues = response.json()
        # Check that inactive leagues are included
        inactive_count = sum(1 for league in leagues if not league['is_active'])
        assert inactive_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
