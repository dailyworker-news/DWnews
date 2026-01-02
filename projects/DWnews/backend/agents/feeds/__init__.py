"""
Feed source modules for Signal Intake Agent.

Each module handles a specific data source (RSS, Twitter, Reddit, government).
"""

from .rss_feeds import RSSFeedAggregator
from .twitter_feed import TwitterFeedMonitor
from .reddit_feed import RedditFeedMonitor
from .government_feeds import GovernmentFeedScraper

__all__ = [
    'RSSFeedAggregator',
    'TwitterFeedMonitor',
    'RedditFeedMonitor',
    'GovernmentFeedScraper',
]
