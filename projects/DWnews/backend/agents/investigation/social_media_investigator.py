"""
Social Media Investigation Module for Investigatory Journalist Agent - Phase 6.9.2

Provides deep social media investigation capabilities beyond basic event discovery:
- Twitter API v2 extended search (hashtag tracking, original tweets, verified accounts)
- Reddit API extended search (subreddit searches, discussion threads, eyewitness accounts)
- Social source credibility scoring (account age, karma, verification status)
- Timeline construction from social mentions (chronological event tracking)
- Eyewitness account identification (firsthand vs. secondhand reports)

This module enhances the Phase 1 investigation engine with social media-specific intelligence.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import tweepy
from tweepy.errors import TweepyException
import praw
from praw.exceptions import PRAWException

logger = logging.getLogger(__name__)


@dataclass
class SocialSource:
    """Social media source with credibility scoring."""

    platform: str  # 'twitter' or 'reddit'
    url: str
    author: str
    author_handle: str  # @username or u/username
    content: str
    published_date: datetime

    # Credibility metrics
    account_age_days: int
    is_verified: bool = False
    follower_count: Optional[int] = None
    karma_score: Optional[int] = None  # Reddit only
    engagement_metrics: Optional[Dict] = None  # likes, retweets, comments

    # Source analysis
    credibility_score: float = 0.0  # 0-100
    is_eyewitness: bool = False
    is_original_content: bool = False
    reliability_tier: str = 'unknown'  # tier1/tier2/tier3/tier4

    # Context
    hashtags: List[str] = None
    mentions: List[str] = None
    related_threads: List[str] = None

    def __post_init__(self):
        """Calculate credibility score after initialization."""
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.related_threads is None:
            self.related_threads = []
        if self.engagement_metrics is None:
            self.engagement_metrics = {}


@dataclass
class SocialTimeline:
    """Timeline of social media mentions for an event."""

    event_description: str
    earliest_mention: Optional[SocialSource]
    earliest_date: Optional[datetime]
    latest_mention: Optional[SocialSource]
    latest_date: Optional[datetime]

    total_mentions: int
    platforms: List[str]  # ['twitter', 'reddit']

    # Chronological entries
    timeline_entries: List[SocialSource]

    # Analysis
    eyewitness_accounts: List[SocialSource]
    verification_sources: List[SocialSource]  # verified accounts or high credibility
    discussion_threads: List[str]  # URLs to discussions

    # Patterns
    mention_velocity: float = 0.0  # mentions per hour
    peak_activity_time: Optional[datetime] = None
    geographic_locations: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.geographic_locations is None:
            self.geographic_locations = []


class SocialMediaInvestigator:
    """
    Deep social media investigation for topics needing additional verification.

    Enhances Phase 1 investigation with social media-specific capabilities:
    - Extended Twitter search beyond hashtags/accounts
    - Deep Reddit thread analysis
    - Source credibility assessment
    - Timeline construction
    - Eyewitness identification
    """

    def __init__(
        self,
        twitter_bearer_token: Optional[str] = None,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
        reddit_user_agent: Optional[str] = None,
        use_mock_data: bool = False
    ):
        """
        Initialize social media investigator.

        Args:
            twitter_bearer_token: Twitter API v2 Bearer Token
            reddit_client_id: Reddit API client ID
            reddit_client_secret: Reddit API client secret
            reddit_user_agent: Reddit API user agent
            use_mock_data: If True, use mock data for testing
        """
        self.use_mock_data = use_mock_data

        # Initialize Twitter API
        self.twitter_bearer_token = twitter_bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.twitter_client = None

        if not self.use_mock_data and self.twitter_bearer_token and self.twitter_bearer_token != 'your_twitter_bearer_token':
            try:
                self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
                logger.info("Twitter API v2 client initialized for investigation")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API: {str(e)}")
                logger.warning("Falling back to mock Twitter data")
                self.use_mock_data = True
        else:
            logger.warning("Twitter API not configured - using mock data")
            self.use_mock_data = True

        # Initialize Reddit API
        self.reddit_client_id = reddit_client_id or os.getenv('REDDIT_CLIENT_ID')
        self.reddit_client_secret = reddit_client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.reddit_user_agent = reddit_user_agent or os.getenv('REDDIT_USER_AGENT', 'DWnews_Investigator/1.0')
        self.reddit = None

        if not self.use_mock_data and self.reddit_client_id and self.reddit_client_id != 'your_reddit_client_id':
            try:
                self.reddit = praw.Reddit(
                    client_id=self.reddit_client_id,
                    client_secret=self.reddit_client_secret,
                    user_agent=self.reddit_user_agent
                )
                logger.info("Reddit API client initialized for investigation")
            except Exception as e:
                logger.error(f"Failed to initialize Reddit API: {str(e)}")
                logger.warning("Falling back to mock Reddit data")
                self.use_mock_data = True
        else:
            logger.warning("Reddit API not configured - using mock data")
            self.use_mock_data = True

    def investigate_topic(
        self,
        topic_title: str,
        topic_description: str,
        keywords: List[str],
        max_results: int = 50,
        days_back: int = 30
    ) -> Tuple[List[SocialSource], SocialTimeline]:
        """
        Conduct social media investigation for a topic.

        Args:
            topic_title: Title of the topic to investigate
            topic_description: Description of the topic
            keywords: List of keywords to search for
            max_results: Maximum results to fetch per platform
            days_back: How many days back to search

        Returns:
            Tuple of (list of social sources, timeline analysis)
        """
        logger.info(f"Starting social media investigation: {topic_title}")
        logger.info(f"Keywords: {keywords}")
        logger.info(f"Search window: {days_back} days, max {max_results} results per platform")

        all_sources = []

        # Search Twitter
        twitter_sources = self._search_twitter(keywords, max_results, days_back)
        all_sources.extend(twitter_sources)
        logger.info(f"Found {len(twitter_sources)} Twitter sources")

        # Search Reddit
        reddit_sources = self._search_reddit(keywords, max_results, days_back)
        all_sources.extend(reddit_sources)
        logger.info(f"Found {len(reddit_sources)} Reddit sources")

        # Score credibility for all sources
        for source in all_sources:
            source.credibility_score = self._calculate_credibility_score(source)
            source.reliability_tier = self._assign_reliability_tier(source.credibility_score)
            source.is_eyewitness = self._detect_eyewitness_account(source)

        # Construct timeline
        timeline = self._construct_timeline(all_sources, topic_description)

        logger.info(f"Investigation complete: {len(all_sources)} total sources, {len(timeline.eyewitness_accounts)} eyewitness accounts")

        return all_sources, timeline

    def _search_twitter(
        self,
        keywords: List[str],
        max_results: int,
        days_back: int
    ) -> List[SocialSource]:
        """Search Twitter for topic mentions."""

        if self.use_mock_data:
            return self._generate_mock_twitter_sources(keywords, max_results)

        if not self.twitter_client:
            logger.warning("Twitter client not available")
            return []

        sources = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        # Build search query
        query = ' OR '.join(keywords)
        query += ' -is:retweet'  # Exclude retweets, only original content

        try:
            # Search recent tweets
            response = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'verified', 'created_at', 'public_metrics']
            )

            if not response.data:
                return sources

            # Create user lookup
            users = {user.id: user for user in (response.includes.get('users', []) if response.includes else [])}

            # Process tweets
            for tweet in response.data:
                if tweet.created_at < cutoff_date:
                    continue

                user = users.get(tweet.author_id)
                if not user:
                    continue

                # Calculate account age
                account_created = user.created_at
                account_age_days = (datetime.utcnow() - account_created.replace(tzinfo=None)).days

                # Extract engagement metrics
                metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') else {}
                engagement = {
                    'likes': metrics.get('like_count', 0),
                    'retweets': metrics.get('retweet_count', 0),
                    'replies': metrics.get('reply_count', 0),
                    'quotes': metrics.get('quote_count', 0)
                }

                # Extract hashtags and mentions
                hashtags = []
                mentions = []
                if hasattr(tweet, 'entities') and tweet.entities:
                    if 'hashtags' in tweet.entities:
                        hashtags = [f"#{tag['tag']}" for tag in tweet.entities['hashtags']]
                    if 'mentions' in tweet.entities:
                        mentions = [f"@{mention['username']}" for mention in tweet.entities['mentions']]

                # Create source
                source = SocialSource(
                    platform='twitter',
                    url=f"https://twitter.com/{user.username}/status/{tweet.id}",
                    author=user.name,
                    author_handle=f"@{user.username}",
                    content=tweet.text,
                    published_date=tweet.created_at.replace(tzinfo=None),
                    account_age_days=account_age_days,
                    is_verified=user.verified if hasattr(user, 'verified') else False,
                    follower_count=user.public_metrics.get('followers_count', 0) if hasattr(user, 'public_metrics') else 0,
                    engagement_metrics=engagement,
                    is_original_content=True,  # We filtered out retweets
                    hashtags=hashtags,
                    mentions=mentions
                )

                sources.append(source)

        except TweepyException as e:
            logger.error(f"Twitter API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}", exc_info=True)

        return sources

    def _search_reddit(
        self,
        keywords: List[str],
        max_results: int,
        days_back: int
    ) -> List[SocialSource]:
        """Search Reddit for topic mentions."""

        if self.use_mock_data:
            return self._generate_mock_reddit_sources(keywords, max_results)

        if not self.reddit:
            logger.warning("Reddit client not available")
            return []

        sources = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        # Search labor-related subreddits
        subreddits = ['labor', 'WorkReform', 'antiwork', 'unions', 'LaborMovement']

        for keyword in keywords[:3]:  # Limit keywords to avoid rate limiting
            try:
                # Search across multiple subreddits
                for subreddit_name in subreddits:
                    subreddit = self.reddit.subreddit(subreddit_name)

                    # Search posts
                    for submission in subreddit.search(keyword, limit=max_results // len(keywords) // len(subreddits), time_filter='month'):
                        post_date = datetime.utcfromtimestamp(submission.created_utc)
                        if post_date < cutoff_date:
                            continue

                        # Get author info
                        try:
                            author = submission.author
                            if not author:  # Deleted account
                                continue

                            # Calculate account age
                            account_created = datetime.utcfromtimestamp(author.created_utc)
                            account_age_days = (datetime.utcnow() - account_created).days

                            # Get karma
                            link_karma = author.link_karma if hasattr(author, 'link_karma') else 0
                            comment_karma = author.comment_karma if hasattr(author, 'comment_karma') else 0
                            total_karma = link_karma + comment_karma

                            # Engagement metrics
                            engagement = {
                                'upvotes': submission.score,
                                'upvote_ratio': submission.upvote_ratio,
                                'num_comments': submission.num_comments
                            }

                            # Create source
                            source = SocialSource(
                                platform='reddit',
                                url=f"https://reddit.com{submission.permalink}",
                                author=author.name,
                                author_handle=f"u/{author.name}",
                                content=f"{submission.title}\n\n{submission.selftext[:500] if submission.selftext else ''}",
                                published_date=post_date,
                                account_age_days=account_age_days,
                                karma_score=total_karma,
                                engagement_metrics=engagement,
                                is_original_content=True,
                                hashtags=[],  # Reddit doesn't use hashtags
                                mentions=[],
                                related_threads=[f"https://reddit.com{submission.permalink}"]
                            )

                            sources.append(source)

                        except Exception as e:
                            logger.error(f"Error processing Reddit submission: {str(e)}")
                            continue

            except PRAWException as e:
                logger.error(f"Reddit API error searching '{keyword}': {str(e)}")
            except Exception as e:
                logger.error(f"Error searching Reddit for '{keyword}': {str(e)}", exc_info=True)

        return sources

    def _calculate_credibility_score(self, source: SocialSource) -> float:
        """
        Calculate credibility score (0-100) for a social source.

        Scoring factors:
        - Account age (older = more credible)
        - Verification status (verified = bonus)
        - Follower/karma count (higher = more credible)
        - Engagement metrics (higher = more visible/validated)
        - Original content vs. shares
        """
        score = 0.0

        # Account age (0-30 points)
        if source.account_age_days > 365:
            score += 30
        elif source.account_age_days > 180:
            score += 20
        elif source.account_age_days > 30:
            score += 10
        else:
            score += 5

        # Verification (20 points bonus)
        if source.is_verified:
            score += 20

        # Follower/Karma count (0-25 points)
        if source.platform == 'twitter' and source.follower_count:
            if source.follower_count > 100000:
                score += 25
            elif source.follower_count > 10000:
                score += 20
            elif source.follower_count > 1000:
                score += 15
            elif source.follower_count > 100:
                score += 10
            else:
                score += 5
        elif source.platform == 'reddit' and source.karma_score:
            if source.karma_score > 50000:
                score += 25
            elif source.karma_score > 10000:
                score += 20
            elif source.karma_score > 1000:
                score += 15
            elif source.karma_score > 100:
                score += 10
            else:
                score += 5

        # Engagement metrics (0-15 points)
        if source.engagement_metrics:
            if source.platform == 'twitter':
                total_engagement = (
                    source.engagement_metrics.get('likes', 0) +
                    source.engagement_metrics.get('retweets', 0) * 2 +  # Retweets weighted higher
                    source.engagement_metrics.get('replies', 0)
                )
                if total_engagement > 1000:
                    score += 15
                elif total_engagement > 100:
                    score += 10
                elif total_engagement > 10:
                    score += 5
            elif source.platform == 'reddit':
                upvotes = source.engagement_metrics.get('upvotes', 0)
                comments = source.engagement_metrics.get('num_comments', 0)
                total_engagement = upvotes + (comments * 2)
                if total_engagement > 500:
                    score += 15
                elif total_engagement > 50:
                    score += 10
                elif total_engagement > 5:
                    score += 5

        # Original content bonus (10 points)
        if source.is_original_content:
            score += 10

        return min(score, 100)  # Cap at 100

    def _assign_reliability_tier(self, credibility_score: float) -> str:
        """Assign reliability tier based on credibility score."""
        if credibility_score >= 80:
            return 'tier1'  # Highly reliable
        elif credibility_score >= 60:
            return 'tier2'  # Moderately reliable
        elif credibility_score >= 40:
            return 'tier3'  # Less reliable
        else:
            return 'tier4'  # Least reliable

    def _detect_eyewitness_account(self, source: SocialSource) -> bool:
        """
        Detect if source appears to be firsthand/eyewitness account.

        Looks for indicators like:
        - First-person language ("I saw", "I was there")
        - Present tense descriptions
        - Specific details (time, location, names)
        - Original photos/videos (URLs)
        """
        content_lower = source.content.lower()

        # First-person indicators
        firsthand_phrases = [
            'i saw', 'i witnessed', 'i was there', 'i heard',
            'we saw', 'we witnessed', 'we were there',
            'just saw', 'just witnessed', 'happening now',
            'currently at', 'live from', 'on the scene'
        ]

        for phrase in firsthand_phrases:
            if phrase in content_lower:
                return True

        return False

    def _construct_timeline(
        self,
        sources: List[SocialSource],
        event_description: str
    ) -> SocialTimeline:
        """Construct chronological timeline from social sources."""

        if not sources:
            return SocialTimeline(
                event_description=event_description,
                earliest_mention=None,
                earliest_date=None,
                latest_mention=None,
                latest_date=None,
                total_mentions=0,
                platforms=[],
                timeline_entries=[],
                eyewitness_accounts=[],
                verification_sources=[],
                discussion_threads=[]
            )

        # Sort by date
        sorted_sources = sorted(sources, key=lambda s: s.published_date)

        earliest = sorted_sources[0]
        latest = sorted_sources[-1]

        # Identify eyewitness accounts
        eyewitness_accounts = [s for s in sources if s.is_eyewitness]

        # Identify high-credibility sources (verified or tier1/tier2)
        verification_sources = [
            s for s in sources
            if s.is_verified or s.reliability_tier in ['tier1', 'tier2']
        ]

        # Collect discussion threads
        discussion_threads = []
        for source in sources:
            if source.related_threads:
                discussion_threads.extend(source.related_threads)
        discussion_threads = list(set(discussion_threads))  # Remove duplicates

        # Calculate mention velocity (mentions per hour)
        if len(sources) > 1:
            time_span_hours = (latest.published_date - earliest.published_date).total_seconds() / 3600
            if time_span_hours > 0:
                mention_velocity = len(sources) / time_span_hours
            else:
                mention_velocity = 0.0
        else:
            mention_velocity = 0.0

        # Find peak activity (hour with most mentions)
        hourly_counts = {}
        for source in sources:
            hour_key = source.published_date.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1

        peak_activity_time = max(hourly_counts, key=hourly_counts.get) if hourly_counts else None

        # Get unique platforms
        platforms = list(set(s.platform for s in sources))

        timeline = SocialTimeline(
            event_description=event_description,
            earliest_mention=earliest,
            earliest_date=earliest.published_date,
            latest_mention=latest,
            latest_date=latest.published_date,
            total_mentions=len(sources),
            platforms=platforms,
            timeline_entries=sorted_sources,
            eyewitness_accounts=eyewitness_accounts,
            verification_sources=verification_sources,
            discussion_threads=discussion_threads,
            mention_velocity=mention_velocity,
            peak_activity_time=peak_activity_time,
            geographic_locations=[]  # TODO: Extract from content
        )

        return timeline

    def _generate_mock_twitter_sources(self, keywords: List[str], max_results: int) -> List[SocialSource]:
        """Generate mock Twitter sources for testing."""
        logger.info("Generating mock Twitter sources")

        mock_sources = [
            SocialSource(
                platform='twitter',
                url='https://twitter.com/unionworker123/status/123456789',
                author='John Worker',
                author_handle='@unionworker123',
                content=f'I witnessed the strike action today at the plant. Over 500 workers on the picket line. #{keywords[0] if keywords else "union"} #solidarity',
                published_date=datetime.utcnow() - timedelta(hours=2),
                account_age_days=730,
                is_verified=False,
                follower_count=250,
                engagement_metrics={'likes': 45, 'retweets': 12, 'replies': 8, 'quotes': 3},
                is_original_content=True,
                hashtags=['#union', '#solidarity'],
                mentions=[]
            ),
            SocialSource(
                platform='twitter',
                url='https://twitter.com/laborunion/status/987654321',
                author='Labor Union Official',
                author_handle='@laborunion',
                content=f'BREAKING: Workers vote 75-25 to authorize strike. Negotiations continue tomorrow. {keywords[0] if keywords else ""}',
                published_date=datetime.utcnow() - timedelta(hours=5),
                account_age_days=2190,
                is_verified=True,
                follower_count=15000,
                engagement_metrics={'likes': 320, 'retweets': 89, 'replies': 45, 'quotes': 12},
                is_original_content=True,
                hashtags=[],
                mentions=['@mediaco']
            ),
        ]

        return mock_sources[:max_results]

    def _generate_mock_reddit_sources(self, keywords: List[str], max_results: int) -> List[SocialSource]:
        """Generate mock Reddit sources for testing."""
        logger.info("Generating mock Reddit sources")

        mock_sources = [
            SocialSource(
                platform='reddit',
                url='https://reddit.com/r/labor/comments/abc123/strike_update',
                author='worker_advocate',
                author_handle='u/worker_advocate',
                content=f'Strike Update: Day 3 and morale is high. Company still refusing to negotiate wage increases. {keywords[0] if keywords else ""}',
                published_date=datetime.utcnow() - timedelta(hours=8),
                account_age_days=1095,
                karma_score=5420,
                engagement_metrics={'upvotes': 234, 'upvote_ratio': 0.95, 'num_comments': 67},
                is_original_content=True,
                related_threads=['https://reddit.com/r/labor/comments/abc123/strike_update']
            ),
            SocialSource(
                platform='reddit',
                url='https://reddit.com/r/unions/comments/def456/organizing',
                author='union_member_99',
                author_handle='u/union_member_99',
                content='We successfully organized our workplace! 80% signed cards in just 2 weeks. Filing with NLRB tomorrow.',
                published_date=datetime.utcnow() - timedelta(hours=12),
                account_age_days=365,
                karma_score=1230,
                engagement_metrics={'upvotes': 89, 'upvote_ratio': 0.92, 'num_comments': 23},
                is_original_content=True,
                related_threads=['https://reddit.com/r/unions/comments/def456/organizing']
            ),
        ]

        return mock_sources[:max_results]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    investigator = SocialMediaInvestigator(use_mock_data=True)

    sources, timeline = investigator.investigate_topic(
        topic_title="Amazon Warehouse Strike",
        topic_description="Workers at Amazon JFK8 warehouse vote to strike over wages and conditions",
        keywords=["amazon", "strike", "warehouse", "workers"],
        max_results=20,
        days_back=7
    )

    print(f"\n=== Investigation Results ===")
    print(f"Total sources: {len(sources)}")
    print(f"Eyewitness accounts: {len(timeline.eyewitness_accounts)}")
    print(f"Verification sources: {len(timeline.verification_sources)}")
    print(f"Mention velocity: {timeline.mention_velocity:.2f} per hour")

    print(f"\n=== Timeline ===")
    print(f"Earliest mention: {timeline.earliest_date}")
    print(f"Latest mention: {timeline.latest_date}")
    print(f"Peak activity: {timeline.peak_activity_time}")

    print(f"\n=== Top Sources ===")
    for source in sorted(sources, key=lambda s: s.credibility_score, reverse=True)[:3]:
        print(f"\n{source.platform.upper()} - {source.author_handle}")
        print(f"  Credibility: {source.credibility_score:.1f}/100 ({source.reliability_tier})")
        print(f"  Eyewitness: {source.is_eyewitness}")
        print(f"  Content: {source.content[:100]}...")
