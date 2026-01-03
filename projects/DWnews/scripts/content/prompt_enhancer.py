#!/usr/bin/env python3
"""
The Daily Worker - Image Prompt Enhancement Service
Uses Claude Sonnet to generate detailed artistic image prompts
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from anthropic import Anthropic

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)


class PromptEnhancer:
    """Generate detailed artistic image prompts using Claude Sonnet"""

    def __init__(self):
        """Initialize Claude client"""
        if not settings.claude_api_key:
            raise ValueError("CLAUDE_API_KEY not configured")

        self.client = Anthropic(api_key=settings.claude_api_key)
        self.model = "claude-sonnet-4-20250514"
        self.temperature = 0.7
        self.max_tokens = 2048

    def generate_image_concepts(
        self,
        article_title: str,
        article_content: str = "",
        num_concepts: int = 3
    ) -> List[Dict[str, any]]:
        """
        Generate diverse artistic image concept prompts for an article

        Args:
            article_title: Article headline
            article_content: Optional article body for context
            num_concepts: Number of concept variations (default: 3)

        Returns:
            List of concept dictionaries with prompt, confidence, rationale
        """
        try:
            logger.info(f"Generating {num_concepts} image concepts for: {article_title[:60]}...")

            # Create prompt for Claude
            user_prompt = self._build_enhancement_prompt(
                article_title,
                article_content,
                num_concepts
            )

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            response_text = message.content[0].text
            logger.info(f"Claude response received ({len(response_text)} chars)")

            # Parse concepts from response
            concepts = self._parse_concepts(response_text)

            if concepts:
                logger.info(f"Parsed {len(concepts)} image concepts successfully")
                return concepts
            else:
                logger.warning("Failed to parse concepts from Claude response")
                return []

        except Exception as e:
            logger.error(f"Image concept generation failed: {e}")
            return []

    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude"""
        return """You are an expert visual concept designer specializing in photojournalism and editorial imagery for labor and working-class news publications.

Your task is to generate detailed, compelling image prompts that will be used with AI image generation models (like Gemini, DALL-E, Midjourney).

Key principles:
- Focus on VISUAL elements (lighting, composition, mood, style)
- Emphasize worker dignity, solidarity, and authenticity
- Use documentary/photojournalistic approaches
- Avoid political symbols unless central to the story
- Be specific about: lighting, camera angle, composition, mood, style
- Consider diversity and representation
- Each concept should explore a DIFFERENT artistic interpretation

Output Format: Use EXACTLY this format for each concept:

**Concept N (Confidence: X.XX):** [Detailed 2-3 sentence image prompt with specific visual direction]
**Rationale:** [1-2 sentences explaining why this interpretation works]

Example:
**Concept 1 (Confidence: 0.85):** Documentary-style photograph of diverse warehouse workers during a union organizing meeting. Warm overhead lighting illuminates serious, determined expressions as workers review documents together. Shot from slightly above with wide angle lens, emphasizing collective action and solidarity. Photorealistic, 16:9 aspect ratio.
**Rationale:** Documentary style provides authenticity and gravitas for labor organizing stories. The overhead angle and warm lighting create an inclusive, collaborative atmosphere that emphasizes worker agency.
"""

    def _build_enhancement_prompt(
        self,
        article_title: str,
        article_content: str,
        num_concepts: int
    ) -> str:
        """Build the enhancement prompt for Claude"""

        # Clean article title
        clean_title = article_title.replace('[NEEDS REVIEW]', '').strip()

        # Build context from content if provided
        context_section = ""
        if article_content:
            # Extract first 500 chars for context
            clean_content = article_content[:500].strip()
            context_section = f"\n\n**Article Context:**\n{clean_content}..."

        prompt = f"""Generate {num_concepts} diverse artistic image concepts for this Daily Worker news article:

**Article Title:** {clean_title}
{context_section}

Please create {num_concepts} DISTINCT visual concepts, each exploring a different artistic interpretation:

Concept Variety Guidelines:
- Concept 1: Documentary photojournalism style (authentic, on-the-ground)
- Concept 2: Editorial illustration style (artistic, symbolic, compositional)
- Concept 3: Photorealistic scene style (cinematic, dramatic lighting)
{f"- Concept 4: Wide-angle environmental style (context, scale, setting)" if num_concepts >= 4 else ""}
{f"- Concept 5: Close-up portrait style (human connection, emotion, faces)" if num_concepts >= 5 else ""}

For each concept, provide:
1. A detailed 2-3 sentence image prompt optimized for AI image generation
2. Confidence score (0.0-1.0) based on how well it matches the article's tone and message
3. Brief rationale explaining the artistic choice

Remember:
- Be SPECIFIC about visual elements (lighting, angle, composition, mood)
- Focus on worker dignity and authenticity
- Avoid clichés and generic "worker" imagery
- Consider the article's specific context and message
- Each concept should feel distinctly different from the others

Use the EXACT format specified in your system prompt."""

        return prompt

    def _parse_concepts(self, response_text: str) -> List[Dict[str, any]]:
        """
        Parse image concepts from Claude's response

        Args:
            response_text: Claude's response text

        Returns:
            List of concept dictionaries
        """
        concepts = []

        # Pattern: **Concept N (Confidence: X.XX):** [prompt]
        # **Rationale:** [rationale]
        concept_pattern = r'\*\*Concept (\d+) \(Confidence: ([\d.]+)\):\*\*\s*(.+?)(?=\*\*Rationale:)'
        rationale_pattern = r'\*\*Rationale:\*\*\s*(.+?)(?=\*\*Concept|\n\n|$)'

        # Find all concept blocks
        concept_matches = list(re.finditer(concept_pattern, response_text, re.DOTALL))
        rationale_matches = list(re.finditer(rationale_pattern, response_text, re.DOTALL))

        for i, concept_match in enumerate(concept_matches):
            concept_num = int(concept_match.group(1))
            confidence = float(concept_match.group(2))
            prompt = concept_match.group(3).strip()

            # Clean up prompt (remove newlines, extra spaces)
            prompt = ' '.join(prompt.split())

            # Find matching rationale
            rationale = ""
            if i < len(rationale_matches):
                rationale = rationale_matches[i].group(1).strip()
                rationale = ' '.join(rationale.split())

            concepts.append({
                'concept_number': concept_num,
                'prompt': prompt,
                'confidence': confidence,
                'rationale': rationale
            })

        return concepts

    def select_best_concept(self, concepts: List[Dict[str, any]]) -> Optional[Dict[str, any]]:
        """
        Select the best concept based on confidence score

        Args:
            concepts: List of concept dictionaries

        Returns:
            Best concept dictionary or None
        """
        if not concepts:
            return None

        # Sort by confidence (highest first)
        sorted_concepts = sorted(concepts, key=lambda x: x['confidence'], reverse=True)

        best = sorted_concepts[0]
        logger.info(f"Selected Concept {best['concept_number']} (Confidence: {best['confidence']:.2f})")

        return best


