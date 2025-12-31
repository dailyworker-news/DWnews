#!/usr/bin/env python3
"""
Test API connections for Twitter, Reddit, and RSS feeds
Verifies that all credentials are valid before running full pipeline tests
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

def test_twitter_api():
    """Test Twitter API v2 connection"""
    print("\n" + "="*80)
    print("TESTING TWITTER API v2")
    print("="*80)

    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

    if not bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not found in .env.local")
        print("   Please add your Twitter API credentials")
        return False

    try:
        import requests

        # Twitter API v2 endpoint for recent search
        url = "https://api.twitter.com/2/tweets/search/recent"

        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

        # Search for recent tweets about labor unions (test query)
        params = {
            "query": "labor union OR workers union -is:retweet",
            "max_results": 10,
            "tweet.fields": "created_at,public_metrics,author_id"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            tweet_count = len(data.get('data', []))

            print(f"✅ Twitter API connection successful")
            print(f"   Retrieved {tweet_count} tweets about labor unions")
            print()

            if tweet_count > 0:
                print("Sample tweets:")
                for i, tweet in enumerate(data['data'][:3], 1):
                    text = tweet['text'][:100] + "..." if len(tweet['text']) > 100 else tweet['text']
                    likes = tweet['public_metrics']['like_count']
                    retweets = tweet['public_metrics']['retweet_count']
                    print(f"  {i}. {text}")
                    print(f"     Likes: {likes}, Retweets: {retweets}")
                    print()

            return True
        else:
            print(f"❌ Twitter API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except ImportError:
        print("❌ 'requests' library not installed")
        print("   Run: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error testing Twitter API: {e}")
        return False


def test_reddit_api():
    """Test Reddit API connection"""
    print("\n" + "="*80)
    print("TESTING REDDIT API")
    print("="*80)

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    if not all([client_id, client_secret, user_agent]):
        print("❌ Reddit credentials not found in .env.local")
        print("   Missing one or more of: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT")
        return False

    try:
        import requests

        # Get OAuth token
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        data = {
            'grant_type': 'client_credentials'
        }
        headers = {
            'User-Agent': user_agent
        }

        token_response = requests.post(
            'https://www.reddit.com/api/v1/access_token',
            auth=auth,
            data=data,
            headers=headers
        )

        if token_response.status_code != 200:
            print(f"❌ Reddit authentication failed: {token_response.status_code}")
            print(f"   Response: {token_response.text}")
            return False

        token = token_response.json()['access_token']

        # Test API call - get posts from r/antiwork
        headers['Authorization'] = f'bearer {token}'

        response = requests.get(
            'https://oauth.reddit.com/r/antiwork/hot',
            headers=headers,
            params={'limit': 10}
        )

        if response.status_code == 200:
            data = response.json()
            posts = data['data']['children']

            print(f"✅ Reddit API connection successful")
            print(f"   Retrieved {len(posts)} posts from r/antiwork")
            print()

            if posts:
                print("Sample posts:")
                for i, post in enumerate(posts[:3], 1):
                    post_data = post['data']
                    title = post_data['title'][:80] + "..." if len(post_data['title']) > 80 else post_data['title']
                    upvotes = post_data['ups']
                    comments = post_data['num_comments']
                    print(f"  {i}. {title}")
                    print(f"     Upvotes: {upvotes}, Comments: {comments}")
                    print()

            return True
        else:
            print(f"❌ Reddit API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except ImportError:
        print("❌ 'requests' library not installed")
        print("   Run: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Error testing Reddit API: {e}")
        return False


def test_rss_feeds():
    """Test RSS feed parsing"""
    print("\n" + "="*80)
    print("TESTING RSS FEEDS (No Authentication Required)")
    print("="*80)

    test_feeds = [
        ("Labor Notes", "https://labornotes.org/feeds/all"),
        ("ProPublica", "https://www.propublica.org/feeds/propublica/main"),
        ("AP News", "https://rsshub.app/apnews/topics/business")
    ]

    try:
        import feedparser

        for feed_name, feed_url in test_feeds:
            print(f"\n📡 Testing {feed_name}...")

            try:
                feed = feedparser.parse(feed_url)

                if feed.entries:
                    print(f"✅ {feed_name}: {len(feed.entries)} articles retrieved")

                    # Show sample article
                    first = feed.entries[0]
                    title = first.title[:80] + "..." if len(first.title) > 80 else first.title
                    print(f"   Latest: {title}")
                else:
                    print(f"⚠️  {feed_name}: No entries found (feed may be down)")

            except Exception as e:
                print(f"❌ {feed_name} error: {e}")

        print()
        return True

    except ImportError:
        print("❌ 'feedparser' library not installed")
        print("   Run: pip install feedparser")
        return False
    except Exception as e:
        print(f"❌ Error testing RSS feeds: {e}")
        return False


def test_llm_api():
    """Test LLM API connection (Claude, OpenAI, or Google)"""
    print("\n" + "="*80)
    print("TESTING LLM API")
    print("="*80)

    # Check which LLM API is configured
    claude_key = os.getenv('CLAUDE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')

    if not any([claude_key, openai_key, google_key]):
        print("⚠️  No LLM API key found in .env.local")
        print("   This is optional if you already have LLM access configured elsewhere")
        print("   Skipping LLM test...")
        return True

    # Test whichever API is configured
    if claude_key:
        print("📡 Testing Claude API...")
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=claude_key)

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[
                    {"role": "user", "content": "Say 'API connection successful' in exactly 3 words."}
                ]
            )

            response_text = message.content[0].text
            print(f"✅ Claude API connection successful")
            print(f"   Test response: {response_text}")
            return True

        except ImportError:
            print("❌ 'anthropic' library not installed")
            print("   Run: pip install anthropic")
            return False
        except Exception as e:
            print(f"❌ Claude API error: {e}")
            return False

    elif openai_key:
        print("📡 Testing OpenAI API...")
        try:
            from openai import OpenAI

            client = OpenAI(api_key=openai_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'API connection successful' in exactly 3 words."}
                ],
                max_tokens=50
            )

            response_text = response.choices[0].message.content
            print(f"✅ OpenAI API connection successful")
            print(f"   Test response: {response_text}")
            return True

        except ImportError:
            print("❌ 'openai' library not installed")
            print("   Run: pip install openai")
            return False
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return False

    elif google_key:
        print("📡 Testing Google Gemini API...")
        try:
            import google.generativeai as genai

            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-pro')

            response = model.generate_content("Say 'API connection successful' in exactly 3 words.")

            print(f"✅ Google Gemini API connection successful")
            print(f"   Test response: {response.text}")
            return True

        except ImportError:
            print("❌ 'google-generativeai' library not installed")
            print("   Run: pip install google-generativeai")
            return False
        except Exception as e:
            print(f"❌ Google Gemini API error: {e}")
            return False


def main():
    """Run all API connection tests"""
    print("\n" + "="*80)
    print("THE DAILY WORKER - API CONNECTION TESTS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if .env.local exists
    env_path = Path(__file__).parent.parent / '.env.local'
    if not env_path.exists():
        print("❌ .env.local file not found!")
        print(f"   Expected location: {env_path}")
        print()
        print("Please create .env.local with your API credentials.")
        print("See API_CREDENTIALS_SETUP.md for instructions.")
        return

    print(f"✅ Found .env.local at: {env_path}")

    # Run all tests
    results = {
        "Twitter": test_twitter_api(),
        "Reddit": test_reddit_api(),
        "RSS Feeds": test_rss_feeds(),
        "LLM": test_llm_api()
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service}: {status}")

    all_required_passed = results["Twitter"] and results["Reddit"] and results["RSS Feeds"]

    print()
    if all_required_passed:
        print("="*80)
        print("🎉 ALL REQUIRED API CONNECTIONS SUCCESSFUL!")
        print("="*80)
        print()
        print("You're ready to run signal intake tests with live data.")
        print()
        print("Next step: python scripts/test_signal_intake.py")
        print()
    else:
        print("="*80)
        print("⚠️  SOME TESTS FAILED")
        print("="*80)
        print()
        print("Please fix the failed connections before proceeding.")
        print("See API_CREDENTIALS_SETUP.md for help obtaining credentials.")
        print()


if __name__ == "__main__":
    main()
