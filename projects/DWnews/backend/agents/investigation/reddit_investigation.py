"""
Reddit Investigation Monitor for Investigatory Journalist Agent (Phase 6.9.2)

Extended Reddit search capabilities for deep investigation:
- Subreddit extended search (find all relevant discussions)
- Discussion thread analysis (analyze comment quality and insights)
- Eyewitness account identification (find firsthand reports)
- Original content filtering (prioritize OC over news links)
- Timeline construction from posts
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import praw
from praw.exceptions import PRAWException

logger = logging.getLogger(__name__)


class RedditInvestigationMonitor:
    """
    Extended Reddit search and analysis for investigatory journalism.

    Builds on RedditFeedMonitor with deeper investigation capabilities:
    - Extended search across multiple subreddits
    - Discussion thread analysis (comment quality, insights)
    - Eyewitness account identification
    - Original content prioritization
    - Timeline construction from posts
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        max_posts_per_sub: int = 100,
        max_age_days: int = 7,
        use_mock_data: bool = False
    ):
        """
        Initialize Reddit investigation monitor.

        Args:
            client_id: Reddit API client ID (defaults to env var)
            client_secret: Reddit API client secret (defaults to env var)
            user_agent: Reddit API user agent (defaults to env var)
            max_posts_per_sub: Max posts to fetch per subreddit (default: 100)
            max_age_days: Only fetch posts from last N days (default: 7)
            use_mock_data: If True, generate mock data instead of API calls
        """
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT', 'DWnews/1.0')
        self.max_posts = max_posts_per_sub
        self.max_age_days = max_age_days
        self.cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
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
                    logger.info("Reddit API client initialized for investigation")
                except Exception as e:
                    logger.error(f"Failed to initialize Reddit API client: {str(e)}")
                    logger.warning("Falling back to mock data mode")
                    self.use_mock_data = True
            else:
                logger.warning("Reddit credentials not configured - using mock data mode")
                self.use_mock_data = True

    def search_extended(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        time_filter: str = 'week'
    ) -> List[Dict[str, Any]]:
        """
        Perform extended Reddit search across multiple subreddits.

        Args:
            query: Search query string
            subreddits: List of subreddit names to search (None = all)
            max_results: Override default max results
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')

        Returns:
            List of post dictionaries with full metadata
        """
        if self.use_mock_data:
            return self._generate_mock_search_results(query)

        if not self.reddit:
            logger.warning("Reddit client not initialized")
            return []

        results = []
        max_results = max_results or self.max_posts

        # Search across specified subreddits or all Reddit
        if subreddits:
            # Search each subreddit
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    posts = subreddit.search(query, time_filter=time_filter, limit=max_results)

                    for post in posts:
                        post_dict = self._extract_post_data(post, subreddit_name)
                        if post_dict:
                            results.append(post_dict)

                except PRAWException as e:
                    logger.error(f"Reddit API error searching r/{subreddit_name}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing r/{subreddit_name}: {str(e)}", exc_info=True)
        else:
            # Search all Reddit
            try:
                posts = self.reddit.subreddit('all').search(query, time_filter=time_filter, limit=max_results)

                for post in posts:
                    post_dict = self._extract_post_data(post, str(post.subreddit))
                    if post_dict:
                        results.append(post_dict)

            except PRAWException as e:
                logger.error(f"Reddit API error searching all: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing Reddit search: {str(e)}", exc_info=True)

        return results

    def analyze_discussion_thread(self, post_id: str) -> Dict[str, Any]:
        """
        Analyze a discussion thread for quality insights and eyewitness accounts.

        Args:
            post_id: Reddit post ID

        Returns:
            Analysis dictionary with comment insights, sentiment, eyewitness accounts
        """
        if self.use_mock_data:
            return self._generate_mock_thread_analysis(post_id)

        if not self.reddit:
            return {
                'comment_count': 0,
                'top_comments': [],
                'sentiment': 'neutral',
                'eyewitness_accounts': []
            }

        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Don't fetch "load more" comments

            top_comments = []
            eyewitness_accounts = []

            # Analyze top-level comments
            for comment in submission.comments[:20]:  # Top 20 comments
                comment_data = {
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': datetime.utcfromtimestamp(comment.created_utc)
                }

                top_comments.append(comment_data)

                # Check for eyewitness language
                if self._is_eyewitness_comment(comment.body):
                    eyewitness_accounts.append(comment_data)

            # Calculate sentiment (simple heuristic)
            sentiment = self._calculate_sentiment(submission, top_comments)

            return {
                'comment_count': submission.num_comments,
                'top_comments': top_comments,
                'sentiment': sentiment,
                'eyewitness_accounts': eyewitness_accounts
            }

        except Exception as e:
            logger.error(f"Error analyzing thread {post_id}: {str(e)}", exc_info=True)
            return {
                'comment_count': 0,
                'top_comments': [],
                'sentiment': 'neutral',
                'eyewitness_accounts': []
            }

    def identify_eyewitness_accounts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify posts that appear to be firsthand eyewitness accounts.

        Args:
            posts: List of post dictionaries

        Returns:
            Filtered list of posts identified as eyewitness accounts
        """
        eyewitness_posts = []

        for post in posts:
            # Check for eyewitness indicators in title and selftext
            text = post['title'] + ' ' + (post.get('selftext', '') or '')

            is_eyewitness, indicators = self._check_eyewitness_indicators(text)

            if is_eyewitness:
                post['is_eyewitness'] = True
                post['eyewitness_indicators'] = indicators
                eyewitness_posts.append(post)

        return eyewitness_posts

    def filter_original_content(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter to only original content posts (exclude news link reposts).

        Args:
            posts: List of post dictionaries

        Returns:
            Filtered list containing only original content
        """
        original = []

        for post in posts:
            # Prioritize posts with selftext (original content)
            # OR posts marked as original content
            has_selftext = bool(post.get('selftext'))
            is_oc = post.get('is_original_content', False)

            if has_selftext or is_oc:
                original.append(post)

        return original

    def construct_timeline(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct chronological timeline from posts.

        Args:
            posts: List of post dictionaries

        Returns:
            Timeline dictionary with sorted events, earliest/latest posts, duration
        """
        if not posts:
            return {
                'events': [],
                'earliest_post': None,
                'latest_post': None,
                'duration_hours': 0
            }

        # Sort posts by timestamp
        sorted_posts = sorted(posts, key=lambda p: datetime.utcfromtimestamp(p['created_utc']))

        # Build events list
        events = []
        for post in sorted_posts:
            events.append({
                'timestamp': datetime.utcfromtimestamp(post['created_utc']),
                'platform': 'reddit',
                'id': post['id'],
                'title': post['title'],
                'text': post.get('selftext', ''),
                'author': post.get('author', {}).get('name', 'unknown'),
                'subreddit': post['subreddit'],
                'score': post['score']
            })

        # Calculate timeline metadata
        earliest = datetime.utcfromtimestamp(sorted_posts[0]['created_utc'])
        latest = datetime.utcfromtimestamp(sorted_posts[-1]['created_utc'])
        duration = (latest - earliest).total_seconds() / 3600  # hours

        return {
            'events': events,
            'earliest_post': earliest.isoformat(),
            'latest_post': latest.isoformat(),
            'duration_hours': duration,
            'total_events': len(events)
        }

    def _extract_post_data(self, submission, subreddit_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from a Reddit submission.

        Args:
            submission: Reddit submission object
            subreddit_name: Name of the subreddit

        Returns:
            Post dictionary or None
        """
        try:
            # Extract author info
            author_name = str(submission.author) if submission.author else '[deleted]'
            author_created = submission.author.created_utc if submission.author else 0
            author_link_karma = submission.author.link_karma if submission.author else 0
            author_comment_karma = submission.author.comment_karma if submission.author else 0

            # Calculate account age in days
            account_age_days = (datetime.utcnow().timestamp() - author_created) / 86400 if author_created > 0 else 0

            post_dict = {
                'id': submission.id,
                'title': submission.title,
                'selftext': submission.selftext,
                'author': {
                    'name': author_name,
                    'created_utc': author_created,
                    'link_karma': author_link_karma,
                    'comment_karma': author_comment_karma,
                    'is_employee': author_name != '[deleted]',
                    'account_age_days': account_age_days
                },
                'created_utc': submission.created_utc,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'subreddit': subreddit_name,
                'is_original_content': submission.is_original_content if hasattr(submission, 'is_original_content') else False
            }

            # Add URL if it's a link post
            if submission.is_self == False:
                post_dict['url'] = submission.url

            return post_dict

        except Exception as e:
            logger.error(f"Error extracting post data: {str(e)}", exc_info=True)
            return None

    def _is_eyewitness_comment(self, text: str) -> bool:
        """
        Check if comment contains eyewitness language.

        Args:
            text: Comment text

        Returns:
            True if eyewitness indicators found
        """
        eyewitness_phrases = [
            'i was there', 'i saw', 'i witnessed', 'i work', 'i am',
            'firsthand', 'in person', 'at the scene', 'i can confirm',
            'as someone who was there', 'i attended', 'i participated'
        ]

        text_lower = text.lower()
        return any(phrase in text_lower for phrase in eyewitness_phrases)

    def _check_eyewitness_indicators(self, text: str) -> tuple[bool, List[str]]:
        """
        Check text for multiple eyewitness indicators.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (is_eyewitness, list_of_indicators)
        """
        indicators = []
        text_lower = text.lower()

        eyewitness_patterns = {
            'firsthand_language': ['i was there', 'i saw', 'i witnessed', 'firsthand', 'in person'],
            'participation': ['i work', 'i participated', 'i attended', 'we organized'],
            'direct_observation': ['just saw', 'just witnessed', 'right now', 'live updates'],
            'present_tense': ['happening now', 'currently', 'as we speak']
        }

        for category, phrases in eyewitness_patterns.items():
            if any(phrase in text_lower for phrase in phrases):
                indicators.append(category)

        is_eyewitness = len(indicators) >= 1

        return is_eyewitness, indicators

    def _calculate_sentiment(self, submission, comments: List[Dict]) -> str:
        """
        Calculate overall sentiment of discussion (simple heuristic).

        Args:
            submission: Reddit submission
            comments: List of comment dicts

        Returns:
            Sentiment string ('positive', 'neutral', 'negative')
        """
        # Simple heuristic based on scores
        if submission.score > 1000 and submission.upvote_ratio > 0.9:
            return 'positive'
        elif submission.score < 100 or submission.upvote_ratio < 0.6:
            return 'negative'
        else:
            return 'neutral'

    def _generate_mock_search_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Generate mock search results for testing.

        Args:
            query: Search query (used to vary mock data)

        Returns:
            List of mock post dictionaries
        """
        logger.info(f"Generating mock Reddit data for query: '{query}'")

        mock_posts = [
            {
                'id': 'abc123',
                'title': f'{query} - live updates from the scene',
                'selftext': f'I work here and can confirm {query}. Will update as things develop. AMA.',
                'author': {
                    'name': 'warehouse_worker_2024',
                    'created_utc': 1640000000,
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
                'title': f'NYT: {query} confirmed',
                'selftext': '',
                'author': {
                    'name': 'newsbot_labor',
                    'created_utc': 1500000000,
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
                'url': 'https://nytimes.com/article'
            },
            {
                'id': 'ghi789',
                'title': f'I was at {query} today - here is what I saw',
                'selftext': 'As someone who was physically there, I can confirm this happened. The energy was incredible.',
                'author': {
                    'name': 'eyewitness_account',
                    'created_utc': 1704067200,
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

        return mock_posts

    def _generate_mock_thread_analysis(self, post_id: str) -> Dict[str, Any]:
        """
        Generate mock thread analysis for testing.

        Args:
            post_id: Post ID

        Returns:
            Mock analysis dictionary
        """
        return {
            'comment_count': 45,
            'top_comments': [
                {
                    'author': 'commenter1',
                    'body': 'I was there too, can confirm this is accurate.',
                    'score': 234,
                    'created_utc': datetime.utcnow() - timedelta(hours=2)
                },
                {
                    'author': 'commenter2',
                    'body': 'This is huge for labor organizing.',
                    'score': 123,
                    'created_utc': datetime.utcnow() - timedelta(hours=1)
                }
            ],
            'sentiment': 'positive',
            'eyewitness_accounts': [
                {
                    'author': 'commenter1',
                    'body': 'I was there too, can confirm this is accurate.',
                    'score': 234,
                    'created_utc': datetime.utcnow() - timedelta(hours=2)
                }
            ]
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Use mock data for testing
    monitor = RedditInvestigationMonitor(use_mock_data=True)

    # Test extended search
    print("\n=== Extended Search ===")
    results = monitor.search_extended("Amazon strike", subreddits=['labor', 'WorkReform', 'antiwork'])
    print(f"Found {len(results)} posts")

    # Test eyewitness identification
    print("\n=== Eyewitness Identification ===")
    eyewitness = monitor.identify_eyewitness_accounts(results)
    print(f"Found {len(eyewitness)} eyewitness accounts")

    # Test filtering
    print("\n=== Original Content Filtering ===")
    original = monitor.filter_original_content(results)
    print(f"Original content posts: {len(original)}")

    # Test timeline construction
    print("\n=== Timeline Construction ===")
    timeline = monitor.construct_timeline(results)
    print(f"Timeline events: {timeline['total_events']}")
    print(f"Duration: {timeline['duration_hours']:.1f} hours")
