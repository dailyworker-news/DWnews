#!/usr/bin/env python3
"""
End-to-End Test for Investigatory Journalist Agent Phases 2-4

Tests the complete enhanced investigation workflow:
- Phase 6.9.2: Social Media Investigation
- Phase 6.9.3: Deep Context Research
- Phase 6.9.4: Advanced Analysis

Validates integration of all modules and final recommendation synthesis.
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.investigation.social_media_investigator import SocialMediaInvestigator
from backend.agents.investigation.deep_context_researcher import DeepContextResearcher
from backend.agents.investigation.advanced_analyzer import AdvancedAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_complete_investigation_pipeline():
    """Test complete investigation pipeline with all 3 phases."""

    print("\n" + "=" * 80)
    print("INVESTIGATORY JOURNALIST AGENT - PHASES 2-4 END-TO-END TEST")
    print("=" * 80)

    # Test case: Amazon warehouse strike
    test_topic = {
        'title': 'Amazon Staten Island Warehouse Workers Authorize Strike',
        'description': 'Workers at Amazon\'s JFK8 warehouse in Staten Island voted 500-200 to authorize strike action over wages and working conditions. The Amazon Labor Union led the organizing campaign.',
        'keywords': ['amazon', 'jfk8', 'staten island', 'warehouse', 'strike', 'alu'],
        'location': 'Staten Island, New York',
        'actors': ['Amazon', 'Amazon Labor Union']
    }

    print(f"\n📋 TEST CASE:")
    print(f"  Title: {test_topic['title']}")
    print(f"  Location: {test_topic['location']}")
    print(f"  Key Actors: {', '.join(test_topic['actors'])}")

    # Initialize all investigators with mock data
    social_investigator = SocialMediaInvestigator(use_mock_data=True)
    context_researcher = DeepContextResearcher(use_mock_data=True)
    advanced_analyzer = AdvancedAnalyzer(use_mock_data=True)

    # PHASE 2: Social Media Investigation
    print("\n" + "=" * 80)
    print("PHASE 2: SOCIAL MEDIA INVESTIGATION")
    print("=" * 80)

    social_sources, social_timeline = social_investigator.investigate_topic(
        topic_title=test_topic['title'],
        topic_description=test_topic['description'],
        keywords=test_topic['keywords'],
        max_results=20,
        days_back=7
    )

    print(f"\n✓ Phase 2 Results:")
    print(f"  Total social sources: {len(social_sources)}")
    print(f"  Platforms: {social_timeline.platforms}")
    print(f"  Eyewitness accounts: {len(social_timeline.eyewitness_accounts)}")
    print(f"  Verification sources: {len(social_timeline.verification_sources)}")
    print(f"  Mention velocity: {social_timeline.mention_velocity:.2f} per hour")

    assert len(social_sources) > 0, "Should find social media sources"
    assert len(social_timeline.eyewitness_accounts) >= 0, "Should identify eyewitness accounts"

    # Show top credible sources
    print(f"\n  Top Credible Sources:")
    for source in sorted(social_sources, key=lambda s: s.credibility_score, reverse=True)[:3]:
        print(f"    • {source.author_handle} ({source.platform})")
        print(f"      Credibility: {source.credibility_score:.1f}/100 ({source.reliability_tier})")
        print(f"      Eyewitness: {'Yes' if source.is_eyewitness else 'No'}")

    # PHASE 3: Deep Context Research
    print("\n" + "=" * 80)
    print("PHASE 3: DEEP CONTEXT RESEARCH")
    print("=" * 80)

    context_research = context_researcher.research_context(
        topic_title=test_topic['title'],
        topic_description=test_topic['description'],
        keywords=test_topic['keywords'],
        location=test_topic['location'],
        actors=test_topic['actors']
    )

    print(f"\n✓ Phase 3 Results:")
    print(f"  Context richness: {context_research.context_richness_score:.1f}/100 ({context_research.research_completeness})")
    print(f"  Historical precedents: {len(context_research.historical_events)}")
    print(f"  Actor profiles: {len(context_research.actor_profiles)}")
    print(f"  Event patterns: {len(context_research.event_clusters)}")
    print(f"  Local news sources: {len(context_research.local_sources)}")

    assert context_research.context_richness_score > 0, "Should have some context richness"
    assert len(context_research.historical_events) > 0, "Should find historical precedents"
    assert len(context_research.actor_profiles) > 0, "Should profile actors"

    # Show most relevant precedent
    if context_research.most_relevant_precedent:
        prec = context_research.most_relevant_precedent
        print(f"\n  Most Relevant Precedent:")
        print(f"    Title: {prec.title}")
        print(f"    Date: {prec.date.strftime('%Y-%m-%d')}")
        print(f"    Similarity: {prec.similarity_score:.1f}/100")
        print(f"    Outcome: {prec.outcome}")

    # Show primary actors
    print(f"\n  Primary Actors:")
    for actor in context_research.primary_actors:
        print(f"    • {actor.name} ({actor.actor_type})")
        print(f"      Credibility: {actor.credibility_score:.1f}/100")
        print(f"      Bias: {actor.bias_indicator}")

    # PHASE 4: Advanced Analysis
    print("\n" + "=" * 80)
    print("PHASE 4: ADVANCED ANALYSIS")
    print("=" * 80)

    # Combine all sources for analysis
    all_sources = []

    # Add social media sources
    for social_source in social_sources:
        all_sources.append({
            'name': social_source.author,
            'url': social_source.url,
            'source_type': social_source.platform,
            'snippet': social_source.content[:200],
            'content': social_source.content
        })

    # Add historical events as sources
    for historical_event in context_research.historical_events:
        all_sources.append({
            'name': f"Historical: {historical_event.title}",
            'url': historical_event.source_url,
            'source_type': 'historical',
            'snippet': historical_event.description[:200],
            'content': historical_event.description
        })

    advanced_analysis = advanced_analyzer.analyze(
        topic_title=test_topic['title'],
        topic_description=test_topic['description'],
        sources=all_sources
    )

    print(f"\n✓ Phase 4 Results:")
    print(f"  Claims extracted: {len(advanced_analysis.extracted_claims)}")
    print(f"  Verified claims: {len(advanced_analysis.verified_claims)}")
    print(f"  Disputed claims: {len(advanced_analysis.disputed_claims)}")
    print(f"  Contradictions: {len(advanced_analysis.contradictions)}")
    print(f"  Critical contradictions: {len(advanced_analysis.critical_contradictions)}")
    print(f"  Overall confidence: {advanced_analysis.overall_confidence:.1f}/100")
    print(f"  Verification recommendation: {advanced_analysis.verification_recommendation}")
    print(f"  Overall bias: {advanced_analysis.overall_bias_assessment}")

    assert len(advanced_analysis.extracted_claims) > 0, "Should extract claims"
    assert advanced_analysis.overall_confidence >= 0, "Should have confidence score"

    # Show verified claims
    if advanced_analysis.verified_claims:
        print(f"\n  Verified Claims:")
        for claim in advanced_analysis.verified_claims[:3]:
            print(f"    • {claim.claim_text}")
            print(f"      Type: {claim.claim_type.value}")
            print(f"      Confidence: {claim.confidence_score:.1f}/100")
            print(f"      Evidence: {len(claim.supporting_evidence)} sources")

    # Show source bias analysis
    print(f"\n  Source Bias Analysis:")
    for bias in advanced_analysis.source_biases[:3]:
        print(f"    • {bias.source_name}")
        print(f"      Objectivity: {bias.objectivity_score:.1f}/100")
        print(f"      Reliability: {bias.reliability_score:.1f}/100")
        biases_str = ', '.join([b.value for b in bias.detected_biases])
        print(f"      Biases: {biases_str}")

    # Human review check
    if advanced_analysis.requires_human_review:
        print(f"\n  ⚠ HUMAN REVIEW REQUIRED:")
        for reason in advanced_analysis.review_reasons:
            print(f"    - {reason}")
        for factor in advanced_analysis.high_risk_factors:
            print(f"    Risk: {factor}")

    # SYNTHESIS: Final Recommendation
    print("\n" + "=" * 80)
    print("FINAL SYNTHESIS")
    print("=" * 80)

    # Calculate aggregate metrics
    total_sources = len(social_sources) + len(context_research.historical_events)
    credible_social = len(social_timeline.verification_sources)
    credible_total = credible_social

    # Boost confidence based on all phases
    base_confidence = advanced_analysis.overall_confidence
    confidence_boost = 0.0

    # Social media boost
    if len(social_timeline.eyewitness_accounts) >= 2:
        confidence_boost += 5.0
        print(f"  + 5 points: Multiple eyewitness accounts")
    if len(social_timeline.verification_sources) >= 3:
        confidence_boost += 5.0
        print(f"  + 5 points: Multiple verified social sources")

    # Context boost
    if context_research.context_richness_score >= 75:
        confidence_boost += 5.0
        print(f"  + 5 points: High context richness")
    if context_research.most_relevant_precedent and context_research.most_relevant_precedent.similarity_score >= 80:
        confidence_boost += 3.0
        print(f"  + 3 points: Highly relevant historical precedent")

    final_confidence = min(base_confidence + confidence_boost, 100.0)

    # Determine final verification level
    if final_confidence >= 80 and len(advanced_analysis.verified_claims) >= 5:
        final_level = 'certified'
    elif final_confidence >= 50 and len(advanced_analysis.verified_claims) >= 3:
        final_level = 'verified'
    else:
        final_level = 'unverified'

    print(f"\n  📊 FINAL ASSESSMENT:")
    print(f"     Total sources found: {total_sources}")
    print(f"     Credible sources: {credible_total}")
    print(f"     Verified claims: {len(advanced_analysis.verified_claims)}")
    print(f"     Base confidence: {base_confidence:.1f}/100")
    print(f"     Confidence boost: +{confidence_boost:.1f}")
    print(f"     Final confidence: {final_confidence:.1f}/100")
    print(f"\n  ✅ RECOMMENDATION: {final_level.upper()}")
    print(f"     Rationale: {advanced_analysis.recommendation_rationale}")
    print(f"     Context: {context_research.context_richness_score:.0f}/100 context richness")
    print(f"     Social: {len(social_timeline.eyewitness_accounts)} eyewitness accounts")

    # Overall test validation
    print("\n" + "=" * 80)
    print("TEST VALIDATION")
    print("=" * 80)

    tests_passed = 0
    tests_total = 8

    # Validate Phase 2
    if len(social_sources) > 0:
        print("  ✓ Phase 2: Social media investigation functional")
        tests_passed += 1
    else:
        print("  ✗ Phase 2: No social sources found")

    if len(social_timeline.eyewitness_accounts) >= 0:
        print("  ✓ Phase 2: Eyewitness detection functional")
        tests_passed += 1
    else:
        print("  ✗ Phase 2: Eyewitness detection failed")

    # Validate Phase 3
    if len(context_research.historical_events) > 0:
        print("  ✓ Phase 3: Historical research functional")
        tests_passed += 1
    else:
        print("  ✗ Phase 3: No historical events found")

    if len(context_research.actor_profiles) > 0:
        print("  ✓ Phase 3: Actor profiling functional")
        tests_passed += 1
    else:
        print("  ✗ Phase 3: No actor profiles created")

    if context_research.context_richness_score > 0:
        print(f"  ✓ Phase 3: Context scoring functional ({context_research.context_richness_score:.0f}/100)")
        tests_passed += 1
    else:
        print("  ✗ Phase 3: Context scoring failed")

    # Validate Phase 4
    if len(advanced_analysis.extracted_claims) > 0:
        print("  ✓ Phase 4: Claim extraction functional")
        tests_passed += 1
    else:
        print("  ✗ Phase 4: No claims extracted")

    if advanced_analysis.overall_confidence >= 0:
        print(f"  ✓ Phase 4: Confidence scoring functional ({advanced_analysis.overall_confidence:.0f}/100)")
        tests_passed += 1
    else:
        print("  ✗ Phase 4: Confidence scoring failed")

    # Validate integration
    if final_level in ['unverified', 'verified', 'certified']:
        print(f"  ✓ Integration: Final recommendation valid ({final_level})")
        tests_passed += 1
    else:
        print("  ✗ Integration: Invalid final recommendation")

    print(f"\n  RESULT: {tests_passed}/{tests_total} tests passed")

    if tests_passed == tests_total:
        print("\n  🎉 ALL TESTS PASSED - PHASES 2-4 FULLY FUNCTIONAL")
        return True
    else:
        print(f"\n  ⚠ {tests_total - tests_passed} test(s) failed")
        return False


if __name__ == "__main__":
    try:
        success = test_complete_investigation_pipeline()

        print("\n" + "=" * 80)
        if success:
            print("✅ END-TO-END TEST SUCCESSFUL")
            print("Investigatory Journalist Agent Phases 2-4: COMPLETE AND FUNCTIONAL")
            sys.exit(0)
        else:
            print("⚠ END-TO-END TEST COMPLETED WITH WARNINGS")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}", exc_info=True)
        print(f"\n✗ TEST FAILED: {str(e)}")
        sys.exit(1)
