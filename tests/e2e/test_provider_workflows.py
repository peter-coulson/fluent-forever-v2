"""End-to-end tests for provider workflows."""

from pathlib import Path
from unittest.mock import patch

import pytest
from src.providers.data.json_provider import JSONDataProvider

from tests.fixtures.mock_implementations import (
    MockDataProvider,
    MockMediaProvider,
    MockSyncProvider,
)


class TestProviderWorkflows:
    """Test end-to-end provider workflows."""

    def test_e2e_data_provider_lifecycle(self, tmp_path):
        """Test full data provider workflow (save/load/exists)."""
        # Create real JSON data provider
        provider = JSONDataProvider(tmp_path)

        # Test data
        test_data = {
            "words": ["hola", "mundo"],
            "definitions": {"hola": "hello", "mundo": "world"},
        }

        # Test save
        assert provider.save_data("vocabulary", test_data)

        # Test exists
        assert provider.exists("vocabulary")
        assert not provider.exists("nonexistent")

        # Test load
        loaded_data = provider.load_data("vocabulary")
        assert loaded_data == test_data

        # Test list
        identifiers = provider.list_identifiers()
        assert "vocabulary" in identifiers

        # Test backup
        backup_id = provider.backup_data("vocabulary")
        assert backup_id is not None
        assert provider.exists(backup_id)

    def test_e2e_data_provider_empty_file_handling(self, tmp_path):
        """Test data provider handles empty and non-existent files gracefully."""
        provider = JSONDataProvider(tmp_path)

        # Test loading non-existent file
        empty_data = provider.load_data("nonexistent")
        assert empty_data == {}

        # Create empty file
        empty_file = tmp_path / "empty.json"
        empty_file.touch()

        # Test loading empty file
        empty_data = provider.load_data("empty")
        assert empty_data == {}

    def test_e2e_data_provider_invalid_json_handling(self, tmp_path):
        """Test data provider handles invalid JSON gracefully."""
        provider = JSONDataProvider(tmp_path)

        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json")

        # Test loading invalid JSON
        with pytest.raises(ValueError, match="Error loading invalid"):
            provider.load_data("invalid")

    def test_e2e_mock_data_provider_failure_simulation(self):
        """Test mock data provider failure scenarios."""
        provider = MockDataProvider()

        # Test normal operation
        assert provider.save_data("test", {"key": "value"})
        assert provider.exists("test")
        assert provider.load_data("test") == {"key": "value"}

        # Simulate failure
        provider.should_fail = True

        # Test failure handling
        with pytest.raises(ValueError):
            provider.load_data("test")

        assert not provider.save_data("new_data", {"key": "value"})

    def test_e2e_media_provider_connection_failure(self):
        """Test external service unavailable scenarios."""
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("audio")

        # Test normal operation
        request = MediaRequest(type="audio", content="test", params={})
        result = provider.generate_media(request)
        assert result.success

        # Simulate service failure
        provider.should_fail = True

        # Test service failure
        result = provider.generate_media(request)
        assert not result.success

    def test_e2e_media_provider_generation_workflow(self):
        """Test complete media generation workflow."""
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("audio")

        # Create media request
        request = MediaRequest(
            type="audio",
            content="hola",
            params={"language": "es"},
            output_path=Path("test_audio.mp3"),
        )

        # Test successful generation
        result = provider.generate_media(request)

        assert result.success
        assert result.file_path is not None
        assert result.metadata["content"] == "hola"
        assert result.error is None

    def test_e2e_media_provider_unsupported_type(self):
        """Test handling of unsupported media types."""
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("audio")  # Only supports audio

        # Request unsupported type
        request = MediaRequest(
            type="video",  # Not supported
            content="test",
            params={},
        )

        result = provider.generate_media(request)

        assert not result.success
        assert "not supported" in result.error.lower()

    def test_e2e_sync_provider_workflow(self):
        """Test complete sync provider workflow."""
        provider = MockSyncProvider()

        # Test connection
        assert provider.test_connection()

        # Test service info
        info = provider.get_service_info()
        assert "service" in info
        assert "type" in info

        # Test card sync
        test_cards = [
            {"front": "hola", "back": "hello"},
            {"front": "mundo", "back": "world"},
        ]

        result = provider.sync_cards(test_cards)

        assert result.success
        assert result.processed_count == 2
        assert result.error_message == ""

    def test_e2e_sync_provider_failure_scenario(self):
        """Test sync provider failure handling."""
        provider = MockSyncProvider()

        # Simulate failure
        provider.should_fail = True

        # Test connection failure
        assert not provider.test_connection()

        # Test sync failure
        test_cards = [{"front": "test", "back": "test"}]
        result = provider.sync_cards(test_cards)

        assert not result.success
        assert result.processed_count == 0
        assert result.error_message != ""

    def test_e2e_provider_authentication_simulation(self):
        """Test authentication error scenarios."""
        # This test simulates authentication failures that might occur
        # with real providers (though our mocks don't implement actual auth)
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("audio")

        # Simulate authentication failure
        provider.should_fail = True

        # Media generation should fail (simulating auth issue)
        request = MediaRequest(type="audio", content="test", params={})
        result = provider.generate_media(request)
        assert not result.success

        # Service operations should fail
        from src.providers.base.media_provider import MediaRequest

        request = MediaRequest(type="audio", content="test", params={})

        result = provider.generate_media(request)
        assert not result.success
        assert "failure" in result.error

    def test_e2e_provider_cost_estimation(self):
        """Test provider cost estimation functionality."""
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("image")

        # Create multiple requests
        requests = [
            MediaRequest(type="image", content="cat", params={}),
            MediaRequest(type="image", content="dog", params={}),
            MediaRequest(type="audio", content="hello", params={}),  # Wrong type
        ]

        # Get cost estimate
        estimate = provider.get_cost_estimate(requests)

        assert "total_cost" in estimate
        assert "per_request" in estimate
        assert "requests_count" in estimate

        # Should only count supported requests (2 image requests)
        assert estimate["requests_count"] == 2

    def test_e2e_provider_directory_creation(self, tmp_path):
        """Test that providers handle directory creation properly."""
        # Use a deep path that doesn't exist
        deep_path = tmp_path / "level1" / "level2" / "level3"

        # Create JSON provider with deep path
        provider = JSONDataProvider(deep_path)

        # Save data should create directories
        assert provider.save_data("test", {"key": "value"})

        # Verify directories were created
        assert deep_path.exists()
        assert (deep_path / "test.json").exists()

    def test_e2e_concurrent_provider_operations(self, tmp_path):
        """Test provider operations work correctly with multiple instances."""
        # Create two provider instances on same directory
        provider1 = JSONDataProvider(tmp_path)
        provider2 = JSONDataProvider(tmp_path)

        # Save with first provider
        assert provider1.save_data("shared", {"source": "provider1"})

        # Load with second provider
        data = provider2.load_data("shared")
        assert data["source"] == "provider1"

        # Both should see the same files
        files1 = set(provider1.list_identifiers())
        files2 = set(provider2.list_identifiers())
        assert files1 == files2

    @patch.dict("os.environ", {"TEST_API_KEY": "test_value"})
    def test_e2e_provider_environment_integration(self):
        """Test provider integration with environment variables."""
        # This would test real provider environment integration
        # For now, we'll test that environment access works
        import os

        assert os.environ.get("TEST_API_KEY") == "test_value"

        # Mock providers don't use real environment variables,
        # but this tests the environment is accessible
        from src.providers.base.media_provider import MediaRequest

        provider = MockMediaProvider("audio")
        request = MediaRequest(type="audio", content="test", params={})
        result = provider.generate_media(request)
        assert result.success  # Should work regardless
