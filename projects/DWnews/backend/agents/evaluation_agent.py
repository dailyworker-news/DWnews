"""
Evaluation Agent - Newsworthiness Scoring

Evaluates discovered events and scores them on newsworthiness to determine
which events should be converted into articles.

Scoring Algorithm:
- Worker Impact (30% weight): Impact on working-class people ($45k-$350k)
- Timeliness (20% weight): How urgent/timely is this event
- Verifiability (20% weight): Can this be verified with credible sources
- Regional Relevance (15% weight): Relevance to target regions
- Conflict (10% weight): Does this involve conflict/injustice
- Novelty (5% weight): Is this new/unique or repetitive

Final Score = Weighted average (0-100 scale)

Thresholds:
- ≥60: APPROVE - Create topic record, mark as 'approved'
- 30-59: HOLD - Mark as 'hold' for human review
- <30: REJECT - Mark as 'rejected' with reason

Target: 10-20% approval rate
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import EventCandidate, Topic, Category
from agents.scoring import (
    WorkerImpactScorer,
    TimelinessScorer,
    VerifiabilityScorer,
    RegionalScorer,
    ConflictScorer,
    NoveltyScorer
)


class EvaluationAgent:
    """
    Evaluates event candidates and scores them on newsworthiness
    """

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        'worker_impact': 0.30,
        'timeliness': 0.20,
        'verifiability': 0.20,
        'regional_relevance': 0.15,
        'conflict': 0.10,
        'novelty': 0.05
    }

    # Score thresholds
    MIN_APPROVAL_SCORE = 65.0  # Raised from 60 to achieve 10-20% approval rate
    MIN_HOLD_SCORE = 30.0

    def __init__(self, session: Session):
        """
        Initialize the Evaluation Agent

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

        # Initialize all scorers
        self.worker_impact_scorer = WorkerImpactScorer()
        self.timeliness_scorer = TimelinessScorer()
        self.verifiability_scorer = VerifiabilityScorer()
        self.regional_scorer = RegionalScorer(db_session=session)
        self.conflict_scorer = ConflictScorer()
        self.novelty_scorer = NoveltyScorer(db_session=session)

    def evaluate_event(self, event: EventCandidate) -> Dict:
        """
        Score an event on 6 dimensions and calculate final newsworthiness score

        Args:
            event: EventCandidate model instance

        Returns:
            Dict with scores for each dimension and final weighted score
        """
        # Convert EventCandidate to dict for scorers
        event_dict = {
            'title': event.title,
            'description': event.description,
            'source_url': event.source_url,
            'discovered_from': event.discovered_from,
            'event_date': event.event_date,
            'discovery_date': event.discovery_date,
            'is_national': event.is_national,
            'is_local': event.is_local,
            'region_id': event.region_id
        }

        # Fetch recent approved events for novelty scoring
        recent_events = self.novelty_scorer.fetch_recent_approved_events(days=7)

        # Score each dimension (0-10)
        worker_impact = self.worker_impact_scorer.score(event_dict)
        timeliness = self.timeliness_scorer.score(event_dict)
        verifiability = self.verifiability_scorer.score(event_dict)
        regional_relevance = self.regional_scorer.score(event_dict)
        conflict = self.conflict_scorer.score(event_dict)
        novelty = self.novelty_scorer.score(event_dict, recent_events)

        # Calculate weighted final score (0-100 scale)
        final_score = (
            (worker_impact * self.WEIGHTS['worker_impact']) +
            (timeliness * self.WEIGHTS['timeliness']) +
            (verifiability * self.WEIGHTS['verifiability']) +
            (regional_relevance * self.WEIGHTS['regional_relevance']) +
            (conflict * self.WEIGHTS['conflict']) +
            (novelty * self.WEIGHTS['novelty'])
        ) * 10  # Scale from 0-10 to 0-100

        return {
            'worker_impact_score': round(worker_impact, 2),
            'timeliness_score': round(timeliness, 2),
            'verifiability_score': round(verifiability, 2),
            'regional_relevance_score': round(regional_relevance, 2),
            'conflict_score': round(conflict, 2),
            'novelty_score': round(novelty, 2),
            'final_newsworthiness_score': round(final_score, 2)
        }

    def process_discovered_events(self, limit: Optional[int] = None) -> Dict:
        """
        Process all discovered events and update their status

        Args:
            limit: Optional limit on number of events to process

        Returns:
            Dict with processing statistics
        """
        # Query events with status='discovered'
        query = self.session.query(EventCandidate).filter(
            EventCandidate.status == 'discovered'
        ).order_by(EventCandidate.discovery_date.desc())

        if limit:
            query = query.limit(limit)

        events = query.all()

        approved_count = 0
        rejected_count = 0
        hold_count = 0

        for event in events:
            try:
                # Score the event
                scores = self.evaluate_event(event)

                # Update event with scores
                event.worker_impact_score = scores['worker_impact_score']
                event.timeliness_score = scores['timeliness_score']
                event.verifiability_score = scores['verifiability_score']
                event.regional_relevance_score = scores['regional_relevance_score']
                event.final_newsworthiness_score = scores['final_newsworthiness_score']
                event.evaluated_at = datetime.utcnow()

                # Determine status based on final score
                final_score = scores['final_newsworthiness_score']

                if final_score >= self.MIN_APPROVAL_SCORE:
                    # APPROVE: Create topic and mark approved
                    event.status = 'approved'
                    try:
                        self.create_topic_from_event(event)
                        self.session.commit()  # Commit after topic creation
                        approved_count += 1
                    except Exception as topic_error:
                        print(f"Error creating topic for event {event.id}: {topic_error}")
                        self.session.rollback()
                        event.status = 'evaluated'
                        event.rejection_reason = f"Score {final_score:.1f} approved but topic creation failed"
                        self.session.commit()
                        hold_count += 1

                elif final_score >= self.MIN_HOLD_SCORE:
                    # HOLD: Mark for human review
                    event.status = 'evaluated'  # Use 'evaluated' status instead of 'hold'
                    event.rejection_reason = f"Score {final_score:.1f} requires human review (hold threshold: {self.MIN_HOLD_SCORE}-{self.MIN_APPROVAL_SCORE})"
                    self.session.commit()
                    hold_count += 1

                else:
                    # REJECT: Score too low
                    event.status = 'rejected'
                    event.rejection_reason = f"Score {final_score:.1f} below approval threshold {self.MIN_APPROVAL_SCORE}"
                    self.session.commit()
                    rejected_count += 1

            except Exception as e:
                self.session.rollback()
                print(f"Error processing event {event.id}: {e}")
                continue

        return {
            'total_processed': len(events),
            'approved': approved_count,
            'hold': hold_count,
            'rejected': rejected_count,
            'approval_rate': round((approved_count / len(events) * 100), 2) if events else 0
        }

    def create_topic_from_event(self, event: EventCandidate):
        """
        Create a topic record for approved events

        Args:
            event: Approved EventCandidate instance
        """
        # Infer category from suggested_category or keywords
        category = None
        if event.suggested_category:
            category = self.session.query(Category).filter(
                Category.slug == event.suggested_category
            ).first()

        # If no category found, try to infer from content
        if not category:
            category = self._infer_category(event)

        # Create topic
        topic = Topic(
            title=event.title,
            description=event.description,
            keywords=event.keywords,
            discovered_from=event.discovered_from,
            discovery_date=event.discovery_date,
            category_id=category.id if category else None,
            is_national=event.is_national,
            is_local=event.is_local,
            region_id=event.region_id,
            status='approved',
            worker_relevance_score=event.worker_impact_score,
            engagement_score=event.final_newsworthiness_score,
            source_count=0,  # Will be updated by Verification Agent
            academic_citation_count=0,
            verification_status='pending'
        )

        self.session.add(topic)
        self.session.flush()  # Get topic.id before linking
        event.topic_id = topic.id

    def _infer_category(self, event: EventCandidate) -> Optional[Category]:
        """
        Infer category from event content

        Args:
            event: EventCandidate instance

        Returns:
            Category instance or None
        """
        text = f"{event.title} {event.description}".lower()

        # Simple keyword-based category inference
        category_keywords = {
            'labor-organizing': ['union', 'organize', 'strike', 'labor', 'collective bargaining'],
            'workplace-conditions': ['safety', 'osha', 'working conditions', 'hazard', 'injury'],
            'wages-benefits': ['wage', 'salary', 'pay', 'benefits', 'overtime', 'minimum wage'],
            'economic-inequality': ['inequality', 'wealth gap', 'income', 'poverty', 'class'],
            'housing': ['housing', 'rent', 'eviction', 'landlord', 'affordable housing'],
            'healthcare': ['healthcare', 'medical', 'insurance', 'hospital', 'nurse'],
            'education': ['education', 'school', 'teacher', 'student', 'university'],
            'climate-labor': ['climate', 'environment', 'green jobs', 'renewable'],
            'technology-labor': ['tech', 'automation', 'gig worker', 'app', 'algorithm']
        }

        best_match = None
        best_score = 0

        for slug, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_match = slug

        if best_match:
            return self.session.query(Category).filter(
                Category.slug == best_match
            ).first()

        return None

    def get_evaluation_stats(self) -> Dict:
        """
        Get statistics about evaluated events

        Returns:
            Dict with evaluation statistics
        """
        # Count events by status
        total_discovered = self.session.query(EventCandidate).filter(
            EventCandidate.status == 'discovered'
        ).count()

        total_evaluated = self.session.query(EventCandidate).filter(
            EventCandidate.status.in_(['approved', 'rejected', 'evaluated'])
        ).count()

        approved = self.session.query(EventCandidate).filter(
            EventCandidate.status == 'approved'
        ).count()

        rejected = self.session.query(EventCandidate).filter(
            EventCandidate.status == 'rejected'
        ).count()

        hold = self.session.query(EventCandidate).filter(
            EventCandidate.status == 'evaluated'
        ).count()

        # Calculate average scores for approved events
        from sqlalchemy import func
        avg_scores = self.session.query(
            func.avg(EventCandidate.worker_impact_score),
            func.avg(EventCandidate.timeliness_score),
            func.avg(EventCandidate.verifiability_score),
            func.avg(EventCandidate.regional_relevance_score),
            func.avg(EventCandidate.final_newsworthiness_score)
        ).filter(EventCandidate.status == 'approved').first()

        return {
            'total_discovered': total_discovered,
            'total_evaluated': total_evaluated,
            'approved': approved,
            'rejected': rejected,
            'hold': hold,
            'approval_rate': round((approved / total_evaluated * 100), 2) if total_evaluated > 0 else 0,
            'avg_approved_scores': {
                'worker_impact': round(avg_scores[0], 2) if avg_scores[0] else 0,
                'timeliness': round(avg_scores[1], 2) if avg_scores[1] else 0,
                'verifiability': round(avg_scores[2], 2) if avg_scores[2] else 0,
                'regional_relevance': round(avg_scores[3], 2) if avg_scores[3] else 0,
                'final_newsworthiness': round(avg_scores[4], 2) if avg_scores[4] else 0
            }
        }


