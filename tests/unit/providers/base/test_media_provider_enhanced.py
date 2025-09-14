#!/usr/bin/env python3
"""
Enhanced MediaProvider Base Class Tests
Tests the new architecture patterns including batch processing, config injection, and validation
"""

import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult


class TestableMediaProvider(MediaProvider):
    """Concrete implementation of MediaProvider for testing"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)

    @property
    def supported_types(self) -> list[str]:
        return ["test_type"]

    def validate_config(self, config: dict[str, Any]) -> None:
        """Test implementation of config validation"""
        if "required_key" in config and not config["required_key"]:
            raise ValueError("required_key cannot be empty")
        if "invalid_value" in config:
            raise ValueError("invalid_value is not allowed")

    def _setup_from_config(self) -> None:
        """Test setup from config"""
        self.test_attribute = self.config.get("test_attribute", "default")
        self._rate_limit_delay = self.config.get("rate_limit_delay", 0.0)

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Test implementation"""
        return MediaResult(
            success=True,
            file_path=Path(f"/tmp/test_{request.content}.txt"),
            metadata={"type": request.type, "content": request.content},
        )

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        """Test cost estimation"""
        return {
            "total_cost": len(requests) * 0.01,
            "per_request": 0.01,
            "requests_count": len(requests),
        }


