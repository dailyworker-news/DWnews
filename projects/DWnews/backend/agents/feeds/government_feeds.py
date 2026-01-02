"""
Government Feed Scraper for Signal Intake Agent.

Discovers newsworthy labor events from government sources:
- Department of Labor newsroom and press releases
- NLRB (National Labor Relations Board) case decisions
- OSHA enforcement actions
- data.gov labor-related datasets
- Bureau of Labor Statistics releases
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import feedparser
import re

logger = logging.getLogger(__name__)


class GovernmentFeedScraper:
    """Scrapes government sources for labor-related news and data."""

    # Government RSS feeds (no authentication required)
    GOVERNMENT_FEEDS = {
        'dol_newsroom': {
            'url': 'https://www.dol.gov/rss/releases.xml',
            'name': 'Department of Labor Newsroom',
            'priority': 'high',
        },
        'osha_news': {
            'url': 'https://www.osha.gov/rss/news_releases.xml',
            'name': 'OSHA News Releases',
            'priority': 'high',
        },
        'bls_news': {
            'url': 'https://www.bls.gov/feed/bls_latest.rss',
            'name': 'Bureau of Labor Statistics',
            'priority': 'medium',
        },
    }

    # Scraped sources (no RSS, need to parse HTML)
    SCRAPED_SOURCES = {
        'nlrb_decisions': {
            'url': 'https://www.nlrb.gov/news-publications/decisions',
            'name': 'NLRB Decisions',
            'priority': 'high',
            'enabled': False,  # Disabled by default (complex scraping)
        },
        'nlrb_press': {
            'url': 'https://www.nlrb.gov/news-outreach/news-story',
            'name': 'NLRB Press Releases',
            'priority': 'high',
            'enabled': False,  # Disabled by default (complex scraping)
        },
    }

    def __init__(
        self,
        max_age_hours: int = 24,
        enable_scraping: bool = False,
        request_timeout: int = 10
    ):
        """
        Initialize government feed scraper.

        Args:
            max_age_hours: Only fetch items from last N hours (default: 24)
            enable_scraping: Enable HTML scraping (slower, may be fragile) (default: False)
            request_timeout: Request timeout in seconds (default: 10)
        """
        self.max_age_hours = max_age_hours
        self.cutoff_date = datetime.now() - timedelta(hours=max_age_hours)
        self.enable_scraping = enable_scraping
        self.timeout = request_timeout

        # HTTP headers for web scraping
        self.headers = {
            'User-Agent': 'DWnews/1.0 (Labor News Aggregator; contact@thedailyworker.news)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def fetch_all_sources(self) -> List[Dict]:
        """
        Fetch from all configured government sources.

        Returns:
            List of event dictionaries ready for database insertion
        """
        all_events = []

        # Fetch RSS feeds
        for source_id, config in self.GOVERNMENT_FEEDS.items():
            try:
                events = self._fetch_rss_feed(source_id, config)
                all_events.extend(events)
                logger.info(f"Fetched {len(events)} events from {config['name']}")
            except Exception as e:
                logger.error(f"Error fetching {config['name']}: {str(e)}")

        # Scrape HTML sources (if enabled)
        if self.enable_scraping:
            for source_id, config in self.SCRAPED_SOURCES.items():
                if not config.get('enabled', True):
                    continue
                try:
                    events = self._scrape_source(source_id, config)
                    all_events.extend(events)
                    logger.info(f"Scraped {len(events)} events from {config['name']}")
                except Exception as e:
                    logger.error(f"Error scraping {config['name']}: {str(e)}")
        else:
            logger.info("HTML scraping disabled - only using RSS feeds")

        logger.info(f"Total events fetched from government sources: {len(all_events)}")
        return all_events

    def _fetch_rss_feed(self, source_id: str, config: Dict) -> List[Dict]:
        """
        Fetch and parse an RSS feed.

        Args:
            source_id: Source identifier
            config: Source configuration

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Parse RSS feed
            feed = feedparser.parse(config['url'])

            if feed.bozo:
                logger.warning(f"Feed {source_id} has parsing issues: {feed.bozo_exception}")

            # Process entries
            for entry in feed.entries:
                # Parse published date
                pub_date = self._parse_published_date(entry)
                if pub_date and pub_date < self.cutoff_date:
                    continue

                # Extract event data
                event = self._extract_rss_event(entry, config['name'])
                if event:
                    events.append(event)

        except Exception as e:
            logger.error(f"Error parsing RSS feed {source_id}: {str(e)}", exc_info=True)

        return events

    def _parse_published_date(self, entry) -> Optional[datetime]:
        """Parse published date from RSS entry."""
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                time_struct = getattr(entry, date_field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except Exception:
                        pass
        return None

    def _extract_rss_event(self, entry, source_name: str) -> Optional[Dict]:
        """
        Extract event data from RSS entry.

        Args:
            entry: RSS feed entry
            source_name: Name of the source

        Returns:
            Event dictionary or None
        """
        try:
            title = entry.get('title', '').strip()
            if not title:
                return None

            # Extract description/summary
            description = (
                entry.get('summary', '') or
                entry.get('description', '') or
                ''
            ).strip()

            # Remove HTML tags
            description = self._strip_html(description)

            # Extract URL
            source_url = entry.get('link', '')

            # Parse publish date
            pub_date = self._parse_published_date(entry)

            # Build event dictionary
            event = {
                'title': title,
                'description': description[:1000] if description else None,
                'source_url': source_url,
                'discovered_from': f"Government: {source_name}",
                'event_date': pub_date,
                'suggested_category': self._suggest_category(source_name, title, description),
                'keywords': self._extract_keywords(title, description),
                'status': 'discovered',
            }

            return event

        except Exception as e:
            logger.error(f"Error extracting RSS event: {str(e)}", exc_info=True)
            return None

    def _scrape_source(self, source_id: str, config: Dict) -> List[Dict]:
        """
        Scrape HTML source for events.

        Args:
            source_id: Source identifier
            config: Source configuration

        Returns:
            List of event dictionaries
        """
        events = []

        try:
            # Fetch HTML page
            response = requests.get(
                config['url'],
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Source-specific parsing logic
            if source_id == 'nlrb_decisions':
                events = self._parse_nlrb_decisions(soup, config['name'])
            elif source_id == 'nlrb_press':
                events = self._parse_nlrb_press(soup, config['name'])

        except Exception as e:
            logger.error(f"Error scraping {source_id}: {str(e)}", exc_info=True)

        return events

    def _parse_nlrb_decisions(self, soup: BeautifulSoup, source_name: str) -> List[Dict]:
        """
        Parse NLRB decisions page.

        Note: This is a placeholder implementation. Actual parsing would need
        to be customized based on current NLRB website structure.

        Args:
            soup: BeautifulSoup object
            source_name: Source name

        Returns:
            List of event dictionaries
        """
        events = []
        logger.warning("NLRB decisions scraping not fully implemented - placeholder only")
        return events

    def _parse_nlrb_press(self, soup: BeautifulSoup, source_name: str) -> List[Dict]:
        """
        Parse NLRB press releases page.

        Note: This is a placeholder implementation.

        Args:
            soup: BeautifulSoup object
            source_name: Source name

        Returns:
            List of event dictionaries
        """
        events = []
        logger.warning("NLRB press scraping not fully implemented - placeholder only")
        return events

    def _strip_html(self, text: str) -> str:
        """Strip HTML tags from text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def _suggest_category(self, source_name: str, title: str, description: str) -> str:
        """
        Suggest category based on source and content.

        Args:
            source_name: Name of the source
            title: Article title
            description: Article description

        Returns:
            Suggested category
        """
        text = (title + " " + description).lower()

        # OSHA → workplace safety
        if 'osha' in source_name.lower():
            return 'workplace_safety'

        # NLRB → labor organizing
        if 'nlrb' in source_name.lower():
            return 'labor'

        # BLS → economy/employment
        if 'labor statistics' in source_name.lower() or 'bls' in source_name.lower():
            if 'unemployment' in text or 'employment' in text:
                return 'economy'

        # DOL → labor policy
        if 'department of labor' in source_name.lower():
            return 'labor'

        return 'government'

    def _extract_keywords(self, title: str, description: str) -> str:
        """
        Extract keywords from title and description.

        Args:
            title: Article title
            description: Article description

        Returns:
            Comma-separated keywords
        """
        text = (title + " " + description).lower()

        # Government-specific keywords
        keyword_list = [
            'dol', 'nlrb', 'osha', 'bls',
            'violation', 'enforcement', 'penalty', 'fine',
            'ruling', 'decision', 'order', 'complaint',
            'investigation', 'inspection', 'citation',
            'union', 'labor', 'worker', 'workers', 'wage', 'wages',
            'employment', 'unemployment', 'job', 'jobs',
            'safety', 'injury', 'accident', 'fatality',
            'discrimination', 'retaliation', 'unfair labor practice',
            'collective bargaining', 'organizing', 'election',
        ]

        found_keywords = [kw for kw in keyword_list if kw in text]

        return ', '.join(found_keywords[:10])


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = GovernmentFeedScraper(max_age_hours=48, enable_scraping=False)
    events = scraper.fetch_all_sources()

    print(f"\nFetched {len(events)} events from government sources")
    for event in events[:5]:
        print(f"\nTitle: {event['title']}")
        print(f"Source: {event['discovered_from']}")
        print(f"Category: {event['suggested_category']}")
        print(f"Keywords: {event['keywords']}")
