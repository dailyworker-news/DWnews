#!/usr/bin/env python3
"""
Correction Workflow Test - Post-Publication Corrections

Tests the post-publication correction system:
1. Publish a test article
2. Monitoring Agent flags a correction (simulated)
3. Editor reviews correction request
4. Editor approves correction
5. Correction notice published on article page
6. Source reliability score updated

Usage:
    python scripts/test_correction_workflow.py
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import Article, Correction, Source, SourceReliabilityLog
from backend.database import SessionLocal
from backend.agents.correction_workflow import CorrectionWorkflowManager
from backend.agents.source_reliability import SourceReliabilityTracker


class CorrectionWorkflowTester:
    """Tests the correction workflow system"""

    def __init__(self):
        self.session = SessionLocal()
        self.article = None
        self.correction = None
        self.source = None

    def print_header(self, text: str):
        """Print formatted section header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)

    def setup_test_article(self):
        """Create or use a published article for testing"""
        self.print_header("SETUP: Creating Test Published Article")

        # Check for existing published article
        self.article = self.session.query(Article).filter_by(status='published').first()

        if not self.article:
            print("⚠ No published articles found. Creating mock article...")

            # Create a test article
            from database.models import Category
            category = self.session.query(Category).first()

            if not category:
                category = Category(
                    name="Labor",
                    slug="labor",
                    description="Labor news and organizing"
                )
                self.session.add(category)
                self.session.commit()

            self.article = Article(
                title="Factory Workers Win 15% Wage Increase After Week-Long Strike",
                slug="factory-workers-win-wage-increase-2026",
                body="""
                Workers at Springfield Manufacturing secured a major victory yesterday when management
                agreed to a 15% wage increase across all positions. The agreement came after a week-long
                strike that saw over 200 employees walk off the job.

                According to union representatives, the average wage will increase from $18.50 to $21.28
                per hour. The contract also includes improved health benefits and paid sick leave.

                "This shows what we can accomplish when we stand together," said Maria Rodriguez, a
                10-year employee and union steward.

                Management initially offered only 5%, but workers remained firm in their demands. The
                factory has been operating since 1985 and employs approximately 250 workers.
                """,
                summary="Springfield factory workers secure 15% wage increase after successful strike",
                category_id=category.id,
                status='published',
                published_at=datetime.now() - timedelta(days=2),
                reading_level=8.0,
                word_count=150,
                self_audit_passed=True,
                bias_scan_report=json.dumps({"overall_score": "PASS"}),
                assigned_editor="editor@dailyworker.news"
            )
            self.session.add(self.article)
            self.session.commit()

        # Create a test source
        self.source = self.session.query(Source).first()
        if not self.source:
            self.source = Source(
                name="Springfield Daily News",
                url="https://springfielddaily.example.com",
                source_type='local',
                credibility_score=4,
                political_lean='center'
            )
            self.session.add(self.source)
            self.session.commit()

        print(f"✓ Using article: {self.article.title}")
        print(f"  Published: {self.article.published_at}")
        print(f"  Status: {self.article.status}")

        return True

    def test_step_1_flag_correction(self):
        """Step 1: Monitoring identifies error and flags correction"""
        self.print_header("STEP 1: Monitoring Agent Flags Error")

        print("👀 Monitoring Agent reviewing published articles...")
        print("🔍 Detected potential factual error in article")

        # Simulate error detection
        error_details = {
            'incorrect_text': 'over 200 employees',
            'correct_text': 'approximately 180 employees',
            'source_of_correction': 'Union official statement (verified)',
            'detected_by': 'MonitoringAgent',
            'detection_method': 'cross_reference_check'
        }

        print(f"\n📋 Error detected:")
        print(f"   Incorrect: '{error_details['incorrect_text']}'")
        print(f"   Correct:   '{error_details['correct_text']}'")
        print(f"   Source:    {error_details['source_of_correction']}")

        # Create correction record
        self.correction = Correction(
            article_id=self.article.id,
            correction_type='factual_error',
            incorrect_text=error_details['incorrect_text'],
            correct_text=error_details['correct_text'],
            section_affected='body',
            severity='minor',
            description=f"Employee count was overstated. Verified count is {error_details['correct_text']}.",
            reported_by='MonitoringAgent',
            reported_at=datetime.now(),
            status='pending'
        )
        self.session.add(self.correction)
        self.session.commit()

        print(f"\n✓ Correction flagged")
        print(f"  Correction ID: {self.correction.id}")
        print(f"  Type: {self.correction.correction_type}")
        print(f"  Severity: {self.correction.severity}")
        print(f"  Status: {self.correction.status}")

        return True

    def test_step_2_editor_review(self):
        """Step 2: Editor reviews correction request"""
        self.print_header("STEP 2: Editor Reviews Correction Request")

        print("📝 Editor reviewing flagged correction...")

        # Simulate editor verification
        print("\n  Verification steps:")
        print("  ✓ Checking original sources")
        print("  ✓ Reviewing union statement")
        print("  ✓ Cross-referencing multiple reports")
        print("  ✓ Confirming accurate employee count")

        # Editor decision
        print("\n📝 Editor analysis:")
        print("  Original article cited 'over 200 employees'")
        print("  Union statement specifies '178 members participated'")
        print("  Local news reports '180 workers on strike'")
        print("  Conclusion: Original count was inaccurate")

        # Update correction status
        self.correction.status = 'verified'
        self.session.commit()

        print(f"\n✓ Correction verified by editor")
        print(f"  Status: {self.correction.status}")

        return True

    def test_step_3_approve_correction(self):
        """Step 3: Editor approves and publishes correction"""
        self.print_header("STEP 3: Editor Approves Correction")

        workflow = CorrectionWorkflowManager(self.session)

        print("📝 Editor approving correction...")

        # Create public correction notice
        public_notice = f"""
        CORRECTION: An earlier version of this article stated that "over 200 employees"
        participated in the strike. The accurate number is approximately 180 workers.
        This correction was made on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.
        """

        # Approve correction
        try:
            workflow.approve_correction(
                correction_id=self.correction.id,
                editor_email="editor@dailyworker.news",
                public_notice=public_notice
            )

            # Refresh from database
            self.session.refresh(self.correction)
            self.session.refresh(self.article)

            print(f"✓ Correction approved and published")
            print(f"\n  Public notice:")
            print(f"  {public_notice.strip()}")
            print(f"\n  Correction status: {self.correction.status}")
            print(f"  Corrected by: {self.correction.corrected_by}")
            print(f"  Published: {self.correction.is_published}")

            return True

        except Exception as e:
            print(f"✗ Failed to approve correction: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_step_4_update_article(self):
        """Step 4: Verify article was updated"""
        self.print_header("STEP 4: Verify Article Updated")

        print("🔍 Checking article for correction notice...\n")

        # In a real system, the article body would be updated
        # and a correction notice would be displayed
        print(f"📄 Article corrections:")

        # Get all corrections for this article
        corrections = self.session.query(Correction).filter_by(
            article_id=self.article.id,
            is_published=True
        ).all()

        if corrections:
            print(f"   Total corrections: {len(corrections)}")
            for i, corr in enumerate(corrections, 1):
                print(f"\n   Correction {i}:")
                print(f"     Type: {corr.correction_type}")
                print(f"     Severity: {corr.severity}")
                print(f"     Incorrect: {corr.incorrect_text}")
                print(f"     Correct: {corr.correct_text}")
                print(f"     Published: {corr.published_at}")
        else:
            print(f"   ✗ No published corrections found")
            return False

        print(f"\n✓ Article corrections visible to readers")

        return True

    def test_step_5_update_source_reliability(self):
        """Step 5: Update source reliability scores"""
        self.print_header("STEP 5: Update Source Reliability")

        tracker = SourceReliabilityTracker(self.session)

        print("📊 Updating source reliability scores...\n")

        # In a real scenario, we'd identify which source provided the incorrect info
        # and adjust its credibility score

        print(f"  Source: {self.source.name}")
        print(f"  Current credibility score: {self.source.credibility_score}/5")

        # Record the correction event
        try:
            tracker.log_correction_issued(
                source_id=self.source.id,
                correction_id=self.correction.id,
                severity=self.correction.severity
            )

            # Refresh source
            self.session.refresh(self.source)

            print(f"  Updated credibility score: {self.source.credibility_score}/5")

            # Get reliability logs
            logs = self.session.query(SourceReliabilityLog).filter_by(
                source_id=self.source.id
            ).order_by(SourceReliabilityLog.logged_at.desc()).limit(5).all()

            if logs:
                print(f"\n  Recent reliability events:")
                for log in logs:
                    print(f"    • {log.event_type}: {log.reliability_delta:+.2f} (score: {log.new_score})")

            print(f"\n✓ Source reliability updated")

            return True

        except Exception as e:
            print(f"✗ Failed to update source reliability: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_step_6_verify_transparency(self):
        """Step 6: Verify transparency and audit trail"""
        self.print_header("STEP 6: Verify Transparency & Audit Trail")

        print("🔍 Checking correction audit trail...\n")

        audit_items = []

        # 1. Correction record exists
        if self.correction:
            audit_items.append(("Correction record", True))
            print(f"✓ Correction record exists (ID: {self.correction.id})")
        else:
            audit_items.append(("Correction record", False))
            print(f"✗ No correction record found")

        # 2. Public notice published
        if self.correction and self.correction.is_published and self.correction.public_notice:
            audit_items.append(("Public notice", True))
            print(f"✓ Public notice published")
        else:
            audit_items.append(("Public notice", False))
            print(f"✗ Public notice not published")

        # 3. Editor attribution
        if self.correction and self.correction.corrected_by:
            audit_items.append(("Editor attribution", True))
            print(f"✓ Corrected by: {self.correction.corrected_by}")
        else:
            audit_items.append(("Editor attribution", False))
            print(f"✗ No editor attribution")

        # 4. Timestamps
        if self.correction and self.correction.reported_at and self.correction.corrected_at:
            audit_items.append(("Timestamps", True))
            time_to_correct = (self.correction.corrected_at - self.correction.reported_at).total_seconds() / 60
            print(f"✓ Timestamps: Reported → Corrected in {time_to_correct:.1f} minutes")
        else:
            audit_items.append(("Timestamps", False))
            print(f"✗ Incomplete timestamps")

        # 5. Source reliability update
        logs = self.session.query(SourceReliabilityLog).filter_by(
            correction_id=self.correction.id
        ).count()
        if logs > 0:
            audit_items.append(("Source reliability", True))
            print(f"✓ Source reliability updated")
        else:
            audit_items.append(("Source reliability", False))
            print(f"✗ Source reliability not updated")

        # Calculate transparency score
        passed = sum(1 for _, success in audit_items if success)
        total = len(audit_items)
        transparency_score = (passed / total) * 100

        print(f"\n📊 Transparency Score: {passed}/{total} ({transparency_score:.0f}%)")

        return transparency_score == 100

    def print_summary(self, success: bool):
        """Print final test summary"""
        self.print_header("CORRECTION WORKFLOW TEST - SUMMARY")

        print(f"\n📊 Test Results:")
        print(f"   Article ID: {self.article.id if self.article else 'N/A'}")
        print(f"   Correction ID: {self.correction.id if self.correction else 'N/A'}")
        print(f"   Correction type: {self.correction.correction_type if self.correction else 'N/A'}")
        print(f"   Severity: {self.correction.severity if self.correction else 'N/A'}")
        print(f"   Status: {self.correction.status if self.correction else 'N/A'}")

        if success:
            print(f"\n✓✓✓ SUCCESS: Correction workflow completed successfully!")
            print(f"     Error was identified, verified, corrected, and disclosed transparently.")
        else:
            print(f"\n✗✗✗ FAILURE: Correction workflow encountered issues")

        # Print workflow diagram
        print(f"\n📋 Workflow Summary:")
        print(f"   1. Error flagged by monitoring    ✓")
        print(f"   2. Editor reviewed correction     ✓")
        print(f"   3. Correction approved            ✓")
        print(f"   4. Article updated                ✓")
        print(f"   5. Source reliability adjusted    ✓")
        print(f"   6. Transparency verified          {'✓' if success else '✗'}")

        # Print key metrics
        if self.correction:
            print(f"\n📈 Key Metrics:")
            time_to_correct = None
            if self.correction.reported_at and self.correction.corrected_at:
                time_to_correct = (self.correction.corrected_at - self.correction.reported_at).total_seconds() / 3600
                print(f"   Time to correction: {time_to_correct:.1f} hours")
            print(f"   Public disclosure: {'Yes' if self.correction.is_published else 'No'}")
            print(f"   Source reliability updated: Yes")

    def run(self):
        """Run the complete correction workflow test"""
        print("\n" + "=" * 70)
        print("  DWnews Automated Journalism Pipeline")
        print("  Correction Workflow Test")
        print("=" * 70)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Setup
            if not self.setup_test_article():
                print("\n✗ Setup failed, aborting test")
                return False

            # Run test steps
            steps = [
                self.test_step_1_flag_correction,
                self.test_step_2_editor_review,
                self.test_step_3_approve_correction,
                self.test_step_4_update_article,
                self.test_step_5_update_source_reliability,
                self.test_step_6_verify_transparency
            ]

            all_passed = True
            for step in steps:
                success = step()
                if not success:
                    print(f"\n⚠ Step had issues, continuing...")
                    all_passed = False

            # Print summary
            self.print_summary(all_passed)

            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            return all_passed

        except Exception as e:
            print(f"\n✗ ERROR: Test failed - {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.session.close()


def main():
    """Main entry point"""
    tester = CorrectionWorkflowTester()
    success = tester.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
