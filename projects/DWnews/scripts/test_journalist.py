#!/usr/bin/env python3
"""
Test Enhanced Journalist Agent - Article Generation from Verified Topics
Phase 6.5 Testing Script
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent))

from backend.database import SessionLocal
from database.models import Topic, Article
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_section(text: str):
    """Print formatted section"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)


def test_journalist_agent():
    """Test journalist agent with verified topics"""
    print_header("Enhanced Journalist Agent - Phase 6.5 Testing")

    # Create database session
    db = SessionLocal()

    try:
        # 1. Find verified topics
        print_section("Finding Verified Topics")

        verified_topics = db.query(Topic).filter_by(
            verification_status='verified'
        ).all()

        if not verified_topics:
            print("\n✗ No verified topics found in database.")
            print("  Run verification agent first (Phase 6.4) to create verified topics.")
            return

        print(f"\n✓ Found {len(verified_topics)} verified topics")

        for topic in verified_topics:
            print(f"  - Topic {topic.id}: {topic.title}")

        # 2. Initialize journalist agent
        print_section("Initializing Enhanced Journalist Agent")

        agent = EnhancedJournalistAgent(db)

        print("\n✓ Journalist agent initialized")
        print("  Modules loaded:")
        print("    - Self-Audit (10-point checklist)")
        print("    - Bias Detector (hallucination & propaganda)")
        print("    - Readability Checker (Flesch-Kincaid)")
        print("    - Attribution Engine (source plan)")

        # 3. Test article generation on each verified topic
        results = []

        for topic in verified_topics[:3]:  # Test first 3 topics
            print_section(f"Generating Article for Topic {topic.id}")
            print(f"\nTopic: {topic.title}")

            # Check if article already exists
            existing_article = db.query(Article).filter_by(
                id=topic.article_id
            ).first() if topic.article_id else None

            if existing_article:
                print(f"\n✓ Article already exists (ID: {existing_article.id})")
                article = existing_article
            else:
                print("\nGenerating new article...")

                # Generate article
                article = agent.generate_article(topic.id)

                if not article:
                    print(f"\n✗ Article generation failed for topic {topic.id}")
                    results.append({
                        "topic_id": topic.id,
                        "success": False,
                        "reason": "Generation failed"
                    })
                    continue

                print(f"\n✓ Article generated successfully (ID: {article.id})")

            # Display article details
            print(f"\nArticle Details:")
            print(f"  Title: {article.title}")
            print(f"  Word Count: {article.word_count}")
            print(f"  Reading Level: {article.reading_level:.1f} (target: 7.5-8.5)")
            print(f"  Self-Audit Passed: {article.self_audit_passed}")
            print(f"  Status: {article.status}")

            # Parse and display bias scan report
            if article.bias_scan_report:
                try:
                    bias_report = json.loads(article.bias_scan_report)
                    print(f"\nBias Scan Report:")
                    print(f"  Overall Score: {bias_report.get('overall_score', 'N/A')}")
                    print(f"  Hallucination Detected: {bias_report.get('hallucination_detected', False)}")
                    print(f"  Propaganda Flags: {len(bias_report.get('propaganda_flags', []))}")
                    print(f"  Bias Indicators: {len(bias_report.get('bias_indicators', []))}")
                    print(f"  Warnings: {len(bias_report.get('warnings', []))}")

                    if bias_report.get('hallucination_details'):
                        print(f"\n  Hallucination Details:")
                        for detail in bias_report['hallucination_details'][:3]:
                            print(f"    - {detail}")

                    if bias_report.get('propaganda_flags'):
                        print(f"\n  Propaganda Flags:")
                        for flag in bias_report['propaganda_flags'][:3]:
                            print(f"    - {flag}")
                except json.JSONDecodeError:
                    print(f"\n  (Invalid bias scan report JSON)")

            # Display article excerpt
            print(f"\nArticle Excerpt:")
            excerpt = article.body[:300] if article.body else ""
            print(f"  {excerpt}...")

            # Record result
            results.append({
                "topic_id": topic.id,
                "article_id": article.id,
                "title": article.title,
                "word_count": article.word_count,
                "reading_level": article.reading_level,
                "self_audit_passed": article.self_audit_passed,
                "bias_score": json.loads(article.bias_scan_report).get('overall_score') if article.bias_scan_report else None,
                "success": True
            })

        # 4. Display summary
        print_section("Test Results Summary")

        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]

        print(f"\n✓ Articles Generated: {len(successful)}/{len(results)}")

        if successful:
            print(f"\nSuccessful Articles:")
            for result in successful:
                print(f"  - Article {result['article_id']}: {result['title']}")
                print(f"    Word Count: {result['word_count']}, Reading Level: {result['reading_level']:.1f}")
                print(f"    Self-Audit: {'PASS' if result['self_audit_passed'] else 'FAIL'}")
                print(f"    Bias Scan: {result['bias_score']}")

        if failed:
            print(f"\nFailed Articles:")
            for result in failed:
                print(f"  - Topic {result['topic_id']}: {result.get('reason', 'Unknown error')}")

        # 5. Validate quality standards
        print_section("Quality Standards Validation")

        self_audit_pass_rate = (
            sum(1 for r in successful if r.get("self_audit_passed")) / len(successful) * 100
            if successful else 0
        )

        reading_level_in_range = sum(
            1 for r in successful
            if r.get("reading_level") and 7.5 <= r["reading_level"] <= 8.5
        )

        bias_scan_pass = sum(
            1 for r in successful
            if r.get("bias_score") == "PASS"
        )

        print(f"\nQuality Metrics:")
        print(f"  Self-Audit Pass Rate: {self_audit_pass_rate:.0f}% (target: 100%)")
        print(f"  Reading Level Compliance: {reading_level_in_range}/{len(successful)} (target range: 7.5-8.5)")
        print(f"  Bias Scan Pass: {bias_scan_pass}/{len(successful)}")

        # Overall success
        overall_success = (
            self_audit_pass_rate == 100 and
            reading_level_in_range == len(successful) and
            bias_scan_pass == len(successful)
        )

        print_section("Final Result")

        if overall_success:
            print("\n✓ ALL TESTS PASSED")
            print("  Enhanced Journalist Agent is working correctly")
            print("  All articles meet quality standards")
        else:
            print("\n⚠ SOME TESTS FAILED")
            print("  Review failed criteria above")

            if self_audit_pass_rate < 100:
                print(f"  - Self-audit pass rate below 100%: {self_audit_pass_rate:.0f}%")

            if reading_level_in_range < len(successful):
                print(f"  - Reading level out of range: {len(successful) - reading_level_in_range} articles")

            if bias_scan_pass < len(successful):
                print(f"  - Bias scan failures: {len(successful) - bias_scan_pass} articles")

    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        print(f"\n✗ Test failed with error: {e}")

    finally:
        db.close()


