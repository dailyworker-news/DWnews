#!/usr/bin/env python3
"""
Sample Content Generator
Generates realistic sample articles for demonstration and testing.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Article, Category, Source, Topic, ArticleSource
from database.init_db import SessionLocal
from scripts.utils.text_utils import generate_hash


# Sample article templates
SAMPLE_ARTICLES = [
    {
        "title": "Tech Workers at Major Company Vote to Unionize",
        "slug": "tech-workers-major-company-vote-unionize",
        "category": "Tech",
        "body": """In a historic victory for tech labor organizing, workers at a major technology company voted overwhelmingly to form a union. The vote passed with 72% support among eligible employees.

The organizing effort began eight months ago when workers raised concerns about long hours, lack of job security, and inadequate compensation relative to company profits. The new union will represent over 300 workers across multiple departments.

"This shows that tech workers are realizing they have power when they stand together," said one organizer. "We're not just asking for better conditions for ourselves, but setting a precedent for the entire industry."

Management initially opposed the unionization effort, arguing it would make the company less competitive. However, workers persisted through an intensive organizing campaign that included educational sessions, one-on-one conversations, and public demonstrations.

The union plans to begin contract negotiations within the next month, focusing on wage increases, improved benefits, and stronger protections against arbitrary dismissals.""",
        "summary": "Tech workers vote to form union with 72% support, marking historic victory for tech labor organizing.",
        "why_this_matters": "This victory demonstrates that even in industries traditionally hostile to unions, workers can successfully organize when they stand together. It may inspire similar efforts at other tech companies.",
        "what_you_can_do": "If you work in tech and are interested in organizing, reach out to established tech worker organizations. Support union campaigns by spreading the word and showing solidarity.",
        "is_national": True,
        "is_local": False,
        "is_ongoing": True,
        "is_new": True,
        "reading_level": 8.0,
        "word_count": 245,
        "status": "published"
    },
    {
        "title": "Local Community Garden Expands to Feed Hundreds",
        "slug": "local-community-garden-expands-feed-hundreds",
        "category": "Good News",
        "body": """A community garden started by neighborhood volunteers has grown into a vital food source for hundreds of families. The garden now spans three city blocks and produces thousands of pounds of fresh vegetables annually.

What began as a small plot tended by a dozen neighbors has transformed into a thriving cooperative with over 80 active participants. Volunteers work together to grow tomatoes, lettuce, peppers, squash, and other vegetables that are distributed for free to anyone in need.

"We're proving that communities can take care of each other," said the garden's co-founder. "Every harvest day, we see neighbors helping neighbors, sharing knowledge, and building real connections."

The garden has become more than just a food source. It's a gathering place where people learn sustainable farming practices, children discover where food comes from, and elderly residents find community engagement.

Local schools have partnered with the garden to create educational programs. Students visit regularly to learn about agriculture and nutrition, while helping with planting and harvesting.""",
        "summary": "Community garden expands to three city blocks, feeding hundreds of families with fresh vegetables.",
        "why_this_matters": "Community gardens demonstrate practical solutions to food insecurity while building stronger neighborhoods. They show what's possible when people work together outside traditional market systems.",
        "what_you_can_do": "Start or join a community garden in your area. If you have gardening skills, offer to teach others. Donate seeds, tools, or time to support existing gardens.",
        "is_national": False,
        "is_local": True,
        "is_ongoing": False,
        "is_new": True,
        "reading_level": 7.8,
        "word_count": 228,
        "status": "published"
    },
    {
        "title": "Manufacturing Workers Strike for Better Safety Conditions",
        "slug": "manufacturing-workers-strike-better-safety",
        "category": "Labor",
        "body": """Workers at a manufacturing plant have entered their second week of striking over dangerous working conditions. The strike began after a series of workplace injuries that workers say could have been prevented with proper safety measures.

Union representatives report that management has ignored repeated requests to fix broken equipment, improve ventilation systems, and provide adequate safety training. Three workers have been injured in the past two months, including one hospitalization.

"We're not asking for luxuries. We're asking not to get hurt at work," explained a striking worker. "Our families depend on us coming home safe every day."

The company has offered minor concessions but refuses to commit to the major safety improvements workers demand. The union remains firm in its position that worker safety is non-negotiable.

Community support for the strike has been strong, with local residents bringing food and supplies to the picket line. Other labor unions have also pledged their support.""",
        "summary": "Manufacturing workers strike for second week demanding improved safety conditions after series of injuries.",
        "why_this_matters": "Worker safety should never be optional. This strike highlights ongoing struggles for basic workplace protections that save lives.",
        "what_you_can_do": "Support striking workers by respecting picket lines, donating to strike funds, and pressuring companies to improve conditions. Report unsafe conditions at your own workplace.",
        "is_national": False,
        "is_local": True,
        "is_ongoing": True,
        "is_new": True,
        "reading_level": 8.2,
        "word_count": 215,
        "status": "published"
    },
    {
        "title": "Study Shows Four-Day Work Week Boosts Productivity",
        "slug": "study-four-day-work-week-boosts-productivity",
        "category": "Economics",
        "body": """A comprehensive study of companies that adopted a four-day work week found increased productivity, happier workers, and reduced burnout. The research tracked 61 companies over six months.

Results showed that 92% of participating companies plan to continue the four-day schedule. Workers reported better work-life balance, improved mental health, and greater job satisfaction. Meanwhile, productivity remained stable or increased in most cases.

