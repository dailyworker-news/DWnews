#!/usr/bin/env python3
"""
Migration 004 Runner: Authentication & Access Control
Phase 7.3: Subscriber Authentication & Access Control
Date: 2026-01-02

Adds:
- user_article_reads table (auth-based tracking)
- A/B test configuration tables (ab_test_groups, user_ab_tests, ab_test_metrics)
- User table updates (ab_test_group_id, article_limit_reset_at, username)
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_migration(db_path: str = "./dwnews.db"):
    """Run migration 004: Authentication & Access Control"""

    # Get migration SQL file path
    migration_file = Path(__file__).parent / "004_auth_access_control.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    # Read migration SQL
    with open(migration_file, "r") as f:
        migration_sql = f.read()

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 80)
        print("Migration 004: Authentication & Access Control")
        print("=" * 80)

        # Execute migration SQL
        print("\n📝 Executing migration SQL...")
        cursor.executescript(migration_sql)

        # Verify tables created
        print("\n✅ Verifying table creation...")

        tables_to_check = [
            "user_article_reads",
            "ab_test_groups",
            "user_ab_tests",
            "ab_test_metrics"
        ]

        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            count = cursor.fetchone()[0]
            if count == 1:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                print(f"  ✓ Table '{table}' exists ({row_count} rows)")
            else:
                print(f"  ❌ Table '{table}' NOT created")
                return False

        # Verify A/B test groups seeded
        print("\n✅ Verifying A/B test groups seeded...")
        cursor.execute("SELECT group_name, description, article_limit_daily FROM ab_test_groups ORDER BY id")
        groups = cursor.fetchall()

        for group_name, description, limit in groups:
            print(f"  ✓ {group_name}: {description} (daily limit: {limit if limit != -1 else 'unlimited'})")

        if len(groups) != 4:
            print(f"  ⚠️  Expected 4 A/B test groups, found {len(groups)}")

        # Verify indexes created
        print("\n✅ Verifying indexes created...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_user_article_reads%'")
        indexes = cursor.fetchall()
        print(f"  ✓ Created {len(indexes)} indexes for user_article_reads")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_user_ab_tests%'")
        indexes = cursor.fetchall()
        print(f"  ✓ Created {len(indexes)} indexes for user_ab_tests")

        # Commit changes
        conn.commit()

        print("\n" + "=" * 80)
        print("✅ Migration 004 completed successfully!")
        print("=" * 80)
        print("\nNew tables created:")
        print("  • user_article_reads - Auth-based article consumption tracking")
        print("  • ab_test_groups - A/B test configuration (4 test groups)")
        print("  • user_ab_tests - User A/B test assignments")
        print("  • ab_test_metrics - Conversion tracking and metrics")
        print("\nUser table updated:")
        print("  • ab_test_group_id - A/B test group assignment")
        print("  • article_limit_reset_at - Article limit reset timestamp")
        print("  • username - Optional username field")
        print("\n✅ Ready for Phase 7.3 implementation!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run migration 004: Authentication & Access Control")
    parser.add_argument(
        "--db",
        default="./dwnews.db",
        help="Path to SQLite database file (default: ./dwnews.db)"
    )

    args = parser.parse_args()

    # Run migration
    success = run_migration(args.db)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
