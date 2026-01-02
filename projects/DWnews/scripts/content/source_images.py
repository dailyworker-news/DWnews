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

        # Initialize Unsplash client
        self.unsplash_enabled = bool(settings.unsplash_access_key)
        if self.unsplash_enabled:
            logger.info("Unsplash API available")

        # Initialize Pexels client
        self.pexels_enabled = bool(settings.pexels_api_key)
        if self.pexels_enabled:
            logger.info("Pexels API available")

        # Initialize OpenAI DALL-E for image generation
        self.openai_enabled = bool(settings.openai_api_key)
        if self.openai_enabled:
            logger.info("OpenAI DALL-E image generation available")

        # Initialize Google Gemini for image generation (if available)
        self.gemini_enabled = bool(getattr(settings, 'gemini_api_key', None))
        if self.gemini_enabled:
            logger.info("Google Gemini image generation available")

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

    def generate_image_with_dalle(self, prompt: str) -> Optional[Dict]:
        """Generate image using OpenAI DALL-E 3"""
        if not self.openai_enabled:
            return None

        try:
            # Sanitize prompt - remove [NEEDS REVIEW], problematic phrases, etc.
            clean_prompt = prompt.replace('[NEEDS REVIEW]', '').strip()

            # Skip if prompt is too generic or problematic
            if (len(clean_prompt) < 10 or
                clean_prompt.lower().startswith('i cannot') or
                'cannot write' in clean_prompt.lower()):
                logger.warning(f"Skipping DALL-E generation - invalid prompt: {clean_prompt[:50]}")
                return None

            # Create neutral, non-political prompt for labor/worker topics
            # Focus on visual elements rather than political/controversial terms
            neutral_prompt = clean_prompt

            # Replace potentially sensitive terms with neutral visual descriptions
            replacements = {
                'Trump': 'federal government',
                'Immigration Crackdown': 'immigration policy',
                'ICE': 'federal agents',
                'deportation': 'immigration enforcement'
            }

            for old, new in replacements.items():
                neutral_prompt = neutral_prompt.replace(old, new)

            # Create a general prompt about workers/labor
            simplified_prompt = "Workers at a union meeting discussing labor issues. Professional photojournalism style."

            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "dall-e-3",
                "prompt": simplified_prompt,
                "n": 1,
                "size": "1792x1024",  # Landscape format
                "quality": "standard"
            }

            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()
            if result.get('data') and len(result['data']) > 0:
                return {
                    'url': result['data'][0]['url'],
                    'attribution': 'AI-generated image by DALL-E 3',
                    'source': 'DALL-E'
                }

        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")

        return None

    def source_image_for_article(self, article: Article, verbose: bool = False) -> bool:
        """
        Generate images from ALL available AI providers for editorial review

        Images are saved to media/article_{id}/ with provider-specific names:
        - dalle.jpg (OpenAI DALL-E 3)
        - gemini.jpg (Google Gemini - if available)
        - unsplash.jpg (stock photo)
        - pexels.jpg (stock photo)

        The article's image_url will be set to the first successful generation.
        Editor can then manually select the best image during review.
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

        # 2. Generate AI images
        if self.openai_enabled:
            if verbose:
                print("   🎨 Generating with DALL-E 3...")
            image_info = self.generate_image_with_dalle(search_query)
            if image_info:
                image_data = self.download_image(image_info['url'])
                if image_data:
                    optimized = self.optimize_image(image_data)
                    saved_path = self.save_image(optimized, article.id, 'dalle')
                    if saved_path:
                        generated_images.append(('DALL-E', saved_path, image_info['attribution']))
                        successful_providers.append('DALL-E')
                        if verbose:
                            print(f"      ✓ Saved DALL-E image")

        # Note: Google Gemini doesn't have public image generation API yet
        # Would add here when available

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
    if not (settings.unsplash_access_key or settings.pexels_api_key or settings.openai_api_key):
        print("\n⚠ No image API configured. Images will use placeholders.")
        print("  Configure in .env:")
        print("  - UNSPLASH_ACCESS_KEY (stock photos)")
        print("  - PEXELS_API_KEY (stock photos)")
        print("  - OPENAI_API_KEY (DALL-E 3 generation)")

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
