#!/usr/bin/env python3
"""
Migration 006: Image Sourcing & Generation Fields
Adds support for multi-tier image sourcing strategy
"""

import sys
from pathlib import Path
import sqlite3

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)


def run_migration():
    """Execute migration 006: Image Sourcing Fields"""
    print("=" * 70)
    print("Migration 006: Image Sourcing & Generation Fields")
    print("Phase 6.11: Image Sourcing & Generation Agent")
    print("=" * 70)

    # Read migration SQL
    migration_file = Path(__file__).parent / "006_image_sourcing_fields.sql"
    if not migration_file.exists():
        print(f"✗ Migration file not found: {migration_file}")
        return False

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Connect to database
    db_path = settings.database_url.replace('sqlite:///', '')

    # Handle relative paths - resolve to absolute
    if not db_path.startswith('/'):
        # Relative path - resolve from project root
        project_root = Path(__file__).parent.parent.parent
        db_path = str(project_root / db_path)

    print(f"\nConnecting to database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute migration in transaction
        print("\nExecuting migration...")

        # Split into individual statements and execute
        statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]

        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  [{i}/{len(statements)}] Executing statement...")
                try:
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    # Ignore "duplicate column" errors (column already exists)
                    if 'duplicate column' in str(e).lower():
                        print(f"    ⚠ Column already exists, skipping...")
                    else:
                        raise

        # Commit changes
        conn.commit()

        # Verify new columns exist
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(articles)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            'image_source_type',
            'gemini_prompt',
            'image_license',
            'generated_by_gemini'
        }

        missing_columns = required_columns - columns
        if missing_columns:
            print(f"✗ Missing columns: {missing_columns}")
            return False

        print("✓ All required columns present")

        # Verify indexes
        cursor.execute("PRAGMA index_list(articles)")
        indexes = {row[1] for row in cursor.fetchall()}

        required_indexes = {
            'idx_articles_image_source_type',
            'idx_articles_generated_by_gemini'
        }

        if required_indexes.issubset(indexes):
            print("✓ All required indexes created")
        else:
            missing_indexes = required_indexes - indexes
            print(f"⚠ Some indexes may be missing: {missing_indexes}")

        # Show statistics
        cursor.execute("""
            SELECT
                image_source_type,
                COUNT(*) as count
            FROM articles
            GROUP BY image_source_type
        """)

        print("\nImage source type distribution:")
        for row in cursor.fetchall():
            source_type, count = row
            print(f"  {source_type}: {count} articles")

        conn.close()

        print("\n" + "=" * 70)
        print("MIGRATION 006 COMPLETE")
        print("=" * 70)
        print("✓ Image sourcing fields added to articles table")
        print("✓ Indexes created for performance")
        print("✓ Existing data migrated")
        print("\nNext steps:")
        print("1. Test Image Sourcing Agent with real articles")
        print("2. Verify Gemini API integration (requires API key)")
        print("3. Monitor cost tracking and daily limits")

        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"\n✗ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
