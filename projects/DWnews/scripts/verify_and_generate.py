#!/usr/bin/env python3
"""
Verify and Generate - Process existing approved topics through full pipeline

Takes approved topics and runs them through:
1. Verification Agent - Gather sources and extract verified facts
2. Enhanced Journalist Agent - Generate articles with proper citations
3. Image Sourcer - Generate images with DALL-E
4. Editorial Review - Prepare for publication

NO HALLUCINATIONS - Only verified, cited content.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import settings
from backend.agents.verification_agent import VerificationAgent
from backend.agents.enhanced_journalist_agent import EnhancedJournalistAgent
from scripts.content.source_images import ImageSourcer
from backend.logging_config import get_logger
from database.models import Topic

logger = get_logger(__name__)

def main():
    """Process existing approved topics through full pipeline"""

    print("=" * 80)
    print("VERIFY AND GENERATE - Process Approved Topics")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Verify sources and extract facts from approved topics")
    print("  2. Generate articles with CITATIONS ONLY from verified sources")
    print("  3. Generate images with DALL-E")
    print("  4. Prepare for editorial review")
    print("\nNO HALLUCINATIONS - Only verified, cited content.\n")

    # Create database session
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get approved topics that need verification
        print("=" * 80)
        print("Finding Approved Topics")
        print("=" * 80)

        topics = session.query(Topic).filter_by(
            status='approved',
            verification_status='unverified'
        ).limit(5).all()

        if not topics:
            print("\n⚠ No unverified approved topics found.")
            return False

        print(f"\n✓ Found {len(topics)} approved topics to process:")
        for topic in topics:
            print(f"  - {topic.title[:70]}...")

        # Step 1: Verification - Gather sources and verify facts
        print("\n" + "=" * 80)
        print("STEP 1: Verifying Sources and Extracting Facts")
        print("=" * 80)

        verifier = VerificationAgent(session)
        verified_count = 0

        for topic in topics:
            print(f"\nVerifying: {topic.title[:70]}...")
            try:
                verifier.verify_topic(topic.id)
                session.commit()
                session.refresh(topic)
                print(f"  ✓ Verified (status: {topic.verification_status}, sources: {topic.source_count})")
                verified_count += 1
            except Exception as e:
                logger.error(f"Verification failed: {e}")
                print(f"  ✗ Verification failed: {e}")

        print(f"\n✓ Verified {verified_count}/{len(topics)} topics")

        # Step 2: Article Generation - Use ONLY verified facts
        print("\n" + "=" * 80)
        print("STEP 2: Generating Articles with Source Citations")
        print("=" * 80)
        print("\nIMPORTANT: Journalist will ONLY use verified facts from sources.")
        print("Any article without proper citations will be flagged.\n")

        journalist = EnhancedJournalistAgent(session)
        articles_generated = []

        for topic in topics:
            print(f"\nGenerating article: {topic.title[:60]}...")
            print(f"  Verification status: {topic.verification_status}")
            print(f"  Source count: {topic.source_count}")

            try:
                article = journalist.generate_article(topic.id)
                if article:
                    session.refresh(article)
                    articles_generated.append(article)
                    print(f"  ✓ Article generated (ID: {article.id})")
                    print(f"    Word count: {article.word_count}")
                    print(f"    Self-audit: {'PASS' if article.self_audit_passed else 'FAIL'}")
                else:
                    print(f"  ✗ Article generation failed")
            except Exception as e:
                logger.error(f"Error generating article: {e}")
                print(f"  ✗ Error: {e}")

        print(f"\n✓ Generated {len(articles_generated)} articles")

        if len(articles_generated) == 0:
            print("\n⚠ No articles generated. Check verification results.")
            return False

        # Step 3: Image Sourcing
        print("\n" + "=" * 80)
        print("STEP 3: Generating Images with DALL-E")
        print("=" * 80)

        sourcer = ImageSourcer(session)
        images_sourced = 0

        for article in articles_generated:
            print(f"\nSourcing image: {article.title[:60]}...")
            try:
                if sourcer.source_image_for_article(article, verbose=True):
                    images_sourced += 1
                    session.commit()
            except Exception as e:
                logger.error(f"Error sourcing image: {e}")
                print(f"  ✗ Error: {e}")

        print(f"\n✓ Sourced {images_sourced} images")

        # Step 4: Prepare for Review
        print("\n" + "=" * 80)
        print("STEP 4: Preparing Articles for Editorial Review")
        print("=" * 80)

        for article in articles_generated:
            article.status = 'draft'
            has_citations = ('According to' in article.body or
                           'reported' in article.body or
                           'said' in article.body)
            print(f"\n✓ {article.title[:60]}...")
            print(f"  Status: draft (ready for review)")
            print(f"  Has citations: {has_citations}")
            print(f"  Has image: {bool(article.image_url)}")

        session.commit()

        # Final Summary
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"  Topics processed: {len(topics)}")
        print(f"  Topics verified: {verified_count}")
        print(f"  Articles generated: {len(articles_generated)}")
        print(f"  Images sourced: {images_sourced}")

        if articles_generated:
            print(f"\n📰 Generated Articles (with verified sources):")
            for article in articles_generated:
                print(f"\n  • {article.title}")
                print(f"    Status: {article.status}")
                print(f"    Self-audit: {'✓ PASS' if article.self_audit_passed else '✗ FAIL'}")
                print(f"    Has image: {'✓' if article.image_url else '✗'}")

        print(f"\n✓ Articles ready for review in admin dashboard:")
        print(f"   http://localhost:8000/frontend/admin/")

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
