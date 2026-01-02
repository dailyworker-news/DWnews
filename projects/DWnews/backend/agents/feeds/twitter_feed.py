"""
Twitter Feed Monitor for Signal Intake Agent.

Discovers newsworthy labor events from Twitter using API v2:
- Trending labor topics and hashtags
- Worker organizing updates
- Union announcements
- Labor movement discussions
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import tweepy
from tweepy.errors import TweepyException

logger = logging.getLogger(__name__)


class TwitterFeedMonitor:
    """Monitors Twitter for labor-related news and events."""

    # Labor-focused hashtags and search terms
    LABOR_HASHTAGS = [
        '#UnionStrong',
        '#WorkersRights',
        '#LaborMovement',
        '#1u',
        '#SolidarityForever',
        '#UnionYes',
        '#OrganizeYourWorkplace',
        '#StrikeAction',
        '#CollectiveBargaining',
        '#FightFor15',
        '#LivingWage',
        '#WorkplaceRights',
    ]

    SEARCH_QUERIES = [
        'union strike',
        'workers organizing',
        'labor union',
        'collective bargaining',
        'workplace rights',
        'union victory',
        'labor action',
        'worker solidarity',
        'union contract',
        'labor organizing',
    ]

    # Verified labor accounts to monitor
    LABOR_ACCOUNTS = [
        'AFLCIO',           # AFL-CIO
        'SEIU',             # Service Employees International Union
        'Teamsters',        # International Brotherhood of Teamsters
        'UFCW',             # United Food and Commercial Workers
        'UAW',              # United Auto Workers
        'AFSCME',           # American Federation of State, County and Municipal Employees
        'RWDSUnion',        # Retail, Wholesale and Department Store Union
        'IATSE',            # International Alliance of Theatrical Stage Employees
        'SBWorkersUnited',  # Starbucks Workers United
        'amazonlabor',      # Amazon Labor Union
    ]

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        max_results_per_query: int = 25,
        max_age_hours: int = 24
    ):
        """
        Initialize Twitter feed monitor.

        Args:
            bearer_token: Twitter API v2 Bearer Token (defaults to env var)
            max_results_per_query: Max tweets to fetch per search query (default: 25)
            max_age_hours: Only fetch tweets from last N hours (default: 24)
        """
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.max_results = max_results_per_query
        self.max_age_hours = max_age_hours
        self.cutoff_date = datetime.utcnow() - timedelta(hours=max_age_hours)

        # Initialize Twitter API client
        self.client = None
        if self.bearer_token and self.bearer_token != 'your_twitter_bearer_token':
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                logger.info("Twitter API v2 client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API client: {str(e)}")
        else:
            logger.warning("Twitter Bearer Token not configured - Twitter monitoring disabled")

    def fetch_all_tweets(self) -> List[Dict]:
        """
        Fetch labor-related tweets from all configured sources.

        Returns:
            List of event dictionaries ready for database insertion
        """
        if not self.client:
            logger.warning("Twitter client not initialized - skipping Twitter monitoring")
            return []

        all_events = []

        # Search hashtags
        for hashtag in self.LABOR_HASHTAGS:
            try:
                events = self._search_tweets(hashtag, event_type='hashtag')
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from {hashtag}")
            except Exception as e:
                logger.error(f"Error searching {hashtag}: {str(e)}")

        # Search queries
        for query in self.SEARCH_QUERIES:
            try:
                events = self._search_tweets(query, event_type='search')
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from query '{query}'")
            except Exception as e:
                logger.error(f"Error searching '{query}': {str(e)}")

        # Monitor labor accounts
        for account in self.LABOR_ACCOUNTS:
            try:
                events = self._fetch_user_tweets(account)
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from @{account}")
            except Exception as e:
                logger.error(f"Error fetching tweets from @{account}: {str(e)}")

        logger.info(f"Total events fetched from Twitter: {len(all_events)}")
        return all_events

    def _search_tweets(self, query: str, event_type: str = 'search') -> List[Dict]:
        """
        Search for tweets matching a query.

        Args:
            query: Search query or hashtag
            event_type: Type of search ('hashtag' or 'search')

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Search recent tweets (last 7 days max for free tier)
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(self.max_results, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities'],
                expansions=['author_id'],
                user_fields=['username', 'verified']
            )

            if not response.data:
                return events

            # Create user lookup dict
            users = {user.id: user for user in (response.includes.get('users', []) if response.includes else [])}

            # Process tweets
            for tweet in response.data:
                # Check if tweet is recent enough
                if tweet.created_at < self.cutoff_date:
                    continue

                # Extract event data
                event = self._extract_tweet_event(tweet, users, query, event_type)
                if event:
                    events.append(event)

        except TweepyException as e:
            logger.error(f"Twitter API error searching '{query}': {str(e)}")
        except Exception as e:
            logger.error(f"Error processing tweets for '{query}': {str(e)}", exc_info=True)

        return events

    def _fetch_user_tweets(self, username: str) -> List[Dict]:
        """
        Fetch recent tweets from a specific user.

        Args:
            username: Twitter username (without @)

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Get user ID
            user = self.client.get_user(username=username)
            if not user.data:
                return events

            user_id = user.data.id

            # Get user's recent tweets
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=min(self.max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'entities'],
                exclude=['retweets', 'replies']  # Only original content
            )

            if not response.data:
                return events

            # Process tweets
            for tweet in response.data:
                # Check if tweet is recent enough
                if tweet.created_at < self.cutoff_date:
                    continue

                # Extract event data
                event = self._extract_tweet_event(
                    tweet,
                    {user_id: user.data},
                    f"@{username}",
                    'account'
                )
                if event:
                    events.append(event)

        except TweepyException as e:
            logger.error(f"Twitter API error fetching @{username}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing tweets from @{username}: {str(e)}", exc_info=True)

        return events

    def _extract_tweet_event(
        self,
        tweet,
        users: Dict,
        source: str,
        event_type: str
    ) -> Optional[Dict]:
        """
        Extract event data from a tweet.

        Args:
            tweet: Tweet object from Twitter API
            users: User lookup dictionary
            source: Source identifier (hashtag, query, or username)
            event_type: Type of source ('hashtag', 'search', 'account')

        Returns:
            Event dictionary or None
        """
        try:
            # Get user info
            user = users.get(tweet.author_id)
            username = user.username if user else 'unknown'

            # Build tweet URL
            tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"

            # Extract tweet text
            text = tweet.text

            # Create title (first 100 chars of tweet)
            title = text[:100] + "..." if len(text) > 100 else text

            # Build event dictionary
            event = {
                'title': title,
                'description': text,
                'source_url': tweet_url,
                'discovered_from': f"Twitter: {source}",
                'event_date': tweet.created_at,
                'suggested_category': 'labor',
                'keywords': self._extract_keywords_from_tweet(text, tweet),
                'status': 'discovered',
            }

            return event

        except Exception as e:
            logger.error(f"Error extracting tweet event: {str(e)}", exc_info=True)
            return None

    def _extract_keywords_from_tweet(self, text: str, tweet) -> str:
        """
        Extract keywords from tweet text and metadata.

        Args:
            text: Tweet text
            tweet: Tweet object

        Returns:
            Comma-separated keywords
        """
        keywords = []

        # Extract hashtags from text
        if hasattr(tweet, 'entities') and tweet.entities:
            if 'hashtags' in tweet.entities:
                keywords.extend([f"#{tag['tag']}" for tag in tweet.entities['hashtags']])

        # Extract common labor keywords from text
        text_lower = text.lower()
        labor_keywords = [
            'union', 'strike', 'labor', 'worker', 'workers', 'organizing',
            'bargaining', 'solidarity', 'protest', 'picket', 'wage', 'wages',
            'contract', 'collective', 'rights', 'workplace', 'employment',
        ]

        found_keywords = [kw for kw in labor_keywords if kw in text_lower]
        keywords.extend(found_keywords)

        # Remove duplicates and limit
        unique_keywords = list(dict.fromkeys(keywords))
        return ', '.join(unique_keywords[:15])


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    monitor = TwitterFeedMonitor(max_results_per_query=10, max_age_hours=24)
    events = monitor.fetch_all_tweets()

    print(f"\nFetched {len(events)} events from Twitter")
    for event in events[:5]:
        print(f"\nTitle: {event['title']}")
        print(f"Source: {event['discovered_from']}")
        print(f"URL: {event['source_url']}")
        print(f"Keywords: {event['keywords']}")
