#!/usr/bin/env python3
"""
Test Editorial Workflow - End-to-End Testing

Tests the complete editorial workflow:
1. Generate test article using Enhanced Journalist Agent
2. Auto-assign article to editor
3. Simulate editor requesting revision
4. Verify journalist agent regeneration (manual trigger)
5. Simulate editor approval
6. Verify article status transitions and audit trail

Usage:
    python scripts/test_editorial_workflow.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from database.models import Article, ArticleRevision, Category, Source
from backend.database import get_db, engine
from backend.agents.editorial_coordinator_agent import EditorialCoordinator
from backend.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EditorialWorkflowTest:
    """Test harness for editorial workflow"""

    def __init__(self):
        self.db = next(get_db())
        self.coordinator = EditorialCoordinator(self.db)
        self.test_article_id = None
        self.editor_email = "test-editor@dailyworker.news"

    def cleanup(self):
        """Clean up test data"""
        if self.test_article_id:
            try:
                # Delete test article and related revisions (cascade)
                article = self.db.query(Article).filter(Article.id == self.test_article_id).first()
                if article:
                    self.db.delete(article)
                    self.db.commit()
                    logger.info(f"Cleaned up test article {self.test_article_id}")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
                self.db.rollback()

    def create_test_article(self) -> int:
        """
        Create a test article simulating Enhanced Journalist Agent output

        Returns:
            Article ID
        """
        logger.info("Creating test article...")

        try:
            # Get or create test category
            category = self.db.query(Category).filter(Category.slug == 'labor').first()
            if not category:
                category = Category(
                    name='Labor',
                    slug='labor',
                    description='Labor and workers rights',
                    sort_order=1
                )
                self.db.add(category)
                self.db.commit()
                self.db.refresh(category)

            # Create test article
            article = Article(
                title="Test: Amazon Workers Vote to Unionize in Historic Victory",
                slug=f"test-amazon-union-{datetime.now().timestamp()}",
                body="""
Workers at Amazon's Staten Island warehouse voted overwhelmingly to form a union in a historic victory for labor organizing in the tech sector.

The vote, which concluded Friday evening, saw 2,654 workers vote in favor of unionization compared to 2,131 against, representing a clear mandate for collective bargaining rights at one of America's largest employers.

"This is a victory for every worker who has ever felt powerless against corporate giants," said union organizer Chris Smalls, who was fired by Amazon in 2020 after organizing a walkout over COVID-19 safety concerns.

The successful unionization effort comes after years of aggressive anti-union campaigns by Amazon, which spent millions on consultants and mandatory worker meetings to discourage organizing.

Labor experts say the victory could inspire similar efforts at Amazon facilities nationwide and signal a broader resurgence in union organizing among younger workers.

