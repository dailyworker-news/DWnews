"""
Correction Workflow - Post-Publication Corrections

Handles the correction workflow for published articles:
1. Flag potential corrections (automated by Monitoring Agent or manual reports)
2. Editor review and approval
3. Publish correction notices
4. Update article content if needed
5. Optionally post correction to social media

Correction Types:
- factual_error: Incorrect fact or figure
- source_error: Source misattributed or incorrect
- clarification: Additional context needed
- update: New information available
- retraction: Article needs to be retracted

Severity Levels:
- minor: Small error, doesn't affect main story
- moderate: Noticeable error, needs correction
- major: Significant error affecting story interpretation
- critical: Fundamental error requiring retraction
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Article, Correction
from backend.logging_config import get_logger

logger = get_logger(__name__)


class CorrectionWorkflow:
    """
    Manages the post-publication correction workflow
    """

    def __init__(self, session: Session):
        """
        Initialize the Correction Workflow

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def flag_correction(
        self,
        article_id: int,
        correction_type: str,
        incorrect_text: str,
        correct_text: str,
        description: str,
        severity: str = 'moderate',
        section_affected: Optional[str] = None,
        reported_by: Optional[str] = 'monitoring_agent'
    ) -> Optional[Correction]:
        """
        Flag a potential correction for editor review

        Args:
            article_id: Article ID needing correction
            correction_type: Type of correction (factual_error, source_error, etc.)
            incorrect_text: Text that needs correction
            correct_text: Corrected text
            description: Explanation of what's wrong
            severity: Severity level (minor, moderate, major, critical)
            section_affected: Section needing correction (headline, body, summary)
            reported_by: Who reported the issue

        Returns:
            Correction instance if created successfully, None otherwise
        """
        try:
            # Verify article exists and is published
            article = self.session.query(Article).filter(
                Article.id == article_id
            ).first()

            if not article:
                logger.error(f"Article {article_id} not found")
                return None

            if article.status != 'published':
                logger.error(f"Article {article_id} is not published (status: {article.status})")
                return None

            # Create correction record
            correction = Correction(
                article_id=article_id,
                correction_type=correction_type,
                incorrect_text=incorrect_text,
                correct_text=correct_text,
                section_affected=section_affected,
                severity=severity,
                description=description,
                reported_by=reported_by,
                reported_at=datetime.utcnow(),
                status='pending'
            )

            self.session.add(correction)
            self.session.commit()

            logger.info(
                f"Flagged correction for article {article_id}: "
                f"type={correction_type}, severity={severity}"
            )

            # Send notification to editors (optional)
            # self._notify_editors(correction)

            return correction

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error flagging correction for article {article_id}: {e}")
            return None

    def review_correction(
        self,
        correction_id: int,
        action: str,
        reviewer: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Editor reviews and approves/rejects correction

        Args:
            correction_id: Correction ID to review
            action: 'approve' or 'reject'
            reviewer: Editor username
            notes: Review notes

        Returns:
            True if successful, False otherwise
        """
        try:
            correction = self.session.query(Correction).filter(
                Correction.id == correction_id
            ).first()

            if not correction:
                logger.error(f"Correction {correction_id} not found")
                return False

            if correction.status != 'pending':
                logger.error(f"Correction {correction_id} already reviewed (status: {correction.status})")
                return False

            if action == 'approve':
                correction.status = 'verified'
                logger.info(f"Correction {correction_id} approved by {reviewer}")
            elif action == 'reject':
                correction.status = 'rejected'
                logger.info(f"Correction {correction_id} rejected by {reviewer}")
            else:
                logger.error(f"Invalid action: {action}")
                return False

            # Add review notes
            if notes:
                correction.description += f"\n\nREVIEW NOTES ({reviewer}): {notes}"

            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error reviewing correction {correction_id}: {e}")
            return False

    def publish_correction(
        self,
        correction_id: int,
        public_notice: str,
        editor: str
    ) -> bool:
        """
        Publish correction notice

        Args:
            correction_id: Correction ID to publish
            public_notice: Public-facing correction notice
            editor: Editor publishing the correction

        Returns:
            True if successful, False otherwise
        """
        try:
            correction = self.session.query(Correction).filter(
                Correction.id == correction_id
            ).first()

            if not correction:
                logger.error(f"Correction {correction_id} not found")
                return False

            if correction.status != 'verified':
                logger.error(f"Correction {correction_id} not verified (status: {correction.status})")
                return False

            # Update correction
            correction.status = 'published'
            correction.public_notice = public_notice
            correction.corrected_by = editor
            correction.corrected_at = datetime.utcnow()
            correction.is_published = True
            correction.published_at = datetime.utcnow()

            self.session.commit()

            logger.info(f"Published correction {correction_id} for article {correction.article_id}")

            # Optionally update article content
            # self._apply_correction_to_article(correction)

            # Optionally post to social media
            # self._post_correction_to_social(correction)

            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error publishing correction {correction_id}: {e}")
            return False

    def apply_correction_to_article(
        self,
        correction_id: int,
        update_content: bool = True
    ) -> bool:
        """
        Apply correction to article content

        Args:
            correction_id: Correction ID to apply
            update_content: Whether to update article body with corrected text

        Returns:
            True if successful, False otherwise
        """
        try:
            correction = self.session.query(Correction).filter(
                Correction.id == correction_id
            ).first()

            if not correction:
                logger.error(f"Correction {correction_id} not found")
                return False

            article = correction.article

            if update_content:
                # Update article content
                if correction.section_affected == 'headline':
                    # Don't auto-update headline - require manual editor action
                    logger.warning("Headline correction flagged but requires manual update")
                elif correction.section_affected == 'summary':
                    article.summary = article.summary.replace(
                        correction.incorrect_text,
                        correction.correct_text
                    )
                elif correction.section_affected == 'body':
                    article.body = article.body.replace(
                        correction.incorrect_text,
                        correction.correct_text
                    )

                # Update article metadata
                article.updated_at = datetime.utcnow()

                self.session.commit()

                logger.info(f"Applied correction {correction_id} to article {article.id}")

            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error applying correction {correction_id}: {e}")
            return False

    def get_pending_corrections(self) -> List[Correction]:
        """
        Get all pending corrections awaiting review

        Returns:
            List of pending Correction instances
        """
        return self.session.query(Correction).filter(
            Correction.status == 'pending'
        ).order_by(Correction.severity.desc(), Correction.reported_at.asc()).all()

    def get_article_corrections(self, article_id: int) -> List[Correction]:
        """
        Get all corrections for a specific article

        Args:
            article_id: Article ID

        Returns:
            List of Correction instances
        """
        return self.session.query(Correction).filter(
            Correction.article_id == article_id
        ).order_by(Correction.published_at.desc()).all()

    def get_correction_stats(self) -> Dict:
        """
        Get correction statistics

        Returns:
            Dict with correction stats
        """
        total_corrections = self.session.query(Correction).count()

        pending = self.session.query(Correction).filter(
            Correction.status == 'pending'
        ).count()

        verified = self.session.query(Correction).filter(
            Correction.status == 'verified'
        ).count()

        published = self.session.query(Correction).filter(
            Correction.status == 'published'
        ).count()

        rejected = self.session.query(Correction).filter(
            Correction.status == 'rejected'
        ).count()

        # Count by severity
        critical = self.session.query(Correction).filter(
            Correction.severity == 'critical'
        ).count()

        major = self.session.query(Correction).filter(
            Correction.severity == 'major'
        ).count()

        return {
            'total_corrections': total_corrections,
            'pending': pending,
            'verified': verified,
            'published': published,
            'rejected': rejected,
            'by_severity': {
                'critical': critical,
                'major': major
            }
        }

    def _notify_editors(self, correction: Correction):
        """
        Notify editors of new correction flag (placeholder)

        Args:
            correction: Correction instance
        """
        # TODO: Implement email notification
        # from backend.agents.email_notifications import send_correction_notification
        # send_correction_notification(correction)
        pass

    def _post_correction_to_social(self, correction: Correction):
        """
        Post correction notice to social media (placeholder)

        Args:
            correction: Correction instance
        """
        # TODO: Implement social media posting
        # Post to Twitter/Reddit with correction notice
        pass


def main():
    """
    Main function for running the Correction Workflow standalone
    """
    from database import get_session

    session = get_session()
    workflow = CorrectionWorkflow(session)

    print("=" * 60)
    print("CORRECTION WORKFLOW - Post-Publication Corrections")
    print("=" * 60)

    # Get current stats
    stats = workflow.get_correction_stats()
    print(f"\nCurrent Status:")
    print(f"  Total corrections: {stats['total_corrections']}")
    print(f"  Pending review: {stats['pending']}")
    print(f"  Verified: {stats['verified']}")
    print(f"  Published: {stats['published']}")
    print(f"  Rejected: {stats['rejected']}")
    print(f"\nBy Severity:")
    print(f"  Critical: {stats['by_severity']['critical']}")
    print(f"  Major: {stats['by_severity']['major']}")

    # Show pending corrections
    pending = workflow.get_pending_corrections()
    if pending:
        print(f"\n{'=' * 60}")
        print("PENDING CORRECTIONS:")
        print(f"{'=' * 60}")
        for correction in pending:
            print(f"\nCorrection ID: {correction.id}")
            print(f"  Article ID: {correction.article_id}")
            print(f"  Type: {correction.correction_type}")
            print(f"  Severity: {correction.severity}")
            print(f"  Reported by: {correction.reported_by}")
            print(f"  Reported at: {correction.reported_at}")
            print(f"  Description: {correction.description[:100]}...")
    else:
        print("\nNo pending corrections.")

    session.close()


if __name__ == '__main__':
    main()
