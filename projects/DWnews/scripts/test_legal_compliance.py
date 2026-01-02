#!/usr/bin/env python3
"""
Test Article Generation with New Legal Compliance
Generates 3 articles with proper sourcing and legal compliance checking
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Topic, Category
from backend.config import settings
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from scripts.content.source_images import ImageSourcer

def create_test_topics_with_sources(session):
    """Create test topics with proper source attributions for legal compliance testing"""

    # Get categories (case-insensitive lookup)
    categories = {cat.name.lower(): cat for cat in session.query(Category).all()}

    # Create missing categories if needed
    needed_categories = ['labor', 'politics', 'tech']
    for cat_name in needed_categories:
        if cat_name not in categories:
            new_cat = Category(
                name=cat_name.capitalize(),
                slug=cat_name.lower(),
                description=f"{cat_name.capitalize()} news and updates"
            )
            session.add(new_cat)
            session.flush()
            categories[cat_name] = new_cat
            print(f"Created category: {cat_name.capitalize()}")

    session.commit()

    test_topics = [
        {
            'title': 'Major Labor Strike at Auto Manufacturing Plant',
            'description': 'Workers at Detroit auto plant walk out over wages and benefits',
            'category': 'labor',
            'keywords': 'strike, auto workers, labor dispute, manufacturing',
            'sources': [
                {
                    'url': 'https://www.reuters.com/business/autos-transportation/auto-workers-strike-2024',
                    'title': 'Auto Workers Launch Strike Over Contract Disputes',
                    'author': 'Reuters News Service',
                    'publication_name': 'Reuters',
                    'credibility_tier': 1,
                    'summary': 'Thousands of auto workers walked off the job demanding better pay and working conditions'
                },
                {
                    'url': 'https://apnews.com/article/labor-auto-strike',
                    'title': 'UAW Members Vote to Strike at Detroit Plant',
                    'author': 'Associated Press',
                    'publication_name': 'Associated Press',
                    'credibility_tier': 1,
                    'summary': 'Union members cite inflation and cost of living as key concerns'
                },
                {
                    'url': 'https://www.npr.org/2024/auto-workers-strike',
                    'title': 'Auto Workers Join Growing Wave of Labor Actions',
                    'author': 'NPR Labor Correspondent',
                    'publication_name': 'NPR',
                    'credibility_tier': 1,
                    'summary': 'The strike is part of a broader labor movement across manufacturing'
                }
            ]
        },
        {
            'title': 'Federal Minimum Wage Increase Proposed in Congress',
            'description': 'New bill would raise federal minimum wage to $17 per hour by 2026',
            'category': 'politics',
            'keywords': 'minimum wage, congress, legislation, workers',
            'sources': [
                {
                    'url': 'https://www.congress.gov/bill/minimum-wage-act',
                    'title': 'Raise the Wage Act of 2024',
                    'author': 'U.S. Congress',
                    'publication_name': 'Congress.gov',
                    'credibility_tier': 1,
                    'summary': 'Official text of proposed legislation to increase minimum wage'
                },
                {
                    'url': 'https://www.washingtonpost.com/politics/minimum-wage-bill',
                    'title': 'Democrats Introduce $17 Minimum Wage Bill',
                    'author': 'Washington Post Staff',
                    'publication_name': 'Washington Post',
                    'credibility_tier': 1,
                    'summary': 'Bill has support from progressive caucus but faces uphill battle'
                }
            ]
        },
        {
            'title': 'Tech Workers Form First Union at Major Silicon Valley Company',
            'description': 'Software engineers and data scientists vote to unionize, citing workload and job security concerns',
            'category': 'tech',
            'keywords': 'tech union, silicon valley, software engineers, labor organizing',
            'sources': [
                {
                    'url': 'https://www.bloomberg.com/tech/silicon-valley-union',
                    'title': 'Tech Workers Vote to Unionize in Historic Move',
                    'author': 'Bloomberg Technology',
                    'publication_name': 'Bloomberg',
                    'credibility_tier': 1,
                    'summary': 'Vote marks significant shift in traditionally anti-union tech sector'
                },
                {
                    'url': 'https://www.wired.com/story/tech-union-organizing',
                    'title': 'Inside the Tech Union Movement',
                    'author': 'WIRED Staff',
                    'publication_name': 'WIRED',
                    'credibility_tier': 2,
                    'summary': 'Workers cite layoffs, return-to-office mandates, and overwork as motivations'
                },
                {
                    'url': 'https://techcrunch.com/tech-workers-unionize',
                    'title': 'First Tech Union Certified in Silicon Valley',
                    'author': 'TechCrunch',
                    'publication_name': 'TechCrunch',
                    'credibility_tier': 2,
                    'summary': 'NLRB certifies union election results'
                },
                {
                    'url': 'https://www.theverge.com/tech-labor-organizing',
                    'title': 'Tech Union Wins Certification',
                    'author': 'The Verge',
                    'publication_name': 'The Verge',
                    'credibility_tier': 2,
                    'summary': 'Union to begin contract negotiations next month'
                }
            ]
        }
    ]

    created_topics = []

    for topic_data in test_topics:
        # Create topic
        category_name = topic_data.pop('category')
        sources_data = topic_data.pop('sources')

        topic = Topic(
            title=topic_data['title'],
            description=topic_data['description'],
            keywords=topic_data['keywords'],
            status='approved',
            discovered_from='Legal Compliance Test'
        )

        # Set category if it exists
        if category_name in categories:
            topic.category_id = categories[category_name].id

        # Set source count and verification status
        # NOTE: Database still uses old terms, but journalist will use new legal terms
        topic.source_count = len(sources_data)

        # Map to database-compatible verification status
        if len(sources_data) >= 5:
            topic.verification_status = 'certified'  # DB term (journalist will output "multi-sourced")
        elif len(sources_data) >= 2:
            topic.verification_status = 'verified'  # DB term (journalist will output "corroborated")
        else:
            topic.verification_status = 'unverified'  # DB term (journalist will output "aggregated")

        # Store source URLs in metadata (for journalist to reference)
        import json
        topic.metadata = json.dumps({
            'sources': [{'url': s['url'], 'title': s['title'], 'publication': s.get('publication_name', 'Unknown')} for s in sources_data]
        })

        # Create verified_facts for journalist agent (required field)
        # Format as dict with key facts from the description
        verified_facts = {
            'main_event': {
                'statement': topic.description,
                'sources': [s.get('publication_name', 'Unknown') for s in sources_data],
                'urls': [s['url'] for s in sources_data],
                'credibility': 'tier_1'
            }
        }

        topic.verified_facts = json.dumps(verified_facts)

        # Create source_plan for journalist agent (required field)
        topic.source_plan = json.dumps({
            'primary_sources': [s.get('publication_name', 'Unknown') for s in sources_data[:3]],
            'attribution_required': True,
            'quotes_needed': 1,
            'source_count': len(sources_data)
        })

        session.add(topic)
        session.commit()
        session.refresh(topic)
        created_topics.append(topic)

        print(f"✓ Created topic: {topic.title}")
        print(f"  - Category: {category_name}")
        print(f"  - Sources: {len(sources_data)}")
        print(f"  - Verification: {topic.verification_status}")

    return created_topics


def run_test():
    """Run complete test workflow"""

    print("=" * 80)
    print("LEGAL COMPLIANCE TEST - Article Generation with New Guidelines")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Step 1: Create test topics with proper sources
        print("=" * 80)
        print("STEP 1: Creating Test Topics with Proper Source Attribution")
        print("=" * 80)
        print()

        topics = create_test_topics_with_sources(session)
        print(f"\n✓ Created {len(topics)} topics with proper sourcing\n")

        # Step 2: Generate articles with legal compliance
        print("=" * 80)
        print("STEP 2: Generating Articles with Legal Compliance")
        print("=" * 80)
        print()

        journalist = EnhancedJournalistAgent(session)
        generated_articles = []

        for topic in topics:
            print(f"Generating: {topic.title}")
            print(f"  Sources: {topic.source_count}")
            print(f"  Verification: {topic.verification_status}")

            try:
                article = journalist.generate_article(topic.id)

                if article:
                    session.refresh(article)
                    print(f"  ✓ Article generated (ID: {article.id})")
                    print(f"    Word count: {article.word_count}")
                    print(f"    Reading level: {article.reading_level or 'N/A'}")
                    print(f"    Self-audit: {'PASS' if article.self_audit_passed else 'FAIL'}")
                    if article.editorial_notes:
                        print(f"    Notes: {article.editorial_notes[:100]}...")
                    generated_articles.append(article)
                else:
                    print(f"  ✗ Article generation failed")

            except Exception as e:
                print(f"  ✗ Error: {e}")

            print()

        print(f"✓ Generated {len(generated_articles)} articles\n")

        # Step 3: Source images
        print("=" * 80)
        print("STEP 3: Sourcing Images for Articles")
        print("=" * 80)
        print()

        image_sourcer = ImageSourcer(session)
        images_sourced = 0

        for article in generated_articles:
            print(f"Sourcing image: {article.title[:60]}...")
            try:
                if image_sourcer.source_image_for_article(article, verbose=True):
                    images_sourced += 1
                    session.commit()
            except Exception as e:
                print(f"  ✗ Error: {e}")

        print(f"\n✓ Sourced {images_sourced} images\n")

        # Step 4: Approve for admin review
        print("=" * 80)
        print("STEP 4: Preparing Articles for Admin Review")
        print("=" * 80)
        print()

        for article in generated_articles:
            # Keep as 'draft' for admin review
            article.status = 'draft'
            session.commit()
            print(f"✓ {article.title[:60]}... - Ready for review")

        # Final Summary
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"  Topics created: {len(topics)}")
        print(f"  Articles generated: {len(generated_articles)}")
        print(f"  Images sourced: {images_sourced}")
        print(f"  Status: All articles in 'draft' status for admin review")

        if generated_articles:
            print(f"\n📰 Generated Articles:")
            for i, article in enumerate(generated_articles, 1):
                print(f"\n  {i}. {article.title}")
                print(f"     Category: {article.category_id}")
                print(f"     Word count: {article.word_count}")
                print(f"     Self-audit: {'✓ PASS' if article.self_audit_passed else '✗ FAIL'}")
                print(f"     Image: {'✓' if article.image_url else '✗'}")

        print(f"\n✓ Articles ready for review in admin dashboard at:")
        print(f"   http://localhost:8000/frontend/admin/")

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
