#!/usr/bin/env python3
"""
The Daily Worker - Unified Topic Discovery
Master script that runs all discovery sources (RSS + Social Media)
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from scripts.content.rss_discovery import run_discovery as rss_discovery
from scripts.content.social_discovery import run_social_discovery

logger = get_logger(__name__)


def discover_all_topics():
    """Run all topic discovery sources"""
    print("=" * 70)
    print(" " * 15 + "THE DAILY WORKER")
    print(" " * 10 + "Unified Topic Discovery")
    print("=" * 70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {settings.environment}")

    total_saved = 0

    # 1. RSS Feed Discovery
    print("\n" + "=" * 70)
    print("PHASE 1: RSS FEED DISCOVERY")
    print("=" * 70)
    try:
        rss_count = rss_discovery(max_topics=50)
        total_saved += rss_count
        print(f"\n✓ RSS Discovery: {rss_count} topics saved")
    except Exception as e:
        print(f"\n✗ RSS Discovery failed: {e}")
        logger.error(f"RSS discovery error: {e}")

    # 2. Social Media Discovery
    print("\n" + "=" * 70)
    print("PHASE 2: SOCIAL MEDIA DISCOVERY")
    print("=" * 70)
    try:
        social_count = run_social_discovery(max_topics=30)
        total_saved += social_count
        print(f"\n✓ Social Discovery: {social_count} topics saved")
    except Exception as e:
        print(f"\n✗ Social Discovery failed: {e}")
        logger.error(f"Social discovery error: {e}")

    # Final Summary
    print("\n" + "=" * 70)
    print("DISCOVERY COMPLETE")
    print("=" * 70)
    print(f"Total topics saved: {total_saved}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if total_saved == 0:
        print("\n⚠ No topics discovered. Check:")
        print("  1. RSS feeds are accessible")
        print("  2. Social media API credentials in .env")
        print("  3. Internet connection")
    else:
        print(f"\n✓ Success! {total_saved} new topics ready for filtering")
        print("\nNext steps:")
        print("  1. Run: python scripts/content/filter_topics.py")
        print("  2. Review filtered topics")
        print("  3. Run: python scripts/content/generate_articles.py")

    return total_saved


if __name__ == "__main__":
    try:
        total = discover_all_topics()
        sys.exit(0 if total > 0 else 1)
    except KeyboardInterrupt:
        print("\n\nDiscovery cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        logger.exception("Discovery failed")
        sys.exit(1)
