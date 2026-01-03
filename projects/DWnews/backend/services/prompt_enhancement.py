"""
The Daily Worker - Claude Prompt Enhancement Service

Provides intelligent prompt enhancement using Claude Sonnet 4.5 to generate
diverse artistic image concepts for news articles.

Phase 6.11.3: Implement Claude Prompt Enhancement
"""

import json
from typing import Optional, Dict, List
from anthropic import Anthropic


class ClaudePromptEnhancer:
    """
    Prompt enhancement service using Claude Sonnet 4.5.

    Features:
    - Generates 3-5 diverse artistic image concepts per article
    - Provides confidence scoring (0.0-1.0) for each concept
    - Includes rationale for artistic choices
    - Automatically selects best concept based on confidence
    - Ensures concept diversity (different artistic approaches)
    """

    # System prompt for Claude
    SYSTEM_PROMPT = """You are an expert art director for a socialist news publication called "The Daily Worker".
Your job is to generate creative, diverse image generation prompts that will produce compelling visual content
for news articles about labor, politics, and social justice.

For each article, generate 3-5 distinct artistic concepts with different visual approaches:
- Photorealistic/documentary style
- Abstract/symbolic interpretation
- Vintage/historical art styles (propaganda posters, socialist realism, etc.)
- Conceptual/metaphorical imagery
- Illustrative/graphic styles

Each concept should include:
1. A detailed image generation prompt (describe composition, style, lighting, mood)
2. A confidence score (0.0-1.0) indicating how well the concept fits the article
3. A brief rationale explaining the artistic choice

Return your response as valid JSON in this exact format:
{
  "concepts": [
    {
      "prompt": "Detailed image generation prompt here",
      "confidence": 0.92,
      "rationale": "Brief explanation of artistic choice"
    }
  ]
}

Make prompts specific, visual, and suitable for AI image generation. Avoid text in images."""

    def __init__(self, api_key: Optional[str] = None, client: Optional[Anthropic] = None):
        """
        Initialize Claude prompt enhancement service.

        Args:
            api_key: Anthropic API key (required if client not provided)
            client: Optional Anthropic client (for testing)

        Raises:
            ValueError: If API key is not provided and client is not provided
        """
        if not api_key and not client:
            raise ValueError("Claude API key is required")

        self.api_key = api_key
        self.client = client if client else Anthropic(api_key=api_key)

    def generate_concepts(
        self,
        headline: str,
        summary: str
    ) -> Optional[Dict]:
        """
        Generate diverse artistic image concepts for an article.

        Args:
            headline: Article headline
            summary: Article summary/lede

        Returns:
            Dict with key:
                - concepts: List[Dict] with keys: prompt, confidence, rationale
            Returns None if generation fails

        Raises:
            ValueError: If headline or summary is empty
        """
        if not headline or not summary:
            raise ValueError("Headline and summary are required")

        # Construct user prompt
        user_prompt = f"""Generate 3-5 diverse artistic image concepts for this article:

HEADLINE: {headline}

SUMMARY: {summary}

Provide concepts with different visual styles. Ensure each concept has a confidence score between 0.0 and 1.0.
Return valid JSON only, no other text."""

        try:
            # Call Claude API
            response = self.client.messages.create(
                model='claude-sonnet-4-5-20250929',
                max_tokens=2048,
                system=self.SYSTEM_PROMPT,
                messages=[
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ]
            )

            # Extract text from response
            response_text = response.content[0].text

            # Parse JSON response
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response if wrapped in markdown
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    data = json.loads(json_text)
                elif '```' in response_text:
                    json_start = response_text.find('```') + 3
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                    data = json.loads(json_text)
                else:
                    return None

            # Validate response structure
            if 'concepts' not in data:
                return None

            concepts = data['concepts']

            # Validate concept count (3-5)
            if len(concepts) < 3:
                return None

            # Limit to 5 concepts if more were returned
            if len(concepts) > 5:
                concepts = concepts[:5]

            # Validate each concept
            valid_concepts = []
            for concept in concepts:
                if not all(key in concept for key in ['prompt', 'confidence', 'rationale']):
                    continue

                # Validate confidence score
                confidence = concept['confidence']
                if not isinstance(confidence, (int, float)):
                    continue
                if confidence < 0.0 or confidence > 1.0:
                    continue

                # Validate non-empty strings
                if not concept['prompt'] or not concept['rationale']:
                    continue

                valid_concepts.append(concept)

            if len(valid_concepts) < 3:
                return None

            return {'concepts': valid_concepts}

        except Exception as e:
            # Return None on any error
            return None

    def enhance_prompt(
        self,
        headline: str,
        summary: str
    ) -> Optional[Dict]:
        """
        Generate concepts and select the best one.

        Args:
            headline: Article headline
            summary: Article summary/lede

        Returns:
            Dict with keys:
                - selected_prompt: str (best concept prompt)
                - confidence: float (confidence score of selected concept)
                - rationale: str (rationale for selected concept)
                - all_concepts: List[Dict] (all generated concepts)
            Returns None if generation fails

        Raises:
            ValueError: If headline or summary is empty
        """
        if not headline or not summary:
            raise ValueError("Headline and summary are required")

        # Generate concepts
        result = self.generate_concepts(headline, summary)

        if not result or 'concepts' not in result:
            return None

        concepts = result['concepts']

        if len(concepts) == 0:
            return None

        # Select concept with highest confidence
        best_concept = max(concepts, key=lambda c: c['confidence'])

        return {
            'selected_prompt': best_concept['prompt'],
            'confidence': best_concept['confidence'],
            'rationale': best_concept['rationale'],
            'all_concepts': concepts
        }