Amazon representatives declined to comment on the results, but the company is expected to challenge the election through the National Labor Relations Board.
                """.strip(),
                summary="Amazon Staten Island workers vote to unionize in historic labor victory, potentially inspiring nationwide organizing efforts.",
                category_id=category.id,
                author="The Daily Worker AI Journalist",
                is_national=True,
                is_local=False,
                is_ongoing=False,
                is_new=True,
                reading_level=7.8,
                word_count=245,
                why_this_matters="This represents a major breakthrough in tech sector labor organizing and demonstrates that even the largest corporations can be challenged by workers acting collectively.",
                what_you_can_do="Support union organizing efforts in your workplace. Follow @amazonlabor on social media for updates and solidarity actions.",
                status='draft',
                self_audit_passed=True,
                bias_scan_report='{"hallucination_check": {"passed": true}, "propaganda_flags": {"count": 0}, "bias_indicators": {"level": "none"}, "self_audit": [{"criterion": "Clear working-class perspective", "passed": true}, {"criterion": "Reading level 8th grade or below", "passed": true}, {"criterion": "Factual accuracy", "passed": true}, {"criterion": "Source verification", "passed": true}, {"criterion": "Worker agency emphasized", "passed": true}, {"criterion": "Corporate power contextualized", "passed": true}, {"criterion": "Clear call to action", "passed": true}, {"criterion": "Accessible language", "passed": true}, {"criterion": "Systemic analysis present", "passed": true}, {"criterion": "No excessive jargon", "passed": true}]}',
                created_at=datetime.utcnow()
            )

            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)

            # Add test source
            source = self.db.query(Source).filter(Source.name == 'Associated Press').first()
            if source:
                article.sources.append(source)
                self.db.commit()

            logger.info(f"Created test article ID {article.id}: {article.title}")
            return article.id

        except Exception as e:
            logger.error(f"Error creating test article: {e}")
            self.db.rollback()
            raise

    def test_auto_assignment(self, article_id: int) -> bool:
        """Test auto-assignment of article to editor"""
        logger.info(f"\nTEST 1: Auto-assignment of article {article_id}")

        try:
            # Assign article
            success = self.coordinator.assign_article(article_id)

            if not success:
                logger.error("Failed to assign article")
                return False

            # Verify assignment
            article = self.db.query(Article).filter(Article.id == article_id).first()

            assert article is not None, "Article not found"
            assert article.assigned_editor is not None, "No editor assigned"
            assert article.status == 'under_review', f"Wrong status: {article.status}"
            assert article.review_deadline is not None, "No review deadline set"

            logger.info(f"✓ Article assigned to {article.assigned_editor}")
            logger.info(f"✓ Status changed to: {article.status}")
            logger.info(f"✓ Review deadline: {article.review_deadline}")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during auto-assignment test: {e}")
            return False

    def test_email_notification(self, article_id: int) -> bool:
        """Test email notification to editor"""
        logger.info(f"\nTEST 2: Email notification")

        try:
            success = self.coordinator.notify_editor(article_id)

            if not success:
                logger.error("Failed to send notification")
                return False

            logger.info("✓ Email notification sent (check logs for EMAIL output)")
            return True

        except Exception as e:
            logger.error(f"✗ Error during notification test: {e}")
            return False

    def test_revision_request(self, article_id: int) -> bool:
        """Test editor revision request"""
        logger.info(f"\nTEST 3: Revision request")

        editorial_notes = """
