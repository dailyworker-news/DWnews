"""
Tests for backend configuration
"""

import pytest
import os
from backend.config import Settings


class TestConfiguration:
    """Test configuration management"""

    def test_default_settings(self):
        """Test default settings load correctly"""
        settings = Settings()

        assert settings.environment == "local"
        assert settings.debug is True
        assert settings.backend_host == "localhost"
        assert settings.backend_port == 8000

    def test_database_url_default(self):
        """Test default database URL"""
        settings = Settings()
        assert "sqlite" in settings.database_url.lower()

    def test_reading_level_settings(self):
        """Test reading level configuration"""
        settings = Settings()
        assert settings.min_reading_level == 7.5
        assert settings.max_reading_level == 8.5

    def test_content_settings(self):
        """Test content generation settings"""
        settings = Settings()
        assert settings.min_articles_per_day == 3
        assert settings.max_articles_per_day == 10
        assert settings.min_good_news_percentage == 10

    def test_viability_filtering_settings(self):
        """Test viability filtering settings"""
        settings = Settings()
        assert settings.min_credible_sources == 3
        assert settings.min_academic_citations == 2

    def test_has_llm_api_method(self):
        """Test LLM API detection"""
        settings = Settings()

        # Mock having Claude API
        settings.claude_api_key = "test_key"
        assert settings.has_llm_api() is True

        # Mock no APIs
        settings.claude_api_key = None
        settings.openai_api_key = None
        settings.gemini_api_key = None
        assert settings.has_llm_api() is False

    def test_get_base_url_method(self):
        """Test base URL generation"""
        settings = Settings()
        base_url = settings.get_base_url()

        assert "http://" in base_url
        assert "localhost" in base_url
        assert "8000" in base_url

    def test_secret_key_validation_local(self, monkeypatch):
        """Test secret key validation in local environment"""
        # Should not raise error in local environment
        monkeypatch.setenv("ENVIRONMENT", "local")
        monkeypatch.setenv("SECRET_KEY", "insecure-dev-key")
        settings = Settings()
        assert settings.secret_key == "insecure-dev-key"
