"""Unit tests for Provider Registry."""

from src.providers.base.data_provider import DataProvider
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from src.providers.base.sync_provider import SyncProvider, SyncResult
from src.providers.registry import ProviderRegistry, get_provider_registry


class MockDataProvider(DataProvider):
    """Mock data provider for testing."""

    def __init__(self):
        super().__init__()

    def _load_data_impl(self, identifier: str) -> dict:
        return {"mock": "data"}

    def _save_data_impl(self, identifier: str, data: dict) -> bool:
        return True

    def exists(self, identifier: str) -> bool:
        return True

    def list_identifiers(self) -> list[str]:
        return ["mock_id"]


class MockMediaProvider(MediaProvider):
    """Mock media provider for testing."""

    def __init__(self, supported_types: list[str] = None):
        super().__init__()
        self._supported_types = supported_types or ["image"]

    @property
    def supported_types(self) -> list[str]:
        return self._supported_types

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        return MediaResult(success=True, file_path=None, metadata={})

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": 0.0}


class MockAudioProvider(MediaProvider):
    """Mock audio-only provider for testing."""

    def __init__(self):
        super().__init__()

    @property
    def supported_types(self) -> list[str]:
        return ["audio"]

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        return MediaResult(success=True, file_path=None, metadata={})

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": 0.0}


class MockImageProvider(MediaProvider):
    """Mock image-only provider for testing."""

    def __init__(self):
        super().__init__()

    @property
    def supported_types(self) -> list[str]:
        return ["image"]

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        return MediaResult(success=True, file_path=None, metadata={})

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": 0.0}


