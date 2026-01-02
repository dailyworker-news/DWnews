#!/usr/bin/env python3
"""
End-to-end test of automated journalism pipeline.

Tests the complete flow:
1. Signal Intake → discovers events
2. Evaluation → scores and approves events
3. Verification → verifies sources and facts
4. Journalist → generates article drafts
5. Editorial → assigns to editor, handles revisions
6. Publication → publishes article
7. Monitoring → tracks mentions, handles corrections

Usage:
    python scripts/test_end_to_end_pipeline.py
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import (
    EventCandidate, Topic, Article, ArticleRevision,
    Correction, Category, Source
)
from backend.database import SessionLocal
from backend.agents.signal_intake_agent import SignalIntakeAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.verification_agent import VerificationAgent
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from backend.agents.editorial_coordinator_agent import EditorialCoordinator
from backend.agents.publication_agent import PublicationAgent
from backend.agents.monitoring_agent import MonitoringAgent


class PipelineTestRunner:
    """Orchestrates end-to-end pipeline testing"""

    def __init__(self):
        self.session = SessionLocal()
        self.results = {
            'events_discovered': 0,
            'events_approved': 0,
            'topics_verified': 0,
            'articles_generated': 0,
            'articles_assigned': 0,
            'articles_published': 0,
            'monitoring_active': 0,
            'errors': []
        }

    def print_header(self, text: str):
        """Print formatted section header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)

    def print_step(self, step: str, status: str = "RUNNING"):
        """Print step with status"""
        print(f"\n[{status}] {step}")

    def cleanup_test_data(self):
        """Clean up any existing test data"""
        self.print_header("CLEANUP: Removing existing test data")

        try:
            # Delete in reverse dependency order
            self.session.query(Correction).delete()
            self.session.query(ArticleRevision).delete()
            self.session.query(Article).filter(Article.status != 'published').delete()
            self.session.query(Topic).delete()
            self.session.query(EventCandidate).delete()
            self.session.commit()
            print("✓ Test data cleaned up successfully")
        except Exception as e:
            self.session.rollback()
            print(f"⚠ Cleanup warning: {e}")

    def test_phase_1_signal_intake(self):
        """Test Phase 1: Signal Intake Agent"""
        self.print_header("PHASE 1: Signal Intake Agent - Event Discovery")

        try:
            agent = SignalIntakeAgent()

            # Discover events from all sources
            self.print_step("Discovering events from RSS, Twitter, Reddit, Government feeds")
            results = agent.discover_events()

            # Store results
            self.results['events_discovered'] = results.get('total_discovered', 0)

            # Print detailed breakdown
            print(f"\n📊 Discovery Results:")
            print(f"   Total events discovered: {self.results['events_discovered']}")
            print(f"   RSS feeds: {results.get('rss_count', 0)}")
            print(f"   Twitter: {results.get('twitter_count', 0)}")
            print(f"   Reddit: {results.get('reddit_count', 0)}")
            print(f"   Government: {results.get('government_count', 0)}")
            print(f"   Duplicates removed: {results.get('duplicates_removed', 0)}")

            # Verify events are in database
            db_count = self.session.query(EventCandidate).filter_by(status='discovered').count()
            print(f"\n✓ Verified {db_count} events stored in database")

            if self.results['events_discovered'] < 20:
                self.results['errors'].append("WARNING: Less than 20 events discovered (target: 20-50/day)")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 1 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_2_evaluation(self):
        """Test Phase 2: Evaluation Agent"""
        self.print_header("PHASE 2: Evaluation Agent - Newsworthiness Scoring")

        try:
            agent = EvaluationAgent(self.session)

            # Evaluate all discovered events
            self.print_step("Scoring events on newsworthiness (target: 10-20% approval)")
            results = agent.evaluate_all_discovered_events()

            # Store results
            self.results['events_approved'] = results.get('approved', 0)
            total_evaluated = results.get('evaluated', 0)

            # Calculate approval rate
            approval_rate = (self.results['events_approved'] / total_evaluated * 100) if total_evaluated > 0 else 0

            print(f"\n📊 Evaluation Results:")
            print(f"   Events evaluated: {total_evaluated}")
            print(f"   Events approved: {self.results['events_approved']}")
            print(f"   Events rejected: {results.get('rejected', 0)}")
            print(f"   Approval rate: {approval_rate:.1f}%")

            # Check quality gates
            print(f"\n🔍 Quality Gate: Newsworthiness ≥65/100")
            approved_events = self.session.query(EventCandidate).filter_by(status='approved').all()
            all_passed = True
            for event in approved_events:
                if event.final_newsworthiness_score < 65:
                    print(f"   ✗ Event {event.id} scored {event.final_newsworthiness_score} (below threshold)")
                    all_passed = False

            if all_passed:
                print(f"   ✓ All approved events scored ≥65/100")
            else:
                self.results['errors'].append("Some approved events scored below 65/100 threshold")

            # Check approval rate
            if approval_rate < 10 or approval_rate > 20:
                self.results['errors'].append(f"Approval rate {approval_rate:.1f}% outside target range (10-20%)")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 2 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_3_verification(self):
        """Test Phase 3: Verification Agent"""
        self.print_header("PHASE 3: Verification Agent - Source Verification")

        try:
            agent = VerificationAgent(self.session)

            # Verify all approved topics
            self.print_step("Verifying sources for approved topics (≥3 credible sources)")
            results = agent.verify_all_approved_topics()

            # Store results
            self.results['topics_verified'] = results.get('successful', 0)

            print(f"\n📊 Verification Results:")
            print(f"   Topics processed: {results.get('total', 0)}")
            print(f"   Successfully verified: {self.results['topics_verified']}")
            print(f"   Failed verification: {results.get('failed', 0)}")

            # Check quality gates
            print(f"\n🔍 Quality Gate: ≥3 credible sources OR ≥2 academic citations")
            verified_topics = self.session.query(Topic).filter_by(verification_status='verified').all()
            all_passed = True

            for topic in verified_topics:
                sources_ok = topic.source_count >= 3
                academic_ok = topic.academic_citation_count >= 2

                if not (sources_ok or academic_ok):
                    print(f"   ✗ Topic {topic.id}: {topic.source_count} sources, {topic.academic_citation_count} academic")
                    all_passed = False

            if all_passed:
                print(f"   ✓ All verified topics meet source requirements")
            else:
                self.results['errors'].append("Some topics failed source verification quality gate")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 3 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_4_journalist(self):
        """Test Phase 4: Enhanced Journalist Agent"""
        self.print_header("PHASE 4: Enhanced Journalist Agent - Article Generation")

        try:
            agent = EnhancedJournalistAgent(self.session)

            # Get verified topics (limit to 5 for testing)
            verified_topics = self.session.query(Topic).filter_by(
                verification_status='verified'
            ).limit(5).all()

            self.print_step(f"Generating articles from {len(verified_topics)} verified topics")

            articles_generated = []
            for i, topic in enumerate(verified_topics, 1):
                try:
                    print(f"\n  [{i}/{len(verified_topics)}] Generating article for: {topic.title[:60]}...")
                    article = agent.generate_article(topic.id)
                    articles_generated.append(article)
                    print(f"      ✓ Generated: {article.title[:60]}...")
                except Exception as e:
                    print(f"      ✗ Failed: {e}")
                    self.results['errors'].append(f"Article generation failed for topic {topic.id}: {str(e)}")

            self.results['articles_generated'] = len(articles_generated)

            print(f"\n📊 Article Generation Results:")
            print(f"   Articles generated: {self.results['articles_generated']}")

            # Check quality gates
            print(f"\n🔍 Quality Gates for Generated Articles:")

            # 1. Self-audit check
            print(f"   1. Self-Audit (10-point check):")
            audit_passed = 0
            for article in articles_generated:
                if article.self_audit_passed:
                    audit_passed += 1
            print(f"      ✓ {audit_passed}/{len(articles_generated)} articles passed self-audit")
            if audit_passed != len(articles_generated):
                self.results['errors'].append("Not all articles passed self-audit")

            # 2. Bias scan check
            print(f"   2. Bias Detection Scan:")
            bias_passed = 0
            for article in articles_generated:
                if article.bias_scan_report:
                    import json
                    report = json.loads(article.bias_scan_report)
                    if report.get('overall_score') == 'PASS':
                        bias_passed += 1
            print(f"      ✓ {bias_passed}/{len(articles_generated)} articles passed bias scan")
            if bias_passed != len(articles_generated):
                self.results['errors'].append("Not all articles passed bias scan")

            # 3. Reading level check
            print(f"   3. Reading Level (target: 7.5-8.5):")
            reading_passed = 0
            for article in articles_generated:
                if article.reading_level and 7.5 <= article.reading_level <= 8.5:
                    reading_passed += 1
            print(f"      ✓ {reading_passed}/{len(articles_generated)} articles in target range")
            if reading_passed != len(articles_generated):
                self.results['errors'].append("Not all articles meet reading level requirements")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 4 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_5_editorial(self):
        """Test Phase 5: Editorial Coordinator Agent"""
        self.print_header("PHASE 5: Editorial Coordinator - Assignment & Review")

        try:
            coordinator = EditorialCoordinator(self.session)

            # Get draft articles
            draft_articles = self.session.query(Article).filter_by(status='draft').all()

            self.print_step(f"Assigning {len(draft_articles)} articles to editors")

            test_editor = "test-editor@dailyworker.news"
            assigned = 0

            for article in draft_articles:
                try:
                    coordinator.assign_article(article.id, test_editor)
                    assigned += 1
                    print(f"   ✓ Assigned article {article.id}: {article.title[:50]}...")
                except Exception as e:
                    print(f"   ✗ Failed to assign article {article.id}: {e}")

            self.results['articles_assigned'] = assigned

            print(f"\n📊 Editorial Assignment Results:")
            print(f"   Articles assigned: {self.results['articles_assigned']}")
            print(f"   Assigned editor: {test_editor}")

            # Check assignment status
            under_review = self.session.query(Article).filter_by(status='under_review').count()
            print(f"   Articles under review: {under_review}")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 5 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_6_publication(self):
        """Test Phase 6: Publication Agent"""
        self.print_header("PHASE 6: Publication Agent - Article Publishing")

        try:
            # Manually approve articles for testing
            self.print_step("Simulating editorial approval")
            under_review = self.session.query(Article).filter_by(status='under_review').all()

            for article in under_review:
                article.status = 'approved'
                article.editorial_notes = "Test approval - automated test suite"
            self.session.commit()
            print(f"   ✓ Approved {len(under_review)} articles for publication")

            # Publish approved articles
            agent = PublicationAgent(self.session)
            self.print_step("Publishing approved articles")
            published = agent.publish_approved_articles()

            self.results['articles_published'] = len(published)

            print(f"\n📊 Publication Results:")
            print(f"   Articles published: {self.results['articles_published']}")

            # Verify publication
            for article in published:
                print(f"   ✓ Published: {article.title[:60]}...")
                print(f"      Status: {article.status}")
                print(f"      Published at: {article.published_at}")

            # Check quality gate: only approved articles should be published
            print(f"\n🔍 Quality Gate: Editorial Approval")
            all_published = self.session.query(Article).filter_by(status='published').all()
            unapproved_published = [a for a in all_published if a.assigned_editor is None]

            if len(unapproved_published) > 0:
                print(f"   ✗ {len(unapproved_published)} articles published without editorial review")
                self.results['errors'].append("Some articles published without editorial approval")
            else:
                print(f"   ✓ All published articles had editorial approval")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 6 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_phase_7_monitoring(self):
        """Test Phase 7: Monitoring Agent"""
        self.print_header("PHASE 7: Monitoring Agent - Post-Publication Tracking")

        try:
            agent = MonitoringAgent(self.session)

            # Monitor published articles
            self.print_step("Monitoring published articles (7-day window)")
            results = agent.monitor_published_articles()

            self.results['monitoring_active'] = len(results)

            print(f"\n📊 Monitoring Results:")
            print(f"   Articles being monitored: {self.results['monitoring_active']}")

            # Display monitoring details
            for result in results[:5]:  # Show first 5
                print(f"\n   Article: {result['title'][:50]}...")
                print(f"      Published: {result['published_at']}")
                print(f"      Social mentions: {result.get('social_mentions', 0)}")
                print(f"      Corrections pending: {result.get('corrections_pending', 0)}")

            return True

        except Exception as e:
            self.results['errors'].append(f"Phase 7 failed: {str(e)}")
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def print_final_summary(self):
        """Print final test summary"""
        self.print_header("PIPELINE TEST COMPLETE - FINAL RESULTS")

        print(f"\n📊 Pipeline Statistics:")
        print(f"   Events discovered:     {self.results['events_discovered']}")
        print(f"   Events approved:       {self.results['events_approved']}")
        print(f"   Topics verified:       {self.results['topics_verified']}")
        print(f"   Articles generated:    {self.results['articles_generated']}")
        print(f"   Articles assigned:     {self.results['articles_assigned']}")
        print(f"   Articles published:    {self.results['articles_published']}")
        print(f"   Monitoring active:     {self.results['monitoring_active']}")

        # Calculate conversion funnel
        if self.results['events_discovered'] > 0:
            approval_rate = (self.results['events_approved'] / self.results['events_discovered']) * 100
            print(f"\n📈 Conversion Funnel:")
            print(f"   Discovery → Approval:  {approval_rate:.1f}%")

            if self.results['events_approved'] > 0:
                verification_rate = (self.results['topics_verified'] / self.results['events_approved']) * 100
                print(f"   Approval → Verified:   {verification_rate:.1f}%")

            if self.results['topics_verified'] > 0:
                generation_rate = (self.results['articles_generated'] / self.results['topics_verified']) * 100
                print(f"   Verified → Generated:  {generation_rate:.1f}%")

            if self.results['articles_generated'] > 0:
                publication_rate = (self.results['articles_published'] / self.results['articles_generated']) * 100
                print(f"   Generated → Published: {publication_rate:.1f}%")

        # Print errors/warnings
        if self.results['errors']:
            print(f"\n⚠ Warnings & Errors ({len(self.results['errors'])}):")
            for i, error in enumerate(self.results['errors'], 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n✓ No errors detected")

        # Success criteria
        print(f"\n🎯 Success Criteria:")
        criteria_met = 0
        total_criteria = 5

        # Criterion 1: At least 20 events discovered
        if self.results['events_discovered'] >= 20:
            print(f"   ✓ Discovered ≥20 events")
            criteria_met += 1
        else:
            print(f"   ✗ Discovered <20 events (got {self.results['events_discovered']})")

        # Criterion 2: 10-20% approval rate
        if self.results['events_discovered'] > 0:
            approval_rate = (self.results['events_approved'] / self.results['events_discovered']) * 100
            if 10 <= approval_rate <= 20:
                print(f"   ✓ Approval rate in target range (10-20%)")
                criteria_met += 1
            else:
                print(f"   ✗ Approval rate outside range (got {approval_rate:.1f}%)")

        # Criterion 3: At least 3 articles generated
        if self.results['articles_generated'] >= 3:
            print(f"   ✓ Generated ≥3 articles")
            criteria_met += 1
        else:
            print(f"   ✗ Generated <3 articles (got {self.results['articles_generated']})")

        # Criterion 4: All quality gates passed
        if not any('quality gate' in e.lower() for e in self.results['errors']):
            print(f"   ✓ All quality gates passed")
            criteria_met += 1
        else:
            print(f"   ✗ Some quality gates failed")

        # Criterion 5: Pipeline completed end-to-end
        if self.results['monitoring_active'] > 0:
            print(f"   ✓ Pipeline completed end-to-end")
            criteria_met += 1
        else:
            print(f"   ✗ Pipeline did not complete")

        # Final verdict
        print(f"\n" + "=" * 70)
        if criteria_met == total_criteria:
            print(f"  ✓✓✓ SUCCESS: All {total_criteria} criteria met!")
        else:
            print(f"  ⚠ PARTIAL SUCCESS: {criteria_met}/{total_criteria} criteria met")
        print("=" * 70)

    def run(self):
        """Run the complete end-to-end test"""
        print("\n" + "=" * 70)
        print("  DWnews Automated Journalism Pipeline")
        print("  End-to-End Integration Test")
        print("=" * 70)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Clean up existing test data
        self.cleanup_test_data()

        # Run all phases
        phases = [
            self.test_phase_1_signal_intake,
            self.test_phase_2_evaluation,
            self.test_phase_3_verification,
            self.test_phase_4_journalist,
            self.test_phase_5_editorial,
            self.test_phase_6_publication,
            self.test_phase_7_monitoring
        ]

        for phase in phases:
            success = phase()
            if not success:
                print(f"\n⚠ Phase failed, continuing with next phase...")

        # Print final summary
        self.print_final_summary()

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Close session
        self.session.close()


def main():
    """Main entry point"""
    runner = PipelineTestRunner()
    runner.run()


if __name__ == "__main__":
    main()
