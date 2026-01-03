"""
The Daily Worker - Configuration Management
Loads and validates configuration from environment variables
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Environment
    environment: str = Field(default="local", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")

    # Server
    backend_host: str = Field(default="localhost", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_host: str = Field(default="localhost", alias="FRONTEND_HOST")
    frontend_port: int = Field(default=3000, alias="FRONTEND_PORT")

    # Database
    database_url: str = Field(default="sqlite:///./dwnews.db", alias="DATABASE_URL")

    # LLM APIs
    claude_api_key: Optional[str] = Field(default=None, alias="CLAUDE_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")

    # Social Media APIs
    twitter_api_key: Optional[str] = Field(default=None, alias="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(default=None, alias="TWITTER_API_SECRET")
    twitter_bearer_token: Optional[str] = Field(default=None, alias="TWITTER_BEARER_TOKEN")
    reddit_client_id: Optional[str] = Field(default=None, alias="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(default=None, alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default="DWnews/1.0", alias="REDDIT_USER_AGENT")

    # Image APIs - GCP Vertex AI Imagen (Primary)
    gcp_project_id: Optional[str] = Field(default=None, alias="GCP_PROJECT_ID")
    gcp_location: str = Field(default="us-central1", alias="GCP_LOCATION")
    gcp_service_account_key_path: Optional[str] = Field(default=None, alias="GCP_SERVICE_ACCOUNT_KEY_PATH")
    gcp_service_account_key_base64: Optional[str] = Field(default=None, alias="GCP_SERVICE_ACCOUNT_KEY_BASE64")

    # DEPRECATED: Gemini doesn't have image generation API - use GCP Vertex AI Imagen instead
    gemini_image_api_key: Optional[str] = Field(default=None, alias="GEMINI_IMAGE_API_KEY")

    # Image APIs - Stock Photos (Fallback)
    unsplash_access_key: Optional[str] = Field(default=None, alias="UNSPLASH_ACCESS_KEY")
    pexels_api_key: Optional[str] = Field(default=None, alias="PEXELS_API_KEY")

    # Admin
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="changeme", alias="ADMIN_PASSWORD")
    secret_key: str = Field(default="insecure-dev-key", alias="SECRET_KEY")

    # Stripe Payment Integration
    stripe_publishable_key: Optional[str] = Field(default=None, alias="STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")

    # Content Settings
    min_reading_level: float = Field(default=7.5, alias="MIN_READING_LEVEL")
    max_reading_level: float = Field(default=8.5, alias="MAX_READING_LEVEL")
    min_articles_per_day: int = Field(default=3, alias="MIN_ARTICLES_PER_DAY")
    max_articles_per_day: int = Field(default=10, alias="MAX_ARTICLES_PER_DAY")
    min_good_news_percentage: int = Field(default=10, alias="MIN_GOOD_NEWS_PERCENTAGE")

    # Regional Settings
    default_region: str = Field(default="national", alias="DEFAULT_REGION")
    test_region: str = Field(default="midwest", alias="TEST_REGION")

    # File Storage
    local_image_storage: str = Field(default="./static/images", alias="LOCAL_IMAGE_STORAGE")
    max_image_size_mb: int = Field(default=5, alias="MAX_IMAGE_SIZE_MB")

    # Logging
    log_file: str = Field(default="./logs/dwnews.log", alias="LOG_FILE")
    log_max_bytes: int = Field(default=10485760, alias="LOG_MAX_BYTES")
    log_backup_count: int = Field(default=5, alias="LOG_BACKUP_COUNT")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, alias="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")

    # Feature Flags
    enable_auto_publish: bool = Field(default=False, alias="ENABLE_AUTO_PUBLISH")
    enable_social_posting: bool = Field(default=False, alias="ENABLE_SOCIAL_POSTING")

    # RSS Feeds
    rss_feed_ap: str = Field(default="https://apnews.com/rss", alias="RSS_FEED_AP")
    rss_feed_reuters: str = Field(default="https://www.reuters.com/rssFeed", alias="RSS_FEED_REUTERS")
    rss_feed_propublica: str = Field(default="https://www.propublica.org/feeds/propublica/main", alias="RSS_FEED_PROPUBLICA")

    # Viability Filtering
    min_credible_sources: int = Field(default=3, alias="MIN_CREDIBLE_SOURCES")
    min_academic_citations: int = Field(default=2, alias="MIN_ACADEMIC_CITATIONS")

    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Warn if using default/insecure secret key in production"""
        if values.get("environment") != "local" and v == "insecure-dev-key":
            raise ValueError("SECRET_KEY must be set to a secure value in production")
        return v

    @validator("admin_password")
    def validate_admin_password(cls, v, values):
        """Warn if using default admin password in production"""
        if values.get("environment") != "local" and v == "changeme":
            raise ValueError("ADMIN_PASSWORD must be changed from default in production")
        return v

    def has_llm_api(self) -> bool:
        """Check if at least one LLM API key is configured"""
        return bool(self.claude_api_key or self.openai_api_key or self.gemini_api_key)

    def get_base_url(self) -> str:
        """Get the base URL for the backend"""
        return f"http://{self.backend_host}:{self.backend_port}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Ensure required directories exist
def setup_directories():
    """Create required directories if they don't exist"""
    base_path = Path(__file__).parent.parent

    # Create image storage directory
    image_path = base_path / settings.local_image_storage
    image_path.mkdir(parents=True, exist_ok=True)

    # Create logs directory
    log_path = base_path / Path(settings.log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    print(f"✓ Image storage: {image_path}")
    print(f"✓ Logs directory: {log_path}")


if __name__ == "__main__":
    # Test configuration loading
    setup_directories()
    print("\n=== The Daily Worker Configuration ===")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Database: {settings.database_url}")
    print(f"Backend: {settings.get_base_url()}")
    print(f"LLM APIs configured: {settings.has_llm_api()}")
    print(f"Image storage: {settings.local_image_storage}")
    print(f"Log file: {settings.log_file}")