class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing."""

    def __init__(self):
        super().__init__()

    def _test_connection_impl(self) -> bool:
        return True

    def sync_templates(self, note_type: str, templates: list[dict]) -> SyncResult:
        return SyncResult(success=True, processed_count=1, metadata={})

    def sync_media(self, media_files) -> SyncResult:
        return SyncResult(success=True, processed_count=1, metadata={})

    def _sync_cards_impl(self, cards: list[dict]) -> SyncResult:
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
        assert registry.list_audio_providers() == []
        assert registry.list_image_providers() == []
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

    def test_clear_all(self):
        """Test clearing all registered providers."""
        registry = ProviderRegistry()

        # Register providers of all types
        registry.register_data_provider("data", MockDataProvider())
        registry.register_audio_provider("audio", MockAudioProvider())
        registry.register_image_provider("image", MockImageProvider())
        registry.register_sync_provider("sync", MockSyncProvider())

        # Verify they're registered
        assert len(registry.list_data_providers()) == 1
        assert len(registry.list_audio_providers()) == 1
        assert len(registry.list_image_providers()) == 1
        assert len(registry.list_sync_providers()) == 1

        # Clear all
        registry.clear_all()

        # Verify all are cleared
        assert registry.list_data_providers() == []
        assert registry.list_audio_providers() == []
        assert registry.list_image_providers() == []
        assert registry.list_sync_providers() == []

    def test_get_provider_info(self):
        """Test getting comprehensive provider information."""
        registry = ProviderRegistry()

        # Register providers with different capabilities
        image_provider = MockImageProvider()
        audio_provider = MockAudioProvider()

        registry.register_data_provider("data1", MockDataProvider())
        registry.register_data_provider("data2", MockDataProvider())
        registry.register_image_provider("image", image_provider)
        registry.register_audio_provider("audio", audio_provider)
        registry.register_sync_provider("sync", MockSyncProvider())

        info = registry.get_provider_info()

        # Check structure and counts
        assert "data_providers" in info
        assert "audio_providers" in info
        assert "image_providers" in info
        assert "sync_providers" in info

        assert info["data_providers"]["count"] == 2
        assert info["audio_providers"]["count"] == 1
        assert info["image_providers"]["count"] == 1
        assert info["sync_providers"]["count"] == 1

        # Check names
        assert set(info["data_providers"]["names"]) == {"data1", "data2"}
        assert info["audio_providers"]["names"] == ["audio"]
        assert info["image_providers"]["names"] == ["image"]
        assert info["sync_providers"]["names"] == ["sync"]

    def test_register_and_get_audio_provider(self):
        """Test registering and retrieving audio providers."""
        registry = ProviderRegistry()
        provider = MockAudioProvider()

        # Register provider
        registry.register_audio_provider("test", provider)

        # Retrieve provider
        retrieved = registry.get_audio_provider("test")
        assert retrieved is provider

        # List providers
        providers = registry.list_audio_providers()
        assert "test" in providers
        assert len(providers) == 1

    def test_get_nonexistent_audio_provider(self):
        """Test retrieving non-existent audio provider returns None."""
        registry = ProviderRegistry()

        result = registry.get_audio_provider("nonexistent")
        assert result is None

    def test_register_and_get_image_provider(self):
        """Test registering and retrieving image providers."""
        registry = ProviderRegistry()
        provider = MockImageProvider()

        # Register provider
        registry.register_image_provider("test", provider)

        # Retrieve provider
        retrieved = registry.get_image_provider("test")
        assert retrieved is provider

        # List providers
        providers = registry.list_image_providers()
        assert "test" in providers
        assert len(providers) == 1

    def test_get_nonexistent_image_provider(self):
        """Test retrieving non-existent image provider returns None."""
        registry = ProviderRegistry()

        result = registry.get_image_provider("nonexistent")
        assert result is None

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

        # Test unsupported audio provider - just check that the right exception is raised
        config_data = {
            "providers": {
                "audio": {"type": "unsupported"},
                "sync": {"type": "anki"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)
            with pytest.raises(
                ValueError, match="Unsupported audio provider type: unsupported"
            ):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()

        # Test unsupported image provider - just check that the right exception is raised
        config_data = {
            "providers": {
                "image": {"type": "unsupported"},
                "sync": {"type": "anki"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)
            with pytest.raises(
                ValueError, match="Unsupported image provider type: unsupported"
            ):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()

        # Test unsupported sync provider
        config_data = {
            "providers": {
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
                "audio": {"type": "forvo"},
                "image": {"type": "runware"},
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
                patch("src.providers.audio.forvo_provider.ForvoProvider") as mock_forvo,
                patch(
                    "src.providers.image.runware_provider.RunwareProvider"
                ) as mock_runware,
                patch("src.providers.sync.anki_provider.AnkiProvider") as mock_anki,
            ):
                registry = ProviderRegistry.from_config(config)

                # Verify providers were created
                assert registry.get_data_provider("default") is not None
                assert registry.get_audio_provider("default") is not None
                assert registry.get_image_provider("default") is not None
                assert registry.get_sync_provider("default") is not None

                # Verify correct types and initialization
                data_provider = registry.get_data_provider("default")
                assert data_provider.__class__.__name__ == "JSONDataProvider"
                mock_forvo.assert_called_once()
                mock_runware.assert_called_once()
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
                "audio": {"type": "forvo"},  # Will fail without API key
                "image": {"type": "runware"},  # Will fail without API key
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
                    "src.providers.audio.forvo_provider.ForvoProvider",
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
                patch("src.providers.audio.forvo_provider.ForvoProvider") as mock_forvo,
                patch(
                    "src.providers.image.runware_provider.RunwareProvider"
                ) as mock_runware,
                patch("src.providers.sync.anki_provider.AnkiProvider") as mock_anki,
            ):
                registry = ProviderRegistry.from_config(config)

                # Should NOT create providers when not configured
                assert registry.get_audio_provider("default") is None
                assert registry.get_image_provider("default") is None
                assert (
                    registry.get_sync_provider("default") is not None
                )  # Sync is always created

                # Should only create sync provider when missing providers config
                mock_forvo.assert_not_called()
                mock_runware.assert_not_called()
                mock_anki.assert_called_once()
        finally:
            Path(config_path).unlink()
