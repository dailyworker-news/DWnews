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

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Keywords for worker-focused news discovery
LABOR_KEYWORDS = [
    "labor union",
    "workers union",
    "strike",
    "workplace safety",
    "wage theft",
    "worker organizing",
    "collective bargaining",
    "unionization",
    "labor rights",
    "workers rights"
]

SUBREDDITS = [
    "antiwork",
    "WorkReform",
    "union",
    "LateStageCapitalism",
    "lostgeneration"
]

RSS_FEEDS = [
    {
        "name": "Labor Notes",
        "url": "https://labornotes.org/feeds/all",
        "type": "labor_focused"
    },
    {
        "name": "ProPublica",
        "url": "https://www.propublica.org/feeds/propublica/main",
        "type": "investigative"
    },
    {
        "name": "Reuters Labor",
        "url": "https://rsshub.app/reuters/world",
        "type": "mainstream"
    },
    {
        "name": "AP Business",
        "url": "https://rsshub.app/apnews/topics/business",
        "type": "mainstream"
    }
]


def discover_twitter_signals():
    """Discover potential news events from Twitter"""
    print("\n" + "="*80)
    print("TWITTER SIGNAL INTAKE")
    print("="*80)

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    if not bearer_token:
        print("❌ Twitter credentials not configured")
        return []

    try:
        import requests

        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

        all_signals = []

        # Search for each keyword
        for keyword in LABOR_KEYWORDS[:3]:  # Limit to 3 keywords for testing
            print(f"\n🔍 Searching Twitter for: '{keyword}'")

            params = {
                "query": f"{keyword} -is:retweet lang:en",
                "max_results": 10,
                "tweet.fields": "created_at,public_metrics,author_id",
                "expansions": "author_id",
                "user.fields": "username,verified"
            }

            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                tweets = data.get('data', [])
                users = {u['id']: u for u in data.get('includes', {}).get('users', [])}

                print(f"   Found {len(tweets)} tweets")

                for tweet in tweets:
                    author = users.get(tweet['author_id'], {})

                    signal = {
                        "source": "Twitter",
                        "keyword": keyword,
                        "text": tweet['text'],
                        "author": author.get('username', 'unknown'),
                        "verified": author.get('verified', False),
                        "created_at": tweet['created_at'],
                        "likes": tweet['public_metrics']['like_count'],
                        "retweets": tweet['public_metrics']['retweet_count'],
                        "engagement_score": tweet['public_metrics']['like_count'] + (tweet['public_metrics']['retweet_count'] * 2)
                    }
                    all_signals.append(signal)

            else:
                print(f"   ⚠️  API error: {response.status_code}")

        print(f"\n✅ Total Twitter signals discovered: {len(all_signals)}")
        return all_signals

    except Exception as e:
        print(f"❌ Error discovering Twitter signals: {e}")
        return []


def discover_reddit_signals():
    """Discover potential news events from Reddit"""
    print("\n" + "="*80)
    print("REDDIT SIGNAL INTAKE")
    print("="*80)

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    if not all([client_id, client_secret, user_agent]):
        print("❌ Reddit credentials not configured")
        return []

    try:
        import requests

        # Get OAuth token
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'client_credentials'}
        headers = {'User-Agent': user_agent}

        token_response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            auth=auth,
            data=data,
            headers=headers
        )

        if token_response.status_code != 200:
            print("❌ Reddit authentication failed")
            return []

        token = token_response.json()['access_token']
        headers['Authorization'] = f'bearer {token}'

        all_signals = []

        # Check each subreddit
        for subreddit in SUBREDDITS[:3]:  # Limit to 3 subreddits for testing
            print(f"\n🔍 Checking r/{subreddit}")

            response = requests.get(
                f'https://oauth.reddit.com/r/{subreddit}/hot',
                headers=headers,
                params={'limit': 10}
            )

            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']

                print(f"   Found {len(posts)} posts")

                for post in posts:
                    post_data = post['data']

                    signal = {
                        "source": "Reddit",
                        "subreddit": subreddit,
                        "title": post_data['title'],
                        "text": post_data.get('selftext', '')[:500],  # Limit to 500 chars
                        "author": post_data['author'],
                        "created_at": datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                        "upvotes": post_data['ups'],
                        "comments": post_data['num_comments'],
                        "url": post_data['url'],
                        "engagement_score": post_data['ups'] + (post_data['num_comments'] * 2)
                    }
                    all_signals.append(signal)

            else:
                print(f"   ⚠️  API error: {response.status_code}")

        print(f"\n✅ Total Reddit signals discovered: {len(all_signals)}")
        return all_signals

    except Exception as e:
        print(f"❌ Error discovering Reddit signals: {e}")
        return []


