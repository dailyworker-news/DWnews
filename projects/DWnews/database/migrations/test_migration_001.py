#!/usr/bin/env python3
"""
Test Script for Migration 001
Verifies that all new tables, columns, and views were created correctly
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.models import (
    Base, EventCandidate, ArticleRevision, Correction,
    SourceReliabilityLog, Article, Topic, Source
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = Path(__file__).parent.parent.parent / 'dwnews.db'


def test_migration():
    """Test that migration 001 was applied correctly"""

    print("=" * 80)
    print("Testing Migration 001")
    print("=" * 80)
    print()

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please run migration first: python database/migrations/run_migration_001.py")
        sys.exit(1)

    # Test 1: Raw SQL verification
    print("Test 1: Verifying tables exist (raw SQL)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    expected_tables = [
        'event_candidates',
        'article_revisions',
        'corrections',
        'source_reliability_log'
    ]

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)
    all_tables = [row[0] for row in cursor.fetchall()]

    for table in expected_tables:
        if table in all_tables:
            print(f"  ✓ {table} exists")
        else:
            print(f"  ✗ {table} MISSING!")
            conn.close()
            sys.exit(1)

    print()

    # Test 2: Verify new columns in articles
    print("Test 2: Verifying new columns in 'articles' table...")
    cursor.execute("PRAGMA table_info(articles)")
    article_columns = [col[1] for col in cursor.fetchall()]

    expected_article_cols = [
        'bias_scan_report',
        'self_audit_passed',
        'editorial_notes',
        'assigned_editor',
        'review_deadline'
    ]

    for col in expected_article_cols:
        if col in article_columns:
            print(f"  ✓ {col} exists")
        else:
            print(f"  ✗ {col} MISSING!")
            conn.close()
            sys.exit(1)

    print()

    # Test 3: Verify new columns in topics
    print("Test 3: Verifying new columns in 'topics' table...")
    cursor.execute("PRAGMA table_info(topics)")
    topic_columns = [col[1] for col in cursor.fetchall()]

    expected_topic_cols = [
        'verified_facts',
        'source_plan',
        'verification_status'
    ]

    for col in expected_topic_cols:
        if col in topic_columns:
            print(f"  ✓ {col} exists")
        else:
            print(f"  ✗ {col} MISSING!")
            conn.close()
            sys.exit(1)

    print()

    # Test 4: Verify views
    print("Test 4: Verifying views...")
    expected_views = [
        'approved_event_candidates',
        'articles_pending_review',
        'article_revision_history',
        'published_corrections',
        'source_reliability_trends'
    ]

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='view'
        ORDER BY name
    """)
    all_views = [row[0] for row in cursor.fetchall()]

    for view in expected_views:
        if view in all_views:
            print(f"  ✓ {view} exists")
        else:
            print(f"  ✗ {view} MISSING!")
            conn.close()
            sys.exit(1)

    conn.close()
    print()

    # Test 5: SQLAlchemy ORM verification
    print("Test 5: Testing SQLAlchemy ORM models...")
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Test EventCandidate model
        print("  Testing EventCandidate model...")
        test_event = EventCandidate(
            title="Test Labor Strike at Amazon Warehouse",
            description="Workers walk out over safety concerns",
            discovered_from="RSS: Reuters Labor Feed",
            worker_impact_score=8.5,
            timeliness_score=9.0,
            verifiability_score=7.0,
            final_newsworthiness_score=8.2,
            status='discovered'
        )
        session.add(test_event)
        session.commit()
        print(f"    ✓ Created EventCandidate (ID: {test_event.id})")

        # Test ArticleRevision model (need an article first)
        print("  Testing ArticleRevision model...")
        article = session.query(Article).first()
        if article:
            test_revision = ArticleRevision(
                article_id=article.id,
                revision_number=1,
                revised_by="test-agent",
                revision_type="draft",
                title_after=article.title,
                body_after=article.body,
                change_summary="Initial draft created",
                sources_verified=True
            )
            session.add(test_revision)
            session.commit()
            print(f"    ✓ Created ArticleRevision (ID: {test_revision.id})")
        else:
            print("    ⚠ Skipped (no articles in database)")

        # Test Correction model
        if article:
            print("  Testing Correction model...")
            test_correction = Correction(
                article_id=article.id,
                correction_type="clarification",
                incorrect_text="Original unclear statement",
                correct_text="Clarified statement",
                severity="minor",
                description="Added clarity to ambiguous phrasing",
                status='pending'
            )
            session.add(test_correction)
            session.commit()
            print(f"    ✓ Created Correction (ID: {test_correction.id})")

        # Test SourceReliabilityLog model
        print("  Testing SourceReliabilityLog model...")
        source = session.query(Source).first()
        if source:
            test_log = SourceReliabilityLog(
                source_id=source.id,
                event_type="fact_check_pass",
                reliability_delta=0.1,
                previous_score=source.credibility_score,
                new_score=source.credibility_score,
                automated_adjustment=True
            )
            session.add(test_log)
            session.commit()
            print(f"    ✓ Created SourceReliabilityLog (ID: {test_log.id})")
        else:
            print("    ⚠ Skipped (no sources in database)")

        # Test new Article columns
        if article:
            print("  Testing new Article columns...")
            article.bias_scan_report = '{"overall_bias": "neutral", "confidence": 0.85}'
            article.self_audit_passed = True
            article.editorial_notes = "Test editorial note"
            article.assigned_editor = "test-editor"
            article.review_deadline = datetime.utcnow() + timedelta(days=1)
            session.commit()
            print("    ✓ Updated Article with new columns")

        # Test new Topic columns
        print("  Testing new Topic columns...")
        topic = session.query(Topic).first()
        if topic:
            topic.verified_facts = '["Fact 1", "Fact 2"]'
            topic.source_plan = '{"primary": "Reuters", "secondary": "AP"}'
            topic.verification_status = 'verified'
            session.commit()
            print("    ✓ Updated Topic with new columns")
        else:
            print("    ⚠ Skipped (no topics in database)")

        print()
        print("Test 6: Querying new views...")

        # Test views
        cursor = session.connection().connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM approved_event_candidates")
        count = cursor.fetchone()[0]
        print(f"  ✓ approved_event_candidates view: {count} rows")

        cursor.execute("SELECT COUNT(*) FROM articles_pending_review")
        count = cursor.fetchone()[0]
        print(f"  ✓ articles_pending_review view: {count} rows")

        cursor.execute("SELECT COUNT(*) FROM article_revision_history")
        count = cursor.fetchone()[0]
        print(f"  ✓ article_revision_history view: {count} rows")

        cursor.execute("SELECT COUNT(*) FROM published_corrections")
        count = cursor.fetchone()[0]
        print(f"  ✓ published_corrections view: {count} rows")

        cursor.execute("SELECT COUNT(*) FROM source_reliability_trends")
        count = cursor.fetchone()[0]
        print(f"  ✓ source_reliability_trends view: {count} rows")

        print()
        print("=" * 80)
        print("All tests passed! ✓")
        print("=" * 80)
        print()
        print("Migration 001 is working correctly.")
        print("Schema is ready for Batch 6: Automated Journalism Pipeline")
        print()

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        session.rollback()
        sys.exit(1)

    finally:
        session.close()


if __name__ == '__main__':
    test_migration()
