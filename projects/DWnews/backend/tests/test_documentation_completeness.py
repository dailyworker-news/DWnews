"""
The Daily Worker - Documentation Completeness Tests

Tests to validate that all required documentation exists and contains
necessary sections for Phase 6.11.5.

Written FIRST following TDD principles.
"""

import pytest
import os
from pathlib import Path


class TestDocumentationCompleteness:
    """Test suite for validating documentation completeness"""

    @pytest.fixture
    def docs_root(self):
        """Get the documentation root directory"""
        # Assuming tests are in backend/tests/
        return Path(__file__).parent.parent.parent

    def test_gemini_setup_guide_exists(self, docs_root):
        """Test that GEMINI_IMAGE_SETUP.md exists"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        assert setup_guide.exists(), "GEMINI_IMAGE_SETUP.md must exist"

    def test_gemini_setup_guide_has_required_sections(self, docs_root):
        """Test that setup guide contains all required sections"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        required_sections = [
            "## Prerequisites",
            "## Step 1: Get Google Gemini API Key",
            "## Step 2: Get Anthropic Claude API Key",
            "## Step 3: Configure DWnews Environment Variables",
            "## Step 4: Install Required Python Libraries",
            "## Step 5: Test the Image Generation Workflow",
            "## How the Two-Step Workflow Works",
            "## Pricing Information",
            "## Troubleshooting",
        ]

        for section in required_sections:
            assert section in content, f"Setup guide must contain '{section}' section"

    def test_gemini_setup_guide_documents_claude_workflow(self, docs_root):
        """Test that setup guide documents Claude prompt enhancement"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        required_keywords = [
            "Claude Sonnet",
            "prompt enhancement",
            "artistic concept",
            "confidence",
            "3-5 artistic concepts",
        ]

        for keyword in required_keywords:
            assert keyword.lower() in content.lower(), \
                f"Setup guide must document '{keyword}'"

    def test_gemini_setup_guide_includes_cost_information(self, docs_root):
        """Test that setup guide includes pricing/cost information"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        cost_keywords = [
            "cost",
            "pricing",
            "free tier",
            "per image",
        ]

        found_cost_info = any(keyword in content.lower() for keyword in cost_keywords)
        assert found_cost_info, "Setup guide must include cost/pricing information"

    def test_gemini_setup_guide_includes_troubleshooting(self, docs_root):
        """Test that setup guide includes troubleshooting section"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        troubleshooting_items = [
            "GEMINI_API_KEY not configured",
            "CLAUDE_API_KEY not configured",
            "Failed to enhance prompt",
            "Poor image quality",
        ]

        for item in troubleshooting_items:
            assert item in content, \
                f"Troubleshooting section must address '{item}'"

    def test_api_specs_documentation_exists(self, docs_root):
        """Test that technical API specs documentation exists"""
        api_specs = docs_root / "docs" / "GEMINI_IMAGE_API_SPECS.md"
        assert api_specs.exists(), "GEMINI_IMAGE_API_SPECS.md must exist"

    def test_api_specs_has_technical_details(self, docs_root):
        """Test that API specs contain technical implementation details"""
        api_specs = docs_root / "docs" / "GEMINI_IMAGE_API_SPECS.md"
        content = api_specs.read_text()

        required_sections = [
            "## Request Format",
            "## Response Format",
            "## Error Handling",
            "## Performance Characteristics",
            "## Security & Safety",
        ]

        for section in required_sections:
            assert section in content, f"API specs must contain '{section}' section"

    def test_image_quality_standards_guide_exists(self, docs_root):
        """Test that image quality standards guide exists for editors"""
        quality_guide = docs_root / "docs" / "IMAGE_QUALITY_STANDARDS.md"
        assert quality_guide.exists(), \
            "IMAGE_QUALITY_STANDARDS.md must exist for editorial team"

    def test_image_quality_standards_has_required_sections(self, docs_root):
        """Test that quality standards guide contains required sections"""
        quality_guide = docs_root / "docs" / "IMAGE_QUALITY_STANDARDS.md"
        content = quality_guide.read_text()

        required_sections = [
            "## Overview",
            "## Quality Criteria",
            "## Category-Specific Guidelines",
            "## Acceptance Criteria",
            "## Rejection Criteria",
            "## Examples",
        ]

        for section in required_sections:
            assert section in content, \
                f"Quality guide must contain '{section}' section"

    def test_image_quality_standards_covers_all_categories(self, docs_root):
        """Test that quality guide covers diverse article categories"""
        quality_guide = docs_root / "docs" / "IMAGE_QUALITY_STANDARDS.md"
        content = quality_guide.read_text()

        categories = [
            "Labor",
            "Politics",
            "Sports",
            "Culture",
            "International",
        ]

        for category in categories:
            assert category in content, \
                f"Quality guide must include guidelines for '{category}' category"

    def test_performance_metrics_documented(self, docs_root):
        """Test that performance metrics are documented"""
        # Check in either setup guide or separate metrics doc
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        metrics_doc = docs_root / "docs" / "IMAGE_GENERATION_METRICS.md"

        setup_content = setup_guide.read_text()
        metrics_content = metrics_doc.read_text() if metrics_doc.exists() else ""

        combined_content = setup_content + metrics_content

        performance_keywords = [
            "generation time",
            "latency",
            "response time",
            "seconds",
        ]

        found_metrics = any(keyword in combined_content.lower()
                          for keyword in performance_keywords)
        assert found_metrics, "Performance metrics must be documented"

    def test_cost_analysis_documented(self, docs_root):
        """Test that cost analysis is documented"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        cost_elements = [
            "per image",
            "Gemini",
            "Claude",
            "month",
        ]

        for element in cost_elements:
            assert element in content, \
                f"Cost analysis must include '{element}'"

    def test_example_prompts_documented(self, docs_root):
        """Test that example prompts and concepts are documented"""
        setup_guide = docs_root / "GEMINI_IMAGE_SETUP.md"
        content = setup_guide.read_text()

        # Should have example enhanced prompts
        assert "Concept 1" in content or "Example:" in content, \
            "Documentation must include example prompts"

        # Should show Claude enhancement workflow
        assert "Documentary-style photograph" in content or \
               "Photorealistic" in content or \
               "Editorial illustration" in content, \
            "Documentation must show example enhanced prompts"

    def test_agent_instructions_updated(self, docs_root):
        """Test that agent instruction files exist and mention image generation"""
        # Look for agent instruction files
        agent_files = [
            ".claude/agents/journalist.md",
            ".claude/agents/editorial-coordinator.md",
        ]

        for agent_file in agent_files:
            agent_path = docs_root.parent / agent_file
            if agent_path.exists():
                content = agent_path.read_text()
                # Should mention image generation workflow
                assert "image" in content.lower(), \
                    f"{agent_file} should reference image generation"

    def test_migration_guide_exists(self, docs_root):
        """Test that migration guide from old system exists"""
        migration_guide = docs_root / "docs" / "IMAGEN_TO_GEMINI_MIGRATION.md"
        assert migration_guide.exists(), \
            "Migration guide from Vertex AI Imagen to Gemini must exist"

    def test_all_documentation_uses_consistent_terminology(self, docs_root):
        """Test that all docs use consistent terminology"""
        docs_to_check = [
            docs_root / "GEMINI_IMAGE_SETUP.md",
            docs_root / "docs" / "GEMINI_IMAGE_API_SPECS.md",
        ]

        # Ensure consistent model naming
        for doc_path in docs_to_check:
            if doc_path.exists():
                content = doc_path.read_text()
                # Should use consistent model name
                if "gemini" in content.lower():
                    assert "gemini-2.5-flash-image" in content.lower() or \
                           "Gemini 2.5 Flash Image" in content, \
                        f"{doc_path.name} should use consistent model name"