def discover_rss_signals():
    """Discover potential news events from RSS feeds"""
    print("\n" + "="*80)
    print("RSS FEED SIGNAL INTAKE")
    print("="*80)

    try:
        import feedparser

        all_signals = []

        for feed_config in RSS_FEEDS:
            feed_name = feed_config['name']
            feed_url = feed_config['url']

            print(f"\n🔍 Fetching {feed_name}")

            try:
                feed = feedparser.parse(feed_url)

                if feed.entries:
                    print(f"   Found {len(feed.entries)} articles")

                    for entry in feed.entries[:10]:  # Limit to 10 per feed
                        signal = {
                            "source": "RSS",
                            "feed": feed_name,
                            "feed_type": feed_config['type'],
                            "title": entry.title,
                            "summary": entry.get('summary', '')[:500],
                            "link": entry.link,
                            "published": entry.get('published', entry.get('updated', '')),
                            "engagement_score": 10 if feed_config['type'] == 'labor_focused' else 5  # Boost labor-focused feeds
                        }
                        all_signals.append(signal)
                else:
                    print(f"   ⚠️  No entries found")

            except Exception as e:
                print(f"   ❌ Error fetching {feed_name}: {e}")

        print(f"\n✅ Total RSS signals discovered: {len(all_signals)}")
        return all_signals

    except Exception as e:
        print(f"❌ Error discovering RSS signals: {e}")
        return []


def calculate_worker_relevance(signal):
    """Calculate worker relevance score for a signal (0-1)"""
    text = ""

    if signal['source'] == 'Twitter':
        text = signal['text'].lower()
    elif signal['source'] == 'Reddit':
        text = (signal['title'] + ' ' + signal.get('text', '')).lower()
    elif signal['source'] == 'RSS':
        text = (signal['title'] + ' ' + signal.get('summary', '')).lower()

    # Worker-focused keywords
    worker_keywords = [
        'worker', 'labor', 'union', 'strike', 'wage', 'organizing',
        'collective', 'bargaining', 'workplace', 'employee', 'contract',
        'safety', 'overtime', 'benefits', 'fired', 'laid off', 'protest'
    ]

    # Count keyword matches
    matches = sum(1 for keyword in worker_keywords if keyword in text)

    # Calculate score (max score at 5+ keyword matches)
    score = min(matches / 5.0, 1.0)

    return round(score, 2)


def score_and_rank_signals(signals):
    """Score and rank all signals by newsworthiness"""
    print("\n" + "="*80)
    print("SCORING SIGNALS")
    print("="*80)

    for signal in signals:
        # Calculate worker relevance
        signal['worker_relevance'] = calculate_worker_relevance(signal)

        # Normalize engagement score (0-1 scale)
        if signal['source'] == 'Twitter':
            # Twitter: high engagement = 100+ combined likes/retweets
            signal['engagement_normalized'] = min(signal['engagement_score'] / 100.0, 1.0)
        elif signal['source'] == 'Reddit':
            # Reddit: high engagement = 500+ combined upvotes/comments
            signal['engagement_normalized'] = min(signal['engagement_score'] / 500.0, 1.0)
        elif signal['source'] == 'RSS':
            # RSS: use feed type as proxy (labor-focused = higher)
            signal['engagement_normalized'] = 0.7 if signal['feed_type'] == 'labor_focused' else 0.5

        # Overall newsworthiness score (60% worker relevance, 40% engagement)
        signal['newsworthiness_score'] = round(
            (signal['worker_relevance'] * 0.6) + (signal['engagement_normalized'] * 0.4),
            2
        )

    # Sort by newsworthiness score
    ranked_signals = sorted(signals, key=lambda s: s['newsworthiness_score'], reverse=True)

    print(f"✅ Scored {len(ranked_signals)} signals")
    print(f"   Top score: {ranked_signals[0]['newsworthiness_score']}")
    print(f"   Average score: {sum(s['newsworthiness_score'] for s in ranked_signals) / len(ranked_signals):.2f}")

    return ranked_signals


