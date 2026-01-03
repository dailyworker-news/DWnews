#!/usr/bin/env python3
"""
The Daily Worker - Image Sourcing
Sources and optimizes images for articles
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import hashlib
import requests
from io import BytesIO

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger
from database.models import Article
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scripts.content.prompt_enhancer import PromptEnhancer

logger = get_logger(__name__)

# Image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not available - image optimization disabled")


class ImageSourcer:
    """Image sourcing and optimization service"""

    def __init__(self, session):
        self.session = session
        # Use media directory with article subdirectories
        self.media_path = Path('media')
        self.media_path.mkdir(parents=True, exist_ok=True)

        # Initialize stock photo providers
        self.unsplash_enabled = bool(settings.unsplash_access_key)
        if self.unsplash_enabled:
            logger.info("Unsplash API available")

        self.pexels_enabled = bool(settings.pexels_api_key)
        if self.pexels_enabled:
            logger.info("Pexels API available")

        # Initialize Gemini 2.5 Flash Image for AI image generation (PRIMARY)
        self.gemini_enabled = bool(settings.gemini_api_key)
        if self.gemini_enabled:
            logger.info("Gemini 2.5 Flash Image available")
            # Initialize Gemini on first use
            self._gemini_initialized = False
            self._gemini_client = None

        # Initialize Claude prompt enhancer
        self.prompt_enhancer_enabled = bool(settings.claude_api_key)
        if self.prompt_enhancer_enabled:
            try:
                self.prompt_enhancer = PromptEnhancer()
                logger.info("Claude prompt enhancer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize prompt enhancer: {e}")
                self.prompt_enhancer_enabled = False

    def download_image(self, url: str, timeout: int = 10) -> Optional[bytes]:
        """Download image from URL"""
        try:
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; DWnews/1.0)'
            })
            response.raise_for_status()

            # Verify it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL returned non-image content: {content_type}")
                return None

            return response.content

        except Exception as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None

    def optimize_image(self, image_data: bytes, max_width: int = 1200, quality: int = 85) -> Optional[bytes]:
        """Optimize image size and quality"""
        if not PIL_AVAILABLE:
            return image_data

        try:
            # Open image
            img = Image.open(BytesIO(image_data))

            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Save optimized
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return image_data

    def save_image(self, image_data: bytes, article_id: int, provider: str) -> str:
        """
        Save image to article-specific directory

        Args:
            image_data: Image bytes
            article_id: Article ID for subdirectory
            provider: Image provider name (e.g., 'dalle', 'gemini', 'unsplash')

        Returns:
            Relative path for storage in DB
        """
        try:
            # Create article-specific directory
            article_dir = self.media_path / f"article_{article_id}"
            article_dir.mkdir(parents=True, exist_ok=True)

            # Save with provider-specific filename
            filename = f"{provider}.jpg"
            file_path = article_dir / filename

            with open(file_path, 'wb') as f:
                f.write(image_data)

            # Return relative path for storage in DB
            return f"media/article_{article_id}/{filename}"

        except Exception as e:
            logger.error(f"Failed to save image {filename}: {e}")
            return ""

    def search_unsplash(self, query: str) -> Optional[Dict]:
        """Search Unsplash for relevant image"""
        if not self.unsplash_enabled:
            return None

        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {settings.unsplash_access_key}"}
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('results'):
                photo = data['results'][0]
                return {
                    'url': photo['urls']['regular'],
                    'attribution': f"Photo by {photo['user']['name']} on Unsplash",
                    'source': 'Unsplash'
                }

        except Exception as e:
            logger.error(f"Unsplash search failed: {e}")

        return None

    def search_pexels(self, query: str) -> Optional[Dict]:
        """Search Pexels for relevant image"""
        if not self.pexels_enabled:
            return None

        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": settings.pexels_api_key}
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get('photos'):
                photo = data['photos'][0]
                return {
                    'url': photo['src']['large'],
                    'attribution': f"Photo by {photo['photographer']} on Pexels",
                    'source': 'Pexels'
                }

        except Exception as e:
            logger.error(f"Pexels search failed: {e}")

        return None

    def generate_image_with_gemini(
        self,
        prompt: str,
        article_id: int,
        article_title: str = "",
        article_content: str = ""
    ) -> Optional[str]:
        """
        Generate image using Gemini 2.5 Flash Image with Claude-enhanced prompts

        Args:
            prompt: Base prompt (article title or concept)
            article_id: Article ID for saving image
            article_title: Full article title for context
            article_content: Optional article content for better context

        Returns:
            Path to saved image file or None if failed
        """
        if not self.gemini_enabled:
            return None

        try:
            # Initialize Gemini on first use
            if not self._gemini_initialized:
                from google import genai
                from google.genai import types

                self._gemini_client = genai.Client(api_key=settings.gemini_api_key)
                self._gemini_types = types
                self._gemini_initialized = True
                logger.info("Gemini 2.5 Flash Image initialized")

            # Enhance prompt using Claude if available
            final_prompt = prompt
            concept_info = {}

            if self.prompt_enhancer_enabled:
                logger.info("=" * 60)
                logger.info("STEP 1: Claude Prompt Enhancement")
                logger.info("=" * 60)
                logger.info(f"Article Title: {article_title or prompt}")
                logger.info(f"Generating {3} diverse artistic concepts...")

                concepts = self.prompt_enhancer.generate_image_concepts(
                    article_title=article_title or prompt,
                    article_content=article_content,
                    num_concepts=3
                )

                if concepts:
                    logger.info(f"✓ Generated {len(concepts)} concepts from Claude")

                    # Log all concepts with confidence scores
                    for i, concept in enumerate(concepts, 1):
                        logger.info(f"  Concept {i}: Confidence {concept['confidence']:.2f}")
                        logger.info(f"    Prompt: {concept['prompt'][:100]}...")
                        logger.info(f"    Rationale: {concept['rationale'][:80]}...")

                    best_concept = self.prompt_enhancer.select_best_concept(concepts)
                    if best_concept:
                        final_prompt = best_concept['prompt']
                        concept_info = best_concept
                        logger.info("")
                        logger.info(f"✓ Selected Best Concept: #{best_concept['concept_number']}")
                        logger.info(f"  Confidence Score: {best_concept['confidence']:.2f}")
                        logger.info(f"  Enhanced Prompt: {final_prompt[:150]}...")
                else:
                    logger.warning("✗ Failed to enhance prompt, using basic prompt")
                    logger.info(f"  Fallback Prompt: {prompt}")

            # Sanitize prompt
            clean_prompt = final_prompt.replace('[NEEDS REVIEW]', '').strip()

            # Skip if prompt is too generic
            if len(clean_prompt) < 10:
                logger.warning(f"✗ Skipping Gemini generation - prompt too short ({len(clean_prompt)} chars)")
                logger.warning(f"  Prompt: '{clean_prompt}'")
                return None

            # Generate image using Gemini 2.5 Flash Image
            logger.info("")
            logger.info("=" * 60)
            logger.info("STEP 2: Gemini 2.5 Flash Image Generation")
            logger.info("=" * 60)
            logger.info(f"Prompt Length: {len(clean_prompt)} characters")
            logger.info(f"Final Prompt: {clean_prompt[:200]}...")
            logger.info("Calling Gemini API...")

            response = self._gemini_client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[clean_prompt],
                config=self._gemini_types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    candidate_count=1
                )
            )

            # Extract image data from response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]

                # Iterate through parts looking for image data
                for part in candidate.content.parts:
                    # Check for inline_data (image)
                    if hasattr(part, 'inline_data') and part.inline_data:
                        inline_data = part.inline_data

                        # Check if it's an image by MIME type
                        if hasattr(inline_data, 'mime_type') and 'image' in inline_data.mime_type:
                            # Get image data (already in bytes format from Gemini)
                            import base64
                            image_data = inline_data.data

                            # If it's a string, decode base64; if already bytes, use directly
                            if isinstance(image_data, str):
                                image_data = base64.b64decode(image_data)

                            # Save image to article directory
                            article_dir = self.media_path / f"article_{article_id}"
                            article_dir.mkdir(parents=True, exist_ok=True)

                            file_path = article_dir / "gemini_flash_image.png"
                            with open(file_path, 'wb') as f:
                                f.write(image_data)

                            logger.info("")
                            logger.info("=" * 60)
                            logger.info("STEP 3: Image Saved Successfully")
                            logger.info("=" * 60)
                            logger.info(f"✓ Image Path: {file_path}")
                            logger.info(f"✓ Image Size: {len(image_data):,} bytes ({len(image_data)/1024:.1f} KB)")
                            logger.info(f"✓ Article ID: {article_id}")

                            # Log metadata if available
                            if concept_info:
                                logger.info("")
                                logger.info("Image Generation Metadata:")
                                logger.info(f"  Concept Number: {concept_info.get('concept_number', 'N/A')}")
                                logger.info(f"  Confidence Score: {concept_info.get('confidence', 0.0):.2f}")
                                logger.info(f"  Rationale: {concept_info.get('rationale', 'N/A')[:80]}...")

                            # Return relative path
                            return f"media/article_{article_id}/gemini_flash_image.png"

            logger.warning("✗ Gemini did not return image data in expected format")
            return None

        except Exception as e:
            logger.error("=" * 60)
            logger.error("ERROR: Gemini 2.5 Flash Image generation failed")
            logger.error("=" * 60)
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error Message: {e}")
            return None

    def source_image_for_article(self, article: Article, verbose: bool = False) -> bool:
        """
        Generate images from ALL available providers for editorial review

        Images are saved to media/article_{id}/ with provider-specific names:
        - gemini_flash_image.png (Gemini 2.5 Flash with Claude-enhanced prompts - PRIMARY)
        - unsplash.jpg (stock photo fallback)
        - pexels.jpg (stock photo fallback)

        The article's image_url will be set to the first successful generation.
        Editor can then manually select the best image during review.

        Claude Enhancement: If Claude API is available, it generates 3 diverse
        artistic concept prompts and selects the best one (by confidence score)
        before passing to Gemini for image generation.
        """
        if verbose:
            print(f"\n🖼️  Generating images for editorial review: {article.title[:50]}...")

        # Clean prompt (remove [NEEDS REVIEW] tags)
        clean_title = article.title.replace('[NEEDS REVIEW]', '').strip()
        search_query = clean_title[:100]

        generated_images = []
        successful_providers = []

        # 1. Try stock photos first (Unsplash, Pexels)
        if self.unsplash_enabled:
            if verbose:
                print("   📸 Trying Unsplash...")
            image_info = self.search_unsplash(search_query)
            if image_info:
                image_data = self.download_image(image_info['url'])
                if image_data:
                    optimized = self.optimize_image(image_data)
                    saved_path = self.save_image(optimized, article.id, 'unsplash')
                    if saved_path:
                        generated_images.append(('Unsplash', saved_path, image_info['attribution']))
                        successful_providers.append('Unsplash')
                        if verbose:
                            print(f"      ✓ Saved Unsplash image")

        if self.pexels_enabled:
            if verbose:
                print("   📸 Trying Pexels...")
            image_info = self.search_pexels(search_query)
            if image_info:
                image_data = self.download_image(image_info['url'])
                if image_data:
                    optimized = self.optimize_image(image_data)
                    saved_path = self.save_image(optimized, article.id, 'pexels')
                    if saved_path:
                        generated_images.append(('Pexels', saved_path, image_info['attribution']))
                        successful_providers.append('Pexels')
                        if verbose:
                            print(f"      ✓ Saved Pexels image")

        # 2. Generate AI images with Gemini 2.5 Flash Image + Claude enhancement
        if self.gemini_enabled:
            if verbose:
                print("   🎨 Generating with Gemini 2.5 Flash Image (Claude-enhanced)...")
            saved_path = self.generate_image_with_gemini(
                prompt=search_query,
                article_id=article.id,
                article_title=article.title,
                article_content=article.content[:500] if article.content else ""
            )
            if saved_path:
                generated_images.append(('Gemini 2.5 Flash', saved_path, 'AI-generated image with Claude-enhanced prompt'))
                successful_providers.append('Gemini 2.5 Flash')
                if verbose:
                    print(f"      ✓ Saved Gemini 2.5 Flash image")

        # Summary
        if verbose:
            print()
            print(f"   📊 Generated {len(generated_images)} images:")
            for provider, path, _ in generated_images:
                print(f"      - {provider}: {path}")

        # Set article's default image to the first successful one
        if generated_images:
            provider, path, attribution = generated_images[0]
            article.image_url = f"/{path}"
            article.image_attribution = attribution
            article.image_source = provider

            if verbose:
                print()
                print(f"   ✓ Default set to: {provider}")
                print(f"   📁 All images in: media/article_{article.id}/")

            return True
        else:
            if verbose:
                print("   ⚠️  No images generated - check API keys")
            article.image_url = "/static/images/placeholder.jpg"
            article.image_attribution = "Placeholder image"
            return False

    def process_batch(self, max_articles: int = 10, verbose: bool = True) -> int:
        """Process images for multiple articles"""
        # Get articles without images
        articles = self.session.query(Article).filter(
            Article.status == 'draft',
            Article.image_url.is_(None)
        ).limit(max_articles).all()

        if not articles:
            logger.info("No articles need images")
            return 0

        success_count = 0
        for article in articles:
            if self.source_image_for_article(article, verbose=verbose):
                success_count += 1

            # Commit after each article
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logger.error(f"Failed to save article image: {e}")

        return success_count


def run_image_sourcing(max_articles: int = 10, verbose: bool = True) -> int:
    """Run image sourcing for articles"""
    print("=" * 60)
    print("The Daily Worker - Image Sourcing")
    print("=" * 60)

    # Check if image APIs available
    if not (settings.unsplash_access_key or settings.pexels_api_key or settings.gemini_api_key):
        print("\n⚠ No image API configured. Images will use placeholders.")
        print("  Configure in .env:")
        print("  - GEMINI_API_KEY (Gemini 2.5 Flash Image - primary AI generation)")
        print("  - CLAUDE_API_KEY (optional - for enhanced prompts)")
        print("  - UNSPLASH_ACCESS_KEY (stock photos - fallback)")
        print("  - PEXELS_API_KEY (stock photos - fallback)")

    # Create database session
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
    )
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Initialize sourcer
        sourcer = ImageSourcer(session)

        # Process articles
        print(f"\nProcessing up to {max_articles} articles...")
        count = sourcer.process_batch(max_articles=max_articles, verbose=verbose)

        # Show results
        print("\n" + "=" * 60)
        print("IMAGE SOURCING COMPLETE")
        print("=" * 60)
        print(f"✓ Processed: {count} articles")

        return count

    except Exception as e:
        logger.error(f"Image sourcing failed: {e}")
        print(f"\n✗ Error: {e}")
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    count = run_image_sourcing(max_articles=10, verbose=True)

    if count > 0:
        print(f"\n✓ {count} articles now have images")
        print("\nNext step: Review and approve articles in admin dashboard")
    else:
        print("\n⚠ No images sourced. Check:")
        print("  1. Draft articles exist (run generate_articles.py)")
        print("  2. Image API keys configured")
        print("  3. Internet connection")
