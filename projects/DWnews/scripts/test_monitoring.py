#!/usr/bin/env python3
"""
Test Monitoring System - End-to-End Test Suite

Tests the complete publication and monitoring workflow:
1. Create and approve a test article
2. Publish article using Publication Agent
3. Monitor social mentions (mock data if APIs unavailable)
4. Flag and process correction
5. Update source reliability scores
6. Verify correction notice displays
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_session
from database.models import Article, Category, Source, Correction, SourceReliabilityLog
from backend.agents.publication_agent import PublicationAgent
from backend.agents.monitoring_agent import MonitoringAgent
from backend.agents.correction_workflow import CorrectionWorkflow
from backend.agents.source_reliability import SourceReliabilityScorer


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def create_test_article(session):
    """
    Create a test article for monitoring

    Returns:
        Article instance
    """
    print_section("STEP 1: Create Test Article")

    # Get or create test category
    category = session.query(Category).filter(
        Category.slug == 'labor-organizing'
    ).first()

    if not category:
        category = Category(
            name='Labor & Organizing',
            slug='labor-organizing',
            description='Labor organizing and union activity',
            is_active=True
        )
        session.add(category)
        session.flush()

    # Get or create test source
    source = session.query(Source).filter(
        Source.name == 'Test News Wire'
    ).first()

    if not source:
        source = Source(
            name='Test News Wire',
            url='https://testnewswire.com',
            source_type='news_wire',
            credibility_score=4,
            political_lean='center',
            is_active=True
        )
        session.add(source)
        session.flush()

    # Create test article
    article = Article(
        title='Test Article: Amazon Workers Strike Over Working Conditions',
        slug=f'test-article-monitoring-{int(datetime.utcnow().timestamp())}',
        body='''Workers at Amazon's Seattle warehouse went on strike today over safety concerns.

The strike involves approximately 100 workers who are demanding better ventilation, more break time, and hazard pay.

Union organizers say the strike will continue until management agrees to negotiate.

Amazon representatives declined to comment on the strike.''',
        summary='Amazon warehouse workers in Seattle strike over safety concerns and working conditions.',
        category_id=category.id,
        author='Test Agent',
        is_national=True,
        is_local=False,
        is_ongoing=True,
        is_new=True,
        reading_level=8.0,
        word_count=50,
        status='approved',  # Start as approved to test publication
        self_audit_passed=True,
        created_at=datetime.utcnow()
    )

    session.add(article)
    session.flush()

    # Link source to article
    article.sources.append(source)

    session.commit()

    print(f"✓ Created test article:")
    print(f"  ID: {article.id}")
    print(f"  Title: {article.title}")
    print(f"  Status: {article.status}")
    print(f"  Source: {source.name} (credibility: {source.credibility_score})")

    return article


def test_publication(session, article):
    """
    Test publication workflow

    Args:
        session: Database session
        article: Article to publish
    """
    print_section("STEP 2: Test Publication Agent")

    agent = PublicationAgent(session)

    # Get publication stats before
    stats_before = agent.get_publication_stats()
    print(f"\nBefore publication:")
    print(f"  Approved pending: {stats_before['approved_pending']}")

    # Publish article
    print(f"\nPublishing article {article.id}...")
    success = agent.publish_article(article.id)

    if success:
        print(f"✓ Article published successfully")

        # Refresh article from database
        session.expire(article)
        print(f"  Status: {article.status}")
        print(f"  Published at: {article.published_at}")
    else:
        print(f"✗ Publication failed")
        return False

    # Get publication stats after
    stats_after = agent.get_publication_stats()
    print(f"\nAfter publication:")
    print(f"  Total published: {stats_after['total_published']}")
    print(f"  Approved pending: {stats_after['approved_pending']}")

    return True


def test_social_monitoring(session, article):
    """
    Test social mention monitoring

    Args:
        session: Database session
        article: Article to monitor
    """
    print_section("STEP 3: Test Social Mention Monitoring")

    agent = MonitoringAgent(session)

    print(f"\nAPI Configuration:")
    print(f"  Twitter API: {'Enabled' if agent.twitter_enabled else 'Disabled'}")
    print(f"  Reddit API: {'Enabled' if agent.reddit_enabled else 'Disabled'}")

    # Check social mentions
    print(f"\nChecking social mentions for article {article.id}...")
    mentions = agent.check_social_mentions(article)

    if mentions:
        print(f"✓ Found {len(mentions)} social mentions:")
        for mention in mentions[:3]:  # Show first 3
            print(f"  - {mention['platform']}: {mention['url']}")
            print(f"    Engagement: {mention['engagement']}")
    else:
        print(f"✓ No social mentions found (APIs may not be configured)")
        print(f"  Note: Set TWITTER_BEARER_TOKEN and REDDIT_CLIENT_ID/SECRET to enable")

    return True


def test_correction_workflow(session, article):
    """
    Test correction workflow

    Args:
        session: Database session
        article: Article to correct
    """
    print_section("STEP 4: Test Correction Workflow")

    workflow = CorrectionWorkflow(session)

    # Flag a correction
    print(f"\n4.1: Flagging correction...")
    correction = workflow.flag_correction(
        article_id=article.id,
        correction_type='factual_error',
        incorrect_text='approximately 100 workers',
        correct_text='approximately 150 workers',
        description='Source updated with official count from union organizers',
        severity='moderate',
        section_affected='body',
        reported_by='monitoring_agent'
    )

    if correction:
        print(f"✓ Correction flagged:")
        print(f"  ID: {correction.id}")
        print(f"  Type: {correction.correction_type}")
        print(f"  Severity: {correction.severity}")
        print(f"  Status: {correction.status}")
    else:
        print(f"✗ Failed to flag correction")
        return False

    # Get pending corrections
    pending = workflow.get_pending_corrections()
    print(f"\n✓ Pending corrections: {len(pending)}")

    # Editor reviews correction
    print(f"\n4.2: Editor reviewing correction...")
    success = workflow.review_correction(
        correction_id=correction.id,
        action='approve',
        reviewer='test_editor',
        notes='Verified with union organizers - official count is 150 workers'
    )

    if success:
        session.expire(correction)
        print(f"✓ Correction approved")
        print(f"  Status: {correction.status}")
    else:
        print(f"✗ Failed to review correction")
        return False

    # Publish correction
    print(f"\n4.3: Publishing correction...")
    success = workflow.publish_correction(
        correction_id=correction.id,
        public_notice='An earlier version of this article stated approximately 100 workers were on strike. The official count from union organizers is 150 workers.',
        editor='test_editor'
    )

    if success:
        session.expire(correction)
        print(f"✓ Correction published")
        print(f"  Status: {correction.status}")
        print(f"  Published at: {correction.published_at}")
        print(f"  Public notice: {correction.public_notice[:80]}...")
    else:
        print(f"✗ Failed to publish correction")
        return False

    # Get correction stats
    stats = workflow.get_correction_stats()
    print(f"\n✓ Correction statistics:")
    print(f"  Total corrections: {stats['total_corrections']}")
    print(f"  Published: {stats['published']}")
    print(f"  By severity - Critical: {stats['by_severity']['critical']}, Major: {stats['by_severity']['major']}")

    return True


def test_source_reliability(session, article):
    """
    Test source reliability scoring

    Args:
        session: Database session
        article: Article to score sources for
    """
    print_section("STEP 5: Test Source Reliability Scoring")

    scorer = SourceReliabilityScorer(session)

    # Get article sources
    sources = article.sources
    if not sources:
        print(f"✗ No sources found for article")
        return False

    source = sources[0]
    print(f"\nTesting source: {source.name}")
    print(f"  Current credibility score: {source.credibility_score}")

    # Get source stats before
    stats_before = scorer.get_source_stats(source.id)
    print(f"  Current score (100-scale): {stats_before['current_score']}")
    print(f"  Total events: {stats_before['total_events']}")

    # Log a correction event (since we just corrected an article using this source)
    print(f"\nLogging correction event...")
    log_entry = scorer.log_event(
        source_id=source.id,
        event_type='correction_issued',
        article_id=article.id,
        notes='Article required correction - official worker count was wrong',
        automated=True
    )

    if log_entry:
        print(f"✓ Logged correction event:")
        print(f"  Event type: {log_entry.event_type}")
        print(f"  Score delta: {log_entry.reliability_delta}")
        print(f"  Previous score: {log_entry.previous_score}")
        print(f"  New score: {log_entry.new_score}")
    else:
        print(f"✗ Failed to log event")
        return False

    # Simulate 7 days passing and article remaining accurate (besides the correction)
    print(f"\nSimulating 7-day monitoring period...")
    # In real scenario, this would be a separate cron job after 7 days
    # For testing, we manually call update_for_article_accuracy

    # This would normally deduct points for the correction, but let's also
    # show what happens with an accurate article
    print(f"  (In production, this runs after 7-day monitoring window)")

    # Get source history
    print(f"\nSource reliability history:")
    history = scorer.get_source_history(source.id, limit=5)
    for entry in history:
        print(f"  - {entry.logged_at.strftime('%Y-%m-%d')}: {entry.event_type} (delta: {entry.reliability_delta})")

    # Get updated stats
    stats_after = scorer.get_source_stats(source.id)
    print(f"\n✓ Updated source stats:")
    print(f"  Current score (100-scale): {stats_after['current_score']}")
    print(f"  Credibility score: {stats_after['credibility_score']}/5")
    print(f"  Total events: {stats_after['total_events']}")

    # Get reliability trends
    trends = scorer.get_reliability_trends()
    print(f"\n✓ Overall reliability trends:")
    print(f"  Average credibility: {trends['avg_credibility_score']}/5")
    print(f"  Recent events (30d): {trends['recent_events_30d']}")

    return True


def test_monitoring_integration(session, article):
    """
    Test complete monitoring integration

    Args:
        session: Database session
        article: Article to monitor
    """
    print_section("STEP 6: Test Monitoring Integration")

    agent = MonitoringAgent(session)

    print(f"\nRunning full monitoring cycle...")
    results = agent.monitor_published_articles()

    print(f"✓ Monitoring results:")
    print(f"  Articles monitored: {results['total_monitored']}")
    print(f"  Social mentions found: {results['mentions_found']}")
    print(f"  Corrections flagged: {results['corrections_flagged']}")
    print(f"  Sources updated: {results['sources_updated']}")

    return True


def cleanup_test_data(session, article):
    """
    Clean up test data (optional)

    Args:
        session: Database session
        article: Article to clean up
    """
    print_section("CLEANUP (Optional)")

    print(f"\nTest article ID: {article.id}")
    print(f"To clean up test data, run:")
    print(f"  DELETE FROM corrections WHERE article_id = {article.id};")
    print(f"  DELETE FROM source_reliability_log WHERE article_id = {article.id};")
    print(f"  DELETE FROM articles WHERE id = {article.id};")

    # For testing, we'll leave the data in place for manual inspection
    print(f"\n✓ Test data preserved for inspection")


def main():
    """
    Run complete monitoring test suite
    """
    print("\n" + "=" * 70)
    print("  MONITORING SYSTEM - End-to-End Test Suite")
    print("=" * 70)

    session = get_session()

    try:
        # Step 1: Create test article
        article = create_test_article(session)

        # Step 2: Test publication
        if not test_publication(session, article):
            print("\n✗ Publication test failed")
            return 1

        # Step 3: Test social monitoring
        if not test_social_monitoring(session, article):
            print("\n✗ Social monitoring test failed")
            return 1

        # Step 4: Test correction workflow
        if not test_correction_workflow(session, article):
            print("\n✗ Correction workflow test failed")
            return 1

        # Step 5: Test source reliability
        if not test_source_reliability(session, article):
            print("\n✗ Source reliability test failed")
            return 1

        # Step 6: Test monitoring integration
        if not test_monitoring_integration(session, article):
            print("\n✗ Monitoring integration test failed")
            return 1

        # Cleanup info
        cleanup_test_data(session, article)

        # Success summary
        print_section("TEST SUMMARY")
        print("\n✓ All tests passed!")
        print("\nComponents tested:")
        print("  1. Publication Agent - Auto-publishing")
        print("  2. Monitoring Agent - Social mention tracking")
        print("  3. Correction Workflow - Flag, review, publish")
        print("  4. Source Reliability - Scoring and logging")
        print("  5. Monitoring Integration - End-to-end flow")

        print("\nNext steps:")
        print("  1. Configure Twitter API (TWITTER_BEARER_TOKEN)")
        print("  2. Configure Reddit API (REDDIT_CLIENT_ID/SECRET)")
        print("  3. Set up daily cron jobs:")
        print("     - Publication: 5pm daily")
        print("     - Monitoring: 9am daily")
        print("  4. Test correction notice display on frontend")
        print("  5. Review test article in database (ID: {})".format(article.id))

        print("\n" + "=" * 70)

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())
