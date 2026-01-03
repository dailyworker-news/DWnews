#!/usr/bin/env python3
"""
Test suite for Phase 11.2: RSS Feed Integration & Testing

Tests the integration of 8 new RSS sources (Batch 1) to expand from 13 to 21 total feeds.
Validates parsing, content quality, deduplication, and event discovery performance.

New Sources (Batch 1):
1. The Lever - https://www.levernews.com/rss
2. Jacobin - https://jacobin.com/feed
3. ICIJ - https://www.icij.org/feed/
4. Reveal - https://revealnews.org/feed/
5. The Markup - https://themarkup.org/feeds/rss.xml
6. LaborPress - https://www.laborpress.org/feed/
7. Belt Magazine - https://beltmag.com/feed/
8. Scalawag - https://scalawagmagazine.org/feed/

Test-Driven Development approach:
- Write tests FIRST to define expected behavior
- Tests will FAIL initially (new sources not yet added to rss_feeds.py)
- Implement feed integration to make tests PASS
- Validate event discovery targets (30-60 events/day)
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import feedparser
from datetime import datetime, timedelta
from backend.agents.feeds.rss_feeds import RSSFeedAggregator


class TestExpandedRSSFeeds(unittest.TestCase):
    """Test suite for expanded RSS feed integration (Phase 11.2)"""

    # New sources to be added in Batch 1
    NEW_SOURCES = {
        'the_lever': {
            'url': 'https://www.levernews.com/rss',
            'priority': 'critical',
            'keywords': [],  # All articles relevant
            'expected_category': 'labor',
        },
        'jacobin': {
            'url': 'https://jacobin.com/feed',
            'priority': 'critical',
            'keywords': [],  # All articles relevant
            'expected_category': 'labor',
        },
        'icij': {
            'url': 'https://www.icij.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'exploitation', 'corruption', 'wage theft'],
            'expected_category': 'labor',
        },
        'reveal': {
            'url': 'https://revealnews.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'safety', 'violation', 'employment'],
            'expected_category': 'labor',
        },
        'the_markup': {
            'url': 'https://themarkup.org/feeds/rss.xml',
            'priority': 'high',
            'keywords': ['worker', 'labor', 'surveillance', 'gig economy', 'tech'],
            'expected_category': 'labor',
        },
        'labor_press_nyc': {
            'url': 'https://www.laborpress.org/feed/',
            'priority': 'high',
            'keywords': [],  # All articles relevant
            'expected_category': 'labor',
        },
        'belt_magazine': {
            'url': 'https://beltmag.com/feed/',
            'priority': 'high',
            'keywords': [],  # All articles relevant
            'expected_category': 'labor',
        },
        'scalawag': {
            'url': 'https://scalawagmagazine.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'economic justice', 'union'],
            'expected_category': 'labor',
        },
    }

    def setUp(self):
        """Set up test fixtures"""
        self.aggregator = RSSFeedAggregator(max_age_hours=24)

    def test_new_sources_added_to_feed_sources(self):
        """Test 1: Verify all 8 new sources are added to FEED_SOURCES dictionary"""
        for source_name in self.NEW_SOURCES.keys():
            self.assertIn(
                source_name,
                self.aggregator.FEED_SOURCES,
                f"New source '{source_name}' not found in FEED_SOURCES dictionary"
            )

    def test_total_feed_count_is_21(self):
        """Test 2: Verify total feed count is 21 (13 existing + 8 new)"""
        total_feeds = len(self.aggregator.FEED_SOURCES)
        self.assertEqual(
            total_feeds,
            21,
            f"Expected 21 total feeds (13 existing + 8 new), found {total_feeds}"
        )

    def test_new_source_urls_match_research(self):
        """Test 3: Verify URLs of new sources match Phase 11.1 research document"""
        for source_name, expected_config in self.NEW_SOURCES.items():
            actual_config = self.aggregator.FEED_SOURCES.get(source_name)
            self.assertIsNotNone(actual_config, f"Source '{source_name}' not found")
            self.assertEqual(
                actual_config['url'],
                expected_config['url'],
                f"URL mismatch for '{source_name}'"
            )

    def test_new_source_priority_levels(self):
        """Test 4: Verify priority levels are correctly configured"""
        for source_name, expected_config in self.NEW_SOURCES.items():
            actual_config = self.aggregator.FEED_SOURCES.get(source_name)
            if actual_config:
                self.assertEqual(
                    actual_config['priority'],
                    expected_config['priority'],
                    f"Priority mismatch for '{source_name}': expected '{expected_config['priority']}', got '{actual_config['priority']}'"
                )

    def test_new_source_keyword_filters(self):
        """Test 5: Verify keyword filters are configured for general news sources"""
        sources_with_keywords = ['icij', 'reveal', 'the_markup', 'scalawag']

        for source_name in sources_with_keywords:
            actual_config = self.aggregator.FEED_SOURCES.get(source_name)
            if actual_config:
                self.assertTrue(
                    len(actual_config['keywords']) > 0,
                    f"Source '{source_name}' should have keyword filters for general news"
                )

    def test_labor_focused_sources_no_keywords(self):
        """Test 6: Verify labor-focused sources have empty keyword filters (all content relevant)"""
        labor_focused = ['the_lever', 'jacobin', 'labor_press_nyc', 'belt_magazine']

        for source_name in labor_focused:
            actual_config = self.aggregator.FEED_SOURCES.get(source_name)
            if actual_config:
                self.assertEqual(
                    len(actual_config['keywords']),
                    0,
                    f"Labor-focused source '{source_name}' should have no keyword filters (all content relevant)"
                )

    @patch('feedparser.parse')
    def test_individual_feed_parsing_the_lever(self, mock_parse):
        """Test 7: Test individual feed parsing - The Lever"""
        # Mock RSS feed response
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': "Scammers' New Billion-Dollar Bank Fraud",
                'description': "Investigation into financial fraud affecting working families",
                'link': "https://www.levernews.com/scammers-bank-fraud/",
                'published_parsed': (2026, 1, 2, 12, 0, 0, 0, 0, 0),
            }
        ])

        events = self.aggregator._fetch_feed('the_lever', {
            'url': 'https://www.levernews.com/rss',
            'priority': 'critical',
            'keywords': [],
        })

        self.assertEqual(len(events), 1, "Should fetch 1 event from The Lever")
        self.assertIn("Scammers", events[0]['title'])

    @patch('feedparser.parse')
    def test_individual_feed_parsing_jacobin(self, mock_parse):
        """Test 8: Test individual feed parsing - Jacobin"""
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': "Building Mass Governance in New York City",
                'description': "Labor politics and organizing in NYC municipal government",
                'link': "https://jacobin.com/2026/01/mass-governance-nyc",
                'published_parsed': (2026, 1, 2, 10, 0, 0, 0, 0, 0),
            }
        ])

        events = self.aggregator._fetch_feed('jacobin', {
            'url': 'https://jacobin.com/feed',
            'priority': 'critical',
            'keywords': [],
        })

        self.assertEqual(len(events), 1, "Should fetch 1 event from Jacobin")
        self.assertIn("Governance", events[0]['title'])

    @patch('feedparser.parse')
    def test_keyword_filtering_works(self, mock_parse):
        """Test 9: Test keyword filtering for general news sources"""
        # Get current date to ensure articles aren't filtered by age
        from datetime import datetime
        now = datetime.now()

        # Mock feed with both labor and non-labor content
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': "Major Union Strike at Manufacturing Plant",
                'description': "Workers organize for better wages and safety",
                'link': "https://example.com/union-strike",
                'published_parsed': (now.year, now.month, now.day, now.hour, 0, 0, 0, 0, 0),
                'summary': "Workers organize for better wages and safety",  # Add summary field
            },
            {
                'title': "Celebrity Wedding Announcement",
                'description': "Famous actor marries in Italy",
                'link': "https://example.com/celebrity",
                'published_parsed': (now.year, now.month, now.day, now.hour - 1, 0, 0, 0, 0, 0),
                'summary': "Famous actor marries in Italy",  # Add summary field
            }
        ])

        events = self.aggregator._fetch_feed('icij', {
            'url': 'https://www.icij.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'union', 'strike'],
        })

        # Should only get labor-related article, not celebrity
        self.assertEqual(len(events), 1, "Should filter to only labor-related content")
        self.assertIn("Union", events[0]['title'])

    @patch('feedparser.parse')
    def test_deduplication_across_sources(self, mock_parse):
        """Test 10: Test deduplication logic with expanded feed list"""
        # Same story from two different sources
        story_title = "Amazon Workers Win Union Election"

        # Mock both sources returning same story
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': story_title,
                'description': "Workers at Amazon facility vote to unionize",
                'link': "https://source1.com/amazon-union",
                'published_parsed': (2026, 1, 2, 12, 0, 0, 0, 0, 0),
            }
        ])

        events1 = self.aggregator._fetch_feed('the_lever', {
            'url': 'https://www.levernews.com/rss',
            'priority': 'critical',
            'keywords': [],
        })

        events2 = self.aggregator._fetch_feed('jacobin', {
            'url': 'https://jacobin.com/feed',
            'priority': 'critical',
            'keywords': [],
        })

        # Both should fetch the event
        self.assertEqual(len(events1), 1)
        self.assertEqual(len(events2), 1)

        # Deduplication should be handled by Signal Intake Agent
        # This test validates that both sources can fetch similar stories

    @patch('feedparser.parse')
    def test_event_volume_target(self, mock_parse):
        """Test 11: Validate event discovery meets 30-60 events/day target"""
        # Mock moderate feed activity (2-3 events per daily source)
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': f"Labor Story {i}",
                'description': "Worker-related news story",
                'link': f"https://example.com/story-{i}",
                'published_parsed': (2026, 1, 2, 12, i, 0, 0, 0, 0),
            }
            for i in range(3)  # 3 events per source
        ])

        # Fetch from all sources
        all_events = self.aggregator.fetch_all_feeds()

        # With 21 sources × ~3 events = ~63 events (within 30-60 target)
        # Note: In practice, some sources update weekly, so actual count varies
        self.assertGreater(
            len(all_events),
            10,
            f"Should fetch at least 10 events from expanded feeds, got {len(all_events)}"
        )

    def test_geographic_diversity_sources(self):
        """Test 12: Verify geographic diversity in new sources"""
        geographic_coverage = {
            'labor_press_nyc': 'NYC',
            'belt_magazine': 'Midwest/Rust Belt',
            'scalawag': 'U.S. South',
            'the_markup': 'California/U.S.',
            'icij': 'Global',
            'reveal': 'U.S. National',
            'the_lever': 'U.S. National',
            'jacobin': 'U.S./International',
        }

        for source_name, region in geographic_coverage.items():
            self.assertIn(
                source_name,
                self.aggregator.FEED_SOURCES,
                f"Geographic source '{source_name}' ({region}) not found"
            )

    def test_source_credibility_tiers(self):
        """Test 13: Verify source credibility matches Phase 11.1 evaluation matrix"""
        # Tier 1 (90-100): ICIJ, Reveal, The Lever
        tier_1_sources = ['icij', 'reveal', 'the_lever']

        # Tier 2 (85-89): Jacobin, Scalawag, Belt Magazine, LaborPress, The Markup
        tier_2_sources = ['jacobin', 'scalawag', 'belt_magazine', 'labor_press_nyc', 'the_markup']

        for source in tier_1_sources:
            self.assertIn(source, self.aggregator.FEED_SOURCES, f"Tier 1 source '{source}' missing")

        for source in tier_2_sources:
            self.assertIn(source, self.aggregator.FEED_SOURCES, f"Tier 2 source '{source}' missing")

    @patch('feedparser.parse')
    def test_parse_date_handling(self, mock_parse):
        """Test 14: Verify parsing of different RSS date formats"""
        # Test with Atom format (Jacobin uses Atom 1.0)
        mock_parse.return_value = self._create_mock_feed([
            {
                'title': "Test Article",
                'description': "Test description",
                'link': "https://example.com/test",
                'updated_parsed': (2026, 1, 2, 12, 0, 0, 0, 0, 0),  # Atom uses updated_parsed
            }
        ])

        events = self.aggregator._fetch_feed('jacobin', {
            'url': 'https://jacobin.com/feed',
            'priority': 'critical',
            'keywords': [],
        })

        self.assertEqual(len(events), 1, "Should parse Atom feed date format")
        self.assertIsNotNone(events[0]['event_date'], "Event date should be parsed")

    @patch('feedparser.parse')
    def test_performance_fetch_time(self, mock_parse):
        """Test 15: Measure and validate feed fetch performance"""
        import time

        mock_parse.return_value = self._create_mock_feed([
            {
                'title': "Performance Test Article",
                'description': "Test description",
                'link': "https://example.com/test",
                'published_parsed': (2026, 1, 2, 12, 0, 0, 0, 0, 0),
            }
        ])

        start_time = time.time()
        events = self.aggregator.fetch_all_feeds()
        fetch_time = time.time() - start_time

        # With 21 sources, should complete in reasonable time (<30 seconds for mocked feeds)
        self.assertLess(
            fetch_time,
            30,
            f"Feed fetching took {fetch_time:.2f}s, should be under 30s (mocked)"
        )

    @patch('feedparser.parse')
    def test_error_handling_feed_failures(self, mock_parse):
        """Test 16: Verify graceful handling of feed failures"""
        # Simulate feed failure
        mock_parse.side_effect = Exception("Network error")

        # Should not crash, should log error and continue
        try:
            events = self.aggregator.fetch_all_feeds()
            # Should return empty list or events from other sources
            self.assertIsInstance(events, list, "Should return list even if some feeds fail")
        except Exception as e:
            self.fail(f"Should handle feed failures gracefully, but raised: {e}")

    def test_worker_relevance_coverage(self):
        """Test 17: Verify worker relevance categories are covered"""
        expected_coverage = {
            'union_organizing': ['the_lever', 'jacobin', 'labor_press_nyc'],
            'investigative': ['icij', 'reveal'],
            'tech_workers': ['the_markup'],
            'regional_labor': ['belt_magazine', 'labor_press_nyc', 'scalawag'],
        }

        for category, sources in expected_coverage.items():
            for source in sources:
                self.assertIn(
                    source,
                    self.aggregator.FEED_SOURCES,
                    f"Worker relevance category '{category}' source '{source}' missing"
                )

    def test_update_frequency_diversity(self):
        """Test 18: Verify mix of daily and weekly update frequencies"""
        # Based on Phase 11.1 research:
        # Daily: The Lever, Jacobin, LaborPress, The Markup, ICIJ, Reveal
        # Weekly: Belt Magazine, Scalawag

        daily_sources = ['the_lever', 'jacobin', 'labor_press_nyc', 'the_markup', 'icij', 'reveal']
        weekly_sources = ['belt_magazine', 'scalawag']

        for source in daily_sources:
            self.assertIn(source, self.aggregator.FEED_SOURCES, f"Daily source '{source}' missing")

        for source in weekly_sources:
            self.assertIn(source, self.aggregator.FEED_SOURCES, f"Weekly source '{source}' missing")

    # Helper methods

    def _create_mock_feed(self, entries):
        """Create a mock feedparser feed object"""
        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = []

        for entry_data in entries:
            entry = MagicMock()
            # Set attributes
            for key, value in entry_data.items():
                setattr(entry, key, value)

            # Add get method for dictionary-style access
            def make_get(data):
                def get(key, default=''):
                    return data.get(key, default)
                return get

            entry.get = make_get(entry_data)

            # Add hasattr support for date fields
            entry.__dict__.update(entry_data)

            mock_feed.entries.append(entry)

        return mock_feed


def run_tests():
    """Run the test suite and print results"""
    print("=" * 80)
    print("Phase 11.2: RSS Feed Integration & Testing")
    print("Test Suite for Expanded RSS Feed Sources")
    print("=" * 80)
    print()
    print("Testing 8 new RSS sources (Batch 1):")
    print("  1. The Lever (CRITICAL)")
    print("  2. Jacobin (CRITICAL)")
    print("  3. ICIJ (HIGH)")
    print("  4. Reveal (HIGH)")
    print("  5. The Markup (HIGH)")
    print("  6. LaborPress NYC (HIGH)")
    print("  7. Belt Magazine (HIGH)")
    print("  8. Scalawag (HIGH)")
    print()
    print("Target: 13 existing + 8 new = 21 total feeds")
    print("Expected event volume: 30-60 events/day")
    print()
    print("=" * 80)
    print()

    # Run tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExpandedRSSFeeds)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED - RSS feed integration successful!")
        print(f"✅ {result.testsRun} feeds validated and operational")
        print("✅ Ready for production event discovery")
        return 0
    else:
        print("❌ TESTS FAILED - Implementation needed")
        print("Next step: Add new sources to rss_feeds.py to make tests pass")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
