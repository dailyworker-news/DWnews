#!/usr/bin/env python3
"""
The Daily Worker - Database Initialization
Creates database tables and initial structure
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from models import Base
from backend.config import settings, setup_directories


def init_database():
    """Initialize database with schema"""

    print("=" * 60)
    print("The Daily Worker - Database Initialization")
    print("=" * 60)

    # Setup directories
    setup_directories()

    # Create engine
    print(f"\nConnecting to database: {settings.database_url}")
    engine = create_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )

    # Create all tables
    print("\nCreating database tables...")
    Base.metadata.create_all(engine)

    print("\n✓ Database initialized successfully!")
    print(f"  - Tables created: {len(Base.metadata.tables)}")
    print(f"  - Tables: {', '.join(Base.metadata.tables.keys())}")

    return engine


if __name__ == "__main__":
    try:
        engine = init_database()
        print("\nNext steps:")
        print("1. Run seed_data.py to populate initial data")
        print("2. Run test_data.py to generate test articles")
        print("3. Start the backend: python backend/main.py")
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        sys.exit(1)
