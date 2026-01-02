#!/usr/bin/env python3
"""
Test script for Social Media Investigation (Phase 6.9.2)

Tests the social media investigation modules:
- TwitterInvestigationMonitor (extended search, timeline construction)
- RedditInvestigationMonitor (discussion thread analysis, eyewitness detection)
- SocialSourceCredibility (account age, karma, verification scoring)
- TimelineConstructor (chronological event tracking)
- EyewitnessDetector (firsthand account identification)
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from database.models import Topic


# Test data for social media investigation
MOCK_TWITTER_POSTS = [
    {
        'id': '1234567890',
        'text': 'I was there when Amazon workers walked out today. They demanded better wages and safer conditions. #UnionStrong #AmazonWorkers',
        'author': {
            'username': 'worker_advocate',
            'verified': False,
            'created_at': '2020-01-15',
            'followers_count': 5432,
            'description': 'Labor organizer, on the ground reporting'
        },
        'created_at': datetime.utcnow() - timedelta(hours=2),
        'metrics': {
            'retweet_count': 234,
            'like_count': 567,
            'reply_count': 45,
            'quote_count': 12
        },
        'entities': {
            'hashtags': ['UnionStrong', 'AmazonWorkers']
        }
    },
    {
        'id': '1234567891',
        'text': 'According to union sources, negotiations broke down this morning. Strike vote expected within 48 hours.',
        'author': {
            'username': 'reuters',
            'verified': True,
            'created_at': '2008-03-10',
            'followers_count': 28000000,
            'description': 'Breaking news from Reuters'
        },
        'created_at': datetime.utcnow() - timedelta(hours=4),
        'metrics': {
            'retweet_count': 1200,
            'like_count': 3400,
            'reply_count': 230,
            'quote_count': 89
        },
        'entities': {
            'hashtags': []
        }
    },
    {
        'id': '1234567892',
        'text': 'Just saw this unfold firsthand at the warehouse. Workers are chanting "Union yes!" Very powerful moment.',
        'author': {
            'username': 'local_reporter_99',
            'verified': False,
            'created_at': '2021-06-20',
            'followers_count': 892,
            'description': 'Freelance journalist'
        },
        'created_at': datetime.utcnow() - timedelta(hours=1),
        'metrics': {
            'retweet_count': 45,
            'like_count': 123,
            'reply_count': 8,
            'quote_count': 2
        },
        'entities': {
            'hashtags': []
        }
    }
]

MOCK_REDDIT_POSTS = [
    {
        'id': 'abc123',
        'title': 'Amazon warehouse workers walking out RIGHT NOW - live updates',
        'selftext': 'I work at JFK8 warehouse. We just walked out demanding better conditions. Will update as things develop. AMA.',
        'author': {
            'name': 'warehouse_worker_2024',
            'created_utc': 1640000000,  # ~2 years ago
            'link_karma': 450,
            'comment_karma': 2340,
            'is_employee': True,
            'account_age_days': 730
        },
        'created_utc': (datetime.utcnow() - timedelta(hours=2)).timestamp(),
        'score': 3456,
        'upvote_ratio': 0.94,
        'num_comments': 234,
        'subreddit': 'labor',
        'is_original_content': True
    },
    {
        'id': 'def456',
        'title': 'NYT: Amazon workers authorize strike vote',
        'selftext': '',
        'author': {
            'name': 'newsbot_labor',
            'created_utc': 1500000000,  # ~7 years ago
            'link_karma': 125000,
            'comment_karma': 8900,
            'is_employee': False,
            'account_age_days': 2555
        },
        'created_utc': (datetime.utcnow() - timedelta(hours=6)).timestamp(),
        'score': 8923,
        'upvote_ratio': 0.96,
        'num_comments': 456,
        'subreddit': 'WorkReform',
        'is_original_content': False,
        'url': 'https://nytimes.com/2024/article'
    },
    {
        'id': 'ghi789',
        'title': 'I was at the Amazon walkout today - here is what I saw',
        'selftext': 'As someone who was physically there, I can confirm that over 200 workers participated. The energy was incredible. Management looked shocked.',
        'author': {
            'name': 'eyewitness_account',
            'created_utc': 1704067200,  # ~1 year ago
            'link_karma': 12,
            'comment_karma': 145,
            'is_employee': False,
            'account_age_days': 365
        },
        'created_utc': (datetime.utcnow() - timedelta(hours=3)).timestamp(),
        'score': 567,
        'upvote_ratio': 0.89,
        'num_comments': 45,
        'subreddit': 'antiwork',
        'is_original_content': True
    }
]


def test_twitter_investigation_monitor():
    """Test TwitterInvestigationMonitor with extended search capabilities"""
    from backend.agents.investigation.twitter_investigation import TwitterInvestigationMonitor

    print("\n" + "=" * 80)
    print("TEST: TwitterInvestigationMonitor")
    print("=" * 80)

    # Initialize monitor with mock data
    monitor = TwitterInvestigationMonitor(use_mock_data=True)

    # Test 1: Extended search
    print("\n[1/5] Testing extended search...")
    query = "Amazon workers strike"
    results = monitor.search_extended(query, max_results=10)

    assert len(results) > 0, "Should return search results"
    print(f"  ✓ Found {len(results)} tweets")

    # Verify result structure
    for result in results:
        assert 'id' in result, "Result should have ID"
        assert 'text' in result, "Result should have text"
        assert 'author' in result, "Result should have author info"
        assert 'created_at' in result, "Result should have timestamp"
        assert 'metrics' in result, "Result should have engagement metrics"
    print("  ✓ All results have required fields")

    # Test 2: Hashtag tracking
    print("\n[2/5] Testing hashtag tracking...")
    hashtags = monitor.track_hashtags(['#UnionStrong', '#AmazonWorkers'])

    assert len(hashtags) > 0, "Should find posts with hashtags"
    print(f"  ✓ Found {len(hashtags)} posts with tracked hashtags")

    # Test 3: Original tweet filtering
    print("\n[3/5] Testing original tweet filtering...")
    original_tweets = monitor.filter_original_tweets(results)

    # Should exclude retweets and replies
    assert len(original_tweets) <= len(results), "Filtered count should be <= total"
    print(f"  ✓ Filtered to {len(original_tweets)} original tweets")

    # Test 4: Verified account filtering
    print("\n[4/5] Testing verified account filtering...")
    verified_tweets = monitor.filter_verified_accounts(results)

    verified_count = len(verified_tweets)
    print(f"  ✓ Found {verified_count} tweets from verified accounts")

    # Test 5: Timeline construction
    print("\n[5/5] Testing timeline construction...")
    timeline = monitor.construct_timeline(results)

    assert 'events' in timeline, "Timeline should have events list"
    assert 'earliest_mention' in timeline, "Timeline should identify earliest mention"
    assert 'latest_update' in timeline, "Timeline should identify latest update"

    # Events should be chronologically sorted
    events = timeline['events']
    if len(events) > 1:
        for i in range(len(events) - 1):
            assert events[i]['timestamp'] <= events[i+1]['timestamp'], "Events should be chronologically sorted"

    print(f"  ✓ Timeline constructed with {len(events)} events")
    print(f"  ✓ Earliest mention: {timeline['earliest_mention']}")
    print(f"  ✓ Latest update: {timeline['latest_update']}")

    print("\n✓ All TwitterInvestigationMonitor tests passed!")
    return True


def test_reddit_investigation_monitor():
    """Test RedditInvestigationMonitor with discussion thread analysis"""
    from backend.agents.investigation.reddit_investigation import RedditInvestigationMonitor

    print("\n" + "=" * 80)
    print("TEST: RedditInvestigationMonitor")
    print("=" * 80)

    # Initialize monitor with mock data
    monitor = RedditInvestigationMonitor(use_mock_data=True)

    # Test 1: Extended search
    print("\n[1/5] Testing extended search...")
    query = "Amazon strike"
    results = monitor.search_extended(query, subreddits=['labor', 'WorkReform', 'antiwork'])

    assert len(results) > 0, "Should return search results"
    print(f"  ✓ Found {len(results)} posts across subreddits")

    # Verify result structure
    for result in results:
        assert 'id' in result, "Result should have ID"
        assert 'title' in result, "Result should have title"
        assert 'author' in result, "Result should have author info"
        assert 'created_utc' in result, "Result should have timestamp"
        assert 'score' in result, "Result should have score"
        assert 'subreddit' in result, "Result should have subreddit"
    print("  ✓ All results have required fields")

    # Test 2: Discussion thread analysis
    print("\n[2/5] Testing discussion thread analysis...")
    for post in results[:2]:  # Test first 2 posts
        analysis = monitor.analyze_discussion_thread(post['id'])

        assert 'comment_count' in analysis, "Analysis should include comment count"
        assert 'top_comments' in analysis, "Analysis should include top comments"
        assert 'sentiment' in analysis, "Analysis should include sentiment"
        assert 'eyewitness_accounts' in analysis, "Analysis should identify eyewitness accounts"

        print(f"  ✓ Post '{post['title'][:50]}...':")
        print(f"    - Comments: {analysis['comment_count']}")
        print(f"    - Sentiment: {analysis['sentiment']}")
        print(f"    - Eyewitness accounts: {len(analysis['eyewitness_accounts'])}")

    # Test 3: Eyewitness account identification
    print("\n[3/5] Testing eyewitness account identification...")
    eyewitness_posts = monitor.identify_eyewitness_accounts(results)

    assert isinstance(eyewitness_posts, list), "Should return list of eyewitness posts"
    print(f"  ✓ Identified {len(eyewitness_posts)} eyewitness accounts")

    # Verify eyewitness markers
    for post in eyewitness_posts:
        assert post.get('is_eyewitness', False), "Should be marked as eyewitness"
        assert 'eyewitness_indicators' in post, "Should list eyewitness indicators"
        print(f"    - '{post['title'][:40]}...' indicators: {', '.join(post['eyewitness_indicators'])}")

    # Test 4: Original content filtering
    print("\n[4/5] Testing original content filtering...")
    original_posts = monitor.filter_original_content(results)

    assert len(original_posts) <= len(results), "Filtered count should be <= total"
    print(f"  ✓ Filtered to {len(original_posts)} original content posts")

    # Test 5: Timeline construction
    print("\n[5/5] Testing timeline construction...")
    timeline = monitor.construct_timeline(results)

    assert 'events' in timeline, "Timeline should have events list"
    assert 'earliest_post' in timeline, "Timeline should identify earliest post"
    assert 'latest_post' in timeline, "Timeline should identify latest post"

    events = timeline['events']
    print(f"  ✓ Timeline constructed with {len(events)} events")

    print("\n✓ All RedditInvestigationMonitor tests passed!")
    return True


def test_social_source_credibility():
    """Test SocialSourceCredibility scoring module"""
    from backend.agents.investigation.social_credibility import SocialSourceCredibility

    print("\n" + "=" * 80)
    print("TEST: SocialSourceCredibility")
    print("=" * 80)

    scorer = SocialSourceCredibility()

    # Test 1: Twitter account credibility
    print("\n[1/4] Testing Twitter account credibility scoring...")

    # High credibility: Verified news org
    twitter_verified = {
        'platform': 'twitter',
        'username': 'reuters',
        'verified': True,
        'created_at': '2008-03-10',
        'followers_count': 28000000,
        'description': 'Breaking news from Reuters'
    }
    score1 = scorer.score_source(twitter_verified)
    assert score1 >= 80, f"Verified news org should have high credibility (got {score1})"
    print(f"  ✓ Reuters (verified): {score1}/100")

    # Medium credibility: Established account, not verified
    twitter_established = {
        'platform': 'twitter',
        'username': 'worker_advocate',
        'verified': False,
        'created_at': '2020-01-15',
        'followers_count': 5432,
        'description': 'Labor organizer'
    }
    score2 = scorer.score_source(twitter_established)
    assert 50 <= score2 < 80, f"Established account should have medium credibility (got {score2})"
    print(f"  ✓ worker_advocate (4 years): {score2}/100")

    # Lower credibility: New account
    twitter_new = {
        'platform': 'twitter',
        'username': 'new_account_123',
        'verified': False,
        'created_at': '2023-12-01',
        'followers_count': 42,
        'description': ''
    }
    score3 = scorer.score_source(twitter_new)
    assert score3 < 50, f"New account should have lower credibility (got {score3})"
    print(f"  ✓ new_account_123 (new): {score3}/100")

    # Test 2: Reddit account credibility
    print("\n[2/4] Testing Reddit account credibility scoring...")

    # High credibility: Old account, high karma
    reddit_high = {
        'platform': 'reddit',
        'username': 'newsbot_labor',
        'account_age_days': 2555,
        'link_karma': 125000,
        'comment_karma': 8900
    }
    score4 = scorer.score_source(reddit_high)
    assert score4 >= 70, f"High karma account should have high credibility (got {score4})"
    print(f"  ✓ newsbot_labor (7 years, 133k karma): {score4}/100")

    # Medium credibility: Moderate age and karma
    reddit_medium = {
        'platform': 'reddit',
        'username': 'warehouse_worker_2024',
        'account_age_days': 730,
        'link_karma': 450,
        'comment_karma': 2340
    }
    score5 = scorer.score_source(reddit_medium)
    assert 40 <= score5 < 70, f"Medium karma account should have medium credibility (got {score5})"
    print(f"  ✓ warehouse_worker_2024 (2 years, 2.8k karma): {score5}/100")

    # Test 3: Engagement metrics
    print("\n[3/4] Testing engagement metrics scoring...")

    twitter_high_engagement = {
        'platform': 'twitter',
        'username': 'reuters',
        'verified': True,
        'created_at': '2008-03-10',
        'followers_count': 28000000,
        'engagement_metrics': {
            'retweet_count': 1200,
            'like_count': 3400,
            'reply_count': 230
        }
    }
    engagement_score = scorer.score_engagement(twitter_high_engagement)
    assert engagement_score > 0, "Should calculate engagement score"
    print(f"  ✓ Reuters tweet engagement: {engagement_score}/100")

    # Test 4: Combined credibility scoring
    print("\n[4/4] Testing combined credibility scoring...")

    combined_source = {
        'platform': 'twitter',
        'username': 'worker_advocate',
        'verified': False,
        'created_at': '2020-01-15',
        'followers_count': 5432,
        'engagement_metrics': {
            'retweet_count': 234,
            'like_count': 567,
            'reply_count': 45
        },
        'content': 'I was there when Amazon workers walked out today. They demanded better wages and safer conditions.',
        'content_indicators': {
            'firsthand_language': True,
            'specific_details': True,
            'emotional_tone': 'moderate'
        }
    }
    combined_score = scorer.score_combined(combined_source)
    assert isinstance(combined_score, dict), "Should return detailed scoring breakdown"
    assert 'total_score' in combined_score, "Should include total score"
    assert 'account_score' in combined_score, "Should include account score"
    assert 'engagement_score' in combined_score, "Should include engagement score"
    assert 'content_score' in combined_score, "Should include content score"

    print(f"  ✓ Combined scoring:")
    print(f"    - Total: {combined_score['total_score']}/100")
    print(f"    - Account: {combined_score['account_score']}/100")
    print(f"    - Engagement: {combined_score['engagement_score']}/100")
    print(f"    - Content: {combined_score['content_score']}/100")

    print("\n✓ All SocialSourceCredibility tests passed!")
    return True


def test_timeline_constructor():
    """Test TimelineConstructor for chronological event tracking"""
    from backend.agents.investigation.timeline_constructor import TimelineConstructor

    print("\n" + "=" * 80)
    print("TEST: TimelineConstructor")
    print("=" * 80)

    constructor = TimelineConstructor()

    # Test 1: Construct timeline from mixed sources
    print("\n[1/4] Testing timeline construction from mixed sources...")

    mixed_sources = []

    # Add Twitter posts
    for tweet in MOCK_TWITTER_POSTS:
        mixed_sources.append({
            'platform': 'twitter',
            'id': tweet['id'],
            'text': tweet['text'],
            'author': tweet['author']['username'],
            'timestamp': tweet['created_at'],
            'source_type': 'social_media'
        })

    # Add Reddit posts
    for post in MOCK_REDDIT_POSTS:
        mixed_sources.append({
            'platform': 'reddit',
            'id': post['id'],
            'text': post['title'] + ' ' + (post.get('selftext', '') or ''),
            'author': post['author']['name'],
            'timestamp': datetime.utcfromtimestamp(post['created_utc']),
            'source_type': 'social_media'
        })

    timeline = constructor.construct_timeline(mixed_sources)

    assert 'events' in timeline, "Timeline should have events"
    assert 'earliest_event' in timeline, "Timeline should identify earliest event"
    assert 'latest_event' in timeline, "Timeline should identify latest event"
    assert 'duration_hours' in timeline, "Timeline should calculate duration"

    print(f"  ✓ Timeline constructed with {len(timeline['events'])} events")
    print(f"  ✓ Earliest event: {timeline['earliest_event']['timestamp']}")
    print(f"  ✓ Latest event: {timeline['latest_event']['timestamp']}")
    print(f"  ✓ Duration: {timeline['duration_hours']:.1f} hours")

    # Test 2: Verify chronological ordering
    print("\n[2/4] Testing chronological ordering...")

    events = timeline['events']
    for i in range(len(events) - 1):
        assert events[i]['timestamp'] <= events[i+1]['timestamp'], "Events should be chronologically sorted"

    print(f"  ✓ All {len(events)} events in chronological order")

    # Test 3: Cluster related events
    print("\n[3/4] Testing event clustering...")

    clusters = constructor.cluster_related_events(timeline['events'])

    assert isinstance(clusters, list), "Should return list of clusters"
    assert len(clusters) > 0, "Should identify at least one cluster"

    print(f"  ✓ Identified {len(clusters)} event clusters")
    for i, cluster in enumerate(clusters, 1):
        print(f"    Cluster {i}: {len(cluster['events'])} events, theme: {cluster.get('theme', 'N/A')}")

    # Test 4: Identify key moments
    print("\n[4/4] Testing key moment identification...")

    key_moments = constructor.identify_key_moments(timeline)

    assert isinstance(key_moments, list), "Should return list of key moments"

    print(f"  ✓ Identified {len(key_moments)} key moments:")
    for moment in key_moments:
        print(f"    - {moment['timestamp']}: {moment['description'][:60]}...")
        print(f"      Significance: {moment['significance_score']}/100")

    print("\n✓ All TimelineConstructor tests passed!")
    return True


def test_eyewitness_detector():
    """Test EyewitnessDetector for firsthand account identification"""
    from backend.agents.investigation.eyewitness_detector import EyewitnessDetector

    print("\n" + "=" * 80)
    print("TEST: EyewitnessDetector")
    print("=" * 80)

    detector = EyewitnessDetector()

    # Test 1: Detect firsthand language
    print("\n[1/4] Testing firsthand language detection...")

    firsthand_texts = [
        "I was there when Amazon workers walked out today.",
        "Just saw this unfold firsthand at the warehouse.",
        "I work at JFK8 warehouse. We just walked out demanding better conditions."
    ]

    secondhand_texts = [
        "According to union sources, negotiations broke down this morning.",
        "NYT reports that Amazon workers are planning a strike.",
        "Sources say the company rejected union demands."
    ]

    for text in firsthand_texts:
        result = detector.detect_firsthand_language(text)
        assert result['is_firsthand'], f"Should detect firsthand language in: {text[:50]}"
        print(f"  ✓ Firsthand: '{text[:50]}...' - {result['confidence']:.0f}% confidence")

    for text in secondhand_texts:
        result = detector.detect_firsthand_language(text)
        assert not result['is_firsthand'], f"Should NOT detect firsthand language in: {text[:50]}"
        print(f"  ✓ Secondhand: '{text[:50]}...' - {result['confidence']:.0f}% confidence")

    # Test 2: Identify eyewitness accounts in posts
    print("\n[2/4] Testing eyewitness account identification...")

    all_posts = []

    # Add mock Twitter posts
    for tweet in MOCK_TWITTER_POSTS:
        all_posts.append({
            'platform': 'twitter',
            'text': tweet['text'],
            'author': tweet['author']
        })

    # Add mock Reddit posts
    for post in MOCK_REDDIT_POSTS:
        all_posts.append({
            'platform': 'reddit',
            'text': post['title'] + ' ' + (post.get('selftext', '') or ''),
            'author': post['author']
        })

    eyewitness_posts = detector.identify_eyewitness_posts(all_posts)

    assert len(eyewitness_posts) > 0, "Should identify at least one eyewitness account"
    print(f"  ✓ Identified {len(eyewitness_posts)} eyewitness accounts")

    for post in eyewitness_posts:
        assert 'eyewitness_score' in post, "Should include eyewitness score"
        assert 'indicators' in post, "Should list eyewitness indicators"
        print(f"    - {post['platform']}: '{post['text'][:40]}...'")
        print(f"      Score: {post['eyewitness_score']}/100")
        print(f"      Indicators: {', '.join(post['indicators'])}")

    # Test 3: Validate eyewitness credibility
    print("\n[3/4] Testing eyewitness credibility validation...")

    for post in eyewitness_posts:
        credibility = detector.validate_eyewitness_credibility(post)

        assert 'credibility_score' in credibility, "Should include credibility score"
        assert 'credibility_factors' in credibility, "Should list credibility factors"

        print(f"    - Credibility: {credibility['credibility_score']}/100")
        print(f"      Factors: {', '.join(credibility['credibility_factors'])}")

    # Test 4: Filter high-confidence eyewitness accounts
    print("\n[4/4] Testing high-confidence filtering...")

    high_confidence = detector.filter_high_confidence_eyewitness(eyewitness_posts, threshold=60)

    assert len(high_confidence) <= len(eyewitness_posts), "Filtered count should be <= total"
    print(f"  ✓ {len(high_confidence)} high-confidence eyewitness accounts (>60% confidence)")

    for account in high_confidence:
        print(f"    - {account['platform']}: {account['eyewitness_score']}/100")

    print("\n✓ All EyewitnessDetector tests passed!")
    return True


def test_integration_with_investigatory_agent():
    """Test integration of social media investigation with main InvestigatoryJournalistAgent"""
    from backend.agents.investigatory_journalist_agent import InvestigatoryJournalistAgent

    print("\n" + "=" * 80)
    print("TEST: Integration with InvestigatoryJournalistAgent")
    print("=" * 80)

    db = SessionLocal()

    try:
        # Find an unverified topic to test with
        unverified_topic = db.query(Topic).filter_by(verification_status='unverified').first()

        if not unverified_topic:
            print("  ⚠ No unverified topics found - creating mock topic for testing")
            # Would create mock topic here if needed
            return True

        print(f"\n[1/3] Testing social media investigation on topic: '{unverified_topic.title}'")

        # Initialize agent
        agent = InvestigatoryJournalistAgent(db)

        # Run investigation (should now include social media search)
        result = agent.investigate(unverified_topic.id)

        if result:
            assert hasattr(result, 'social_media_findings'), "Result should include social media findings"

            social_findings = result.social_media_findings

            print(f"\n[2/3] Social media findings:")
            print(f"  - Twitter posts found: {social_findings.get('twitter_post_count', 0)}")
            print(f"  - Reddit posts found: {social_findings.get('reddit_post_count', 0)}")
            print(f"  - Eyewitness accounts: {len(social_findings.get('eyewitness_accounts', []))}")
            print(f"  - Timeline events: {len(social_findings.get('timeline_events', []))}")

            # Test 3: Verify social sources added to investigation result
            print(f"\n[3/3] Verifying social sources added to investigation...")

            assert result.additional_sources is not None, "Should have additional sources"

            # Count social media sources
            social_sources = [s for s in result.additional_sources if s.source_type in ['twitter', 'reddit']]

            print(f"  ✓ {len(social_sources)} social media sources added")
            print(f"  ✓ Total credibility score: {result.credibility_score:.1f}/100")

            print("\n✓ Integration test passed!")
        else:
            print("  ⚠ Investigation returned no result (topic may not need investigation)")

        return True

    finally:
        db.close()


def main():
    """Run all social media investigation tests"""
    print("\n" + "=" * 80)
    print("SOCIAL MEDIA INVESTIGATION TEST SUITE (Phase 6.9.2)")
    print("=" * 80)

    tests = [
        ("TwitterInvestigationMonitor", test_twitter_investigation_monitor),
        ("RedditInvestigationMonitor", test_reddit_investigation_monitor),
        ("SocialSourceCredibility", test_social_source_credibility),
        ("TimelineConstructor", test_timeline_constructor),
        ("EyewitnessDetector", test_eyewitness_detector),
        ("Integration with InvestigatoryJournalistAgent", test_integration_with_investigatory_agent),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}")
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {str(e)}")
            results.append((test_name, False, str(e)))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, success, _ in results if success)
    failed = len(results) - passed

    for test_name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"  Error: {error}")

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if failed > 0:
        print(f"\n⚠ {failed} test(s) failed - fix issues before proceeding")
        return False
    else:
        print("\n✓ All tests passed! Ready to implement.")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
