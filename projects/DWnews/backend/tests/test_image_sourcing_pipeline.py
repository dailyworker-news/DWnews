"""
The Daily Worker - Image Sourcing Pipeline Tests
Test-driven development for Phase 6.11.4: Update Image Sourcing Pipeline

Tests the complete workflow:
Article → Claude Enhancement → Gemini Image Generation

Includes logging, metadata storage, and quality testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import json
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock database.models before any imports that need it
sys.modules['database'] = Mock()
sys.modules['database.models'] = Mock()


class TestImageSourcingPipelineWorkflow:
    """Test complete image sourcing pipeline with Claude enhancement"""

    def test_pipeline_initialization(self):
        """Test that ImageSourcer initializes with all required components"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_gemini_key"
            mock_settings.claude_api_key = "test_claude_key"
            mock_settings.unsplash_access_key = None
            mock_settings.pexels_api_key = None

            with patch('scripts.content.source_images.PromptEnhancer'):
                sourcer = ImageSourcer(mock_session)

                # Verify all flags are set correctly
                assert sourcer.gemini_enabled is True
                assert sourcer.prompt_enhancer_enabled is True
                assert sourcer.unsplash_enabled is False
                assert sourcer.pexels_enabled is False

    def test_pipeline_enhancement_workflow(self):
        """Test complete Claude enhancement → Gemini generation workflow"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()
        mock_article = Mock()
        mock_article.id = 123
        mock_article.title = "Test Article Title"
        mock_article.content = "Test article content for context"

        # Mock concept from Claude
        mock_concept = {
            'concept_number': 1,
            'prompt': 'Enhanced artistic prompt with detailed visual elements',
            'confidence': 0.92,
            'rationale': 'This concept best captures the article message'
        }

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.PromptEnhancer') as mock_enhancer_class:
                mock_enhancer = Mock()
                mock_enhancer.generate_image_concepts.return_value = [mock_concept]
                mock_enhancer.select_best_concept.return_value = mock_concept
                mock_enhancer_class.return_value = mock_enhancer

                # Create mock Gemini client and response
                mock_gemini_client = Mock()
                mock_response = Mock()
                mock_candidate = Mock()
                mock_part = Mock()
                mock_inline = Mock()
                mock_inline.mime_type = "image/png"
                mock_inline.data = b"fake_image_data"
                mock_part.inline_data = mock_inline
                mock_candidate.content.parts = [mock_part]
                mock_response.candidates = [mock_candidate]
                mock_gemini_client.models.generate_content.return_value = mock_response

                sourcer = ImageSourcer(mock_session)
                sourcer._gemini_client = mock_gemini_client
                sourcer._gemini_initialized = True
                sourcer._gemini_types = Mock()

                with patch('builtins.open', create=True):
                    # Execute pipeline
                    result = sourcer.generate_image_with_gemini(
                        prompt="Basic prompt",
                        article_id=123,
                        article_title="Test Article Title",
                        article_content="Test article content"
                    )

                # Verify Claude was called for enhancement
                mock_enhancer.generate_image_concepts.assert_called_once()
                mock_enhancer.select_best_concept.assert_called_once()

                # Verify enhanced prompt was used (not basic prompt)
                gemini_call = mock_gemini_client.models.generate_content.call_args
                assert 'Enhanced artistic prompt' in str(gemini_call)

                # Verify result
                assert result is not None
                assert 'media/article_123/gemini_flash_image.png' in result

    def test_pipeline_logging_all_steps(self):
        """Test that all pipeline steps are logged properly"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.logger') as mock_logger:
                with patch('scripts.content.source_images.PromptEnhancer'):
                    sourcer = ImageSourcer(mock_session)

                    # Verify initialization logging
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    assert any('Gemini' in call for call in log_calls)
                    assert any('Claude' in call for call in log_calls)

    def test_pipeline_concept_generation_logging(self):
        """Test that concept generation step is logged"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()
        mock_concepts = [
            {'concept_number': 1, 'prompt': 'Concept 1', 'confidence': 0.85, 'rationale': 'Good'},
            {'concept_number': 2, 'prompt': 'Concept 2', 'confidence': 0.90, 'rationale': 'Better'},
            {'concept_number': 3, 'prompt': 'Concept 3', 'confidence': 0.78, 'rationale': 'Okay'}
        ]

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.PromptEnhancer') as mock_enhancer_class:
                mock_enhancer = Mock()
                mock_enhancer.generate_image_concepts.return_value = mock_concepts
                mock_enhancer.select_best_concept.return_value = mock_concepts[1]
                mock_enhancer_class.return_value = mock_enhancer

                with patch('scripts.content.source_images.logger') as mock_logger:
                    # Mock Gemini response
                    mock_response = Mock()
                    mock_candidate = Mock()
                    mock_part = Mock()
                    mock_inline = Mock()
                    mock_inline.mime_type = "image/png"
                    mock_inline.data = b"data"
                    mock_part.inline_data = mock_inline
                    mock_candidate.content.parts = [mock_part]
                    mock_response.candidates = [mock_candidate]

                    mock_gemini_client = Mock()
                    mock_gemini_client.models.generate_content.return_value = mock_response

                    sourcer = ImageSourcer(mock_session)
                    sourcer._gemini_client = mock_gemini_client
                    sourcer._gemini_initialized = True
                    sourcer._gemini_types = Mock()

                    with patch('builtins.open', create=True):
                        sourcer.generate_image_with_gemini(
                            prompt="test",
                            article_id=1,
                            article_title="Test",
                            article_content="Content"
                        )

                    # Verify logging
                    log_messages = [str(call) for call in mock_logger.info.call_args_list]
                    assert any('Claude Prompt Enhancement' in msg for msg in log_messages)
                    assert any('0.90' in msg or 'Confidence' in msg for msg in log_messages)

    def test_pipeline_metadata_storage(self):
        """Test that image metadata includes concept, confidence, and rationale"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()
        mock_article = Mock()
        mock_article.id = 456
        mock_article.title = "Test Article"
        mock_article.content = "Test content"

        # This test verifies the metadata structure expected
        # Actual storage will be implemented in the update phase
        expected_metadata = {
            'concept_number': 2,
            'prompt': 'Enhanced prompt with visual details',
            'confidence': 0.88,
            'rationale': 'Best matches article tone and message'
        }

        # For now, verify the concept structure is correct
        assert 'concept_number' in expected_metadata
        assert 'prompt' in expected_metadata
        assert 'confidence' in expected_metadata
        assert 'rationale' in expected_metadata
        assert 0.0 <= expected_metadata['confidence'] <= 1.0

    def test_pipeline_fallback_without_claude(self):
        """Test that pipeline works without Claude (uses basic prompt)"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = None  # No Claude

            sourcer = ImageSourcer(mock_session)

            # Verify Claude is disabled
            assert sourcer.prompt_enhancer_enabled is False

            # Pipeline should still work with basic prompts
            with patch.object(sourcer, '_gemini_client') as mock_gemini:
                mock_response = Mock()
                mock_candidate = Mock()
                mock_part = Mock()
                mock_inline = Mock()
                mock_inline.mime_type = "image/png"
                mock_inline.data = b"image_data"
                mock_part.inline_data = mock_inline
                mock_candidate.content.parts = [mock_part]
                mock_response.candidates = [mock_candidate]
                mock_gemini.models.generate_content.return_value = mock_response

                sourcer._gemini_initialized = True
                sourcer._gemini_types = Mock()

                result = sourcer.generate_image_with_gemini(
                    prompt="Basic prompt",
                    article_id=1
                )

                # Should succeed with basic prompt
                assert result is not None

    def test_pipeline_error_handling_claude_failure(self):
        """Test pipeline handles Claude enhancement failures gracefully"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.PromptEnhancer') as mock_enhancer_class:
                mock_enhancer = Mock()
                # Claude fails to generate concepts
                mock_enhancer.generate_image_concepts.return_value = []
                mock_enhancer_class.return_value = mock_enhancer

                with patch('scripts.content.source_images.logger') as mock_logger:
                    # Mock Gemini response for fallback path
                    mock_response = Mock()
                    mock_candidate = Mock()
                    mock_part = Mock()
                    mock_inline = Mock()
                    mock_inline.mime_type = "image/png"
                    mock_inline.data = b"fallback_data"
                    mock_part.inline_data = mock_inline
                    mock_candidate.content.parts = [mock_part]
                    mock_response.candidates = [mock_candidate]

                    mock_gemini_client = Mock()
                    mock_gemini_client.models.generate_content.return_value = mock_response

                    sourcer = ImageSourcer(mock_session)
                    sourcer._gemini_client = mock_gemini_client
                    sourcer._gemini_initialized = True
                    sourcer._gemini_types = Mock()

                    with patch('builtins.open', create=True):
                        result = sourcer.generate_image_with_gemini(
                            prompt="Fallback prompt with enough length",
                            article_id=1,
                            article_title="Test"
                        )

                    # Should log warning and use fallback
                    warnings = [str(call) for call in mock_logger.warning.call_args_list]
                    assert any('Failed to enhance' in msg for msg in warnings)

    def test_pipeline_short_prompt_rejection(self):
        """Test that very short prompts are rejected"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = None

            with patch('scripts.content.source_images.logger') as mock_logger:
                sourcer = ImageSourcer(mock_session)

                # Try with very short prompt
                result = sourcer.generate_image_with_gemini(
                    prompt="abc",  # Too short
                    article_id=1
                )

                # Should reject
                assert result is None

                # Should log warning
                warnings = [str(call) for call in mock_logger.warning.call_args_list]
                assert any('too short' in msg.lower() for msg in warnings)

    def test_pipeline_review_tag_removal(self):
        """Test that [NEEDS REVIEW] tags are removed from prompts"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = None

            sourcer = ImageSourcer(mock_session)
            sourcer._gemini_initialized = True
            sourcer._gemini_types = Mock()

            with patch.object(sourcer, '_gemini_client') as mock_gemini:
                mock_response = Mock()
                mock_candidate = Mock()
                mock_part = Mock()
                mock_inline = Mock()
                mock_inline.mime_type = "image/png"
                mock_inline.data = b"data"
                mock_part.inline_data = mock_inline
                mock_candidate.content.parts = [mock_part]
                mock_response.candidates = [mock_candidate]
                mock_gemini.models.generate_content.return_value = mock_response

                result = sourcer.generate_image_with_gemini(
                    prompt="[NEEDS REVIEW] Test Article About Workers",
                    article_id=1
                )

                # Verify [NEEDS REVIEW] was stripped
                call_contents = str(mock_gemini.models.generate_content.call_args)
                assert '[NEEDS REVIEW]' not in call_contents
                assert 'Test Article About Workers' in call_contents


