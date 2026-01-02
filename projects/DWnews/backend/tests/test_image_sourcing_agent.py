"""
The Daily Worker - Image Sourcing Agent Tests
Tests for image sourcing and generation functionality
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import base64
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.agents.image_sourcing_agent import ImageSourcingAgent


class TestSourceImageExtraction:
    """Test suite for source image extraction functionality"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    @pytest.fixture
    def mock_html_with_og_image(self):
        """Mock HTML with Open Graph image"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:image" content="https://example.com/image.jpg" />
            <meta property="og:image:url" content="https://example.com/image.jpg" />
            <meta property="og:image:width" content="1200" />
            <meta property="og:image:height" content="630" />
        </head>
        <body><h1>Article</h1></body>
        </html>
        """

    @pytest.fixture
    def mock_html_with_featured_image(self):
        """Mock HTML with featured image"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Article</title></head>
        <body>
            <article>
                <img class="featured-image" src="https://example.com/featured.jpg" alt="Featured" />
                <h1>Article Title</h1>
            </article>
        </body>
        </html>
        """

    @pytest.fixture
    def mock_html_with_twitter_image(self):
        """Mock HTML with Twitter Card image"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="twitter:image" content="https://example.com/twitter-image.jpg" />
            <meta name="twitter:card" content="summary_large_image" />
        </head>
        <body><h1>Article</h1></body>
        </html>
        """

    @pytest.fixture
    def mock_html_no_image(self):
        """Mock HTML without any images"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>No Images</title></head>
        <body><h1>Article</h1><p>Content</p></body>
        </html>
        """

    def test_extract_og_image_from_html(self, agent, mock_html_with_og_image):
        """Test extracting Open Graph image from HTML"""
        url = agent.extract_image_from_html(mock_html_with_og_image, "https://example.com/article")
        assert url == "https://example.com/image.jpg"

    def test_extract_featured_image_from_html(self, agent, mock_html_with_featured_image):
        """Test extracting featured image from HTML"""
        url = agent.extract_image_from_html(mock_html_with_featured_image, "https://example.com/article")
        assert url == "https://example.com/featured.jpg"

    def test_extract_twitter_image_from_html(self, agent, mock_html_with_twitter_image):
        """Test extracting Twitter Card image from HTML"""
        url = agent.extract_image_from_html(mock_html_with_twitter_image, "https://example.com/article")
        assert url == "https://example.com/twitter-image.jpg"

    def test_extract_no_image_returns_none(self, agent, mock_html_no_image):
        """Test that None is returned when no image found"""
        url = agent.extract_image_from_html(mock_html_no_image, "https://example.com/article")
        assert url is None

    @patch('requests.get')
    def test_download_source_image_success(self, mock_get, agent):
        """Test successful image download from source URL"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response

        # Test download
        image_data = agent.download_image("https://example.com/image.jpg")

        assert image_data is not None
        assert image_data == b'fake_image_data'
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_download_source_image_non_image_content(self, mock_get, agent):
        """Test that non-image content returns None"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_response.content = b'<html></html>'
        mock_get.return_value = mock_response

        # Test download
        image_data = agent.download_image("https://example.com/page.html")

        assert image_data is None

    @patch('requests.get')
    def test_download_source_image_404(self, mock_get, agent):
        """Test handling of 404 errors"""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response

        # Test download
        image_data = agent.download_image("https://example.com/missing.jpg")

        assert image_data is None

    @patch('requests.get')
    def test_extract_from_source_url_full_workflow(self, mock_get, agent):
        """Test complete source extraction workflow"""
        # Mock HTML page response
        html_response = Mock()
        html_response.status_code = 200
        html_response.headers = {'content-type': 'text/html'}
        html_response.text = """
        <html>
        <head>
            <meta property="og:image" content="https://example.com/og-image.jpg" />
        </head>
        <body><h1>Article</h1></body>
        </html>
        """

        # Mock image download response
        image_response = Mock()
        image_response.status_code = 200
        image_response.headers = {'content-type': 'image/jpeg'}
        image_response.content = b'fake_jpeg_data'

        # Setup mock to return different responses
        mock_get.side_effect = [html_response, image_response]

        # Test full extraction
        result = agent.extract_from_source("https://example.com/article")

        assert result is not None
        assert result['url'] == "https://example.com/og-image.jpg"
        assert result['image_data'] is not None
        assert result['source_type'] == 'extracted'
        assert 'example.com' in result['attribution']

    def test_relative_url_conversion(self, agent):
        """Test that relative image URLs are converted to absolute"""
        html = """
        <html>
        <head>
            <meta property="og:image" content="/images/article.jpg" />
        </head>
        <body></body>
        </html>
        """

        url = agent.extract_image_from_html(html, "https://example.com/article")
        assert url == "https://example.com/images/article.jpg"

    def test_image_priority_og_over_twitter(self, agent):
        """Test that Open Graph images have priority over Twitter images"""
        html = """
        <html>
        <head>
            <meta property="og:image" content="https://example.com/og.jpg" />
            <meta name="twitter:image" content="https://example.com/twitter.jpg" />
        </head>
        <body></body>
        </html>
        """

        url = agent.extract_image_from_html(html, "https://example.com/article")
        assert url == "https://example.com/og.jpg"

    def test_image_priority_twitter_over_featured(self, agent):
        """Test that Twitter images have priority over featured images"""
        html = """
        <html>
        <head>
            <meta name="twitter:image" content="https://example.com/twitter.jpg" />
        </head>
        <body>
            <img class="featured" src="https://example.com/featured.jpg" />
        </body>
        </html>
        """

        url = agent.extract_image_from_html(html, "https://example.com/article")
        assert url == "https://example.com/twitter.jpg"


