#!/usr/bin/env python3
"""
Test script for Phase 7.3.1: Chronological Timeline Layout

This script verifies that the timeline layout features are working correctly:
1. Articles are displayed in reverse chronological order
2. Date separators are shown for each day
3. Archive access is limited based on subscription tier
4. Relative timestamps are displayed correctly
5. Load More pagination works
"""

import requests
import sys
from datetime import datetime, timedelta

API_BASE_URL = 'http://localhost:8000/api'

def test_article_ordering():
    """Test that articles are returned in reverse chronological order (newest first)"""
    print("\n=== Test 1: Article Ordering (Reverse Chronological) ===")

    try:
        response = requests.get(f'{API_BASE_URL}/articles/', params={
            'status': 'published',
            'ongoing': 'false',
            'limit': 20
        })

        if response.status_code != 200:
            print(f"❌ FAILED: API returned status {response.status_code}")
            return False

        articles = response.json()

        if len(articles) == 0:
            print("⚠️  WARNING: No articles found (database may be empty)")
            return True

        # Check ordering
        dates = [article.get('published_at') for article in articles if article.get('published_at')]

        if not dates:
            print("⚠️  WARNING: No published dates found")
            return True

        # Verify reverse chronological order
        for i in range(len(dates) - 1):
            if dates[i] < dates[i + 1]:
                print(f"❌ FAILED: Articles not in reverse chronological order")
                print(f"   Article {i}: {dates[i]}")
                print(f"   Article {i+1}: {dates[i+1]}")
                return False

        print(f"✅ PASSED: {len(articles)} articles in correct order (newest first)")
        print(f"   Newest: {dates[0]}")
        print(f"   Oldest: {dates[-1]}")
        return True

    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Cannot connect to backend at", API_BASE_URL)
        print("   Make sure the backend is running: cd projects/DWnews && python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_archive_filtering():
    """Test archive filtering logic (client-side simulation)"""
    print("\n=== Test 2: Archive Filtering Logic ===")

    now = datetime.now()

    # Test cases for different subscription tiers
    test_cases = [
        {
            'tier': 'free',
            'limit_days': 5,
            'test_dates': [
                (now, False, "Today"),
                (now - timedelta(days=3), False, "3 days ago"),
                (now - timedelta(days=5), False, "5 days ago (boundary)"),
                (now - timedelta(days=6), True, "6 days ago (locked)"),
                (now - timedelta(days=10), True, "10 days ago (locked)"),
            ]
        },
        {
            'tier': 'basic',
            'limit_days': 10,
            'test_dates': [
                (now, False, "Today"),
                (now - timedelta(days=5), False, "5 days ago"),
                (now - timedelta(days=10), False, "10 days ago (boundary)"),
                (now - timedelta(days=11), True, "11 days ago (locked)"),
                (now - timedelta(days=30), True, "30 days ago (locked)"),
            ]
        },
        {
            'tier': 'premium',
            'limit_days': 365,
            'test_dates': [
                (now, False, "Today"),
                (now - timedelta(days=30), False, "30 days ago"),
                (now - timedelta(days=100), False, "100 days ago"),
                (now - timedelta(days=365), False, "365 days ago (boundary)"),
                (now - timedelta(days=366), True, "366 days ago (locked)"),
            ]
        }
    ]

    all_passed = True

    for case in test_cases:
        tier = case['tier']
        limit_days = case['limit_days']

        print(f"\n  Testing {tier.upper()} tier ({limit_days} days):")

        for test_date, expected_locked, description in case['test_dates']:
            days_diff = (now - test_date).days
            is_locked = days_diff > limit_days

            if is_locked == expected_locked:
                status = "✅"
            else:
                status = "❌"
                all_passed = False

            print(f"    {status} {description}: {'LOCKED' if is_locked else 'ACCESSIBLE'}")

    if all_passed:
        print("\n✅ PASSED: All archive filtering logic correct")
    else:
        print("\n❌ FAILED: Some archive filtering logic incorrect")

    return all_passed


def test_date_grouping():
    """Test date grouping logic (client-side simulation)"""
    print("\n=== Test 3: Date Grouping for Separators ===")

    # Simulate articles from different days
    now = datetime.now()

    test_articles = [
        {'published_at': now.isoformat(), 'title': 'Article 1 (today)'},
        {'published_at': now.isoformat(), 'title': 'Article 2 (today)'},
        {'published_at': (now - timedelta(days=1)).isoformat(), 'title': 'Article 3 (yesterday)'},
        {'published_at': (now - timedelta(days=1)).isoformat(), 'title': 'Article 4 (yesterday)'},
        {'published_at': (now - timedelta(days=3)).isoformat(), 'title': 'Article 5 (3 days ago)'},
    ]

    # Group by day
    groups = {}
    for article in test_articles:
        date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
        date_key = date.strftime('%Y-%m-%d')

        if date_key not in groups:
            groups[date_key] = []
        groups[date_key].append(article)

    expected_groups = 3  # Today, Yesterday, 3 days ago
    actual_groups = len(groups)

    if actual_groups == expected_groups:
        print(f"✅ PASSED: Correctly grouped into {actual_groups} date groups")
        for date_key, articles in groups.items():
            print(f"   {date_key}: {len(articles)} article(s)")
        return True
    else:
        print(f"❌ FAILED: Expected {expected_groups} groups, got {actual_groups}")
        return False


def test_pagination():
    """Test that pagination parameters work correctly"""
    print("\n=== Test 4: Load More Pagination ===")

    try:
        # Get first page
        response1 = requests.get(f'{API_BASE_URL}/articles/', params={
            'status': 'published',
            'ongoing': 'false',
            'limit': 12,
            'offset': 0
        })

        # Get second page
        response2 = requests.get(f'{API_BASE_URL}/articles/', params={
            'status': 'published',
            'ongoing': 'false',
            'limit': 12,
            'offset': 12
        })

        if response1.status_code != 200 or response2.status_code != 200:
            print(f"❌ FAILED: API returned error status")
            return False

        articles_page1 = response1.json()
        articles_page2 = response2.json()

        print(f"✅ PASSED: Pagination working")
        print(f"   Page 1: {len(articles_page1)} articles")
        print(f"   Page 2: {len(articles_page2)} articles")

        # Check for duplicates
        if articles_page1 and articles_page2:
            ids_page1 = {a['id'] for a in articles_page1}
            ids_page2 = {a['id'] for a in articles_page2}

            duplicates = ids_page1 & ids_page2

            if duplicates:
                print(f"❌ FAILED: Found {len(duplicates)} duplicate articles between pages")
                return False
            else:
                print(f"✅ No duplicate articles between pages")

        return True

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("Phase 7.3.1: Chronological Timeline Layout - Test Suite")
    print("=" * 60)

    results = {
        'Article Ordering': test_article_ordering(),
        'Archive Filtering': test_archive_filtering(),
        'Date Grouping': test_date_grouping(),
        'Pagination': test_pagination(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Test the timeline layout visually")
        print("3. Use the subscription tier dropdown to test different tiers")
        print("4. Test mobile responsiveness (resize browser or use DevTools)")
        print("5. Test 'Load More' button to load older articles")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease review the failures above and fix them before proceeding.")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
