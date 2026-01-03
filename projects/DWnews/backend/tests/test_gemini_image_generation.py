"""
The Daily Worker - Gemini 2.5 Flash Image Generation Tests

Test-driven development for new Gemini image generation service.
Tests are written FIRST, then implementation follows.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from PIL import Image


class TestGeminiImageGeneration:
    """Test suite for Gemini 2.5 Flash Image generation"""

    def test_service_initialization(self):
        """Test that service initializes correctly with API key"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure') as mock_configure:
            service = GeminiImageService(api_key="test_key_123")

            # Verify Gemini was configured with correct API key
            mock_configure.assert_called_once_with(api_key="test_key_123")
            assert service is not None

    def test_service_initialization_without_api_key(self):
        """Test that service handles missing API key gracefully"""
        from backend.services.image_generation import GeminiImageService

        with pytest.raises(ValueError, match="Gemini API key is required"):
            GeminiImageService(api_key=None)

    def test_generate_image_basic(self):
        """Test basic image generation with valid prompt"""
        from backend.services.image_generation import GeminiImageService

        # Create mock response
        mock_pil_image = Image.new('RGB', (1024, 576), color='red')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(
                    prompt="Documentary photo of workers",
                    aspect_ratio="16:9"
                )

                # Verify result structure
                assert result is not None
                assert 'image_data' in result
                assert 'source_type' in result
                assert 'attribution' in result
                assert result['source_type'] == 'generated'

                # Verify image data is bytes
                assert isinstance(result['image_data'], bytes)
                assert len(result['image_data']) > 100  # Non-empty image

    def test_generate_image_with_parameters(self):
        """Test image generation with all parameters specified"""
        from backend.services.image_generation import GeminiImageService

        mock_pil_image = Image.new('RGB', (1024, 576), color='blue')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(
                    prompt="Test prompt",
                    aspect_ratio="16:9",
                    negative_prompt="blurry, low quality",
                    guidance_scale=7.5,
                    number_of_images=1
                )

                # Verify model.generate_images was called with correct params
                mock_model.generate_images.assert_called_once()
                call_kwargs = mock_model.generate_images.call_args[1]

                assert call_kwargs['prompt'] == "Test prompt"
                assert call_kwargs['aspect_ratio'] == "16:9"
                assert call_kwargs['negative_prompt'] == "blurry, low quality"
                assert call_kwargs['guidance_scale'] == 7.5
                assert call_kwargs['number_of_images'] == 1

    def test_generate_image_safety_filter_blocked(self):
        """Test handling of safety filter blocking"""
        from backend.services.image_generation import GeminiImageService

        mock_response = MagicMock()
        mock_response.prompt_feedback.block_reason = "SAFETY"

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="inappropriate content")

                # Should return None when blocked
                assert result is None

    def test_generate_image_api_error(self):
        """Test handling of API errors"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.side_effect = Exception("API Error")
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="test")

                # Should return None on error
                assert result is None

    def test_generate_image_with_retry(self):
        """Test retry logic on transient failures"""
        from backend.services.image_generation import GeminiImageService

        mock_pil_image = Image.new('RGB', (1024, 576), color='green')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_success_response = MagicMock()
        mock_success_response.images = [mock_image]
        mock_success_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                # First call fails, second succeeds
                mock_model.generate_images.side_effect = [
                    Exception("Temporary error"),
                    mock_success_response
                ]
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key", max_retries=2)
                result = service.generate_image(prompt="test")

                # Should succeed after retry
                assert result is not None
                assert result['image_data'] is not None
                assert mock_model.generate_images.call_count == 2

    def test_prompt_length_validation(self):
        """Test that prompts over 2000 characters are truncated"""
        from backend.services.image_generation import GeminiImageService

        mock_pil_image = Image.new('RGB', (1024, 576), color='yellow')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")

                # Create prompt longer than 2000 chars
                long_prompt = "A" * 2500
                result = service.generate_image(prompt=long_prompt)

                # Verify prompt was truncated
                call_kwargs = mock_model.generate_images.call_args[1]
                actual_prompt = call_kwargs['prompt']
                assert len(actual_prompt) <= 2000
                assert actual_prompt.endswith("...")

    def test_aspect_ratio_validation(self):
        """Test that only valid aspect ratios are accepted"""
        from backend.services.image_generation import GeminiImageService

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel'):
                service = GeminiImageService(api_key="test_key")

                # Invalid aspect ratio should raise ValueError
                with pytest.raises(ValueError, match="Invalid aspect ratio"):
                    service.generate_image(
                        prompt="test",
                        aspect_ratio="invalid"
                    )

    def test_image_bytes_conversion(self):
        """Test that PIL Image is correctly converted to bytes"""
        from backend.services.image_generation import GeminiImageService

        # Create a real PIL image
        test_image = Image.new('RGB', (100, 100), color='red')
        mock_image = MagicMock()
        mock_image._pil_image = test_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="test")

                # Verify we can load the bytes back as an image
                image_bytes = result['image_data']
                loaded_image = Image.open(BytesIO(image_bytes))
                assert loaded_image.size == (100, 100)
                assert loaded_image.mode == 'RGB'

    def test_default_parameters(self):
        """Test that default parameters are correctly applied"""
        from backend.services.image_generation import GeminiImageService

        mock_pil_image = Image.new('RGB', (1024, 576), color='white')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="test")

                # Check defaults were applied
                call_kwargs = mock_model.generate_images.call_args[1]
                assert call_kwargs['aspect_ratio'] == "16:9"
                assert call_kwargs['number_of_images'] == 1
                assert 'negative_prompt' in call_kwargs

    def test_attribution_metadata(self):
        """Test that proper attribution and metadata are included"""
        from backend.services.image_generation import GeminiImageService

        mock_pil_image = Image.new('RGB', (1024, 576), color='black')
        mock_image = MagicMock()
        mock_image._pil_image = mock_pil_image

        mock_response = MagicMock()
        mock_response.images = [mock_image]
        mock_response.prompt_feedback.block_reason = None

        with patch('google.generativeai.configure'):
            with patch('google.generativeai.GenerativeModel') as mock_model_class:
                mock_model = MagicMock()
                mock_model.generate_images.return_value = mock_response
                mock_model_class.return_value = mock_model

                service = GeminiImageService(api_key="test_key")
                result = service.generate_image(prompt="test")

                # Verify attribution metadata
                assert 'attribution' in result
                assert 'Google Gemini' in result['attribution']
                assert 'license' in result
                assert result['source_type'] == 'generated'


class TestGeminiImageIntegration:
    """Integration tests for Gemini image generation (require API key)"""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration test - requires valid API key")
    def test_real_api_call(self):
        """Test real API call to Gemini (requires valid API key in env)"""
        import os
        from backend.services.image_generation import GeminiImageService

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")

        service = GeminiImageService(api_key=api_key)
        result = service.generate_image(
            prompt="A simple red square on white background",
            aspect_ratio="1:1"
        )

        assert result is not None
        assert len(result['image_data']) > 1000
        assert result['source_type'] == 'generated'