class TestGeminiImageGeneration:
    """Test suite for Google Gemini Imagen integration"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    @pytest.fixture
    def mock_article_data(self):
        """Mock article data for testing"""
        return {
            'headline': "Local Workers Win Union Recognition at Amazon Warehouse",
            'summary': "Workers at a Queens warehouse vote 2-1 in favor of union representation",
            'category': 'labor',
            'is_opinion': False
        }

    @pytest.fixture
    def mock_opinion_article_data(self):
        """Mock opinion article data for testing"""
        return {
            'headline': "Why Universal Healthcare Is a Workers' Right",
            'summary': "Healthcare should not depend on employment status",
            'category': 'opinion',
            'is_opinion': True
        }

    def test_generate_gemini_prompt_news_article(self, agent, mock_article_data):
        """Test prompt generation for news articles"""
        prompt = agent.generate_gemini_prompt(
            headline=mock_article_data['headline'],
            summary=mock_article_data['summary'],
            category=mock_article_data['category'],
            is_opinion=False
        )

        assert "Local Workers Win Union Recognition" in prompt
        assert "photojournalistic" in prompt.lower() or "news photo" in prompt.lower()
        assert "editorial cartoon" not in prompt.lower()

    def test_generate_gemini_prompt_opinion_article(self, agent, mock_opinion_article_data):
        """Test prompt generation for opinion articles"""
        prompt = agent.generate_gemini_prompt(
            headline=mock_opinion_article_data['headline'],
            summary=mock_opinion_article_data['summary'],
            category=mock_opinion_article_data['category'],
            is_opinion=True
        )

        assert "Universal Healthcare" in prompt
        assert "editorial" in prompt.lower() or "illustration" in prompt.lower()

    def test_generate_gemini_prompt_labor_category(self, agent):
        """Test that labor category gets worker-centric prompts"""
        prompt = agent.generate_gemini_prompt(
            headline="Factory Workers Strike for Better Conditions",
            summary="200 workers walk out demanding safety improvements",
            category="labor",
            is_opinion=False
        )

        assert "worker" in prompt.lower() or "labor" in prompt.lower()

    @patch('requests.post')
    def test_gemini_api_call_success(self, mock_post, agent):
        """Test successful Gemini API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200

        # Create fake image data
        fake_image = b'fake_generated_image_data'
        fake_base64 = base64.b64encode(fake_image).decode('utf-8')

        mock_response.json.return_value = {
            "predictions": [{
                "bytesBase64Encoded": fake_base64
            }]
        }
        mock_post.return_value = mock_response

        # Test API call
        result = agent.generate_with_gemini(
            prompt="Test prompt for news article",
            api_key="test_api_key"
        )

        assert result is not None
        assert result['image_data'] == fake_image
        assert result['prompt'] == "Test prompt for news article"
        assert result['source_type'] == 'generated'

    @patch('requests.post')
    def test_gemini_api_call_failure(self, mock_post, agent):
        """Test handling of Gemini API failures"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        # Test API call
        result = agent.generate_with_gemini(
            prompt="Test prompt",
            api_key="test_api_key"
        )

        assert result is None

    @patch('requests.post')
    def test_gemini_api_retry_logic(self, mock_post, agent):
        """Test retry logic with exponential backoff"""
        # Mock responses: fail twice, succeed third time
        fail_response = Mock()
        fail_response.status_code = 503
        fail_response.raise_for_status.side_effect = Exception("Service Unavailable")

        fake_image = b'fake_image'
        fake_base64 = base64.b64encode(fake_image).decode('utf-8')

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "predictions": [{"bytesBase64Encoded": fake_base64}]
        }

        mock_post.side_effect = [fail_response, fail_response, success_response]

        # Test with retries
        result = agent.generate_with_gemini(
            prompt="Test",
            api_key="test_key",
            max_retries=3
        )

        assert result is not None
        assert mock_post.call_count == 3


class TestCascadingFallbackLogic:
    """Test suite for cascading fallback logic"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    @pytest.fixture
    def article_with_source(self):
        """Mock article with source URL"""
        return {
            'id': 1,
            'title': "Test Article",
            'summary': "Test summary",
            'category': 'labor',
            'is_opinion': False,
            'source_url': "https://example.com/article"
        }

    @pytest.fixture
    def article_no_source(self):
        """Mock article without source URL"""
        return {
            'id': 2,
            'title': "Opinion Piece",
            'summary': "Test opinion",
            'category': 'opinion',
            'is_opinion': True,
            'source_url': None
        }

    @patch.object(ImageSourcingAgent, 'extract_from_source')
    @patch.object(ImageSourcingAgent, 'generate_with_gemini')
    @patch.object(ImageSourcingAgent, 'search_stock_photos')
    def test_cascade_source_success(self, mock_stock, mock_gemini, mock_source, agent, article_with_source):
        """Test cascade stops at source extraction when successful"""
        # Mock successful source extraction
        mock_source.return_value = {
            'url': 'https://example.com/image.jpg',
            'image_data': b'image_data',
            'source_type': 'extracted',
            'attribution': 'Source: example.com'
        }

        # Execute cascade
        result = agent.source_image_cascading(article_with_source)

        # Assert source extraction called, others not called
        mock_source.assert_called_once()
        mock_gemini.assert_not_called()
        mock_stock.assert_not_called()

        assert result['source_type'] == 'extracted'

    @patch.object(ImageSourcingAgent, 'extract_from_source')
    @patch.object(ImageSourcingAgent, 'generate_with_gemini')
    @patch.object(ImageSourcingAgent, 'search_stock_photos')
    def test_cascade_source_fail_gemini_success(self, mock_stock, mock_gemini, mock_source, agent, article_with_source):
        """Test cascade falls to Gemini when source extraction fails"""
        # Mock failed source extraction
        mock_source.return_value = None

        # Mock successful Gemini generation
        mock_gemini.return_value = {
            'image_data': b'generated_data',
            'prompt': 'Test prompt',
            'source_type': 'generated'
        }

        # Execute cascade
        result = agent.source_image_cascading(article_with_source)

        # Assert both called
        mock_source.assert_called_once()
        mock_gemini.assert_called_once()
        mock_stock.assert_not_called()

        assert result['source_type'] == 'generated'

    @patch.object(ImageSourcingAgent, 'extract_from_source')
    @patch.object(ImageSourcingAgent, 'generate_with_gemini')
    @patch.object(ImageSourcingAgent, 'search_stock_photos')
    def test_cascade_all_fail_stock_success(self, mock_stock, mock_gemini, mock_source, agent, article_with_source):
        """Test cascade falls to stock photos when source and Gemini fail"""
        # Mock failures
        mock_source.return_value = None
        mock_gemini.return_value = None

        # Mock successful stock search
        mock_stock.return_value = {
            'url': 'https://unsplash.com/photo',
            'image_data': b'stock_data',
            'source_type': 'stock',
            'attribution': 'Photo by John Doe on Unsplash'
        }

        # Execute cascade
        result = agent.source_image_cascading(article_with_source)

        # Assert all called
        mock_source.assert_called_once()
        mock_gemini.assert_called_once()
        mock_stock.assert_called_once()

        assert result['source_type'] == 'stock'

    @patch.object(ImageSourcingAgent, 'extract_from_source')
    @patch.object(ImageSourcingAgent, 'generate_with_gemini')
    @patch.object(ImageSourcingAgent, 'search_stock_photos')
    def test_cascade_all_fail_placeholder(self, mock_stock, mock_gemini, mock_source, agent, article_with_source):
        """Test cascade uses placeholder when all methods fail"""
        # Mock all failures
        mock_source.return_value = None
        mock_gemini.return_value = None
        mock_stock.return_value = None

        # Execute cascade
        result = agent.source_image_cascading(article_with_source)

        # Assert all called
        mock_source.assert_called_once()
        mock_gemini.assert_called_once()
        mock_stock.assert_called_once()

        assert result['source_type'] == 'placeholder'
        assert 'placeholder' in result['url']

    @patch.object(ImageSourcingAgent, 'extract_from_source')
    @patch.object(ImageSourcingAgent, 'generate_with_gemini')
    def test_cascade_no_source_url_skips_extraction(self, mock_gemini, mock_source, agent, article_no_source):
        """Test cascade skips source extraction when no source URL"""
        # Mock successful Gemini
        mock_gemini.return_value = {
            'image_data': b'generated',
            'prompt': 'Test',
            'source_type': 'generated'
        }

        # Execute cascade
        result = agent.source_image_cascading(article_no_source)

        # Assert source NOT called
        mock_source.assert_not_called()
        mock_gemini.assert_called_once()