class TestMediaProviderEnhanced:
    """Test enhanced MediaProvider functionality"""

    def test_batch_processing_abstract_method(self):
        """Test: generate_batch abstract method enforced"""
        # ARRANGE: Create provider instance
        config = {"required_key": "test_value", "rate_limit_delay": 0.01}
        provider = TestableMediaProvider(config)

        requests = [
            MediaRequest(type="test_type", content="item1", params={}),
            MediaRequest(type="test_type", content="item2", params={}),
            MediaRequest(type="test_type", content="item3", params={}),
        ]

        # ACT: Call batch processing method
        results = provider.generate_batch(requests)

        # ASSERT: Batch processing works and returns correct number of results
        assert len(results) == len(requests)
        assert all(isinstance(result, MediaResult) for result in results)
        assert all(result.success for result in results)

        # Verify each result corresponds to the correct request
        for i, result in enumerate(results):
            assert result.metadata["content"] == f"item{i+1}"
            assert result.file_path == Path(f"/tmp/test_item{i+1}.txt")

    def test_file_validation_framework(self):
        """Test: Universal file validation works"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        # Test valid request
        request = MediaRequest(type="test_type", content="valid_content", params={})
        assert provider.validate_request(request) is True

        # Test invalid request (unsupported type)
        invalid_request = MediaRequest(
            type="unsupported_type", content="content", params={}
        )
        assert provider.validate_request(invalid_request) is False

    def test_rate_limiting_framework(self):
        """Test: Rate limiting prevents API overuse"""
        # ARRANGE: Provider with rate limiting configured
        config = {"required_key": "test", "rate_limit_delay": 0.05}
        provider = TestableMediaProvider(config)

        requests = [
            MediaRequest(type="test_type", content=f"item{i}", params={})
            for i in range(4)
        ]

        # ACT: Execute batch with rate limiting
        start_time = time.time()
        results = provider.generate_batch(requests)
        elapsed_time = time.time() - start_time

        # ASSERT: Rate limiting was applied
        # Should take at least rate_limit_delay * (num_requests - 1)
        expected_min_time = config["rate_limit_delay"] * (len(requests) - 1)
        assert elapsed_time >= expected_min_time * 0.8  # Allow 20% variance for timing

        assert len(results) == len(requests)
        assert all(result.success for result in results)

    def test_config_injection_validation(self):
        """Test: Config injection with fail-fast validation"""
        # Test valid configuration
        valid_config = {"required_key": "valid_value", "test_attribute": "configured"}
        provider = TestableMediaProvider(valid_config)

        assert provider.config == valid_config
        assert provider.test_attribute == "configured"

        # Test invalid configuration - should raise ValueError
        invalid_config = {"required_key": ""}  # Empty required_key
        with pytest.raises(ValueError, match="required_key cannot be empty"):
            TestableMediaProvider(invalid_config)

        # Test another invalid configuration
        invalid_config2 = {"invalid_value": "not_allowed"}
        with pytest.raises(ValueError, match="invalid_value is not allowed"):
            TestableMediaProvider(invalid_config2)

        # Test empty configuration (should not raise error for this test provider)
        empty_provider = TestableMediaProvider({})
        assert empty_provider.config == {}
        assert empty_provider.test_attribute == "default"

    def test_fail_fast_initialization_pattern(self):
        """Test: Providers fail immediately on invalid config"""
        # Should fail during __init__, not later during usage
        with pytest.raises(ValueError, match="required_key cannot be empty"):
            TestableMediaProvider({"required_key": ""})

        # Verify that valid config passes through initialization
        provider = TestableMediaProvider({"required_key": "valid"})
        assert provider.config["required_key"] == "valid"

    def test_convenience_methods(self):
        """Test: Convenience methods work correctly"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        # Test generate_image convenience method
        with patch.object(provider, "generate_media") as mock_generate:
            mock_generate.return_value = MediaResult(True, Path("/tmp/image.jpg"), {})

            _ = provider.generate_image("test prompt", size="1024x1024")

            # Verify generate_media was called with correct MediaRequest
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[0][0]  # First argument
            assert call_args.type == "image"
            assert call_args.content == "test prompt"
            assert call_args.params == {"size": "1024x1024"}

        # Test generate_audio convenience method
        with patch.object(provider, "generate_media") as mock_generate:
            mock_generate.return_value = MediaResult(True, Path("/tmp/audio.mp3"), {})

            _ = provider.generate_audio("hello", language="es")

            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[0][0]
            assert call_args.type == "audio"
            assert call_args.content == "hello"
            assert call_args.params == {"language": "es"}

    def test_media_request_validation(self):
        """Test: MediaRequest validation works correctly"""
        # Valid request
        valid_request = MediaRequest(
            type="test_type", content="valid content", params={"param1": "value1"}
        )
        assert valid_request.type == "test_type"
        assert valid_request.content == "valid content"

        # Invalid requests should raise ValueError
        with pytest.raises(ValueError, match="Media request type cannot be empty"):
            MediaRequest(type="", content="content", params={})

        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type="test", content="", params={})

    def test_media_result_structure(self):
        """Test: MediaResult structure and validation"""
        # Successful result
        success_result = MediaResult(
            success=True, file_path=Path("/tmp/test.jpg"), metadata={"key": "value"}
        )
        assert success_result.success is True
        assert success_result.file_path == Path("/tmp/test.jpg")
        assert success_result.metadata == {"key": "value"}
        assert success_result.error is None

        # Failed result
        failure_result = MediaResult(
            success=False, file_path=None, metadata={}, error="Test error message"
        )
        assert failure_result.success is False
        assert failure_result.file_path is None
        assert failure_result.error == "Test error message"

    def test_supported_types_property(self):
        """Test: supported_types property works correctly"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        assert provider.supported_types == ["test_type"]
        assert provider.supports_type("test_type") is True
        assert provider.supports_type("unsupported_type") is False

    def test_cost_estimation_framework(self):
        """Test: Cost estimation framework functions correctly"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        requests = [
            MediaRequest(type="test_type", content=f"item{i}", params={})
            for i in range(5)
        ]

        cost_estimate = provider.get_cost_estimate(requests)

        assert cost_estimate["total_cost"] == 0.05  # 5 * 0.01
        assert cost_estimate["per_request"] == 0.01
        assert cost_estimate["requests_count"] == 5

    def test_error_handling_in_media_generation(self):
        """Test: Error handling works correctly in media generation"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        # Mock _generate_media_impl to raise an exception
        with patch.object(provider, "_generate_media_impl") as mock_impl:
            mock_impl.side_effect = Exception("Test exception")

            request = MediaRequest(type="test_type", content="test", params={})
            result = provider.generate_media(request)

            assert result.success is False
            assert result.error == "Test exception"
            assert result.file_path is None

    def test_request_validation_flow(self):
        """Test: Request validation flow works correctly"""
        config = {"required_key": "test"}
        provider = TestableMediaProvider(config)

        # Test unsupported media type
        unsupported_request = MediaRequest(
            type="unsupported_type", content="test content", params={}
        )

        result = provider.generate_media(unsupported_request)

        assert result.success is False
        assert "Request not supported by TestableMediaProvider" in result.error
        assert result.file_path is None


class TestDefaultBatchImplementation:
    """Test the default batch implementation behavior"""

    def test_default_batch_implementation_with_rate_limiting(self):
        """Test: Default batch implementation applies rate limiting"""
        config = {"required_key": "test", "rate_limit_delay": 0.02}
        provider = TestableMediaProvider(config)

        requests = [
            MediaRequest(type="test_type", content=f"item{i}", params={})
            for i in range(3)
        ]

        start_time = time.time()
        results = provider.generate_batch(requests)
        elapsed_time = time.time() - start_time

        # Verify rate limiting was applied
        expected_min_time = config["rate_limit_delay"] * (len(requests) - 1)
        assert elapsed_time >= expected_min_time * 0.7  # Allow variance

        assert len(results) == len(requests)
        assert all(r.success for r in results)

    def test_default_batch_handles_individual_failures(self):
        """Test: Default batch implementation handles individual failures"""
        config = {"required_key": "test", "rate_limit_delay": 0.001}
        provider = TestableMediaProvider(config)

        # Mock implementation to fail on certain content
        original_impl = provider._generate_media_impl

        def selective_failure(request):
            if request.content == "fail_me":
                raise Exception("Simulated failure")
            return original_impl(request)

        with patch.object(
            provider, "_generate_media_impl", side_effect=selective_failure
        ):
            requests = [
                MediaRequest(type="test_type", content="success1", params={}),
                MediaRequest(type="test_type", content="fail_me", params={}),
                MediaRequest(type="test_type", content="success2", params={}),
            ]

            results = provider.generate_batch(requests)

            assert len(results) == 3
            assert results[0].success is True
            assert results[1].success is False
            assert results[2].success is True
            assert "Simulated failure" in results[1].error

    def test_batch_processing_preserves_request_order(self):
        """Test: Batch processing preserves request order"""
        config = {"required_key": "test", "rate_limit_delay": 0.001}
        provider = TestableMediaProvider(config)

        requests = [
            MediaRequest(type="test_type", content=f"item_{i:03d}", params={})
            for i in range(10)
        ]

        results = provider.generate_batch(requests)

        assert len(results) == 10
        for i, result in enumerate(results):
            expected_content = f"item_{i:03d}"
            assert result.metadata["content"] == expected_content
