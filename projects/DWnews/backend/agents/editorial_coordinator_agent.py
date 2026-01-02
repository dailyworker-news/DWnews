"""
Editorial Coordinator Agent - Manages human editorial oversight workflow

Responsibilities:
- Assign draft articles to human editors
- Set review deadlines based on article type
- Send email notifications to editors
- Track SLA compliance and flag overdue reviews
- Orchestrate revision loop when editors request changes
- Update article status through workflow states

Workflow States:
draft → under_review → revision_requested → draft → under_review → approved → published
                                    ↑______________|
                                    (revision loop)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import Article, ArticleRevision
from backend.agents.email_notifications import send_assignment_email, send_revision_complete_email, send_overdue_alert_email

logger = logging.getLogger(__name__)

# Editor pool configuration
EDITORS = [
    {"email": "labor@dailyworker.news", "categories": ["labor", "unions"]},
    {"email": "housing@dailyworker.news", "categories": ["housing", "community"]},
    {"email": "politics@dailyworker.news", "categories": ["politics", "government"]},
    {"email": "general@dailyworker.news", "categories": []},  # Handles all categories
]

# SLA configuration (in hours)
SLA_DEADLINES = {
    "labor": 24,
    "unions": 24,
    "politics": 24,
    "housing": 48,
    "community": 48,
    "environment": 48,
    "culture": 72,
    "default": 48
}

MAX_REVISIONS = 2  # Maximum number of revision attempts per article


class EditorialCoordinator:
    """
    Coordinates editorial workflow between AI-generated articles and human editors
    """

    def __init__(self, db: Session):
        self.db = db
        self.logger = logger

    def assign_article(self, article_id: int, editor_email: Optional[str] = None) -> bool:
        """
        Assign an article to an editor for review

        Args:
            article_id: ID of article to assign
            editor_email: Optional specific editor email, otherwise auto-assigns

        Returns:
            True if assignment successful
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            # Determine editor if not specified
            if not editor_email:
                editor_email = self._select_editor(article)

            # Set assignment
            article.assigned_editor = editor_email
            article.status = 'under_review'

            # Set review deadline
            hours = self._get_deadline_hours(article)
            article.review_deadline = datetime.utcnow() + timedelta(hours=hours)

            self.db.commit()

            self.logger.info(f"Assigned article {article_id} to {editor_email}, deadline in {hours}h")
            return True

        except Exception as e:
            self.logger.error(f"Error assigning article {article_id}: {e}")
            self.db.rollback()
            return False

    def set_review_deadline(self, article_id: int, hours: Optional[int] = None) -> bool:
        """
        Set or update review deadline for an article

        Args:
            article_id: ID of article
            hours: Hours until deadline, defaults to SLA for article category

        Returns:
            True if successful
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            if hours is None:
                hours = self._get_deadline_hours(article)

            article.review_deadline = datetime.utcnow() + timedelta(hours=hours)
            self.db.commit()

            self.logger.info(f"Set review deadline for article {article_id}: {hours} hours")
            return True

        except Exception as e:
            self.logger.error(f"Error setting deadline for article {article_id}: {e}")
            self.db.rollback()
            return False

    def notify_editor(self, article_id: int) -> bool:
        """
        Send email notification to assigned editor about article review

        Args:
            article_id: ID of article

        Returns:
            True if notification sent successfully
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            if not article.assigned_editor:
                self.logger.error(f"Article {article_id} has no assigned editor")
                return False

            success = send_assignment_email(article.assigned_editor, article)

            if success:
                self.logger.info(f"Sent assignment notification for article {article_id} to {article.assigned_editor}")
            else:
                self.logger.warning(f"Failed to send notification for article {article_id}")

            return success

        except Exception as e:
            self.logger.error(f"Error notifying editor for article {article_id}: {e}")
            return False

    def process_revision_request(self, article_id: int, editorial_notes: str) -> bool:
        """
        Process an editor's request for article revision

        Workflow:
        1. Update article status to 'revision_requested'
        2. Log editorial notes in article_revisions table
        3. Trigger Enhanced Journalist Agent to regenerate
        4. Re-assign to same editor for re-review

        Args:
            article_id: ID of article
            editorial_notes: Specific feedback from editor

        Returns:
            True if revision request processed successfully
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            # Check revision count
            revision_count = self.db.query(ArticleRevision).filter(
                ArticleRevision.article_id == article_id,
                ArticleRevision.revision_type == 'human_edit'
            ).count()

            if revision_count >= MAX_REVISIONS:
                self.logger.warning(f"Article {article_id} has reached max revisions ({MAX_REVISIONS})")
                article.status = 'needs_senior_review'
                article.editorial_notes = f"Max revisions reached. Latest notes: {editorial_notes}"
                self.db.commit()
                return False

            # Store current state before revision
            old_status = article.status
            old_body = article.body
            old_reading_level = article.reading_level

            # Update article with editorial notes
            article.editorial_notes = editorial_notes
            article.status = 'revision_requested'

            # Log the revision request
            revision = ArticleRevision(
                article_id=article.id,
                revision_number=revision_count + 1,
                revised_by=article.assigned_editor or 'unknown_editor',
                revision_type='human_edit',
                body_before=old_body,
                change_reason=editorial_notes,
                reading_level_before=old_reading_level,
                created_at=datetime.utcnow()
            )
            self.db.add(revision)
            self.db.commit()

            self.logger.info(f"Revision requested for article {article_id}, revision #{revision_count + 1}")
            self.logger.info(f"Editorial notes: {editorial_notes[:100]}...")

            # Note: The actual regeneration should be triggered by the Enhanced Journalist Agent
            # This is handled separately in the workflow orchestration

            return True

        except Exception as e:
            self.logger.error(f"Error processing revision request for article {article_id}: {e}")
            self.db.rollback()
            return False

    def approve_article(self, article_id: int, approved_by: str) -> bool:
        """
        Approve an article for publication

        Args:
            article_id: ID of article
            approved_by: Email/username of approving editor

        Returns:
            True if approved successfully
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            article.status = 'approved'
            article.assigned_editor = approved_by
            article.editorial_notes = f"Approved by {approved_by} on {datetime.utcnow().isoformat()}"

            self.db.commit()

            self.logger.info(f"Article {article_id} approved by {approved_by}")
            return True

        except Exception as e:
            self.logger.error(f"Error approving article {article_id}: {e}")
            self.db.rollback()
            return False

    def reject_article(self, article_id: int, rejected_by: str, reason: str) -> bool:
        """
        Reject an article

        Args:
            article_id: ID of article
            rejected_by: Email/username of rejecting editor
            reason: Reason for rejection

        Returns:
            True if rejected successfully
        """
        try:
            article = self.db.query(Article).filter(Article.id == article_id).first()

            if not article:
                self.logger.error(f"Article {article_id} not found")
                return False

            article.status = 'archived'
            article.assigned_editor = rejected_by
            article.editorial_notes = f"Rejected by {rejected_by}: {reason}"

            self.db.commit()

            self.logger.info(f"Article {article_id} rejected by {rejected_by}: {reason[:100]}")
            return True

        except Exception as e:
            self.logger.error(f"Error rejecting article {article_id}: {e}")
            self.db.rollback()
            return False

    def check_overdue_reviews(self) -> List[Article]:
        """
        Find all articles with overdue reviews

        Returns:
            List of overdue articles
        """
        try:
            now = datetime.utcnow()

            overdue_articles = self.db.query(Article).filter(
                and_(
                    Article.status == 'under_review',
                    Article.review_deadline < now,
                    Article.review_deadline.isnot(None)
                )
            ).all()

            self.logger.info(f"Found {len(overdue_articles)} overdue articles")
            return overdue_articles

        except Exception as e:
            self.logger.error(f"Error checking overdue reviews: {e}")
            return []

    def send_overdue_alerts(self) -> int:
        """
        Send email alerts for all overdue reviews

        Returns:
            Number of alerts sent
        """
        try:
            overdue_articles = self.check_overdue_reviews()
            sent_count = 0

            for article in overdue_articles:
                if article.assigned_editor:
                    success = send_overdue_alert_email(article.assigned_editor, article)
                    if success:
                        sent_count += 1

            self.logger.info(f"Sent {sent_count} overdue alerts")
            return sent_count

        except Exception as e:
            self.logger.error(f"Error sending overdue alerts: {e}")
            return 0

    def get_editor_workload(self, editor_email: str) -> int:
        """
        Get count of articles currently assigned to an editor

        Args:
            editor_email: Editor's email address

        Returns:
            Number of articles assigned to editor
        """
        try:
            workload = self.db.query(Article).filter(
                and_(
                    Article.assigned_editor == editor_email,
                    Article.status.in_(['under_review', 'revision_requested'])
                )
            ).count()

            return workload

        except Exception as e:
            self.logger.error(f"Error getting workload for {editor_email}: {e}")
            return 0

    def get_pending_articles(self) -> List[Article]:
        """
        Get all articles pending editorial review

        Returns:
            List of draft articles ready for assignment
        """
        try:
            pending = self.db.query(Article).filter(
                Article.status == 'draft',
                Article.self_audit_passed == True
            ).order_by(Article.created_at.asc()).all()

            self.logger.info(f"Found {len(pending)} articles pending review")
            return pending

        except Exception as e:
            self.logger.error(f"Error getting pending articles: {e}")
            return []

    def auto_assign_pending_articles(self) -> int:
        """
        Automatically assign all pending draft articles to editors

        Returns:
            Number of articles assigned
        """
        try:
            pending_articles = self.get_pending_articles()
            assigned_count = 0

            for article in pending_articles:
                if self.assign_article(article.id):
                    # Send notification
                    self.notify_editor(article.id)
                    assigned_count += 1

            self.logger.info(f"Auto-assigned {assigned_count} articles")
            return assigned_count

        except Exception as e:
            self.logger.error(f"Error auto-assigning articles: {e}")
            return 0

    def _select_editor(self, article: Article) -> str:
        """
        Select the best editor for an article based on category and workload

        Args:
            article: Article to assign

        Returns:
            Editor email address
        """
        category_slug = article.category.slug if article.category else None

        # Find editors who specialize in this category
        specialist_editors = [
            e for e in EDITORS
            if category_slug in e['categories']
        ]

        # If no specialists, use general editors
        if not specialist_editors:
            specialist_editors = [e for e in EDITORS if not e['categories']]

        # If still none, use all editors
        if not specialist_editors:
            specialist_editors = EDITORS

        # Select editor with lowest workload
        best_editor = None
        min_workload = float('inf')

        for editor in specialist_editors:
            workload = self.get_editor_workload(editor['email'])
            if workload < min_workload:
                min_workload = workload
                best_editor = editor['email']

        return best_editor or EDITORS[0]['email']  # Fallback to first editor

    def _get_deadline_hours(self, article: Article) -> int:
        """
        Get SLA deadline hours for an article based on category

        Args:
            article: Article to check

        Returns:
            Number of hours for review deadline
        """
        category_slug = article.category.slug if article.category else None
        return SLA_DEADLINES.get(category_slug, SLA_DEADLINES['default'])


# Convenience function for running as a scheduled job
def run_editorial_coordinator(db: Session) -> Dict[str, int]:
    """
    Run editorial coordinator tasks (for scheduled execution)

    1. Auto-assign pending articles
    2. Send overdue alerts

    Args:
        db: Database session

    Returns:
        Dictionary with task results
    """
    coordinator = EditorialCoordinator(db)

    results = {
        'assigned': coordinator.auto_assign_pending_articles(),
        'alerts_sent': coordinator.send_overdue_alerts()
    }

    logger.info(f"Editorial coordinator run complete: {results}")
    return results