class TestImageOptimization:
    """Test suite for image optimization and storage"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    @pytest.fixture
    def sample_jpeg_data(self):
        """Create sample JPEG data for testing"""
        # This is minimal valid JPEG data
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'

    def test_optimize_image_resizes_large_images(self, agent):
        """Test that images larger than max width are resized"""
        # This test requires PIL - will be skipped if not available
        pytest.importorskip("PIL")

        from PIL import Image

        # Create large test image
        large_image = Image.new('RGB', (2400, 1600), color='red')
        buffer = BytesIO()
        large_image.save(buffer, format='JPEG')
        large_data = buffer.getvalue()

        # Optimize
        optimized = agent.optimize_image(large_data, max_width=1200)

        # Verify resized
        optimized_img = Image.open(BytesIO(optimized))
        assert optimized_img.width == 1200
        assert optimized_img.height == 800  # Maintains aspect ratio

    def test_optimize_image_converts_rgba_to_rgb(self, agent):
        """Test that RGBA images are converted to RGB"""
        pytest.importorskip("PIL")

        from PIL import Image

        # Create RGBA image
        rgba_image = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
        buffer = BytesIO()
        rgba_image.save(buffer, format='PNG')
        rgba_data = buffer.getvalue()

        # Optimize
        optimized = agent.optimize_image(rgba_data)

        # Verify RGB
        optimized_img = Image.open(BytesIO(optimized))
        assert optimized_img.mode == 'RGB'

    def test_save_image_to_storage(self, agent, tmp_path, sample_jpeg_data):
        """Test saving image to local storage"""
        # Override storage path for testing
        agent.storage_path = tmp_path

        # Save image
        saved_path = agent.save_image(sample_jpeg_data, "test_image.jpg")

        # Verify file exists
        assert saved_path is not None
        file_path = tmp_path / "test_image.jpg"
        assert file_path.exists()
        assert file_path.read_bytes() == sample_jpeg_data


class TestCostTracking:
    """Test suite for cost tracking and optimization"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    def test_cost_tracking_gemini_usage(self, agent):
        """Test that Gemini API usage is tracked"""
        # Record usage
        agent.record_gemini_usage(article_id=1, cost=0.03)

        # Verify tracked
        stats = agent.get_usage_stats()
        assert stats['gemini_calls'] == 1
        assert stats['gemini_cost'] == 0.03

    def test_cost_tracking_daily_limit(self, agent):
        """Test that daily cost limits are enforced"""
        # Set low daily limit
        agent.daily_cost_limit = 0.10

        # Record several uses
        agent.record_gemini_usage(article_id=1, cost=0.04)
        agent.record_gemini_usage(article_id=2, cost=0.04)
        agent.record_gemini_usage(article_id=3, cost=0.04)

        # Check if limit exceeded
        assert agent.is_daily_limit_exceeded() is True

    def test_cost_optimization_prefers_source_over_gemini(self, agent):
        """Test that cost optimization prefers free sources"""
        # Verify priority order reflects cost optimization
        priorities = agent.get_source_priorities()

        assert priorities.index('extracted') < priorities.index('generated')
        assert priorities.index('generated') < priorities.index('stock')


