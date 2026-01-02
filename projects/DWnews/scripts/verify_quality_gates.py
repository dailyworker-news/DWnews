#!/usr/bin/env python3
"""
Quality Gates Verification Script

Verifies that all quality gates are enforced throughout the automated journalism pipeline:

1. Newsworthiness: All approved events scored ≥65/100
2. Source Verification: All verified topics have ≥3 credible sources OR ≥2 academic citations
3. Self-Audit: All generated articles passed 10-point self-audit
4. Bias Detection: All articles have bias_scan_report with overall_score='PASS'
5. Reading Level: All articles have Flesch-Kincaid score 7.5-8.5
6. Editorial Approval: Only approved articles are published

Usage:
    python scripts/verify_quality_gates.py [--verbose]
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.models import EventCandidate, Topic, Article
from backend.database import SessionLocal


class QualityGateVerifier:
    """Verifies quality gates across the pipeline"""

    def __init__(self, verbose: bool = False):
        self.session = SessionLocal()
        self.verbose = verbose
        self.results = {
            'newsworthiness': {'passed': 0, 'failed': 0, 'issues': []},
            'source_verification': {'passed': 0, 'failed': 0, 'issues': []},
            'self_audit': {'passed': 0, 'failed': 0, 'issues': []},
            'bias_detection': {'passed': 0, 'failed': 0, 'issues': []},
            'reading_level': {'passed': 0, 'failed': 0, 'issues': []},
            'editorial_approval': {'passed': 0, 'failed': 0, 'issues': []}
        }

    def print_header(self, text: str):
        """Print formatted section header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)

    def print_gate_result(self, gate_name: str, passed: int, failed: int, issues: List[str]):
        """Print results for a quality gate"""
        total = passed + failed
        pass_rate = (passed / total * 100) if total > 0 else 0

        status = "✓ PASS" if failed == 0 else "✗ FAIL"
        print(f"\n{status} - {gate_name}")
        print(f"   Checked: {total}")
        print(f"   Passed:  {passed} ({pass_rate:.1f}%)")
        print(f"   Failed:  {failed}")

        if issues and (self.verbose or failed > 0):
            print(f"\n   Issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"     • {issue}")
            if len(issues) > 10:
                print(f"     ... and {len(issues) - 10} more")

    def verify_gate_1_newsworthiness(self):
        """Gate 1: Newsworthiness ≥65/100"""
        self.print_header("GATE 1: Newsworthiness Scoring (≥65/100)")

        print("🔍 Checking approved events...")

        # Get all approved events
        approved_events = self.session.query(EventCandidate).filter_by(
            status='approved'
        ).all()

        print(f"   Found {len(approved_events)} approved events")

        for event in approved_events:
            if event.final_newsworthiness_score is None:
                self.results['newsworthiness']['failed'] += 1
                self.results['newsworthiness']['issues'].append(
                    f"Event {event.id}: No score recorded"
                )
            elif event.final_newsworthiness_score < 65:
                self.results['newsworthiness']['failed'] += 1
                self.results['newsworthiness']['issues'].append(
                    f"Event {event.id}: Score {event.final_newsworthiness_score:.1f} < 65 ('{event.title[:50]}...')"
                )
            else:
                self.results['newsworthiness']['passed'] += 1

        self.print_gate_result(
            "Newsworthiness ≥65/100",
            self.results['newsworthiness']['passed'],
            self.results['newsworthiness']['failed'],
            self.results['newsworthiness']['issues']
        )

    def verify_gate_2_source_verification(self):
        """Gate 2: ≥3 credible sources OR ≥2 academic citations"""
        self.print_header("GATE 2: Source Verification (≥3 sources OR ≥2 academic)")

        print("🔍 Checking verified topics...")

        # Get all verified topics
        verified_topics = self.session.query(Topic).filter_by(
            verification_status='verified'
        ).all()

        print(f"   Found {len(verified_topics)} verified topics")

        for topic in verified_topics:
            sources_ok = topic.source_count >= 3
            academic_ok = topic.academic_citation_count >= 2

            if not (sources_ok or academic_ok):
                self.results['source_verification']['failed'] += 1
                self.results['source_verification']['issues'].append(
                    f"Topic {topic.id}: {topic.source_count} sources, {topic.academic_citation_count} academic ('{topic.title[:50]}...')"
                )
            else:
                self.results['source_verification']['passed'] += 1

                if self.verbose:
                    reason = "sources" if sources_ok else "academic citations"
                    print(f"   ✓ Topic {topic.id}: Verified via {reason}")

        self.print_gate_result(
            "Source Verification",
            self.results['source_verification']['passed'],
            self.results['source_verification']['failed'],
            self.results['source_verification']['issues']
        )

    def verify_gate_3_self_audit(self):
        """Gate 3: Self-audit passed"""
        self.print_header("GATE 3: Self-Audit (10-point check)")

        print("🔍 Checking generated articles...")

        # Get all articles (exclude very old ones)
        recent_date = datetime.now() - timedelta(days=30)
        articles = self.session.query(Article).filter(
            Article.created_at >= recent_date
        ).all()

        print(f"   Found {len(articles)} recent articles")

        for article in articles:
            if not article.self_audit_passed:
                self.results['self_audit']['failed'] += 1
                self.results['self_audit']['issues'].append(
                    f"Article {article.id}: Self-audit not passed ('{article.title[:50]}...')"
                )
            else:
                self.results['self_audit']['passed'] += 1

        self.print_gate_result(
            "Self-Audit",
            self.results['self_audit']['passed'],
            self.results['self_audit']['failed'],
            self.results['self_audit']['issues']
        )

    def verify_gate_4_bias_detection(self):
        """Gate 4: Bias scan passed"""
        self.print_header("GATE 4: Bias Detection Scan")

        print("🔍 Checking bias scan reports...")

        # Get all articles with bias scans
        recent_date = datetime.now() - timedelta(days=30)
        articles = self.session.query(Article).filter(
            Article.created_at >= recent_date,
            Article.bias_scan_report.isnot(None)
        ).all()

        print(f"   Found {len(articles)} articles with bias scans")

        for article in articles:
            try:
                report = json.loads(article.bias_scan_report)
                overall_score = report.get('overall_score', 'UNKNOWN')

                if overall_score == 'PASS':
                    self.results['bias_detection']['passed'] += 1
                else:
                    self.results['bias_detection']['failed'] += 1
                    self.results['bias_detection']['issues'].append(
                        f"Article {article.id}: Bias scan {overall_score} ('{article.title[:50]}...')"
                    )

            except json.JSONDecodeError:
                self.results['bias_detection']['failed'] += 1
                self.results['bias_detection']['issues'].append(
                    f"Article {article.id}: Invalid bias scan report"
                )

        # Check for articles without bias scans
        articles_no_scan = self.session.query(Article).filter(
            Article.created_at >= recent_date,
            Article.bias_scan_report.is_(None),
            Article.status.in_(['draft', 'pending_review', 'under_review', 'approved', 'published'])
        ).count()

        if articles_no_scan > 0:
            self.results['bias_detection']['issues'].append(
                f"{articles_no_scan} articles missing bias scan report"
            )

        self.print_gate_result(
            "Bias Detection",
            self.results['bias_detection']['passed'],
            self.results['bias_detection']['failed'],
            self.results['bias_detection']['issues']
        )

    def verify_gate_5_reading_level(self):
        """Gate 5: Reading level 7.5-8.5"""
        self.print_header("GATE 5: Reading Level (7.5-8.5)")

        print("🔍 Checking reading levels...")

        # Get all recent articles
        recent_date = datetime.now() - timedelta(days=30)
        articles = self.session.query(Article).filter(
            Article.created_at >= recent_date,
            Article.reading_level.isnot(None)
        ).all()

        print(f"   Found {len(articles)} articles with reading levels")

        for article in articles:
            if 7.5 <= article.reading_level <= 8.5:
                self.results['reading_level']['passed'] += 1
            else:
                self.results['reading_level']['failed'] += 1
                self.results['reading_level']['issues'].append(
                    f"Article {article.id}: Reading level {article.reading_level:.2f} outside range ('{article.title[:50]}...')"
                )

        # Check for articles without reading level
        articles_no_level = self.session.query(Article).filter(
            Article.created_at >= recent_date,
            Article.reading_level.is_(None),
            Article.status.in_(['draft', 'pending_review', 'under_review', 'approved', 'published'])
        ).count()

        if articles_no_level > 0:
            self.results['reading_level']['issues'].append(
                f"{articles_no_level} articles missing reading level"
            )

        self.print_gate_result(
            "Reading Level",
            self.results['reading_level']['passed'],
            self.results['reading_level']['failed'],
            self.results['reading_level']['issues']
        )

    def verify_gate_6_editorial_approval(self):
        """Gate 6: Editorial approval required for publication"""
        self.print_header("GATE 6: Editorial Approval (for published articles)")

        print("🔍 Checking published articles...")

        # Get all published articles
        recent_date = datetime.now() - timedelta(days=30)
        published_articles = self.session.query(Article).filter(
            Article.status == 'published',
            Article.published_at >= recent_date
        ).all()

        print(f"   Found {len(published_articles)} recently published articles")

        for article in published_articles:
            # Check if article had editorial review
            had_editor = article.assigned_editor is not None
            had_review_deadline = article.review_deadline is not None

            if not (had_editor or had_review_deadline):
                self.results['editorial_approval']['failed'] += 1
                self.results['editorial_approval']['issues'].append(
                    f"Article {article.id}: Published without editorial review ('{article.title[:50]}...')"
                )
            else:
                self.results['editorial_approval']['passed'] += 1

        self.print_gate_result(
            "Editorial Approval",
            self.results['editorial_approval']['passed'],
            self.results['editorial_approval']['failed'],
            self.results['editorial_approval']['issues']
        )

    def generate_summary(self):
        """Generate overall summary"""
        self.print_header("QUALITY GATES SUMMARY")

        print("\n📊 Gate-by-Gate Results:\n")

        gates = [
            ('Newsworthiness', 'newsworthiness'),
            ('Source Verification', 'source_verification'),
            ('Self-Audit', 'self_audit'),
            ('Bias Detection', 'bias_detection'),
            ('Reading Level', 'reading_level'),
            ('Editorial Approval', 'editorial_approval')
        ]

        all_passed = True
        total_checked = 0
        total_passed = 0
        total_failed = 0

        for gate_name, gate_key in gates:
            passed = self.results[gate_key]['passed']
            failed = self.results[gate_key]['failed']
            total = passed + failed

            if total > 0:
                pass_rate = (passed / total) * 100
                status = "✓" if failed == 0 else "✗"
                print(f"{status} {gate_name:25s}: {passed}/{total} ({pass_rate:5.1f}%)")

                if failed > 0:
                    all_passed = False

                total_checked += total
                total_passed += passed
                total_failed += failed
            else:
                print(f"⊘ {gate_name:25s}: No items checked")

        # Overall statistics
        print(f"\n📈 Overall Statistics:")
        print(f"   Total checks:  {total_checked}")
        print(f"   Passed:        {total_passed}")
        print(f"   Failed:        {total_failed}")

        if total_checked > 0:
            overall_pass_rate = (total_passed / total_checked) * 100
            print(f"   Pass rate:     {overall_pass_rate:.1f}%")

        # Final verdict
        print("\n" + "=" * 70)
        if all_passed and total_checked > 0:
            print("  ✓✓✓ ALL QUALITY GATES PASSING")
            print("  Pipeline is enforcing quality standards correctly")
        elif total_failed == 0 and total_checked == 0:
            print("  ⚠ NO DATA TO VERIFY")
            print("  Run the pipeline to generate data for verification")
        else:
            print("  ✗✗✗ SOME QUALITY GATES FAILING")
            print(f"  {total_failed} quality issues detected - review required")
        print("=" * 70)

        return all_passed and total_checked > 0

    def run(self):
        """Run all quality gate verifications"""
        print("\n" + "=" * 70)
        print("  DWnews Automated Journalism Pipeline")
        print("  Quality Gates Verification")
        print("=" * 70)
        print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if self.verbose:
            print("\n[Verbose mode enabled - showing detailed output]")

        # Run all verifications
        try:
            self.verify_gate_1_newsworthiness()
            self.verify_gate_2_source_verification()
            self.verify_gate_3_self_audit()
            self.verify_gate_4_bias_detection()
            self.verify_gate_5_reading_level()
            self.verify_gate_6_editorial_approval()

            # Generate summary
            success = self.generate_summary()

            print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            return success

        except Exception as e:
            print(f"\n✗ ERROR: Verification failed - {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.session.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Verify quality gates in journalism pipeline')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    args = parser.parse_args()

    verifier = QualityGateVerifier(verbose=args.verbose)
    success = verifier.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
