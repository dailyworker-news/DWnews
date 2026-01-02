"""
Source Reliability Scoring - Learning Loop

Tracks and updates source reliability scores based on real-world performance.

Scoring Logic:
- Initial score: Based on source tier (Tier 1: 90-100, Tier 2: 70-89, etc.)
- Accuracy confirmed (7 days, no corrections): +5 points
- Minor correction needed: -5 points
- Source issues correction or retraction: -10 points
- Severe penalty for complete retraction: -30 points
- Fact check pass: +3 points
- Fact check fail: -8 points

Score Range: 1-100 (mapped to credibility_score 1-5 in database)

Event Types:
- article_published: Article using this source published
- correction_issued: Correction issued for article using this source
- fact_check_pass: Source verified accurate
- fact_check_fail: Source found inaccurate
- retraction: Source completely retracted article
- citation_added: Source cited in new article
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Source, SourceReliabilityLog, Article, Correction
from backend.logging_config import get_logger

logger = get_logger(__name__)


class SourceReliabilityScorer:
    """
    Manages source reliability scoring and learning loop
    """

    # Score deltas for different events (on 0-100 scale)
    SCORE_DELTAS = {
        'accuracy_confirmed': +5,
        'minor_correction': -5,
        'correction_issued': -10,
        'retraction': -30,
        'fact_check_pass': +3,
        'fact_check_fail': -8,
        'article_published': 0,  # Neutral event (just tracking)
        'citation_added': 0  # Neutral event (just tracking)
    }

    # Source tier initial scores
    TIER_SCORES = {
        1: 95,  # Wire services, major newspapers
        2: 85,  # Regional newspapers, established outlets
        3: 75,  # Online-native outlets, trade publications
        4: 65,  # Blogs, smaller outlets
        5: 50   # Social media, unverified sources
    }

    def __init__(self, session: Session):
        """
        Initialize the Source Reliability Scorer

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def initialize_source_score(self, source: Source, tier: int = 3) -> int:
        """
        Initialize a new source with a score based on its tier

        Args:
            source: Source instance
            tier: Source tier (1-5, default 3)

        Returns:
            Initial score (0-100 scale)
        """
        initial_score = self.TIER_SCORES.get(tier, 75)

        # Map to credibility_score (1-5 scale)
        source.credibility_score = self._map_to_credibility_score(initial_score)

        logger.info(f"Initialized source {source.id} ({source.name}) with tier {tier} score {initial_score}")

        return initial_score

    def log_event(
        self,
        source_id: int,
        event_type: str,
        article_id: Optional[int] = None,
        correction_id: Optional[int] = None,
        notes: Optional[str] = None,
        automated: bool = True,
        reviewer: Optional[str] = None
    ) -> Optional[SourceReliabilityLog]:
        """
        Log a source reliability event and update score

        Args:
            source_id: Source ID
            event_type: Event type (see SCORE_DELTAS)
            article_id: Related article ID (optional)
            correction_id: Related correction ID (optional)
            notes: Additional notes
            automated: Whether this is automated or manual adjustment
            reviewer: Human reviewer if manual

        Returns:
            SourceReliabilityLog instance if created successfully
        """
        try:
            source = self.session.query(Source).filter(
                Source.id == source_id
            ).first()

            if not source:
                logger.error(f"Source {source_id} not found")
                return None

            # Calculate score delta
            score_delta = self.SCORE_DELTAS.get(event_type, 0)

            # Get current score (on 0-100 scale)
            current_score_100 = self._map_from_credibility_score(source.credibility_score)
            previous_score = current_score_100

            # Calculate new score
            new_score_100 = max(0, min(100, current_score_100 + score_delta))
            new_credibility_score = self._map_to_credibility_score(new_score_100)

            # Create log entry
            log_entry = SourceReliabilityLog(
                source_id=source_id,
                event_type=event_type,
                reliability_delta=score_delta / 20,  # Normalize to 0-5 scale for compatibility
                previous_score=source.credibility_score,
                new_score=new_credibility_score,
                article_id=article_id,
                correction_id=correction_id,
                notes=notes or f"{event_type} event (delta: {score_delta})",
                automated_adjustment=automated,
                manual_override=not automated,
                reviewed_by=reviewer,
                logged_at=datetime.utcnow()
            )

            self.session.add(log_entry)

            # Update source score
            source.credibility_score = new_credibility_score
            source.updated_at = datetime.utcnow()

            self.session.commit()

            logger.info(
                f"Logged {event_type} for source {source_id}: "
                f"{previous_score} -> {new_score_100} "
                f"(credibility: {source.credibility_score})"
            )

            return log_entry

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error logging event for source {source_id}: {e}")
            return None

    def update_for_article_accuracy(
        self,
        article_id: int,
        days_monitored: int = 7
    ) -> int:
        """
        Update source scores based on article accuracy after monitoring period

        Args:
            article_id: Article ID
            days_monitored: Number of days article was monitored

        Returns:
            Number of sources updated
        """
        try:
            article = self.session.query(Article).filter(
                Article.id == article_id
            ).first()

            if not article:
                logger.error(f"Article {article_id} not found")
                return 0

            # Check if article has corrections
            has_corrections = self.session.query(Correction).filter(
                Correction.article_id == article_id,
                Correction.status == 'published'
            ).count() > 0

            # Get article sources
            sources = article.sources
            if not sources:
                return 0

            sources_updated = 0

            for source in sources:
                try:
                    if has_corrections:
                        # Source had accuracy issues
                        event_type = 'correction_issued'
                        notes = f"Article {article_id} required correction after {days_monitored} days"
                    else:
                        # Source remained accurate
                        event_type = 'accuracy_confirmed'
                        notes = f"Article {article_id} verified accurate for {days_monitored} days"

                    log_entry = self.log_event(
                        source_id=source.id,
                        event_type=event_type,
                        article_id=article_id,
                        notes=notes,
                        automated=True
                    )

                    if log_entry:
                        sources_updated += 1

                except Exception as e:
                    logger.error(f"Error updating source {source.id} for article {article_id}: {e}")
                    continue

            logger.info(f"Updated {sources_updated} sources for article {article_id}")
            return sources_updated

        except Exception as e:
            logger.error(f"Error updating article accuracy for article {article_id}: {e}")
            return 0

    def get_source_history(self, source_id: int, limit: int = 50) -> List[SourceReliabilityLog]:
        """
        Get reliability log history for a source

        Args:
            source_id: Source ID
            limit: Maximum number of entries to return

        Returns:
            List of SourceReliabilityLog instances
        """
        return self.session.query(SourceReliabilityLog).filter(
            SourceReliabilityLog.source_id == source_id
        ).order_by(SourceReliabilityLog.logged_at.desc()).limit(limit).all()

    def get_source_stats(self, source_id: int) -> Dict:
        """
        Get statistics for a source

        Args:
            source_id: Source ID

        Returns:
            Dict with source stats
        """
        source = self.session.query(Source).filter(
            Source.id == source_id
        ).first()

        if not source:
            return {}

        # Count events by type
        log_entries = self.session.query(SourceReliabilityLog).filter(
            SourceReliabilityLog.source_id == source_id
        ).all()

        event_counts = {}
        for entry in log_entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1

        # Count articles citing this source
        article_count = self.session.query(Article).join(
            Article.sources
        ).filter(Source.id == source_id).count()

        # Get current score (on 100 scale)
        current_score_100 = self._map_from_credibility_score(source.credibility_score)

        return {
            'source_id': source.id,
            'source_name': source.name,
            'current_score': current_score_100,
            'credibility_score': source.credibility_score,
            'articles_citing': article_count,
            'total_events': len(log_entries),
            'event_counts': event_counts,
            'last_updated': source.updated_at
        }

    def get_reliability_trends(self) -> Dict:
        """
        Get overall reliability trends across all sources

        Returns:
            Dict with reliability trends
        """
        # Average credibility score
        avg_credibility = self.session.query(
            func.avg(Source.credibility_score)
        ).filter(Source.is_active == True).scalar()

        # Count sources by credibility score
        score_distribution = {}
        for score in range(1, 6):
            count = self.session.query(Source).filter(
                Source.credibility_score == score,
                Source.is_active == True
            ).count()
            score_distribution[score] = count

        # Count events in last 30 days
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        recent_events = self.session.query(SourceReliabilityLog).filter(
            SourceReliabilityLog.logged_at >= thirty_days_ago
        ).count()

        # Top performing sources
        top_sources = self.session.query(Source).filter(
            Source.is_active == True
        ).order_by(Source.credibility_score.desc()).limit(10).all()

        return {
            'avg_credibility_score': round(avg_credibility, 2) if avg_credibility else 0,
            'score_distribution': score_distribution,
            'recent_events_30d': recent_events,
            'top_sources': [
                {'id': s.id, 'name': s.name, 'score': s.credibility_score}
                for s in top_sources
            ]
        }

    def _map_to_credibility_score(self, score_100: int) -> int:
        """
        Map 0-100 scale to 1-5 credibility score

        Args:
            score_100: Score on 0-100 scale

        Returns:
            Credibility score (1-5)
        """
        if score_100 >= 90:
            return 5
        elif score_100 >= 75:
            return 4
        elif score_100 >= 60:
            return 3
        elif score_100 >= 40:
            return 2
        else:
            return 1

    def _map_from_credibility_score(self, credibility: int) -> int:
        """
        Map 1-5 credibility score to 0-100 scale (midpoint)

        Args:
            credibility: Credibility score (1-5)

        Returns:
            Score on 0-100 scale
        """
        mapping = {
            5: 95,
            4: 82,
            3: 67,
            2: 50,
            1: 25
        }
        return mapping.get(credibility, 50)


def main():
    """
    Main function for running the Source Reliability Scorer standalone
    """
    from database import get_session

    session = get_session()
    scorer = SourceReliabilityScorer(session)

    print("=" * 60)
    print("SOURCE RELIABILITY SCORER - Learning Loop")
    print("=" * 60)

    # Get overall trends
    trends = scorer.get_reliability_trends()
    print(f"\nOverall Trends:")
    print(f"  Average credibility score: {trends['avg_credibility_score']}/5")
    print(f"  Recent events (30 days): {trends['recent_events_30d']}")

    print(f"\nScore Distribution:")
    for score in range(5, 0, -1):
        count = trends['score_distribution'].get(score, 0)
        print(f"  Score {score}: {count} sources")

    print(f"\nTop Performing Sources:")
    for source in trends['top_sources'][:5]:
        print(f"  {source['name']}: {source['score']}/5")

    session.close()


if __name__ == '__main__':
    main()
