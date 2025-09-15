#!/usr/bin/env python3
"""
Provider API Integration Tests
Tests integration with actual APIs (where possible) and validates API compliance
"""

import os
import time
from pathlib import Path
from unittest.mock import Mock, patch

from src.providers.audio.forvo_provider import ForvoProvider
from src.providers.base.media_provider import MediaRequest
from src.providers.image.openai_provider import OpenAIProvider


class TestProviderAPIIntegration:
    """Integration testing with real/mock APIs"""

    def test_openai_api_integration(self):
        """Test: OpenAI provider with real API calls"""
        # Uses test API key if available, mocks if not
        api_key = os.getenv("OPENAI_API_KEY", "test-key-mock")

        config = {
            "api_key": api_key,
            "model": "dall-e-2",
            "rate_limit_delay": 4.0,  # Respect OpenAI rate limits
        }

        if api_key.startswith("test-"):
            # Mock the OpenAI client for test environment
            # First ensure openai module exists for patching
            import sys
            from types import ModuleType

            if "openai" not in sys.modules:
                openai_mock = ModuleType("openai")
                openai_mock.OpenAI = type("MockOpenAI", (), {})
                sys.modules["openai"] = openai_mock

            with (
                patch("openai.OpenAI") as mock_openai_class,
                patch("src.providers.image.openai_provider.OPENAI_AVAILABLE", True),
                patch(
                    "src.providers.image.openai_provider.openai", sys.modules["openai"]
                ),
            ):
                mock_client = Mock()
                mock_openai_class.return_value = mock_client

                # Mock DALL-E response
                mock_response = Mock()
                mock_response.data = [
                    Mock(url="https://example.com/generated_image.jpg")
                ]
                mock_client.images.generate.return_value = mock_response

                # Create provider after setting up mocks
                provider = OpenAIProvider(config)

                # Mock image download
                with patch("requests.get") as mock_download:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.content = b"mock_image_data_12345"
                    mock_response.iter_content.return_value = [b"mock_image_data_12345"]
                    mock_response.raise_for_status.return_value = None
                    mock_download.return_value = mock_response

                    request = MediaRequest(
                        type="image",
                        content="A simple red apple on a white background",
                        params={"size": "1024x1024", "quality": "standard"},
                        output_path=Path("/tmp/test_A_simple_red_apple_o.jpg"),
                    )

                    result = provider.generate_media(request)

                    assert result.success, f"Image generation failed: {result.error}"
                    assert result.file_path is not None
                    assert result.metadata["model"] == "dall-e-2"
                    assert result.metadata["size"] == "1024x1024"

                    # Verify API was called with correct parameters
                    mock_client.images.generate.assert_called_once()
                    call_kwargs = mock_client.images.generate.call_args.kwargs
                    assert call_kwargs["model"] == "dall-e-2"
                    assert (
                        call_kwargs["prompt"]
                        == "A simple red apple on a white background"
                    )
                    assert call_kwargs["size"] == "1024x1024"
        else:
            # Real API integration test (only if API key is available)
            provider = OpenAIProvider(config)
            request = MediaRequest(
                type="image",
                content="A simple test image: red circle on white background",
                params={"size": "1024x1024", "quality": "standard"},
                output_path=Path("/tmp/test_A_simple_test_image_.jpg"),
            )

            result = provider.generate_media(request)

            # Real API results
            assert result.success, f"Real OpenAI API call failed: {result.error}"
            assert result.file_path is not None
            assert result.file_path.exists()
            assert result.metadata["model"] == "dall-e-2"

    def test_forvo_api_integration(self):
        """Test: Forvo provider with real API calls"""
        # Tests actual pronunciation downloads
        api_key = os.getenv("FORVO_API_KEY", "test-key-mock")

        config = {
            "api_key": api_key,
            "country_priorities": ["MX", "ES", "AR"],
            "rate_limit_delay": 0.5,
        }

        provider = ForvoProvider(config)

        if api_key.startswith("test-"):
            # Mock Forvo API for test environment
            with patch.object(provider, "_make_request") as mock_request, patch(
                "requests.get"
            ) as mock_download, patch("pathlib.Path.mkdir"), patch(
                "builtins.open", create=True
            ):
                # Mock API response for pronunciations
                mock_request.return_value = Mock(
                    success=True,
                    data={
                        "items": [
                            {
                                "pathmp3": "https://apifree.forvo.com/audio/test.mp3",
                                "country": "MX",
                                "username": "test_user",
                                "votes": 10,
                            }
                        ]
                    },
                )

                # Mock audio download
                mock_download.return_value = Mock(
                    status_code=200,
                    iter_content=Mock(return_value=[b"mock_audio_data_forvo"]),
                )
                mock_download.return_value.raise_for_status.return_value = None

                request = MediaRequest(
                    type="audio",
                    content="hola",
                    params={"language": "es", "country": "MX"},
                    output_path=Path("/tmp/test_hola.mp3"),
                )

                result = provider.generate_media(request)

                assert result.success, f"Audio generation failed: {result.error}"
                assert result.file_path is not None
                assert result.metadata["word"] == "hola"
                assert result.metadata["country"] == "MX"
                assert result.metadata["votes"] == 10

                # Verify correct API endpoint was called
                mock_request.assert_called()
                api_url = mock_request.call_args[0][1]  # Second argument is the URL
                assert "word-pronunciations" in api_url
                assert "word/hola" in api_url
                assert "language/es" in api_url
        else:
            # Real Forvo API integration test
            request = MediaRequest(
                type="audio",
                content="hola",
                params={"language": "es", "country": "MX"},
                output_path=Path("/tmp/test_hola.mp3"),
            )

            result = provider.generate_media(request)

            # Real API results
            if result.success:
                assert result.file_path is not None
                assert result.file_path.exists()
                assert result.metadata["word"] == "hola"
                assert "country" in result.metadata
            else:
                # If real API fails, ensure error is informative
                assert result.error is not None
                assert len(result.error) > 0

    def test_rate_limiting_compliance(self):
        """Test: Providers respect API rate limits"""
        # Test with configured rate limits
        forvo_config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.1,  # 100ms delay
        }

        openai_config = {
            "api_key": "test-key",
            "model": "dall-e-2",
            "rate_limit_delay": 0.2,  # 200ms delay
        }

        forvo_provider = ForvoProvider(forvo_config)
        openai_provider = OpenAIProvider(openai_config)

        requests = [
            MediaRequest(
                type="audio",
                content=f"word{i}",
                params={"language": "es"},
                output_path=Path(f"/tmp/test_word{i}.mp3"),
            )
            for i in range(3)
        ]

        image_requests = [
            MediaRequest(
                type="image",
                content=f"Image {i}",
                params={"size": "1024x1024"},
                output_path=Path(f"/tmp/test_Image_{i}.jpg"),
            )
            for i in range(3)
        ]

        # Mock both providers
        with patch.object(forvo_provider, "_make_request") as mock_forvo, patch(
            "requests.get"
        ) as mock_download, patch("openai.OpenAI") as mock_openai, patch(
            "pathlib.Path.mkdir"
        ), patch("builtins.open", create=True):
            # Setup Forvo mocks
            mock_forvo.return_value = Mock(
                success=True,
                data={
                    "items": [
                        {
                            "pathmp3": "http://example.com/audio.mp3",
                            "country": "MX",
                            "votes": 1,
                        }
                    ]
                },
            )
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.iter_content.return_value = [b"audio"]
            mock_response.raise_for_status.return_value = None
            mock_download.return_value = mock_response

            # Setup OpenAI mocks
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_response = Mock()
            mock_response.data = [Mock(url="http://example.com/image.jpg")]
            mock_client.images.generate.return_value = mock_response

            with patch("requests.get") as mock_img_download, patch(
                "pathlib.Path.mkdir"
            ), patch("builtins.open", create=True), patch(
                "src.providers.image.openai_provider.OPENAI_AVAILABLE", True
            ):
                mock_img_response = Mock()
                mock_img_response.status_code = 200
                mock_img_response.content = b"image_data"
                mock_img_response.iter_content.return_value = [b"image_data"]
                mock_img_response.raise_for_status.return_value = None
                mock_img_download.return_value = mock_img_response

                # Test Forvo rate limiting
                start_time = time.time()
                forvo_results = forvo_provider.generate_batch(requests)
                forvo_elapsed = time.time() - start_time

                # Should take at least rate_limit_delay * (num_requests - 1)
                expected_min_time = forvo_config["rate_limit_delay"] * (
                    len(requests) - 1
                )
                assert forvo_elapsed >= expected_min_time * 0.8  # Allow 20% variance

                # Test OpenAI rate limiting
                start_time = time.time()
                openai_results = openai_provider.generate_batch(image_requests)
                openai_elapsed = time.time() - start_time

                expected_min_time = openai_config["rate_limit_delay"] * (
                    len(image_requests) - 1
                )
                assert openai_elapsed >= expected_min_time * 0.8  # Allow 20% variance

                # Verify all requests completed successfully
                assert len(forvo_results) == len(requests)
                assert len(openai_results) == len(image_requests)
                assert all(r.success for r in forvo_results)
                assert all(r.success for r in openai_results)

    def test_api_error_handling(self):
        """Test: Providers handle API errors gracefully"""
        config = {
            "api_key": "invalid-key-12345",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        # Mock API failure
        with patch.object(provider, "_make_request") as mock_request:
            mock_request.return_value = Mock(
                success=False, data={}, error="Invalid API key"
            )

            request = MediaRequest(
                type="audio",
                content="test",
                params={"language": "es"},
                output_path=Path("/tmp/test_test.mp3"),
            )

            result = provider.generate_media(request)

            assert not result.success
            assert result.error is not None
            assert (
                "No pronunciations found" in result.error
            )  # Provider-specific error handling

    def test_network_timeout_handling(self):
        """Test: Providers handle network timeouts gracefully"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        with patch.object(provider, "_make_request") as mock_request:
            # Simulate network timeout
            mock_request.side_effect = Exception("Connection timeout")

            request = MediaRequest(
                type="audio",
                content="test",
                params={"language": "es"},
                output_path=Path("/tmp/test_test.mp3"),
            )

            result = provider.generate_media(request)

            assert not result.success
            assert result.error is not None
            assert "Connection timeout" in result.error


class TestProviderConfigurationIntegration:
    """Test configuration integration patterns"""

    def test_config_injection_from_registry(self):
        """Test: Registry properly injects configuration into providers"""
        from src.providers.registry import ProviderRegistry

        registry = ProviderRegistry()

        # Test configuration injection
        forvo_config = {
            "api_key": "test-forvo-key",
            "country_priorities": ["MX", "ES"],
            "rate_limit_delay": 0.5,
        }

        openai_config = {
            "api_key": "test-openai-key",
            "model": "dall-e-2",
            "rate_limit_delay": 4.0,
        }

        # Create providers with configuration and register them
        forvo_provider = ForvoProvider(forvo_config)
        openai_provider = OpenAIProvider(openai_config)

        registry.register_audio_provider("forvo", forvo_provider)
        registry.register_image_provider("openai", openai_provider)

        # Retrieve and verify configuration injection
        retrieved_forvo = registry.get_audio_provider("forvo")
        retrieved_openai = registry.get_image_provider("openai")

        assert retrieved_forvo.config["api_key"] == "test-forvo-key"
        assert retrieved_forvo.config["country_priorities"] == ["MX", "ES"]

        assert retrieved_openai.config["api_key"] == "test-openai-key"
        assert retrieved_openai.config["model"] == "dall-e-2"

    def test_provider_reconfiguration(self):
        """Test: Providers can be reconfigured without registry restart"""
        # Initial configuration
        config_v1 = {
            "api_key": "key-v1",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.5,
        }

        provider_v1 = ForvoProvider(config_v1)
        assert provider_v1.config["api_key"] == "key-v1"
        assert provider_v1.config["country_priorities"] == ["MX"]

        # New configuration
        config_v2 = {
            "api_key": "key-v2",
            "country_priorities": ["ES", "AR"],
            "rate_limit_delay": 0.2,
        }

        provider_v2 = ForvoProvider(config_v2)
        assert provider_v2.config["api_key"] == "key-v2"
        assert provider_v2.config["country_priorities"] == ["ES", "AR"]
        assert provider_v2.config["rate_limit_delay"] == 0.2


class TestProviderHealthMonitoring:
    """Test provider health and monitoring capabilities"""

    def test_provider_health_check(self):
        """Test: Providers support health checking"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)

        with patch.object(provider, "_make_request") as mock_request:
            # Mock successful health check
            mock_request.return_value = Mock(success=True)

            health_status = provider.test_connection()
            assert health_status is True

            # Mock failed health check
            mock_request.return_value = Mock(success=False)
            health_status = provider.test_connection()
            assert health_status is False

    def test_service_info_retrieval(self):
        """Test: Providers expose service information"""
        config = {
            "api_key": "test-key",
            "country_priorities": ["MX", "ES", "AR"],
            "rate_limit_delay": 0.01,
        }

        provider = ForvoProvider(config)
        service_info = provider.get_service_info()

        assert service_info["service"] == "Forvo"
        assert service_info["type"] == "audio_provider"
        assert service_info["supported_languages"] == ["es"]
        assert service_info["supported_countries"] == ["MX", "ES", "AR"]

    def test_cost_estimation_accuracy(self):
        """Test: Cost estimation provides accurate projections"""
        # Forvo (free API)
        forvo_config = {
            "api_key": "test-key",
            "country_priorities": ["MX"],
            "rate_limit_delay": 0.01,
        }

        forvo_provider = ForvoProvider(forvo_config)

        requests = [
            MediaRequest(
                type="audio",
                content=f"word{i}",
                params={"language": "es"},
                output_path=Path(f"/tmp/test_word{i}.mp3"),
            )
            for i in range(5)
        ]

        cost_estimate = forvo_provider.get_cost_estimate(requests)

        assert cost_estimate["total_cost"] == 0.0  # Free API
        assert cost_estimate["per_request"] == 0.0
        assert cost_estimate["requests_count"] == 5

        # OpenAI (paid API)
        openai_config = {
            "api_key": "test-key",
            "model": "dall-e-2",
            "rate_limit_delay": 4.0,
        }

        openai_provider = OpenAIProvider(openai_config)

        image_requests = [
            MediaRequest(
                type="image",
                content=f"Image {i}",
                params={"size": "1024x1024"},
                output_path=Path(f"/tmp/test_Image_{i}.jpg"),
            )
            for i in range(3)
        ]

        cost_estimate = openai_provider.get_cost_estimate(image_requests)

        assert cost_estimate["total_cost"] > 0  # Paid API
        assert cost_estimate["per_request"] > 0
        assert cost_estimate["requests_count"] == 3
        assert cost_estimate["total_cost"] == cost_estimate["per_request"] * 3
