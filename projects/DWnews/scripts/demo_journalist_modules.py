#!/usr/bin/env python3
"""
Demo Enhanced Journalist Agent Modules - No API Required
Tests individual modules with sample data
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent))

from backend.agents.journalist.self_audit import SelfAudit
from backend.agents.journalist.bias_detector import BiasDetector
from backend.agents.journalist.readability_checker import ReadabilityChecker
from backend.agents.journalist.attribution_engine import AttributionEngine


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_section(text: str):
    """Print formatted section"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)


# Sample article text
SAMPLE_ARTICLE = """
Amazon Warehouse Workers in NYC Launch Strike Over Safety Violations

Workers at Amazon's Staten Island warehouse walked off the job Monday morning,
citing dangerous working conditions and repeated safety violations. According to
the Amazon Labor Union, over 200 employees participated in the work stoppage.

The strike follows months of complaints about excessive heat, inadequate breaks,
and unsafe equipment. Workers reported temperatures inside the facility reaching
95 degrees during summer months, with limited access to water and rest areas.

"We've been raising these issues for over a year," said Sarah Martinez, a warehouse
associate and union organizer. "Management keeps promising improvements, but
nothing changes. Workers are getting injured and passing out from heat exhaustion."

Amazon spokesperson declined to comment on specific allegations but stated the
company "prioritizes worker safety and complies with all OSHA regulations."

OSHA records obtained by the union show 15 safety citations against the facility
in the past 18 months, including violations for blocked emergency exits and
inadequate ventilation systems.

Why This Matters

Safe working conditions are a fundamental right, not a privilege. When companies
prioritize profits over worker safety, employees suffer preventable injuries and
health problems. This strike demonstrates workers' collective power to demand
accountability from one of the world's largest employers.

What You Can Do

Support striking workers by avoiding Amazon purchases during the strike. Contact
your representatives to demand stronger OSHA enforcement and penalties for
repeat violators. Share this story to raise awareness about warehouse working
conditions.
"""

# Sample verified facts JSON
SAMPLE_VERIFIED_FACTS = {
    "facts": [
        {
            "fact": "Over 200 Amazon warehouse workers in Staten Island participated in a work stoppage on Monday",
            "type": "observed",
            "confidence": "high",
            "sources": [
                {"name": "Amazon Labor Union", "credibility": "high"}
            ]
        },
        {
            "fact": "Temperatures inside the facility reached 95 degrees during summer months",
            "type": "claimed",
            "confidence": "high",
            "sources": [
                {"name": "Amazon Labor Union", "credibility": "high"},
                {"name": "Worker testimony", "credibility": "medium"}
            ]
        },
        {
            "fact": "OSHA records show 15 safety citations in past 18 months",
            "type": "observed",
            "confidence": "high",
            "sources": [
                {"name": "OSHA Records", "credibility": "high"}
            ]
        }
    ],
    "conflicting_info": [],
    "verification_summary": "All key facts verified through credible sources"
}

# Sample source plan JSON
SAMPLE_SOURCE_PLAN = {
    "sources": [
        {
            "name": "Amazon Labor Union",
            "url": "https://amazonlaborunion.org",
            "tier": "primary",
            "credibility_tier": "high",
            "relevance": "Core source - strike organizers"
        },
        {
            "name": "OSHA Records",
            "url": "https://osha.gov",
            "tier": "primary",
            "credibility_tier": "high",
            "relevance": "Official safety violation records"
        },
        {
            "name": "Worker testimony",
            "tier": "supporting",
            "credibility_tier": "medium",
            "relevance": "First-hand accounts of conditions"
        }
    ],
    "attribution_strategy": "Primary sources (ALU, OSHA) cited prominently in lead. Worker quotes for first-hand perspective."
}


def demo_self_audit():
    """Demonstrate self-audit module"""
    print_header("Self-Audit Module Demo")

    audit = SelfAudit()

    print("\nRunning 10-point self-audit on sample article...")

    result = audit.audit_article(
        article_text=SAMPLE_ARTICLE,
        verified_facts=SAMPLE_VERIFIED_FACTS,
        source_plan=SAMPLE_SOURCE_PLAN,
        reading_level=8.0
    )

    print(f"\nOverall Result: {'PASS' if result.passed else 'FAIL'}")
    print(f"Score: {result.score:.0f}% ({sum(result.checklist.values())}/10 criteria passed)")

    print("\nDetailed Checklist:")
    for criterion, passed in result.checklist.items():
        status = "✓" if passed else "✗"
        detail = result.details.get(criterion, "")
        print(f"  {status} {criterion.replace('_', ' ').title()}")
        if detail:
            print(f"    → {detail}")