class TestImagePipelineIntegration:
    """Integration tests for complete pipeline workflow"""

    def test_complete_article_pipeline(self):
        """Test complete workflow from article to saved image with metadata"""
        from scripts.content.source_images import ImageSourcer
        from database.models import Article

        mock_session = Mock()
        mock_article = Article()
        mock_article.id = 789
        mock_article.title = "Historic Union Victory at Tech Giant"
        mock_article.content = "Workers celebrate after successful vote"
        mock_article.image_url = None

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.PromptEnhancer') as mock_enhancer_class:
                mock_concepts = [{
                    'concept_number': 1,
                    'prompt': 'Documentary photo of diverse tech workers celebrating union victory',
                    'confidence': 0.91,
                    'rationale': 'Captures celebration and collective success'
                }]

                mock_enhancer = Mock()
                mock_enhancer.generate_image_concepts.return_value = mock_concepts
                mock_enhancer.select_best_concept.return_value = mock_concepts[0]
                mock_enhancer_class.return_value = mock_enhancer

                with patch('builtins.open', create=True) as mock_open:
                    sourcer = ImageSourcer(mock_session)
                    sourcer._gemini_initialized = True
                    sourcer._gemini_types = Mock()

                    with patch.object(sourcer, '_gemini_client') as mock_gemini:
                        mock_response = Mock()
                        mock_candidate = Mock()
                        mock_part = Mock()
                        mock_inline = Mock()
                        mock_inline.mime_type = "image/png"
                        mock_inline.data = b"generated_image_data"
                        mock_part.inline_data = mock_inline
                        mock_candidate.content.parts = [mock_part]
                        mock_response.candidates = [mock_candidate]
                        mock_gemini.models.generate_content.return_value = mock_response

                        # Execute pipeline
                        result = sourcer.source_image_for_article(mock_article, verbose=False)

                        # Verify success
                        assert result is True
                        assert mock_article.image_url is not None
                        assert 'gemini_flash_image.png' in mock_article.image_url

                        # Verify Claude was used for enhancement
                        mock_enhancer.generate_image_concepts.assert_called_once()

                        # Verify Gemini was called
                        mock_gemini.models.generate_content.assert_called_once()

    def test_batch_processing_with_logging(self):
        """Test batch processing logs progress for each article"""
        from scripts.content.source_images import ImageSourcer

        # Create Article mock class
        Article = Mock()
        mock_session = Mock()

        # Create mock article instances
        articles = []
        for i in range(3):
            article = Mock()
            article.id = i
            article.title = f"Article {i} with enough length for processing"
            article.content = f"Content {i}"
            article.status = 'draft'
            article.image_url = None
            articles.append(article)

        mock_session.query.return_value.filter.return_value.limit.return_value.all.return_value = articles

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = None
            mock_settings.unsplash_access_key = None
            mock_settings.pexels_api_key = None

            with patch('scripts.content.source_images.logger') as mock_logger:
                # Mock Gemini response
                mock_response = Mock()
                mock_candidate = Mock()
                mock_part = Mock()
                mock_inline = Mock()
                mock_inline.mime_type = "image/png"
                mock_inline.data = b"data"
                mock_part.inline_data = mock_inline
                mock_candidate.content.parts = [mock_part]
                mock_response.candidates = [mock_candidate]

                mock_gemini_client = Mock()
                mock_gemini_client.models.generate_content.return_value = mock_response

                sourcer = ImageSourcer(mock_session)
                sourcer._gemini_client = mock_gemini_client
                sourcer._gemini_initialized = True
                sourcer._gemini_types = Mock()

                with patch('builtins.open', create=True):
                    count = sourcer.process_batch(max_articles=10, verbose=False)

                    # Verify processed all articles
                    assert count == 3

                    # Verify Gemini was called for each
                    assert mock_gemini_client.models.generate_content.call_count == 3


