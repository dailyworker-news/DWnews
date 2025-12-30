#!/usr/bin/env python3
"""
The Daily Worker - Test Data Generator
Creates test articles for local development and testing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Article, Source, Region, Category
from backend.config import settings


def generate_test_articles(count=10):
    """Generate test articles for local testing"""

    print("=" * 60)
    print("The Daily Worker - Generating Test Articles")
    print("=" * 60)

    # Create engine and session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Fetch categories, regions, and sources
        categories = session.query(Category).all()
        regions = session.query(Region).all()
        sources = session.query(Source).filter(Source.credibility_score >= 4).all()

        if not categories or not regions or not sources:
            print("✗ Please run seed_data.py first to populate categories, regions, and sources")
            return

        # Test article templates
        test_articles = [
            {
                "title": "Amazon Workers in Alabama Win Union Vote After Three-Year Battle",
                "slug": "amazon-alabama-union-victory-2025",
                "category": "labor",
                "is_national": True,
                "is_local": False,
                "is_ongoing": True,
                "body": """In a landmark victory for labor organizing, Amazon warehouse workers in Bessemer, Alabama have successfully voted to unionize after a three-year campaign marked by intense corporate resistance.

The final vote count of 2,654 to 2,131 in favor of unionization marks the first successful union drive at an Amazon facility in the United States. The Retail, Wholesale and Department Store Union (RWDSU) led the organizing effort.

"This is a historic moment for working people across America," said union organizer Maria Gonzalez. "Amazon workers have shown that even the most powerful corporations can be held accountable when workers stand together."

The victory comes after previous failed attempts in 2021 and 2023, which were marred by allegations of union-busting tactics including mandatory anti-union meetings and surveillance of organizers.""",
                "why_this_matters": "This victory could spark a wave of union organizing at Amazon facilities nationwide and demonstrates that workers can successfully organize even at companies known for aggressive anti-union tactics.",
                "what_you_can_do": "Support unionization efforts by: 1) Shopping at unionized retailers when possible, 2) Sharing pro-union content on social media, 3) Contacting your representatives to support the PRO Act",
                "reading_level": 8.2
            },
            {
                "title": "Federal Reserve Raises Interest Rates, Economists Warn of Recession Impact on Workers",
                "slug": "fed-rate-hike-worker-impact-2025",
                "category": "economics",
                "is_national": True,
                "is_local": False,
                "is_ongoing": False,
                "body": """The Federal Reserve announced another quarter-point interest rate increase today, bringing the benchmark rate to 5.75%, the highest level in over two decades.

While Fed Chair Jerome Powell emphasized the need to combat inflation, economists warn that continued rate hikes could trigger a recession that would disproportionately impact working-class Americans through job losses.

"The Fed's singular focus on inflation ignores the real pain these policies cause working families," said Dr. Susan Martinez of the Economic Policy Institute. "Higher interest rates mean more expensive mortgages, car loans, and credit card debt for people already struggling with high costs."

Unemployment has ticked up from 3.5% to 3.9% over the past six months, with layoffs concentrated in manufacturing and retail sectors.""",
                "why_this_matters": "Interest rate policy directly affects workers' ability to afford housing, cars, and everyday expenses. Recession fears could lead to widespread layoffs.",
                "reading_level": 7.8
            },
            {
                "title": "Chicago Teachers Union Reaches Tentative Agreement, Averts Strike",
                "slug": "chicago-teachers-tentative-agreement",
                "category": "labor",
                "is_national": False,
                "is_local": True,
                "is_ongoing": True,
                "body": """The Chicago Teachers Union (CTU) and Chicago Public Schools reached a tentative agreement early this morning, averting a planned strike that would have affected 300,000 students.

The three-year deal includes a 15% salary increase, reduced class sizes, and increased funding for social workers and nurses in schools. Union members will vote on ratification next week.

"Our members stood strong and won real improvements for students and educators," said CTU President Maria Lopez. "This agreement shows what's possible when workers organize and fight for what they deserve."

The deal comes after months of contentious negotiations and follows successful teacher strikes in Los Angeles and Oakland that resulted in similar wins for educators.""",
                "why_this_matters": "Teacher organizing nationwide is securing better working conditions and demonstrating the power of collective action in the public sector.",
                "what_you_can_do": "Support teachers' unions by voting for school board candidates who support fair contracts and attending school board meetings to voice support for educators.",
                "reading_level": 7.5
            },
            {
                "title": "New Study Reveals Corporate Profits Hit Record Highs While Wages Stagnate",
                "slug": "corporate-profits-wage-stagnation-study",
                "category": "economics",
                "is_national": True,
                "is_local": False,
                "is_ongoing": False,
                "body": """A comprehensive study released today by the Economic Policy Institute reveals that corporate profits reached record levels in 2024 while real wages for workers remained essentially flat after accounting for inflation.

The analysis found that corporate profit margins increased by 28% since 2019, while median wages grew by just 4.2% over the same period—well below the 15% inflation rate.

"This is clear evidence that inflation has been driven by corporate price gouging, not wage increases," said lead researcher Dr. James Williams. "Workers are producing more value than ever, but corporations are capturing all the gains."

The study found the disparity was most pronounced in sectors like retail, food service, and logistics where frontline workers saw minimal wage growth despite record company profits.""",
                "why_this_matters": "This data undermines claims that worker wages are driving inflation and demonstrates how corporate greed is enriching executives at workers' expense.",
                "reading_level": 8.0
            },
            {
                "title": "Starbucks Workers Win Major NLRB Ruling on Illegal Union Busting",
                "slug": "starbucks-nlrb-ruling-union-busting",
                "category": "labor",
                "is_national": True,
                "is_local": False,
                "is_ongoing": True,
                "body": """The National Labor Relations Board (NLRB) issued a sweeping ruling today finding that Starbucks engaged in illegal union-busting activities at hundreds of locations nationwide.

