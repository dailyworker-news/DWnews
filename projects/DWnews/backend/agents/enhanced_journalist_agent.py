"""
Enhanced Journalist Agent - Main Orchestrator
Generates quality articles with self-audit, bias detection, and verified facts integration
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

# Add project root to path (go up from backend/agents/ to project root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import Topic, Article, ArticleRevision, Category
from backend.config import settings
from backend.agents.journalist.self_audit import SelfAudit, AuditResult
from backend.agents.journalist.bias_detector import BiasDetector, BiasReport
from backend.agents.journalist.readability_checker import ReadabilityChecker
from backend.agents.journalist.attribution_engine import AttributionEngine


# Configure logging
logger = logging.getLogger(__name__)


class EnhancedJournalistAgent:
    """
    Enhanced journalist agent that generates articles with:
    - Self-audit validation (10-point checklist)
    - Bias detection (hallucination & propaganda checks)
    - Reading level validation (7.5-8.5 Flesch-Kincaid)
    - Proper source attribution using verified facts
    """

    MAX_REGENERATION_ATTEMPTS = 3

    def __init__(self, db_session: Session):
        """
        Initialize enhanced journalist agent.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.self_audit = SelfAudit()
        self.bias_detector = BiasDetector()
        self.readability_checker = ReadabilityChecker()
        self.attribution_engine = AttributionEngine()

        # Initialize LLM client (Claude)
        self.llm_client = self._initialize_llm_client()

    def _initialize_llm_client(self):
        """Initialize LLM client (Claude API)"""
        try:
            import anthropic
            api_key = os.getenv("CLAUDE_API_KEY") or settings.claude_api_key

            if not api_key:
                logger.warning("CLAUDE_API_KEY not set. Article generation will fail.")
                return None

            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            logger.error("anthropic library not installed. Install with: pip install anthropic")
            return None

    def generate_article(self, topic_id: int) -> Optional[Article]:
        """
        Generate article from verified topic with full quality pipeline.

        Args:
            topic_id: ID of verified topic in database

        Returns:
            Article object if successful, None if failed
        """
        logger.info(f"Starting article generation for topic_id={topic_id}")

        # 1. Load topic with verified facts
        topic = self._load_verified_topic(topic_id)
        if not topic:
            logger.error(f"Topic {topic_id} not found or not verified")
            return None

        # 2. Validate topic has required data
        if not self._validate_topic_data(topic):
            logger.error(f"Topic {topic_id} missing required data (verified_facts or source_plan)")
            return None

        # 3. Parse JSON data
        verified_facts = json.loads(topic.verified_facts)
        source_plan = json.loads(topic.source_plan)

        # 4. Generate article with regeneration loop
        article_text = None
        reading_level = None
        audit_result = None
        bias_report = None
        attempts = 0

        while attempts < self.MAX_REGENERATION_ATTEMPTS:
            attempts += 1
            logger.info(f"Article generation attempt {attempts}/{self.MAX_REGENERATION_ATTEMPTS}")

            # Generate article draft
            article_text = self._generate_article_draft(
                topic.title,
                verified_facts,
                source_plan,
                previous_feedback=audit_result if attempts > 1 else None
            )

            if not article_text:
                logger.error("Article generation failed (LLM error)")
                continue

            # Calculate reading level
            reading_level = self.readability_checker.check_reading_level(article_text)
            logger.info(f"Reading level: {reading_level:.1f}")

            # Get verification level from source plan or topic
            verification_level = source_plan.get('verification_level', topic.verification_status or 'unverified')

            # Run self-audit
            audit_result = self.self_audit.audit_article(
                article_text,
                verified_facts,
                source_plan,
                reading_level,
                verification_level
            )

            logger.info(f"Self-audit score: {audit_result.score:.0f}% ({sum(audit_result.checklist.values())}/10 passed)")

            # Run bias detection
            bias_report = self.bias_detector.scan_article(
                article_text,
                verified_facts,
                source_plan
            )

            logger.info(f"Bias scan: {bias_report.overall_score}")

            # Check if article passes all checks
            if audit_result.passed and bias_report.overall_score == "PASS":
                logger.info("Article passed all quality checks!")
                break
            else:
                logger.warning(f"Article failed quality checks. Attempt {attempts}/{self.MAX_REGENERATION_ATTEMPTS}")
                self._log_failure_reasons(audit_result, bias_report)

        # 5. Check if we succeeded or exhausted attempts
        if not audit_result or not audit_result.passed:
            logger.error(f"Article generation failed after {attempts} attempts")
            return self._create_failed_article(
                topic,
                article_text,
                audit_result,
                bias_report,
                reading_level
            )

        # 6. Create article record
        article = self._create_article_record(
            topic,
            article_text,
            audit_result,
            bias_report,
            reading_level
        )

        logger.info(f"Article created successfully: id={article.id}, title='{article.title}'")

        return article

    def _load_verified_topic(self, topic_id: int) -> Optional[Topic]:
        """Load topic from database and validate verification status"""
        topic = self.db.query(Topic).filter_by(id=topic_id).first()

        if not topic:
            return None

        # Accept any verification level except 'failed'
        accepted_statuses = ['verified', 'certified', 'unverified']

        if topic.verification_status not in accepted_statuses:
            logger.warning(f"Topic {topic_id} has unacceptable verification status: {topic.verification_status}")
            return None

        if topic.verification_status == 'unverified':
            logger.info(f"Topic {topic_id} is UNVERIFIED - will include disclaimer in article")
        elif topic.verification_status == 'certified':
            logger.info(f"Topic {topic_id} is CERTIFIED - thoroughly researched")

        return topic

    def _validate_topic_data(self, topic: Topic) -> bool:
        """Validate topic has required data for article generation"""
        if not topic.verified_facts:
            logger.error("Topic missing verified_facts")
            return False

        if not topic.source_plan:
            logger.error("Topic missing source_plan")
            return False

        try:
            json.loads(topic.verified_facts)
            json.loads(topic.source_plan)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in topic data: {e}")
            return False

        return True

    def _generate_article_draft(
        self,
        topic_title: str,
        verified_facts: Dict[str, Any],
        source_plan: Dict[str, Any],
        previous_feedback: Optional[AuditResult] = None
    ) -> Optional[str]:
        """
        Generate article draft using LLM.

        Args:
            topic_title: Topic title
            verified_facts: Verified facts JSON
            source_plan: Source plan JSON
            previous_feedback: Audit result from previous attempt (for regeneration)

        Returns:
            Article text or None if generation failed
        """
        if not self.llm_client:
            logger.error("LLM client not initialized")
            return None

        # Generate prompt with attribution instructions
        prompt = self.attribution_engine.generate_attribution_prompt(
            topic_title,
            verified_facts,
            source_plan
        )

        # Add verification disclosure to prompt
        verification_note = source_plan.get('verification_note', '')
        verification_level = source_plan.get('verification_level', 'unverified')

        if verification_note:
            prompt += f"\n\nSOURCING DISCLOSURE (REQUIRED):\n"
            prompt += f"This article has sourcing level: {verification_level.upper()}\n"
            prompt += f"You MUST include this disclosure at the end of the article:\n\n"
            prompt += f"---\n**Sourcing Note:** {verification_note}\n---\n"

        # Add feedback if regenerating
        if previous_feedback:
            feedback_text = self._format_feedback(previous_feedback)
            prompt += f"\n\nPREVIOUS ATTEMPT FAILED. Address these issues:\n{feedback_text}\n\nRegenerate the article now."

        try:
            response = self.llm_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            article_text = response.content[0].text
            return article_text

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return None

    def _format_feedback(self, audit_result: AuditResult) -> str:
        """Format audit feedback for regeneration"""
        feedback_lines = []

        for criterion, passed in audit_result.checklist.items():
            if not passed:
                detail = audit_result.details.get(criterion, "No details")
                feedback_lines.append(f"- {criterion}: FAILED - {detail}")

        return "\n".join(feedback_lines)

    def _log_failure_reasons(self, audit_result: AuditResult, bias_report: BiasReport):
        """Log why article failed quality checks"""
        failed_criteria = [k for k, v in audit_result.checklist.items() if not v]

        if failed_criteria:
            logger.warning(f"Failed audit criteria: {', '.join(failed_criteria)}")

        if bias_report.hallucination_detected:
            logger.warning(f"Hallucinations detected: {len(bias_report.hallucination_details)}")

        if bias_report.propaganda_flags:
            logger.warning(f"Propaganda flags: {len(bias_report.propaganda_flags)}")

        if bias_report.bias_indicators:
            logger.warning(f"Bias indicators: {len(bias_report.bias_indicators)}")

    def _create_article_record(
        self,
        topic: Topic,
        article_text: str,
        audit_result: AuditResult,
        bias_report: BiasReport,
        reading_level: float
    ) -> Article:
        """Create article record in database"""
        # Parse article to extract title and body
        title, body = self._parse_article_text(article_text)

        # Generate slug
        slug = self._generate_slug(title)

        # Extract special sections
        why_this_matters = self._extract_section(article_text, "Why This Matters")
        what_you_can_do = self._extract_section(article_text, "What You Can Do")

        # Get verification info from topic
        verification_level = topic.verification_status or 'unverified'
        source_count = topic.source_count or 0

        # Create article
        # Get category_id with fallback to default "Labor" category
        category_id = topic.category_id
        if category_id is None:
            # Fallback to Labor category (id=1) if topic has no category
            logger.warning(f"Topic {topic.id} missing category_id, using default Labor category")
            category_id = 1

        article = Article(
            title=title,
            slug=slug,
            body=body,
            summary=self._generate_summary(body),
            category_id=category_id,
            author="DWnews AI Journalist",
            is_national=topic.is_national,
            is_local=topic.is_local,
            region_id=topic.region_id,
            reading_level=reading_level,
            word_count=len(article_text.split()),
            why_this_matters=why_this_matters,
            what_you_can_do=what_you_can_do,
            status='draft',  # For editorial review
            bias_scan_report=bias_report.to_json(),
            self_audit_passed=audit_result.passed,
            editorial_notes=f"Generated from topic_id={topic.id}. Audit score: {audit_result.score:.0f}%. Verification: {verification_level.upper()} ({source_count} sources)",
            created_at=datetime.utcnow()
        )

        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)

        # Update topic
        topic.article_id = article.id
        topic.status = 'generated'
        self.db.commit()

        # Create initial revision
        self._create_revision(article, audit_result, bias_report, reading_level)

        return article

    def _create_failed_article(
        self,
        topic: Topic,
        article_text: Optional[str],
        audit_result: Optional[AuditResult],
        bias_report: Optional[BiasReport],
        reading_level: Optional[float]
    ) -> Optional[Article]:
        """Create article record for failed generation (for human review)"""
        if not article_text:
            return None

        title, body = self._parse_article_text(article_text)
        slug = self._generate_slug(title) + "-needs-review"

        # Get category_id with fallback to default "Labor" category
        category_id = topic.category_id
        if category_id is None:
            logger.warning(f"Topic {topic.id} missing category_id, using default Labor category")
            category_id = 1

        article = Article(
            title=title + " [NEEDS REVIEW]",
            slug=slug,
            body=body,
            category_id=category_id,
            author="DWnews AI Journalist",
            reading_level=reading_level or 0.0,
            word_count=len(article_text.split()),
            status='draft',
            bias_scan_report=bias_report.to_json() if bias_report else "{}",
            self_audit_passed=False,
            editorial_notes=f"FAILED QUALITY CHECKS. Generated from topic_id={topic.id}. Requires human review.",
            created_at=datetime.utcnow()
        )

        self.db.add(article)
        self.db.commit()

        logger.info(f"Created failed article for human review: {article.id}")

        return article

    def _parse_article_text(self, article_text: str) -> Tuple[str, str]:
        """Parse article text to extract title and body"""
        lines = article_text.strip().split('\n')

        # Find title (first non-empty line, often starts with # in markdown)
        title = ""
        body_start = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Remove markdown heading markers
                title = line.lstrip('#').strip()
                body_start = i + 1
                break

        # Body is everything after title
        body = '\n'.join(lines[body_start:]).strip()

        return title, body

    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug[:100]  # Limit length

        # Add timestamp for uniqueness
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{slug}-{timestamp}"

    def _generate_summary(self, body: str) -> str:
        """Generate article summary (first 2-3 sentences)"""
        import re
        sentences = re.split(r'[.!?]+', body)
        summary_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        return '. '.join(summary_sentences) + '.'

    def _extract_section(self, article_text: str, section_name: str) -> Optional[str]:
        """Extract content from a specific section (e.g., 'Why This Matters')"""
        import re

        # Look for section heading
        pattern = rf'##?\s*{re.escape(section_name)}[:\s]*\n(.+?)(?:\n##|\Z)'
        match = re.search(pattern, article_text, re.IGNORECASE | re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    def _create_revision(
        self,
        article: Article,
        audit_result: AuditResult,
        bias_report: BiasReport,
        reading_level: float
    ):
        """Create initial article revision record"""
        revision = ArticleRevision(
            article_id=article.id,
            revision_number=1,
            revised_by="enhanced_journalist_agent",
            revision_type="draft",
            title_after=article.title,
            body_after=article.body,
            change_summary="Initial article generation with self-audit and bias detection",
            sources_verified=True,
            bias_check_passed=(bias_report.overall_score == "PASS"),
            reading_level_after=reading_level,
            created_at=datetime.utcnow()
        )

        self.db.add(revision)
        self.db.commit()


def main():
    """CLI for testing enhanced journalist agent"""
    import argparse
    from backend.database import SessionLocal

    parser = argparse.ArgumentParser(description="Enhanced Journalist Agent - Article Generation")
    parser.add_argument("topic_id", type=int, help="Topic ID to generate article from")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create database session
    db = SessionLocal()

    try:
        # Create agent
        agent = EnhancedJournalistAgent(db)

        # Generate article
        article = agent.generate_article(args.topic_id)

        if article:
            print(f"\n✓ Article generated successfully!")
            print(f"  ID: {article.id}")
            print(f"  Title: {article.title}")
            print(f"  Reading Level: {article.reading_level:.1f}")
            print(f"  Word Count: {article.word_count}")
            print(f"  Self-Audit Passed: {article.self_audit_passed}")
            print(f"  Status: {article.status}")
        else:
            print(f"\n✗ Article generation failed for topic {args.topic_id}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