def demo_bias_detector():
    """Demonstrate bias detector module"""
    print_header("Bias Detector Module Demo")

    detector = BiasDetector()

    print("\nScanning article for bias, hallucinations, and propaganda...")

    report = detector.scan_article(
        article_text=SAMPLE_ARTICLE,
        verified_facts=SAMPLE_VERIFIED_FACTS,
        source_plan=SAMPLE_SOURCE_PLAN
    )

    print(f"\nOverall Score: {report.overall_score}")
    print(f"Hallucination Detected: {report.hallucination_detected}")
    print(f"Propaganda Flags: {len(report.propaganda_flags)}")
    print(f"Bias Indicators: {len(report.bias_indicators)}")
    print(f"Warnings: {len(report.warnings)}")

    if report.hallucination_details:
        print("\nHallucination Details:")
        for detail in report.hallucination_details:
            print(f"  - {detail}")

    if report.propaganda_flags:
        print("\nPropaganda Flags:")
        for flag in report.propaganda_flags:
            print(f"  - {flag}")

    if report.bias_indicators:
        print("\nBias Indicators:")
        for indicator in report.bias_indicators:
            print(f"  - {indicator}")

    if report.warnings:
        print("\nWarnings:")
        for warning in report.warnings:
            print(f"  - {warning}")


def demo_readability_checker():
    """Demonstrate readability checker module"""
    print_header("Readability Checker Module Demo")

    checker = ReadabilityChecker()

    print("\nCalculating Flesch-Kincaid Grade Level...")

    analysis = checker.analyze_article(SAMPLE_ARTICLE)

    print(f"\nReading Level: {analysis['score']:.1f}")
    print(f"Description: {analysis['description']}")
    print(f"Target Range: {analysis['target_range']}")
    print(f"Within Target: {analysis['within_target']}")

    if analysis['suggestion']:
        print(f"\nSuggestion: {analysis['suggestion']}")

    # Show calculation details
    print("\nCalculation Details:")
    print(f"  - Textstat library: {'Available' if checker.textstat_available else 'Not available (using manual calculation)'}")


def demo_attribution_engine():
    """Demonstrate attribution engine module"""
    print_header("Attribution Engine Module Demo")

    engine = AttributionEngine()

    print("\nGenerating attribution prompt for LLM...")

    prompt = engine.generate_attribution_prompt(
        topic_title="Amazon Warehouse Workers in NYC Launch Strike Over Safety Violations",
        verified_facts=SAMPLE_VERIFIED_FACTS,
        source_plan=SAMPLE_SOURCE_PLAN
    )

    print("\nGenerated Prompt (excerpt):")
    print("-" * 80)
    print(prompt[:800] + "...")
    print("-" * 80)

    print("\nValidating attribution coverage in sample article...")

    coverage = engine.validate_attribution_coverage(
        article_text=SAMPLE_ARTICLE,
        source_plan=SAMPLE_SOURCE_PLAN
    )

    print(f"\nAttribution Coverage:")
    print(f"  Total Primary Sources: {coverage['total_primary_sources']}")
    print(f"  Cited Sources: {len(coverage['cited_sources'])}")
    print(f"  Missing Sources: {len(coverage['missing_sources'])}")
    print(f"  Coverage: {coverage['coverage_percentage']:.0f}%")
    print(f"  Meets Standard: {'✓' if coverage['meets_standard'] else '✗'} (80% minimum)")

    if coverage['cited_sources']:
        print(f"\n  Cited: {', '.join(coverage['cited_sources'])}")

    if coverage['missing_sources']:
        print(f"  Missing: {', '.join(coverage['missing_sources'])}")


def demo_all_modules():
    """Run all module demos"""
    print_header("Enhanced Journalist Agent - Module Demonstration")
    print("\nThis demo tests all 4 journalist modules without requiring API access.")
    print("Using sample article about Amazon warehouse strike.")

    demo_self_audit()
    demo_bias_detector()
    demo_readability_checker()
    demo_attribution_engine()

    print_section("Demo Complete")
    print("\n✓ All modules demonstrated successfully")
    print("\nTo test with real database topics, run:")
    print("  python3 scripts/test_journalist.py")
    print("\nTo generate articles, ensure CLAUDE_API_KEY is set and run:")
    print("  python3 -m backend.agents.enhanced_journalist_agent <topic_id>")


if __name__ == "__main__":
    demo_all_modules()
