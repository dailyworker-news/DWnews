#!/usr/bin/env python3
"""
Run Migration 002: Editorial Workflow Statuses

Adds new article status values for editorial workflow integration:
- under_review
- revision_requested
- needs_senior_review

Usage:
    python database/migrations/run_migration_002.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import sqlite3
import logging

from backend.config import settings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def run_migration():
    """Run migration 002"""
    logger.info("=" * 80)
    logger.info("Running Migration 002: Editorial Workflow Statuses")
    logger.info("=" * 80)

    # Get database path from settings
    db_path = settings.database_url.replace('sqlite:///', '')
    migration_file = Path(__file__).parent / '002_editorial_workflow_statuses.sql'
    backup_path = f"{db_path}.backup_migration_002"

    logger.info(f"Database: {db_path}")
    logger.info(f"Migration file: {migration_file}")

    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}")
        logger.error("Please run database initialization first: python database/init_db.py")
        return False

    # Read migration SQL
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current schema
        logger.info("\nChecking current schema...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='articles'")
        current_schema = cursor.fetchone()

        if current_schema:
            logger.info("Current articles table exists")
            logger.info("Proceeding with migration...")

        # Backup database
        logger.info(f"\nBacking up database to: {backup_path}")

        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info("✓ Backup created")

        # Run migration
        logger.info("\nRunning migration SQL...")
        cursor.executescript(migration_sql)
        conn.commit()

        logger.info("✓ Migration completed successfully")

        # Verify migration
        logger.info("\nVerifying migration...")

        # Test new status values
        test_statuses = ['under_review', 'revision_requested', 'needs_senior_review']
        for status in test_statuses:
            try:
                cursor.execute("""INSERT INTO articles
                    (title, slug, body, category_id, author, is_national, is_local, is_ongoing, is_new, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (f"TEST {status}", f"test-{status}", "test", 1, "Test Author", 1, 0, 0, 1, status))
                cursor.execute(f"DELETE FROM articles WHERE slug = 'test-{status}'")
                conn.commit()
                logger.info(f"✓ Status '{status}' verified")
            except sqlite3.IntegrityError as e:
                logger.error(f"✗ Status '{status}' failed: {e}")
                return False

        # Count articles
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]
        logger.info(f"✓ Articles table contains {article_count} articles")

        logger.info("\n" + "=" * 80)
        logger.info("Migration 002 completed successfully!")
        logger.info(f"Backup saved at: {backup_path}")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()

        logger.error("\nTo restore from backup:")
        logger.error(f"  cp {backup_path} {db_path}")

        return False

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
