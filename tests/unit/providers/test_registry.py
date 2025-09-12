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

    def test_register_data_provider_with_config(self):
        """Test registering data provider with configuration (Phase 2 enhancement)."""
        registry = ProviderRegistry()
        provider = MockDataProvider()
        config = {"files": ["file1", "file2"], "read_only": True}

        # Register with config
        registry.register_data_provider("test", provider, config)

        # Verify provider is registered
        assert registry.get_data_provider("test") is provider

        # Verify config is stored (internal implementation detail)
        assert hasattr(registry, "_data_provider_configs")
        assert registry._data_provider_configs.get("test") == config

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

        # Test unsupported audio provider - using new format
        config_data = {
            "providers": {
                "audio": {
                    "unsupported_audio": {"type": "unsupported", "pipelines": ["*"]}
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
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

        # Test unsupported image provider - using new format
        config_data = {
            "providers": {
                "image": {
                    "unsupported_image": {"type": "unsupported", "pipelines": ["*"]}
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
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

        # Test unsupported sync provider - using new format
        config_data = {
            "providers": {
                "sync": {
                    "unsupported_sync": {"type": "unsupported", "pipelines": ["*"]}
                }
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
        """Test from_config method creates providers with valid new configuration format"""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from src.core.config import Config

        config_data = {
            "providers": {
                "data": {
                    "default": {"type": "json", "base_path": ".", "pipelines": ["*"]}
                },
                "audio": {"forvo": {"type": "forvo", "pipelines": ["vocabulary"]}},
                "image": {"runware": {"type": "runware", "pipelines": ["*"]}},
                "sync": {
                    "anki": {"type": "anki", "pipelines": ["vocabulary", "conjugation"]}
                },
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

                # Verify providers were created with correct names
                assert registry.get_data_provider("default") is not None
                assert registry.get_audio_provider("forvo") is not None
                assert registry.get_image_provider("runware") is not None
                assert registry.get_sync_provider("anki") is not None

                # Verify correct types and initialization
                data_provider = registry.get_data_provider("default")
                assert data_provider.__class__.__name__ == "JSONDataProvider"
                mock_forvo.assert_called_once()
                mock_runware.assert_called_once()
                mock_anki.assert_called_once()

                # Verify pipeline assignments were set correctly
                assert registry.get_pipeline_assignments("data", "default") == ["*"]
                assert registry.get_pipeline_assignments("audio", "forvo") == [
                    "vocabulary"
                ]
                assert registry.get_pipeline_assignments("image", "runware") == ["*"]
                assert registry.get_pipeline_assignments("sync", "anki") == [
                    "vocabulary",
                    "conjugation",
                ]
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
                "audio": {"forvo": {"type": "forvo", "pipelines": ["*"]}},
                "image": {"runware": {"type": "runware", "pipelines": ["*"]}},
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
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

        import pytest
        from src.core.config import Config

        # Config with no providers section should fail
        config_data = {"system": {"log_level": "info"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Should fail when no providers section exists
            with pytest.raises(ValueError, match="No providers configuration found"):
                ProviderRegistry.from_config(config)
        finally:
            Path(config_path).unlink()


class TestProviderRegistryPipelineAssignments:
    """Test cases for pipeline assignment functionality."""

    def test_set_pipeline_assignments(self):
        """Test setting pipeline assignments for providers."""
        registry = ProviderRegistry()

        # Test setting assignments for different provider types
        registry.set_pipeline_assignments("data", "test", ["vocabulary", "conjugation"])
        registry.set_pipeline_assignments("audio", "forvo", ["vocabulary"])
        registry.set_pipeline_assignments("image", "runware", ["*"])
        registry.set_pipeline_assignments("sync", "anki", ["vocabulary", "conjugation"])

        # Verify assignments are stored correctly
        assert registry.get_pipeline_assignments("data", "test") == [
            "vocabulary",
            "conjugation",
        ]
        assert registry.get_pipeline_assignments("audio", "forvo") == ["vocabulary"]
        assert registry.get_pipeline_assignments("image", "runware") == ["*"]
        assert registry.get_pipeline_assignments("sync", "anki") == [
            "vocabulary",
            "conjugation",
        ]

        # Test overwriting existing assignments
        registry.set_pipeline_assignments("data", "test", ["conjugation"])
        assert registry.get_pipeline_assignments("data", "test") == ["conjugation"]

    def test_get_pipeline_assignments(self):
        """Test retrieving pipeline assignments."""
        registry = ProviderRegistry()

        # Test getting assignments for assigned providers
        registry.set_pipeline_assignments("audio", "forvo", ["vocabulary"])
        assignments = registry.get_pipeline_assignments("audio", "forvo")
        assert assignments == ["vocabulary"]

        # Test getting assignments for unassigned providers (should return ["*"] for universal access)
        unassigned = registry.get_pipeline_assignments("audio", "unassigned")
        assert unassigned == ["*"]

    def test_get_providers_for_pipeline_with_assignments(self):
        """Test filtering providers by pipeline assignments."""
        registry = ProviderRegistry()

        # Register providers with specific pipeline assignments
        data_provider1 = MockDataProvider()
        data_provider2 = MockDataProvider()
        audio_provider = MockAudioProvider()
        image_provider = MockImageProvider()
        sync_provider = MockSyncProvider()

        registry.register_data_provider("vocab_data", data_provider1)
        registry.register_data_provider("conjugation_data", data_provider2)
        registry.register_audio_provider("forvo", audio_provider)
        registry.register_image_provider("runware", image_provider)
        registry.register_sync_provider("anki", sync_provider)

        # Set pipeline assignments
        registry.set_pipeline_assignments("data", "vocab_data", ["vocabulary"])
        registry.set_pipeline_assignments("data", "conjugation_data", ["conjugation"])
        registry.set_pipeline_assignments("audio", "forvo", ["vocabulary"])
        registry.set_pipeline_assignments("image", "runware", ["vocabulary"])
        registry.set_pipeline_assignments("sync", "anki", ["vocabulary", "conjugation"])

        # Test vocabulary pipeline gets assigned providers
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "vocab_data" in vocab_providers["data"]
        assert "conjugation_data" not in vocab_providers["data"]
        assert "forvo" in vocab_providers["audio"]
        assert "runware" in vocab_providers["image"]
        assert "anki" in vocab_providers["sync"]

        # Test conjugation pipeline gets assigned providers
        conjugation_providers = registry.get_providers_for_pipeline("conjugation")
        assert "vocab_data" not in conjugation_providers["data"]
        assert "conjugation_data" in conjugation_providers["data"]
        assert "forvo" not in conjugation_providers["audio"]
        assert "runware" not in conjugation_providers["image"]
        assert "anki" in conjugation_providers["sync"]

    def test_get_providers_for_pipeline_with_wildcard(self):
        """Test wildcard '*' assignments work for all pipelines."""
        registry = ProviderRegistry()

        # Register providers with wildcard assignment
        data_provider = MockDataProvider()
        audio_provider = MockAudioProvider()

        registry.register_data_provider("universal_data", data_provider)
        registry.register_audio_provider("universal_audio", audio_provider)

        # Set wildcard assignments
        registry.set_pipeline_assignments("data", "universal_data", ["*"])
        registry.set_pipeline_assignments("audio", "universal_audio", ["*"])

        # Test providers appear for any pipeline
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "universal_data" in vocab_providers["data"]
        assert "universal_audio" in vocab_providers["audio"]

        conjugation_providers = registry.get_providers_for_pipeline("conjugation")
        assert "universal_data" in conjugation_providers["data"]
        assert "universal_audio" in conjugation_providers["audio"]

        # Test with any random pipeline name
        random_providers = registry.get_providers_for_pipeline("random_pipeline")
        assert "universal_data" in random_providers["data"]
        assert "universal_audio" in random_providers["audio"]

    def test_get_providers_for_pipeline_no_assignments_defaults_universal(self):
        """Test providers without assignments default to universal access."""
        registry = ProviderRegistry()

        # Register providers without explicit assignments
        data_provider = MockDataProvider()
        audio_provider = MockAudioProvider()

        registry.register_data_provider("default_data", data_provider)
        registry.register_audio_provider("default_audio", audio_provider)

        # Test providers appear for all pipelines (backward compatibility)
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "default_data" in vocab_providers["data"]
        assert "default_audio" in vocab_providers["audio"]

        conjugation_providers = registry.get_providers_for_pipeline("conjugation")
        assert "default_data" in conjugation_providers["data"]
        assert "default_audio" in conjugation_providers["audio"]

    def test_from_config_with_pipeline_assignments(self):
        """Test loading config with new pipeline assignment format."""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from src.core.config import Config

        # Test config with named providers and pipeline assignments
        config_data = {
            "providers": {
                "data": {
                    "vocab_data": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["vocabulary"],
                    },
                    "conjugation_data": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["conjugation"],
                    },
                },
                "audio": {"forvo": {"type": "forvo", "pipelines": ["vocabulary"]}},
                "image": {"runware": {"type": "runware", "pipelines": ["*"]}},
                "sync": {
                    "anki": {"type": "anki", "pipelines": ["vocabulary", "conjugation"]}
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock the providers to avoid requiring actual API keys/Anki
            with (
                patch("src.providers.audio.forvo_provider.ForvoProvider"),
                patch("src.providers.image.runware_provider.RunwareProvider"),
                patch("src.providers.sync.anki_provider.AnkiProvider"),
            ):
                registry = ProviderRegistry.from_config(config)

                # Verify providers were created with correct names
                assert registry.get_data_provider("vocab_data") is not None
                assert registry.get_data_provider("conjugation_data") is not None
                assert registry.get_audio_provider("forvo") is not None
                assert registry.get_image_provider("runware") is not None
                assert registry.get_sync_provider("anki") is not None

                # Verify pipeline assignments were stored correctly
                assert registry.get_pipeline_assignments("data", "vocab_data") == [
                    "vocabulary"
                ]
                assert registry.get_pipeline_assignments(
                    "data", "conjugation_data"
                ) == ["conjugation"]
                assert registry.get_pipeline_assignments("audio", "forvo") == [
                    "vocabulary"
                ]
                assert registry.get_pipeline_assignments("image", "runware") == ["*"]
                assert registry.get_pipeline_assignments("sync", "anki") == [
                    "vocabulary",
                    "conjugation",
                ]

        finally:
            Path(config_path).unlink()

    def test_from_config_old_format_fails(self):
        """Test old config format fails with clear error message."""
        import json
        import tempfile
        from pathlib import Path

        import pytest
        from src.core.config import Config

        # Test config in old format without pipeline assignments
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

            # Should fail with clear error message for old format
            with pytest.raises(
                ValueError, match="Configuration uses old format.*named provider"
            ):
                ProviderRegistry.from_config(config)

        finally:
            Path(config_path).unlink()

    def test_from_config_missing_pipelines_field_fails(self):
        """Test config missing pipelines field fails."""
        import json
        import tempfile
        from pathlib import Path

        import pytest
        from src.core.config import Config

        # Test config with new structure but missing pipelines field
        config_data = {
            "providers": {
                "data": {
                    "vocab_data": {
                        "type": "json",
                        "base_path": ".",
                        # Missing pipelines field
                    }
                },
                "sync": {
                    "anki": {
                        "type": "anki",
                        "pipelines": ["*"],  # This one has pipelines
                    }
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Should fail with clear error message for missing pipelines field
            with pytest.raises(
                ValueError,
                match="Provider 'vocab_data'.*missing required 'pipelines' field",
            ):
                ProviderRegistry.from_config(config)

        finally:
            Path(config_path).unlink()
