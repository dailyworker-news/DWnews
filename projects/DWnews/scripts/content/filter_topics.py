#!/usr/bin/env python3
"""
The Daily Worker - Topic Viability Filtering
Filters discovered topics for factual credibility and worker relevance
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from database.models import Topic, Source, Category
from scripts.utils.text_utils import contains_keywords
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)


class TopicFilter:
    """Topic viability filtering service"""

    def __init__(self, session):
        self.session = session

        # Worker-relevance keywords
        self.worker_keywords = [
            'worker', 'workers', 'labor', 'union', 'wage', 'wages', 'salary',
            'employment', 'job', 'jobs', 'workplace', 'employee', 'staff',
            'working class', 'blue collar', 'service worker', 'gig economy',
            'minimum wage', 'living wage', 'overtime', 'benefits', 'pension',
            'healthcare', 'insurance', 'retirement', 'strike', 'protest',
            'layoff', 'layoffs', 'unemployment', 'cost of living', 'inflation',
            'rent', 'housing', 'eviction', 'student debt', 'bankruptcy',
            'inequality', 'poverty', 'economic justice', 'exploitation'
        ]

        # High-priority impact keywords
        self.high_impact_keywords = [
            'strike', 'union victory', 'labor law', 'minimum wage increase',
            'mass layoff', 'plant closing', 'corporate greed', 'price gouging',
            'union organizing', 'collective bargaining', 'work reform'
        ]

    def check_source_credibility(self, topic: Topic) -> Dict:
        """Check if topic has sufficient credible sources

        Returns dict with:
            - passed: bool
            - source_count: int
            - academic_count: int
            - score: float (0-1)
        """
        # For now, we'll do a simple check since we don't have multi-source verification yet
        # In production, this would check multiple independent sources

        # Parse discovered_from to count sources
        source_count = 1  # Default: discovered from one source

        # Check if topic keywords match high-credibility sources
        keywords_lower = (topic.keywords or "").lower()
        title_lower = topic.title.lower()
        full_text = f"{title_lower} {keywords_lower}"

        # Boost score for topics from investigative/academic sources
        is_investigative = any(term in (topic.discovered_from or "").lower()
                              for term in ['propublica', 'intercept', 'investigative'])

        is_academic = any(term in full_text
                         for term in ['study', 'research', 'university', 'professor', 'data shows'])

        # Calculate credibility score
        score = 0.5  # Base score

        if is_investigative:
            score += 0.3
        if is_academic:
            score += 0.2
            source_count += 1  # Academic sources count extra

        # High engagement suggests multiple sources are covering it
        if topic.engagement_score and topic.engagement_score > 5.0:
            score += 0.1
            source_count += 1

        passed = source_count >= settings.min_credible_sources or (is_academic and source_count >= 2)

        return {
            'passed': passed,
            'source_count': source_count,
            'academic_count': 1 if is_academic else 0,
            'score': min(score, 1.0),
            'reason': 'Sufficient sources' if passed else 'Insufficient sources for verification'
        }

    def check_worker_relevance(self, topic: Topic) -> Dict:
        """Check if topic is relevant to working-class Americans

        Returns dict with:
            - passed: bool
            - score: float (0-1)
            - matched_keywords: List[str]
        """
        full_text = f"{topic.title} {topic.description or ''} {topic.keywords or ''}".lower()

        # Check for worker-related keywords
        matched_keywords = [kw for kw in self.worker_keywords if kw in full_text]

        # Check for high-impact keywords (worth more)
        high_impact_matches = [kw for kw in self.high_impact_keywords if kw in full_text]

        # Calculate relevance score
        base_score = len(matched_keywords) * 0.1
        impact_bonus = len(high_impact_matches) * 0.2

        score = min(base_score + impact_bonus, 1.0)

        # Pass if score >= 0.3 (at least 3 worker keywords or 1-2 high-impact)
        passed = score >= 0.3

        return {
            'passed': passed,
            'score': score,
            'matched_keywords': matched_keywords[:5],  # Top 5
            'reason': 'Relevant to workers' if passed else 'Low worker relevance'
        }

    def check_engagement_potential(self, topic: Topic) -> Dict:
        """Check if topic has potential for social engagement

        Returns dict with:
            - passed: bool
            - score: float (0-1)
        """
        score = 0.0

        # Engagement score from social media
        if topic.engagement_score:
            score = min(topic.engagement_score / 10.0, 0.5)

        # Recency bonus (fresher topics score higher)
        if topic.discovery_date:
            hours_old = (datetime.utcnow() - topic.discovery_date).total_seconds() / 3600
            if hours_old < 24:
                score += 0.3
            elif hours_old < 72:
                score += 0.2
            else:
                score += 0.1

        # Topic type bonuses
        title_lower = topic.title.lower()
        if any(term in title_lower for term in ['breaking', 'major', 'historic', 'victory']):
            score += 0.2

        score = min(score, 1.0)
        passed = score >= 0.3

        return {
            'passed': passed,
            'score': score,
            'reason': 'Good engagement potential' if passed else 'Low engagement potential'
        }

    def filter_topic(self, topic: Topic, verbose: bool = False) -> bool:
        """Filter a single topic through all checks

        Returns True if topic passes all filters
        """
        if verbose:
            print(f"\nFiltering: {topic.title[:60]}...")

        # Run all checks
        credibility = self.check_source_credibility(topic)
        relevance = self.check_worker_relevance(topic)
        engagement = self.check_engagement_potential(topic)

        # Calculate overall score (weighted average)
        overall_score = (
            credibility['score'] * 0.4 +
            relevance['score'] * 0.4 +
            engagement['score'] * 0.2
        )

        # Topic passes if:
        # 1. Credibility check passes AND
        # 2. Worker relevance check passes AND
        # 3. Overall score >= 0.5
        passed = (
            credibility['passed'] and
            relevance['passed'] and
            overall_score >= 0.4
        )

        # Update topic
        topic.source_count = credibility['source_count']
        topic.academic_citation_count = credibility['academic_count']
        topic.worker_relevance_score = relevance['score']
        topic.engagement_score = engagement['score']

        if passed:
            topic.status = 'filtered'
            if verbose:
                print(f"  ✓ PASSED (score: {overall_score:.2f})")
        else:
            topic.status = 'rejected'
            # Determine rejection reason
            reasons = []
            if not credibility['passed']:
                reasons.append(credibility['reason'])
            if not relevance['passed']:
                reasons.append(relevance['reason'])
            if overall_score < 0.4:
                reasons.append(f"Low overall score ({overall_score:.2f})")

            topic.rejection_reason = '; '.join(reasons)

            if verbose:
                print(f"  ✗ REJECTED: {topic.rejection_reason}")

        return passed

    def filter_all_discovered(self, verbose: bool = False) -> Dict:
        """Filter all discovered topics

        Returns dict with statistics
        """
        # Get all discovered topics
        topics = self.session.query(Topic).filter_by(status='discovered').all()

        if not topics:
            logger.warning("No discovered topics to filter")
            return {'total': 0, 'passed': 0, 'rejected': 0}

        passed_count = 0
        rejected_count = 0

        for topic in topics:
            if self.filter_topic(topic, verbose=verbose):
                passed_count += 1
            else:
                rejected_count += 1

        # Commit changes
        try:
            self.session.commit()
            logger.info(f"Filtered {len(topics)} topics: {passed_count} passed, {rejected_count} rejected")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error committing filter results: {e}")
            raise

        return {
            'total': len(topics),
            'passed': passed_count,
            'rejected': rejected_count
        }


def run_filtering(verbose: bool = True) -> Dict:
    """Run topic filtering"""
    print("=" * 60)
    print("The Daily Worker - Topic Viability Filtering")
    print("=" * 60)

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Initialize filter
        topic_filter = TopicFilter(session)

        # Run filtering
        print(f"\nFiltering discovered topics...")
        results = topic_filter.filter_all_discovered(verbose=verbose)

        if results['total'] == 0:
            print("\nNo topics to filter. Run discover_topics.py first.")
            return results

        # Show results
        print("\n" + "=" * 60)
        print("FILTERING COMPLETE")
        print("=" * 60)
        print(f"Total topics: {results['total']}")
        print(f"✓ Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
        print(f"✗ Rejected: {results['rejected']} ({results['rejected']/results['total']*100:.1f}%)")

        # Show category breakdown of passed topics
        print("\nPassed topics by category:")
        categories = session.query(Category).all()
        for category in categories:
            count = session.query(Topic).filter_by(
                category_id=category.id,
                status='filtered'
            ).count()
            if count > 0:
                print(f"  - {category.name}: {count}")

        # Show top rejected reasons
        print("\nTop rejection reasons:")
        rejected_topics = session.query(Topic).filter_by(status='rejected').all()
        rejection_reasons = {}
        for topic in rejected_topics:
            if topic.rejection_reason:
                reason = topic.rejection_reason.split(';')[0].strip()  # First reason
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1

        for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {reason}: {count}")

        return results

    except Exception as e:
        logger.error(f"Filtering failed: {e}")
        print(f"\n✗ Error: {e}")
        return {'total': 0, 'passed': 0, 'rejected': 0}
    finally:
        session.close()


if __name__ == "__main__":
    results = run_filtering(verbose=True)

    if results['passed'] > 0:
        print(f"\n✓ {results['passed']} topics ready for article generation")
        print("\nNext step: python scripts/content/generate_articles.py")
    else:
        print("\n⚠ No topics passed filtering. Try:")
        print("  1. Adjusting filter criteria in filter_topics.py")
        print("  2. Running discover_topics.py to get more topics")
