"""
Reddit Feed Monitor for Signal Intake Agent.

Discovers newsworthy labor events from Reddit:
- r/labor - Labor movement discussions
- r/WorkReform - Workplace reform advocacy
- r/antiwork - Work culture critique
- r/unions - Union organizing and news
- Local city subreddits for regional labor news
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import praw
from praw.exceptions import PRAWException

logger = logging.getLogger(__name__)


class RedditFeedMonitor:
    """Monitors Reddit for labor-related news and events."""

    # Labor-focused subreddits
    LABOR_SUBREDDITS = [
        'labor',
        'WorkReform',
        'antiwork',
        'unions',
        'union',
        'IWW',  # Industrial Workers of the World
        'LateStageCapitalism',
        'WorkersStrikeBack',
        'LaborMovement',
    ]

    # Local/regional subreddits (add more based on target cities)
    REGIONAL_SUBREDDITS = [
        'chicago',
        'nyc',
        'LosAngeles',
        'SanFrancisco',
        'Seattle',
        'Detroit',
        'Boston',
        'Atlanta',
        'Philadelphia',
        'Minneapolis',
    ]

    # Keywords to filter regional posts
    LABOR_KEYWORDS = [
        'union', 'strike', 'labor', 'worker', 'workers', 'organizing',
        'protest', 'wage', 'wages', 'employment', 'fired', 'layoff',
        'workplace', 'boss', 'manager', 'contract', 'bargaining',
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        max_posts_per_sub: int = 25,
        max_age_hours: int = 24,
        use_mock_data: bool = False
    ):
        """
        Initialize Reddit feed monitor.

        Args:
            client_id: Reddit API client ID (defaults to env var)
            client_secret: Reddit API client secret (defaults to env var)
            user_agent: Reddit API user agent (defaults to env var)
            max_posts_per_sub: Max posts to fetch per subreddit (default: 25)
            max_age_hours: Only fetch posts from last N hours (default: 24)
            use_mock_data: If True, generate mock data instead of API calls
        """
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'DWnews/1.0')
        self.max_posts = max_posts_per_sub
        self.max_age_hours = max_age_hours
        self.cutoff_date = datetime.utcnow() - timedelta(hours=max_age_hours)
        self.use_mock_data = use_mock_data

        # Initialize Reddit API client
        self.reddit = None
        if not self.use_mock_data:
            if (self.client_id and self.client_id != 'your_reddit_client_id' and
                self.client_secret and self.client_secret != 'your_reddit_client_secret'):
                try:
                    self.reddit = praw.Reddit(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        user_agent=self.user_agent
                    )
                    # Test authentication
                    _ = self.reddit.user.me()
                    logger.info("Reddit API client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Reddit API client: {str(e)}")
                    logger.warning("Falling back to mock data mode")
                    self.use_mock_data = True
            else:
                logger.warning("Reddit credentials not configured - using mock data mode")
                self.use_mock_data = True

    def fetch_all_posts(self) -> List[Dict]:
        """
        Fetch labor-related posts from all configured subreddits.

        Returns:
            List of event dictionaries ready for database insertion
        """
        if self.use_mock_data:
            logger.info("Using mock Reddit data (credentials not available)")
            return self._generate_mock_data()

        if not self.reddit:
            logger.warning("Reddit client not initialized - skipping Reddit monitoring")
            return []

        all_events = []

        # Monitor labor subreddits (all posts are relevant)
        for subreddit_name in self.LABOR_SUBREDDITS:
            try:
                events = self._fetch_subreddit_posts(
                    subreddit_name,
                    filter_keywords=False
                )
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from r/{subreddit_name}")
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit_name}: {str(e)}")

        # Monitor regional subreddits (filter by keywords)
        for subreddit_name in self.REGIONAL_SUBREDDITS:
            try:
                events = self._fetch_subreddit_posts(
                    subreddit_name,
                    filter_keywords=True
                )
                all_events.extend(events)
                if events:
                    logger.info(f"Fetched {len(events)} labor-related events from r/{subreddit_name}")
            except Exception as e:
                logger.error(f"Error fetching r/{subreddit_name}: {str(e)}")

        logger.info(f"Total events fetched from Reddit: {len(all_events)}")
        return all_events

    def _fetch_subreddit_posts(
        self,
        subreddit_name: str,
        filter_keywords: bool = False
    ) -> List[Dict]:
        """
        Fetch posts from a specific subreddit.

        Args:
            subreddit_name: Name of the subreddit
            filter_keywords: If True, only include posts matching labor keywords

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            # Fetch hot posts (most active discussions)
            for submission in subreddit.hot(limit=self.max_posts):
                # Check post age
                post_date = datetime.utcfromtimestamp(submission.created_utc)
                if post_date < self.cutoff_date:
                    continue

                # Filter by keywords if required
                if filter_keywords and not self._matches_keywords(submission):
                    continue

                # Extract event data
                event = self._extract_post_event(submission, subreddit_name)
                if event:
                    events.append(event)

        except PRAWException as e:
            logger.error(f"Reddit API error fetching r/{subreddit_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing posts from r/{subreddit_name}: {str(e)}", exc_info=True)

        return events

    def _matches_keywords(self, submission) -> bool:
        """
        Check if submission matches labor keywords.

        Args:
            submission: Reddit submission object

        Returns:
            True if any keyword found in title or selftext
        """
        text = (submission.title + " " + (submission.selftext or "")).lower()

        for keyword in self.LABOR_KEYWORDS:
            if keyword in text:
                return True

        return False

    def _extract_post_event(self, submission, subreddit_name: str) -> Optional[Dict]:
        """
        Extract event data from a Reddit submission.

        Args:
            submission: Reddit submission object
            subreddit_name: Name of the subreddit

        Returns:
            Event dictionary or None
        """
        try:
            # Build event dictionary
            event = {
                'title': submission.title,
                'description': submission.selftext[:1000] if submission.selftext else None,
                'source_url': f"https://reddit.com{submission.permalink}",
                'discovered_from': f"Reddit: r/{subreddit_name}",
                'event_date': datetime.utcfromtimestamp(submission.created_utc),
                'suggested_category': self._suggest_category(subreddit_name),
                'keywords': self._extract_keywords(submission),
                'status': 'discovered',
            }

            return event

        except Exception as e:
            logger.error(f"Error extracting post event: {str(e)}", exc_info=True)
            return None

    def _suggest_category(self, subreddit_name: str) -> str:
        """
        Suggest category based on subreddit.

        Args:
            subreddit_name: Name of the subreddit

        Returns:
            Suggested category
        """
        # Labor subreddits → labor category
        if subreddit_name.lower() in [s.lower() for s in self.LABOR_SUBREDDITS]:
            return 'labor'

        # Regional subreddits → local category
        if subreddit_name in self.REGIONAL_SUBREDDITS:
            return 'local'

        return 'news'

    def _extract_keywords(self, submission) -> str:
        """
        Extract keywords from submission.

        Args:
            submission: Reddit submission object

        Returns:
            Comma-separated keywords
        """
        text = (submission.title + " " + (submission.selftext or "")).lower()

        found_keywords = [kw for kw in self.LABOR_KEYWORDS if kw in text]

        # Add flair if available
        if submission.link_flair_text:
            found_keywords.append(submission.link_flair_text.lower())

        # Remove duplicates and limit
        unique_keywords = list(dict.fromkeys(found_keywords))
        return ', '.join(unique_keywords[:10])

    def _generate_mock_data(self) -> List[Dict]:
        """
        Generate mock Reddit data for testing when credentials not available.

        Returns:
            List of mock event dictionaries
        """
        logger.info("Generating mock Reddit data")

        mock_events = [
            {
                'title': 'Amazon workers in NYC vote to unionize with ALU',
                'description': 'Historic victory as Amazon JFK8 warehouse workers vote 2654-2131 to join Amazon Labor Union',
                'source_url': 'https://reddit.com/r/labor/mock_post_1',
                'discovered_from': 'Reddit: r/labor (MOCK)',
                'event_date': datetime.utcnow() - timedelta(hours=2),
                'suggested_category': 'labor',
                'keywords': 'union, amazon, workers, organizing, victory',
                'status': 'discovered',
            },
            {
                'title': 'Starbucks baristas in Buffalo file for union election',
                'description': 'Workers at three Buffalo-area Starbucks stores file for union elections with NLRB',
                'source_url': 'https://reddit.com/r/WorkReform/mock_post_2',
                'discovered_from': 'Reddit: r/WorkReform (MOCK)',
                'event_date': datetime.utcnow() - timedelta(hours=5),
                'suggested_category': 'labor',
                'keywords': 'starbucks, union, workers, organizing, nlrb',
                'status': 'discovered',
            },
            {
                'title': 'Chicago teachers authorize strike over class sizes',
                'description': 'Chicago Teachers Union members vote 95% in favor of authorizing strike action',
                'source_url': 'https://reddit.com/r/chicago/mock_post_3',
                'discovered_from': 'Reddit: r/chicago (MOCK)',
                'event_date': datetime.utcnow() - timedelta(hours=8),
                'suggested_category': 'local',
                'keywords': 'teachers, strike, union, chicago, education',
                'status': 'discovered',
            },
        ]

        return mock_events


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Will use mock data if credentials not configured
    monitor = RedditFeedMonitor(max_posts_per_sub=10, max_age_hours=24)
    events = monitor.fetch_all_posts()

    print(f"\nFetched {len(events)} events from Reddit")
    for event in events[:5]:
        print(f"\nTitle: {event['title']}")
        print(f"Source: {event['discovered_from']}")
        print(f"Category: {event['suggested_category']}")
        print(f"Keywords: {event['keywords']}")