def test_enhancer():
    """Test the prompt enhancer"""
    enhancer = PromptEnhancer()

    # Test with sample article
    article_title = "Amazon Workers Vote to Unionize Despite Anti-Union Campaign"
    article_content = """
    Workers at Amazon's Staten Island warehouse voted overwhelmingly to form the company's
    first U.S. union, delivering a historic victory for organized labor. The grassroots
    organizing effort overcame a massive anti-union campaign by Amazon that included
    mandatory meetings and text messages to workers.
    """

    print("\n" + "="*60)
    print("Testing Image Prompt Enhancement")
    print("="*60)

    concepts = enhancer.generate_image_concepts(
        article_title,
        article_content,
        num_concepts=3
    )

    if concepts:
        print(f"\n✓ Generated {len(concepts)} concepts:\n")

        for concept in concepts:
            print(f"Concept {concept['concept_number']} (Confidence: {concept['confidence']:.2f})")
            print(f"Prompt: {concept['prompt']}")
            print(f"Rationale: {concept['rationale']}")
            print()

        best = enhancer.select_best_concept(concepts)
        if best:
            print(f"Best Concept: #{best['concept_number']} (Confidence: {best['confidence']:.2f})")
            print(f"Prompt: {best['prompt']}")
    else:
        print("\n✗ Failed to generate concepts")


if __name__ == "__main__":
    test_enhancer()
