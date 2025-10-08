"""Comprehensive unit tests for ProviderRegistry.

High-Risk Component Testing:
- Dynamic loading accuracy
- Configuration injection validation
- Access control enforcement
- Provider instantiation error handling
- File conflict detection
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
from src.core.config import Config
from src.providers.base.data_provider import DataProvider
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from src.providers.base.sync_provider import SyncProvider
from src.providers.registry import (
    ProviderRegistry,
    get_provider_registry,
)


class MockDataProvider(DataProvider):
    """Mock implementation of DataProvider for unit tests."""

    def __init__(
        self,
        base_path: Path,
        read_only: bool = False,
        managed_files: list[str] | None = None,
    ):
        super().__init__()
        self.base_path = base_path
        self.read_only = read_only
        self._managed_files = managed_files or []
        self._data: dict[str, dict[str, Any]] = {}

    def _load_data_impl(self, identifier: str) -> dict[str, Any]:
        return self._data.get(identifier, {"test": "data"})

    def _save_data_impl(self, identifier: str, data: dict[str, Any]) -> bool:
        self._data[identifier] = data
        return True

    def exists(self, identifier: str) -> bool:
        return identifier in self._data

    def list_identifiers(self) -> list[str]:
        return list(self._data.keys())


class MockAudioProvider(MediaProvider):
    """Mock implementation of MediaProvider for audio."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.api_calls: list[dict[str, Any]] = []

    @property
    def supported_types(self) -> list[str]:
        return ["audio"]

    def validate_config(self, config: dict[str, Any]) -> None:
        # Allow empty config for testing
        pass

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        self.api_calls.append({"request": request})
        return MediaResult(
            success=True,
            file_path=request.output_path,
            metadata={"provider": "test_audio"},
        )

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": len(requests) * 0.01}


class MockImageProvider(MediaProvider):
    """Mock implementation of MediaProvider for images."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.api_calls: list[dict[str, Any]] = []

    @property
    def supported_types(self) -> list[str]:
        return ["image"]

    def validate_config(self, config: dict[str, Any]) -> None:
        # Allow empty config for testing
        pass

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        self.api_calls.append({"request": request})
        return MediaResult(
            success=True,
            file_path=request.output_path,
            metadata={"provider": "test_image"},
        )

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        return {"total_cost": len(requests) * 0.05}


class MockSyncProvider(SyncProvider):
    """Mock implementation of SyncProvider."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__()
        self.config = config or {}
        self.sync_calls: list[dict[str, Any]] = []

    def _test_connection_impl(self) -> bool:
        return True

    def sync_templates(self, note_type: str, templates: list[dict]) -> Any:
        from src.providers.base.sync_provider import SyncResult

        self.sync_calls.append(
            {"method": "sync_templates", "note_type": note_type, "templates": templates}
        )
        return SyncResult(success=True, processed_count=len(templates), metadata={})

    def sync_media(self, media_files: list[Path]) -> Any:
        from src.providers.base.sync_provider import SyncResult

        self.sync_calls.append({"method": "sync_media", "media_files": media_files})
        return SyncResult(success=True, processed_count=len(media_files), metadata={})

    def _sync_cards_impl(self, cards: list[dict]) -> Any:
        from src.providers.base.sync_provider import SyncResult

        self.sync_calls.append({"method": "sync_cards", "cards": cards})
        return SyncResult(success=True, processed_count=len(cards), metadata={})

    def list_existing(self, note_type: str) -> list[dict]:
        self.sync_calls.append({"method": "list_existing", "note_type": note_type})
        return []


