#!/usr/bin/env python3
"""
Test script for Signal Intake Agent.

This script tests the complete event discovery pipeline:
1. Fetch events from all sources (RSS, Twitter, Reddit, Government)
2. Deduplicate events
3. Store in database
4. Verify storage and display statistics

Usage:
    python scripts/test_signal_intake.py                    # Full test
    python scripts/test_signal_intake.py --dry-run          # Test without DB writes
    python scripts/test_signal_intake.py --rss-only         # Test RSS feeds only
    python scripts/test_signal_intake.py --stats            # Show discovery statistics
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import agent
from backend.agents.signal_intake_agent import SignalIntakeAgent
from backend.database import get_db
from database.models import EventCandidate


def setup_logging(verbose: bool = False):
    """Configure logging for the test script."""
    level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory if it doesn't exist
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / 'signal_intake_test.log')
        ]
    )


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def test_discovery(
    dry_run: bool = False,
    rss_only: bool = False,
    twitter_only: bool = False,
    reddit_only: bool = False,
    government_only: bool = False,
    max_age_hours: int = 24
):
    """
    Test event discovery.

    Args:
        dry_run: If True, don't write to database
        rss_only: Only test RSS feeds
        twitter_only: Only test Twitter
        reddit_only: Only test Reddit
        government_only: Only test government sources
        max_age_hours: Only fetch events from last N hours
    """
    print_header("SIGNAL INTAKE AGENT - DISCOVERY TEST")

    # Determine which sources to enable
    if rss_only:
        enable_rss, enable_twitter, enable_reddit, enable_gov = True, False, False, False
    elif twitter_only:
        enable_rss, enable_twitter, enable_reddit, enable_gov = False, True, False, False
    elif reddit_only:
        enable_rss, enable_twitter, enable_reddit, enable_gov = False, False, True, False
    elif government_only:
        enable_rss, enable_twitter, enable_reddit, enable_gov = False, False, False, True
    else:
        enable_rss, enable_twitter, enable_reddit, enable_gov = True, True, True, True

    print(f"Configuration:")
    print(f"  Max age: {max_age_hours} hours")
    print(f"  Dry run: {dry_run}")
    print(f"  Sources: RSS={enable_rss}, Twitter={enable_twitter}, "
          f"Reddit={enable_reddit}, Government={enable_gov}")

    # Create agent
    print_section("Initializing Agent")
    agent = SignalIntakeAgent(
        max_age_hours=max_age_hours,
        enable_rss=enable_rss,
        enable_twitter=enable_twitter,
        enable_reddit=enable_reddit,
        enable_government=enable_gov,
        dry_run=dry_run
    )

    # Run discovery
    print_section("Running Discovery")
    start_time = datetime.now()

    try:
        results = agent.discover_events()
        success = True
    except Exception as e:
        print(f"\n❌ ERROR: Discovery failed: {str(e)}")
        logging.error("Discovery failed", exc_info=True)
        success = False
        results = None

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()

    # Display results
    if success and results:
        print_section("Discovery Results")
        print(f"  Runtime: {runtime:.2f} seconds")
        print(f"  Total fetched: {results['total_fetched']}")
        print(f"  Unique events: {results['total_unique']}")
        print(f"  Stored in DB: {results['total_discovered']}")

        print("\n  By source:")
        for source, count in results['by_source'].items():
            print(f"    {source}: {count}")

        if results['errors']:
            print("\n  ⚠️  Errors encountered:")
            for error in results['errors']:
                print(f"    - {error}")

        # Calculate deduplication rate
        if results['total_fetched'] > 0:
            dedup_rate = (1 - results['total_unique'] / results['total_fetched']) * 100
            print(f"\n  Deduplication rate: {dedup_rate:.1f}%")

        # Success criteria
        print_section("Success Criteria")
        criteria = {
            'Minimum events (20)': results['total_discovered'] >= 20,
            'Source diversity (≥2)': len([c for c in results['by_source'].values() if c > 0]) >= 2,
            'Runtime (<5 min)': runtime < 300,
            'Error rate (<50%)': len(results['errors']) < len(results['by_source']) / 2,
        }

        for criterion, passed in criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {status}: {criterion}")

        # Overall result
        all_passed = all(criteria.values())
        print_section("Overall Result")
        if all_passed:
            print("  ✅ ALL TESTS PASSED")
        else:
            print("  ⚠️  SOME TESTS FAILED")

        return all_passed

    else:
        print_section("Overall Result")
        print("  ❌ DISCOVERY FAILED")
        return False


def show_discovery_stats(days: int = 7):
    """
    Show statistics about recent discoveries.

    Args:
        days: Number of days to look back
    """
    print_header(f"DISCOVERY STATISTICS (Last {days} days)")

    agent = SignalIntakeAgent()
    stats = agent.get_discovery_stats(days=days)

    print(f"\nTotal discoveries: {stats['total_discoveries']}")

    print("\nBy status:")
    for status, count in stats['by_status'].items():
        percentage = (count / stats['total_discoveries'] * 100) if stats['total_discoveries'] > 0 else 0
        print(f"  {status}: {count} ({percentage:.1f}%)")

    print("\nBy source:")
    for source, count in stats['by_source'].items():
        percentage = (count / stats['total_discoveries'] * 100) if stats['total_discoveries'] > 0 else 0
        print(f"  {source}: {count} ({percentage:.1f}%)")

    # Calculate daily average
    daily_avg = stats['total_discoveries'] / days
    print(f"\nDaily average: {daily_avg:.1f} events/day")

    # Success metrics
    print_section("Target Metrics")
    metrics = {
        'Minimum (20/day)': daily_avg >= 20,
        'Target (30-50/day)': 30 <= daily_avg <= 50,
        'Approval rate (10-20%)': 10 <= (stats['by_status'].get('approved', 0) / max(stats['total_discoveries'], 1) * 100) <= 20,
    }

    for metric, met in metrics.items():
        status = "✅" if met else "⚠️"
        print(f"  {status} {metric}")


def show_sample_events(limit: int = 5):
    """
    Show sample discovered events.

    Args:
        limit: Number of events to display
    """
    print_header(f"SAMPLE DISCOVERED EVENTS (Last {limit})")

    session = next(get_db())

    try:
        # Get recent events
        events = session.query(EventCandidate).order_by(
            EventCandidate.discovery_date.desc()
        ).limit(limit).all()

        if not events:
            print("\nNo events found in database.")
            return

        for i, event in enumerate(events, 1):
            print(f"\n{i}. {event.title}")
            print(f"   Source: {event.discovered_from}")
            print(f"   Category: {event.suggested_category}")
            print(f"   Status: {event.status}")
            print(f"   Discovered: {event.discovery_date}")
            if event.keywords:
                print(f"   Keywords: {event.keywords}")
            if event.source_url:
                print(f"   URL: {event.source_url[:80]}...")

    finally:
        session.close()


def main():
    """Main test script entry point."""
    parser = argparse.ArgumentParser(
        description='Test Signal Intake Agent event discovery'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test without writing to database'
    )
    parser.add_argument(
        '--rss-only',
        action='store_true',
        help='Only test RSS feeds'
    )
    parser.add_argument(
        '--twitter-only',
        action='store_true',
        help='Only test Twitter API'
    )
    parser.add_argument(
        '--reddit-only',
        action='store_true',
        help='Only test Reddit API'
    )
    parser.add_argument(
        '--government-only',
        action='store_true',
        help='Only test government sources'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show discovery statistics'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Show sample discovered events'
    )
    parser.add_argument(
        '--max-age',
        type=int,
        default=24,
        help='Max age of events in hours (default: 24)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days to look back for stats (default: 7)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Run tests
    try:
        if args.stats:
            show_discovery_stats(days=args.days)

        elif args.sample:
            show_sample_events(limit=5)

        else:
            # Run discovery test
            success = test_discovery(
                dry_run=args.dry_run,
                rss_only=args.rss_only,
                twitter_only=args.twitter_only,
                reddit_only=args.reddit_only,
                government_only=args.government_only,
                max_age_hours=args.max_age
            )

            # Show sample events if not dry run
            if success and not args.dry_run:
                show_sample_events(limit=5)

            # Exit with appropriate code
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        logging.error("Unexpected error in test script", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
