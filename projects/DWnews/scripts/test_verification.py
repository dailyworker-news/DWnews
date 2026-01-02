#!/usr/bin/env python3
"""
Test script for Verification Agent

Tests the verification agent with approved topics from the database.
Validates source count, attribution plans, and fact classification.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.agents.verification_agent import VerificationAgent
from database.models import Topic, EventCandidate


def create_mock_web_search(topic_title: str):
    """
    Create a mock web search function for testing
    Returns predefined search results based on topic
    """
    def mock_search(query: str, max_results: int = 3):
        """Mock search that returns realistic results"""
        # Simulate different types of sources based on query
        results = []

        if 'nlrb' in query.lower() or 'government' in query.lower():
            results.append({
                'title': f'NLRB Decision on {topic_title}',
                'url': 'https://nlrb.gov/case/12345',
                'snippet': f'Official ruling regarding {topic_title}. The National Labor Relations Board certified the results...'
            })

        if 'official' in query.lower() or 'statement' in query.lower():
            results.append({
                'title': f'Official Statement on {topic_title}',
                'url': 'https://example.com/press-release',
                'snippet': f'Company issues official statement about {topic_title}...'
            })

        if 'reuters' in query.lower() or 'news' in query.lower():
            results.append({
                'title': f'Reuters: {topic_title}',
                'url': 'https://reuters.com/article/12345',
                'snippet': f'According to sources, {topic_title} represents a significant development...'
            })

        if 'ap' in query.lower() or 'news' in query.lower():
            results.append({
                'title': f'AP News: {topic_title}',
                'url': 'https://apnews.com/article/67890',
                'snippet': f'Workers involved in {topic_title} said they are hopeful for change...'
            })

        if 'academic' in query.lower() or 'scholar' in query.lower():
            results.append({
                'title': f'Research Study: Impact of {topic_title}',
                'url': 'https://scholar.google.com/citations?view_op=view',
                'snippet': f'This peer-reviewed study examines the effects of {topic_title} on workers...'
            })

        if 'bloomberg' in query.lower():
            results.append({
                'title': f'Bloomberg: {topic_title}',
                'url': 'https://bloomberg.com/news/articles/12345',
                'snippet': f'Analysis of {topic_title} shows potential economic implications...'
            })

        # Generic news results
        if 'site:nytimes' in query.lower():
            results.append({
                'title': f'New York Times: {topic_title}',
                'url': 'https://nytimes.com/2024/01/01/business/topic.html',
                'snippet': f'Coverage of {topic_title} in the labor sector...'
            })

        # Ensure we return at least some results
        if not results:
            results.append({
                'title': f'News about {topic_title}',
                'url': 'https://example.com/news',
                'snippet': f'General coverage of {topic_title}...'
            })

        return results[:max_results]

    return mock_search


def print_topic_details(topic: Topic):
    """Print detailed information about a topic"""
    print(f"\nTopic ID: {topic.id}")
    print(f"Title: {topic.title}")
    print(f"Description: {topic.description}")
    print(f"Status: {topic.status}")
    print(f"Verification Status: {topic.verification_status}")
    print(f"Discovered from: {topic.discovered_from}")
    print(f"Category: {topic.category.name if topic.category else 'None'}")


def print_verification_results(topic: Topic):
    """Print verification results for a topic"""
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)

    if topic.verified_facts:
        print("\nVerified Facts:")
        print("-" * 60)
        verified_facts = json.loads(topic.verified_facts)

        for i, fact in enumerate(verified_facts.get('facts', []), 1):
            print(f"\n{i}. {fact['claim']}")
            print(f"   Type: {fact['type']}")
            print(f"   Confidence: {fact['confidence']}")
            print(f"   Sources: {len(fact.get('sources', []))}")
            if fact.get('conflicting_info'):
                print(f"   ⚠ Conflict: {fact['conflicting_info']}")

        summary = verified_facts.get('source_summary', {})
        print("\n" + "-" * 60)
        print("Source Summary:")
        print(f"  Total sources: {summary.get('total_sources', 0)}")
        print(f"  Credible sources: {summary.get('credible_sources', 0)}")
        print(f"  Academic citations: {summary.get('academic_citations', 0)}")
        print(f"  Meets threshold: {'YES' if summary.get('meets_threshold') else 'NO'}")
        print(f"  Agreement score: {summary.get('source_agreement_score', 0):.2f}")

    if topic.source_plan:
        print("\n" + "=" * 60)
        print("SOURCE PLAN")
        print("=" * 60)
        source_plan = json.loads(topic.source_plan)

        print("\nPrimary Sources:")
        for i, source in enumerate(source_plan.get('primary_sources', []), 1):
            print(f"{i}. {source['name']}")
            print(f"   URL: {source['url']}")
            print(f"   Type: {source['type']}")
            print(f"   Tier: {source['credibility_tier']}, Score: {source['credibility_score']}")

        if source_plan.get('supporting_sources'):
            print("\nSupporting Sources:")
            for i, source in enumerate(source_plan.get('supporting_sources', []), 1):
                print(f"{i}. {source['name']}")
                print(f"   Type: {source['type']}, Tier: {source['credibility_tier']}")

        print("\nAttribution Strategy:")
        print(f"  {source_plan.get('attribution_strategy', 'N/A')}")

    print("\nDatabase Fields:")
    print(f"  source_count: {topic.source_count}")
    print(f"  academic_citation_count: {topic.academic_citation_count}")
    print(f"  verification_status: {topic.verification_status}")


def test_single_topic(session, topic_id: int):
    """Test verification on a single topic"""
    print("\n" + "=" * 60)
    print(f"TESTING TOPIC {topic_id}")
    print("=" * 60)

    topic = session.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        print(f"✗ Topic {topic_id} not found")
        return False

    print_topic_details(topic)

    # Create agent with mock search
    mock_search = create_mock_web_search(topic.title)
    agent = VerificationAgent(session, web_search_fn=mock_search)

    # Reset verification status for testing
    topic.verification_status = 'pending'
    topic.verified_facts = None
    topic.source_plan = None
    session.commit()

    # Run verification
    print("\nRunning verification...")
    success = agent.verify_topic(topic.id)

    # Refresh topic to get updated data
    session.refresh(topic)

    if success:
        print("\n✓ Verification succeeded")
        print_verification_results(topic)
        return True
    else:
        print(f"\n✗ Verification failed: {topic.verification_status}")
        return False


def test_all_approved_topics(session, limit: int = 5):
    """Test verification on all approved topics"""
    print("\n" + "=" * 60)
    print("TESTING ALL APPROVED TOPICS")
    print("=" * 60)

    # Get approved topics
    topics = session.query(Topic).filter(
        Topic.status == 'approved'
    ).limit(limit).all()

    if not topics:
        print("\n✗ No approved topics found in database")
        print("\nTo create test topics, run:")
        print("  python backend/agents/evaluation_agent.py")
        return

    print(f"\nFound {len(topics)} approved topics")

    # Test each topic
    results = []
    for i, topic in enumerate(topics, 1):
        print(f"\n{'#' * 60}")
        print(f"TOPIC {i}/{len(topics)}: {topic.title}")
        print('#' * 60)

        # Create agent with mock search
        mock_search = create_mock_web_search(topic.title)
        agent = VerificationAgent(session, web_search_fn=mock_search)

        # Reset verification status for testing
        topic.verification_status = 'pending'
        topic.verified_facts = None
        topic.source_plan = None
        session.commit()

        # Run verification
        success = agent.verify_topic(topic.id)

        # Refresh topic
        session.refresh(topic)

        results.append({
            'topic_id': topic.id,
            'title': topic.title,
            'success': success,
            'status': topic.verification_status,
            'source_count': topic.source_count,
            'academic_citations': topic.academic_citation_count
        })

        if success:
            print(f"\n✓ Verification succeeded")
            print(f"  Sources: {topic.source_count}, Academic: {topic.academic_citation_count}")
        else:
            print(f"\n✗ Verification failed: {topic.verification_status}")

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\nTotal topics tested: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)}")

    if successful:
        avg_sources = sum(r['source_count'] for r in successful) / len(successful)
        avg_academic = sum(r['academic_citations'] for r in successful) / len(successful)

        print(f"\nAverage metrics (successful topics):")
        print(f"  Sources: {avg_sources:.1f}")
        print(f"  Academic citations: {avg_academic:.1f}")

    print("\nDetailed Results:")
    for r in results:
        status_icon = "✓" if r['success'] else "✗"
        print(f"{status_icon} [{r['topic_id']}] {r['title'][:50]}")
        print(f"   Status: {r['status']}, Sources: {r['source_count']}, Academic: {r['academic_citations']}")


def main():
    """Main test function"""
    session = SessionLocal()

    print("=" * 60)
    print("VERIFICATION AGENT - TEST SUITE")
    print("=" * 60)

    # Check if there are approved topics
    approved_count = session.query(Topic).filter(
        Topic.status == 'approved'
    ).count()

    print(f"\nApproved topics in database: {approved_count}")

    if approved_count == 0:
        print("\n⚠ No approved topics found!")
        print("\nTo create approved topics, run:")
        print("  cd /Users/home/sandbox/daily_worker/projects/DWnews")
        print("  python backend/agents/signal_intake_agent.py")
        print("  python backend/agents/evaluation_agent.py")
        session.close()
        return

    # Test all approved topics
    test_all_approved_topics(session, limit=10)

    session.close()


if __name__ == '__main__':
    main()
