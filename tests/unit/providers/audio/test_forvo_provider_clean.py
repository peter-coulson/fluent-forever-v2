#!/usr/bin/env python3
"""
Clean Forvo Provider Tests
Tests the new architecture for Forvo audio provider with simplified config validation
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.providers.audio.forvo_provider import ForvoProvider
from src.providers.base.media_provider import MediaRequest


class TestForvoProviderClean:
    """Test clean Forvo provider implementation"""

    def test_simplified_config_validation(self):
        """Test: No fallback logic, clean config requirements"""
        # Test valid configuration
        valid_config = {
            "api_key": "test-api-key-12345",
            "country_priorities": ["MX", "ES", "AR"],
            "rate_limit_delay": 0.5,
        }

        provider = ForvoProvider(valid_config)
        assert provider.config == valid_config
        assert provider.api_key == "test-api-key-12345"
        assert provider.country_priorities == ["MX", "ES", "AR"]

        # Test missing api_key
        with pytest.raises(
            ValueError, match="Missing required Forvo config key: api_key"
        ):
            ForvoProvider({"country_priorities": ["MX"]})

        # Test missing country_priorities
        with pytest.raises(
            ValueError, match="Missing required Forvo config key: country_priorities"
        ):
            ForvoProvider({"api_key": "test-key"})

        # Test empty country_priorities
        invalid_config = {"api_key": "test-key", "country_priorities": []}
        with pytest.raises(ValueError, match="country_priorities cannot be empty"):
            ForvoProvider(invalid_config)

        # Test empty configuration
        with pytest.raises(ValueError, match="Missing required Forvo config key"):
            ForvoProvider({})

    def test_static_data_from_config(self):
        """Test: Country priorities from config, not hardcoded"""
        # Test custom country priorities
        config = {
            "api_key": "test-key",
            "country_priorities": ["ES", "AR", "CO", "PE", "CL"],
            "rate_limit_delay": 0.2,
        }

        provider = ForvoProvider(config)

        # Verify country priorities are taken from config
        assert provider.country_priorities == ["ES", "AR", "CO", "PE", "CL"]

        # Test priority groups are generated from config
        assert hasattr(provider, "group1")
        assert hasattr(provider, "group2")
        assert hasattr(provider, "group3")

        # Test different configuration
        config2 = {
            "api_key": "test-key",
            "country_priorities": ["MX", "US"],
            "priority_groups": [["MX"], ["US"]],
            "rate_limit_delay": 0.1,
        }

        provider2 = ForvoProvider(config2)
        assert provider2.country_priorities == ["MX", "US"]
        assert provider2.group1 == ["MX"]
        assert provider2.group2 == ["US"]

    def test_batch_audio_processing(self):
        """Test: Multiple word requests efficiently processed"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX", "ES"],
            "rate_limit_delay": 0.05,  # 50ms for testing
        }

        provider = ForvoProvider(config)

        requests = [
            MediaRequest(
                type="audio", content=word, params={"language": "es", "country": "MX"}
            )
            for word in ["hola", "gracias", "por", "favor", "adiós"]
        ]

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ):
            # Mock API responses
            mock_request.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "https://apifree.forvo.com/audio/test.mp3",
                            "country": "MX",
                            "username": "native_speaker",
                            "votes": 5,
                        }
                    ]
                },
            )

            # Mock audio download
            mock_download.return_value = Mock(
                status_code=200, iter_content=Mock(return_value=[b"mock_audio_data"])
            )
            mock_download.return_value.raise_for_status.return_value = None

            results = provider.generate_batch(requests)

            # Assert batch processing completed successfully
            assert len(results) == 5
            assert all(result.success for result in results)

            # Verify API was called for each word
            assert mock_request.call_count == 5

            # Check that each result has correct metadata
            words = ["hola", "gracias", "por", "favor", "adiós"]
            for i, result in enumerate(results):
                assert result.metadata["word"] == words[i]
                assert result.metadata["country"] == "MX"
                assert result.metadata["votes"] == 5
                assert result.file_path is not None

    def test_pronunciation_selection_logic(self):
        """Test: Pronunciation selection follows priority groups"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX", "ES", "AR"],
            "priority_groups": [["MX"], ["ES"], ["AR"]],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        request = MediaRequest(
            type="audio", content="test_word", params={"language": "es"}
        )

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ):
            # Mock API response with multiple pronunciations
            pronunciations = [
                {
                    "pathmp3": "https://example.com/ar_audio.mp3",
                    "country": "AR",
                    "username": "user1",
                    "votes": 10,
                },
                {
                    "pathmp3": "https://example.com/mx_audio.mp3",
                    "country": "MX",
                    "username": "user2",
                    "votes": 5,
                },
                {
                    "pathmp3": "https://example.com/es_audio.mp3",
                    "country": "ES",
                    "username": "user3",
                    "votes": 8,
                },
            ]

            mock_request.return_value = Mock(
                success=True, data={"items": pronunciations}
            )

            mock_download.return_value = Mock(
                status_code=200, iter_content=Mock(return_value=[b"audio_data"])
            )
            mock_download.return_value.raise_for_status.return_value = None

            result = provider.generate_media(request)

            # Should select MX pronunciation (highest priority group)
            assert result.success is True
            assert result.metadata["country"] == "MX"
            assert result.metadata["votes"] == 5

            # Verify correct audio URL was downloaded
            mock_download.assert_called_once()
            download_url = mock_download.call_args[0][0]
            assert download_url == "https://example.com/mx_audio.mp3"

    def test_api_error_handling(self):
        """Test: API errors are handled gracefully"""
        config = {
            "api_key": "invalid-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        request = MediaRequest(
            type="audio", content="test_word", params={"language": "es"}
        )

        with patch.object(provider, "_make_request") as mock_request:
            # Mock API failure
            mock_request.return_value = Mock(success=False, data={})

            result = provider.generate_media(request)

            assert result.success is False
            assert "No pronunciations found for word: test_word" in result.error
            assert result.file_path is None

    def test_download_error_handling(self):
        """Test: Audio download errors are handled properly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        request = MediaRequest(
            type="audio", content="test_word", params={"language": "es"}
        )

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ):
            # Mock successful API response
            mock_request.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "https://example.com/audio.mp3",
                            "country": "MX",
                            "votes": 1,
                        }
                    ]
                },
            )

            # Mock download failure
            mock_download.side_effect = Exception("Network timeout during download")

            result = provider.generate_media(request)

            assert result.success is False
            assert "Network timeout during download" in result.error
            assert result.file_path is None

    def test_unsupported_media_type_handling(self):
        """Test: Unsupported media types are rejected correctly"""
        config = {"api_key": "test-key", "country_priorities": ["MX"]}

        provider = ForvoProvider(config)

        # Test unsupported image request
        image_request = MediaRequest(type="image", content="Test image", params={})

        result = provider.generate_media(image_request)

        assert result.success is False
        assert "not supported" in result.error

    def test_empty_word_handling(self):
        """Test: Empty words are handled gracefully"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        # Test empty content
        empty_request = MediaRequest(
            type="audio",
            content="   ",  # Whitespace only
            params={"language": "es"},
        )

        result = provider.generate_media(empty_request)

        assert result.success is False
        assert "Empty word provided for audio generation" in result.error

        # Test truly empty content - MediaRequest validation catches this
        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type="audio", content="", params={"language": "es"})

    def test_custom_output_path_handling(self):
        """Test: Custom output paths are handled correctly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        custom_path = Path("/tmp/custom_audio.mp3")
        request = MediaRequest(
            type="audio",
            content="custom",
            params={"language": "es"},
            output_path=custom_path,
        )

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ) as mock_open:
            mock_request.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "https://example.com/audio.mp3",
                            "country": "MX",
                            "votes": 1,
                        }
                    ]
                },
            )

            mock_download.return_value = Mock(
                status_code=200, iter_content=Mock(return_value=[b"audio_data"])
            )
            mock_download.return_value.raise_for_status.return_value = None

            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = provider.generate_media(request)

            assert result.success is True
            assert result.file_path == custom_path

    def test_default_file_path_generation(self):
        """Test: Default file paths are generated correctly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        request = MediaRequest(
            type="audio",
            content="héllo-world",  # Test special characters
            params={"language": "es"},
        )

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ) as mock_open:
            mock_request.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "https://example.com/audio.mp3",
                            "country": "MX",
                            "votes": 1,
                        }
                    ]
                },
            )

            mock_download.return_value = Mock(
                status_code=200, iter_content=Mock(return_value=[b"audio_data"])
            )
            mock_download.return_value.raise_for_status.return_value = None

            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = provider.generate_media(request)

            assert result.success is True
            # Check that path contains expected elements
            assert "media/audio" in str(result.file_path)
            assert "_MX.mp3" in str(result.file_path)
            # Special characters should be cleaned (alphanumeric + ._- kept)
            assert "héllo-world" in str(result.file_path)  # é is alphanumeric

    def test_preferred_country_handling(self):
        """Test: Preferred country parameter is used correctly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX", "ES", "AR"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        request = MediaRequest(
            type="audio",
            content="test_word",
            params={"language": "es", "country": "AR"},  # Specific country requested
        )

        with patch.object(provider, "_make_request") as mock_request, patch(
            "requests.get"
        ) as mock_download, patch("pathlib.Path.mkdir"), patch(
            "builtins.open", create=True
        ):
            # Mock API response for specific country
            mock_request.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "https://example.com/ar_audio.mp3",
                            "country": "AR",
                            "votes": 3,
                        }
                    ]
                },
            )

            mock_download.return_value = Mock(
                status_code=200, iter_content=Mock(return_value=[b"audio_data"])
            )
            mock_download.return_value.raise_for_status.return_value = None

            result = provider.generate_media(request)

            assert result.success is True
            assert result.metadata["country"] == "AR"

            # Verify API was called with specific country first
            api_calls = mock_request.call_args_list
            assert len(api_calls) >= 1
            first_call_url = api_calls[0][0][1]  # Second argument is the URL
            assert "country/AR" in first_call_url

    def test_cost_estimation(self):
        """Test: Cost estimation for free API"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.5,
        }

        provider = ForvoProvider(config)

        requests = [
            MediaRequest(type="audio", content=f"word{i}", params={"language": "es"})
            for i in range(10)
        ]

        cost_estimate = provider.get_cost_estimate(requests)

        # Forvo is a free API
        assert cost_estimate["total_cost"] == 0.0
        assert cost_estimate["per_request"] == 0.0
        assert cost_estimate["requests_count"] == 10

    def test_service_info_accuracy(self):
        """Test: Service information reflects current configuration"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX", "ES", "AR", "CO"],
            "rate_limit_delay": 0.5,
        }

        provider = ForvoProvider(config)
        service_info = provider.get_service_info()

        assert service_info["service"] == "Forvo"
        assert service_info["type"] == "audio_provider"
        assert service_info["supported_languages"] == ["es"]
        assert service_info["supported_countries"] == ["MX", "ES", "AR", "CO"]

    def test_connection_test(self):
        """Test: Connection testing works correctly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        with patch.object(provider, "_make_request") as mock_request:
            # Test successful connection
            mock_request.return_value = Mock(success=True)
            assert provider.test_connection() is True

            # Test failed connection
            mock_request.return_value = Mock(success=False)
            assert provider.test_connection() is False

            # Test connection with exception
            mock_request.side_effect = Exception("Connection failed")
            assert provider.test_connection() is False

    def test_rate_limiting_configuration(self):
        """Test: Rate limiting configuration is applied correctly"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.25,
        }

        provider = ForvoProvider(config)

        # Test rate limit is set correctly
        assert provider._rate_limit_delay == 0.25

        # Test default rate limit
        default_config = {"api_key": "test-key", "country_priorities": ["MX"]}

        default_provider = ForvoProvider(default_config)
        # Should have default rate limit for Forvo (0.5 seconds)
        assert default_provider._rate_limit_delay == 0.5

    def test_no_fallback_config_logic(self):
        """Test: No legacy fallback configuration logic"""
        # This test ensures the new provider has NO fallback logic
        # Any invalid/incomplete config should fail immediately

        # Test partial config fails immediately
        with pytest.raises(ValueError):
            ForvoProvider({"api_key": "test"})  # Missing country_priorities

        with pytest.raises(ValueError):
            ForvoProvider({"country_priorities": ["MX"]})  # Missing api_key

        # Test no environment variable fallback
        with pytest.raises(ValueError):
            ForvoProvider({})  # Empty config should fail

        # No config structure compatibility layer should exist
        # Old config formats should not work
        with pytest.raises(ValueError):
            ForvoProvider(
                {"apis": {"forvo": {"api_key": "test", "country_priorities": ["MX"]}}}
            )
