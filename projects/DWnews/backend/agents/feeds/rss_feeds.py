"""
RSS Feed Aggregator for Signal Intake Agent.

Discovers newsworthy events from RSS feeds including:
- Reuters business/labor news
- Associated Press news
- ProPublica investigative reporting
- Labor Notes and other labor-focused sources
"""

import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class RSSFeedAggregator:
    """Aggregates events from multiple RSS feed sources."""

    # Labor-focused RSS feeds (free, no authentication)
    FEED_SOURCES = {
        # Major news sources with labor coverage
        'reuters_business': {
            'url': 'https://www.reuters.com/rssFeed/businessNews',
            'priority': 'high',
            'keywords': ['union', 'labor', 'strike', 'worker', 'wage', 'employment', 'workplace'],
        },
        'ap_news': {
            'url': 'https://apnews.com/rss',
            'priority': 'high',
            'keywords': ['labor', 'union', 'worker', 'strike', 'employment'],
        },

        # Investigative journalism
        'propublica': {
            'url': 'https://www.propublica.org/feeds/propublica/main',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'employment', 'workplace', 'wage theft', 'exploitation'],
        },

        # Labor-specific sources
        'labor_notes': {
            'url': 'https://labornotes.org/rss.xml',
            'priority': 'critical',
            'keywords': [],  # All articles relevant
        },

        # Additional labor sources
        'working_class_perspectives': {
            'url': 'https://workingclassstudies.wordpress.com/feed/',
            'priority': 'medium',
            'keywords': [],  # All articles relevant
        },

        # Economic justice
        'economic_policy_institute': {
            'url': 'https://www.epi.org/blog/feed/',
            'priority': 'medium',
            'keywords': ['wage', 'worker', 'labor', 'union', 'employment', 'inequality'],
        },

        # Alternative sources
        'truthout': {
            'url': 'https://truthout.org/feed/',
            'priority': 'medium',
            'keywords': ['labor', 'union', 'worker', 'strike', 'working class'],
        },

        'common_dreams': {
            'url': 'https://www.commondreams.org/feeds/feed.rss',
            'priority': 'medium',
            'keywords': ['labor', 'union', 'worker', 'strike', 'working class', 'wage'],
        },

        # Democracy Now! - Independent news
        'democracy_now': {
            'url': 'https://www.democracynow.org/democracynow.rss',
            'priority': 'high',
            'keywords': ['labor', 'union', 'worker', 'strike', 'working class', 'protest', 'community'],
        },

        # Al Jazeera - English edition
        'aljazeera_news': {
            'url': 'https://www.aljazeera.com/xml/rss/all.xml',
            'priority': 'high',
            'keywords': ['labor', 'union', 'worker', 'strike', 'protest', 'economy', 'community'],
        },

        # The Guardian - UK news with good labor coverage
        'guardian_world': {
            'url': 'https://www.theguardian.com/world/rss',
            'priority': 'high',
            'keywords': ['labor', 'union', 'worker', 'strike', 'working class', 'employment'],
        },

        # BBC News - Sports (for Premier League coverage)
        'bbc_sport': {
            'url': 'http://feeds.bbci.co.uk/sport/football/rss.xml',
            'priority': 'medium',
            'keywords': [],  # All sports articles relevant
        },

        # The Intercept - Investigative journalism
        'the_intercept': {
            'url': 'https://theintercept.com/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'union', 'community', 'technology', 'surveillance'],
        },

        # ===== NEW SOURCES (Phase 11.2 - Batch 1) =====
        # Added 2026-01-02: RSS Feed Expansion to address Twitter API limitations
        # Target: 13 existing + 8 new = 21 total feeds

        # Worker-Focused Media (CRITICAL priority)
        'the_lever': {
            'url': 'https://www.levernews.com/rss',
            'priority': 'critical',
            'keywords': [],  # All articles relevant (worker-focused investigative journalism)
        },
        'jacobin': {
            'url': 'https://jacobin.com/feed',
            'priority': 'critical',
            'keywords': [],  # All articles relevant (socialist labor perspective)
        },

        # Investigative Journalism (HIGH priority)
        'icij': {
            'url': 'https://www.icij.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'exploitation', 'corruption', 'wage theft', 'employment'],
        },
        'reveal': {
            'url': 'https://revealnews.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'safety', 'violation', 'employment', 'workplace'],
        },
        'the_markup': {
            'url': 'https://themarkup.org/feeds/rss.xml',
            'priority': 'high',
            'keywords': ['worker', 'labor', 'surveillance', 'gig economy', 'tech', 'algorithm'],
        },

        # Regional Labor Publications (HIGH priority)
        'labor_press_nyc': {
            'url': 'https://www.laborpress.org/feed/',
            'priority': 'high',
            'keywords': [],  # All articles relevant (NYC labor news)
        },
        'belt_magazine': {
            'url': 'https://beltmag.com/feed/',
            'priority': 'high',
            'keywords': [],  # All articles relevant (Rust Belt/Midwest labor)
        },

        # Local News Aggregators (HIGH priority)
        'scalawag': {
            'url': 'https://scalawagmagazine.org/feed/',
            'priority': 'high',
            'keywords': ['labor', 'worker', 'economic justice', 'union', 'organizing'],
        },
    }

    def __init__(self, max_age_hours: int = 24):
        """
        Initialize RSS feed aggregator.

        Args:
            max_age_hours: Only fetch articles published in last N hours (default: 24)
        """
        self.max_age_hours = max_age_hours
        self.cutoff_date = datetime.now() - timedelta(hours=max_age_hours)

    def fetch_all_feeds(self) -> List[Dict]:
        """
        Fetch and parse all configured RSS feeds.

        Returns:
            List of event dictionaries ready for database insertion
        """
        all_events = []

        for source_name, source_config in self.FEED_SOURCES.items():
            try:
                events = self._fetch_feed(source_name, source_config)
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from {source_name}")
            except Exception as e:
                logger.error(f"Error fetching {source_name}: {str(e)}", exc_info=True)

        logger.info(f"Total events fetched from RSS feeds: {len(all_events)}")
        return all_events

    def _fetch_feed(self, source_name: str, config: Dict) -> List[Dict]:
        """
        Fetch and parse a single RSS feed.

        Args:
            source_name: Name identifier for the feed
            config: Feed configuration (url, priority, keywords)

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(config['url'])

            if feed.bozo:
                logger.warning(f"Feed {source_name} has parsing issues: {feed.bozo_exception}")

            # Process each entry
            for entry in feed.entries:
                # Check if article is recent enough
                pub_date = self._parse_published_date(entry)
                if pub_date and pub_date < self.cutoff_date:
                    continue

                # Check if article matches keywords (if any specified)
                if config['keywords'] and not self._matches_keywords(entry, config['keywords']):
                    continue

                # Extract event data
                event = self._extract_event_data(entry, source_name, config['priority'])
                if event:
                    events.append(event)

        except Exception as e:
            logger.error(f"Error parsing feed {source_name}: {str(e)}", exc_info=True)

        return events

    def _parse_published_date(self, entry: feedparser.FeedParserDict) -> Optional[datetime]:
        """
        Parse published date from RSS entry.

        Args:
            entry: RSS feed entry

        Returns:
            datetime object or None if parsing fails
        """
        # Try different date fields
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                time_struct = getattr(entry, date_field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except Exception:
                        pass

        return None

    def _matches_keywords(self, entry: feedparser.FeedParserDict, keywords: List[str]) -> bool:
        """
        Check if entry matches any of the specified keywords.

        Args:
            entry: RSS feed entry
            keywords: List of keywords to match

        Returns:
            True if any keyword found in title or description
        """
        # Combine title and description for searching
        text = ""
        if hasattr(entry, 'title'):
            text += entry.title.lower()
        if hasattr(entry, 'description'):
            text += " " + entry.description.lower()
        if hasattr(entry, 'summary'):
            text += " " + entry.summary.lower()

        # Check if any keyword matches
        for keyword in keywords:
            if keyword.lower() in text:
                return True

        return False

    def _extract_event_data(
        self,
        entry: feedparser.FeedParserDict,
        source_name: str,
        priority: str
    ) -> Optional[Dict]:
        """
        Extract event data from RSS entry.

        Args:
            entry: RSS feed entry
            source_name: Name of the source feed
            priority: Priority level of the source

        Returns:
            Event dictionary or None if extraction fails
        """
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None

            # Extract description/summary
            description = (
                entry.get('summary', '') or
                entry.get('description', '') or
                ''
            ).strip()

            # Remove HTML tags from description
            description = self._strip_html(description)

            # Extract URL
            source_url = entry.get('link', '')

            # Extract publish date
            pub_date = self._parse_published_date(entry)

            # Build event dictionary
            event = {
                'title': title,
                'description': description[:1000] if description else None,  # Limit description length
                'source_url': source_url,
                'discovered_from': f"RSS: {source_name}",
                'event_date': pub_date,
                'suggested_category': self._suggest_category(title, description),
                'keywords': self._extract_keywords(title, description),
                'status': 'discovered',
            }

            return event

        except Exception as e:
            logger.error(f"Error extracting event data: {str(e)}", exc_info=True)
            return None

    def _strip_html(self, text: str) -> str:
        """
        Strip HTML tags from text.

        Args:
            text: Text potentially containing HTML

        Returns:
            Plain text
        """
        # Simple HTML tag removal (for basic RSS descriptions)
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)  # Normalize whitespace
        return clean.strip()

    def _suggest_category(self, title: str, description: str) -> Optional[str]:
        """
        Suggest an article category based on content.

        Args:
            title: Article title
            description: Article description

        Returns:
            Suggested category name or None
        """
        text = (title + " " + description).lower()

        # Category keywords
        category_patterns = {
            'labor': ['union', 'strike', 'labor', 'worker', 'wage', 'bargaining', 'organizing'],
            'economy': ['economy', 'inflation', 'recession', 'employment', 'unemployment', 'jobs'],
            'politics': ['congress', 'senate', 'legislation', 'bill', 'policy', 'election'],
            'healthcare': ['health', 'healthcare', 'insurance', 'medical', 'hospital'],
            'environment': ['climate', 'environment', 'pollution', 'renewable', 'fossil'],
            'education': ['school', 'teacher', 'education', 'student', 'university'],
            'housing': ['housing', 'rent', 'eviction', 'homeless', 'affordable housing'],
        }

        # Find best matching category
        for category, keywords in category_patterns.items():
            if any(keyword in text for keyword in keywords):
                return category

        return 'news'  # Default category

    def _extract_keywords(self, title: str, description: str) -> str:
        """
        Extract relevant keywords from title and description.

        Args:
            title: Article title
            description: Article description

        Returns:
            Comma-separated keywords
        """
        text = (title + " " + description).lower()

        # Important keywords to extract
        keyword_list = [
            'union', 'strike', 'labor', 'worker', 'workers', 'wage', 'wages',
            'employment', 'unemployment', 'workplace', 'organizing', 'bargaining',
            'collective bargaining', 'picket', 'protest', 'demonstration',
            'layoff', 'layoffs', 'firing', 'termination',
            'benefit', 'benefits', 'healthcare', 'pension', 'retirement',
            'safety', 'osha', 'injury', 'accident', 'violation',
            'discrimination', 'harassment', 'retaliation',
            'minimum wage', 'living wage', 'pay raise', 'salary',
            'working class', 'blue collar', 'white collar',
        ]

        found_keywords = [kw for kw in keyword_list if kw in text]

        return ', '.join(found_keywords[:10])  # Limit to 10 keywords


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    aggregator = RSSFeedAggregator(max_age_hours=24)
    events = aggregator.fetch_all_feeds()

    print(f"\nFetched {len(events)} events from RSS feeds")
    for event in events[:5]:
        print(f"\nTitle: {event['title']}")
        print(f"Source: {event['discovered_from']}")
        print(f"Category: {event['suggested_category']}")
        print(f"Keywords: {event['keywords']}")