class TestAttributionCompliance:
    """Test suite for proper attribution and licensing"""

    @pytest.fixture
    def agent(self):
        """Create ImageSourcingAgent instance for testing"""
        return ImageSourcingAgent()

    def test_attribution_extracted_image(self, agent):
        """Test attribution for extracted source images"""
        result = {
            'source_type': 'extracted',
            'url': 'https://example.com/image.jpg',
            'source_domain': 'example.com'
        }

        attribution = agent.generate_attribution(result)

        assert 'example.com' in attribution
        assert 'Source:' in attribution or 'Image from' in attribution

    def test_attribution_gemini_image(self, agent):
        """Test attribution for AI-generated images"""
        result = {
            'source_type': 'generated',
            'prompt': 'Test prompt'
        }

        attribution = agent.generate_attribution(result)

        assert 'AI-generated' in attribution or 'Generated by' in attribution

    def test_attribution_stock_unsplash(self, agent):
        """Test attribution for Unsplash images"""
        result = {
            'source_type': 'stock',
            'photographer': 'John Doe',
            'platform': 'Unsplash'
        }

        attribution = agent.generate_attribution(result)

        assert 'John Doe' in attribution
        assert 'Unsplash' in attribution

    def test_attribution_stock_pexels(self, agent):
        """Test attribution for Pexels images"""
        result = {
            'source_type': 'stock',
            'photographer': 'Jane Smith',
            'platform': 'Pexels'
        }

        attribution = agent.generate_attribution(result)

        assert 'Jane Smith' in attribution
        assert 'Pexels' in attribution

    def test_licensing_info_extracted(self, agent):
        """Test license information for extracted images"""
        license_info = agent.get_license_info('extracted')

        assert license_info is not None
        assert 'Fair use' in license_info or 'Editorial use' in license_info

    def test_licensing_info_stock(self, agent):
        """Test license information for stock photos"""
        license_info = agent.get_license_info('stock', platform='Unsplash')

        assert license_info is not None
        assert 'Unsplash License' in license_info or 'Free to use' in license_info
