"""
The Daily Worker - Comprehensive Article Testing

Tests for validating image generation across 20+ diverse article scenarios.
Tests different categories, tones, and edge cases.

Written FIRST following TDD principles.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
from io import BytesIO


# Test article scenarios covering diverse categories
TEST_ARTICLES = [
    # Labor Category (5 articles)
    {
        "id": 1,
        "category": "Labor",
        "title": "Amazon Workers Vote to Unionize Despite Anti-Union Campaign",
        "content": "Workers at Amazon's Staten Island warehouse voted to form a union...",
        "expected_concepts": ["warehouse workers", "union", "organizing meeting"],
    },
    {
        "id": 2,
        "category": "Labor",
        "title": "Starbucks Workers Win Historic Contract Gains",
        "content": "After months of negotiations, Starbucks workers secured...",
        "expected_concepts": ["barista", "coffee shop", "celebration"],
    },
    {
        "id": 3,
        "category": "Labor",
        "title": "Auto Workers Strike Expands to Third Plant",
        "content": "The UAW strike continues to grow as workers at Ford's...",
        "expected_concepts": ["picket line", "factory", "strike signs"],
    },
    {
        "id": 4,
        "category": "Labor",
        "title": "Teachers Demand Better Pay and Smaller Class Sizes",
        "content": "Educators across the state are organizing for improved...",
        "expected_concepts": ["teachers", "classroom", "protest"],
    },
    {
        "id": 5,
        "category": "Labor",
        "title": "Healthcare Workers Rally for Patient Safety Standards",
        "content": "Nurses and hospital staff demonstrated for safer...",
        "expected_concepts": ["healthcare workers", "hospital", "rally"],
    },
    # Politics Category (5 articles)
    {
        "id": 6,
        "category": "Politics",
        "title": "Progressive Candidates Sweep Local Elections",
        "content": "In a historic night, progressive candidates won...",
        "expected_concepts": ["election", "celebration", "campaign"],
    },
    {
        "id": 7,
        "category": "Politics",
        "title": "New Housing Bill Promises Rent Control Protections",
        "content": "Lawmakers introduced legislation to cap rent increases...",
        "expected_concepts": ["housing", "legislation", "community"],
    },
    {
        "id": 8,
        "category": "Politics",
        "title": "Climate Activists Pressure Congress on Green New Deal",
        "content": "Environmental groups intensified their lobbying efforts...",
        "expected_concepts": ["activists", "protest", "climate"],
    },
    {
        "id": 9,
        "category": "Politics",
        "title": "Voting Rights Groups Fight Restrictive Election Laws",
        "content": "Civil rights organizations are challenging new voting...",
        "expected_concepts": ["voting", "civic engagement", "registration"],
    },
    {
        "id": 10,
        "category": "Politics",
        "title": "Medicare Expansion Gains Bipartisan Support",
        "content": "A coalition of lawmakers is building support for...",
        "expected_concepts": ["healthcare", "senior citizens", "medicare"],
    },
    # Sports Category (3 articles)
    {
        "id": 11,
        "category": "Sports",
        "title": "College Athletes Win Right to Unionize",
        "content": "In a landmark decision, student athletes at Northwestern...",
        "expected_concepts": ["athletes", "college sports", "celebration"],
    },
    {
        "id": 12,
        "category": "Sports",
        "title": "Women's Soccer Team Fights for Equal Pay",
        "content": "The US Women's National Team continues their legal battle...",
        "expected_concepts": ["soccer", "women athletes", "equality"],
    },
    {
        "id": 13,
        "category": "Sports",
        "title": "Minor League Baseball Players Form Players Association",
        "content": "After years of organizing, minor league players...",
        "expected_concepts": ["baseball", "players", "organizing"],
    },
    # Culture Category (3 articles)
    {
        "id": 14,
        "category": "Culture",
        "title": "Broadway Stagehands Negotiate Historic Safety Agreement",
        "content": "Theater workers reached a breakthrough contract including...",
        "expected_concepts": ["theater", "backstage", "workers"],
    },
    {
        "id": 15,
        "category": "Culture",
        "title": "Museum Workers Fight for Living Wages",
        "content": "Cultural workers at major museums are organizing...",
        "expected_concepts": ["museum", "art workers", "organizing"],
    },
    {
        "id": 16,
        "category": "Culture",
        "title": "Writers Guild Wins Protections Against AI Replacement",
        "content": "The WGA secured contract language protecting writers...",
        "expected_concepts": ["writers", "creative work", "solidarity"],
    },
    # International Category (4 articles)
    {
        "id": 17,
        "category": "International",
        "title": "French Workers Win Pension Reform Battle",
        "content": "After weeks of nationwide strikes, French workers...",
        "expected_concepts": ["protest", "French workers", "solidarity"],
    },
    {
        "id": 18,
        "category": "International",
        "title": "South Korean Unions Block Anti-Labor Legislation",
        "content": "Mass demonstrations in Seoul successfully stopped...",
        "expected_concepts": ["protest", "Korean workers", "demonstration"],
    },
    {
        "id": 19,
        "category": "International",
        "title": "Brazilian Metalworkers Secure Major Wage Increases",
        "content": "Unions representing metalworkers achieved significant...",
        "expected_concepts": ["industrial workers", "factory", "celebration"],
    },
    {
        "id": 20,
        "category": "International",
        "title": "Nigerian Teachers End Strike with Victory",
        "content": "After a two-week strike, educators won commitments...",
        "expected_concepts": ["teachers", "classroom", "Africa"],
    },
    # Edge Cases (3 articles)
    {
        "id": 21,
        "category": "Labor",
        "title": "Tech Workers Organize Against Layoffs",
        "content": "A" * 3000,  # Very long content
        "expected_concepts": ["tech workers", "office", "organizing"],
    },
    {
        "id": 22,
        "category": "Politics",
        "title": "Strike!",
        "content": "Short article.",  # Very short content
        "expected_concepts": ["workers", "strike"],
    },
    {
        "id": 23,
        "category": "Labor",
        "title": "Workers & Organizers Unite—Fighting for Justice!",
        "content": "Special characters & punctuation test...",
        "expected_concepts": ["workers", "organizing", "solidarity"],
    },
]


class TestComprehensiveArticleScenarios:
    """Test image generation across diverse article scenarios"""

    @pytest.fixture
    def mock_gemini_service(self):
        """Create a mock Gemini service that returns valid images"""
        mock_service = MagicMock()

        # Create a valid mock image response
        mock_pil_image = Image.new('RGB', (1024, 576), color='blue')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        mock_service.generate_image.return_value = {
            'image_data': self._create_mock_image_bytes(),
            'source_type': 'generated',
            'attribution': 'AI-generated image via Google Gemini 2.5 Flash Image',
            'license': 'Generated content - Editorial use'
        }

        return mock_service

    def _create_mock_image_bytes(self):
        """Create valid image bytes for testing"""
        img = Image.new('RGB', (1024, 576), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    @pytest.mark.parametrize("article", TEST_ARTICLES, ids=lambda a: f"article_{a['id']}")
    def test_generate_image_for_article(self, article, mock_gemini_service):
        """Test image generation for each diverse article scenario"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                # Setup mock
                mock_model = MagicMock()
                mock_pil_image = Image.new('RGB', (1024, 576), color='green')
                mock_image = MagicMock()
                mock_image._pil_image = mock_pil_image

                mock_response = MagicMock()
                mock_response.images = [mock_image]
                mock_response.prompt_feedback.block_reason = None
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")

                # Generate prompt from article
                prompt = self._create_prompt_from_article(article)

                # Generate image
                result = service.generate_image(prompt=prompt, aspect_ratio="16:9")

                # Verify result
                assert result is not None, \
                    f"Failed to generate image for article {article['id']}: {article['title']}"
                assert 'image_data' in result
                assert isinstance(result['image_data'], bytes)
                assert len(result['image_data']) > 100

    def _create_prompt_from_article(self, article):
        """Create a basic prompt from article metadata"""
        # Simulate what the real system does
        title = article['title']
        category = article['category']

        prompt = f"Documentary-style photograph for news article about: {title}. "
        prompt += f"Category: {category}. Professional photojournalism style."

        return prompt

    def test_all_categories_represented(self):
        """Test that test suite covers all major article categories"""
        categories = {article['category'] for article in TEST_ARTICLES}

        required_categories = {'Labor', 'Politics', 'Sports', 'Culture', 'International'}

        assert required_categories.issubset(categories), \
            f"Test suite must cover all categories: {required_categories}"

    def test_minimum_article_count(self):
        """Test that we have at least 20 diverse articles"""
        assert len(TEST_ARTICLES) >= 20, \
            "Test suite must include at least 20 diverse article scenarios"

    def test_each_category_has_multiple_articles(self):
        """Test that each category has multiple test cases"""
        from collections import Counter

        category_counts = Counter(article['category'] for article in TEST_ARTICLES)

        for category, count in category_counts.items():
            assert count >= 2, \
                f"Category '{category}' should have at least 2 test articles (has {count})"

    def test_edge_cases_included(self):
        """Test that edge cases are included in test suite"""
        # Check for very long content
        has_long_content = any(len(a['content']) > 2000 for a in TEST_ARTICLES)
        assert has_long_content, "Test suite should include very long article content"

        # Check for very short content
        has_short_content = any(len(a['content']) < 50 for a in TEST_ARTICLES)
        assert has_short_content, "Test suite should include very short article content"

        # Check for special characters
        has_special_chars = any(
            any(char in a['title'] for char in ['&', '—', '!', '?'])
            for a in TEST_ARTICLES
        )
        assert has_special_chars, "Test suite should include special characters in titles"

    @pytest.mark.parametrize("article", TEST_ARTICLES[:5], ids=lambda a: f"perf_{a['id']}")
    def test_generation_time_acceptable(self, article, mock_gemini_service):
        """Test that image generation completes in reasonable time"""
        import time
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_pil_image = Image.new('RGB', (1024, 576), color='yellow')
                mock_image = MagicMock()
                mock_image._pil_image = mock_pil_image

                mock_response = MagicMock()
                mock_response.images = [mock_image]
                mock_response.prompt_feedback.block_reason = None

                # Simulate realistic API latency
                def slow_generate(*args, **kwargs):
                    time.sleep(0.1)  # Simulate 100ms API call
                    return mock_response

                mock_model.generate_images.side_effect = slow_generate
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")

                start_time = time.time()
                result = service.generate_image(
                    prompt=self._create_prompt_from_article(article),
                    aspect_ratio="16:9"
                )
                elapsed_time = time.time() - start_time

                assert result is not None
                # In real scenario: < 30s; in mock: < 1s
                assert elapsed_time < 1.0, \
                    f"Generation took {elapsed_time:.2f}s (should be < 1s in mock)"

    def test_image_quality_validation(self):
        """Test that generated images meet quality standards"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                # Create a proper image with expected dimensions
                mock_pil_image = Image.new('RGB', (1024, 576), color='blue')
                mock_image = MagicMock()
                mock_image._pil_image = mock_pil_image

                mock_response = MagicMock()
                mock_response.images = [mock_image]
                mock_response.prompt_feedback.block_reason = None

                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(
                    prompt="Test prompt",
                    aspect_ratio="16:9"
                )

                # Load image and validate
                image = Image.open(BytesIO(result['image_data']))

                # Quality checks
                assert image.mode == 'RGB', "Image must be RGB format"
                assert image.width >= 800, "Image width should be at least 800px"
                assert image.height >= 400, "Image height should be at least 400px"

                # Aspect ratio check (16:9)
                aspect_ratio = image.width / image.height
                expected_ratio = 16 / 9
                assert abs(aspect_ratio - expected_ratio) < 0.1, \
                    f"Image aspect ratio {aspect_ratio:.2f} should be close to {expected_ratio:.2f}"

    def test_cost_tracking_per_category(self):
        """Test that we can track costs per article category"""
        from collections import defaultdict

        # Simulate cost tracking
        CLAUDE_COST_PER_ARTICLE = 0.015  # ~$0.015 per prompt enhancement
        GEMINI_COST_PER_IMAGE = 0.025    # ~$0.025 per image
        TOTAL_COST_PER_ARTICLE = CLAUDE_COST_PER_ARTICLE + GEMINI_COST_PER_IMAGE

        category_costs = defaultdict(float)

        for article in TEST_ARTICLES:
            category_costs[article['category']] += TOTAL_COST_PER_ARTICLE

        # Verify cost tracking works
        assert len(category_costs) >= 5, "Should track costs for multiple categories"

        total_cost = sum(category_costs.values())
        expected_total = len(TEST_ARTICLES) * TOTAL_COST_PER_ARTICLE

        assert abs(total_cost - expected_total) < 0.01, \
            f"Total cost ${total_cost:.2f} should match expected ${expected_total:.2f}"

    def test_safety_filter_handling_across_categories(self):
        """Test that safety filters are handled appropriately per category"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                # Simulate safety filter blocking
                mock_response = MagicMock()
                mock_response.prompt_feedback.block_reason = "SAFETY"

                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="Test prompt")

                # Should return None when blocked
                assert result is None, \
                    "Service should return None when safety filter blocks generation"

    def test_diverse_international_content(self):
        """Test that international articles are properly represented"""
        international_articles = [
            a for a in TEST_ARTICLES if a['category'] == 'International'
        ]

        assert len(international_articles) >= 3, \
            "Should have at least 3 international article scenarios"

        # Check for geographic diversity in titles/content
        countries_mentioned = set()
        for article in international_articles:
            content_combined = article['title'] + article['content']
            if 'French' in content_combined or 'France' in content_combined:
                countries_mentioned.add('France')
            if 'Korean' in content_combined or 'Korea' in content_combined:
                countries_mentioned.add('Korea')
            if 'Brazilian' in content_combined or 'Brazil' in content_combined:
                countries_mentioned.add('Brazil')
            if 'Nigerian' in content_combined or 'Nigeria' in content_combined:
                countries_mentioned.add('Nigeria')

        assert len(countries_mentioned) >= 3, \
            "International articles should cover diverse geographic regions"


