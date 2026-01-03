"""
The Daily Worker - Gemini 2.5 Flash Image Generation Service

Provides image generation using Google's Gemini 2.5 Flash Image model.
Simpler, faster, and higher quality than Vertex AI Imagen.
"""

import google.generativeai as genai
from io import BytesIO
from typing import Optional, Dict
import time


class GeminiImageService:
    """
    Image generation service using Gemini 2.5 Flash Image.

    Features:
    - Fast generation (10-15s typical)
    - High quality photorealistic or stylized images
    - Simple API key authentication
    - Automatic retry with exponential backoff
    - Built-in safety filters
    """

    # Valid aspect ratios per Gemini API spec
    VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]

    # Default negative prompt for quality
    DEFAULT_NEGATIVE_PROMPT = "low quality, blurry, distorted, text, watermark, signature"

    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """
        Initialize Gemini image generation service.

        Args:
            api_key: Gemini API key (required)
            max_retries: Maximum retry attempts on transient failures

        Raises:
            ValueError: If API key is not provided
        """
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.api_key = api_key
        self.max_retries = max_retries

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        guidance_scale: float = 7.0,
        number_of_images: int = 1
    ) -> Optional[Dict]:
        """
        Generate image using Gemini 2.5 Flash Image.

        Args:
            prompt: Text description of desired image (max 2000 chars)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
            negative_prompt: What to avoid in generation (optional)
            guidance_scale: Prompt adherence strength (1.0-20.0, default 7.0)
            number_of_images: Number of images to generate (1-4, default 1)

        Returns:
            Dict with keys:
                - image_data: bytes (PNG format)
                - source_type: 'generated'
                - attribution: str
                - license: str
            Returns None if generation fails

        Raises:
            ValueError: If aspect_ratio is invalid
        """
        # Validate aspect ratio
        if aspect_ratio not in self.VALID_ASPECT_RATIOS:
            raise ValueError(
                f"Invalid aspect ratio: {aspect_ratio}. "
                f"Must be one of {self.VALID_ASPECT_RATIOS}"
            )

        # Truncate prompt if too long (Gemini max: 2000 chars)
        if len(prompt) > 2000:
            prompt = prompt[:1997] + "..."

        # Use default negative prompt if not provided
        if negative_prompt is None:
            negative_prompt = self.DEFAULT_NEGATIVE_PROMPT

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                # Call Gemini API
                response = self.model.generate_images(
                    prompt=prompt,
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                    negative_prompt=negative_prompt,
                    guidance_scale=guidance_scale
                )

                # Check for safety filter blocking
                if response.prompt_feedback.block_reason:
                    return None

                # Extract image from response
                if not response.images or len(response.images) == 0:
                    return None

                image = response.images[0]

                # Convert PIL Image to bytes (PNG format)
                buffer = BytesIO()
                image._pil_image.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()

                # Return structured result
                return {
                    'image_data': image_bytes,
                    'source_type': 'generated',
                    'attribution': 'AI-generated image via Google Gemini 2.5 Flash Image',
                    'license': 'Generated content - Editorial use'
                }

            except Exception as e:
                # Retry on transient errors
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    # Max retries exceeded
                    return None

        return None
