#!/usr/bin/env python3
"""
Clean OpenAI Provider Tests
Tests the new architecture for OpenAI image generation provider
"""

from unittest.mock import Mock, patch

import pytest
from src.providers.base.media_provider import MediaRequest
from src.providers.image.openai_provider import OpenAIProvider


class TestOpenAIProviderClean:
    """Test clean OpenAI provider implementation"""

    def test_config_injection_validation(self):
        """Test: Config injection with fail-fast validation"""
        # Test valid configuration
        valid_config = {
            "api_key": "sk-test123456789",
            "model": "dall-e-2",
            "rate_limit_delay": 4.0,
        }

        provider = OpenAIProvider(valid_config)
        assert provider.config == valid_config
        assert provider.api_key == "sk-test123456789"
        assert provider.model == "dall-e-2"

        # Test missing api_key
        with pytest.raises(
            ValueError, match="Missing required OpenAI config key: api_key"
        ):
            OpenAIProvider({"model": "dall-e-2"})

        # Test missing model
        with pytest.raises(
            ValueError, match="Missing required OpenAI config key: model"
        ):
            OpenAIProvider({"api_key": "test-key"})

        # Test invalid model
        invalid_model_config = {"api_key": "test-key", "model": "invalid-model"}
        with pytest.raises(ValueError, match="Invalid model: invalid-model"):
            OpenAIProvider(invalid_model_config)

        # Test empty configuration
        with pytest.raises(ValueError, match="Missing required OpenAI config key"):
            OpenAIProvider({})

    def test_supported_types(self):
        """Test: Provider supports correct media types"""
        config = {"api_key": "test-key", "model": "dall-e-2"}

        provider = OpenAIProvider(config)
        assert provider.supported_types == ["image"]
        assert provider.supports_type("image") is True
        assert provider.supports_type("audio") is False

    def test_cost_estimation(self):
        """Test: Cost estimation works correctly"""
        config = {"api_key": "test-key", "model": "dall-e-2", "rate_limit_delay": 4.0}

        provider = OpenAIProvider(config)

        requests = [
            MediaRequest(
                type="image", content=f"Image {i}", params={"size": "1024x1024"}
            )
            for i in range(5)
        ]

        cost_estimate = provider.get_cost_estimate(requests)

        assert cost_estimate["requests_count"] == 5
        assert cost_estimate["total_cost"] > 0  # Should have positive cost
        assert cost_estimate["per_request"] > 0
        assert cost_estimate["total_cost"] == cost_estimate["per_request"] * 5

        # Test DALL-E 3 costs differently than DALL-E 2
        dalle3_config = {**config, "model": "dall-e-3"}
        dalle3_provider = OpenAIProvider(dalle3_config)

        dalle3_cost = dalle3_provider.get_cost_estimate(requests[:1])  # Single request
        dalle2_cost = provider.get_cost_estimate(requests[:1])

        # DALL-E 3 should be more expensive than DALL-E 2
        assert dalle3_cost["per_request"] > dalle2_cost["per_request"]

    def test_unsupported_media_type_handling(self):
        """Test: Unsupported media types are rejected correctly"""
        config = {"api_key": "test-key", "model": "dall-e-2"}

        provider = OpenAIProvider(config)

        # Test unsupported audio request
        audio_request = MediaRequest(type="audio", content="Hello world", params={})

        result = provider.generate_media(audio_request)

        assert result.success is False
        assert "Request not supported by OpenAIProvider" in result.error
        assert result.file_path is None

    def test_rate_limiting_configuration(self):
        """Test: Rate limiting is properly configured and applied"""
        config = {
            "api_key": "test-key",
            "model": "dall-e-2",
            "rate_limit_delay": 0.1,  # 100ms delay
        }

        provider = OpenAIProvider(config)

        # Test that rate limit delay is stored correctly
        assert provider._rate_limit_delay == 0.1

        # Test default rate limit when not specified
        default_config = {"api_key": "test-key", "model": "dall-e-2"}

        default_provider = OpenAIProvider(default_config)
        # Should have default rate limit for OpenAI (4 seconds for 15 req/min)
        assert default_provider._rate_limit_delay == 4.0

    def test_client_initialization(self):
        """Test: OpenAI client is initialized correctly"""
        config = {"api_key": "sk-test123456789", "model": "dall-e-2"}

        # Test without mocking since _create_openai_client handles ImportError gracefully
        provider = OpenAIProvider(config)

        # Client should be None when openai is not installed
        assert provider.client is None
        assert provider.api_key == "sk-test123456789"

    def test_batch_image_generation_mock(self):
        """Test: Sequential batch processing with rate limits"""
        config = {
            "api_key": "test-key",
            "model": "dall-e-2",
            "rate_limit_delay": 0.01,  # Small delay for testing
        }

        provider = OpenAIProvider(config)

        requests = [
            MediaRequest(
                type="image", content=f"A test image {i}", params={"size": "1024x1024"}
            )
            for i in range(3)
        ]

        # Mock the client directly since we're testing without openai installed
        mock_client = Mock()
        provider.client = mock_client

        # Mock DALL-E responses
        mock_image = Mock()
        mock_image.url = "https://example.com/generated_image.jpg"
        mock_response = Mock()
        mock_response.data = [mock_image]
        mock_client.images.generate.return_value = mock_response

        # Mock image download and file operations
        with patch("requests.get") as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ) as mock_open:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b"mock_image_data_12345"]
            mock_download.return_value = mock_response

            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            results = provider.generate_batch(requests)

            # Assert batch processing completed successfully
            assert len(results) == 3
            assert all(result.success for result in results)

            # Verify OpenAI API was called for each request
            assert mock_client.images.generate.call_count == 3

    def test_single_image_generation_mock(self):
        """Test: Single image generation with mocked client"""
        config = {"api_key": "test-key", "model": "dall-e-3", "rate_limit_delay": 0.01}

        provider = OpenAIProvider(config)

        request = MediaRequest(
            type="image",
            content="A beautiful sunset over mountains",
            params={"size": "1024x1024", "quality": "hd", "style": "vivid"},
        )

        # Mock the client
        mock_client = Mock()
        provider.client = mock_client

        # Mock successful API response
        mock_image = Mock()
        mock_image.url = "https://example.com/generated_image.jpg"
        mock_image.revised_prompt = "Enhanced: A beautiful sunset over mountains"
        mock_response = Mock()
        mock_response.data = [mock_image]
        mock_client.images.generate.return_value = mock_response

        # Mock download and file operations
        with patch("requests.get") as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ) as mock_open:
            mock_dl_response = Mock()
            mock_dl_response.status_code = 200
            mock_dl_response.raise_for_status.return_value = None
            mock_dl_response.iter_content.return_value = [b"actual_image_data"]
            mock_download.return_value = mock_dl_response
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = provider.generate_media(request)

            assert result.success is True
            assert result.file_path is not None
            assert result.metadata["model"] == "dall-e-3"
            assert result.metadata["size"] == "1024x1024"
            assert result.metadata["quality"] == "hd"
            assert result.metadata["style"] == "vivid"
            assert "revised_prompt" in result.metadata

            # Verify API call parameters for DALL-E 3
            mock_client.images.generate.assert_called_once_with(
                model="dall-e-3",
                prompt="A beautiful sunset over mountains",
                size="1024x1024",
                quality="hd",
                style="vivid",
                n=1,
            )

    def test_api_error_handling(self):
        """Test: API errors are handled gracefully"""
        config = {"api_key": "test-key", "model": "dall-e-2", "rate_limit_delay": 0.01}

        provider = OpenAIProvider(config)

        request = MediaRequest(
            type="image", content="Test prompt", params={"size": "1024x1024"}
        )

        # Mock the client to raise an exception
        mock_client = Mock()
        provider.client = mock_client

        # Simulate OpenAI API error
        mock_client.images.generate.side_effect = Exception("API quota exceeded")

        result = provider.generate_media(request)

        assert result.success is False
        assert "API quota exceeded" in result.error
        assert result.file_path is None

    def test_download_error_handling(self):
        """Test: Image download errors are handled properly"""
        config = {"api_key": "test-key", "model": "dall-e-2", "rate_limit_delay": 0.01}

        provider = OpenAIProvider(config)

        request = MediaRequest(
            type="image", content="Test prompt", params={"size": "1024x1024"}
        )

        # Mock client with successful API response
        mock_client = Mock()
        provider.client = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(url="https://example.com/image.jpg")]
        mock_client.images.generate.return_value = mock_response

        # Mock download failure
        with patch("requests.get") as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ):
            mock_download.side_effect = Exception("Download failed: connection timeout")

            result = provider.generate_media(request)

            assert result.success is False
            assert "Download failed: connection timeout" in result.error
            assert result.file_path is None
