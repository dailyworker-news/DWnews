#!/usr/bin/env python3
"""
The Daily Worker - Article Generation
Generates articles from filtered topics using LLM APIs
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from database.models import Topic, Article, Category, Source
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = get_logger(__name__)

# Reading level checker
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logger.warning("textstat not available - reading level checks disabled")


class ArticleGenerator:
    """Article generation service using LLM APIs"""

    def __init__(self, session):
        self.session = session
        self.llm_client = None
        self.llm_type = None

        # Initialize LLM client (try in order: Claude, OpenAI, Gemini)
        if settings.claude_api_key:
            try:
                from anthropic import Anthropic
                self.llm_client = Anthropic(api_key=settings.claude_api_key)
                self.llm_type = 'claude'
                logger.info("Claude API initialized")
            except ImportError:
                logger.warning("anthropic package not installed")
        elif settings.openai_api_key:
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=settings.openai_api_key)
                self.llm_type = 'openai'
                logger.info("OpenAI API initialized")
            except ImportError:
                logger.warning("openai package not installed")
        elif settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.llm_client = genai.GenerativeModel('gemini-pro')
                self.llm_type = 'gemini'
                logger.info("Gemini API initialized")
            except ImportError:
                logger.warning("google-generativeai package not installed")

    def create_generation_prompt(self, topic: Topic) -> str:
        """Create article generation prompt in Joe Sugarman copywriting style"""

        prompt = f"""You are writing for The Daily Worker, a news platform that delivers accurate, worker-centric news through a Marxist/Leninist lens.

TOPIC: {topic.title}

BACKGROUND: {topic.description or 'No additional context provided'}

INSTRUCTIONS:
Write a news article following these strict requirements:

1. ACCURACY: Present only factual information. No speculation or opinion unless clearly labeled.

2. WORKER-CENTRIC LENS: Focus on how this affects working-class Americans. Explain the material impact on workers' lives.

3. MARXIST/LENINIST ANALYSIS: Analyze power dynamics between workers and capital. Don't pull punches when describing corporate or political malfeasance.

4. READING LEVEL: Write at an 8th-grade reading level (Flesch-Kincaid 7.5-8.5). Use clear, direct language. Short sentences. Active voice.

5. STRUCTURE (Joe Sugarman format):
   - Headline: Compelling, factual, worker-focused
   - Opening: Hook with the most important fact
   - Body: Chronological or pyramid structure
   - Quotes: Include perspectives from workers/unions when possible
   - Analysis: Connect to broader patterns of exploitation or worker power
   - Conclusion: Clear takeaway about what this means for workers

6. SPECIAL SECTIONS:
   - "Why This Matters": 2-3 sentences on broader significance
   - "What You Can Do": 2-3 concrete actions readers can take (only if applicable)

7. LENGTH: 300-600 words

8. TONE: Professional journalist but not neutral. We have a perspective: pro-worker, anti-exploitation.

Write the article now. Use this exact format:

HEADLINE: [Your headline]

[Article body]

WHY THIS MATTERS:
[2-3 sentences]

