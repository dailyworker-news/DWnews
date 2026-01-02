"""
Self-Audit Module - 10-Point Article Validation Checklist
Validates articles against DWnews editorial standards
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AuditResult:
    """Result of self-audit validation"""
    passed: bool
    checklist: Dict[str, bool]  # criterion name -> pass/fail
    details: Dict[str, str]  # criterion name -> details/reason
    score: float  # percentage passed (0-100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class SelfAudit:
    """
    Self-audit validator for articles.
    Implements 10-point checklist for article quality.
    """

    CHECKLIST_CRITERIA = [
        "factual_accuracy",
        "source_attribution",
        "reading_level",
        "worker_centric_framing",
        "no_hallucinations",
        "proper_context",
        "active_voice",
        "specific_details",
        "balanced_representation",
        "editorial_standards"
    ]

    def __init__(self):
        """Initialize self-audit validator"""
        pass

    def audit_article(
        self,
        article_text: str,
        verified_facts: Dict[str, Any],
        source_plan: Dict[str, Any],
        reading_level: float
    ) -> AuditResult:
        """
        Run complete 10-point self-audit on article.

        Args:
            article_text: Full article text (title + body)
            verified_facts: JSON dict from topics.verified_facts
            source_plan: JSON dict from topics.source_plan
            reading_level: Calculated Flesch-Kincaid score

        Returns:
            AuditResult with pass/fail for each criterion
        """
        checklist = {}
        details = {}

        # 1. Factual Accuracy
        result, detail = self._check_factual_accuracy(article_text, verified_facts)
        checklist["factual_accuracy"] = result
        details["factual_accuracy"] = detail

        # 2. Source Attribution
        result, detail = self._check_source_attribution(article_text, source_plan)
        checklist["source_attribution"] = result
        details["source_attribution"] = detail

        # 3. Reading Level
        result, detail = self._check_reading_level(reading_level)
        checklist["reading_level"] = result
        details["reading_level"] = detail

        # 4. Worker-Centric Framing
        result, detail = self._check_worker_centric_framing(article_text)
        checklist["worker_centric_framing"] = result
        details["worker_centric_framing"] = detail

        # 5. No Hallucinations
        result, detail = self._check_no_hallucinations(article_text, verified_facts)
        checklist["no_hallucinations"] = result
        details["no_hallucinations"] = detail

        # 6. Proper Context
        result, detail = self._check_proper_context(article_text, verified_facts)
        checklist["proper_context"] = result
        details["proper_context"] = detail

        # 7. Active Voice
        result, detail = self._check_active_voice(article_text)
        checklist["active_voice"] = result
        details["active_voice"] = detail

        # 8. Specific Details
        result, detail = self._check_specific_details(article_text)
        checklist["specific_details"] = result
        details["specific_details"] = detail

        # 9. Balanced Representation
        result, detail = self._check_balanced_representation(article_text, verified_facts)
        checklist["balanced_representation"] = result
        details["balanced_representation"] = detail

        # 10. Editorial Standards
        result, detail = self._check_editorial_standards(article_text)
        checklist["editorial_standards"] = result
        details["editorial_standards"] = detail

        # Calculate pass rate
        passed_count = sum(1 for v in checklist.values() if v)
        score = (passed_count / len(checklist)) * 100
        all_passed = all(checklist.values())

        return AuditResult(
            passed=all_passed,
            checklist=checklist,
            details=details,
            score=score
        )

    def _check_factual_accuracy(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Check that all facts are sourced from verified_facts"""
        if not verified_facts or "facts" not in verified_facts:
            return False, "No verified facts available"

        facts = verified_facts.get("facts", [])
        high_confidence_facts = [
            f for f in facts
            if f.get("confidence") == "high"
        ]

        if not high_confidence_facts:
            return False, "No high-confidence facts available"

        # Check that article mentions key facts
        # Look for at least 50% of high-confidence facts mentioned
        mentioned_count = 0
        for fact in high_confidence_facts:
            fact_text = fact.get("fact", "").lower()
            if fact_text and any(word in article_text.lower() for word in fact_text.split()[:3]):
                mentioned_count += 1

        coverage = mentioned_count / len(high_confidence_facts) if high_confidence_facts else 0

        if coverage >= 0.5:
            return True, f"Good fact coverage: {mentioned_count}/{len(high_confidence_facts)} high-confidence facts"
        else:
            return False, f"Low fact coverage: only {mentioned_count}/{len(high_confidence_facts)} high-confidence facts mentioned"

    def _check_source_attribution(
        self,
        article_text: str,
        source_plan: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Check that claims are properly attributed using source_plan"""
        if not source_plan or "sources" not in source_plan:
            return False, "No source plan available"

        sources = source_plan.get("sources", [])
        primary_sources = [s for s in sources if s.get("tier") == "primary"]

        if not primary_sources:
            return False, "No primary sources in source plan"

        # Check that primary sources are cited
        cited_count = 0
        for source in primary_sources:
            source_name = source.get("name", "").lower()
            if source_name and source_name in article_text.lower():
                cited_count += 1

        if cited_count >= len(primary_sources) * 0.8:  # 80% of primary sources cited
            return True, f"Good attribution: {cited_count}/{len(primary_sources)} primary sources cited"
        else:
            return False, f"Weak attribution: only {cited_count}/{len(primary_sources)} primary sources cited"

    def _check_reading_level(self, reading_level: float) -> tuple[bool, str]:
        """Check reading level is between 7.5-8.5 Flesch-Kincaid"""
        if 7.5 <= reading_level <= 8.5:
            return True, f"Reading level {reading_level:.1f} within target range (7.5-8.5)"
        else:
            return False, f"Reading level {reading_level:.1f} outside target range (7.5-8.5)"

    def _check_worker_centric_framing(self, article_text: str) -> tuple[bool, str]:
        """Check for worker-centric perspective"""
        # Look for worker-related keywords
        worker_keywords = [
            "worker", "workers", "employee", "employees", "labor", "union",
            "wage", "wages", "job", "jobs", "workplace", "organizing"
        ]

        # Look for capital-biased framing to avoid
        capital_bias = [
            "labor costs", "efficiency gains", "shareholder value",
            "labor flexibility", "gig economy"
        ]

        text_lower = article_text.lower()
        worker_mentions = sum(1 for kw in worker_keywords if kw in text_lower)
        bias_mentions = sum(1 for phrase in capital_bias if phrase in text_lower)

        if worker_mentions >= 3 and bias_mentions == 0:
            return True, f"Strong worker-centric framing: {worker_mentions} worker keywords, no capital bias"
        elif worker_mentions >= 3:
            return False, f"Worker-centric but has capital bias: {bias_mentions} instances found"
        else:
            return False, f"Weak worker-centric framing: only {worker_mentions} worker keywords"

    def _check_no_hallucinations(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Check that information is traceable to source material"""
        # This is a basic check - look for unverified claims
        # In production, would use more sophisticated NLP

        # Check for unsupported superlatives or absolute claims
        suspicious_patterns = [
            r'\bfirst ever\b',
            r'\bunprecedented\b',
            r'\ball\b.*\bagree\b',
            r'\beveryone\b.*\bknows\b',
            r'\bobviously\b',
            r'\bclearly\b.*\bproves\b'
        ]

        found_issues = []
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                found_issues.append(pattern)

        if not found_issues:
            return True, "No hallucination indicators detected"
        else:
            return False, f"Potential hallucinations: {len(found_issues)} suspicious patterns found"

    def _check_proper_context(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Check that article includes relevant background context"""
        # Check for context indicators
        context_indicators = [
            "background", "context", "previously", "history", "earlier",
            "according to", "reported", "studies show", "data shows"
        ]

        text_lower = article_text.lower()
        context_count = sum(1 for indicator in context_indicators if indicator in text_lower)

        # Also check article length - short articles might lack context
        word_count = len(article_text.split())

        if context_count >= 2 and word_count >= 300:
            return True, f"Good context: {context_count} context indicators, {word_count} words"
        elif word_count < 300:
            return False, f"Article too short for proper context: {word_count} words"
        else:
            return False, f"Weak context: only {context_count} context indicators"

    def _check_active_voice(self, article_text: str) -> tuple[bool, str]:
        """Check for predominant use of active voice (80%+)"""
        sentences = re.split(r'[.!?]+', article_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Simple passive voice detection: look for "was/were/been + past participle"
        passive_patterns = [
            r'\b(was|were|been|being)\s+\w+ed\b',
            r'\b(is|are|am)\s+being\s+\w+ed\b'
        ]

        passive_count = 0
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_count += 1
                    break

        total_sentences = len(sentences)
        passive_percentage = (passive_count / total_sentences * 100) if total_sentences > 0 else 0
        active_percentage = 100 - passive_percentage

        if active_percentage >= 80:
            return True, f"Good active voice: {active_percentage:.0f}% active sentences"
        else:
            return False, f"Too much passive voice: only {active_percentage:.0f}% active sentences"

    def _check_specific_details(self, article_text: str) -> tuple[bool, str]:
        """Check for concrete numbers, dates, names"""
        # Look for numbers
        numbers = re.findall(r'\b\d+[,\d]*\.?\d*\b', article_text)

        # Look for dates
        date_patterns = [
            r'\b\d{4}\b',  # Year
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b',
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, article_text, re.IGNORECASE))

        # Look for proper names (capitalized words not at sentence start)
        sentences = re.split(r'[.!?]+', article_text)
        proper_names = []
        for sentence in sentences:
            words = sentence.split()
            for i, word in enumerate(words):
                if i > 0 and word and word[0].isupper() and len(word) > 1:
                    proper_names.append(word)

        if len(numbers) >= 3 and len(dates) >= 1 and len(proper_names) >= 3:
            return True, f"Good specificity: {len(numbers)} numbers, {len(dates)} dates, {len(proper_names)} names"
        else:
            return False, f"Lacks specificity: {len(numbers)} numbers, {len(dates)} dates, {len(proper_names)} names"

    def _check_balanced_representation(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Check that multiple perspectives are presented when available"""
        # Look for perspective indicators
        perspective_indicators = [
            "according to", "said", "stated", "claims", "argues",
            "on the other hand", "however", "meanwhile", "alternatively",
            "critics", "supporters", "opponents", "proponents"
        ]

        text_lower = article_text.lower()
        perspective_count = sum(1 for indicator in perspective_indicators if indicator in text_lower)

        # Check if verified_facts has multiple sources
        has_multiple_sources = False
        if verified_facts and "facts" in verified_facts:
            sources = set()
            for fact in verified_facts["facts"]:
                if "sources" in fact:
                    sources.update([s.get("name") for s in fact["sources"] if s.get("name")])
            has_multiple_sources = len(sources) >= 2

        if perspective_count >= 3 or has_multiple_sources:
            return True, f"Balanced representation: {perspective_count} perspective indicators"
        else:
            return False, f"Limited perspectives: only {perspective_count} perspective indicators"

    def _check_editorial_standards(self, article_text: str) -> tuple[bool, str]:
        """Check DWnews style: punchy, accurate, doesn't pull punches"""
        # Check for weak language that pulls punches
        weak_phrases = [
            "might", "maybe", "perhaps", "possibly", "could be",
            "seems to", "appears to", "allegedly"
        ]

        # Check for corporate euphemisms
        euphemisms = [
            "rightsizing", "downsizing", "restructuring",
            "let go", "transitioning out", "optimization"
        ]

        text_lower = article_text.lower()
        weak_count = sum(1 for phrase in weak_phrases if phrase in text_lower)
        euphemism_count = sum(1 for phrase in euphemisms if phrase in text_lower)

        # Check for direct, punchy language
        punchy_indicators = ["exposed", "revealed", "uncovered", "investigation", "found"]
        punchy_count = sum(1 for word in punchy_indicators if word in text_lower)

        # Good: punchy language, minimal weak language, no euphemisms
        if punchy_count >= 1 and weak_count <= 2 and euphemism_count == 0:
            return True, f"Meets editorial standards: punchy={punchy_count}, weak={weak_count}, euphemisms={euphemism_count}"
        else:
            return False, f"Weak editorial standards: punchy={punchy_count}, weak={weak_count}, euphemisms={euphemism_count}"
