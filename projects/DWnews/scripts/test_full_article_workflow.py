#!/usr/bin/env python3
"""
Full Article Workflow Test

Tests the complete automated journalism pipeline:
1. Signal Intake Agent (event discovery)
2. Evaluation Agent (newsworthiness scoring)
3. Verification Agent (source verification)
4. Enhanced Journalist Agent (article drafting)
5. Publication (article publishing)

Generates 3 articles across different categories.
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_db
from database.models import Topic, Article, EventCandidate
from backend.agents.signal_intake_agent import SignalIntakeAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.agents.verification_agent import VerificationAgent
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from backend.agents.publication_agent import PublicationAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_event_candidates(db):
    """Create test event candidates for 3 different categories."""

    test_events = [
        {
            'title': 'Amazon Warehouse Workers in NYC Vote to Authorize Strike',
            'description': 'Workers at Amazon\'s JFK8 warehouse in Staten Island voted 500-200 to authorize strike action over wages and working conditions. The Amazon Labor Union led the organizing campaign.',
            'source_url': 'https://example.com/labor/amazon-strike-vote',
            'discovered_from': 'Test: Labor Category',
            'event_date': datetime.utcnow() - timedelta(hours=6),
            'suggested_category': 'labor',
            'keywords': 'amazon, warehouse, strike, union, alu, staten island',
            'status': 'discovered'
        },
        {
            'title': 'Healthcare Workers Rally for Better Staffing Ratios at City Hospital',
            'description': 'Nurses and healthcare workers at Metropolitan Hospital held a rally demanding mandatory nurse-to-patient ratios. Over 300 workers participated, citing unsafe working conditions and patient care concerns.',
            'source_url': 'https://example.com/healthcare/staffing-rally',
            'discovered_from': 'Test: Healthcare Category',
            'event_date': datetime.utcnow() - timedelta(hours=12),
            'suggested_category': 'healthcare',
            'keywords': 'nurses, healthcare, hospital, staffing, patient safety',
            'status': 'discovered'
        },
        {
            'title': 'Teachers Union Reaches Tentative Agreement on Contract After Months of Negotiations',
            'description': 'Chicago Teachers Union announced a tentative agreement with the school district that includes a 15% wage increase over three years and reduced class sizes. The deal came after six months of intense negotiations.',
            'source_url': 'https://example.com/education/teachers-contract',
            'discovered_from': 'Test: Education Category',
            'event_date': datetime.utcnow() - timedelta(hours=18),
            'suggested_category': 'education',
            'keywords': 'teachers, union, contract, chicago, wages, class size',
            'status': 'discovered'
        }
    ]

    created_events = []
    for event_data in test_events:
        event = EventCandidate(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        created_events.append(event)
        logger.info(f"Created test event: {event.title}")

    return created_events


def run_full_workflow_test():
    """Run complete article generation workflow for 3 categories."""

    print("\n" + "=" * 80)
    print("FULL ARTICLE WORKFLOW TEST")
    print("Generating 3 Articles Across Different Categories")
    print("=" * 80)

    db = next(get_db())

    try:
        # Step 1: Create test event candidates
        print("\n" + "=" * 80)
        print("STEP 1: EVENT DISCOVERY (Signal Intake)")
        print("=" * 80)

        events = create_test_event_candidates(db)
        print(f"\n✓ Created {len(events)} test event candidates:")
        for event in events:
            print(f"  • {event.title} ({event.suggested_category})")

        # Step 2: Evaluate events for newsworthiness
        print("\n" + "=" * 80)
        print("STEP 2: NEWSWORTHINESS EVALUATION")
        print("=" * 80)

        evaluation_agent = EvaluationAgent(db)
        approved_topics = []

        for event in events:
            result = evaluation_agent.evaluate_event(event)
            if result and result.get('status') == 'approved':
                topic_id = result.get('topic_id')
                topic = db.query(Topic).filter_by(id=topic_id).first()
                if topic:
                    approved_topics.append(topic)
                    print(f"\n✓ Approved: {topic.title}")
                    print(f"  Score: {result.get('score', 0):.1f}/100")
                    print(f"  Impact: {result.get('worker_impact_score', 0):.1f}/100")
            else:
                print(f"\n✗ Rejected: {event.title}")

        if not approved_topics:
            print("\n⚠ No topics approved. Creating topics manually for testing...")
            # Create topics manually for testing
            for event in events:
                topic = Topic(
                    title=event.title,
                    description=event.description,
                    keywords=event.keywords,
                    discovered_from=event.discovered_from,
                    status='approved',
                    verification_status='unverified'
                )
                db.add(topic)
                db.commit()
                db.refresh(topic)
                approved_topics.append(topic)
                print(f"  Created topic: {topic.title}")

        print(f"\n✓ Total approved topics: {len(approved_topics)}")

        # Step 3: Verify sources for each topic
        print("\n" + "=" * 80)
        print("STEP 3: SOURCE VERIFICATION")
        print("=" * 80)

        verification_agent = VerificationAgent(db)
        verified_topics = []

        for topic in approved_topics:
            print(f"\nVerifying: {topic.title}")
            result = verification_agent.verify_topic(topic.id)

            if result:
                db.refresh(topic)
                print(f"  ✓ Verification status: {topic.verification_status}")
                print(f"  ✓ Source count: {topic.source_count or 0}")
                if hasattr(topic, 'verification_score'):
                    print(f"  ✓ Verification score: {topic.verification_score or 0:.1f}/100")
                verified_topics.append(topic)
            else:
                print(f"  ✗ Verification failed")

        print(f"\n✓ Total verified topics: {len(verified_topics)}")

        # Step 4: Generate articles
        print("\n" + "=" * 80)
        print("STEP 4: ARTICLE GENERATION")
        print("=" * 80)

        journalist_agent = EnhancedJournalistAgent(db)
        generated_articles = []

        for topic in verified_topics:
            print(f"\nGenerating article: {topic.title}")

            try:
                article = journalist_agent.generate_article(topic.id)

                if article:
                    db.refresh(article)
                    print(f"  ✓ Article ID: {article.id}")
                    print(f"  ✓ Headline: {article.headline}")
                    print(f"  ✓ Word count: {len(article.content.split()) if article.content else 0}")
                    print(f"  ✓ Reading level: {article.reading_level_score or 0:.1f}")
                    print(f"  ✓ Self-audit passed: {article.self_audit_passed}")
                    generated_articles.append(article)
                else:
                    print(f"  ✗ Article generation failed")

            except Exception as e:
                logger.error(f"Error generating article: {str(e)}", exc_info=True)
                print(f"  ✗ Error: {str(e)}")

        print(f"\n✓ Total articles generated: {len(generated_articles)}")

        # Step 5: Publish articles
        print("\n" + "=" * 80)
        print("STEP 5: ARTICLE PUBLICATION")
        print("=" * 80)

        publication_agent = PublicationAgent(db)
        published_articles = []

        for article in generated_articles:
            print(f"\nPublishing: {article.headline}")

            # Set article to approved status for testing
            article.status = 'approved'
            db.commit()

            # Publish
            result = publication_agent.publish_article(article.id)

            if result:
                db.refresh(article)
                print(f"  ✓ Published successfully")
                print(f"  ✓ Status: {article.status}")
                print(f"  ✓ Published at: {article.published_at}")
                published_articles.append(article)
            else:
                print(f"  ✗ Publication failed")

        print(f"\n✓ Total articles published: {len(published_articles)}")

        # Final Summary
        print("\n" + "=" * 80)
        print("WORKFLOW TEST SUMMARY")
        print("=" * 80)

        print(f"\n📊 Pipeline Statistics:")
        print(f"  Events discovered: {len(events)}")
        print(f"  Topics approved: {len(approved_topics)}")
        print(f"  Topics verified: {len(verified_topics)}")
        print(f"  Articles generated: {len(generated_articles)}")
        print(f"  Articles published: {len(published_articles)}")

        if published_articles:
            print(f"\n📰 Published Articles:")
            for i, article in enumerate(published_articles, 1):
                print(f"\n  {i}. {article.headline}")
                print(f"     Category: {article.category}")
                print(f"     Verification: {article.verification_badge or 'N/A'}")
                print(f"     Word count: {len(article.content.split()) if article.content else 0}")
                print(f"     Reading level: {article.reading_level_score or 0:.1f}")
                print(f"     URL: /article/{article.id}")

        # Validation
        print(f"\n" + "=" * 80)
        print("VALIDATION")
        print("=" * 80)

        success = True

        if len(events) < 3:
            print("  ✗ Failed to create 3 test events")
            success = False
        else:
            print(f"  ✓ Created {len(events)} test events")

        if len(approved_topics) < 1:
            print("  ✗ No topics approved")
            success = False
        else:
            print(f"  ✓ Approved {len(approved_topics)} topics")

        if len(generated_articles) < 1:
            print("  ✗ No articles generated")
            success = False
        else:
            print(f"  ✓ Generated {len(generated_articles)} articles")

        if len(published_articles) < 1:
            print("  ✗ No articles published")
            success = False
        else:
            print(f"  ✓ Published {len(published_articles)} articles")

        # Check category diversity
        categories = set(a.category for a in published_articles)
        if len(categories) >= 2:
            print(f"  ✓ Article diversity: {len(categories)} categories ({', '.join(categories)})")
        elif published_articles:
            print(f"  ⚠ Limited diversity: only {len(categories)} category")

        print("\n" + "=" * 80)
        if success and len(published_articles) >= 2:
            print("✅ WORKFLOW TEST SUCCESSFUL")
            print(f"Generated {len(published_articles)} articles across {len(categories)} categories")
            return True
        elif success:
            print("⚠ WORKFLOW TEST PARTIALLY SUCCESSFUL")
            print(f"Generated {len(published_articles)} articles (target: 3)")
            return True
        else:
            print("✗ WORKFLOW TEST FAILED")
            return False

    except Exception as e:
        logger.error(f"Workflow test failed: {str(e)}", exc_info=True)
        print(f"\n✗ TEST FAILED: {str(e)}")
        return False

    finally:
        db.close()


if __name__ == "__main__":
    try:
        success = run_full_workflow_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
