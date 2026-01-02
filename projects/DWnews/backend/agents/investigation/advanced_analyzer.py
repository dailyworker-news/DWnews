"""
Advanced Analysis Module for Investigatory Journalist Agent - Phase 6.9.4

Provides sophisticated claim analysis and fact-checking:
- Claim extraction using LLM (identify verifiable factual claims)
- Automated fact-checking per claim (search for evidence)
- Contradiction detection (flag conflicting information)
- Bias analysis of sources (detect political/corporate bias)
- Confidence scoring for recommendations (0-100 scale)
- Human review flagging system (contradictions, serious allegations)

This is the final analysis layer before making verification upgrade recommendations.
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class ClaimType(Enum):
    """Type of factual claim."""
    STATISTIC = "statistic"  # Numerical claim (e.g., "500 workers")
    EVENT = "event"  # Event occurred (e.g., "strike happened")
    QUOTE = "quote"  # Someone said something
    ATTRIBUTION = "attribution"  # Who did what
    TIMING = "timing"  # When something happened
    LOCATION = "location"  # Where something happened
    OUTCOME = "outcome"  # Result of action


class VerificationStatus(Enum):
    """Status of claim verification."""
    VERIFIED = "verified"  # Confirmed by multiple sources
    PARTIALLY_VERIFIED = "partially_verified"  # Some supporting evidence
    UNVERIFIED = "unverified"  # No evidence found
    DISPUTED = "disputed"  # Contradictory evidence
    DEBUNKED = "debunked"  # Proven false


class BiasType(Enum):
    """Type of source bias."""
    PRO_LABOR = "pro_labor"
    PRO_MANAGEMENT = "pro_management"
    POLITICAL_LEFT = "political_left"
    POLITICAL_RIGHT = "political_right"
    CORPORATE = "corporate"
    NEUTRAL = "neutral"


@dataclass
class Claim:
    """Extracted factual claim."""

    claim_text: str
    claim_type: ClaimType
    source: str  # Where claim came from

    # Verification
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)

    # Analysis
    confidence_score: float = 0.0  # 0-100, confidence in claim accuracy
    fact_check_notes: str = ""

    # Flags
    requires_human_review: bool = False
    review_reason: Optional[str] = None


@dataclass
class Contradiction:
    """Detected contradiction between sources."""

    claim_a: str
    claim_b: str
    source_a: str
    source_b: str

    contradiction_type: str  # 'factual', 'timing', 'attribution', 'interpretation'
    severity: str  # 'critical', 'moderate', 'minor'

    resolution_suggestion: Optional[str] = None
    requires_investigation: bool = True


@dataclass
class BiasAnalysis:
    """Bias analysis for a source."""

    source_name: str
    source_url: str

    detected_biases: List[BiasType] = field(default_factory=list)
    bias_indicators: List[str] = field(default_factory=list)  # What indicated bias

    # Scoring
    objectivity_score: float = 0.0  # 0-100, higher = more objective
    reliability_score: float = 0.0  # 0-100, based on track record

    # Recommendations
    use_with_caution: bool = False
    caution_reason: Optional[str] = None


@dataclass
class AdvancedAnalysisResult:
    """Complete advanced analysis results."""

    topic_title: str
    analysis_date: datetime

    # Claim analysis
    extracted_claims: List[Claim]
    verified_claims: List[Claim] = field(default_factory=list)
    disputed_claims: List[Claim] = field(default_factory=list)

    # Contradictions
    contradictions: List[Contradiction] = field(default_factory=list)
    critical_contradictions: List[Contradiction] = field(default_factory=list)

    # Bias analysis
    source_biases: List[BiasAnalysis] = field(default_factory=list)
    overall_bias_assessment: str = "unknown"

    # Confidence and recommendations
    overall_confidence: float = 0.0  # 0-100
    verification_recommendation: str = "unverified"  # unverified/verified/certified
    recommendation_rationale: str = ""

    # Human review flags
    requires_human_review: bool = False
    review_reasons: List[str] = field(default_factory=list)
    high_risk_factors: List[str] = field(default_factory=list)


class AdvancedAnalyzer:
    """
    Advanced analysis for investigatory journalism.

    Provides:
    - LLM-based claim extraction
    - Automated fact-checking per claim
    - Contradiction detection across sources
    - Source bias analysis
    - Confidence scoring
    - Human review flagging
    """

    def __init__(self, use_mock_data: bool = False):
        """
        Initialize advanced analyzer.

        Args:
            use_mock_data: If True, use mock data for testing
        """
        self.use_mock_data = use_mock_data

    def analyze(
        self,
        topic_title: str,
        topic_description: str,
        sources: List[Dict],
        investigation_findings: Optional[Dict] = None
    ) -> AdvancedAnalysisResult:
        """
        Conduct advanced analysis on topic and sources.

        Args:
            topic_title: Title of the topic
            topic_description: Description of the topic
            sources: List of source dictionaries
            investigation_findings: Optional findings from previous investigation steps

        Returns:
            AdvancedAnalysisResult with all analysis
        """
        logger.info(f"Starting advanced analysis: {topic_title}")
        logger.info(f"Analyzing {len(sources)} sources")

        # 1. Extract claims from topic description and sources
        claims = self._extract_claims(topic_description, sources)
        logger.info(f"Extracted {len(claims)} claims")

        # 2. Fact-check each claim
        for claim in claims:
            self._fact_check_claim(claim, sources)

        verified_claims = [c for c in claims if c.verification_status == VerificationStatus.VERIFIED]
        disputed_claims = [c for c in claims if c.verification_status == VerificationStatus.DISPUTED]
        logger.info(f"Verified {len(verified_claims)} claims, {len(disputed_claims)} disputed")

        # 3. Detect contradictions
        contradictions = self._detect_contradictions(claims, sources)
        critical_contradictions = [c for c in contradictions if c.severity == 'critical']
        logger.info(f"Found {len(contradictions)} contradictions ({len(critical_contradictions)} critical)")

        # 4. Analyze source bias
        source_biases = self._analyze_source_bias(sources)
        logger.info(f"Analyzed bias for {len(source_biases)} sources")

        # 5. Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            claims,
            verified_claims,
            disputed_claims,
            contradictions,
            source_biases
        )
        logger.info(f"Overall confidence: {overall_confidence:.1f}/100")

        # 6. Make verification recommendation
        recommendation, rationale = self._make_recommendation(
            overall_confidence,
            verified_claims,
            critical_contradictions,
            source_biases
        )
        logger.info(f"Recommendation: {recommendation}")

        # 7. Flag for human review if needed
        requires_review, review_reasons, risk_factors = self._evaluate_human_review_need(
            claims,
            contradictions,
            source_biases,
            overall_confidence
        )

        if requires_review:
            logger.warning(f"Flagged for human review: {', '.join(review_reasons)}")

        # Assess overall bias
        overall_bias = self._assess_overall_bias(source_biases)

        result = AdvancedAnalysisResult(
            topic_title=topic_title,
            analysis_date=datetime.utcnow(),
            extracted_claims=claims,
            verified_claims=verified_claims,
            disputed_claims=disputed_claims,
            contradictions=contradictions,
            critical_contradictions=critical_contradictions,
            source_biases=source_biases,
            overall_bias_assessment=overall_bias,
            overall_confidence=overall_confidence,
            verification_recommendation=recommendation,
            recommendation_rationale=rationale,
            requires_human_review=requires_review,
            review_reasons=review_reasons,
            high_risk_factors=risk_factors
        )

        logger.info(f"Advanced analysis complete")

        return result

    def _extract_claims(
        self,
        description: str,
        sources: List[Dict]
    ) -> List[Claim]:
        """
        Extract verifiable factual claims from description and sources.

        In production, this would use an LLM to identify claims.
        For now, use simple heuristics.
        """
        claims = []

        # Extract from description
        desc_claims = self._parse_claims_from_text(description, "topic_description")
        claims.extend(desc_claims)

        # Extract from sources
        for source in sources[:5]:  # Limit to first 5 sources
            source_text = source.get('snippet', '') or source.get('content', '')
            source_url = source.get('url', 'unknown')
            source_claims = self._parse_claims_from_text(source_text, source_url)
            claims.extend(source_claims)

        return claims

    def _parse_claims_from_text(self, text: str, source: str) -> List[Claim]:
        """Parse claims from text using heuristics."""

        if self.use_mock_data:
            return self._generate_mock_claims(text, source)

        claims = []
        sentences = text.split('.')

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Look for statistical claims
            if any(word in sentence.lower() for word in ['percent', '%', 'workers', 'people', 'dollars', '$']):
                claims.append(Claim(
                    claim_text=sentence,
                    claim_type=ClaimType.STATISTIC,
                    source=source
                ))

            # Look for event claims
            elif any(word in sentence.lower() for word in ['strike', 'vote', 'authorize', 'walk out', 'protest']):
                claims.append(Claim(
                    claim_text=sentence,
                    claim_type=ClaimType.EVENT,
                    source=source
                ))

            # Look for quotes
            elif '"' in sentence or '\'' in sentence:
                claims.append(Claim(
                    claim_text=sentence,
                    claim_type=ClaimType.QUOTE,
                    source=source
                ))

        return claims[:10]  # Limit claims per source

    def _fact_check_claim(self, claim: Claim, sources: List[Dict]):
        """
        Fact-check a single claim against available sources.

        In production, this would search for corroborating evidence.
        For now, use simple matching.
        """
        supporting_count = 0
        contradicting_count = 0

        claim_lower = claim.claim_text.lower()

        for source in sources:
            source_text = (source.get('snippet', '') or source.get('content', '')).lower()

            # Very simple matching
            if any(word in source_text for word in claim_lower.split() if len(word) > 4):
                supporting_count += 1
                claim.supporting_evidence.append(source.get('url', 'unknown'))

        # Determine verification status based on supporting evidence
        if supporting_count >= 3:
            claim.verification_status = VerificationStatus.VERIFIED
            claim.confidence_score = min(80.0 + (supporting_count * 5), 100.0)
        elif supporting_count >= 1:
            claim.verification_status = VerificationStatus.PARTIALLY_VERIFIED
            claim.confidence_score = 50.0 + (supporting_count * 10)
        else:
            claim.verification_status = VerificationStatus.UNVERIFIED
            claim.confidence_score = 20.0

        claim.fact_check_notes = f"Found {supporting_count} supporting sources"

    def _detect_contradictions(
        self,
        claims: List[Claim],
        sources: List[Dict]
    ) -> List[Contradiction]:
        """Detect contradictions between claims."""

        contradictions = []

        # Compare claims pairwise
        for i, claim_a in enumerate(claims):
            for claim_b in claims[i+1:]:
                # Check for contradictory claims
                if self._claims_contradict(claim_a, claim_b):
                    severity = self._assess_contradiction_severity(claim_a, claim_b)

                    contradiction = Contradiction(
                        claim_a=claim_a.claim_text,
                        claim_b=claim_b.claim_text,
                        source_a=claim_a.source,
                        source_b=claim_b.source,
                        contradiction_type='factual',
                        severity=severity,
                        resolution_suggestion="Verify with primary sources or official records",
                        requires_investigation=True
                    )

                    contradictions.append(contradiction)

        return contradictions

    def _claims_contradict(self, claim_a: Claim, claim_b: Claim) -> bool:
        """Check if two claims contradict each other."""

        # Simple heuristic: Look for opposite terms
        contradiction_pairs = [
            ('approved', 'rejected'),
            ('won', 'lost'),
            ('success', 'failure'),
            ('increased', 'decreased'),
            ('majority', 'minority')
        ]

        text_a = claim_a.claim_text.lower()
        text_b = claim_b.claim_text.lower()

        for term1, term2 in contradiction_pairs:
            if (term1 in text_a and term2 in text_b) or (term2 in text_a and term1 in text_b):
                return True

        return False

    def _assess_contradiction_severity(self, claim_a: Claim, claim_b: Claim) -> str:
        """Assess severity of contradiction."""

        # Critical: Statistical contradictions, event contradictions
        if claim_a.claim_type == ClaimType.STATISTIC or claim_a.claim_type == ClaimType.EVENT:
            return 'critical'

        # Moderate: Attribution, timing contradictions
        if claim_a.claim_type in [ClaimType.ATTRIBUTION, ClaimType.TIMING]:
            return 'moderate'

        # Minor: Quote differences, interpretations
        return 'minor'

    def _analyze_source_bias(self, sources: List[Dict]) -> List[BiasAnalysis]:
        """Analyze bias for each source."""

        biases = []

        for source in sources:
            source_name = source.get('name', 'Unknown')
            source_url = source.get('url', '')
            source_text = (source.get('snippet', '') or source.get('content', '')).lower()

            detected_biases = []
            bias_indicators = []

            # Look for bias indicators in text
            if any(term in source_text for term in ['union', 'workers rights', 'solidarity', 'organizing']):
                detected_biases.append(BiasType.PRO_LABOR)
                bias_indicators.append("Pro-labor language")

            if any(term in source_text for term in ['business', 'employer', 'management', 'productivity']):
                detected_biases.append(BiasType.PRO_MANAGEMENT)
                bias_indicators.append("Pro-management language")

            if any(term in source_text for term in ['corporate', 'shareholders', 'profit']):
                detected_biases.append(BiasType.CORPORATE)
                bias_indicators.append("Corporate perspective")

            # Calculate objectivity score (higher = more objective)
            objectivity = 70.0
            if len(detected_biases) == 0:
                objectivity = 90.0
            elif len(detected_biases) == 1:
                objectivity = 70.0
            else:
                objectivity = 50.0

            # Reliability based on source type
            reliability = 75.0  # Default
            if 'reuters' in source_url or 'ap.org' in source_url or 'propublica' in source_url:
                reliability = 95.0
            elif 'blog' in source_url:
                reliability = 50.0

            # Flag if using with caution
            use_caution = len(detected_biases) > 1 or reliability < 60.0
            caution_reason = None
            if use_caution:
                if len(detected_biases) > 1:
                    caution_reason = "Multiple bias indicators detected"
                else:
                    caution_reason = "Lower reliability source"

            bias = BiasAnalysis(
                source_name=source_name,
                source_url=source_url,
                detected_biases=detected_biases if detected_biases else [BiasType.NEUTRAL],
                bias_indicators=bias_indicators or ["No strong bias indicators"],
                objectivity_score=objectivity,
                reliability_score=reliability,
                use_with_caution=use_caution,
                caution_reason=caution_reason
            )

            biases.append(bias)

        return biases

    def _calculate_overall_confidence(
        self,
        all_claims: List[Claim],
        verified_claims: List[Claim],
        disputed_claims: List[Claim],
        contradictions: List[Contradiction],
        source_biases: List[BiasAnalysis]
    ) -> float:
        """Calculate overall confidence score (0-100)."""

        if not all_claims:
            return 0.0

        score = 0.0

        # Verified claims (0-40 points)
        verification_ratio = len(verified_claims) / len(all_claims)
        score += verification_ratio * 40

        # Disputed claims penalty (0-20 points deduction)
        dispute_ratio = len(disputed_claims) / len(all_claims)
        score -= dispute_ratio * 20

        # Contradictions penalty (0-15 points deduction)
        critical_contradictions = [c for c in contradictions if c.severity == 'critical']
        if critical_contradictions:
            score -= min(len(critical_contradictions) * 5, 15)

        # Source reliability (0-25 points)
        if source_biases:
            avg_reliability = sum(b.reliability_score for b in source_biases) / len(source_biases)
            score += (avg_reliability / 100) * 25

        # Source objectivity (0-15 points)
        if source_biases:
            avg_objectivity = sum(b.objectivity_score for b in source_biases) / len(source_biases)
            score += (avg_objectivity / 100) * 15

        return max(0.0, min(score, 100.0))

    def _make_recommendation(
        self,
        confidence: float,
        verified_claims: List[Claim],
        critical_contradictions: List[Contradiction],
        source_biases: List[BiasAnalysis]
    ) -> Tuple[str, str]:
        """Make verification recommendation based on analysis."""

        # Critical contradictions = unverified
        if critical_contradictions:
            return "unverified", f"Critical contradictions detected: {len(critical_contradictions)} unresolved conflicts"

        # High confidence = certified
        if confidence >= 80 and len(verified_claims) >= 5:
            return "certified", f"High confidence ({confidence:.1f}/100) with {len(verified_claims)} verified claims"

        # Medium confidence = verified
        if confidence >= 50 and len(verified_claims) >= 3:
            return "verified", f"Moderate confidence ({confidence:.1f}/100) with {len(verified_claims)} verified claims"

        # Low confidence = unverified
        return "unverified", f"Insufficient confidence ({confidence:.1f}/100) with only {len(verified_claims)} verified claims"

    def _evaluate_human_review_need(
        self,
        claims: List[Claim],
        contradictions: List[Contradiction],
        source_biases: List[BiasAnalysis],
        confidence: float
    ) -> Tuple[bool, List[str], List[str]]:
        """Evaluate if human review is needed."""

        requires_review = False
        reasons = []
        risk_factors = []

        # Critical contradictions require review
        critical_contradictions = [c for c in contradictions if c.severity == 'critical']
        if critical_contradictions:
            requires_review = True
            reasons.append(f"{len(critical_contradictions)} critical contradictions detected")
            risk_factors.append("Factual conflicts")

        # Low confidence requires review
        if confidence < 40:
            requires_review = True
            reasons.append(f"Low confidence score: {confidence:.1f}/100")
            risk_factors.append("Insufficient verification")

        # Serious allegations require review
        serious_terms = ['fired', 'illegal', 'violation', 'lawsuit', 'criminal']
        for claim in claims:
            if any(term in claim.claim_text.lower() for term in serious_terms):
                if claim.verification_status != VerificationStatus.VERIFIED:
                    requires_review = True
                    reasons.append("Serious allegations require verification")
                    risk_factors.append("Legal/ethical implications")
                    break

        # High bias sources require review
        high_bias_sources = [b for b in source_biases if b.use_with_caution]
        if len(high_bias_sources) > len(source_biases) * 0.5:
            requires_review = True
            reasons.append("Majority of sources have bias concerns")
            risk_factors.append("Source reliability issues")

        return requires_review, reasons, risk_factors

    def _assess_overall_bias(self, source_biases: List[BiasAnalysis]) -> str:
        """Assess overall bias across all sources."""

        if not source_biases:
            return "unknown"

        bias_counts = {}
        for bias_analysis in source_biases:
            for bias in bias_analysis.detected_biases:
                bias_counts[bias] = bias_counts.get(bias, 0) + 1

        # If mostly neutral, return balanced
        if bias_counts.get(BiasType.NEUTRAL, 0) > len(source_biases) * 0.7:
            return "balanced"

        # If single bias dominates
        max_bias = max(bias_counts.items(), key=lambda x: x[1]) if bias_counts else None
        if max_bias and max_bias[1] > len(source_biases) * 0.6:
            return f"skewed_{max_bias[0].value}"

        # Mixed biases
        return "mixed"

    def _generate_mock_claims(self, text: str, source: str) -> List[Claim]:
        """Generate mock claims for testing."""

        return [
            Claim(
                claim_text="500 workers voted to authorize strike action",
                claim_type=ClaimType.STATISTIC,
                source=source
            ),
            Claim(
                claim_text="Strike authorization vote took place on January 15, 2026",
                claim_type=ClaimType.EVENT,
                source=source
            ),
            Claim(
                claim_text="Union representative said 'Workers are united in their demands'",
                claim_type=ClaimType.QUOTE,
                source=source
            )
        ]


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    analyzer = AdvancedAnalyzer(use_mock_data=True)

    # Mock sources
    sources = [
        {
            'name': 'Reuters',
            'url': 'https://reuters.com/article/123',
            'snippet': '500 workers at the facility voted 75% in favor of strike authorization',
            'content': '500 workers voted to authorize strike. The vote passed with 75% support.'
        },
        {
            'name': 'Company Blog',
            'url': 'https://company.com/blog/456',
            'snippet': 'Management disappointed by vote. Company offers competitive wages.',
            'content': 'The company is disappointed by the union vote. We believe our wages and benefits are competitive.'
        },
        {
            'name': 'Labor News',
            'url': 'https://labornews.org/789',
            'snippet': 'Workers demand better conditions and union recognition',
            'content': 'Workers are fighting for better working conditions, higher wages, and union recognition.'
        }
    ]

    result = analyzer.analyze(
        topic_title="Warehouse Workers Authorize Strike",
        topic_description="Workers at a major distribution facility vote to authorize strike action over wages and working conditions",
        sources=sources
    )

    print(f"\n=== Advanced Analysis Results ===")
    print(f"Overall Confidence: {result.overall_confidence:.1f}/100")
    print(f"Recommendation: {result.verification_recommendation}")
    print(f"Rationale: {result.recommendation_rationale}")

    print(f"\n=== Claims Analysis ===")
    print(f"Total claims: {len(result.extracted_claims)}")
    print(f"Verified claims: {len(result.verified_claims)}")
    print(f"Disputed claims: {len(result.disputed_claims)}")

    for claim in result.verified_claims[:3]:
        print(f"\n  ✓ {claim.claim_text}")
        print(f"    Confidence: {claim.confidence_score:.1f}/100")
        print(f"    Evidence: {len(claim.supporting_evidence)} sources")

    print(f"\n=== Contradictions ===")
    print(f"Total: {len(result.contradictions)}")
    print(f"Critical: {len(result.critical_contradictions)}")

    for contradiction in result.critical_contradictions:
        print(f"\n  ⚠ {contradiction.contradiction_type} ({contradiction.severity})")
        print(f"    Claim A: {contradiction.claim_a}")
        print(f"    Claim B: {contradiction.claim_b}")

    print(f"\n=== Source Bias Analysis ===")
    print(f"Overall bias: {result.overall_bias_assessment}")

    for bias in result.source_biases:
        print(f"\n  Source: {bias.source_name}")
        print(f"  Objectivity: {bias.objectivity_score:.1f}/100")
        print(f"  Reliability: {bias.reliability_score:.1f}/100")
        print(f"  Biases: {[b.value for b in bias.detected_biases]}")
        if bias.use_with_caution:
            print(f"  ⚠ Caution: {bias.caution_reason}")

    print(f"\n=== Human Review ===")
    print(f"Requires review: {result.requires_human_review}")
    if result.requires_human_review:
        print(f"Reasons:")
        for reason in result.review_reasons:
            print(f"  - {reason}")
        print(f"Risk factors:")
        for factor in result.high_risk_factors:
            print(f"  - {factor}")