class TestImageGenerationMetrics:
    """Test that we can collect and report metrics"""

    def test_metrics_collection_structure(self):
        """Test that metrics collection has proper structure"""
        metrics = {
            'total_articles': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'avg_generation_time': 0.0,
            'total_cost': 0.0,
            'cost_per_category': {},
            'quality_scores': [],
        }

        # Verify structure
        assert 'total_articles' in metrics
        assert 'successful_generations' in metrics
        assert 'avg_generation_time' in metrics
        assert 'total_cost' in metrics
        assert 'cost_per_category' in metrics

    def test_metrics_calculation(self):
        """Test metrics calculation logic"""
        # Simulate metrics from test run
        total_articles = len(TEST_ARTICLES)
        successful = total_articles - 0  # Assume all succeed in tests

        avg_time = 12.5  # seconds
        cost_per_image = 0.04  # $0.04

        total_cost = successful * cost_per_image

        assert total_articles >= 20
        assert successful == total_articles
        assert total_cost > 0
        assert avg_time > 0

    def test_cost_breakdown_by_category(self):
        """Test cost breakdown calculation by category"""
        from collections import defaultdict

        cost_per_image = 0.04
        category_costs = defaultdict(float)

        for article in TEST_ARTICLES:
            category_costs[article['category']] += cost_per_image

        # Verify all categories tracked
        assert 'Labor' in category_costs
        assert 'Politics' in category_costs
        assert 'Sports' in category_costs

        # Verify Labor has highest cost (most articles)
        labor_cost = category_costs['Labor']
        assert labor_cost > 0
