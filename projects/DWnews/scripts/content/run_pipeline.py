#!/usr/bin/env python3
"""
The Daily Worker - Complete Content Pipeline
Runs the full content generation workflow:
1. Discovery (RSS + Social Media)
2. Filtering (Viability checks)
3. Generation (LLM articles)
4. Images (Sourcing and optimization)
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from scripts.content.discover_topics import discover_all_topics
from scripts.content.filter_topics import run_filtering
from scripts.content.generate_articles import run_generation
from scripts.content.source_images import run_image_sourcing

logger = get_logger(__name__)


def run_full_pipeline(
    max_topics: int = 50,
    max_articles: int = 10,
    skip_discovery: bool = False,
    skip_filtering: bool = False,
    skip_generation: bool = False,
    skip_images: bool = False,
    verbose: bool = True
):
    """Run complete content generation pipeline"""

    print("=" * 70)
    print(" " * 20 + "THE DAILY WORKER")
    print(" " * 15 + "Content Generation Pipeline")
    print("=" * 70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {settings.environment}")
    print(f"Max articles: {max_articles}")

    results = {
        'topics_discovered': 0,
        'topics_filtered': 0,
        'articles_generated': 0,
        'images_sourced': 0,
        'errors': []
    }

    # Phase 1: Topic Discovery
    if not skip_discovery:
        print("\n" + "=" * 70)
        print("PHASE 1: TOPIC DISCOVERY")
        print("=" * 70)
        try:
            results['topics_discovered'] = discover_all_topics()
        except Exception as e:
            error = f"Discovery failed: {e}"
            results['errors'].append(error)
            logger.error(error)
            print(f"\n✗ {error}")

            if not skip_filtering:
                print("\n⚠ Skipping remaining phases due to discovery failure")
                return results
    else:
        print("\n⏭  Skipping discovery (--skip-discovery)")

    # Phase 2: Viability Filtering
    if not skip_filtering:
        print("\n" + "=" * 70)
        print("PHASE 2: VIABILITY FILTERING")
        print("=" * 70)
        try:
            filter_results = run_filtering(verbose=verbose)
            results['topics_filtered'] = filter_results.get('passed', 0)

            if results['topics_filtered'] == 0:
                print("\n⚠ No topics passed filtering. Cannot generate articles.")
                return results
        except Exception as e:
            error = f"Filtering failed: {e}"
            results['errors'].append(error)
            logger.error(error)
            print(f"\n✗ {error}")
            return results
    else:
        print("\n⏭  Skipping filtering (--skip-filtering)")

    # Phase 3: Article Generation
    if not skip_generation:
        print("\n" + "=" * 70)
        print("PHASE 3: ARTICLE GENERATION")
        print("=" * 70)

        if not settings.has_llm_api():
            print("\n⚠ No LLM API configured. Skipping generation.")
            print("  Add to .env: CLAUDE_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY")
        else:
            try:
                results['articles_generated'] = run_generation(
                    max_articles=max_articles,
                    verbose=verbose
                )

                if results['articles_generated'] == 0:
                    print("\n⚠ No articles generated. Cannot source images.")
                    return results
            except Exception as e:
                error = f"Generation failed: {e}"
                results['errors'].append(error)
                logger.error(error)
                print(f"\n✗ {error}")
                return results
    else:
        print("\n⏭  Skipping generation (--skip-generation)")

    # Phase 4: Image Sourcing
    if not skip_images:
        print("\n" + "=" * 70)
        print("PHASE 4: IMAGE SOURCING")
        print("=" * 70)
        try:
            results['images_sourced'] = run_image_sourcing(
                max_articles=max_articles,
                verbose=verbose
            )
        except Exception as e:
            error = f"Image sourcing failed: {e}"
            results['errors'].append(error)
            logger.error(error)
            print(f"\n✗ {error}")
    else:
        print("\n⏭  Skipping images (--skip-images)")

    return results


def print_final_summary(results: dict):
    """Print pipeline execution summary"""
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\n📊 Results Summary:")
    print(f"  • Topics discovered: {results['topics_discovered']}")
    print(f"  • Topics filtered (passed): {results['topics_filtered']}")
    print(f"  • Articles generated: {results['articles_generated']}")
    print(f"  • Images sourced: {results['images_sourced']}")

    if results['errors']:
        print(f"\n⚠ Errors encountered: {len(results['errors'])}")
        for i, error in enumerate(results['errors'], 1):
            print(f"  {i}. {error}")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if results['articles_generated'] > 0:
        print("\n✓ Pipeline successful!")
        print("\nNext steps:")
        print("  1. Review generated articles: query database for status='draft'")
        print("  2. Use admin dashboard to approve articles")
        print("  3. Publish approved articles")
    else:
        print("\n⚠ No articles generated. Check configuration and logs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run The Daily Worker content pipeline")
    parser.add_argument("--max-topics", type=int, default=50, help="Maximum topics to discover")
    parser.add_argument("--max-articles", type=int, default=10, help="Maximum articles to generate")
    parser.add_argument("--skip-discovery", action="store_true", help="Skip topic discovery")
    parser.add_argument("--skip-filtering", action="store_true", help="Skip topic filtering")
    parser.add_argument("--skip-generation", action="store_true", help="Skip article generation")
    parser.add_argument("--skip-images", action="store_true", help="Skip image sourcing")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")

    args = parser.parse_args()

    try:
        results = run_full_pipeline(
            max_topics=args.max_topics,
            max_articles=args.max_articles,
            skip_discovery=args.skip_discovery,
            skip_filtering=args.skip_filtering,
            skip_generation=args.skip_generation,
            skip_images=args.skip_images,
            verbose=not args.quiet
        )

        print_final_summary(results)

        # Exit with success if articles were generated
        sys.exit(0 if results['articles_generated'] > 0 else 1)

    except KeyboardInterrupt:
        print("\n\nPipeline cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        logger.exception("Pipeline failed")
        sys.exit(1)