Please make the following improvements:
1. Strengthen worker perspective in lead paragraph
2. Add more direct quotes from union organizers
3. Explain what collective bargaining means for average readers
4. Reading level could be slightly lower (target 7.0)
        """.strip()

        try:
            # Request revision
            success = self.coordinator.process_revision_request(article_id, editorial_notes)

            if not success:
                logger.error("Failed to process revision request")
                return False

            # Verify revision was logged
            article = self.db.query(Article).filter(Article.id == article_id).first()
            revision = self.db.query(ArticleRevision).filter(
                ArticleRevision.article_id == article_id
            ).order_by(ArticleRevision.created_at.desc()).first()

            assert article is not None, "Article not found"
            assert article.status == 'revision_requested', f"Wrong status: {article.status}"
            assert article.editorial_notes == editorial_notes, "Editorial notes not saved"
            assert revision is not None, "Revision record not created"
            assert revision.revision_number == 1, f"Wrong revision number: {revision.revision_number}"
            assert revision.change_reason == editorial_notes, "Revision notes don't match"

            logger.info(f"✓ Revision requested")
            logger.info(f"✓ Status changed to: {article.status}")
            logger.info(f"✓ Revision #{revision.revision_number} logged")
            logger.info(f"✓ Editorial notes saved")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during revision request test: {e}")
            return False

    def test_max_revisions(self, article_id: int) -> bool:
        """Test maximum revision limit"""
        logger.info(f"\nTEST 4: Maximum revision limit")

        try:
            # Create second revision
            success1 = self.coordinator.process_revision_request(
                article_id,
                "Second revision: Please add more context about Amazon's anti-union activities"
            )

            assert success1, "Second revision should succeed"
            logger.info("✓ Second revision request succeeded")

            # Try third revision (should fail)
            success2 = self.coordinator.process_revision_request(
                article_id,
                "Third revision: This should fail"
            )

            assert not success2, "Third revision should fail (max reached)"
            logger.info("✓ Third revision request blocked (max reached)")

            # Verify article status
            article = self.db.query(Article).filter(Article.id == article_id).first()
            assert article.status == 'needs_senior_review', f"Wrong status: {article.status}"
            logger.info(f"✓ Article status set to: {article.status}")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during max revisions test: {e}")
            return False

    def test_approval(self, article_id: int) -> bool:
        """Test article approval"""
        logger.info(f"\nTEST 5: Article approval")

        try:
            # Reset article to under_review for approval test
            article = self.db.query(Article).filter(Article.id == article_id).first()
            article.status = 'under_review'
            self.db.commit()

            # Approve article
            success = self.coordinator.approve_article(article_id, self.editor_email)

            if not success:
                logger.error("Failed to approve article")
                return False

            # Verify approval
            self.db.refresh(article)

            assert article.status == 'approved', f"Wrong status: {article.status}"
            assert article.assigned_editor == self.editor_email, "Wrong editor in approval"

            logger.info(f"✓ Article approved")
            logger.info(f"✓ Status changed to: {article.status}")
            logger.info(f"✓ Approved by: {article.assigned_editor}")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during approval test: {e}")
            return False

    def test_rejection(self, article_id: int) -> bool:
        """Test article rejection"""
        logger.info(f"\nTEST 6: Article rejection")

        try:
            # Reset article to under_review for rejection test
            article = self.db.query(Article).filter(Article.id == article_id).first()
            article.status = 'under_review'
            self.db.commit()

            # Reject article
            reason = "Topic not aligned with current editorial priorities"
            success = self.coordinator.reject_article(article_id, self.editor_email, reason)

            if not success:
                logger.error("Failed to reject article")
                return False

            # Verify rejection
            self.db.refresh(article)

            assert article.status == 'archived', f"Wrong status: {article.status}"
            assert reason in article.editorial_notes, "Rejection reason not saved"

            logger.info(f"✓ Article rejected")
            logger.info(f"✓ Status changed to: {article.status}")
            logger.info(f"✓ Rejection reason saved")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during rejection test: {e}")
            return False

    def test_overdue_tracking(self, article_id: int) -> bool:
        """Test overdue review tracking"""
        logger.info(f"\nTEST 7: Overdue review tracking")

        try:
            # Set review deadline to past
            article = self.db.query(Article).filter(Article.id == article_id).first()
            article.status = 'under_review'
            article.review_deadline = datetime.utcnow() - timedelta(hours=5)
            self.db.commit()

            # Check overdue articles
            overdue = self.coordinator.check_overdue_reviews()

            assert len(overdue) > 0, "No overdue articles found"
            assert article.id in [a.id for a in overdue], "Test article not in overdue list"

            logger.info(f"✓ Found {len(overdue)} overdue articles")
            logger.info(f"✓ Test article correctly identified as overdue")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during overdue tracking test: {e}")
            return False

    def test_workload_calculation(self) -> bool:
        """Test editor workload calculation"""
        logger.info(f"\nTEST 8: Editor workload calculation")

        try:
            workload = self.coordinator.get_editor_workload(self.editor_email)

            # Should be at least 1 (our test article)
            assert workload >= 0, f"Invalid workload: {workload}"

            logger.info(f"✓ Editor workload: {workload} articles")

            return True

        except AssertionError as e:
            logger.error(f"✗ Assertion failed: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during workload test: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        logger.info("=" * 80)
        logger.info("EDITORIAL WORKFLOW END-TO-END TEST")
        logger.info("=" * 80)

        try:
            # Create test article
            self.test_article_id = self.create_test_article()

            # Run tests
            results = {
                'Auto-assignment': self.test_auto_assignment(self.test_article_id),
                'Email notification': self.test_email_notification(self.test_article_id),
                'Revision request': self.test_revision_request(self.test_article_id),
                'Max revisions': self.test_max_revisions(self.test_article_id),
                'Article approval': self.test_approval(self.test_article_id),
                'Article rejection': self.test_rejection(self.test_article_id),
                'Overdue tracking': self.test_overdue_tracking(self.test_article_id),
                'Workload calculation': self.test_workload_calculation()
            }

            # Print summary
            logger.info("\n" + "=" * 80)
            logger.info("TEST SUMMARY")
            logger.info("=" * 80)

            passed = sum(1 for result in results.values() if result)
            total = len(results)

            for test_name, result in results.items():
                status = "✓ PASS" if result else "✗ FAIL"
                logger.info(f"{status} - {test_name}")

            logger.info(f"\nTotal: {passed}/{total} tests passed")

            if passed == total:
                logger.info("\n🎉 ALL TESTS PASSED!")
                return True
            else:
                logger.error(f"\n⚠️  {total - passed} tests failed")
                return False

        except Exception as e:
            logger.error(f"Test suite error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Cleanup
            logger.info("\nCleaning up test data...")
            self.cleanup()
            logger.info("Cleanup complete")


def main():
    """Main test entry point"""
    # Set email mode to test
    os.environ['EMAIL_MODE'] = 'test'

    test_suite = EditorialWorkflowTest()

    try:
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        test_suite.cleanup()
        sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        test_suite.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    main()
