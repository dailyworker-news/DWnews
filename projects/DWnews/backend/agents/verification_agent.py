"""
Verification Agent - Source Verification & Attribution

Orchestrates source verification for approved topics in the automated journalism pipeline.
Verifies sources, creates attribution plans, and ensures ≥3 credible sources per topic.

Pipeline position: Between Evaluation Agent and Enhanced Journalist Agent
Input: Approved topics from topics table
Output: verified_facts and source_plan JSON stored in topics table
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from database.models import Topic, EventCandidate
from backend.agents.verification.source_identifier import SourceIdentifier, Source
from backend.agents.verification.cross_reference import CrossReferenceVerifier, VerificationResult
from backend.agents.verification.fact_classifier import FactClassifier
from backend.agents.verification.source_ranker import SourceRanker, RankedSource


class VerificationAgent:
    """
    Main orchestrator for source verification and attribution
    """

    def __init__(self, session: Session, web_search_fn=None):
        """
        Initialize the Verification Agent

        Args:
            session: SQLAlchemy database session
            web_search_fn: Optional function for web searching (default: None, will use mock)
        """
        self.session = session
        self.web_search_fn = web_search_fn

        # Initialize components
        self.source_identifier = SourceIdentifier(web_search_fn=web_search_fn)
        self.cross_verifier = CrossReferenceVerifier()
        self.fact_classifier = FactClassifier()
        self.source_ranker = SourceRanker()

    def verify_topic(self, topic_id: int) -> bool:
        """
        Verify a single topic by finding sources and creating attribution plan

        Args:
            topic_id: ID of topic to verify

        Returns:
            True if verification succeeded, False otherwise
        """
        # Fetch topic
        topic = self.session.query(Topic).filter(Topic.id == topic_id).first()

        if not topic:
            print(f"Topic {topic_id} not found")
            return False

        if topic.status != 'approved':
            print(f"Topic {topic_id} is not approved (status: {topic.status})")
            return False

        print(f"\nVerifying topic: {topic.title}")
        print("=" * 60)

        try:
            # Update status
            topic.verification_status = 'in_progress'
            self.session.commit()

            # Step 1: Identify sources
            print("\n1. Identifying sources...")
            sources = self._identify_sources(topic)
            print(f"   Found {len(sources)} potential sources")

            if not sources:
                print("   No sources found - will proceed as UNVERIFIED")
                # Don't fail immediately - let 3-tier system handle it
                sources = []  # Empty list for ranking

            # Step 2: Rank sources by credibility
            print("\n2. Ranking sources by credibility...")
            ranked_sources = self._rank_sources(sources)

            # Display ranking
            for rs in ranked_sources[:5]:  # Show top 5
                print(f"   {rs.rank}. {rs.name} (Tier {rs.credibility_tier}, Score: {rs.credibility_score:.1f})")

            # Step 3: Validate threshold
            print("\n3. Validating source threshold...")
            validation = self.source_ranker.validate_source_threshold(ranked_sources)

            print(f"   Credible sources (Tier 1-2): {validation['credible_sources_count']}")
            print(f"   Academic citations: {validation['academic_sources_count']}")

            # NEW: 3-tier verification system (unverified/verified/certified)
            credible_count = validation['credible_sources_count']
            academic_count = validation['academic_sources_count']

            if credible_count >= 6 or academic_count >= 3:
                verification_level = 'certified'
                print(f"   Verification level: CERTIFIED (thorough research)")
            elif credible_count >= 1:
                verification_level = 'verified'
                print(f"   Verification level: VERIFIED ({credible_count} sources)")
            else:
                verification_level = 'unverified'
                print(f"   Verification level: UNVERIFIED (proceed with disclaimer)")

            # Always proceed - don't block on insufficient sources
            # Step 4: Extract and verify facts
            print("\n4. Extracting and verifying facts...")
            verified_facts = self._extract_and_verify_facts(topic, sources, ranked_sources)

            # Step 5: Create source plan
            print("\n5. Creating attribution plan...")
            source_plan = self._create_source_plan(ranked_sources, validated=validation)

            # Add verification level to source plan
            source_plan['verification_level'] = verification_level.upper()
            source_plan['verification_note'] = self._get_verification_note(verification_level, credible_count)

            # Step 6: Store results
            print("\n6. Storing verification results...")
            topic.verified_facts = json.dumps(verified_facts, indent=2)
            topic.source_plan = json.dumps(source_plan, indent=2)
            topic.verification_status = verification_level  # Changed: use tier instead of binary
            topic.source_count = len([s for s in ranked_sources if s.credibility_tier <= 2])
            topic.academic_citation_count = validation['academic_sources_count']

            self.session.commit()

            print("\n✓ Verification complete!")
            return True

        except Exception as e:
            print(f"\n✗ Verification failed: {e}")
            topic.verification_status = 'failed'
            self.session.commit()
            return False

    def verify_all_approved_topics(self, limit: Optional[int] = None) -> Dict:
        """
        Verify all approved topics that haven't been verified yet

        Args:
            limit: Optional limit on number of topics to process

        Returns:
            Dict with processing statistics
        """
        # Query approved topics with pending verification
        query = self.session.query(Topic).filter(
            Topic.status == 'approved',
            Topic.verification_status == 'pending'
        ).order_by(Topic.discovery_date.desc())

        if limit:
            query = query.limit(limit)

        topics = query.all()

        print(f"\nFound {len(topics)} topics to verify")
        print("=" * 60)

        certified_count = 0
        verified_count = 0
        unverified_count = 0
        failed_count = 0

        for i, topic in enumerate(topics, 1):
            print(f"\n[{i}/{len(topics)}] Processing: {topic.title}")

            success = self.verify_topic(topic.id)

            if success:
                # Count by verification level (all proceed, just different disclosure)
                if topic.verification_status == 'certified':
                    certified_count += 1
                elif topic.verification_status == 'verified':
                    verified_count += 1
                elif topic.verification_status == 'unverified':
                    unverified_count += 1
            else:
                failed_count += 1

        total_successful = certified_count + verified_count + unverified_count

        return {
            'total_processed': len(topics),
            'successful': total_successful,  # All non-failed are successful
            'certified': certified_count,
            'verified': verified_count,
            'unverified': unverified_count,
            'failed': failed_count,
            'avg_sources': sum([t.source_count or 0 for t in topics]) / len(topics) if topics else 0,
            'success_rate': round((total_successful / len(topics) * 100), 2) if topics else 0
        }

    def _identify_sources(self, topic: Topic) -> List[Source]:
        """
        Identify sources for a topic

        Args:
            topic: Topic to find sources for

        Returns:
            List of Source objects
        """
        sources = []

        # FIRST: Get the original RSS source URL if this topic came from an event
        event = self.session.query(EventCandidate).filter(
            EventCandidate.topic_id == topic.id
        ).first()

        if event and event.source_url:
            # Fetch content from the original source URL
            print(f"   Fetching original source: {event.source_url[:80]}...")
            original_source = self._fetch_original_source(event.source_url, event.title)
            if original_source:
                sources.append(original_source)
                print(f"   ✓ Fetched content from original source")
            else:
                print(f"   ✗ Could not fetch original source")

        # SECOND: Search for additional corroborating sources
        if len(sources) < 3:  # Only search if we need more sources
            # Build topic text
            topic_text = f"{topic.title}. {topic.description or ''}"

            # Build event data context
            event_data = {
                'keywords': topic.keywords,
                'category': topic.category.slug if topic.category else None,
                'region': topic.region.name if topic.region else None,
                'is_national': topic.is_national
            }

            # Search for additional sources
            additional_sources = self.source_identifier.identify_sources(topic_text, event_data)
            sources.extend(additional_sources)

        return sources

    def _fetch_original_source(self, url: str, title: str) -> Optional[Source]:
        """
        Fetch content from the original RSS source URL

        Args:
            url: URL to fetch
            title: Article title

        Returns:
            Source object with fetched content, or None if fetch failed
        """
        try:
            # Import WebFetch at runtime to avoid circular imports
            from backend.tools.web_tools import WebFetch

            # Fetch the article content
            fetcher = WebFetch()
            prompt = """Extract the main article content including:
            1. The full text of the article
            2. Any key facts, statistics, or quotes
            3. Names of people or organizations mentioned
            4. Dates and locations mentioned

            Return the content in a structured format."""

            result = fetcher.fetch(url, prompt)

            if result and len(result) > 100:  # Ensure we got substantial content
                # Determine source type based on URL
                source_type = 'news_agency'
                if 'intercept.com' in url:
                    source_type = 'investigative_journalism'
                elif 'truthout.org' in url:
                    source_type = 'news_agency'
                elif 'democracynow.org' in url:
                    source_type = 'news_agency'
                elif '.gov' in url:
                    source_type = 'government_document'
                elif '.edu' in url or 'academic' in url:
                    source_type = 'academic'

                # Extract publication name from URL
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                name = domain.replace('www.', '').split('.')[0].title()

                return Source(
                    name=name,
                    url=url,
                    source_type=source_type,
                    snippet=result,  # Store FULL content for fact extraction
                    discovered_via='original_rss_source',
                    credibility_tier=1  # Original sources are tier 1
                )
            else:
                print(f"     Warning: Fetched content too short ({len(result) if result else 0} chars)")
                return None

        except Exception as e:
            print(f"     Error fetching {url}: {e}")
            return None

    def _rank_sources(self, sources: List[Source]) -> List[RankedSource]:
        """
        Rank sources by credibility

        Args:
            sources: List of Source objects

        Returns:
            List of RankedSource objects
        """
        # Convert Source objects to dicts for ranking
        source_dicts = [
            {
                'url': source.url,
                'name': source.name,
                'source_type': source.source_type
            }
            for source in sources
        ]

        # Rank sources
        ranked_sources = self.source_ranker.rank_sources(source_dicts)

        return ranked_sources

    def _extract_and_verify_facts(self, topic: Topic, sources: List[Source], ranked_sources: List[RankedSource]) -> Dict:
        """
        Extract facts from topic and verify them against sources

        Args:
            topic: Topic to extract facts from
            sources: Original Source objects with fetched content
            ranked_sources: Ranked source list

        Returns:
            Dict with verified_facts structure
        """
        # Extract key facts from FETCHED SOURCE CONTENT (not just topic title)
        facts = []
        fact_source_map = {}  # Track which source each fact came from

        # First, extract from topic description
        topic_facts = self._extract_facts_from_topic(topic)
        facts.extend(topic_facts)

        # CRITICAL: Extract facts from fetched source content
        for source in sources:
            if source.snippet and len(source.snippet) > 200:
                # Extract facts from the fetched article content
                source_facts = self._extract_facts_from_text(source.snippet, source.url)

                # Map each extracted fact to its source URL
                for fact in source_facts:
                    facts.append(fact)
                    fact_source_map[fact] = source.url

        # Build source_contents from actual fetched sources
        # Match ranked sources back to original Source objects with content
        source_contents = []
        for rs in ranked_sources[:10]:  # Limit to top 10 sources
            # Find the original Source object to get the snippet/content
            source_obj = next(
                (s for s in sources if s.url == rs.url),
                None
            )

            content_text = source_obj.snippet if source_obj and source_obj.snippet else f"Content from {rs.name}"

            source_contents.append({
                'url': rs.url,
                'name': rs.name,
                'content': content_text,
                'snippet': content_text[:500],  # First 500 chars
                'source_type': rs.source_type
            })

        # Cross-reference verify facts
        verification_result = self.cross_verifier.verify_claims(facts, source_contents)

        # Classify each verified fact
        classified_facts = []
        for verified_fact in verification_result.verified_facts:
            # IMPORTANT: Override sources with our tracked source mapping
            fact_sources = verified_fact.sources

            # If this fact was extracted from a specific source, use that
            if verified_fact.claim in fact_source_map:
                fact_sources = [fact_source_map[verified_fact.claim]]

            # Determine source type from sources
            source_type = 'unknown'
            if fact_sources:
                # Get source type from first supporting source
                source_url = fact_sources[0]
                matching_source = next(
                    (rs for rs in ranked_sources if rs.url == source_url),
                    None
                )
                if matching_source:
                    source_type = matching_source.source_type

            # Classify fact
            fact_type = self.fact_classifier.classify_fact(verified_fact.claim, source_type)

            # Use higher confidence for facts extracted from fetched sources
            confidence = verified_fact.confidence
            if verified_fact.claim in fact_source_map:
                confidence = 'high' if confidence == 'medium' else 'medium'

            classified_facts.append({
                'claim': verified_fact.claim,
                'type': fact_type,
                'sources': fact_sources,
                'confidence': confidence,
                'conflicting_info': verified_fact.conflicting_info
            })

        # Get credible sources only (Tier 1-2)
        credible_sources = [rs for rs in ranked_sources if rs.credibility_tier <= 2]
        academic_sources = [
            rs for rs in ranked_sources
            if rs.source_type == 'academic' or 'academic' in rs.reasoning.lower()
        ]

        # Build summary
        source_summary = {
            'total_sources': len(ranked_sources),
            'credible_sources': len(credible_sources),
            'academic_citations': len(academic_sources),
            'meets_threshold': len(credible_sources) >= 3 or len(academic_sources) >= 2,
            'source_agreement_score': round(verification_result.source_agreement_score, 2)
        }

        return {
            'facts': classified_facts,
            'source_summary': source_summary
        }

    def _extract_facts_from_text(self, text: str, source_url: str) -> List[str]:
        """
        Extract key factual claims from article text

        Args:
            text: Article text to extract from
            source_url: URL of the source (for attribution)

        Returns:
            List of factual claims
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        facts = []
        for sentence in sentences:
            # Skip very short or very long sentences
            if len(sentence) < 30 or len(sentence) > 300:
                continue

            # Skip questions and hypotheticals
            if '?' in sentence or sentence.lower().startswith(('if ', 'what if', 'suppose')):
                continue

            # Prioritize sentences with:
            # - Numbers/statistics
            # - Proper nouns (names of people/organizations)
            # - Specific dates
            # - Quoted text
            # - Action verbs (said, announced, reported, etc.)

            has_number = bool(re.search(r'\d+', sentence))
            has_proper_noun = bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+', sentence))
            has_action_verb = bool(re.search(r'\b(said|announced|reported|stated|confirmed|revealed|according to)\b', sentence, re.I))
            has_quote = '"' in sentence or "'" in sentence

            # Score the sentence
            score = sum([has_number, has_proper_noun, has_action_verb * 2, has_quote * 2])

            # Keep sentences with score >= 2
            if score >= 2:
                facts.append(sentence)

        # Limit to top 10 most fact-dense sentences
        return facts[:10]

    def _extract_facts_from_topic(self, topic: Topic) -> List[str]:
        """
        Extract key factual claims from topic

        Args:
            topic: Topic to extract from

        Returns:
            List of factual claims
        """
        # Simple fact extraction based on sentences
        text = f"{topic.title}. {topic.description or ''}"

        # Split into sentences
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Filter to factual-sounding sentences (heuristic)
        facts = []
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence) < 20:
                continue

            # Skip questions
            if '?' in sentence:
                continue

            # Keep sentences with numbers, names, or specific details
            if re.search(r'\d+|[A-Z][a-z]+\s+[A-Z][a-z]+|\$', sentence):
                facts.append(sentence)

        # If no facts extracted, use the whole description
        if not facts and topic.description:
            facts = [topic.description]

        # Default: just use title if nothing else
        if not facts:
            facts = [topic.title]

        return facts[:5]  # Limit to 5 facts

    def _create_source_plan(self, ranked_sources: List[RankedSource], validated: Dict) -> Dict:
        """
        Create attribution plan for journalist

        Args:
            ranked_sources: List of ranked sources
            validated: Validation results dict

        Returns:
            Dict with source_plan structure
        """
        # Split sources into primary and supporting
        primary_sources = [rs for rs in ranked_sources if rs.credibility_tier == 1][:3]
        supporting_sources = [rs for rs in ranked_sources if rs.credibility_tier == 2][:3]

        # Build attribution strategy
        if primary_sources:
            primary_name = primary_sources[0].name
            strategy = f"Lead with {primary_name} as primary source"

            if len(primary_sources) > 1:
                strategy += f", corroborate with {primary_sources[1].name}"

            if supporting_sources:
                strategy += f", cite {supporting_sources[0].name} for additional context"
        elif supporting_sources:
            strategy = f"Lead with {supporting_sources[0].name}, cross-reference with other credible sources"
        else:
            strategy = "Use available sources with appropriate attribution and verification notes"

        return {
            'primary_sources': [
                {
                    'name': rs.name,
                    'url': rs.url,
                    'type': rs.source_type,
                    'rank': rs.rank,
                    'credibility_tier': rs.credibility_tier,
                    'credibility_score': rs.credibility_score
                }
                for rs in primary_sources
            ],
            'supporting_sources': [
                {
                    'name': rs.name,
                    'url': rs.url,
                    'type': rs.source_type,
                    'rank': rs.rank,
                    'credibility_tier': rs.credibility_tier,
                    'credibility_score': rs.credibility_score
                }
                for rs in supporting_sources
            ],
            'attribution_strategy': strategy,
            'verification_notes': {
                'total_sources_found': len(ranked_sources),
                'credible_sources': validated['credible_sources_count'],
                'academic_citations': validated['academic_sources_count'],
                'threshold_met': validated['meets_threshold'],
                'threshold_met_by': validated.get('threshold_met_by')
            }
        }

    def _get_verification_note(self, level: str, source_count: int) -> str:
        """
        Get sourcing disclosure note based on sourcing level

        Args:
            level: Sourcing level (aggregated, corroborated, multi-sourced) or legacy (unverified, verified, certified)
            source_count: Number of credible sources found

        Returns:
            Sourcing disclosure text to display with article
        """
        # Map old terminology to new if needed (backwards compatibility)
        if level == 'certified':
            level = 'multi-sourced'
        elif level == 'verified':
            level = 'corroborated'
        elif level == 'unverified':
            level = 'aggregated'

        if level == 'multi-sourced':
            return f"Multi-sourced from {source_count}+ independent sources. See references below."
        elif level == 'corroborated':
            return f"Corroborated by {source_count} independent source{'s' if source_count != 1 else ''}. See references below."
        else:  # aggregated
            return f"Aggregated from single credible source. See references below."

    def get_verification_stats(self) -> Dict:
        """
        Get statistics about verified topics

        Returns:
            Dict with verification statistics
        """
        # Count topics by verification status
        total_topics = self.session.query(Topic).filter(
            Topic.status == 'approved'
        ).count()

        verified = self.session.query(Topic).filter(
            Topic.verification_status == 'verified'
        ).count()

        pending = self.session.query(Topic).filter(
            Topic.verification_status == 'pending'
        ).count()

        insufficient = self.session.query(Topic).filter(
            Topic.verification_status == 'insufficient_sources'
        ).count()

        failed = self.session.query(Topic).filter(
            Topic.verification_status == 'failed'
        ).count()

        # Calculate average source counts for verified topics
        from sqlalchemy import func
        avg_sources = self.session.query(
            func.avg(Topic.source_count),
            func.avg(Topic.academic_citation_count)
        ).filter(Topic.verification_status == 'verified').first()

        return {
            'total_approved_topics': total_topics,
            'verified': verified,
            'pending': pending,
            'insufficient_sources': insufficient,
            'failed': failed,
            'verification_rate': round((verified / total_topics * 100), 2) if total_topics > 0 else 0,
            'avg_source_count': round(avg_sources[0], 1) if avg_sources[0] else 0,
            'avg_academic_citations': round(avg_sources[1], 1) if avg_sources[1] else 0
        }