"This challenges the assumption that longer hours equal more output," noted the study's lead researcher. "Workers with more time for rest and personal life actually perform better during work hours."

The companies studied represent various industries including technology, marketing, healthcare, and manufacturing. They implemented different models, but all reduced weekly work hours without reducing pay.

Employee retention improved dramatically, with turnover dropping by an average of 57%. Many workers said they would not return to a five-day schedule even for significantly higher pay at another company.""",
        "summary": "Study of 61 companies finds four-day work week increases productivity and worker satisfaction with no loss in output.",
        "why_this_matters": "This research provides concrete evidence that reducing work hours benefits both workers and employers. It challenges outdated assumptions about productivity.",
        "what_you_can_do": "Advocate for reduced work hours at your workplace. Share this research with management and fellow workers. Support political candidates who back shorter work weeks.",
        "is_national": True,
        "is_local": False,
        "is_ongoing": False,
        "is_new": False,
        "reading_level": 8.1,
        "word_count": 209,
        "status": "published"
    },
    {
        "title": "Rent Strike Forces Landlord to Make Long-Overdue Repairs",
        "slug": "rent-strike-forces-landlord-repairs",
        "category": "Current Affairs",
        "body": """Tenants in a 40-unit apartment building organized a successful rent strike that forced their landlord to address years of neglected maintenance. After three months of collective action, major repairs are now underway.

Residents had complained for years about broken heating systems, water leaks, pest infestations, and unsafe electrical wiring. When individual complaints went unaddressed, tenants came together to form a tenants' association.

The group delivered a formal letter demanding repairs with a deadline. When the deadline passed with no action, residents voted to withhold rent until conditions improved. They placed their rent payments into an escrow account to demonstrate good faith.

The landlord initially threatened evictions, but found that mass eviction of organized tenants would be difficult and expensive. After mediation, the landlord agreed to a repair schedule and reduced rent during the work period.

"Standing together made all the difference," said a tenant organizer. "One person complaining gets ignored. Forty people united get results."

The association continues to meet regularly to ensure repairs are completed properly and to address any new issues collectively.""",
        "summary": "Tenants organize successful rent strike forcing landlord to complete long-overdue repairs after years of complaints.",
        "why_this_matters": "This shows how tenant organizing can force landlords to meet basic obligations. Collective action gives renters power they don't have as individuals.",
        "what_you_can_do": "If you're a renter facing neglect, talk to your neighbors about organizing. Join or start a tenants' association. Document all maintenance issues and know your rights.",
        "is_national": False,
        "is_local": True,
        "is_ongoing": False,
        "is_new": True,
        "reading_level": 7.9,
        "word_count": 248,
        "status": "published"
    }
]


def generate_sample_content():
    """Generate sample articles for demonstration."""

    print("=" * 50)
    print("Sample Content Generator")
    print("=" * 50)
    print()

    db = SessionLocal()

    try:
        # Get categories
        categories = {cat.name: cat for cat in db.query(Category).all()}

        if not categories:
            print("❌ No categories found. Please run seed_data.py first.")
            return False

        print(f"✓ Found {len(categories)} categories")

        # Get sources
        sources = db.query(Source).filter(Source.is_active == True).all()
        if not sources:
            print("❌ No sources found. Please run seed_data.py first.")
            return False

        print(f"✓ Found {len(sources)} active sources")
        print()

        # Generate articles
        articles_created = 0
        now = datetime.utcnow()

        for i, article_data in enumerate(SAMPLE_ARTICLES, 1):
            print(f"Creating article {i}/{len(SAMPLE_ARTICLES)}: {article_data['title']}")

            # Check if article already exists
            existing = db.query(Article).filter(
                Article.slug == article_data['slug']
            ).first()

            if existing:
                print(f"  ⚠ Article already exists, skipping...")
                continue

            # Get category
            category = categories.get(article_data['category'])
            if not category:
                print(f"  ❌ Category '{article_data['category']}' not found")
                continue

            # Create article
            article = Article(
                title=article_data['title'],
                slug=article_data['slug'],
                category_id=category.id,
                body=article_data['body'],
                summary=article_data.get('summary'),
                why_this_matters=article_data.get('why_this_matters'),
                what_you_can_do=article_data.get('what_you_can_do'),
                is_national=article_data['is_national'],
                is_local=article_data['is_local'],
                is_ongoing=article_data['is_ongoing'],
                is_new=article_data['is_new'],
                reading_level=article_data['reading_level'],
                word_count=article_data['word_count'],
                status=article_data['status'],
                published_at=now - timedelta(days=random.randint(0, 5)),
                created_at=now - timedelta(days=random.randint(0, 10))
            )

            # Add 2-3 random credible sources
            num_sources = random.randint(2, 3)
            article_sources = random.sample(sources, min(num_sources, len(sources)))

            for source in article_sources:
                article.sources.append(source)

            db.add(article)
            articles_created += 1
            print(f"  ✓ Created article with {len(article_sources)} sources")

        db.commit()

        print()
        print("=" * 50)
        print(f"✅ Successfully created {articles_created} sample articles")
        print("=" * 50)
        print()
        print("You can now:")
        print("1. Start the backend: cd backend && uvicorn main:app --reload")
        print("2. View articles at: http://localhost:8000/api/articles/")
        print("3. Open the frontend: frontend/index.html")
        print("4. Open the admin dashboard: frontend/admin/index.html")
        print()

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = generate_sample_content()
    sys.exit(0 if success else 1)
