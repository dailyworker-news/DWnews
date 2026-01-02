"""
Timeline Constructor for Investigatory Journalist Agent (Phase 6.9.2)

Constructs chronological timelines from social media mentions:
- Sorts events chronologically
- Identifies earliest/latest mentions
- Clusters related events
- Identifies key moments with significance scoring
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class TimelineConstructor:
    """
    Construct chronological timelines from social media events.

    Capabilities:
    - Sort events chronologically
    - Identify earliest/latest mentions
    - Calculate event duration
    - Cluster related events
    - Identify key moments
    """

    def __init__(self):
        """Initialize timeline constructor"""
        pass

    def construct_timeline(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct chronological timeline from mixed social media sources.

        Args:
            sources: List of source dicts (Twitter, Reddit, etc.)

        Returns:
            Timeline dictionary with events, metadata
        """
        if not sources:
            return {
                'events': [],
                'earliest_event': None,
                'latest_event': None,
                'duration_hours': 0
            }

        # Extract events from sources
        events = []
        for source in sources:
            event = self._source_to_event(source)
            if event:
                events.append(event)

        # Sort chronologically
        sorted_events = sorted(events, key=lambda e: e['timestamp'])

        if not sorted_events:
            return {
                'events': [],
                'earliest_event': None,
                'latest_event': None,
                'duration_hours': 0
            }

        # Calculate metadata
        earliest = sorted_events[0]
        latest = sorted_events[-1]
        duration = (latest['timestamp'] - earliest['timestamp']).total_seconds() / 3600

        return {
            'events': sorted_events,
            'earliest_event': earliest,
            'latest_event': latest,
            'duration_hours': round(duration, 1),
            'total_events': len(sorted_events)
        }

    def cluster_related_events(self, events: List[Dict[str, Any]], time_window_hours: int = 2) -> List[Dict[str, Any]]:
        """
        Cluster related events within time windows.

        Args:
            events: List of event dictionaries
            time_window_hours: Max hours between events in same cluster

        Returns:
            List of event clusters
        """
        if not events:
            return []

        # Sort by timestamp
        sorted_events = sorted(events, key=lambda e: e['timestamp'])

        clusters = []
        current_cluster = {
            'events': [sorted_events[0]],
            'start_time': sorted_events[0]['timestamp'],
            'theme': self._extract_theme(sorted_events[0])
        }

        for event in sorted_events[1:]:
            # Check if within time window
            time_diff = (event['timestamp'] - current_cluster['start_time']).total_seconds() / 3600

            if time_diff <= time_window_hours:
                # Add to current cluster
                current_cluster['events'].append(event)
            else:
                # Start new cluster
                clusters.append(current_cluster)
                current_cluster = {
                    'events': [event],
                    'start_time': event['timestamp'],
                    'theme': self._extract_theme(event)
                }

        # Add final cluster
        if current_cluster['events']:
            clusters.append(current_cluster)

        # Add cluster metadata
        for cluster in clusters:
            cluster['event_count'] = len(cluster['events'])
            cluster['end_time'] = cluster['events'][-1]['timestamp']
            duration = (cluster['end_time'] - cluster['start_time']).total_seconds() / 3600
            cluster['duration_hours'] = round(duration, 1)

        return clusters

    def identify_key_moments(self, timeline: Dict[str, Any], min_significance: float = 70.0) -> List[Dict[str, Any]]:
        """
        Identify key moments in timeline based on significance.

        Args:
            timeline: Timeline dictionary
            min_significance: Minimum significance score (0-100)

        Returns:
            List of key moment dictionaries
        """
        events = timeline.get('events', [])
        key_moments = []

        for event in events:
            significance = self._calculate_significance(event)

            if significance >= min_significance:
                key_moments.append({
                    'timestamp': event['timestamp'],
                    'description': event.get('text', event.get('title', 'Unknown event')),
                    'platform': event.get('platform', 'unknown'),
                    'author': event.get('author', 'unknown'),
                    'significance_score': round(significance, 1)
                })

        # Sort by significance
        key_moments.sort(key=lambda m: m['significance_score'], reverse=True)

        return key_moments

    def _source_to_event(self, source: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert source to timeline event.

        Args:
            source: Source dictionary

        Returns:
            Event dictionary or None
        """
        try:
            # Extract timestamp
            timestamp = source.get('timestamp')
            if not timestamp:
                # Try other timestamp fields
                if 'created_at' in source:
                    timestamp = source['created_at']
                elif 'event_date' in source:
                    timestamp = source['event_date']

            # Ensure timestamp is datetime
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.utcfromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            if not timestamp:
                return None

            # Build event
            event = {
                'timestamp': timestamp,
                'platform': source.get('platform', 'unknown'),
                'id': source.get('id', ''),
                'text': source.get('text', source.get('title', '')),
                'author': source.get('author', 'unknown'),
                'source_type': source.get('source_type', 'unknown')
            }

            return event

        except Exception as e:
            logger.error(f"Error converting source to event: {e}")
            return None

    def _extract_theme(self, event: Dict[str, Any]) -> str:
        """
        Extract theme from event text.

        Args:
            event: Event dictionary

        Returns:
            Theme string
        """
        text = event.get('text', '').lower()

        # Simple keyword matching
        if any(word in text for word in ['strike', 'walkout', 'protest']):
            return 'labor_action'
        elif any(word in text for word in ['union', 'organizing', 'election']):
            return 'union_organizing'
        elif any(word in text for word in ['fired', 'layoff', 'termination']):
            return 'employment_change'
        elif any(word in text for word in ['wage', 'pay', 'salary']):
            return 'compensation'
        else:
            return 'general'

    def _calculate_significance(self, event: Dict[str, Any]) -> float:
        """
        Calculate significance score for event.

        Factors:
        - Platform credibility
        - Author verification/karma
        - Engagement metrics
        - Content indicators

        Args:
            event: Event dictionary

        Returns:
            Significance score 0-100
        """
        score = 50.0  # Base score

        # Platform credibility
        platform = event.get('platform', '')
        if platform == 'twitter':
            # Check if verified
            if isinstance(event.get('author'), dict) and event['author'].get('verified'):
                score += 20.0
        elif platform == 'reddit':
            # Check karma
            if isinstance(event.get('author'), dict):
                karma = event['author'].get('link_karma', 0) + event['author'].get('comment_karma', 0)
                if karma > 10000:
                    score += 15.0

        # Engagement metrics
        if 'engagement' in event:
            engagement = event['engagement']
            if isinstance(engagement, dict):
                total = sum(engagement.values()) if all(isinstance(v, (int, float)) for v in engagement.values()) else 0
                if total > 1000:
                    score += 15.0
                elif total > 100:
                    score += 10.0

        # Content indicators (firsthand language)
        text = event.get('text', '').lower()
        if any(phrase in text for phrase in ['i was', 'i saw', 'firsthand', 'i witnessed']):
            score += 15.0

        return min(score, 100.0)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    constructor = TimelineConstructor()

    # Mock events
    mock_events = [
        {
            'platform': 'twitter',
            'timestamp': datetime.utcnow() - timedelta(hours=6),
            'text': 'Union vote scheduled for tomorrow',
            'author': {'username': 'union_organizer', 'verified': False}
        },
        {
            'platform': 'reddit',
            'timestamp': datetime.utcnow() - timedelta(hours=3),
            'text': 'I was there when workers walked out',
            'author': {'name': 'warehouse_worker', 'link_karma': 500, 'comment_karma': 1500}
        },
        {
            'platform': 'twitter',
            'timestamp': datetime.utcnow() - timedelta(hours=1),
            'text': 'Reuters: Amazon workers strike continues',
            'author': {'username': 'reuters', 'verified': True}
        }
    ]

    # Construct timeline
    timeline = constructor.construct_timeline(mock_events)
    print(f"\nTimeline: {timeline['total_events']} events over {timeline['duration_hours']:.1f} hours")

    # Cluster events
    clusters = constructor.cluster_related_events(timeline['events'])
    print(f"\nEvent clusters: {len(clusters)}")

    # Identify key moments
    key_moments = constructor.identify_key_moments(timeline)
    print(f"\nKey moments: {len(key_moments)}")