class TestProviderRegistry:
    """Test ProviderRegistry dynamic loading and access control."""

    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test."""
        registry = ProviderRegistry()
        registry.clear_all()
        return registry

    @pytest.fixture
    def mock_data_provider(self):
        """Create mock data provider."""
        return MockDataProvider(Path("/test"), read_only=False)

    @pytest.fixture
    def mock_audio_provider(self):
        """Create mock audio provider."""
        return MockAudioProvider({"api_key": "test_key"})

    @pytest.fixture
    def mock_image_provider(self):
        """Create mock image provider."""
        return MockImageProvider({"api_key": "test_key"})

    @pytest.fixture
    def mock_sync_provider(self):
        """Create mock sync provider."""
        return MockSyncProvider({"url": "http://localhost:8765"})

    def test_singleton_instance_access(self):
        """Test that get_provider_registry returns singleton instance."""
        registry1 = get_provider_registry()
        registry2 = get_provider_registry()

        assert registry1 is registry2
        assert isinstance(registry1, ProviderRegistry)

    def test_register_data_provider_success(self, registry, mock_data_provider):
        """Test successful data provider registration."""
        config = {"files": ["test.json"], "read_only": False}

        registry.register_data_provider("test_provider", mock_data_provider, config)

        assert "test_provider" in registry.list_data_providers()
        assert registry.get_data_provider("test_provider") is mock_data_provider

    def test_register_audio_provider_success(self, registry, mock_audio_provider):
        """Test successful audio provider registration."""
        registry.register_audio_provider("test_audio", mock_audio_provider)

        assert "test_audio" in registry.list_audio_providers()
        assert registry.get_audio_provider("test_audio") is mock_audio_provider

    def test_register_image_provider_success(self, registry, mock_image_provider):
        """Test successful image provider registration."""
        registry.register_image_provider("test_image", mock_image_provider)

        assert "test_image" in registry.list_image_providers()
        assert registry.get_image_provider("test_image") is mock_image_provider

    def test_register_sync_provider_success(self, registry, mock_sync_provider):
        """Test successful sync provider registration."""
        registry.register_sync_provider("test_sync", mock_sync_provider)

        assert "test_sync" in registry.list_sync_providers()
        assert registry.get_sync_provider("test_sync") is mock_sync_provider

    def test_register_duplicate_provider_name_error(self, registry, mock_data_provider):
        """Test that duplicate provider names are handled correctly."""
        # Current implementation allows overwriting - test this behavior
        provider1 = MockDataProvider(Path("/test1"))
        provider2 = MockDataProvider(Path("/test2"))

        registry.register_data_provider("duplicate_name", provider1)
        registry.register_data_provider("duplicate_name", provider2)

        # Second registration overwrites first
        assert registry.get_data_provider("duplicate_name") is provider2

    def test_register_invalid_provider_type_error(self, registry):
        """Test handling of invalid provider types in registration."""
        # Test _register_provider_by_type with invalid type
        mock_provider = MagicMock()

        with pytest.raises(ValueError, match="Unknown provider type for registration"):
            registry._register_provider_by_type("invalid_type", "test", mock_provider)

    def test_get_providers_for_pipeline_authorized_only(self, registry):
        """Test that get_providers_for_pipeline returns only authorized providers."""
        # Register providers with specific pipeline assignments
        audio_provider = MockAudioProvider()
        image_provider = MockImageProvider()

        registry.register_audio_provider("vocab_audio", audio_provider)
        registry.register_image_provider("vocab_image", image_provider)
        registry.register_image_provider("conj_image", image_provider)

        # Set pipeline assignments
        registry.set_pipeline_assignments("audio", "vocab_audio", ["vocabulary"])
        registry.set_pipeline_assignments("image", "vocab_image", ["vocabulary"])
        registry.set_pipeline_assignments("image", "conj_image", ["conjugation"])

        # Test vocabulary pipeline access
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "vocab_audio" in vocab_providers["audio"]
        assert "vocab_image" in vocab_providers["image"]
        assert "conj_image" not in vocab_providers["image"]

        # Test conjugation pipeline access
        conj_providers = registry.get_providers_for_pipeline("conjugation")
        assert "vocab_audio" not in conj_providers["audio"]
        assert "vocab_image" not in conj_providers["image"]
        assert "conj_image" in conj_providers["image"]

    def test_get_providers_for_pipeline_empty_result(self, registry):
        """Test that get_providers_for_pipeline returns empty dict when no providers."""
        providers = registry.get_providers_for_pipeline("nonexistent_pipeline")

        assert providers["data"] == {}
        assert providers["audio"] == {}
        assert providers["image"] == {}
        assert providers["sync"] == {}

    def test_get_providers_for_pipeline_nonexistent_pipeline(self, registry):
        """Test behavior with nonexistent pipeline name."""
        # Register provider with specific pipeline assignment
        audio_provider = MockAudioProvider()
        registry.register_audio_provider("specific_audio", audio_provider)
        registry.set_pipeline_assignments("audio", "specific_audio", ["vocabulary"])

        # Request providers for nonexistent pipeline
        providers = registry.get_providers_for_pipeline("nonexistent")
        assert "specific_audio" not in providers["audio"]

    def test_create_media_provider_success(self, registry):
        """Test successful media provider creation via dynamic loading."""
        # Mock the import system
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()

            mock_import.return_value = mock_module
            mock_module.ForvoProvider = mock_provider_class
            mock_provider_class.return_value = mock_provider_instance

            config = {
                "type": "forvo",
                "api_key": "test_key",
                "pipelines": ["vocabulary"],
            }

            provider = registry._create_media_provider("audio", "forvo", config)

            # Verify dynamic import was called correctly
            mock_import.assert_called_with("src.providers.audio.forvo_provider")
            # Verify provider was instantiated with config
            assert provider is mock_provider_instance

    def test_create_media_provider_invalid_type(self, registry):
        """Test media provider creation with invalid provider type."""
        config = {"type": "invalid_provider", "pipelines": ["test"]}

        with pytest.raises(
            ValueError, match="Unknown audio provider: invalid_provider"
        ):
            registry._create_media_provider("audio", "invalid_provider", config)

    def test_create_media_provider_missing_config(self, registry):
        """Test media provider creation with missing required configuration."""
        with pytest.raises(ValueError, match="Unknown provider type: invalid_type"):
            registry._create_media_provider("invalid_type", "test", {})

    def test_configuration_injection_validation(self, registry):
        """Test that configuration injection works correctly."""
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()

            mock_import.return_value = mock_module
            mock_module.ForvoProvider = mock_provider_class
            mock_provider_class.return_value = mock_provider_instance

            config = {
                "type": "forvo",
                "api_key": "test_key",
                "base_url": "https://api.forvo.com",
                "pipelines": ["vocabulary"],
            }

            registry._create_media_provider("audio", "forvo", config)

            # Verify provider was called with extracted config (no metadata fields)
            expected_config = {
                "api_key": "test_key",
                "base_url": "https://api.forvo.com",
            }
            mock_provider_class.assert_called_with(expected_config)

    def test_provider_access_control_enforcement(self, registry):
        """Test that access control is properly enforced."""
        # Set up providers with different access levels
        audio_provider = MockAudioProvider()
        image_provider = MockImageProvider()
        sync_provider = MockSyncProvider()

        registry.register_audio_provider("restricted_audio", audio_provider)
        registry.register_image_provider("universal_image", image_provider)
        registry.register_sync_provider("specific_sync", sync_provider)

        # Set different access control levels
        registry.set_pipeline_assignments("audio", "restricted_audio", ["vocabulary"])
        registry.set_pipeline_assignments(
            "image", "universal_image", ["*"]
        )  # Universal access
        registry.set_pipeline_assignments("sync", "specific_sync", ["conjugation"])

        # Test vocabulary pipeline access
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "restricted_audio" in vocab_providers["audio"]
        assert "universal_image" in vocab_providers["image"]
        assert "specific_sync" not in vocab_providers["sync"]

        # Test conjugation pipeline access
        conj_providers = registry.get_providers_for_pipeline("conjugation")
        assert "restricted_audio" not in conj_providers["audio"]
        assert "universal_image" in conj_providers["image"]
        assert "specific_sync" in conj_providers["sync"]

    def test_file_conflict_validation_success(self, registry):
        """Test file conflict validation with no conflicts."""
        provider1 = MockDataProvider(Path("/test"))
        provider2 = MockDataProvider(Path("/test"))

        config1 = {"files": ["file1.json", "file2.json"]}
        config2 = {"files": ["file3.json", "file4.json"]}

        # Should not raise exception
        registry.register_data_provider("provider1", provider1, config1)
        registry.register_data_provider("provider2", provider2, config2)

    def test_file_conflict_validation_error(self, registry):
        """Test file conflict validation detects conflicts."""
        provider1 = MockDataProvider(Path("/test"))
        provider2 = MockDataProvider(Path("/test"))

        config1 = {"files": ["file1.json", "shared.json"]}

        registry.register_data_provider("provider1", provider1, config1)

        config2 = {"files": ["file2.json", "shared.json"]}  # Conflict!

        with pytest.raises(ValueError, match="File conflicts detected"):
            registry.register_data_provider("provider2", provider2, config2)

    def test_provider_instantiation_error_handling(self, registry):
        """Test handling of provider instantiation errors."""
        with patch("importlib.import_module") as mock_import:
            # Mock import failure
            mock_import.side_effect = ImportError("Module not found")

            config = {"type": "forvo", "pipelines": ["vocabulary"]}

            with pytest.raises(ImportError):
                registry._create_media_provider("audio", "forvo", config)

    def test_configuration_processing_environment_vars(self, registry):
        """Test that configuration processing handles environment variables."""
        # This tests the integration with Config class environment substitution
        config_data = {
            "providers": {
                "audio": {
                    "forvo": {
                        "type": "forvo",
                        "api_key": "${FORVO_API_KEY:default_key}",
                        "pipelines": ["vocabulary"],
                    }
                }
            }
        }

        with (
            patch.dict("os.environ", {"FORVO_API_KEY": "env_key_value"}),
            patch("builtins.open", mock_open(read_data='{"test": "data"}')),
            patch("json.load", return_value=config_data),
        ):
            config = Config()
            ProviderRegistry.from_config(config)

            # Environment substitution should have occurred in Config
            assert config.get("providers.audio.forvo.api_key") == "env_key_value"

    def test_registry_state_isolation_between_tests(self):
        """Test that registry state is properly isolated between tests."""
        # Create two separate registries
        registry1 = ProviderRegistry()
        registry2 = ProviderRegistry()

        # Clear both to ensure clean state
        registry1.clear_all()
        registry2.clear_all()

        # Modify first registry
        provider1 = MockAudioProvider()
        registry1.register_audio_provider("test1", provider1)

        # Verify second registry is not affected
        assert "test1" not in registry2.list_audio_providers()
        assert registry2.get_audio_provider("test1") is None

    def test_provider_info_aggregation(self, registry):
        """Test get_provider_info returns correct aggregated information."""
        # Register various providers
        registry.register_data_provider("data1", MockDataProvider(Path("/test")))
        registry.register_audio_provider("audio1", MockAudioProvider())
        registry.register_audio_provider("audio2", MockAudioProvider())
        registry.register_image_provider("image1", MockImageProvider())
        registry.register_sync_provider("sync1", MockSyncProvider())

        info = registry.get_provider_info()

        assert info["data_providers"]["count"] == 1
        assert "data1" in info["data_providers"]["names"]
        assert info["audio_providers"]["count"] == 2
        assert "audio1" in info["audio_providers"]["names"]
        assert "audio2" in info["audio_providers"]["names"]
        assert info["image_providers"]["count"] == 1
        assert "image1" in info["image_providers"]["names"]
        assert info["sync_providers"]["count"] == 1
        assert "sync1" in info["sync_providers"]["names"]

    def test_pipeline_assignment_management(self, registry):
        """Test pipeline assignment setting and getting."""
        # Test default assignments (universal access)
        assignments = registry.get_pipeline_assignments("audio", "test_provider")
        assert assignments == ["*"]

        # Test setting specific assignments
        registry.set_pipeline_assignments(
            "audio", "test_provider", ["vocabulary", "conjugation"]
        )
        assignments = registry.get_pipeline_assignments("audio", "test_provider")
        assert assignments == ["vocabulary", "conjugation"]

        # Test overwriting assignments
        registry.set_pipeline_assignments("audio", "test_provider", ["vocabulary"])
        assignments = registry.get_pipeline_assignments("audio", "test_provider")
        assert assignments == ["vocabulary"]

    @patch("src.providers.registry.get_logger")
    def test_from_config_initialization(self, mock_get_logger):
        """Test ProviderRegistry.from_config class method."""
        config_data = {
            "providers": {
                "data": {
                    "main_data": {
                        "type": "json",
                        "base_path": "data",
                        "pipelines": ["vocabulary"],
                        "read_only": False,
                    }
                },
                "audio": {
                    "forvo": {
                        "type": "forvo",
                        "api_key": "test_key",
                        "pipelines": ["vocabulary"],
                    }
                },
            }
        }

        with (
            patch("builtins.open", mock_open()),
            patch("json.load", return_value=config_data),
        ):
            config = Config()

            with patch.object(
                ProviderRegistry, "_create_media_provider"
            ) as mock_create:
                mock_audio_provider = MockAudioProvider()
                mock_create.return_value = mock_audio_provider

                registry = ProviderRegistry.from_config(config)

                # Verify data provider was registered
                assert "main_data" in registry.list_data_providers()

                # Verify media provider creation was attempted
                mock_create.assert_called()

    def test_unsupported_provider_type_error(self, registry):
        """Test error handling for unsupported provider types."""
        config_data = {
            "providers": {
                "audio": {
                    "unsupported": {
                        "type": "unsupported_type",
                        "pipelines": ["vocabulary"],
                    }
                }
            }
        }

        registry.config = config_data

        with pytest.raises(ValueError, match="Unsupported audio provider type"):
            registry._extract_provider_configs()

    def test_missing_pipelines_field_error(self, registry):
        """Test error when provider configuration is missing pipelines field."""
        config_data = {
            "providers": {
                "audio": {
                    "forvo": {
                        "type": "forvo",
                        "api_key": "test_key",
                        # Missing 'pipelines' field
                    }
                }
            }
        }

        with (
            patch("builtins.open", mock_open()),
            patch("json.load", return_value=config_data),
        ):
            config = Config()

            with pytest.raises(ValueError, match="missing required 'pipelines' field"):
                ProviderRegistry.from_config(config)

    def test_provider_creation_fallback_behavior(self, registry):
        """Test fallback behavior when provider constructor fails with config."""
        with patch("importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_provider_class = MagicMock()

            mock_import.return_value = mock_module
            mock_module.ForvoProvider = mock_provider_class

            # First call (with config) raises TypeError, second call (no args) succeeds
            mock_provider_instance = MagicMock()
            mock_provider_class.side_effect = [
                TypeError("No config support"),
                mock_provider_instance,
            ]

            config = {
                "type": "forvo",
                "api_key": "test_key",
                "pipelines": ["vocabulary"],
            }

            provider = registry._create_media_provider("audio", "forvo", config)

            # Verify both calls were made
            assert mock_provider_class.call_count == 2
            # First call with config, second call without args
            mock_provider_class.assert_any_call({"api_key": "test_key"})
            mock_provider_class.assert_any_call()
            assert provider is mock_provider_instance

    def test_clear_all_functionality(self, registry):
        """Test that clear_all removes all providers and assignments."""
        # Register providers of all types
        registry.register_data_provider("data1", MockDataProvider(Path("/test")))
        registry.register_audio_provider("audio1", MockAudioProvider())
        registry.register_image_provider("image1", MockImageProvider())
        registry.register_sync_provider("sync1", MockSyncProvider())
        registry.set_pipeline_assignments("audio", "audio1", ["vocabulary"])

        # Verify providers are registered
        assert len(registry.list_data_providers()) > 0
        assert len(registry.list_audio_providers()) > 0
        assert len(registry.list_image_providers()) > 0
        assert len(registry.list_sync_providers()) > 0

        # Clear all
        registry.clear_all()

        # Verify all are cleared
        assert len(registry.list_data_providers()) == 0
        assert len(registry.list_audio_providers()) == 0
        assert len(registry.list_image_providers()) == 0
        assert len(registry.list_sync_providers()) == 0
        assert registry.get_pipeline_assignments("audio", "audio1") == [
            "*"
        ]  # Reset to default
