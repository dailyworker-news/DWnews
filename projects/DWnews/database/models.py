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

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="articles")
    region: Mapped[Optional["Region"]] = relationship(back_populates="articles")
    sources: Mapped[List["Source"]] = relationship(
        secondary=article_sources,
        back_populates="articles"
    )

    __table_args__ = (
        CheckConstraint("status IN ('draft', 'pending_review', 'approved', 'published', 'archived')"),
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

    # Relationships
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey('articles.id'))
    category: Mapped[Optional["Category"]] = relationship(back_populates="topics")
    region: Mapped[Optional["Region"]] = relationship(back_populates="topics")

    __table_args__ = (
        CheckConstraint("status IN ('discovered', 'filtered', 'approved', 'rejected', 'generated')"),
    )

    def __repr__(self):
        return f"<Topic(title='{self.title}', status='{self.status}')>"