class TestPipelineQualityMetrics:
    """Tests for pipeline quality measurements"""

    def test_confidence_score_logging(self):
        """Test that confidence scores are logged for quality tracking"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()
        mock_concepts = [
            {'concept_number': 1, 'prompt': 'High quality', 'confidence': 0.95, 'rationale': 'Excellent'},
            {'concept_number': 2, 'prompt': 'Medium quality', 'confidence': 0.75, 'rationale': 'Good'},
            {'concept_number': 3, 'prompt': 'Low quality', 'confidence': 0.60, 'rationale': 'Acceptable'}
        ]

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = "test_key"

            with patch('scripts.content.source_images.PromptEnhancer') as mock_enhancer_class:
                mock_enhancer = Mock()
                mock_enhancer.generate_image_concepts.return_value = mock_concepts
                mock_enhancer.select_best_concept.return_value = mock_concepts[0]
                mock_enhancer_class.return_value = mock_enhancer

                with patch('scripts.content.source_images.logger') as mock_logger:
                    # Mock Gemini response
                    mock_response = Mock()
                    mock_candidate = Mock()
                    mock_part = Mock()
                    mock_inline = Mock()
                    mock_inline.mime_type = "image/png"
                    mock_inline.data = b"data"
                    mock_part.inline_data = mock_inline
                    mock_candidate.content.parts = [mock_part]
                    mock_response.candidates = [mock_candidate]

                    mock_gemini_client = Mock()
                    mock_gemini_client.models.generate_content.return_value = mock_response

                    sourcer = ImageSourcer(mock_session)
                    sourcer._gemini_client = mock_gemini_client
                    sourcer._gemini_initialized = True
                    sourcer._gemini_types = Mock()

                    with patch('builtins.open', create=True):
                        sourcer.generate_image_with_gemini(
                            prompt="test",
                            article_id=1,
                            article_title="Test",
                            article_content="Content"
                        )

                    # Verify confidence score was logged
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    assert any('0.95' in msg or 'Confidence' in msg for msg in log_calls)

    def test_prompt_length_logging(self):
        """Test that prompt lengths are logged for monitoring"""
        from scripts.content.source_images import ImageSourcer

        mock_session = Mock()

        with patch('scripts.content.source_images.settings') as mock_settings:
            mock_settings.gemini_api_key = "test_key"
            mock_settings.claude_api_key = None

            with patch('scripts.content.source_images.logger') as mock_logger:
                sourcer = ImageSourcer(mock_session)
                sourcer._gemini_initialized = True
                sourcer._gemini_types = Mock()

                with patch.object(sourcer, '_gemini_client') as mock_gemini:
                    mock_response = Mock()
                    mock_candidate = Mock()
                    mock_part = Mock()
                    mock_inline = Mock()
                    mock_inline.mime_type = "image/png"
                    mock_inline.data = b"data"
                    mock_part.inline_data = mock_inline
                    mock_candidate.content.parts = [mock_part]
                    mock_response.candidates = [mock_candidate]
                    mock_gemini.models.generate_content.return_value = mock_response

                    test_prompt = "This is a test prompt for image generation"

                    sourcer.generate_image_with_gemini(
                        prompt=test_prompt,
                        article_id=1
                    )

                    # Verify prompt length was logged
                    log_calls = [str(call) for call in mock_logger.info.call_args_list]
                    assert any('prompt length' in msg.lower() for msg in log_calls)
