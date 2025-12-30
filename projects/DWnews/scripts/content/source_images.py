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
        self.storage_path = Path(settings.local_image_storage)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize Unsplash client
        self.unsplash_enabled = bool(settings.unsplash_access_key)
        if self.unsplash_enabled:
            logger.info("Unsplash API available")

        # Initialize Pexels client
        self.pexels_enabled = bool(settings.pexels_api_key)
        if self.pexels_enabled:
            logger.info("Pexels API available")

        # Initialize Gemini for image generation (opinion pieces)
        self.gemini_enabled = bool(settings.gemini_image_api_key or settings.gemini_api_key)
        if self.gemini_enabled:
            logger.info("Gemini image generation available")

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

    def save_image(self, image_data: bytes, filename: str) -> str:
        """Save image to local storage"""
        try:
            file_path = self.storage_path / filename
            with open(file_path, 'wb') as f:
                f.write(image_data)

            # Return relative path for storage in DB
            return f"static/images/{filename}"

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

    def source_image_for_article(self, article: Article, verbose: bool = False) -> bool:
        """Source and attach image to article"""
        if verbose:
            print(f"\n🖼️  Sourcing image: {article.title[:50]}...")

        # Generate search query from title
        search_query = article.title[:100]

        # Try Unsplash first
        image_info = self.search_unsplash(search_query)

        # Try Pexels if Unsplash fails
        if not image_info:
            image_info = self.search_pexels(search_query)

        # Use placeholder if no image found
        if not image_info:
            if verbose:
                print("   ⚠ No image found, using placeholder")
            article.image_url = "/static/images/placeholder.jpg"
            article.image_attribution = "Placeholder image"
            return False

        # Download image
        image_data = self.download_image(image_info['url'])
        if not image_data:
            if verbose:
                print("   ✗ Failed to download image")
            return False

        # Optimize image
        optimized = self.optimize_image(image_data)

        # Generate filename
        filename_hash = hashlib.md5(article.slug.encode()).hexdigest()[:12]
        filename = f"{filename_hash}.jpg"

        # Save image
        saved_path = self.save_image(optimized, filename)
        if not saved_path:
            if verbose:
                print("   ✗ Failed to save image")
            return False

        # Update article
        article.image_url = f"/{saved_path}"
        article.image_attribution = image_info['attribution']
        article.image_source = image_info['source']

        if verbose:
            print(f"   ✓ Saved from {image_info['source']}")

        return True

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
    if not (settings.unsplash_access_key or settings.pexels_api_key):
        print("\n⚠ No image API configured. Images will use placeholders.")
        print("  Configure in .env:")
        print("  - UNSPLASH_ACCESS_KEY")
        print("  - PEXELS_API_KEY")

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
