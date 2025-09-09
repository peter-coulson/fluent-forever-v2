"""Unit tests for Mock Media Provider."""

from pathlib import Path

from src.providers.base.media_provider import MediaRequest
from src.providers.media.mock_provider import MockMediaProvider


class TestMockMediaProvider:
    """Test cases for MockMediaProvider."""

    def test_provider_creation_defaults(self):
        """Test mock provider creation with defaults."""
        provider = MockMediaProvider()
        assert provider.supported_types == ["image", "audio"]
        assert not provider.should_fail
        assert provider.generation_count == 0
        assert len(provider.generated_requests) == 0

    def test_provider_creation_custom(self):
        """Test mock provider creation with custom parameters."""
        provider = MockMediaProvider(supported_types=["image"], should_fail=True)
        assert provider.supported_types == ["image"]
        assert provider.should_fail
        assert "audio" not in provider.supported_types

    def test_successful_media_generation(self):
        """Test successful media generation."""
        provider = MockMediaProvider()
        request = MediaRequest(
            type="image", content="test image", params={"filename": "test"}
        )

        result = provider.generate_media(request)

        assert result.success
        assert result.file_path is not None
        assert result.file_path.name == "test.jpg"
        assert result.metadata["mock"] is True
        assert result.metadata["generation_id"] == 1
        assert result.error is None

        # Check tracking
        assert provider.generation_count == 1
        assert len(provider.generated_requests) == 1
        assert provider.generated_requests[0] is request

    def test_failure_mode(self):
        """Test provider configured to fail."""
        provider = MockMediaProvider(should_fail=True)
        request = MediaRequest(type="image", content="test image", params={})

        result = provider.generate_media(request)

        assert not result.success
        assert result.file_path is None
        assert result.error == "Mock provider configured to fail"
        assert result.metadata["failure_mode"] is True

        # Should still track the request
        assert len(provider.generated_requests) == 1

    def test_unsupported_media_type(self):
        """Test generation with unsupported media type."""
        provider = MockMediaProvider(supported_types=["image"])
        request = MediaRequest(type="audio", content="test audio", params={})

        result = provider.generate_media(request)

        assert not result.success
        assert result.file_path is None
        assert "doesn't support media type: audio" in result.error

    def test_filename_generation(self):
        """Test automatic filename generation."""
        provider = MockMediaProvider()

        # Test image without filename
        image_request = MediaRequest(type="image", content="test", params={})
        image_result = provider.generate_media(image_request)
        assert image_result.file_path.name == "mock_image_1.jpg"

        # Test audio without filename
        audio_request = MediaRequest(type="audio", content="test", params={})
        audio_result = provider.generate_media(audio_request)
        assert audio_result.file_path.name == "mock_audio_2.mp3"

        # Test with custom filename
        custom_request = MediaRequest(
            type="image", content="test", params={"filename": "custom_name.png"}
        )
        custom_result = provider.generate_media(custom_request)
        assert custom_result.file_path.name == "custom_name.png"

    def test_output_path_handling(self):
        """Test handling of output path."""
        provider = MockMediaProvider()
        output_path = Path("/custom/output/path")

        request = MediaRequest(
            type="image",
            content="test",
            params={"filename": "test.jpg"},
            output_path=output_path,
        )

        result = provider.generate_media(request)
        assert result.file_path == output_path / "test.jpg"

    def test_cost_estimation(self):
        """Test cost estimation functionality."""
        provider = MockMediaProvider()

        requests = [
            MediaRequest(type="image", content="img1", params={}),
            MediaRequest(type="image", content="img2", params={}),
            MediaRequest(type="audio", content="audio1", params={}),
            MediaRequest(type="video", content="unsupported", params={}),  # unsupported
        ]

        costs = provider.get_cost_estimate(requests)

        assert costs["total_cost"] == 0.025  # 2 * 0.01 + 1 * 0.005
        assert costs["image_cost"] == 0.02
        assert costs["audio_cost"] == 0.005
        assert costs["total_requests"] == 3.0  # video excluded
        assert costs["image_requests"] == 2.0
        assert costs["audio_requests"] == 1.0

    def test_request_tracking(self):
        """Test request tracking functionality."""
        provider = MockMediaProvider()

        image_request = MediaRequest(type="image", content="img", params={})
        audio_request = MediaRequest(type="audio", content="audio", params={})

        provider.generate_media(image_request)
        provider.generate_media(audio_request)

        # Test get_request_history
        history = provider.get_request_history()
        assert len(history) == 2
        assert history[0] is image_request
        assert history[1] is audio_request

        # Test get_requests_by_type
        image_requests = provider.get_requests_by_type("image")
        assert len(image_requests) == 1
        assert image_requests[0] is image_request

        audio_requests = provider.get_requests_by_type("audio")
        assert len(audio_requests) == 1
        assert audio_requests[0] is audio_request

        video_requests = provider.get_requests_by_type("video")
        assert len(video_requests) == 0

    def test_clear_history(self):
        """Test clearing request history."""
        provider = MockMediaProvider()

        # Generate some requests
        for i in range(3):
            request = MediaRequest(type="image", content=f"img{i}", params={})
            provider.generate_media(request)

        assert provider.generation_count == 3
        assert len(provider.generated_requests) == 3

        # Clear history
        provider.clear_history()

        assert provider.generation_count == 0
        assert len(provider.generated_requests) == 0

    def test_dynamic_configuration(self):
        """Test dynamic configuration changes."""
        provider = MockMediaProvider(supported_types=["image"])

        # Initially doesn't support audio
        assert not provider.supports_type("audio")

        # Add audio support
        provider.add_supported_type("audio")
        assert provider.supports_type("audio")
        assert "audio" in provider.supported_types

        # Remove image support
        provider.remove_supported_type("image")
        assert not provider.supports_type("image")
        assert "image" not in provider.supported_types

        # Test failure mode toggle
        assert not provider.should_fail
        provider.set_failure_mode(True)
        assert provider.should_fail

        provider.set_failure_mode(False)
        assert not provider.should_fail

    def test_metadata_content(self):
        """Test metadata contains expected information."""
        provider = MockMediaProvider()

        request = MediaRequest(
            type="audio",
            content="hello world",
            params={"language": "es", "voice": "female"},
        )

        result = provider.generate_media(request)

        metadata = result.metadata
        assert metadata["mock"] is True
        assert metadata["content"] == "hello world"
        assert metadata["type"] == "audio"
        assert metadata["params"] == {"language": "es", "voice": "female"}
        assert metadata["generation_id"] == 1
        assert metadata["request_count"] == 1

    def test_convenience_methods(self):
        """Test convenience methods work correctly."""
        provider = MockMediaProvider()

        # Test generate_image
        image_result = provider.generate_image("test image", size="large")
        assert image_result.success
        assert image_result.metadata["type"] == "image"
        assert image_result.metadata["params"] == {"size": "large"}

        # Test generate_audio
        audio_result = provider.generate_audio("test audio", voice="female")
        assert audio_result.success
        assert audio_result.metadata["type"] == "audio"
        assert audio_result.metadata["params"] == {"voice": "female"}
