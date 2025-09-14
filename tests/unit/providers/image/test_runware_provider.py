"""Unit tests for RunwareProvider following TDD methodology."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from providers.base.media_provider import MediaRequest, MediaResult
from providers.image.runware_provider import RunwareProvider


class TestRunwareProvider:
    """Comprehensive unit tests for Runware provider"""

    def test_config_injection_validation_success(self):
        """Test: Valid config initialization succeeds"""
        config = {
            "api_key": "test-api-key",
            "model": "runware:100@1",
            "image_size": "512x512",
        }

        provider = RunwareProvider(config)
        assert provider.config == config
        assert provider.api_key == "test-api-key"
        assert provider.model == "runware:100@1"
        assert provider.image_size == "512x512"

    def test_config_injection_validation_missing_api_key(self):
        """Test: Missing api_key raises ValueError"""
        config = {
            "model": "runware:100@1",
        }

        with pytest.raises(
            ValueError, match="Missing required Runware config key: api_key"
        ):
            RunwareProvider(config)

    def test_config_injection_validation_invalid_model(self):
        """Test: Invalid model format raises ValueError"""
        config = {
            "api_key": "test-key",
            "model": "invalid-model-format",
        }

        with pytest.raises(ValueError, match="Invalid Runware model format"):
            RunwareProvider(config)

    def test_config_injection_validation_invalid_image_size(self):
        """Test: Invalid image size format raises ValueError"""
        config = {
            "api_key": "test-key",
            "image_size": "invalid-size",
        }

        with pytest.raises(ValueError, match="Invalid image size format"):
            RunwareProvider(config)

    def test_default_configuration_values(self):
        """Test: Default values are applied when not specified"""
        config = {"api_key": "test-key"}

        provider = RunwareProvider(config)

        assert provider.model == "runware:100@1"
        assert provider.image_size == "512x512"
        assert provider.steps == 20
        assert provider.guidance == 7
        assert provider._rate_limit_delay == 1.0
        assert provider.timeout == 30
        assert provider.batch_size == 4

    def test_api_key_masking_in_representation(self):
        """Test: API key is masked in string representations"""
        config = {"api_key": "secret-api-key-12345"}
        provider = RunwareProvider(config)

        # API key should not appear in string representation
        repr_str = repr(provider)
        assert "secret-api-key-12345" not in repr_str
        assert "***" in repr_str or "masked" in repr_str.lower()

    def test_model_validation_valid_formats(self):
        """Test: Valid model formats are accepted"""
        valid_models = [
            "runware:100@1",
            "runware:200@2",
            "custom:model@1",
        ]

        for model in valid_models:
            config = {"api_key": "test-key", "model": model}
            provider = RunwareProvider(config)
            assert provider.model == model

    def test_image_size_validation_valid_formats(self):
        """Test: Valid image size formats are accepted"""
        valid_sizes = [
            "512x512",
            "1024x1024",
            "768x512",
            "512x768",
        ]

        for size in valid_sizes:
            config = {"api_key": "test-key", "image_size": size}
            provider = RunwareProvider(config)
            assert provider.image_size == size

    @patch("requests.Session")
    def test_api_session_setup(self, mock_session_class):
        """Test: API session is properly configured"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        config = {"api_key": "test-key"}
        _ = RunwareProvider(config)

        mock_session.headers.update.assert_called_once_with(
            {"Authorization": "Bearer test-key", "Content-Type": "application/json"}
        )

    def test_generate_media_request_validation(self):
        """Test: MediaRequest validation for image generation"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        # Invalid request type - the base class handles this by returning error result
        request = MediaRequest(type="audio", content="test", params={})

        result = provider.generate_media(request)
        assert result.success is False
        assert "not supported" in result.error

    def test_single_image_generation_success(self):
        """Test: Successful single image generation"""
        config = {"api_key": "test-key"}

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "success",
            "data": {"taskId": "task-123", "imageUrl": "https://example.com/image.png"},
        }

        # Mock image download
        mock_download_response = Mock()
        mock_download_response.status_code = 200
        mock_download_response.iter_content.return_value = [b"image_data"]
        mock_download_response.headers = {"content-type": "image/png"}
        mock_download_response.raise_for_status.return_value = None

        with patch("requests.Session") as mock_session_class, patch.object(
            RunwareProvider, "_validate_downloaded_file", return_value=True
        ):
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.post.return_value = mock_response
            mock_session.get.return_value = mock_download_response

            provider = RunwareProvider(config)
            # Override the session created during init
            provider._session = mock_session

            request = MediaRequest(
                type="image", content="a beautiful sunset", params={"language": "en"}
            )

            result = provider.generate_media(request)

            assert result.success is True
            assert result.file_path is not None
            assert result.metadata["prompt"] == "a beautiful sunset"
            assert result.error is None

    @patch("requests.Session")
    def test_api_error_handling(self, mock_session_class):
        """Test: API error handling and classification"""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        # Test 401 Unauthorized
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "401 Unauthorized"
        )
        mock_session.post.return_value = mock_response

        request = MediaRequest(type="image", content="test", params={})
        result = provider.generate_media(request)

        assert result.success is False
        assert "Authentication" in result.error

        # Test 429 Rate Limit
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "429 Rate Limited"
        )

        result = provider.generate_media(request)
        assert result.success is False
        assert "rate limit" in result.error.lower()

    def test_batch_processing_chunking(self):
        """Test: Batch processing respects chunk size limits"""
        config = {"api_key": "test-key", "batch_size": 2}
        provider = RunwareProvider(config)

        requests = [
            MediaRequest(type="image", content=f"test {i}", params={}) for i in range(5)
        ]

        with patch.object(provider, "generate_media") as mock_generate:
            mock_generate.return_value = MediaResult(
                success=True, file_path=Path("test.png"), metadata={}, error=None
            )

            results = provider.generate_batch(requests)

            # Should process all 5 requests
            assert len(results) == 5
            assert mock_generate.call_count == 5

    @patch("time.sleep")
    def test_rate_limiting_delays(self, mock_sleep):
        """Test: Rate limiting introduces proper delays"""
        config = {"api_key": "test-key", "rate_limit_delay": 2.0}
        provider = RunwareProvider(config)

        requests = [
            MediaRequest(type="image", content="test 1", params={}),
            MediaRequest(type="image", content="test 2", params={}),
        ]

        with patch.object(provider, "generate_media") as mock_generate:
            mock_generate.return_value = MediaResult(
                success=True, file_path=Path("test.png"), metadata={}, error=None
            )

            provider.generate_batch(requests)

            # Should have rate limiting delay between requests
            mock_sleep.assert_called_with(2.0)

    def test_file_path_generation_format(self):
        """Test: File path generation follows expected format"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        request = MediaRequest(
            type="image",
            content="test prompt with special chars!@#",
            params={"language": "en"},
        )

        with patch("hashlib.md5") as mock_md5:
            mock_md5.return_value.hexdigest.return_value = "abcdef123456"

            file_path = provider._generate_file_path(request)

            assert "test-prompt-with-special-chars" in str(file_path)
            assert "abcdef123456" in str(file_path)
            assert file_path.suffix == ".png"

    def test_metadata_extraction_comprehensive(self):
        """Test: Complete metadata extraction from API response"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        api_response = {
            "status": "success",
            "data": {
                "taskId": "task-123",
                "imageUrl": "https://example.com/image.png",
                "model": "runware:100@1",
                "steps": 25,
                "guidance": 7.5,
                "seed": 12345,
            },
        }

        metadata = provider._extract_metadata(api_response, "test prompt")

        assert metadata["prompt"] == "test prompt"
        assert metadata["task_id"] == "task-123"
        assert metadata["model"] == "runware:100@1"
        assert metadata["steps"] == 25
        assert metadata["guidance"] == 7.5
        assert metadata["seed"] == 12345
        assert "generation_time" in metadata

    def test_retry_logic_exponential_backoff(self):
        """Test: Retry logic with exponential backoff"""
        config = {"api_key": "test-key"}

        with patch("time.sleep") as mock_sleep, patch(
            "requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            # First two calls fail with 500, third succeeds
            mock_response_fail = Mock()
            mock_response_fail.status_code = 500
            mock_response_fail.raise_for_status.side_effect = requests.HTTPError(
                "500 Server Error"
            )

            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.raise_for_status.return_value = None
            mock_response_success.json.return_value = {
                "status": "success",
                "data": {"taskId": "123", "imageUrl": "https://example.com/image.png"},
            }

            mock_session.post.side_effect = [
                mock_response_fail,
                mock_response_fail,
                mock_response_success,
            ]

            provider = RunwareProvider(config)
            # Override the session created during init
            provider._session = mock_session

            _ = provider._make_api_request("test prompt")

            # Should have made 3 attempts
            assert mock_session.post.call_count == 3

            # Should have exponential backoff delays: 1s, 2s
            expected_delays = [1, 2]
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            assert actual_delays == expected_delays

    def test_unsupported_media_type_rejection(self):
        """Test: Unsupported media types are rejected"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        request = MediaRequest(type="audio", content="test", params={})

        result = provider.generate_media(request)
        assert result.success is False
        assert "not supported" in result.error

    def test_empty_prompt_handling(self):
        """Test: Empty or whitespace-only prompts are handled"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        # Empty content is caught by MediaRequest validation
        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type="image", content="", params={})

        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type="image", content=None, params={})

        # Test whitespace-only content
        request = MediaRequest(type="image", content="   ", params={})
        result = provider.generate_media(request)
        assert result.success is False
        assert "Prompt cannot be empty" in result.error

    def test_file_validation_after_download(self, tmp_path):
        """Test: Downloaded files are validated"""
        config = {"api_key": "test-key"}
        provider = RunwareProvider(config)

        # Create a real test file with reasonable size
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"x" * 1024 * 100)  # 100KB
        assert provider._validate_downloaded_file(test_file) is True

        # Create file that's too small
        small_file = tmp_path / "small.png"
        small_file.write_bytes(b"x" * 10)  # 10 bytes
        assert provider._validate_downloaded_file(small_file) is False

        # Test non-existent file
        nonexistent_file = tmp_path / "nonexistent.png"
        assert provider._validate_downloaded_file(nonexistent_file) is False

    def test_connection_timeout_handling(self):
        """Test: Connection timeouts are handled gracefully"""
        config = {"api_key": "test-key", "timeout": 5}

        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            mock_session.post.side_effect = requests.Timeout("Connection timed out")

            provider = RunwareProvider(config)
            # Override the session created during init
            provider._session = mock_session

            request = MediaRequest(type="image", content="test", params={})
            result = provider.generate_media(request)

            assert result.success is False
            assert "timeout" in result.error.lower()

    def test_invalid_json_response_handling(self):
        """Test: Invalid JSON responses are handled"""
        config = {"api_key": "test-key"}

        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError(
                "Invalid JSON", "response", 0
            )
            mock_response.text = "Invalid response text"
            mock_response.raise_for_status.return_value = None  # Don't raise HTTP error
            mock_session.post.return_value = mock_response

            provider = RunwareProvider(config)
            # Override the session created during init
            provider._session = mock_session

            request = MediaRequest(type="image", content="test", params={})
            result = provider.generate_media(request)

            assert result.success is False
            assert "Invalid JSON" in result.error