def show_article_details(article_id: int):
    """Show detailed information about a specific article"""
    db = SessionLocal()

    try:
        article = db.query(Article).filter_by(id=article_id).first()

        if not article:
            print(f"✗ Article {article_id} not found")
            return

        print_header(f"Article {article_id} Details")

        print(f"\nTitle: {article.title}")
        print(f"Slug: {article.slug}")
        print(f"Author: {article.author}")
        print(f"Status: {article.status}")
        print(f"Category: {article.category.name if article.category else 'N/A'}")

        print(f"\nMetrics:")
        print(f"  Word Count: {article.word_count}")
        print(f"  Reading Level: {article.reading_level:.1f}")
        print(f"  Self-Audit Passed: {article.self_audit_passed}")

        if article.bias_scan_report:
            bias_report = json.loads(article.bias_scan_report)
            print(f"\nBias Scan Report:")
            print(json.dumps(bias_report, indent=2))

        print(f"\nBody:")
        print(article.body)

        if article.why_this_matters:
            print(f"\nWhy This Matters:")
            print(article.why_this_matters)

        if article.what_you_can_do:
            print(f"\nWhat You Can Do:")
            print(article.what_you_can_do)

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Enhanced Journalist Agent")
    parser.add_argument(
        "--article",
        type=int,
        help="Show detailed information about specific article ID"
    )

    args = parser.parse_args()

    if args.article:
        show_article_details(args.article)
    else:
        test_journalist_agent()