The decision orders Starbucks to reinstate fired union organizers, reverse store closures targeting union locations, and bargain in good faith with unionized stores. The company may also face significant financial penalties.

"This ruling vindicates what workers have been saying all along," said Starbucks Workers United organizer Alex Kim. "Starbucks broke the law repeatedly to stop workers from organizing, and now they're being held accountable."

More than 300 Starbucks locations have voted to unionize since 2021, but the company has yet to sign a single union contract. This ruling could force meaningful negotiations.""",
                "why_this_matters": "This major NLRB decision sets a precedent for holding corporations accountable for illegal anti-union tactics and could accelerate organizing at Starbucks and similar companies.",
                "what_you_can_do": "Support Starbucks workers by: 1) Visiting unionized stores and thanking workers, 2) Sharing #StarbucksWorkersUnited content, 3) Filing NLRB complaints if you witness union-busting",
                "reading_level": 8.1
            },
            {
                "title": "Los Angeles Passes Nation's Strongest Tenant Protections Against Corporate Landlords",
                "slug": "la-tenant-protections-corporate-landlords",
                "category": "politics",
                "is_national": False,
                "is_local": True,
                "is_ongoing": False,
                "body": """Los Angeles City Council voted unanimously yesterday to pass sweeping tenant protection legislation targeting corporate landlords and private equity-owned rental properties.

The new law caps annual rent increases at 3%, bans algorithm-based rent pricing, and requires 180-day notice for no-fault evictions. It applies to all buildings with 5 or more units.

"Corporate landlords have been using technology and market power to price working families out of their homes," said Council Member Rosa Martinez, who authored the legislation. "This law puts people over profits."

Housing advocates estimate the law will protect over 400,000 renter households from predatory pricing practices that have driven LA rents up 45% since 2019.""",
                "why_this_matters": "Housing costs are the largest expense for most workers. This legislation could serve as a model for other cities fighting corporate landlord exploitation.",
                "reading_level": 7.9
            },
            {
                "title": "Good News: Maine Becomes First State to Guarantee Paid Sick Leave for All Workers",
                "slug": "maine-paid-sick-leave-guarantee",
                "category": "good-news",
                "is_national": False,
                "is_local": False,
                "is_ongoing": False,
                "body": """Maine has become the first state to guarantee paid sick leave for all workers, regardless of employer size or industry, after Governor Janet Mills signed landmark legislation yesterday.

The law requires employers to provide one hour of paid sick leave for every 30 hours worked, up to 40 hours annually. It covers all employees including part-time, seasonal, and gig workers.

"No worker should have to choose between their health and their paycheck," Governor Mills said at the signing ceremony. "This is a victory for working families across Maine."

Business groups opposed the measure, but polls showed 72% of Mainers supported guaranteed paid sick leave. The law takes effect January 1, 2026.""",
                "why_this_matters": "This sets a precedent for guaranteed paid sick leave nationwide and demonstrates that progressive labor policies can pass even in competitive political environments.",
                "what_you_can_do": "Contact your state representatives to support similar paid sick leave legislation in your state.",
                "reading_level": 7.7
            },
        ]

        print(f"\nGenerating {len(test_articles)} test articles...")

        created_count = 0
        for i, article_data in enumerate(test_articles):
            # Find category
            category = next((c for c in categories if c.slug == article_data["category"]), None)
            if not category:
                print(f"Warning: Category '{article_data['category']}' not found, skipping article")
                continue

            # Find or create region
            region = None
            if article_data.get("is_local"):
                region = next((r for r in regions if r.name != "National"), None)

            # Check if article already exists
            existing = session.query(Article).filter_by(slug=article_data["slug"]).first()
            if existing:
                print(f"  - Skipping '{article_data['title']}' (already exists)")
                continue

            # Create article
            article = Article(
                title=article_data["title"],
                slug=article_data["slug"],
                body=article_data["body"],
                summary=article_data["body"][:200] + "...",
                category_id=category.id,
                is_national=article_data.get("is_national", True),
                is_local=article_data.get("is_local", False),
                region_id=region.id if region else None,
                is_ongoing=article_data.get("is_ongoing", False),
                is_new=True,
                reading_level=article_data.get("reading_level", 8.0),
                word_count=len(article_data["body"].split()),
                why_this_matters=article_data.get("why_this_matters"),
                what_you_can_do=article_data.get("what_you_can_do"),
                status="published",
                published_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )

            # Add random sources
            article_sources = random.sample(sources, min(3, len(sources)))
            article.sources = article_sources

            session.add(article)
            created_count += 1
            print(f"  ✓ Created: {article.title}")

        session.commit()

        print(f"\n✓ Created {created_count} test articles (total: {session.query(Article).count()})")
        print("\nArticle breakdown:")
        print(f"  - National: {session.query(Article).filter_by(is_national=True).count()}")
        print(f"  - Local: {session.query(Article).filter_by(is_local=True).count()}")
        print(f"  - Ongoing: {session.query(Article).filter_by(is_ongoing=True).count()}")

        # Show category distribution
        print("\nCategory distribution:")
        for category in categories:
            count = session.query(Article).filter_by(category_id=category.id).count()
            if count > 0:
                print(f"  - {category.name}: {count}")

    except Exception as e:
        session.rollback()
        print(f"\n✗ Error generating test data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        generate_test_articles()
        print("\n" + "=" * 60)
        print("✓ Test data generated successfully!")
        print("=" * 60)
        print("\nNext step: Start the backend server")
        print("  cd backend && python main.py")
    except Exception as e:
        print(f"\n✗ Failed to generate test data: {e}")
        sys.exit(1)
