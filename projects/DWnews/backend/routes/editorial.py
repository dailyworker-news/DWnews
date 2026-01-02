"""
Editorial API Routes - Human editorial oversight endpoints

Provides endpoints for:
- Viewing articles pending review
- Getting detailed article review data (with bias scan, self-audit, sources)
- Approving articles
- Requesting revisions
- Rejecting articles
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Article, ArticleRevision, Category
from backend.database import get_db
from backend.agents.editorial_coordinator_agent import EditorialCoordinator

router = APIRouter()


# Pydantic models for API
class SelfAuditResult(BaseModel):
    """Individual self-audit checklist item"""
    criterion: str
    passed: bool
    notes: Optional[str] = None


class SourceInfo(BaseModel):
    """Source information"""
    name: str
    url: str
    credibility_score: int
    source_type: str
    citation_url: Optional[str] = None


class ArticleReviewResponse(BaseModel):
    """Complete article review data"""
    # Basic info
    id: int
    title: str
    slug: str
    body: str
    summary: Optional[str]
    category_name: str
    author: str
    word_count: Optional[int]
    reading_level: Optional[float]
    status: str
    created_at: datetime

    # Editorial info
    assigned_editor: Optional[str]
    review_deadline: Optional[datetime]
    editorial_notes: Optional[str]

    # Quality checks
    self_audit_passed: bool
    bias_scan_report: Optional[Dict[str, Any]]
    self_audit_details: Optional[List[SelfAuditResult]]

    # Sources
    sources: List[SourceInfo]
    verified_facts: Optional[List[str]]

    # Revision history
    revision_count: int
    latest_revision_notes: Optional[str]

    class Config:
        from_attributes = True


class PendingArticleResponse(BaseModel):
    """Simplified article info for pending list"""
    id: int
    title: str
    category_name: str
    word_count: Optional[int]
    reading_level: Optional[float]
    status: str
    assigned_editor: Optional[str]
    review_deadline: Optional[datetime]
    self_audit_passed: bool
    created_at: datetime


class ApproveRequest(BaseModel):
    """Article approval request"""
    approved_by: str


class RevisionRequest(BaseModel):
    """Revision request with editorial notes"""
    editorial_notes: str
    requested_by: str


class RejectRequest(BaseModel):
    """Article rejection request"""
    rejected_by: str
    reason: str


# Routes
@router.get("/pending", response_model=List[PendingArticleResponse])
def get_pending_articles(
    status: Optional[str] = Query('draft'),
    db: Session = Depends(get_db)
):
    """
    Get list of articles pending editorial review

    Query params:
    - status: Filter by status (draft, under_review, revision_requested)
    """
    try:
        query = db.query(Article)

        # Filter by status
        if status:
            if status in ['draft', 'under_review', 'revision_requested']:
                query = query.filter(Article.status == status)
            elif status == 'all_pending':
                query = query.filter(Article.status.in_(['draft', 'under_review', 'revision_requested']))

        # Only show articles that passed self-audit
        query = query.filter(Article.self_audit_passed == True)

        # Order by deadline (urgent first), then creation date
        query = query.order_by(
            Article.review_deadline.asc().nullslast(),
            Article.created_at.asc()
        )

        articles = query.all()

        # Format response
        result = []
        for article in articles:
            result.append(PendingArticleResponse(
                id=article.id,
                title=article.title,
                category_name=article.category.name if article.category else 'Uncategorized',
                word_count=article.word_count,
                reading_level=article.reading_level,
                status=article.status,
                assigned_editor=article.assigned_editor,
                review_deadline=article.review_deadline,
                self_audit_passed=article.self_audit_passed,
                created_at=article.created_at
            ))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching pending articles: {str(e)}")


@router.get("/review/{article_id}", response_model=ArticleReviewResponse)
def get_article_for_review(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete article review data including bias scan, self-audit, sources
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()

        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # Parse bias scan report
        bias_scan_report = None
        if article.bias_scan_report:
            try:
                bias_scan_report = json.loads(article.bias_scan_report)
            except json.JSONDecodeError:
                bias_scan_report = {"error": "Invalid JSON in bias_scan_report"}

        # Parse self-audit details (if stored in bias_scan_report)
        self_audit_details = None
        if bias_scan_report and 'self_audit' in bias_scan_report:
            self_audit_details = [
                SelfAuditResult(
                    criterion=item['criterion'],
                    passed=item['passed'],
                    notes=item.get('notes')
                )
                for item in bias_scan_report['self_audit']
            ]

        # Get sources
        sources = []
        for source in article.sources:
            sources.append(SourceInfo(
                name=source.name,
                url=source.url,
                credibility_score=source.credibility_score,
                source_type=source.source_type,
                citation_url=None  # Could be enhanced to get from article_sources table
            ))

        # Parse verified facts from topic
        verified_facts = None
        # This would require joining with topics table if needed
        # For now, we'll leave it as None or parse from article metadata if stored

        # Get revision history
        revision_count = db.query(ArticleRevision).filter(
            ArticleRevision.article_id == article_id
        ).count()

        latest_revision = db.query(ArticleRevision).filter(
            ArticleRevision.article_id == article_id
        ).order_by(ArticleRevision.created_at.desc()).first()

        latest_revision_notes = latest_revision.change_reason if latest_revision else None

        return ArticleReviewResponse(
            id=article.id,
            title=article.title,
            slug=article.slug,
            body=article.body,
            summary=article.summary,
            category_name=article.category.name if article.category else 'Uncategorized',
            author=article.author,
            word_count=article.word_count,
            reading_level=article.reading_level,
            status=article.status,
            created_at=article.created_at,
            assigned_editor=article.assigned_editor,
            review_deadline=article.review_deadline,
            editorial_notes=article.editorial_notes,
            self_audit_passed=article.self_audit_passed,
            bias_scan_report=bias_scan_report,
            self_audit_details=self_audit_details,
            sources=sources,
            verified_facts=verified_facts,
            revision_count=revision_count,
            latest_revision_notes=latest_revision_notes
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article review data: {str(e)}")


@router.post("/{article_id}/approve")
def approve_article(
    article_id: int,
    request: ApproveRequest,
    db: Session = Depends(get_db)
):
    """
    Approve an article for publication
    """
    try:
        coordinator = EditorialCoordinator(db)
        success = coordinator.approve_article(article_id, request.approved_by)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to approve article")

        return {
            "success": True,
            "message": f"Article {article_id} approved by {request.approved_by}",
            "article_id": article_id
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving article: {str(e)}")


@router.post("/{article_id}/request-revision")
def request_revision(
    article_id: int,
    request: RevisionRequest,
    db: Session = Depends(get_db)
):
    """
    Request revision of an article with editorial notes
    """
    try:
        coordinator = EditorialCoordinator(db)

        # Process revision request
        success = coordinator.process_revision_request(article_id, request.editorial_notes)

        if not success:
            # Check if it's due to max revisions
            article = db.query(Article).filter(Article.id == article_id).first()
            if article and article.status == 'needs_senior_review':
                raise HTTPException(
                    status_code=400,
                    detail="Article has reached maximum revision attempts. Senior editor review required."
                )
            raise HTTPException(status_code=400, detail="Failed to process revision request")

        # Update assigned editor
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.assigned_editor = request.requested_by
            db.commit()

        return {
            "success": True,
            "message": f"Revision requested for article {article_id}",
            "article_id": article_id,
            "editorial_notes": request.editorial_notes
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error requesting revision: {str(e)}")


@router.post("/{article_id}/reject")
def reject_article(
    article_id: int,
    request: RejectRequest,
    db: Session = Depends(get_db)
):
    """
    Reject an article
    """
    try:
        coordinator = EditorialCoordinator(db)
        success = coordinator.reject_article(article_id, request.rejected_by, request.reason)

        if not success:
            raise HTTPException(status_code=400, detail="Failed to reject article")

        return {
            "success": True,
            "message": f"Article {article_id} rejected by {request.rejected_by}",
            "article_id": article_id,
            "reason": request.reason
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting article: {str(e)}")


@router.get("/overdue")
def get_overdue_articles(db: Session = Depends(get_db)):
    """
    Get all articles with overdue reviews
    """
    try:
        coordinator = EditorialCoordinator(db)
        overdue_articles = coordinator.check_overdue_reviews()

        result = []
        for article in overdue_articles:
            hours_overdue = (datetime.utcnow() - article.review_deadline).total_seconds() / 3600 if article.review_deadline else 0

            result.append({
                "id": article.id,
                "title": article.title,
                "category": article.category.name if article.category else 'Uncategorized',
                "assigned_editor": article.assigned_editor,
                "review_deadline": article.review_deadline.isoformat() if article.review_deadline else None,
                "hours_overdue": round(hours_overdue, 1),
                "status": article.status
            })

        return {
            "count": len(result),
            "articles": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching overdue articles: {str(e)}")


@router.get("/workload/{editor_email}")
def get_editor_workload(
    editor_email: str,
    db: Session = Depends(get_db)
):
    """
    Get current workload for an editor
    """
    try:
        coordinator = EditorialCoordinator(db)
        workload = coordinator.get_editor_workload(editor_email)

        # Get details of assigned articles
        articles = db.query(Article).filter(
            Article.assigned_editor == editor_email,
            Article.status.in_(['under_review', 'revision_requested'])
        ).all()

        article_details = []
        for article in articles:
            article_details.append({
                "id": article.id,
                "title": article.title,
                "status": article.status,
                "review_deadline": article.review_deadline.isoformat() if article.review_deadline else None
            })

        return {
            "editor": editor_email,
            "workload": workload,
            "articles": article_details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching editor workload: {str(e)}")


@router.post("/auto-assign")
def auto_assign_articles(db: Session = Depends(get_db)):
    """
    Automatically assign all pending draft articles to editors

    Used by scheduled jobs or manual trigger
    """
    try:
        coordinator = EditorialCoordinator(db)
        assigned_count = coordinator.auto_assign_pending_articles()

        return {
            "success": True,
            "message": f"Assigned {assigned_count} articles to editors",
            "count": assigned_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auto-assigning articles: {str(e)}")


@router.post("/send-overdue-alerts")
def send_overdue_alerts(db: Session = Depends(get_db)):
    """
    Send email alerts for all overdue reviews

    Used by scheduled jobs or manual trigger
    """
    try:
        coordinator = EditorialCoordinator(db)
        alerts_sent = coordinator.send_overdue_alerts()

        return {
            "success": True,
            "message": f"Sent {alerts_sent} overdue alerts",
            "count": alerts_sent
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending overdue alerts: {str(e)}")