def main():
    """
    Main function for running the Evaluation Agent standalone
    """
    from database import get_session

    session = get_session()
    agent = EvaluationAgent(session)

    print("=" * 60)
    print("EVALUATION AGENT - Newsworthiness Scoring")
    print("=" * 60)

    # Get current stats
    stats = agent.get_evaluation_stats()
    print(f"\nCurrent Status:")
    print(f"  Discovered events: {stats['total_discovered']}")
    print(f"  Total evaluated: {stats['total_evaluated']}")
    print(f"  Approved: {stats['approved']}")
    print(f"  On hold: {stats['hold']}")
    print(f"  Rejected: {stats['rejected']}")
    print(f"  Approval rate: {stats['approval_rate']}%")

    if stats['total_discovered'] == 0:
        print("\nNo discovered events to process.")
        return

    # Process discovered events
    print(f"\nProcessing {stats['total_discovered']} discovered events...")
    results = agent.process_discovered_events()

    print(f"\n{'=' * 60}")
    print("RESULTS:")
    print(f"{'=' * 60}")
    print(f"Total processed: {results['total_processed']}")
    print(f"Approved: {results['approved']} ({results['approval_rate']}%)")
    print(f"On hold: {results['hold']}")
    print(f"Rejected: {results['rejected']}")

    # Show updated stats
    updated_stats = agent.get_evaluation_stats()
    print(f"\nUpdated Status:")
    print(f"  Total evaluated: {updated_stats['total_evaluated']}")
    print(f"  Overall approval rate: {updated_stats['approval_rate']}%")

    if updated_stats['approved'] > 0:
        print(f"\nAverage scores for approved events:")
        print(f"  Worker Impact: {updated_stats['avg_approved_scores']['worker_impact']}/10")
        print(f"  Timeliness: {updated_stats['avg_approved_scores']['timeliness']}/10")
        print(f"  Verifiability: {updated_stats['avg_approved_scores']['verifiability']}/10")
        print(f"  Regional Relevance: {updated_stats['avg_approved_scores']['regional_relevance']}/10")
        print(f"  Final Score: {updated_stats['avg_approved_scores']['final_newsworthiness']}/100")

    session.close()


if __name__ == '__main__':
    main()
