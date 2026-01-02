"""
Signal Intake Agent - Automated Event Discovery

This agent discovers newsworthy labor events from multiple sources:
- RSS feeds (Reuters, AP, ProPublica, labor news)
- Twitter API v2 (labor hashtags, union accounts)
- Reddit API (r/labor, r/WorkReform, local subs)
- Government sources (DOL, NLRB, OSHA, BLS)

Discovered events are stored in the event_candidates table with status='discovered'
for evaluation by the Evaluation Agent.

Usage:
    from backend.agents.signal_intake_agent import SignalIntakeAgent

    agent = SignalIntakeAgent()
    results = agent.discover_events()
    print(f"Discovered {results['total_discovered']} new events")
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

# Import feed modules
from .feeds.rss_feeds import RSSFeedAggregator
from .feeds.twitter_feed import TwitterFeedMonitor
from .feeds.reddit_feed import RedditFeedMonitor
from .feeds.government_feeds import GovernmentFeedScraper

# Import utilities
from .utils.deduplication import EventDeduplicator

# Import database models
from database.models import EventCandidate
from backend.database import get_db

logger = logging.getLogger(__name__)


class SignalIntakeAgent:
    """
    Main orchestrator for automated event discovery.

    Coordinates multiple feed sources, deduplicates events,
    and stores them in the database for downstream processing.
    """

    def __init__(
        self,
        max_age_hours: int = 24,
        enable_rss: bool = True,
        enable_twitter: bool = True,
        enable_reddit: bool = True,
        enable_government: bool = True,
        deduplication_threshold: float = 0.80,
        dry_run: bool = False
    ):
        """
        Initialize Signal Intake Agent.

        Args:
            max_age_hours: Only fetch events from last N hours (default: 24)
            enable_rss: Enable RSS feed aggregation (default: True)
            enable_twitter: Enable Twitter monitoring (default: True)
            enable_reddit: Enable Reddit monitoring (default: True)
            enable_government: Enable government feed scraping (default: True)
            deduplication_threshold: Similarity threshold for deduplication (default: 0.80)
            dry_run: If True, don't write to database (default: False)
        """
        self.max_age_hours = max_age_hours
        self.dry_run = dry_run

        # Initialize feed sources
        self.rss_aggregator = RSSFeedAggregator(max_age_hours=max_age_hours) if enable_rss else None
        self.twitter_monitor = TwitterFeedMonitor(max_age_hours=max_age_hours) if enable_twitter else None
        self.reddit_monitor = RedditFeedMonitor(max_age_hours=max_age_hours) if enable_reddit else None
        self.government_scraper = GovernmentFeedScraper(max_age_hours=max_age_hours) if enable_government else None

        # Initialize deduplicator
        self.deduplicator = EventDeduplicator(similarity_threshold=deduplication_threshold)

        logger.info(f"Signal Intake Agent initialized (max_age={max_age_hours}h, dry_run={dry_run})")

    def discover_events(self, session: Optional[Session] = None) -> Dict:
        """
        Discover events from all configured sources.

        Args:
            session: Database session (optional, will create if not provided)

        Returns:
            Dictionary with discovery statistics:
            {
                'total_fetched': int,
                'total_unique': int,
                'total_discovered': int,
                'by_source': {
                    'rss': int,
                    'twitter': int,
                    'reddit': int,
                    'government': int
                },
                'errors': List[str]
            }
        """
        start_time = datetime.now()
        logger.info(f"Starting event discovery run at {start_time}")

        # Create database session if not provided
        session_provided = session is not None
        if not session_provided:
            session = next(get_db())

        try:
            # Reset deduplication cache for fresh run
            self.deduplicator.reset_cache()

            # Fetch from all sources
            all_events = []
            source_stats = {}
            errors = []

            # RSS feeds
            if self.rss_aggregator:
                try:
                    rss_events = self.rss_aggregator.fetch_all_feeds()
                    all_events.extend(rss_events)
                    source_stats['rss'] = len(rss_events)
                    logger.info(f"RSS: Fetched {len(rss_events)} events")
                except Exception as e:
                    error_msg = f"RSS fetch failed: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    source_stats['rss'] = 0

            # Twitter
            if self.twitter_monitor:
                try:
                    twitter_events = self.twitter_monitor.fetch_all_tweets()
                    all_events.extend(twitter_events)
                    source_stats['twitter'] = len(twitter_events)
                    logger.info(f"Twitter: Fetched {len(twitter_events)} events")
                except Exception as e:
                    error_msg = f"Twitter fetch failed: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    source_stats['twitter'] = 0

            # Reddit
            if self.reddit_monitor:
                try:
                    reddit_events = self.reddit_monitor.fetch_all_posts()
                    all_events.extend(reddit_events)
                    source_stats['reddit'] = len(reddit_events)
                    logger.info(f"Reddit: Fetched {len(reddit_events)} events")
                except Exception as e:
                    error_msg = f"Reddit fetch failed: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    source_stats['reddit'] = 0

            # Government sources
            if self.government_scraper:
                try:
                    gov_events = self.government_scraper.fetch_all_sources()
                    all_events.extend(gov_events)
                    source_stats['government'] = len(gov_events)
                    logger.info(f"Government: Fetched {len(gov_events)} events")
                except Exception as e:
                    error_msg = f"Government fetch failed: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    errors.append(error_msg)
                    source_stats['government'] = 0

            total_fetched = len(all_events)
            logger.info(f"Total events fetched: {total_fetched}")

            # Deduplicate events
            unique_events = self.deduplicator.filter_duplicates(
                all_events,
                session=session,
                check_database=not self.dry_run
            )

            total_unique = len(unique_events)
            logger.info(f"Unique events after deduplication: {total_unique}")

            # Store events in database
            total_stored = 0
            if not self.dry_run:
                total_stored = self._store_events(unique_events, session)
                logger.info(f"Stored {total_stored} events in database")
            else:
                logger.info("DRY RUN: Skipping database storage")
                total_stored = total_unique

            # Calculate runtime
            end_time = datetime.now()
            runtime_seconds = (end_time - start_time).total_seconds()

            # Prepare results
            results = {
                'total_fetched': total_fetched,
                'total_unique': total_unique,
                'total_discovered': total_stored,
                'by_source': source_stats,
                'errors': errors,
                'runtime_seconds': runtime_seconds,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
            }

            logger.info(f"Discovery run completed in {runtime_seconds:.2f}s: "
                       f"{total_fetched} fetched, {total_unique} unique, {total_stored} stored")

            return results

        except Exception as e:
            logger.error(f"Error in discovery run: {str(e)}", exc_info=True)
            raise

        finally:
            # Close session if we created it
            if not session_provided:
                session.close()

    def _store_events(self, events: List[Dict], session: Session) -> int:
        """
        Store discovered events in database.

        Args:
            events: List of event dictionaries
            session: Database session

        Returns:
            Number of events successfully stored
        """
        stored_count = 0

        for event in events:
            try:
                # Create EventCandidate record
                candidate = EventCandidate(
                    title=event['title'],
                    description=event.get('description'),
                    source_url=event.get('source_url'),
                    discovered_from=event['discovered_from'],
                    event_date=event.get('event_date'),
                    suggested_category=event.get('suggested_category'),
                    keywords=event.get('keywords'),
                    status='discovered'
                )

                session.add(candidate)
                stored_count += 1

            except Exception as e:
                logger.error(f"Error storing event '{event.get('title', 'Unknown')}': {str(e)}")

        # Commit all at once
        try:
            session.commit()
            logger.info(f"Successfully committed {stored_count} events to database")
        except Exception as e:
            logger.error(f"Error committing events: {str(e)}", exc_info=True)
            session.rollback()
            raise

        return stored_count

    def get_discovery_stats(self, session: Optional[Session] = None, days: int = 7) -> Dict:
        """
        Get statistics about recent discoveries.

        Args:
            session: Database session (optional)
            days: Number of days to look back (default: 7)

        Returns:
            Dictionary with statistics
        """
        session_provided = session is not None
        if not session_provided:
            session = next(get_db())

        try:
            from datetime import timedelta

            cutoff = datetime.now() - timedelta(days=days)

            # Count total discoveries
            total = session.query(EventCandidate).filter(
                EventCandidate.discovery_date >= cutoff
            ).count()

            # Count by status
            by_status = {}
            for status in ['discovered', 'evaluated', 'approved', 'rejected', 'converted']:
                count = session.query(EventCandidate).filter(
                    EventCandidate.discovery_date >= cutoff,
                    EventCandidate.status == status
                ).count()
                by_status[status] = count

            # Count by source
            results = session.query(
                EventCandidate.discovered_from
            ).filter(
                EventCandidate.discovery_date >= cutoff
            ).all()

            by_source = {}
            for (source,) in results:
                if source:
                    source_type = source.split(':')[0] if ':' in source else source
                    by_source[source_type] = by_source.get(source_type, 0) + 1

            return {
                'total_discoveries': total,
                'by_status': by_status,
                'by_source': by_source,
                'days': days,
            }

        finally:
            if not session_provided:
                session.close()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create agent
    agent = SignalIntakeAgent(
        max_age_hours=24,
        dry_run=False  # Set to True for testing without database writes
    )

    # Run discovery
    results = agent.discover_events()

    # Print results
    print("\n" + "="*60)
    print("SIGNAL INTAKE AGENT - DISCOVERY RESULTS")
    print("="*60)
    print(f"Runtime: {results['runtime_seconds']:.2f} seconds")
    print(f"Total fetched: {results['total_fetched']}")
    print(f"Unique events: {results['total_unique']}")
    print(f"Stored in DB: {results['total_discovered']}")
    print("\nBy source:")
    for source, count in results['by_source'].items():
        print(f"  {source}: {count}")
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    print("="*60)
