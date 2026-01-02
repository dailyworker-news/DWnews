"""
Bias Detection Module - Hallucination and Propaganda Detection
Scans articles for bias, hallucinations, and propaganda patterns
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class BiasReport:
    """Result of bias detection scan"""
    hallucination_detected: bool
    hallucination_details: List[str]
    propaganda_flags: List[str]
    bias_indicators: List[str]
    overall_score: str  # PASS, WARNING, FAIL
    warnings: List[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class BiasDetector:
    """
    Detects bias, hallucinations, and propaganda in articles.
    Implements worker-centric bias detection aligned with DWnews values.
    """

    # Corporate PR language that gets repeated uncritically
    CORPORATE_PR_PATTERNS = [
        r'\bsynergy\b',
        r'\blean\s+and\s+mean\b',
        r'\bright-?sizing\b',
        r'\boptimization\b',
        r'\bstreamlining\b',
        r'\befficiency\s+gains\b',
        r'\bmarket\s+forces\b',
        r'\bjob\s+creators\b',
        r'\btrickle\s+down\b',
    ]

    # Capital-biased framing patterns
    CAPITAL_BIAS_PATTERNS = [
        (r'\blabor\s+costs\b', 'worker wages'),
        (r'\bgig\s+economy\b', 'precarious labor'),
        (r'\bflexible\s+workforce\b', 'disposable workers'),
        (r'\bindependent\s+contractors\b', 'misclassified employees'),
        (r'\bsharing\s+economy\b', 'platform exploitation'),
    ]

    # Victim-blaming narratives
    VICTIM_BLAMING_PATTERNS = [
        r'should\s+have\s+known\s+better',
        r'failed\s+to\s+adapt',
        r'lack\s+of\s+skills',
        r'not\s+competitive\s+enough',
        r'unwilling\s+to\s+change',
    ]

    # Passive voice patterns that hide accountability
    ACCOUNTABILITY_HIDING_PATTERNS = [
        r'mistakes\s+were\s+made',
        r'jobs\s+were\s+lost',
        r'workers\s+were\s+laid\s+off',
        r'wages\s+were\s+cut',
        r'benefits\s+were\s+reduced',
    ]

    # Euphemisms for exploitation
    EXPLOITATION_EUPHEMISMS = [
        (r'\bwork-life\s+integration\b', 'always-on culture'),
        (r'\bon-demand\s+scheduling\b', 'unpredictable hours'),
        (r'\bperformance\s+management\b', 'surveillance'),
        (r'\bdynamic\s+pricing\b', 'price gouging'),
        (r'\bfurlough\b', 'unpaid suspension'),
    ]

    def __init__(self):
        """Initialize bias detector"""
        pass

    def scan_article(
        self,
        article_text: str,
        verified_facts: Dict[str, Any],
        source_plan: Dict[str, Any]
    ) -> BiasReport:
        """
        Run comprehensive bias detection scan on article.

        Args:
            article_text: Full article text
            verified_facts: Verified facts from verification agent
            source_plan: Source plan with attribution strategy

        Returns:
            BiasReport with detected issues
        """
        hallucination_details = []
        propaganda_flags = []
        bias_indicators = []
        warnings = []

        # 1. Hallucination Checks
        hallucinations = self._detect_hallucinations(article_text, verified_facts)
        hallucination_details.extend(hallucinations)

        # 2. Corporate PR Detection
        pr_language = self._detect_corporate_pr(article_text)
        if pr_language:
            propaganda_flags.extend(pr_language)

        # 3. Capital Bias Detection
        capital_bias = self._detect_capital_bias(article_text)
        if capital_bias:
            bias_indicators.extend(capital_bias)

        # 4. Victim Blaming Detection
        victim_blaming = self._detect_victim_blaming(article_text)
        if victim_blaming:
            propaganda_flags.extend(victim_blaming)

        # 5. Accountability Hiding Detection
        accountability_issues = self._detect_accountability_hiding(article_text)
        if accountability_issues:
            bias_indicators.extend(accountability_issues)

        # 6. Euphemism Detection
        euphemisms = self._detect_euphemisms(article_text)
        if euphemisms:
            bias_indicators.extend(euphemisms)

        # 7. Missing Worker Voices
        worker_voice_issues = self._detect_missing_worker_voices(article_text, verified_facts)
        if worker_voice_issues:
            warnings.extend(worker_voice_issues)

        # 8. False Balance Detection
        false_balance = self._detect_false_balance(article_text)
        if false_balance:
            propaganda_flags.extend(false_balance)

        # Determine overall score
        hallucination_detected = len(hallucination_details) > 0
        critical_issues = len(hallucination_details) + len(propaganda_flags)
        minor_issues = len(bias_indicators) + len(warnings)

        if hallucination_detected or critical_issues >= 3:
            overall_score = "FAIL"
        elif critical_issues > 0 or minor_issues >= 5:
            overall_score = "WARNING"
        else:
            overall_score = "PASS"

        return BiasReport(
            hallucination_detected=hallucination_detected,
            hallucination_details=hallucination_details,
            propaganda_flags=propaganda_flags,
            bias_indicators=bias_indicators,
            overall_score=overall_score,
            warnings=warnings,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def _detect_hallucinations(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> List[str]:
        """Detect claims not present in source material"""
        issues = []

        # Check for unverified numbers
        numbers_in_article = set(re.findall(r'\b\d+[,\d]*\.?\d*\b', article_text))

        numbers_in_facts = set()
        if verified_facts and "facts" in verified_facts:
            for fact in verified_facts["facts"]:
                fact_text = fact.get("fact", "")
                numbers_in_facts.update(re.findall(r'\b\d+[,\d]*\.?\d*\b', fact_text))

        unverified_numbers = numbers_in_article - numbers_in_facts
        if unverified_numbers and len(unverified_numbers) > 3:
            issues.append(f"Unverified numbers in article: {', '.join(list(unverified_numbers)[:5])}")

        # Check for invented quotes (quotes not in verified facts)
        quotes_in_article = re.findall(r'"([^"]+)"', article_text)
        if quotes_in_article:
            # Check if quotes appear in verified facts
            facts_text = json.dumps(verified_facts) if verified_facts else ""
            unverified_quotes = []
            for quote in quotes_in_article:
                if len(quote) > 20 and quote not in facts_text:  # Substantial quotes
                    unverified_quotes.append(quote[:50])

            if len(unverified_quotes) > 0:
                issues.append(f"Potentially invented quotes: {len(unverified_quotes)} quotes not found in verified facts")

        # Check for unsupported conclusions
        conclusion_patterns = [
            r'this\s+proves\s+that',
            r'clearly\s+demonstrates',
            r'undeniably\s+shows',
            r'definitively\s+establishes',
        ]

        for pattern in conclusion_patterns:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Unsupported strong conclusion: '{matches[0]}'")

        return issues

    def _detect_corporate_pr(self, article_text: str) -> List[str]:
        """Detect corporate PR language repeated uncritically"""
        issues = []

        for pattern in self.CORPORATE_PR_PATTERNS:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Corporate PR language: '{matches[0]}'")

        # Check for press release indicators
        pr_indicators = [
            'pleased to announce',
            'exciting opportunity',
            'thrilled to',
            'strategic partnership',
            'going forward',
        ]

        for indicator in pr_indicators:
            if indicator in article_text.lower():
                issues.append(f"Press release language: '{indicator}'")

        return issues

    def _detect_capital_bias(self, article_text: str) -> List[str]:
        """Detect capital-biased framing"""
        issues = []

        for pattern, alternative in self.CAPITAL_BIAS_PATTERNS:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Capital-biased framing: '{matches[0]}' (use '{alternative}' instead)")

        return issues

    def _detect_victim_blaming(self, article_text: str) -> List[str]:
        """Detect victim-blaming narratives"""
        issues = []

        for pattern in self.VICTIM_BLAMING_PATTERNS:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Victim-blaming narrative: '{matches[0]}'")

        return issues

    def _detect_accountability_hiding(self, article_text: str) -> List[str]:
        """Detect passive voice hiding accountability"""
        issues = []

        for pattern in self.ACCOUNTABILITY_HIDING_PATTERNS:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Passive voice hiding accountability: '{matches[0]}'")

        return issues

    def _detect_euphemisms(self, article_text: str) -> List[str]:
        """Detect euphemisms for exploitation"""
        issues = []

        for pattern, reality in self.EXPLOITATION_EUPHEMISMS:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Euphemism for exploitation: '{matches[0]}' (actually: {reality})")

        return issues

    def _detect_missing_worker_voices(
        self,
        article_text: str,
        verified_facts: Dict[str, Any]
    ) -> List[str]:
        """Detect missing worker perspectives when available"""
        warnings = []

        # Check if verified facts contain worker quotes/perspectives
        has_worker_perspective_in_facts = False
        if verified_facts and "facts" in verified_facts:
            for fact in verified_facts["facts"]:
                fact_text = fact.get("fact", "").lower()
                if any(word in fact_text for word in ["worker", "employee", "union", "labor"]):
                    has_worker_perspective_in_facts = True
                    break

        # Check if article includes worker voices
        has_worker_voice_in_article = bool(
            re.search(r'(worker|employee|union\s+member).+said', article_text, re.IGNORECASE)
        )

        if has_worker_perspective_in_facts and not has_worker_voice_in_article:
            warnings.append("Worker voices available in sources but not quoted in article")

        return warnings

    def _detect_false_balance(self, article_text: str) -> List[str]:
        """Detect false balance (equating worker complaints with employer denials)"""
        issues = []

        # Pattern: workers say X, but company says Y (giving equal weight)
        false_balance_patterns = [
            r'(workers?\s+claim.+but\s+company\s+says)',
            r'(employees?\s+allege.+but\s+management\s+denies)',
            r'(union\s+argues.+but\s+employer\s+maintains)',
        ]

        for pattern in false_balance_patterns:
            matches = re.findall(pattern, article_text, re.IGNORECASE)
            if matches:
                issues.append(f"Potential false balance: equating worker complaints with employer denials")

        # Check for "both sides" language
        if re.search(r'both\s+sides|on\s+the\s+other\s+hand', article_text, re.IGNORECASE):
            # This is only false balance if it's worker vs. employer
            if re.search(r'(worker|employee|union).+(employer|company|management)', article_text, re.IGNORECASE):
                issues.append("Potential false balance: 'both sides' framing on labor dispute")

        return issues
