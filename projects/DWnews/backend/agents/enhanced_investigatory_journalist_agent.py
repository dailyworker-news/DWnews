"""
Enhanced Investigatory Journalist Agent - Phases 1-4 Complete

Combines all investigation capabilities:
- Phase 1: Multi-engine search, origin tracing, cross-reference validation
- Phase 2: Social media investigation (Twitter/Reddit with credibility scoring)
- Phase 3: Deep context research (historical precedents, actor profiling, geographic context)
- Phase 4: Advanced analysis (claim extraction, fact-checking, contradiction detection, bias analysis)

This is the complete investigatory journalism agent ready for production use.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import Topic

# Import Phase 1 (core investigation)
from backend.agents.investigatory_journalist_agent import (
    InvestigatoryJournalistAgent,
    InvestigationResult,
    SearchResult,
    Source
)

# Import Phase 2 (social media)
from backend.agents.investigation.social_media_investigator import (
    SocialMediaInvestigator,
    SocialSource,
    SocialTimeline
)

# Import Phase 3 (deep context)
from backend.agents.investigation.deep_context_researcher import (
    DeepContextResearcher,
    ContextResearch,
    HistoricalEvent,
    ActorProfile,
    GeographicContext
)

# Import Phase 4 (advanced analysis)
from backend.agents.investigation.advanced_analyzer import (
    AdvancedAnalyzer,
    AdvancedAnalysisResult,
    Claim,
    Contradiction,
    BiasAnalysis
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancedInvestigationResult:
    """
    Complete investigation result incorporating all phases.

    This combines results from:
    - Phase 1: Core investigation
    - Phase 2: Social media investigation
    - Phase 3: Deep context research
    - Phase 4: Advanced analysis
    """

    topic_id: int
    investigation_date: datetime

    # Phase 1: Core investigation
    core_investigation: Optional[InvestigationResult] = None

    # Phase 2: Social media
    social_sources: List[SocialSource] = None
    social_timeline: Optional[SocialTimeline] = None

    # Phase 3: Deep context
    context_research: Optional[ContextResearch] = None

    # Phase 4: Advanced analysis
    advanced_analysis: Optional[AdvancedAnalysisResult] = None

    # Overall assessment
    final_verification_level: str = 'unverified'  # unverified/verified/certified
    final_confidence: float = 0.0  # 0-100
    recommendation_rationale: str = ""

    # Aggregate metrics
    total_sources_found: int = 0
    credible_sources_count: int = 0
    verified_claims_count: int = 0

    # Flags
    requires_human_review: bool = False
    review_reasons: List[str] = None

    # Summary
    investigation_summary: str = ""

    def __post_init__(self):
        """Initialize default values."""
        if self.social_sources is None:
            self.social_sources = []
        if self.review_reasons is None:
            self.review_reasons = []


class EnhancedInvestigatoryJournalistAgent:
    """
    Complete investigatory journalism agent with all 4 phases.

    Workflow:
    1. Phase 1: Core multi-engine search and origin tracing
    2. Phase 2: Social media deep investigation (Twitter/Reddit)
    3. Phase 3: Historical and geographic context research
    4. Phase 4: Advanced claim analysis and fact-checking
    5. Synthesize all findings into final recommendation
    """

    def __init__(
        self,
        db_session: Session,
        use_mock_data: bool = False,
        twitter_bearer_token: Optional[str] = None,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None
    ):
        """
        Initialize enhanced investigatory journalist agent.

        Args:
            db_session: SQLAlchemy database session
            use_mock_data: If True, use mock data for testing
            twitter_bearer_token: Twitter API token (optional)
            reddit_client_id: Reddit API client ID (optional)
            reddit_client_secret: Reddit API client secret (optional)
        """
        self.db = db_session
        self.use_mock_data = use_mock_data

        # Initialize all phase agents
        self.core_investigator = InvestigatoryJournalistAgent(db_session)

        self.social_investigator = SocialMediaInvestigator(
            twitter_bearer_token=twitter_bearer_token,
            reddit_client_id=reddit_client_id,
            reddit_client_secret=reddit_client_secret,
            use_mock_data=use_mock_data
        )

        self.context_researcher = DeepContextResearcher(
            use_mock_data=use_mock_data
        )

        self.advanced_analyzer = AdvancedAnalyzer(
            use_mock_data=use_mock_data
        )

    def investigate(self, topic_id: int) -> Optional[EnhancedInvestigationResult]:
        """
        Conduct complete 4-phase investigation on a topic.

        Args:
            topic_id: ID of topic to investigate

        Returns:
            EnhancedInvestigationResult if successful, None if failed
        """
        logger.info(f"Starting enhanced investigation for topic_id={topic_id}")
        logger.info("=" * 80)

        # Load topic
        topic = self.db.query(Topic).filter_by(id=topic_id).first()
        if not topic:
            logger.error(f"Topic {topic_id} not found")
            return None

        logger.info(f"Topic: {topic.title}")
        logger.info(f"Current status: {topic.verification_status}")

        # Extract keywords from topic
        keywords = self._extract_keywords(topic)
        location = self._extract_location(topic)
        actors = self._extract_actors(topic)

        # Phase 1: Core Investigation
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: CORE INVESTIGATION (Multi-engine search, origin tracing)")
        logger.info("=" * 80)

        core_result = self.core_investigator.investigate(topic_id)
        if not core_result:
            logger.warning("Phase 1 investigation returned no results")

        # Phase 2: Social Media Investigation
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: SOCIAL MEDIA INVESTIGATION (Twitter/Reddit deep search)")
        logger.info("=" * 80)

        social_sources, social_timeline = self.social_investigator.investigate_topic(
            topic_title=topic.title,
            topic_description=topic.description or "",
            keywords=keywords,
            max_results=50,
            days_back=30
        )

        logger.info(f"Found {len(social_sources)} social media sources")
        logger.info(f"Identified {len(social_timeline.eyewitness_accounts)} eyewitness accounts")

        # Phase 3: Deep Context Research
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: DEEP CONTEXT RESEARCH (Historical precedents, actor profiling)")
        logger.info("=" * 80)

        context_research = self.context_researcher.research_context(
            topic_title=topic.title,
            topic_description=topic.description or "",
            keywords=keywords,
            location=location,
            actors=actors
        )

        logger.info(f"Context richness: {context_research.context_richness_score:.1f}/100")
        logger.info(f"Found {len(context_research.historical_events)} historical precedents")
        logger.info(f"Profiled {len(context_research.actor_profiles)} key actors")

        # Phase 4: Advanced Analysis
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 4: ADVANCED ANALYSIS (Claim extraction, fact-checking, bias detection)")
        logger.info("=" * 80)

        # Combine all sources for analysis
        all_sources = self._combine_sources(core_result, social_sources, context_research)

        advanced_analysis = self.advanced_analyzer.analyze(
            topic_title=topic.title,
            topic_description=topic.description or "",
            sources=all_sources,
            investigation_findings={
                'core': asdict(core_result) if core_result else None,
                'social_timeline': asdict(social_timeline),
                'context': asdict(context_research)
            }
        )

        logger.info(f"Extracted {len(advanced_analysis.extracted_claims)} claims")
        logger.info(f"Verified {len(advanced_analysis.verified_claims)} claims")
        logger.info(f"Overall confidence: {advanced_analysis.overall_confidence:.1f}/100")

        # Synthesize final recommendation
        logger.info("\n" + "=" * 80)
        logger.info("FINAL SYNTHESIS")
        logger.info("=" * 80)

        final_level, final_confidence, rationale = self._synthesize_recommendation(
            core_result,
            social_timeline,
            context_research,
            advanced_analysis
        )

        logger.info(f"Final verification level: {final_level}")
        logger.info(f"Final confidence: {final_confidence:.1f}/100")
        logger.info(f"Rationale: {rationale}")

        # Determine if human review needed
        requires_review, review_reasons = self._evaluate_human_review(
            core_result,
            advanced_analysis,
            final_confidence
        )

        if requires_review:
            logger.warning(f"HUMAN REVIEW REQUIRED: {', '.join(review_reasons)}")

        # Calculate aggregate metrics
        total_sources = (
            (len(core_result.additional_sources) if core_result else 0) +
            len(social_sources) +
            len(context_research.local_sources)
        )

        credible_sources = (
            core_result.credible_sources_found if core_result else 0
        ) + len(social_timeline.verification_sources)

        # Build investigation summary
        summary = self._build_investigation_summary(
            core_result,
            social_sources,
            context_research,
            advanced_analysis,
            final_level,
            final_confidence
        )

        # Create enhanced result
        result = EnhancedInvestigationResult(
            topic_id=topic_id,
            investigation_date=datetime.utcnow(),
            core_investigation=core_result,
            social_sources=social_sources,
            social_timeline=social_timeline,
            context_research=context_research,
            advanced_analysis=advanced_analysis,
            final_verification_level=final_level,
            final_confidence=final_confidence,
            recommendation_rationale=rationale,
            total_sources_found=total_sources,
            credible_sources_count=credible_sources,
            verified_claims_count=len(advanced_analysis.verified_claims),
            requires_human_review=requires_review,
            review_reasons=review_reasons,
            investigation_summary=summary
        )

        logger.info("\n" + "=" * 80)
        logger.info("INVESTIGATION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total sources: {total_sources}")
        logger.info(f"Credible sources: {credible_sources}")
        logger.info(f"Verified claims: {len(advanced_analysis.verified_claims)}")
        logger.info(f"Recommendation: {final_level} ({final_confidence:.1f}% confidence)")

        return result

    def _extract_keywords(self, topic: Topic) -> List[str]:
        """Extract keywords from topic for searching."""
        keywords = []

        # From title
        keywords.extend(topic.title.split()[:5])

        # From description
        if topic.description:
            keywords.extend(topic.description.split()[:10])

        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [k for k in keywords if k.lower() not in stopwords and len(k) > 3]

        return list(set(keywords))[:10]

    def _extract_location(self, topic: Topic) -> Optional[str]:
        """Extract location from topic if mentioned."""
        # Simple heuristic: Look for city/state mentions in title or description
        text = (topic.title + " " + (topic.description or "")).lower()

        cities = ['new york', 'chicago', 'seattle', 'san francisco', 'los angeles', 'detroit', 'boston']
        for city in cities:
            if city in text:
                return city.title()

        return None

    def _extract_actors(self, topic: Topic) -> Optional[List[str]]:
        """Extract actor names (companies, unions) from topic."""
        text = (topic.title + " " + (topic.description or "")).lower()

        actors = []

        # Look for common company/union names
        known_entities = [
            'amazon', 'starbucks', 'walmart', 'target', 'tesla',
            'alu', 'uaw', 'teamsters', 'seiu', 'ufcw'
        ]

        for entity in known_entities:
            if entity in text:
                actors.append(entity.upper() if entity == 'alu' or entity == 'uaw' else entity.title())

        return actors if actors else None

    def _combine_sources(
        self,
        core_result: Optional[InvestigationResult],
        social_sources: List[SocialSource],
        context_research: ContextResearch
    ) -> List[Dict]:
        """Combine all sources into unified format for analysis."""
        combined = []

        # Add core investigation sources
        if core_result and core_result.additional_sources:
            for source in core_result.additional_sources:
                combined.append({
                    'name': source.name,
                    'url': source.url,
                    'source_type': source.source_type,
                    'snippet': '',
                    'content': ''
                })

        # Add social media sources
        for social_source in social_sources:
            combined.append({
                'name': social_source.author,
                'url': social_source.url,
                'source_type': social_source.platform,
                'snippet': social_source.content[:200],
                'content': social_source.content
            })

        # Add context research sources
        for historical_event in context_research.historical_events:
            combined.append({
                'name': f"Historical: {historical_event.title}",
                'url': historical_event.source_url,
                'source_type': 'historical',
                'snippet': historical_event.description[:200],
                'content': historical_event.description
            })

        return combined

    def _synthesize_recommendation(
        self,
        core_result: Optional[InvestigationResult],
        social_timeline: SocialTimeline,
        context_research: ContextResearch,
        advanced_analysis: AdvancedAnalysisResult
    ) -> Tuple[str, float, str]:
        """
        Synthesize final verification recommendation from all phases.

        Returns:
            Tuple of (verification_level, confidence, rationale)
        """
        # Start with Phase 4 recommendation as base
        base_level = advanced_analysis.verification_recommendation
        base_confidence = advanced_analysis.overall_confidence

        # Boost confidence based on other phases
        confidence_boost = 0.0

        # Social media boost
        if len(social_timeline.eyewitness_accounts) >= 2:
            confidence_boost += 5.0
        if len(social_timeline.verification_sources) >= 3:
            confidence_boost += 5.0

        # Context boost
        if context_research.context_richness_score >= 75:
            confidence_boost += 5.0
        if context_research.most_relevant_precedent:
            confidence_boost += 3.0

        # Core investigation boost
        if core_result and core_result.credible_sources_found >= 5:
            confidence_boost += 5.0

        final_confidence = min(base_confidence + confidence_boost, 100.0)

        # Re-evaluate level based on boosted confidence
        if final_confidence >= 80 and len(advanced_analysis.verified_claims) >= 5:
            final_level = 'certified'
        elif final_confidence >= 50 and len(advanced_analysis.verified_claims) >= 3:
            final_level = 'verified'
        else:
            final_level = 'unverified'

        # Build rationale
        rationale_parts = [
            advanced_analysis.recommendation_rationale,
            f"{len(social_timeline.eyewitness_accounts)} eyewitness accounts from social media",
            f"Context research: {context_research.context_richness_score:.0f}/100",
            f"Confidence boost from multi-phase investigation: +{confidence_boost:.0f} points"
        ]

        rationale = "; ".join(rationale_parts)

        return final_level, final_confidence, rationale

    def _evaluate_human_review(
        self,
        core_result: Optional[InvestigationResult],
        advanced_analysis: AdvancedAnalysisResult,
        final_confidence: float
    ) -> Tuple[bool, List[str]]:
        """Evaluate if human review is needed."""

        requires_review = False
        reasons = []

        # Check core investigation flags
        if core_result and core_result.requires_human_review:
            requires_review = True
            reasons.append(core_result.review_reason or "Core investigation flagged for review")

        # Check advanced analysis flags
        if advanced_analysis.requires_human_review:
            requires_review = True
            reasons.extend(advanced_analysis.review_reasons)

        # Low confidence requires review
        if final_confidence < 40:
            requires_review = True
            reasons.append("Low confidence score requires verification")

        return requires_review, reasons

    def _build_investigation_summary(
        self,
        core_result: Optional[InvestigationResult],
        social_sources: List[SocialSource],
        context_research: ContextResearch,
        advanced_analysis: AdvancedAnalysisResult,
        final_level: str,
        final_confidence: float
    ) -> str:
        """Build comprehensive investigation summary."""

        summary_parts = [
            f"Complete 4-phase investigation conducted.",
            f"\nPhase 1 (Core): {core_result.total_sources_found if core_result else 0} sources found",
            f"Phase 2 (Social): {len(social_sources)} social media sources analyzed",
            f"Phase 3 (Context): {len(context_research.historical_events)} historical precedents identified",
            f"Phase 4 (Analysis): {len(advanced_analysis.extracted_claims)} claims extracted, {len(advanced_analysis.verified_claims)} verified",
            f"\nFinal Assessment: {final_level.upper()} ({final_confidence:.1f}% confidence)",
            f"Bias assessment: {advanced_analysis.overall_bias_assessment}",
            f"Context richness: {context_research.context_richness_score:.0f}/100"
        ]

        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    from database.database import get_db
    logging.basicConfig(level=logging.INFO)

    # Create session
    db = next(get_db())

    # Initialize enhanced agent with mock data
    agent = EnhancedInvestigatoryJournalistAgent(
        db_session=db,
        use_mock_data=True
    )

    # Find an unverified topic to investigate
    topic = db.query(Topic).filter_by(verification_status='unverified').first()

    if topic:
        print(f"\nInvestigating topic: {topic.title}")
        print(f"Current status: {topic.verification_status}")

        result = agent.investigate(topic.id)

        if result:
            print(f"\n{'=' * 80}")
            print("INVESTIGATION COMPLETE")
            print(f"{'=' * 80}")
            print(result.investigation_summary)
            print(f"\nRecommendation: {result.final_verification_level}")
            print(f"Confidence: {result.final_confidence:.1f}/100")
            print(f"Rationale: {result.recommendation_rationale}")

            if result.requires_human_review:
                print(f"\n⚠ HUMAN REVIEW REQUIRED")
                for reason in result.review_reasons:
                    print(f"  - {reason}")
    else:
        print("No unverified topics found to test with")
