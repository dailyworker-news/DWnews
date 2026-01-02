"""
Event Deduplication for Signal Intake Agent.

Prevents duplicate events from being stored in the database by:
- Normalizing titles and hashing them
- Checking for similar events in the last 7 days
- Using fuzzy matching for 80%+ similarity detection
- URL-based deduplication for exact matches
"""

import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from difflib import SequenceMatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EventDeduplicator:
    """
    Deduplicates event candidates to avoid storing duplicate discoveries.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.80,
        lookback_days: int = 7,
        enable_url_dedup: bool = True,
        enable_title_dedup: bool = True
    ):
        """
        Initialize event deduplicator.

        Args:
            similarity_threshold: Minimum similarity ratio (0-1) to consider duplicate (default: 0.80)
            lookback_days: Days to look back for duplicates (default: 7)
            enable_url_dedup: Enable URL-based deduplication (default: True)
            enable_title_dedup: Enable title-based fuzzy deduplication (default: True)
        """
        self.similarity_threshold = similarity_threshold
        self.lookback_days = lookback_days
        self.enable_url_dedup = enable_url_dedup
        self.enable_title_dedup = enable_title_dedup
        self.cutoff_date = datetime.now() - timedelta(days=lookback_days)

        # In-memory caches for current batch
        self.seen_urls: Set[str] = set()
        self.seen_title_hashes: Set[str] = set()
        self.seen_titles: List[str] = []

    def is_duplicate(
        self,
        event: Dict,
        session: Optional[Session] = None,
        check_database: bool = True
    ) -> bool:
        """
        Check if an event is a duplicate.

        Args:
            event: Event dictionary to check
            session: Database session for checking existing events (optional)
            check_database: If True, check database for duplicates (default: True)

        Returns:
            True if event is a duplicate, False otherwise
        """
        # URL-based deduplication (exact match)
        if self.enable_url_dedup and event.get('source_url'):
            url = event['source_url']

            # Check in-memory cache
            if url in self.seen_urls:
                logger.debug(f"Duplicate URL (in-memory): {url}")
                return True

            # Check database
            if check_database and session:
                if self._is_duplicate_url_in_db(url, session):
                    logger.debug(f"Duplicate URL (database): {url}")
                    self.seen_urls.add(url)
                    return True

            # Not a duplicate, add to cache
            self.seen_urls.add(url)

        # Title-based deduplication (fuzzy match)
        if self.enable_title_dedup and event.get('title'):
            title = event['title']

            # Normalize title
            normalized_title = self._normalize_title(title)
            title_hash = self._hash_title(normalized_title)

            # Check exact hash match (in-memory)
            if title_hash in self.seen_title_hashes:
                logger.debug(f"Duplicate title hash (in-memory): {title}")
                return True

            # Check fuzzy match (in-memory)
            if self._is_similar_title_in_memory(normalized_title):
                logger.debug(f"Duplicate title (fuzzy, in-memory): {title}")
                return True

            # Check database
            if check_database and session:
                if self._is_similar_title_in_db(normalized_title, session):
                    logger.debug(f"Duplicate title (database): {title}")
                    self.seen_title_hashes.add(title_hash)
                    self.seen_titles.append(normalized_title)
                    return True

            # Not a duplicate, add to caches
            self.seen_title_hashes.add(title_hash)
            self.seen_titles.append(normalized_title)

        return False

    def filter_duplicates(
        self,
        events: List[Dict],
        session: Optional[Session] = None,
        check_database: bool = True
    ) -> List[Dict]:
        """
        Filter out duplicate events from a list.

        Args:
            events: List of event dictionaries
            session: Database session for checking existing events (optional)
            check_database: If True, check database for duplicates (default: True)

        Returns:
            List of unique events (duplicates removed)
        """
        unique_events = []

        for event in events:
            if not self.is_duplicate(event, session, check_database):
                unique_events.append(event)
            else:
                logger.debug(f"Filtered duplicate: {event.get('title', 'Unknown')}")

        logger.info(f"Filtered {len(events) - len(unique_events)} duplicates out of {len(events)} events")
        return unique_events

    def reset_cache(self):
        """Reset in-memory deduplication caches."""
        self.seen_urls.clear()
        self.seen_title_hashes.clear()
        self.seen_titles.clear()
        logger.debug("Deduplication cache reset")

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison.

        Args:
            title: Raw title

        Returns:
            Normalized title (lowercase, no punctuation, normalized whitespace)
        """
        # Convert to lowercase
        normalized = title.lower()

        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)

        # Normalize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        # Strip leading/trailing whitespace
        normalized = normalized.strip()

        return normalized

    def _hash_title(self, normalized_title: str) -> str:
        """
        Create a hash of normalized title.

        Args:
            normalized_title: Normalized title

        Returns:
            SHA-256 hash of title
        """
        return hashlib.sha256(normalized_title.encode()).hexdigest()

    def _is_similar_title_in_memory(self, normalized_title: str) -> bool:
        """
        Check if a similar title exists in in-memory cache.

        Args:
            normalized_title: Normalized title to check

        Returns:
            True if similar title found
        """
        for seen_title in self.seen_titles:
            similarity = self._calculate_similarity(normalized_title, seen_title)
            if similarity >= self.similarity_threshold:
                logger.debug(f"Similar titles (ratio={similarity:.2f}): '{normalized_title}' ~ '{seen_title}'")
                return True

        return False

    def _calculate_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity ratio between two titles.

        Args:
            title1: First title
            title2: Second title

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return SequenceMatcher(None, title1, title2).ratio()

    def _is_duplicate_url_in_db(self, url: str, session: Session) -> bool:
        """
        Check if URL exists in database.

        Args:
            url: Source URL to check
            session: Database session

        Returns:
            True if URL found in database
        """
        try:
            # Import here to avoid circular dependency
            from database.models import EventCandidate

            # Query for matching URL in recent events
            existing = session.query(EventCandidate).filter(
                EventCandidate.source_url == url,
                EventCandidate.discovery_date >= self.cutoff_date
            ).first()

            return existing is not None

        except Exception as e:
            logger.error(f"Error checking URL in database: {str(e)}", exc_info=True)
            return False

    def _is_similar_title_in_db(self, normalized_title: str, session: Session) -> bool:
        """
        Check if similar title exists in database.

        Args:
            normalized_title: Normalized title to check
            session: Database session

        Returns:
            True if similar title found in database
        """
        try:
            # Import here to avoid circular dependency
            from database.models import EventCandidate

            # Fetch recent titles from database
            recent_events = session.query(EventCandidate).filter(
                EventCandidate.discovery_date >= self.cutoff_date
            ).all()

            # Check similarity against each recent event
            for event in recent_events:
                if not event.title:
                    continue

                db_normalized = self._normalize_title(event.title)
                similarity = self._calculate_similarity(normalized_title, db_normalized)

                if similarity >= self.similarity_threshold:
                    logger.debug(f"Similar in DB (ratio={similarity:.2f}): '{normalized_title}' ~ '{db_normalized}'")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error checking title in database: {str(e)}", exc_info=True)
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    deduplicator = EventDeduplicator(similarity_threshold=0.80)

    # Test events
    events = [
        {
            'title': 'Amazon workers in NYC vote to unionize',
            'source_url': 'https://example.com/article1',
        },
        {
            'title': 'Amazon workers in NYC vote to unionize!',  # Very similar
            'source_url': 'https://example.com/article2',
        },
        {
            'title': 'NYC Amazon workers vote for union',  # Similar but different order
            'source_url': 'https://example.com/article3',
        },
        {
            'title': 'Starbucks baristas file for union election',  # Different
            'source_url': 'https://example.com/article4',
        },
        {
            'title': 'Amazon workers in NYC vote to unionize',  # Exact duplicate
            'source_url': 'https://example.com/article1',  # Same URL
        },
    ]

    # Filter duplicates
    unique = deduplicator.filter_duplicates(events, check_database=False)

    print(f"\nOriginal: {len(events)} events")
    print(f"After deduplication: {len(unique)} events")
    print("\nUnique events:")
    for event in unique:
        print(f"  - {event['title']}")
