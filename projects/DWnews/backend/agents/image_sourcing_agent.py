"""
The Daily Worker - Image Sourcing & Generation Agent
Implements multi-tier image sourcing strategy with AI generation
"""

import sys
import time
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from io import BytesIO

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config import settings
from backend.logging_config import get_logger

logger = get_logger(__name__)

# Image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow not available - image optimization disabled")


class ImageSourcingAgent:
    """
    Multi-tier image sourcing and generation agent.

    Cascading Strategy:
    1. Extract from source article (Open Graph, featured images)
    2. Generate via Google Gemini Imagen (AI-generated editorial images)
    3. Search stock photos (Unsplash/Pexels)
    4. Use category-specific placeholder (fallback only)

    Target Success Rate:
    - ≥70% from sources or Gemini generation
    - ≤30% from stock photos
    - <5% using placeholders
    """

    def __init__(self):
        """Initialize the Image Sourcing Agent"""
        self.storage_path = Path(settings.local_image_storage)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # API configuration
        self.gemini_api_key = settings.gemini_image_api_key
        self.unsplash_key = settings.unsplash_access_key
        self.pexels_key = settings.pexels_api_key

        # Cost tracking
        self.daily_cost_limit = 15.0  # $15/month ≈ $0.50/day
        self.gemini_cost_per_image = 0.03  # Estimated cost per generation
        self._usage_stats = {
            'gemini_calls': 0,
            'gemini_cost': 0.0,
            'last_reset': datetime.now().date()
        }

        logger.info("Image Sourcing Agent initialized")
        logger.info(f"Gemini API: {'enabled' if self.gemini_api_key else 'disabled'}")
        logger.info(f"Unsplash API: {'enabled' if self.unsplash_key else 'disabled'}")
        logger.info(f"Pexels API: {'enabled' if self.pexels_key else 'disabled'}")

    # ========================================
    # Source Image Extraction
    # ========================================

    def extract_image_from_html(self, html: str, base_url: str) -> Optional[str]:
        """
        Extract image URL from HTML using multiple strategies.

        Priority Order:
        1. Open Graph images (og:image, og:image:url)
        2. Twitter Card images (twitter:image)
        3. Featured images (class="featured-image", etc.)
        4. First large image in article content

        Args:
            html: HTML content as string
            base_url: Base URL for resolving relative URLs

        Returns:
            Absolute image URL or None if not found
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Strategy 1: Open Graph image
            og_image = soup.find('meta', property='og:image')
            if not og_image:
                og_image = soup.find('meta', property='og:image:url')

            if og_image and og_image.get('content'):
                url = og_image['content']
                return self._make_absolute_url(url, base_url)

            # Strategy 2: Twitter Card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                url = twitter_image['content']
                return self._make_absolute_url(url, base_url)

            # Strategy 3: Featured image (common class names)
            featured_selectors = [
                'img.featured-image',
                'img.featured',
                'img.wp-post-image',
                'img.entry-image',
                'article img:first-of-type',
                '.article-image img',
                '.post-thumbnail img'
            ]

            for selector in featured_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    url = img['src']
                    return self._make_absolute_url(url, base_url)

            # Strategy 4: First large image in content
            # Look for images >400px (indicated by width attribute or large filename)
            all_images = soup.find_all('img')
            for img in all_images:
                src = img.get('src', '')
                width = img.get('width', '')

                # Skip small images, icons, logos
                if any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'thumb']):
                    continue

                # Check if width indicates large image
                if width and str(width).replace('px', '').isdigit():
                    if int(str(width).replace('px', '')) >= 400:
                        return self._make_absolute_url(src, base_url)

                # If no width, assume it might be large
                if src and not width:
                    return self._make_absolute_url(src, base_url)

            logger.warning(f"No suitable image found in HTML from {base_url}")
            return None

        except Exception as e:
            logger.error(f"Error extracting image from HTML: {e}")
            return None

    def _make_absolute_url(self, url: str, base_url: str) -> str:
        """Convert relative URL to absolute using base URL"""
        if url.startswith('http://') or url.startswith('https://'):
            return url
        return urljoin(base_url, url)

    def download_image(self, url: str, timeout: int = 10) -> Optional[bytes]:
        """
        Download image from URL.

        Args:
            url: Image URL to download
            timeout: Request timeout in seconds

        Returns:
            Image binary data or None on failure
        """
        try:
            response = requests.get(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; DWnews/1.0; +https://dailyworker.news)'
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

    def extract_from_source(self, source_url: str) -> Optional[Dict]:
        """
        Complete workflow to extract image from source article.

        Args:
            source_url: URL of source article

        Returns:
            Dict with image data and metadata, or None on failure
        """
        try:
            # Fetch source page HTML
            logger.info(f"Extracting image from source: {source_url}")
            response = requests.get(source_url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; DWnews/1.0; +https://dailyworker.news)'
            })
            response.raise_for_status()

            # Extract image URL from HTML
            image_url = self.extract_image_from_html(response.text, source_url)
            if not image_url:
                logger.info(f"No image found in source: {source_url}")
                return None

            # Download image
            image_data = self.download_image(image_url)
            if not image_data:
                logger.warning(f"Failed to download extracted image: {image_url}")
                return None

            # Generate attribution
            domain = urlparse(source_url).netloc
            attribution = f"Image from {domain}"

            logger.info(f"✓ Successfully extracted image from {domain}")

            return {
                'url': image_url,
                'image_data': image_data,
                'source_type': 'extracted',
                'attribution': attribution,
                'source_domain': domain,
                'license': 'Fair use - Editorial content'
            }

        except Exception as e:
            logger.error(f"Source extraction failed for {source_url}: {e}")
            return None

    # ========================================
    # Google Gemini Imagen Generation
    # ========================================

    def generate_gemini_prompt(
        self,
        headline: str,
        summary: str,
        category: str,
        is_opinion: bool = False
    ) -> str:
        """
        Generate context-aware prompt for Gemini image generation.

        Args:
            headline: Article headline
            summary: Article summary
            category: Article category (labor, politics, etc.)
            is_opinion: Whether this is an opinion piece

        Returns:
            Optimized prompt string for Imagen
        """
        # Category-specific style guidance
        category_styles = {
            'labor': 'workers, solidarity, union, workplace, diverse working people',
            'politics': 'civic engagement, democracy, government, policy',
            'economy': 'economic justice, financial equality, workers economy',
            'environment': 'environmental justice, climate action, sustainable work',
            'healthcare': 'healthcare workers, medical equity, public health',
            'education': 'educators, students, public education, learning',
            'housing': 'affordable housing, community, neighborhoods',
            'opinion': 'editorial illustration, bold perspective, worker-centric viewpoint',
            'sports': 'athletic competition, teamwork, sports culture'
        }

        style_keywords = category_styles.get(category, 'news, journalism, current events')

        # Different prompts for opinion vs news
        if is_opinion:
            prompt = (
                f"Create an editorial illustration for: {headline}. "
                f"Style: Bold, graphic, editorial cartoon aesthetic with worker perspective. "
                f"Themes: {style_keywords}. "
                f"Mood: Thought-provoking, engaging, clear visual metaphor. "
                f"Technical: Horizontal 16:9 ratio, professional editorial quality, "
                f"suitable for news publication."
            )
        else:
            prompt = (
                f"Create a photojournalistic image for news article: {headline}. "
                f"Style: Realistic, professional news photography, documentary aesthetic. "
                f"Themes: {style_keywords}. "
                f"Mood: Authentic, dignified, empowering. "
                f"Technical: Horizontal 16:9 ratio, news-quality photography, "
                f"diverse representation, worker-focused perspective."
            )

        # Trim to reasonable length (Imagen has limits)
        if len(prompt) > 1000:
            prompt = prompt[:997] + "..."

        return prompt

    def generate_with_gemini(
        self,
        prompt: str,
        api_key: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[Dict]:
        """
        Generate image using Google Gemini Imagen API.

        Args:
            prompt: Text prompt for image generation
            api_key: Gemini API key (uses config if not provided)
            max_retries: Number of retry attempts on failure

        Returns:
            Dict with generated image data and metadata, or None on failure
        """
        if not api_key:
            api_key = self.gemini_api_key

        if not api_key:
            logger.warning("Gemini API key not configured - skipping generation")
            return None

        # Check daily cost limit
        if self.is_daily_limit_exceeded():
            logger.warning("Daily Gemini cost limit exceeded - skipping generation")
            return None

        # Vertex AI Image Generation endpoint
        # Note: This requires GCP project ID - using placeholder for now
        # In production, this would be configured via environment variable
        endpoint = (
            "https://us-central1-aiplatform.googleapis.com/v1/projects/"
            "{project}/locations/us-central1/publishers/google/models/imagegeneration:predict"
        )

        request_body = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
                "negativePrompt": "low quality, blurry, distorted, text, watermark, signature",
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_adult"
            }
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Gemini Imagen API (attempt {attempt + 1}/{max_retries})")

                response = requests.post(
                    endpoint,
                    json=request_body,
                    headers=headers,
                    timeout=60
                )
                response.raise_for_status()

                # Parse response
                result = response.json()

                # Extract base64 encoded image
                if 'predictions' in result and len(result['predictions']) > 0:
                    prediction = result['predictions'][0]

                    # Handle different response formats
                    if 'bytesBase64Encoded' in prediction:
                        image_base64 = prediction['bytesBase64Encoded']
                    elif 'image' in prediction:
                        image_base64 = prediction['image'].get('bytesBase64Encoded', '')
                    else:
                        logger.error("Unexpected Gemini API response format")
                        return None

                    # Decode base64 image
                    image_data = base64.b64decode(image_base64)

                    # Record usage
                    self.record_gemini_usage(article_id=None, cost=self.gemini_cost_per_image)

                    logger.info("✓ Successfully generated image with Gemini")

                    return {
                        'image_data': image_data,
                        'prompt': prompt,
                        'source_type': 'generated',
                        'attribution': 'AI-generated image via Google Gemini Imagen',
                        'license': 'Generated content - Editorial use'
                    }
                else:
                    logger.error("No predictions in Gemini API response")
                    return None

            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff: 2^attempt seconds
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded for Gemini API")
                    return None

        return None

    # ========================================
    # Stock Photo Search
    # ========================================

    def search_stock_photos(self, query: str) -> Optional[Dict]:
        """
        Search stock photo APIs (Unsplash, Pexels) for relevant images.

        Args:
            query: Search query (usually article headline keywords)

        Returns:
            Dict with stock photo data and metadata, or None on failure
        """
        # Try Unsplash first (higher quality, better licensing)
        if self.unsplash_key:
            result = self._search_unsplash(query)
            if result:
                return result

        # Try Pexels as backup
        if self.pexels_key:
            result = self._search_pexels(query)
            if result:
                return result

        logger.warning(f"No stock photos found for query: {query}")
        return None

    def _search_unsplash(self, query: str) -> Optional[Dict]:
        """Search Unsplash for relevant image"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
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

                # Download image
                image_data = self.download_image(photo['urls']['regular'])
                if not image_data:
                    return None

                return {
                    'url': photo['urls']['regular'],
                    'image_data': image_data,
                    'source_type': 'stock',
                    'attribution': f"Photo by {photo['user']['name']} on Unsplash",
                    'photographer': photo['user']['name'],
                    'platform': 'Unsplash',
                    'license': 'Unsplash License - Free to use'
                }

        except Exception as e:
            logger.error(f"Unsplash search failed: {e}")

        return None

    def _search_pexels(self, query: str) -> Optional[Dict]:
        """Search Pexels for relevant image"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_key}
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

                # Download image
                image_data = self.download_image(photo['src']['large'])
                if not image_data:
                    return None

                return {
                    'url': photo['src']['large'],
                    'image_data': image_data,
                    'source_type': 'stock',
                    'attribution': f"Photo by {photo['photographer']} on Pexels",
                    'photographer': photo['photographer'],
                    'platform': 'Pexels',
                    'license': 'Pexels License - Free to use'
                }

        except Exception as e:
            logger.error(f"Pexels search failed: {e}")

        return None

    # ========================================
    # Cascading Fallback Logic
    # ========================================

    def source_image_cascading(self, article: Dict) -> Dict:
        """
        Execute cascading image sourcing strategy.

        Strategy:
        1. Try source extraction (if source_url provided)
        2. Try Gemini generation
        3. Try stock photos
        4. Use category-specific placeholder

        Args:
            article: Dict with article data (title, summary, category, source_url, etc.)

        Returns:
            Dict with image data, always returns something (placeholder if all else fails)
        """
        logger.info(f"Starting cascading image source for: {article.get('title', 'Unknown')[:50]}")

        # Step 1: Try source extraction
        if article.get('source_url'):
            logger.info("Step 1: Attempting source extraction...")
            result = self.extract_from_source(article['source_url'])
            if result:
                logger.info("✓ Source extraction successful")
                return result
            logger.info("✗ Source extraction failed, continuing cascade")
        else:
            logger.info("Step 1: No source URL - skipping source extraction")

        # Step 2: Try Gemini generation
        logger.info("Step 2: Attempting Gemini image generation...")
        prompt = self.generate_gemini_prompt(
            headline=article.get('title', article.get('headline', '')),
            summary=article.get('summary', ''),
            category=article.get('category', 'news'),
            is_opinion=article.get('is_opinion', False)
        )

        result = self.generate_with_gemini(prompt)
        if result:
            logger.info("✓ Gemini generation successful")
            return result
        logger.info("✗ Gemini generation failed, continuing cascade")

        # Step 3: Try stock photos
        logger.info("Step 3: Attempting stock photo search...")
        # Extract keywords from headline for search
        search_query = article.get('title', article.get('headline', ''))[:100]
        result = self.search_stock_photos(search_query)
        if result:
            logger.info("✓ Stock photo search successful")
            return result
        logger.info("✗ Stock photo search failed, using placeholder")

        # Step 4: Category-specific placeholder
        logger.info("Step 4: Using category-specific placeholder")
        category = article.get('category', 'news')
        placeholder_map = {
            'labor': '/static/images/placeholder-labor.jpg',
            'politics': '/static/images/placeholder-politics.jpg',
            'economy': '/static/images/placeholder-economy.jpg',
            'environment': '/static/images/placeholder-environment.jpg',
            'healthcare': '/static/images/placeholder-healthcare.jpg',
            'education': '/static/images/placeholder-education.jpg',
            'housing': '/static/images/placeholder-housing.jpg',
            'opinion': '/static/images/placeholder-opinion.jpg',
            'sports': '/static/images/placeholder-sports.jpg'
        }

        placeholder_url = placeholder_map.get(category, '/static/images/placeholder.jpg')

        return {
            'url': placeholder_url,
            'image_data': None,  # Placeholder already exists on disk
            'source_type': 'placeholder',
            'attribution': 'Placeholder image',
            'license': 'Default placeholder'
        }

    # ========================================
    # Image Optimization & Storage
    # ========================================

    def optimize_image(
        self,
        image_data: bytes,
        max_width: int = 1200,
        quality: int = 85
    ) -> bytes:
        """
        Optimize image size and quality.

        Args:
            image_data: Raw image binary data
            max_width: Maximum width in pixels
            quality: JPEG quality (1-100)

        Returns:
            Optimized image binary data
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL not available - returning unoptimized image")
            return image_data

        try:
            # Open image
            img = Image.open(BytesIO(image_data))

            # Convert RGBA/palette to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')

            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {max_width}x{new_height}")

            # Save optimized
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            optimized_data = output.getvalue()

            # Log size reduction
            original_size = len(image_data) / 1024  # KB
            optimized_size = len(optimized_data) / 1024  # KB
            savings = ((original_size - optimized_size) / original_size) * 100
            logger.info(f"Image optimized: {original_size:.1f}KB → {optimized_size:.1f}KB ({savings:.1f}% reduction)")

            return optimized_data

        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return image_data

    def save_image(self, image_data: bytes, filename: str) -> str:
        """
        Save image to local storage.

        Args:
            image_data: Image binary data
            filename: Filename (e.g., "abc123.jpg")

        Returns:
            Relative path for database storage
        """
        try:
            file_path = self.storage_path / filename
            with open(file_path, 'wb') as f:
                f.write(image_data)

            # Return relative path for storage in DB
            return f"static/images/{filename}"

        except Exception as e:
            logger.error(f"Failed to save image {filename}: {e}")
            return ""

    # ========================================
    # Cost Tracking & Optimization
    # ========================================

    def record_gemini_usage(self, article_id: Optional[int], cost: float):
        """Record Gemini API usage for cost tracking"""
        # Reset daily stats if new day
        if datetime.now().date() > self._usage_stats['last_reset']:
            self._usage_stats = {
                'gemini_calls': 0,
                'gemini_cost': 0.0,
                'last_reset': datetime.now().date()
            }

        self._usage_stats['gemini_calls'] += 1
        self._usage_stats['gemini_cost'] += cost

        logger.info(
            f"Gemini usage: {self._usage_stats['gemini_calls']} calls, "
            f"${self._usage_stats['gemini_cost']:.2f} today"
        )

    def is_daily_limit_exceeded(self) -> bool:
        """Check if daily Gemini cost limit exceeded"""
        return self._usage_stats['gemini_cost'] >= self.daily_cost_limit

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return self._usage_stats.copy()

    def get_source_priorities(self) -> List[str]:
        """Get priority order of image sources (for cost optimization)"""
        return ['extracted', 'generated', 'stock', 'placeholder']

    # ========================================
    # Attribution & Licensing
    # ========================================

    def generate_attribution(self, result: Dict) -> str:
        """
        Generate proper attribution text for image.

        Args:
            result: Dict with image metadata

        Returns:
            Attribution string
        """
        source_type = result.get('source_type', 'unknown')

        if source_type == 'extracted':
            domain = result.get('source_domain', 'source')
            return f"Image from {domain}"

        elif source_type == 'generated':
            return "AI-generated image via Google Gemini Imagen"

        elif source_type == 'stock':
            photographer = result.get('photographer', 'Unknown')
            platform = result.get('platform', 'Stock photo')
            return f"Photo by {photographer} on {platform}"

        elif source_type == 'placeholder':
            return "Placeholder image"

        return "Image source unknown"

    def get_license_info(self, source_type: str, platform: Optional[str] = None) -> str:
        """
        Get licensing information for image source type.

        Args:
            source_type: Type of image source
            platform: Platform name (for stock photos)

        Returns:
            License information string
        """
        licenses = {
            'extracted': 'Fair use - Editorial content',
            'generated': 'Generated content - Editorial use',
            'placeholder': 'Default placeholder',
            'stock': {
                'Unsplash': 'Unsplash License - Free to use',
                'Pexels': 'Pexels License - Free to use',
                'default': 'Stock photo license'
            }
        }

        if source_type == 'stock' and platform:
            stock_licenses = licenses.get('stock', {})
            return stock_licenses.get(platform, stock_licenses.get('default', ''))

        return licenses.get(source_type, 'Unknown license')


# Convenience function for single article processing
def source_image_for_article(article_data: Dict) -> Dict:
    """
    Convenience function to source image for a single article.

    Args:
        article_data: Dict with article information

    Returns:
        Dict with image data and metadata
    """
    agent = ImageSourcingAgent()
    return agent.source_image_cascading(article_data)
