"""Unit tests for Media Provider interface."""

from pathlib import Path

import pytest
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult


class MockMediaProvider(MediaProvider):
    """Mock media provider for testing interface."""

    def __init__(self):
        super().__init__()

    @property
    def supported_types(self) -> list[str]:
        return ["image", "audio"]

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        return MediaResult(
            success=True,
            file_path=Path(f"test_{request.type}.file"),
            metadata={"mock": True},
        )

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": len(requests) * 0.01}


class TestMediaRequest:
    """Test cases for MediaRequest."""

    def test_media_request_creation(self):
        """Test MediaRequest creation."""
        request = MediaRequest(
            type="image", content="test prompt", params={"size": "large"}
        )

        assert request.type == "image"
        assert request.content == "test prompt"
        assert request.params == {"size": "large"}
        assert request.output_path is None

    def test_media_request_with_output_path(self):
        """Test MediaRequest with output path."""
        output_path = Path("/test/output")
        request = MediaRequest(
            type="audio", content="hello world", params={}, output_path=output_path
        )

        assert request.output_path == output_path

    def test_media_request_validation_empty_type(self):
        """Test MediaRequest validation fails with empty type."""
        with pytest.raises(ValueError, match="Media request type cannot be empty"):
            MediaRequest(type="", content="test", params={})

    def test_media_request_validation_empty_content(self):
        """Test MediaRequest validation fails with empty content."""
        with pytest.raises(ValueError, match="Media request content cannot be empty"):
            MediaRequest(type="image", content="", params={})

    def test_media_request_validation_none_values(self):
        """Test MediaRequest validation with None values."""
        with pytest.raises(ValueError):
            MediaRequest(type=None, content="test", params={})

        with pytest.raises(ValueError):
            MediaRequest(type="image", content=None, params={})


class TestMediaResult:
    """Test cases for MediaResult."""

    def test_media_result_success(self):
        """Test successful MediaResult creation."""
        file_path = Path("/test/file.jpg")
        result = MediaResult(
            success=True, file_path=file_path, metadata={"width": 512, "height": 512}
        )

        assert result.success
        assert result.file_path == file_path
        assert result.metadata == {"width": 512, "height": 512}
        assert result.error is None

    def test_media_result_failure(self):
        """Test failed MediaResult creation."""
        result = MediaResult(
            success=False, file_path=None, metadata={}, error="Generation failed"
        )

        assert not result.success
        assert result.file_path is None
        assert result.metadata == {}
        assert result.error == "Generation failed"

    def test_media_result_post_init(self):
        """Test MediaResult post_init validation."""
        # Should not raise - post_init is currently empty but validates structure
        result = MediaResult(success=True, file_path=None, metadata={"test": "value"})
        assert result is not None


class TestMediaProvider:
    """Test cases for MediaProvider interface."""

    def test_media_provider_interface(self):
        """Test media provider can be implemented."""
        provider = MockMediaProvider()
        assert provider is not None
        assert provider.supported_types == ["image", "audio"]

    def test_supports_type(self):
        """Test supports_type method."""
        provider = MockMediaProvider()

        assert provider.supports_type("image")
        assert provider.supports_type("audio")
        assert not provider.supports_type("video")
        assert not provider.supports_type("unknown")

    def test_validate_request_supported(self):
        """Test request validation for supported types."""
        provider = MockMediaProvider()

        image_request = MediaRequest(type="image", content="test", params={})
        assert provider.validate_request(image_request)

        audio_request = MediaRequest(type="audio", content="test", params={})
        assert provider.validate_request(audio_request)

    def test_validate_request_unsupported(self):
        """Test request validation for unsupported types."""
        provider = MockMediaProvider()

        video_request = MediaRequest(type="video", content="test", params={})
        assert not provider.validate_request(video_request)

    def test_generate_media_supported_type(self):
        """Test media generation for supported type."""
        provider = MockMediaProvider()
        request = MediaRequest(type="image", content="test prompt", params={})

        result = provider.generate_media(request)

        assert result.success
        assert result.file_path is not None
        assert result.file_path.name == "test_image.file"
        assert result.metadata["mock"] is True

    def test_generate_media_unsupported_type(self):
        """Test media generation for unsupported type."""
        provider = MockMediaProvider()
        request = MediaRequest(type="video", content="test", params={})

        result = provider.generate_media(request)

        assert not result.success
        assert result.file_path is None
        assert "not supported" in result.error

    def test_generate_image_convenience_method(self):
        """Test generate_image convenience method."""
        provider = MockMediaProvider()

        result = provider.generate_image(
            "test prompt", size="large", style="photorealistic"
        )

        assert result.success
        assert result.file_path is not None
        assert result.file_path.name == "test_image.file"

    def test_generate_audio_convenience_method(self):
        """Test generate_audio convenience method."""
        provider = MockMediaProvider()

        result = provider.generate_audio("hello world", voice="female", speed=1.2)

        assert result.success
        assert result.file_path is not None
        assert result.file_path.name == "test_audio.file"

    def test_cost_estimation(self):
        """Test cost estimation method."""
        provider = MockMediaProvider()

        requests = [
            MediaRequest(type="image", content="img1", params={}),
            MediaRequest(type="audio", content="audio1", params={}),
            MediaRequest(type="image", content="img2", params={}),
        ]

        costs = provider.get_cost_estimate(requests)

        assert costs["total_cost"] == 0.03  # 3 requests * 0.01

    def test_abstract_methods_enforcement(self):
        """Test that abstract methods must be implemented."""

        class IncompleteProvider(MediaProvider):
            # Missing implementations
            pass

        # Should not be able to instantiate incomplete provider
        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_convenience_method_parameter_passing(self):
        """Test that convenience methods pass parameters correctly."""

        class ParameterTrackingProvider(MediaProvider):
            def __init__(self):
                super().__init__()
                self.last_request = None

            @property
            def supported_types(self) -> list[str]:
                return ["image", "audio"]

            def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
                self.last_request = request
                return MediaResult(success=True, file_path=None, metadata={})

            def get_cost_estimate(
                self, requests: list[MediaRequest]
            ) -> dict[str, float]:
                return {"total_cost": 0.0}

        provider = ParameterTrackingProvider()

        # Test image generation
        provider.generate_image("test prompt", size="large", quality="high")

        assert provider.last_request.type == "image"
        assert provider.last_request.content == "test prompt"
        assert provider.last_request.params == {"size": "large", "quality": "high"}

        # Test audio generation
        provider.generate_audio("hello", voice="female", speed=1.5)

        assert provider.last_request.type == "audio"
        assert provider.last_request.content == "hello"
        assert provider.last_request.params == {"voice": "female", "speed": 1.5}