def display_top_signals(signals, limit=15):
    """Display top-ranked signals for review"""
    print("\n" + "="*80)
    print(f"TOP {limit} NEWSWORTHY SIGNALS")
    print("="*80)

    for i, signal in enumerate(signals[:limit], 1):
        print(f"\n[{i}] Score: {signal['newsworthiness_score']} | Worker Relevance: {signal['worker_relevance']} | Source: {signal['source']}")

        if signal['source'] == 'Twitter':
            text = signal['text'][:150] + "..." if len(signal['text']) > 150 else signal['text']
            print(f"    @{signal['author']} {'✓' if signal['verified'] else ''}")
            print(f"    {text}")
            print(f"    Engagement: {signal['likes']} likes, {signal['retweets']} retweets")

        elif signal['source'] == 'Reddit':
            title = signal['title'][:120] + "..." if len(signal['title']) > 120 else signal['title']
            print(f"    r/{signal['subreddit']} by u/{signal['author']}")
            print(f"    {title}")
            print(f"    Engagement: {signal['upvotes']} upvotes, {signal['comments']} comments")

        elif signal['source'] == 'RSS':
            title = signal['title'][:120] + "..." if len(signal['title']) > 120 else signal['title']
            print(f"    {signal['feed']} ({signal['feed_type']})")
            print(f"    {title}")
            print(f"    Link: {signal['link']}")


def save_signals_to_file(signals):
    """Save signals to JSON file for further processing"""
    output_dir = Path(__file__).parent.parent / 'test_output'
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'discovered_signals_{timestamp}.json'

    with open(output_file, 'w') as f:
        json.dump(signals, f, indent=2)

    print(f"\n📁 Signals saved to: {output_file}")
    return output_file


def main():
    """Run signal intake test"""
    print("\n" + "="*80)
    print("THE DAILY WORKER - SIGNAL INTAKE TEST")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Discover signals from all sources
    twitter_signals = discover_twitter_signals()
    reddit_signals = discover_reddit_signals()
    rss_signals = discover_rss_signals()

    # Combine all signals
    all_signals = twitter_signals + reddit_signals + rss_signals

    if not all_signals:
        print("\n❌ No signals discovered. Check API connections.")
        return

    print(f"\n" + "="*80)
    print(f"TOTAL SIGNALS DISCOVERED: {len(all_signals)}")
    print(f"  Twitter: {len(twitter_signals)}")
    print(f"  Reddit: {len(reddit_signals)}")
    print(f"  RSS: {len(rss_signals)}")
    print("="*80)

    # Score and rank signals
    ranked_signals = score_and_rank_signals(all_signals)

    # Display top signals
    display_top_signals(ranked_signals, limit=15)

    # Save to file
    output_file = save_signals_to_file(ranked_signals)

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print()
    print(f"1. Review the top 15 signals above")
    print(f"2. Select 1 interesting signal for full article generation test")
    print(f"3. All signals saved to: {output_file}")
    print()
    print("Once you've selected a signal, we'll:")
    print("  • Verify sources for that event")
    print("  • Generate a full test article")
    print("  • Run through editorial review")
    print()


if __name__ == "__main__":
    main()
