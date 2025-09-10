"""Unit tests for Provider Registry."""

from src.providers.base.data_provider import DataProvider
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from src.providers.base.sync_provider import SyncProvider, SyncResult
from src.providers.registry import ProviderRegistry, get_provider_registry


class MockDataProvider(DataProvider):
    """Mock data provider for testing."""

    def load_data(self, identifier: str) -> dict:
        return {"mock": "data"}

    def save_data(self, identifier: str, data: dict) -> bool:
        return True

    def exists(self, identifier: str) -> bool:
        return True

    def list_identifiers(self) -> list[str]:
        return ["mock_id"]


class MockMediaProvider(MediaProvider):
    """Mock media provider for testing."""

    def __init__(self, supported_types: list[str] = None):
        self._supported_types = supported_types or ["image"]

    @property
    def supported_types(self) -> list[str]:
        return self._supported_types

    def generate_media(self, request: MediaRequest) -> MediaResult:
        return MediaResult(success=True, file_path=None, metadata={})

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": 0.0}


class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing."""

    def test_connection(self) -> bool:
        return True

    def sync_templates(self, note_type: str, templates: list[dict]) -> SyncResult:
        return SyncResult(success=True, processed_count=1, metadata={})

    def sync_media(self, media_files) -> SyncResult:
        return SyncResult(success=True, processed_count=1, metadata={})

    def sync_cards(self, cards: list[dict]) -> SyncResult:
        return SyncResult(success=True, processed_count=len(cards), metadata={})

    def list_existing(self, note_type: str) -> list[dict]:
        return []


class TestProviderRegistry:
    """Test cases for ProviderRegistry."""

    def test_registry_creation(self):
        """Test registry can be created."""
        registry = ProviderRegistry()
        assert registry is not None
        assert registry.list_data_providers() == []
        assert registry.list_media_providers() == []
        assert registry.list_sync_providers() == []

    def test_register_and_get_data_provider(self):
        """Test registering and retrieving data providers."""
        registry = ProviderRegistry()
        provider = MockDataProvider()

        # Register provider
        registry.register_data_provider("test", provider)

        # Retrieve provider
        retrieved = registry.get_data_provider("test")
        assert retrieved is provider

        # List providers
        providers = registry.list_data_providers()
        assert "test" in providers
        assert len(providers) == 1

    def test_get_nonexistent_data_provider(self):
        """Test retrieving non-existent data provider returns None."""
        registry = ProviderRegistry()

        result = registry.get_data_provider("nonexistent")
        assert result is None

    def test_register_and_get_media_provider(self):
        """Test registering and retrieving media providers."""
        registry = ProviderRegistry()
        provider = MockMediaProvider()

        # Register provider
        registry.register_media_provider("test", provider)

        # Retrieve provider
        retrieved = registry.get_media_provider("test")
        assert retrieved is provider

        # List providers
        providers = registry.list_media_providers()
        assert "test" in providers
        assert len(providers) == 1

    def test_get_nonexistent_media_provider(self):
        """Test retrieving non-existent media provider returns None."""
        registry = ProviderRegistry()

        result = registry.get_media_provider("nonexistent")
        assert result is None

    def test_register_and_get_sync_provider(self):
        """Test registering and retrieving sync providers."""
        registry = ProviderRegistry()
        provider = MockSyncProvider()

        # Register provider
        registry.register_sync_provider("test", provider)

        # Retrieve provider
        retrieved = registry.get_sync_provider("test")
        assert retrieved is provider

        # List providers
        providers = registry.list_sync_providers()
        assert "test" in providers
        assert len(providers) == 1

    def test_get_nonexistent_sync_provider(self):
        """Test retrieving non-existent sync provider returns None."""
        registry = ProviderRegistry()

        result = registry.get_sync_provider("nonexistent")
        assert result is None

    def test_duplicate_registration(self):
        """Test overwriting existing provider registration."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()

        # Register first provider
        registry.register_data_provider("test", provider1)
        retrieved1 = registry.get_data_provider("test")
        assert retrieved1 is provider1

        # Overwrite with second provider
        registry.register_data_provider("test", provider2)
        retrieved2 = registry.get_data_provider("test")
        assert retrieved2 is provider2
        assert retrieved2 is not provider1

        # Should still have only one provider in list
        providers = registry.list_data_providers()
        assert len(providers) == 1

    def test_get_media_providers_by_type(self):
        """Test filtering media providers by supported type."""
        registry = ProviderRegistry()

        image_provider = MockMediaProvider(["image"])
        audio_provider = MockMediaProvider(["audio"])
        both_provider = MockMediaProvider(["image", "audio"])

        registry.register_media_provider("image", image_provider)
        registry.register_media_provider("audio", audio_provider)
        registry.register_media_provider("both", both_provider)

        # Test image providers
        image_providers = registry.get_media_providers_by_type("image")
        assert len(image_providers) == 2  # image and both
        assert image_provider in image_providers
        assert both_provider in image_providers
        assert audio_provider not in image_providers

        # Test audio providers
        audio_providers = registry.get_media_providers_by_type("audio")
        assert len(audio_providers) == 2  # audio and both
        assert audio_provider in audio_providers
        assert both_provider in audio_providers
        assert image_provider not in audio_providers

        # Test unsupported type
        video_providers = registry.get_media_providers_by_type("video")
        assert len(video_providers) == 0

    def test_clear_all(self):
        """Test clearing all registered providers."""
        registry = ProviderRegistry()

        # Register providers of all types
        registry.register_data_provider("data", MockDataProvider())
        registry.register_media_provider("media", MockMediaProvider())
        registry.register_sync_provider("sync", MockSyncProvider())

        # Verify they're registered
        assert len(registry.list_data_providers()) == 1
        assert len(registry.list_media_providers()) == 1
        assert len(registry.list_sync_providers()) == 1

        # Clear all
        registry.clear_all()

        # Verify all are cleared
        assert registry.list_data_providers() == []
        assert registry.list_media_providers() == []
        assert registry.list_sync_providers() == []

    def test_get_provider_info(self):
        """Test getting comprehensive provider information."""
        registry = ProviderRegistry()

        # Register providers with different capabilities
        image_provider = MockMediaProvider(["image"])
        audio_provider = MockMediaProvider(["audio"])

        registry.register_data_provider("data1", MockDataProvider())
        registry.register_data_provider("data2", MockDataProvider())
        registry.register_media_provider("image", image_provider)
        registry.register_media_provider("audio", audio_provider)
        registry.register_sync_provider("sync", MockSyncProvider())

        info = registry.get_provider_info()

        # Check structure and counts
        assert "data_providers" in info
        assert "media_providers" in info
        assert "sync_providers" in info

        assert info["data_providers"]["count"] == 2
        assert info["media_providers"]["count"] == 2
        assert info["sync_providers"]["count"] == 1

        # Check names
        assert set(info["data_providers"]["names"]) == {"data1", "data2"}
        assert set(info["media_providers"]["names"]) == {"image", "audio"}
        assert info["sync_providers"]["names"] == ["sync"]

        # Check media providers by type
        assert info["media_providers"]["by_type"]["image"] == ["image"]
        assert info["media_providers"]["by_type"]["audio"] == ["audio"]

    def test_global_registry_singleton(self):
        """Test that get_provider_registry returns same instance."""
        registry1 = get_provider_registry()
        registry2 = get_provider_registry()

        assert registry1 is registry2

        # Test that registration persists
        provider = MockDataProvider()
        registry1.register_data_provider("test", provider)

        retrieved = registry2.get_data_provider("test")
        assert retrieved is provider

    def test_from_config_unsupported_provider_types(self):
        """Test that unsupported provider types raise ValueError"""
        import json
        import tempfile
        from pathlib import Path

        import pytest
        from src.core.config import Config

        # Test unsupported media provider
        config_data = {
            "providers": {
                "media": {"type": "unsupported"},
                "sync": {"type": "anki"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)
            with pytest.raises(
                ValueError, match="Unsupported media provider type: unsupported"
            ):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()

        # Test unsupported sync provider
        config_data = {
            "providers": {
                "media": {"type": "openai"},
                "sync": {"type": "unsupported"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)
            with pytest.raises(
                ValueError, match="Unsupported sync provider type: unsupported"
            ):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()


class TestProviderRegistryFromConfig:
    """Test cases for ProviderRegistry.from_config method."""

    def test_from_config_basic_functionality(self):
        """Test from_config method creates providers with valid configuration"""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from src.core.config import Config

        config_data = {
            "providers": {
                "data": {"type": "json", "base_path": "."},
                "media": {"type": "openai"},
                "sync": {"type": "anki"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock the providers to avoid requiring actual API keys/Anki
            with (
                patch(
                    "src.providers.media.openai_provider.OpenAIProvider"
                ) as mock_openai,
                patch("src.providers.sync.anki_provider.AnkiProvider") as mock_anki,
            ):
                registry = ProviderRegistry.from_config(config)

                # Verify providers were created
                assert registry.get_data_provider("default") is not None
                assert registry.get_media_provider("default") is not None
                assert registry.get_sync_provider("default") is not None

                # Verify correct types and initialization
                data_provider = registry.get_data_provider("default")
                assert data_provider.__class__.__name__ == "JSONDataProvider"
                mock_openai.assert_called_once()
                mock_anki.assert_called_once()
        finally:
            Path(config_path).unlink()

    def test_from_config_provider_failure(self):
        """Test provider initialization fails fast when providers cannot be created"""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        import pytest
        from src.core.config import Config

        config_data = {
            "providers": {
                "media": {"type": "openai"},  # Will fail without API key
                "sync": {"type": "anki"},  # Will fail without Anki running
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock provider imports to simulate failures and expect exception
            with (
                patch(
                    "src.providers.media.openai_provider.OpenAIProvider",
                    side_effect=Exception("API key missing"),
                ),
                pytest.raises(Exception, match="API key missing"),
            ):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()

    def test_from_config_missing_sections(self):
        """Test handling of missing provider configuration sections"""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from src.core.config import Config

        # Config with no providers section
        config_data = {"system": {"log_level": "info"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock the providers to avoid requiring actual API keys/Anki
            with (
                patch(
                    "src.providers.media.openai_provider.OpenAIProvider"
                ) as mock_openai,
                patch("src.providers.sync.anki_provider.AnkiProvider") as mock_anki,
            ):
                registry = ProviderRegistry.from_config(config)

                # Should create default providers using default types
                assert registry.get_media_provider("default") is not None
                assert registry.get_sync_provider("default") is not None

                # Should use defaults (openai for media, anki for sync)
                mock_openai.assert_called_once()
                mock_anki.assert_called_once()
        finally:
            Path(config_path).unlink()
