"""
The Daily Worker - Claude Prompt Enhancement Service Tests

Test-driven development for Claude-based prompt enhancement.
Tests are written FIRST, then implementation follows.

Phase 6.11.3: Implement Claude Prompt Enhancement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestClaudePromptEnhancement:
    """Test suite for Claude prompt enhancement service"""

    def test_service_initialization(self):
        """Test that service initializes correctly with API key"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        with patch('anthropic.Anthropic'):
            service = ClaudePromptEnhancer(api_key="test_api_key_123")
            assert service is not None
            assert service.api_key == "test_api_key_123"

    def test_service_initialization_without_api_key(self):
        """Test that service handles missing API key gracefully"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        with pytest.raises(ValueError, match="Claude API key is required"):
            ClaudePromptEnhancer(api_key=None)

    def test_generate_concepts_basic(self):
        """Test basic concept generation from article metadata"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        # Mock Claude API response
        mock_response = {
            "concepts": [
                {
                    "prompt": "Documentary-style photograph of factory workers operating machinery, industrial setting, natural lighting",
                    "confidence": 0.92,
                    "rationale": "Direct representation of working-class labor aligns with article content"
                },
                {
                    "prompt": "Abstract composition of interlocking gears and human hands, symbolizing labor and industry",
                    "confidence": 0.85,
                    "rationale": "Symbolic approach provides artistic interpretation of worker solidarity"
                },
                {
                    "prompt": "Vintage propaganda poster style illustration of diverse workers united, bold colors, socialist realism aesthetic",
                    "confidence": 0.88,
                    "rationale": "Historical art style connects to labor movement heritage"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Workers Unite for Better Wages",
            summary="Labor unions organize massive rally demanding living wages and better conditions."
        )

        # Verify result structure
        assert result is not None
        assert 'concepts' in result
        assert len(result['concepts']) >= 3
        assert len(result['concepts']) <= 5

    def test_generate_concepts_full_response(self):
        """Test that all concept fields are properly parsed"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "concepts": [
                {
                    "prompt": "Wide angle photo of protest march, thousands of workers with signs",
                    "confidence": 0.91,
                    "rationale": "Captures scale and energy of labor movement"
                },
                {
                    "prompt": "Close-up portrait of factory worker's weathered hands holding tools",
                    "confidence": 0.87,
                    "rationale": "Intimate perspective on working-class experience"
                },
                {
                    "prompt": "Drone aerial view of industrial complex at sunrise, workers streaming in",
                    "confidence": 0.83,
                    "rationale": "Epic scale shows magnitude of workforce"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Test Headline",
            summary="Test Summary"
        )

        concepts = result['concepts']
        for concept in concepts:
            # Verify all required fields present
            assert 'prompt' in concept
            assert 'confidence' in concept
            assert 'rationale' in concept

            # Verify data types
            assert isinstance(concept['prompt'], str)
            assert isinstance(concept['confidence'], (int, float))
            assert isinstance(concept['rationale'], str)

            # Verify non-empty
            assert len(concept['prompt']) > 0
            assert len(concept['rationale']) > 0

    def test_confidence_score_validation(self):
        """Test that confidence scores are validated (0.0-1.0)"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "concepts": [
                {
                    "prompt": "Test prompt 1",
                    "confidence": 0.95,
                    "rationale": "High confidence concept"
                },
                {
                    "prompt": "Test prompt 2",
                    "confidence": 0.5,
                    "rationale": "Medium confidence concept"
                },
                {
                    "prompt": "Test prompt 3",
                    "confidence": 0.2,
                    "rationale": "Low confidence concept"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Test",
            summary="Test"
        )

        concepts = result['concepts']
        for concept in concepts:
            # All confidence scores must be between 0.0 and 1.0
            assert 0.0 <= concept['confidence'] <= 1.0

    def test_select_best_prompt(self):
        """Test that best prompt is selected by highest confidence score"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "concepts": [
                {
                    "prompt": "Low confidence prompt",
                    "confidence": 0.65,
                    "rationale": "Not the best option"
                },
                {
                    "prompt": "Highest confidence prompt - THIS ONE",
                    "confidence": 0.94,
                    "rationale": "Best artistic interpretation"
                },
                {
                    "prompt": "Medium confidence prompt",
                    "confidence": 0.78,
                    "rationale": "Decent but not optimal"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.enhance_prompt(
            headline="Test Article",
            summary="Test content"
        )

        # Verify best prompt selected
        assert result is not None
        assert result['selected_prompt'] == "Highest confidence prompt - THIS ONE"
        assert result['confidence'] == 0.94
        assert result['rationale'] == "Best artistic interpretation"

    def test_enhance_prompt_returns_all_data(self):
        """Test that enhance_prompt returns selected prompt and all concepts"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "concepts": [
                {
                    "prompt": "Concept 1",
                    "confidence": 0.85,
                    "rationale": "Rationale 1"
                },
                {
                    "prompt": "Concept 2",
                    "confidence": 0.92,
                    "rationale": "Rationale 2"
                },
                {
                    "prompt": "Concept 3",
                    "confidence": 0.78,
                    "rationale": "Rationale 3"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.enhance_prompt(
            headline="Test",
            summary="Test"
        )

        # Verify all required fields
        assert 'selected_prompt' in result
        assert 'confidence' in result
        assert 'rationale' in result
        assert 'all_concepts' in result

        # Verify all concepts included
        assert len(result['all_concepts']) == 3

        # Verify selected is the highest confidence
        assert result['selected_prompt'] == "Concept 2"
        assert result['confidence'] == 0.92

    def test_concept_diversity_validation(self):
        """Test that concepts have diverse artistic approaches"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        # Response with diverse approaches
        mock_response = {
            "concepts": [
                {
                    "prompt": "Photorealistic documentary style worker portrait",
                    "confidence": 0.90,
                    "rationale": "Documentary approach"
                },
                {
                    "prompt": "Abstract geometric composition representing labor",
                    "confidence": 0.85,
                    "rationale": "Abstract artistic interpretation"
                },
                {
                    "prompt": "Vintage propaganda poster illustration",
                    "confidence": 0.88,
                    "rationale": "Historical art style"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Labor News",
            summary="Workers organize"
        )

        concepts = result['concepts']
        prompts = [c['prompt'] for c in concepts]

        # Each prompt should be unique
        assert len(prompts) == len(set(prompts))

        # Prompts should have different artistic styles
        # (photorealistic vs abstract vs vintage)
        assert any('photorealistic' in p.lower() or 'documentary' in p.lower() for p in prompts)
        assert any('abstract' in p.lower() for p in prompts)

    def test_api_error_handling(self):
        """Test graceful handling of API errors"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error: Rate limit exceeded")

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.enhance_prompt(
            headline="Test",
            summary="Test"
        )

        # Should return None on error
        assert result is None

    def test_invalid_json_response(self):
        """Test handling of invalid JSON in Claude response"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="This is not valid JSON")]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.enhance_prompt(
            headline="Test",
            summary="Test"
        )

        # Should return None on parse error
        assert result is None

    def test_missing_concepts_in_response(self):
        """Test handling of malformed response missing concepts field"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "invalid_field": "data"
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Test",
            summary="Test"
        )

        # Should return None when concepts missing
        assert result is None

    def test_claude_prompt_format(self):
        """Test that correct prompt is sent to Claude API"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_response = {
            "concepts": [
                {
                    "prompt": "Test prompt",
                    "confidence": 0.9,
                    "rationale": "Test rationale"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        service.generate_concepts(
            headline="Workers Strike for Wages",
            summary="Thousands of workers walked out demanding better pay and conditions."
        )

        # Verify Claude API was called with correct parameters
        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]

        # Verify model
        assert call_kwargs['model'] == 'claude-sonnet-4-5-20250929'

        # Verify max_tokens
        assert call_kwargs['max_tokens'] >= 2000

        # Verify messages structure
        assert 'messages' in call_kwargs
        messages = call_kwargs['messages']
        assert len(messages) > 0
        assert messages[0]['role'] == 'user'

        # Verify prompt contains article metadata
        prompt_text = messages[0]['content']
        assert "Workers Strike for Wages" in prompt_text
        assert "Thousands of workers walked out demanding better pay" in prompt_text

    def test_minimum_concepts_generated(self):
        """Test that at least 3 concepts are generated"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        # Response with only 2 concepts (should be rejected or handled)
        mock_response = {
            "concepts": [
                {
                    "prompt": "Concept 1",
                    "confidence": 0.9,
                    "rationale": "Rationale 1"
                },
                {
                    "prompt": "Concept 2",
                    "confidence": 0.85,
                    "rationale": "Rationale 2"
                }
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Test",
            summary="Test"
        )

        # Should handle insufficient concepts gracefully
        # Either return None or the concepts it has (implementation decision)
        assert result is None or len(result['concepts']) >= 2

    def test_maximum_concepts_limit(self):
        """Test that no more than 5 concepts are returned"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        # Response with 6 concepts
        mock_response = {
            "concepts": [
                {"prompt": f"Concept {i}", "confidence": 0.9 - (i * 0.05), "rationale": f"Rationale {i}"}
                for i in range(1, 7)
            ]
        }

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_response))]
        mock_client.messages.create.return_value = mock_message

        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)
        result = service.generate_concepts(
            headline="Test",
            summary="Test"
        )

        # Should limit to 5 concepts
        assert result is not None
        assert len(result['concepts']) <= 5

    def test_empty_headline_handling(self):
        """Test handling of empty headline"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_client = MagicMock()
        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)

        with pytest.raises(ValueError, match="Headline and summary are required"):
            service.enhance_prompt(headline="", summary="Valid summary")

    def test_empty_summary_handling(self):
        """Test handling of empty summary"""
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        mock_client = MagicMock()
        service = ClaudePromptEnhancer(api_key="test_key", client=mock_client)

        with pytest.raises(ValueError, match="Headline and summary are required"):
            service.enhance_prompt(headline="Valid headline", summary="")


class TestClaudePromptIntegration:
    """Integration tests for Claude prompt enhancement (require API key)"""

    @pytest.mark.integration
    @pytest.mark.skip(reason="Integration test - requires valid Claude API key")
    def test_real_claude_api_call(self):
        """Test real API call to Claude (requires valid API key in env)"""
        import os
        from backend.services.prompt_enhancement import ClaudePromptEnhancer

        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")

        service = ClaudePromptEnhancer(api_key=api_key)
        result = service.enhance_prompt(
            headline="Workers Unite for Better Wages",
            summary="Labor unions across the country organized rallies demanding living wages and improved working conditions."
        )

        assert result is not None
        assert 'selected_prompt' in result
        assert 'confidence' in result
        assert 'all_concepts' in result
        assert len(result['all_concepts']) >= 3
        assert 0.0 <= result['confidence'] <= 1.0