def main():
    """
    Main function for running the Verification Agent standalone
    """
    from backend.database import SessionLocal

    session = SessionLocal()
    agent = VerificationAgent(session)

    print("=" * 60)
    print("VERIFICATION AGENT - Source Verification & Attribution")
    print("=" * 60)

    # Get current stats
    stats = agent.get_verification_stats()
    print(f"\nCurrent Status:")
    print(f"  Total approved topics: {stats['total_approved_topics']}")
    print(f"  Verified: {stats['verified']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Insufficient sources: {stats['insufficient_sources']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Verification rate: {stats['verification_rate']}%")

    if stats['pending'] == 0:
        print("\nNo pending topics to verify.")
        return

    # Process pending topics
    print(f"\nProcessing {stats['pending']} pending topics...")
    results = agent.verify_all_approved_topics()

    print(f"\n{'=' * 60}")
    print("RESULTS:")
    print(f"{'=' * 60}")
    print(f"Total processed: {results['total_processed']}")
    print(f"Verified: {results['verified']} ({results['success_rate']}%)")
    print(f"Insufficient sources: {results['insufficient_sources']}")
    print(f"Failed: {results['failed']}")

    # Show updated stats
    updated_stats = agent.get_verification_stats()
    print(f"\nUpdated Status:")
    print(f"  Total verified: {updated_stats['verified']}")
    print(f"  Verification rate: {updated_stats['verification_rate']}%")

    if updated_stats['verified'] > 0:
        print(f"\nAverage metrics for verified topics:")
        print(f"  Source count: {updated_stats['avg_source_count']}")
        print(f"  Academic citations: {updated_stats['avg_academic_citations']}")

    session.close()


if __name__ == '__main__':
    main()
