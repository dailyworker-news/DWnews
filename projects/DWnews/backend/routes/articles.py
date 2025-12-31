"""
The Daily Worker - Article API Routes
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Article, Category, Region, Source
from backend.database import get_db

router = APIRouter()


# Pydantic models for API
class ArticleResponse(BaseModel):
    id: int
    title: str
    slug: str
    body: str
    summary: Optional[str]
    category_name: str
    category_slug: str
    author: str
    is_national: bool
    is_local: bool
    is_ongoing: bool
    is_new: bool
    region_name: Optional[str]
    reading_level: Optional[float]
    word_count: Optional[int]
    image_url: Optional[str]
    image_attribution: Optional[str]
    why_this_matters: Optional[str]
    what_you_can_do: Optional[str]
    status: str
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str]
    category_name: str
    is_national: bool
    is_local: bool
    is_ongoing: bool
    is_new: bool
    status: str
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleUpdateRequest(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    is_ongoing: Optional[bool] = None


# Routes
@router.get("/", response_model=List[ArticleListResponse])
def get_articles(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    region: Optional[str] = Query(None),  # Changed default from "national" to None to show all articles
    ongoing: Optional[bool] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Get list of articles with filters"""

    query = db.query(Article)

    # Apply filters
    if status:
        query = query.filter(Article.status == status)

    if category:
        cat = db.query(Category).filter(Category.slug == category).first()
        if cat:
            query = query.filter(Article.category_id == cat.id)

    if region == "national":
        query = query.filter(Article.is_national == True)
    elif region == "local":
        query = query.filter(Article.is_local == True)

    if ongoing is not None:
        query = query.filter(Article.is_ongoing == ongoing)

    # Order by published date (newest first) or created date for drafts
    query = query.order_by(
        Article.published_at.desc().nullsfirst(),
        Article.created_at.desc()
    )

    articles = query.offset(offset).limit(limit).all()

    # Format response
    result = []
    for article in articles:
        result.append(ArticleListResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            category_name=article.category.name,
            is_national=article.is_national,
            is_local=article.is_local,
            is_ongoing=article.is_ongoing,
            is_new=article.is_new,
            status=article.status,
            published_at=article.published_at,
            created_at=article.created_at
        ))

    return result


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get single article by ID"""

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse(
        id=article.id,
        title=article.title,
        slug=article.slug,
        body=article.body,
        summary=article.summary,
        category_name=article.category.name,
        category_slug=article.category.slug,
        author=article.author,
        is_national=article.is_national,
        is_local=article.is_local,
        is_ongoing=article.is_ongoing,
        is_new=article.is_new,
        region_name=article.region.name if article.region else None,
        reading_level=article.reading_level,
        word_count=article.word_count,
        image_url=article.image_url,
        image_attribution=article.image_attribution,
        why_this_matters=article.why_this_matters,
        what_you_can_do=article.what_you_can_do,
        status=article.status,
        published_at=article.published_at,
        created_at=article.created_at
    )


@router.patch("/{article_id}")
def update_article(
    article_id: int,
    update: ArticleUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update article (for admin approval/rejection)"""

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Update fields
    if update.status:
        valid_statuses = ['draft', 'pending_review', 'approved', 'published', 'archived']
        if update.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")

        article.status = update.status

        # Set published_at when publishing
        if update.status == 'published' and not article.published_at:
            article.published_at = datetime.utcnow()

    if update.title:
        article.title = update.title

    if update.body:
        article.body = update.body

    if update.is_ongoing is not None:
        article.is_ongoing = update.is_ongoing

    db.commit()
    db.refresh(article)

    return {"message": "Article updated successfully", "id": article.id}


@router.get("/slug/{slug}", response_model=ArticleResponse)
def get_article_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get article by slug"""

    article = db.query(Article).filter(Article.slug == slug).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return ArticleResponse(
        id=article.id,
        title=article.title,
        slug=article.slug,
        body=article.body,
        summary=article.summary,
        category_name=article.category.name,
        category_slug=article.category.slug,
        author=article.author,
        is_national=article.is_national,
        is_local=article.is_local,
        is_ongoing=article.is_ongoing,
        is_new=article.is_new,
        region_name=article.region.name if article.region else None,
        reading_level=article.reading_level,
        word_count=article.word_count,
        image_url=article.image_url,
        image_attribution=article.image_attribution,
        why_this_matters=article.why_this_matters,
        what_you_can_do=article.what_you_can_do,
        status=article.status,
        published_at=article.published_at,
        created_at=article.created_at
    )
