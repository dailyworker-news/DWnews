"""
Twitter Investigation Monitor for Investigatory Journalist Agent (Phase 6.9.2)

Extended Twitter search capabilities for deep investigation:
- Hashtag tracking (find all mentions of specific hashtags)
- Original tweet filtering (exclude retweets and replies)
- Verified account filtering (prioritize verified sources)
- Timeline construction (chronological event tracking)
- Engagement metrics analysis
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tweepy
from tweepy.errors import TweepyException

logger = logging.getLogger(__name__)


class TwitterInvestigationMonitor:
    """
    Extended Twitter search and analysis for investigatory journalism.

    Builds on TwitterFeedMonitor with deeper investigation capabilities:
    - Extended search across multiple time periods
    - Hashtag tracking for event-related discussions
    - Original tweet filtering (no retweets/replies)
    - Verified account prioritization
    - Timeline construction from mentions
    """

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        max_results_per_query: int = 100,
        max_age_days: int = 7,
        use_mock_data: bool = False
    ):
        """
        Initialize Twitter investigation monitor.

        Args:
            bearer_token: Twitter API v2 Bearer Token (defaults to env var)
            max_results_per_query: Max tweets to fetch per search query (default: 100)
            max_age_days: Only fetch tweets from last N days (default: 7)
            use_mock_data: If True, generate mock data instead of API calls
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.max_results = max_results_per_query
        self.max_age_days = max_age_days
        self.cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        self.use_mock_data = use_mock_data

        # Initialize Twitter API client
        self.client = None
        if not self.use_mock_data:
            if self.bearer_token and self.bearer_token != 'your_twitter_bearer_token':
                try:
                    self.client = tweepy.Client(bearer_token=self.bearer_token)
                    logger.info("Twitter API v2 client initialized for investigation")
                except Exception as e:
                    logger.error(f"Failed to initialize Twitter API client: {str(e)}")
                    logger.warning("Falling back to mock data mode")
                    self.use_mock_data = True
            else:
                logger.warning("Twitter Bearer Token not configured - using mock data mode")
                self.use_mock_data = True

    def search_extended(
        self,
        query: str,
        max_results: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform extended Twitter search with advanced filtering.

        Args:
            query: Search query string
            max_results: Override default max results
            start_time: Optional start time for search window
            end_time: Optional end time for search window

        Returns:
            List of tweet dictionaries with full metadata
        """
        if self.use_mock_data:
            return self._generate_mock_search_results(query)

        if not self.client:
            logger.warning("Twitter client not initialized")
            return []

        results = []
        max_results = max_results or self.max_results

        # Default time window: last N days
        if not start_time:
            start_time = self.cutoff_date
        if not end_time:
            end_time = datetime.utcnow()

        try:
            response = self.client.search_recent_tweets(
                query=query,
                start_time=start_time,
                end_time=end_time,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities', 'referenced_tweets'],
                expansions=['author_id', 'referenced_tweets.id'],
                user_fields=['username', 'verified', 'created_at', 'public_metrics', 'description']
            )

            if not response.data:
                return results

            # Create user lookup dict
            users = {user.id: user for user in (response.includes.get('users', []) if response.includes else [])}

            # Process tweets
            for tweet in response.data:
                tweet_dict = self._extract_tweet_data(tweet, users)
                if tweet_dict:
                    results.append(tweet_dict)

        except TweepyException as e:
            logger.error(f"Twitter API error searching '{query}': {str(e)}")
        except Exception as e:
            logger.error(f"Error processing tweets for '{query}': {str(e)}", exc_info=True)

        return results

    def track_hashtags(self, hashtags: List[str], max_results_per_tag: int = 50) -> List[Dict[str, Any]]:
        """
        Track specific hashtags for event-related discussions.

        Args:
            hashtags: List of hashtags to track (e.g., ['#UnionStrong', '#Strike'])
            max_results_per_tag: Max results per hashtag

        Returns:
            List of tweet dictionaries
        """
        all_results = []
        seen_ids = set()

        for hashtag in hashtags:
            # Ensure hashtag starts with #
            if not hashtag.startswith('#'):
                hashtag = f'#{hashtag}'

            logger.info(f"Tracking hashtag: {hashtag}")

            # Search for hashtag
            query = f"{hashtag} -is:retweet"  # Exclude retweets for original content
            results = self.search_extended(query, max_results=max_results_per_tag)

            # Deduplicate
            for result in results:
                if result['id'] not in seen_ids:
                    all_results.append(result)
                    seen_ids.add(result['id'])

        logger.info(f"Total unique tweets from {len(hashtags)} hashtags: {len(all_results)}")
        return all_results

    def filter_original_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter to only original tweets (exclude retweets and replies).

        Args:
            tweets: List of tweet dictionaries

        Returns:
            Filtered list containing only original tweets
        """
        original = []

        for tweet in tweets:
            # Check if it's a retweet or reply
            is_retweet = 'retweeted_status' in tweet or tweet.get('text', '').startswith('RT @')
            is_reply = tweet.get('in_reply_to_user_id') or tweet.get('referenced_tweets')

            if not is_retweet and not is_reply:
                original.append(tweet)

        return original

    def filter_verified_accounts(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter to only tweets from verified accounts.

        Args:
            tweets: List of tweet dictionaries

        Returns:
            Filtered list containing only tweets from verified accounts
        """
        verified = []

        for tweet in tweets:
            author = tweet.get('author', {})
            if author.get('verified', False):
                verified.append(tweet)

        return verified

    def construct_timeline(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct chronological timeline from tweets.

        Args:
            tweets: List of tweet dictionaries

        Returns:
            Timeline dictionary with sorted events, earliest/latest mentions, duration
        """
        if not tweets:
            return {
                'events': [],
                'earliest_mention': None,
                'latest_update': None,
                'duration_hours': 0
            }

        # Sort tweets by timestamp
        sorted_tweets = sorted(tweets, key=lambda t: t['created_at'])

        # Build events list
        events = []
        for tweet in sorted_tweets:
            events.append({
                'timestamp': tweet['created_at'],
                'platform': 'twitter',
                'id': tweet['id'],
                'text': tweet['text'],
                'author': tweet.get('author', {}).get('username', 'unknown'),
                'verified': tweet.get('author', {}).get('verified', False),
                'engagement': tweet.get('metrics', {})
            })

        # Calculate timeline metadata
        earliest = sorted_tweets[0]['created_at']
        latest = sorted_tweets[-1]['created_at']
        duration = (latest - earliest).total_seconds() / 3600  # hours

        return {
            'events': events,
            'earliest_mention': earliest.isoformat(),
            'latest_update': latest.isoformat(),
            'duration_hours': duration,
            'total_events': len(events)
        }

    def _extract_tweet_data(self, tweet, users: Dict) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from a tweet object.

        Args:
            tweet: Tweet object from Twitter API
            users: User lookup dictionary

        Returns:
            Tweet dictionary or None
        """
        try:
            # Get user info
            user = users.get(tweet.author_id)
            if not user:
                return None

            # Extract tweet data
            tweet_dict = {
                'id': str(tweet.id),
                'text': tweet.text,
                'created_at': tweet.created_at,
                'author': {
                    'username': user.username,
                    'verified': user.verified,
                    'created_at': str(user.created_at) if hasattr(user, 'created_at') else None,
                    'followers_count': user.public_metrics.get('followers_count', 0) if hasattr(user, 'public_metrics') else 0,
                    'description': user.description if hasattr(user, 'description') else ''
                },
                'metrics': {
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                    'like_count': tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                    'reply_count': tweet.public_metrics.get('reply_count', 0) if hasattr(tweet, 'public_metrics') else 0,
                    'quote_count': tweet.public_metrics.get('quote_count', 0) if hasattr(tweet, 'public_metrics') else 0
                },
                'entities': {
                    'hashtags': [tag.get('tag', '') for tag in (tweet.entities.get('hashtags', []) if hasattr(tweet, 'entities') and tweet.entities else [])]
                }
            }

            # Check if it's a reply or retweet
            if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
                tweet_dict['referenced_tweets'] = tweet.referenced_tweets
                tweet_dict['in_reply_to_user_id'] = tweet.referenced_tweets[0].id if tweet.referenced_tweets else None

            return tweet_dict

        except Exception as e:
            logger.error(f"Error extracting tweet data: {str(e)}", exc_info=True)
            return None

    def _generate_mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Generate mock search results for testing.

        Args:
            query: Search query (used to vary mock data)

        Returns:
            List of mock tweet dictionaries
        """
        logger.info(f"Generating mock Twitter data for query: '{query}'")

        mock_tweets = [
            {
                'id': '1234567890',
                'text': f'I was there when the event happened. {query} is a major development. #Breaking',
                'created_at': datetime.utcnow() - timedelta(hours=2),
                'author': {
                    'username': 'eyewitness_reporter',
                    'verified': False,
                    'created_at': '2020-01-15',
                    'followers_count': 1234,
                    'description': 'Independent journalist'
                },
                'metrics': {
                    'retweet_count': 45,
                    'like_count': 123,
                    'reply_count': 12,
                    'quote_count': 3
                },
                'entities': {
                    'hashtags': ['Breaking']
                }
            },
            {
                'id': '1234567891',
                'text': f'Reuters: {query} confirmed by official sources. Full story at link.',
                'created_at': datetime.utcnow() - timedelta(hours=4),
                'author': {
                    'username': 'reuters',
                    'verified': True,
                    'created_at': '2008-03-10',
                    'followers_count': 28000000,
                    'description': 'Breaking news from Reuters'
                },
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
                'text': f'Just witnessed this firsthand. {query} - workers are organizing. Very powerful.',
                'created_at': datetime.utcnow() - timedelta(hours=1),
                'author': {
                    'username': 'local_activist',
                    'verified': False,
                    'created_at': '2019-06-01',
                    'followers_count': 567,
                    'description': 'Labor organizer'
                },
                'metrics': {
                    'retweet_count': 23,
                    'like_count': 89,
                    'reply_count': 5,
                    'quote_count': 1
                },
                'entities': {
                    'hashtags': []
                }
            }
        ]

        return mock_tweets


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Use mock data for testing
    monitor = TwitterInvestigationMonitor(use_mock_data=True)

    # Test extended search
    print("\n=== Extended Search ===")
    results = monitor.search_extended("Amazon workers strike")
    print(f"Found {len(results)} tweets")

    # Test hashtag tracking
    print("\n=== Hashtag Tracking ===")
    hashtag_results = monitor.track_hashtags(['#UnionStrong', '#AmazonWorkers'])
    print(f"Found {len(hashtag_results)} tweets with hashtags")

    # Test filtering
    print("\n=== Filtering ===")
    original = monitor.filter_original_tweets(results)
    verified = monitor.filter_verified_accounts(results)
    print(f"Original tweets: {len(original)}")
    print(f"Verified accounts: {len(verified)}")

    # Test timeline construction
    print("\n=== Timeline Construction ===")
    timeline = monitor.construct_timeline(results)
    print(f"Timeline events: {timeline['total_events']}")
    print(f"Duration: {timeline['duration_hours']:.1f} hours")
