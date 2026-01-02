#!/usr/bin/env python3
"""
Migration Runner for 003_subscription_schema.sql
Phase 7.1: Database Schema for Subscriptions

Usage:
    python run_migration_003.py
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

def run_migration():
    """Run the subscription schema migration."""

    # Get database path
    db_path = Path(__file__).parent.parent / "daily_worker.db"
    migration_file = Path(__file__).parent / "003_subscription_schema.sql"

    print(f"Database: {db_path}")
    print(f"Migration: {migration_file}")

    if not migration_file.exists():
        print(f"Error: Migration file not found: {migration_file}")
        return False

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Read migration SQL
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print("\n" + "="*60)
        print("Starting Migration 003: Subscription Schema")
        print("="*60)

        # Split SQL statements (handle multi-line statements)
        statements = []
        current_statement = []

        for line in migration_sql.split('\n'):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue

            current_statement.append(line)

            # Check if statement is complete (ends with semicolon)
            if stripped.endswith(';'):
                stmt = '\n'.join(current_statement)
                statements.append(stmt)
                current_statement = []

        # Execute each statement
        total_statements = len(statements)
        print(f"\nExecuting {total_statements} SQL statements...")

        for i, statement in enumerate(statements, 1):
            # Show progress for CREATE TABLE/INDEX and INSERT statements
            stmt_preview = statement.strip()[:80]
            if stmt_preview.startswith(('CREATE TABLE', 'CREATE INDEX', 'INSERT INTO', 'ALTER TABLE')):
                print(f"  [{i}/{total_statements}] {stmt_preview}...")

            try:
                cursor.execute(statement)
            except sqlite3.OperationalError as e:
                # Handle "column already exists" errors gracefully (idempotent migration)
                if "duplicate column name" in str(e).lower():
                    print(f"    Warning: Column already exists (skipping)")
                else:
                    raise

        # Commit transaction
        conn.commit()

        print("\n" + "="*60)
        print("Migration Completed Successfully")
        print("="*60)

        # Verify tables were created
        print("\nVerifying new tables...")
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            AND name IN (
                'subscription_plans', 'subscriptions', 'payment_methods',
                'invoices', 'subscription_events', 'sports_leagues',
                'user_sports_preferences', 'sports_results'
            )
            ORDER BY name
        """)

        tables = cursor.fetchall()
        print(f"  Created {len(tables)} tables:")
        for table in tables:
            print(f"    ✓ {table[0]}")

        # Show subscription plans
        print("\nSubscription Plans:")
        cursor.execute("SELECT plan_name, price_cents, billing_interval FROM subscription_plans")
        plans = cursor.fetchall()
        for plan_name, price_cents, interval in plans:
            price_display = f"${price_cents/100:.2f}" if price_cents > 0 else "Free"
            print(f"  • {plan_name}: {price_display}/{interval}")

        # Show sports leagues
        print("\nSports Leagues:")
        cursor.execute("SELECT league_code, name, tier_requirement FROM sports_leagues")
        leagues = cursor.fetchall()
        for code, name, tier in leagues:
            print(f"  • {code}: {name} ({tier} tier)")

        print("\n" + "="*60)
        print("Migration Summary")
        print("="*60)
        print(f"  Tables created: {len(tables)}")
        print(f"  Subscription plans: {len(plans)}")
        print(f"  Sports leagues: {len(leagues)}")
        print(f"  Migration file: 003_subscription_schema.sql")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