WHAT YOU CAN DO:
[2-3 concrete actions, or write "N/A" if not applicable]
"""
        return prompt

    def call_llm(self, prompt: str, max_tokens: int = 1500) -> Optional[str]:
        """Call LLM API to generate article"""
        if not self.llm_client:
            logger.error("No LLM client available")
            return None

        try:
            if self.llm_type == 'claude':
                response = self.llm_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.llm_type == 'openai':
                response = self.llm_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif self.llm_type == 'gemini':
                response = self.llm_client.generate_content(prompt)
                return response.text

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None

    def parse_article_response(self, response: str) -> Dict:
        """Parse LLM response into article components"""
        if not response:
            return {}

        # Extract headline
        headline_match = re.search(r'HEADLINE:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        headline = headline_match.group(1).strip() if headline_match else ""

        # Extract "Why This Matters"
        why_match = re.search(r'WHY THIS MATTERS:\s*(.+?)(?=WHAT YOU CAN DO:|$)', response, re.DOTALL | re.IGNORECASE)
        why_matters = why_match.group(1).strip() if why_match else ""

        # Extract "What You Can Do"
        what_match = re.search(r'WHAT YOU CAN DO:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        what_can_do = what_match.group(1).strip() if what_match else ""
        if what_can_do.upper() == "N/A":
            what_can_do = ""

        # Extract body (everything between headline and "Why This Matters")
        body = response
        if headline:
            body = body.split(headline, 1)[1] if headline in body else body
        if "WHY THIS MATTERS:" in body.upper():
            body = body.split("WHY THIS MATTERS:")[0]

        # Clean body
        body = body.strip()
        body = re.sub(r'\n{3,}', '\n\n', body)  # Max 2 newlines

        return {
            'headline': headline,
            'body': body,
            'why_this_matters': why_matters,
            'what_you_can_do': what_can_do
        }

    def check_reading_level(self, text: str) -> float:
        """Check Flesch-Kincaid reading level"""
        if not TEXTSTAT_AVAILABLE or not text:
            return 8.0  # Default assumption

        try:
            level = textstat.flesch_kincaid_grade(text)
            return level
        except Exception as e:
            logger.warning(f"Reading level check failed: {e}")
            return 8.0

    def generate_article(self, topic: Topic, verbose: bool = False) -> Optional[Article]:
        """Generate article from topic"""
        if verbose:
            print(f"\n📝 Generating: {topic.title[:60]}...")

        # Create prompt
        prompt = self.create_generation_prompt(topic)

        # Call LLM
        if verbose:
            print(f"   Calling {self.llm_type.upper()} API...")

        response = self.call_llm(prompt)
        if not response:
            if verbose:
                print("   ✗ Failed to generate article")
            return None

        # Parse response
        parsed = self.parse_article_response(response)
        if not parsed.get('headline') or not parsed.get('body'):
            if verbose:
                print("   ✗ Failed to parse article")
            logger.error(f"Parse failed for topic {topic.id}")
            return None

        # Check reading level
        reading_level = self.check_reading_level(parsed['body'])

        if verbose:
            print(f"   Reading level: {reading_level:.1f}")

        # Warn if outside target range
        if reading_level < settings.min_reading_level or reading_level > settings.max_reading_level:
            if verbose:
                print(f"   ⚠ Reading level outside target ({settings.min_reading_level}-{settings.max_reading_level})")

        # Generate slug
        slug = re.sub(r'[^\w\s-]', '', parsed['headline'].lower())
        slug = re.sub(r'[-\s]+', '-', slug)[:100]

        # Count words
        word_count = len(parsed['body'].split())

        # Create article
        article = Article(
            title=parsed['headline'],
            slug=slug,
            body=parsed['body'],
            summary=parsed['body'][:200] + "..." if len(parsed['body']) > 200 else parsed['body'],
            category_id=topic.category_id,
            is_national=topic.is_national,
            is_local=topic.is_local,
            region_id=topic.region_id,
            reading_level=reading_level,
            word_count=word_count,
            why_this_matters=parsed.get('why_this_matters'),
            what_you_can_do=parsed.get('what_you_can_do'),
            status='draft',  # Needs human review
            created_at=datetime.utcnow()
        )

        # Link topic to article
        topic.article_id = article.id
        topic.status = 'generated'

        if verbose:
            print(f"   ✓ Generated ({word_count} words)")

        return article

    def generate_batch(self, max_articles: int = 10, verbose: bool = True) -> int:
        """Generate multiple articles from filtered topics"""
        # Get filtered topics without articles
        topics = self.session.query(Topic).filter_by(status='filtered').limit(max_articles).all()

        if not topics:
            logger.warning("No filtered topics available")
            return 0

        generated_count = 0
        for topic in topics:
            article = self.generate_article(topic, verbose=verbose)

            if article:
                self.session.add(article)
                generated_count += 1

                # Commit after each article (in case of failures)
                try:
                    self.session.commit()
                except Exception as e:
                    self.session.rollback()
                    logger.error(f"Failed to save article: {e}")

        return generated_count


def run_generation(max_articles: int = 10, verbose: bool = True) -> int:
    """Run article generation"""
    print("=" * 60)
    print("The Daily Worker - Article Generation")
    print("=" * 60)

    # Check LLM API availability
    if not settings.has_llm_api():
        print("\n✗ No LLM API configured. Add API key to .env:")
        print("  - CLAUDE_API_KEY")
        print("  - OPENAI_API_KEY")
        print("  - GEMINI_API_KEY")
        return 0

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Initialize generator
        generator = ArticleGenerator(session)

        if not generator.llm_client:
            print("\n✗ Failed to initialize LLM client")
            return 0

        print(f"\nUsing LLM: {generator.llm_type.upper()}")

        # Generate articles
        print(f"\nGenerating up to {max_articles} articles...")
        count = generator.generate_batch(max_articles=max_articles, verbose=verbose)

        # Show results
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE")
        print("=" * 60)
        print(f"✓ Generated: {count} articles")

        if count > 0:
            # Show reading level distribution
            articles = session.query(Article).filter_by(status='draft').all()
            avg_level = sum(a.reading_level for a in articles) / len(articles)
            print(f"\nAverage reading level: {avg_level:.1f}")
            print(f"Target range: {settings.min_reading_level}-{settings.max_reading_level}")

        return count

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        print(f"\n✗ Error: {e}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    count = run_generation(max_articles=10, verbose=True)

    if count > 0:
        print(f"\n✓ {count} articles generated and saved as drafts")
        print("\nNext steps:")
        print("  1. Review articles in admin dashboard")
        print("  2. Approve articles for publishing")
        print("  3. Run image sourcing: python scripts/content/source_images.py")
    else:
        print("\n⚠ No articles generated. Check:")
        print("  1. Filtered topics exist (run filter_topics.py)")
        print("  2. LLM API key is valid")
        print("  3. API quota/rate limits")
