"""
The Daily Worker - SQLAlchemy Database Models
ORM models for the application
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, Integer, String, Text, Float, DateTime,
    ForeignKey, CheckConstraint, Table
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Association table for article-source many-to-many relationship
article_sources = Table(
    'article_sources',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    Column('source_id', Integer, ForeignKey('sources.id'), primary_key=True),
    Column('citation_url', String),
    Column('citation_text', Text)
)


class Source(Base):
    """News source model"""
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    rss_feed: Mapped[Optional[str]] = mapped_column(String)
    credibility_score: Mapped[int] = mapped_column(Integer, default=5)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    political_lean: Mapped[str] = mapped_column(String, default='center')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    articles: Mapped[List["Article"]] = relationship(
        secondary=article_sources,
        back_populates="sources"
    )

    __table_args__ = (
        CheckConstraint('credibility_score BETWEEN 1 AND 5'),
        CheckConstraint("source_type IN ('news_wire', 'investigative', 'academic', 'local', 'social')"),
        CheckConstraint("political_lean IN ('left', 'center-left', 'center', 'center-right', 'right')"),
    )

    def __repr__(self):
        return f"<Source(name='{self.name}', type='{self.source_type}')>"


class Region(Base):
    """Geographic region model"""
    __tablename__ = 'regions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    region_type: Mapped[str] = mapped_column(String, nullable=False)
    state_code: Mapped[Optional[str]] = mapped_column(String(2))
    population: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    articles: Mapped[List["Article"]] = relationship(back_populates="region")
    topics: Mapped[List["Topic"]] = relationship(back_populates="region")

    __table_args__ = (
        CheckConstraint("region_type IN ('national', 'state', 'city', 'metro')"),
    )

    def __repr__(self):
        return f"<Region(name='{self.name}', type='{self.region_type}')>"


class Category(Base):
    """Article category model"""
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    articles: Mapped[List["Article"]] = relationship(back_populates="category")
    topics: Mapped[List["Topic"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}')>"


class Article(Base):
    """Article model"""
    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)

    # Article metadata
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'), nullable=False)
    author: Mapped[str] = mapped_column(String, default='The Daily Worker Editorial Team')

    # Regional flags
    is_national: Mapped[bool] = mapped_column(Boolean, default=False)
    is_local: Mapped[bool] = mapped_column(Boolean, default=False)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey('regions.id'))

    # Story type flags
    is_ongoing: Mapped[bool] = mapped_column(Boolean, default=False)
    is_new: Mapped[bool] = mapped_column(Boolean, default=True)

    # Content quality
    reading_level: Mapped[Optional[float]] = mapped_column(Float)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Images
    image_url: Mapped[Optional[str]] = mapped_column(String)
    image_attribution: Mapped[Optional[str]] = mapped_column(String)
    image_source: Mapped[Optional[str]] = mapped_column(String)

    # Special sections
    why_this_matters: Mapped[Optional[str]] = mapped_column(Text)
    what_you_can_do: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(String, default='draft')

    # Publishing
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Automated journalism workflow (added in migration 001)
    bias_scan_report: Mapped[Optional[str]] = mapped_column(Text)  # JSON report from bias detection scan
    self_audit_passed: Mapped[bool] = mapped_column(Boolean, default=False)  # Did article pass self-audit?
    editorial_notes: Mapped[Optional[str]] = mapped_column(Text)  # Notes from human editors
    assigned_editor: Mapped[Optional[str]] = mapped_column(String)  # Editor assigned to review
    review_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)  # Review deadline

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="articles")
    region: Mapped[Optional["Region"]] = relationship(back_populates="articles")
    sources: Mapped[List["Source"]] = relationship(
        secondary=article_sources,
        back_populates="articles"
    )
    revisions: Mapped[List["ArticleRevision"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    corrections: Mapped[List["Correction"]] = relationship(back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'pending_review', 'under_review', 'revision_requested', 'approved', 'published', 'archived', 'needs_senior_review')"),
    )

    def __repr__(self):
        return f"<Article(title='{self.title}', status='{self.status}')>"


class Topic(Base):
    """Content discovery topic model"""
    __tablename__ = 'topics'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[Optional[str]] = mapped_column(Text)

    # Discovery metadata
    discovered_from: Mapped[Optional[str]] = mapped_column(String)
    discovery_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Viability checks
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    academic_citation_count: Mapped[int] = mapped_column(Integer, default=0)
    worker_relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    engagement_score: Mapped[Optional[float]] = mapped_column(Float)

    # Categorization
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id'))
    is_national: Mapped[bool] = mapped_column(Boolean, default=False)
    is_local: Mapped[bool] = mapped_column(Boolean, default=False)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey('regions.id'))

    # Processing status
    status: Mapped[str] = mapped_column(String, default='discovered')
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Verification workflow (added in migration 001)
    verified_facts: Mapped[Optional[str]] = mapped_column(Text)  # JSON array of verified facts
    source_plan: Mapped[Optional[str]] = mapped_column(Text)  # JSON: planned sources for verification
    verification_status: Mapped[str] = mapped_column(String, default='pending')

    # Investigation tracking (added for Investigatory Journalist Agent)
    investigated: Mapped[bool] = mapped_column(Boolean, default=False)
    investigation_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    investigation_confidence: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    investigation_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey('articles.id'))
    category: Mapped[Optional["Category"]] = relationship(back_populates="topics")
    region: Mapped[Optional["Region"]] = relationship(back_populates="topics")

    __table_args__ = (
        CheckConstraint("status IN ('discovered', 'filtered', 'approved', 'rejected', 'generated')"),
        CheckConstraint("verification_status IN ('pending', 'in_progress', 'verified', 'partial', 'failed', 'unverified', 'certified')"),
    )

    def __repr__(self):
        return f"<Topic(title='{self.title}', status='{self.status}')>"


class EventCandidate(Base):
    """Event candidate model for automated journalism pipeline"""
    __tablename__ = 'event_candidates'

    id: Mapped[int] = mapped_column(primary_key=True)

    # Event details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String)
    discovered_from: Mapped[Optional[str]] = mapped_column(String)  # RSS feed, Twitter, Reddit, etc.

    # Event metadata
    event_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    discovery_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Newsworthiness scoring (evaluated by Evaluation Agent)
    worker_impact_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-10
    timeliness_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-10
    verifiability_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-10
    regional_relevance_score: Mapped[Optional[float]] = mapped_column(Float)  # 0-10
    final_newsworthiness_score: Mapped[Optional[float]] = mapped_column(Float)  # Weighted average

    # Topic categorization
    suggested_category: Mapped[Optional[str]] = mapped_column(String)
    keywords: Mapped[Optional[str]] = mapped_column(Text)  # JSON array or comma-separated

    # Regional classification
    is_national: Mapped[bool] = mapped_column(Boolean, default=False)
    is_local: Mapped[bool] = mapped_column(Boolean, default=False)
    region_id: Mapped[Optional[int]] = mapped_column(ForeignKey('regions.id'))

    # Processing status
    status: Mapped[str] = mapped_column(String, default='discovered')
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Links to generated content
    topic_id: Mapped[Optional[int]] = mapped_column(ForeignKey('topics.id'))
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey('articles.id'))

    # Timestamps
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    region: Mapped[Optional["Region"]] = relationship()
    topic: Mapped[Optional["Topic"]] = relationship()
    article: Mapped[Optional["Article"]] = relationship()

    __table_args__ = (
        CheckConstraint("status IN ('discovered', 'evaluated', 'approved', 'rejected', 'converted')"),
    )

    def __repr__(self):
        return f"<EventCandidate(title='{self.title}', status='{self.status}', score={self.final_newsworthiness_score})>"


class ArticleRevision(Base):
    """Article revision tracking model"""
    __tablename__ = 'article_revisions'

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)

    # Revision metadata
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    revised_by: Mapped[str] = mapped_column(String, nullable=False)  # Agent name or editor username
    revision_type: Mapped[str] = mapped_column(String, nullable=False)

    # Changed fields (NULL if not changed in this revision)
    title_before: Mapped[Optional[str]] = mapped_column(Text)
    title_after: Mapped[Optional[str]] = mapped_column(Text)
    body_before: Mapped[Optional[str]] = mapped_column(Text)
    body_after: Mapped[Optional[str]] = mapped_column(Text)
    summary_before: Mapped[Optional[str]] = mapped_column(Text)
    summary_after: Mapped[Optional[str]] = mapped_column(Text)

    # Revision notes
    change_summary: Mapped[Optional[str]] = mapped_column(Text)  # Brief description of changes
    change_reason: Mapped[Optional[str]] = mapped_column(Text)  # Why changes were made

    # Verification data
    sources_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    bias_check_passed: Mapped[Optional[bool]] = mapped_column(Boolean)
    reading_level_before: Mapped[Optional[float]] = mapped_column(Float)
    reading_level_after: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    article: Mapped["Article"] = relationship(back_populates="revisions")

    __table_args__ = (
        CheckConstraint("revision_type IN ('draft', 'ai_edit', 'human_edit', 'fact_check', 'bias_correction', 'copy_edit')"),
    )

    def __repr__(self):
        return f"<ArticleRevision(article_id={self.article_id}, revision={self.revision_number}, type='{self.revision_type}')>"


class Correction(Base):
    """Post-publication correction model"""
    __tablename__ = 'corrections'

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)

    # Correction details
    correction_type: Mapped[str] = mapped_column(String, nullable=False)

    # What was wrong
    incorrect_text: Mapped[str] = mapped_column(Text, nullable=False)
    correct_text: Mapped[str] = mapped_column(Text, nullable=False)
    section_affected: Mapped[Optional[str]] = mapped_column(String)  # headline, body, summary, etc.

    # Correction metadata
    severity: Mapped[str] = mapped_column(String, default='minor')
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Explanation of what was wrong

    # Discovery
    reported_by: Mapped[Optional[str]] = mapped_column(String)  # Who found the error
    reported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Resolution
    corrected_by: Mapped[Optional[str]] = mapped_column(String)  # Editor who made the correction
    corrected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Transparency
    public_notice: Mapped[Optional[str]] = mapped_column(Text)  # Public correction notice
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)  # Is correction notice published
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Status
    status: Mapped[str] = mapped_column(String, default='pending')

    # Relationships
    article: Mapped["Article"] = relationship(back_populates="corrections")

    __table_args__ = (
        CheckConstraint("correction_type IN ('factual_error', 'source_error', 'clarification', 'update', 'retraction')"),
        CheckConstraint("severity IN ('minor', 'moderate', 'major', 'critical')"),
        CheckConstraint("status IN ('pending', 'verified', 'corrected', 'published')"),
    )

    def __repr__(self):
        return f"<Correction(article_id={self.article_id}, type='{self.correction_type}', severity='{self.severity}')>"


class SourceReliabilityLog(Base):
    """Source reliability tracking and learning loop model"""
    __tablename__ = 'source_reliability_log'

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey('sources.id'), nullable=False)

    # Event details
    event_type: Mapped[str] = mapped_column(String, nullable=False)

    # Impact on reliability
    reliability_delta: Mapped[Optional[float]] = mapped_column(Float)  # +/- change to credibility score
    previous_score: Mapped[Optional[int]] = mapped_column(Integer)
    new_score: Mapped[Optional[int]] = mapped_column(Integer)

    # Context
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey('articles.id', ondelete='SET NULL'))
    correction_id: Mapped[Optional[int]] = mapped_column(ForeignKey('corrections.id', ondelete='SET NULL'))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Automated learning
    automated_adjustment: Mapped[bool] = mapped_column(Boolean, default=False)  # Auto-adjusted by agent?
    manual_override: Mapped[bool] = mapped_column(Boolean, default=False)  # Manually set by human?
    reviewed_by: Mapped[Optional[str]] = mapped_column(String)  # Human reviewer if manual

    # Timestamps
    logged_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source: Mapped["Source"] = relationship()
    article: Mapped[Optional["Article"]] = relationship()
    correction: Mapped[Optional["Correction"]] = relationship()

    __table_args__ = (
        CheckConstraint("event_type IN ('article_published', 'correction_issued', 'fact_check_pass', 'fact_check_fail', 'retraction', 'citation_added')"),
    )

    def __repr__(self):
        return f"<SourceReliabilityLog(source_id={self.source_id}, event='{self.event_type}', delta={self.reliability_delta})>"


class SportsLeague(Base):
    """Sports league model for subscription-based sports content"""
    __tablename__ = 'sports_leagues'

    id: Mapped[int] = mapped_column(primary_key=True)
    league_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String)
    tier_requirement: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user_preferences: Mapped[List["UserSportsPreference"]] = relationship(back_populates="league")
    results: Mapped[List["SportsResult"]] = relationship(back_populates="league")

    __table_args__ = (
        CheckConstraint("tier_requirement IN ('free', 'basic', 'premium')"),
    )

    def __repr__(self):
        return f"<SportsLeague(code='{self.league_code}', name='{self.name}', tier='{self.tier_requirement}')>"


class UserSportsPreference(Base):
    """User sports league preferences"""
    __tablename__ = 'user_sports_preferences'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    league_id: Mapped[int] = mapped_column(ForeignKey('sports_leagues.id'), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league: Mapped["SportsLeague"] = relationship(back_populates="user_preferences")

    def __repr__(self):
        return f"<UserSportsPreference(user_id={self.user_id}, league_id={self.league_id}, enabled={self.enabled})>"


class SportsResult(Base):
    """Sports match results for article generation"""
    __tablename__ = 'sports_results'

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey('sports_leagues.id'), nullable=False)
    match_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    home_team: Mapped[str] = mapped_column(String, nullable=False)
    away_team: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[Optional[str]] = mapped_column(String)  # e.g., "2-1", "104-98"
    summary: Mapped[Optional[str]] = mapped_column(Text)  # Brief match summary
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey('articles.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    league: Mapped["SportsLeague"] = relationship(back_populates="results")

    def __repr__(self):
        return f"<SportsResult(league_id={self.league_id}, {self.home_team} vs {self.away_team}, {self.match_date})>"
