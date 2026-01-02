#!/usr/bin/env python3
"""
Migration Script: Automated Journalism Pipeline Schema Extensions
Version: 001
Date: 2026-01-01

This script applies migration 001 to add tables and columns for the automated
journalism workflow (Batch 6, Phase 6.1).

Compatible with: SQLite (local) and PostgreSQL (cloud)
"""

import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / 'dwnews.db'
MIGRATION_SQL_PATH = Path(__file__).parent / '001_automated_journalism_schema.sql'


def run_migration():
    """Run the migration on SQLite database"""

    print("=" * 80)
    print("Migration 001: Automated Journalism Pipeline Schema Extensions")
    print("=" * 80)
    print()

    # Check if database exists
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please run 'python database/init_db.py' first to create the database.")
        sys.exit(1)

    # Check if migration SQL exists
    if not MIGRATION_SQL_PATH.exists():
        print(f"ERROR: Migration SQL not found at {MIGRATION_SQL_PATH}")
        sys.exit(1)

    # Read migration SQL
    with open(MIGRATION_SQL_PATH, 'r') as f:
        migration_sql = f.read()

    # Connect to database
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if migration has already been run
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_candidates'")
        if cursor.fetchone():
            print()
            print("WARNING: Migration 001 appears to have already been run.")
            print("Table 'event_candidates' already exists.")
            response = input("Do you want to continue anyway? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Migration cancelled.")
                conn.close()
                return

        print()
        print("Running migration...")
        print()

        # Execute migration (SQLite executescript handles multiple statements)
        cursor.executescript(migration_sql)

        # Commit changes
        conn.commit()

        print("✓ Migration completed successfully!")
        print()

        # Verify new tables
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name IN ('event_candidates', 'article_revisions', 'corrections', 'source_reliability_log')
            ORDER BY name
        """)
        new_tables = cursor.fetchall()

        print("New tables created:")
        for table in new_tables:
            print(f"  ✓ {table[0]}")

        print()

        # Verify new columns in articles table
        cursor.execute("PRAGMA table_info(articles)")
        article_columns = [col[1] for col in cursor.fetchall()]
        new_article_cols = [
            'bias_scan_report',
            'self_audit_passed',
            'editorial_notes',
            'assigned_editor',
            'review_deadline'
        ]

        print("New columns in 'articles' table:")
        for col in new_article_cols:
            if col in article_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} (MISSING!)")

        print()

        # Verify new columns in topics table
        cursor.execute("PRAGMA table_info(topics)")
        topic_columns = [col[1] for col in cursor.fetchall()]
        new_topic_cols = [
            'verified_facts',
            'source_plan',
            'verification_status'
        ]

        print("New columns in 'topics' table:")
        for col in new_topic_cols:
            if col in topic_columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} (MISSING!)")

        print()

        # Verify new views
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='view'
            AND name IN (
                'approved_event_candidates',
                'articles_pending_review',
                'article_revision_history',
                'published_corrections',
                'source_reliability_trends'
            )
            ORDER BY name
        """)
        new_views = cursor.fetchall()

        print("New views created:")
        for view in new_views:
            print(f"  ✓ {view[0]}")

        print()
        print("=" * 80)
        print("Migration 001 completed successfully!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Verify the migration by running: python database/migrations/test_migration_001.py")
        print("2. Continue with Phase 6.2: Signal Intake Agent")
        print()

    except sqlite3.Error as e:
        print(f"ERROR: Migration failed!")
        print(f"SQLite error: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()


if __name__ == '__main__':
    run_migration()
