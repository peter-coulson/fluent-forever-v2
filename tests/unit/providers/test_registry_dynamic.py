"""Unit tests for dynamic provider registry functionality."""

from unittest.mock import Mock, patch

import pytest
from src.providers.registry import ProviderRegistry


class TestDynamicRegistry:
    """Test cases for dynamic provider loading functionality."""

    def test_media_provider_registry_structure(self):
        """Test MEDIA_PROVIDER_REGISTRY contains required provider mappings."""
        # This will fail initially since MEDIA_PROVIDER_REGISTRY doesn't exist yet
        from src.providers.registry import MEDIA_PROVIDER_REGISTRY

        # Test registry structure
        assert "audio" in MEDIA_PROVIDER_REGISTRY
        assert "image" in MEDIA_PROVIDER_REGISTRY
        assert "sync" in MEDIA_PROVIDER_REGISTRY

        # Test audio providers
        assert "forvo" in MEDIA_PROVIDER_REGISTRY["audio"]
        audio_mapping = MEDIA_PROVIDER_REGISTRY["audio"]["forvo"]
        assert len(audio_mapping) == 2
        assert audio_mapping[0] == "providers.audio.forvo_provider"
        assert audio_mapping[1] == "ForvoProvider"

        # Test image providers
        assert "openai" in MEDIA_PROVIDER_REGISTRY["image"]
        assert "runware" in MEDIA_PROVIDER_REGISTRY["image"]
        openai_mapping = MEDIA_PROVIDER_REGISTRY["image"]["openai"]
        assert openai_mapping == ("providers.image.openai_provider", "OpenAIProvider")
        runware_mapping = MEDIA_PROVIDER_REGISTRY["image"]["runware"]
        assert runware_mapping == (
            "providers.image.runware_provider",
            "RunwareProvider",
        )

        # Test sync providers
        assert "anki" in MEDIA_PROVIDER_REGISTRY["sync"]
        sync_mapping = MEDIA_PROVIDER_REGISTRY["sync"]["anki"]
        assert sync_mapping == ("providers.sync.anki_provider", "AnkiProvider")

    def test_create_media_provider_valid_types(self):
        """Test _create_media_provider with valid provider types."""
        registry = ProviderRegistry()

        # Mock the provider classes
        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_provider_class = Mock()
            mock_provider_instance = Mock()

            mock_module.ForvoProvider = mock_provider_class
            mock_provider_class.return_value = mock_provider_instance
            mock_import.return_value = mock_module

            config = {"api_key": "test", "type": "forvo", "pipelines": ["*"]}

            # This will fail initially since _create_media_provider doesn't exist yet
            result = registry._create_media_provider("audio", "forvo", config)

            # Verify dynamic import was called correctly
            mock_import.assert_called_once_with("src.providers.audio.forvo_provider")

            # Verify provider class was instantiated with filtered config
            expected_config = {"api_key": "test"}  # type and pipelines excluded
            mock_provider_class.assert_called_once_with(expected_config)

            assert result == mock_provider_instance

    def test_create_media_provider_invalid_provider_type(self):
        """Test _create_media_provider raises ValueError for invalid provider type."""
        registry = ProviderRegistry()

        config = {"api_key": "test", "type": "invalid", "pipelines": ["*"]}

        # This will fail initially since _create_media_provider doesn't exist yet
        with pytest.raises(ValueError, match="Unknown provider type: invalid"):
            registry._create_media_provider("invalid", "forvo", config)

    def test_create_media_provider_invalid_provider_name(self):
        """Test _create_media_provider raises ValueError for invalid provider name."""
        registry = ProviderRegistry()

        config = {"api_key": "test", "type": "invalid", "pipelines": ["*"]}

        # This will fail initially since _create_media_provider doesn't exist yet
        with pytest.raises(ValueError, match="Unknown audio provider: invalid"):
            registry._create_media_provider("audio", "invalid", config)

    def test_create_media_provider_import_error(self):
        """Test _create_media_provider handles import errors properly."""
        registry = ProviderRegistry()

        with patch(
            "importlib.import_module", side_effect=ImportError("Module not found")
        ):
            config = {"api_key": "test", "type": "forvo", "pipelines": ["*"]}

            # This will fail initially since _create_media_provider doesn't exist yet
            with pytest.raises(ImportError, match="Module not found"):
                registry._create_media_provider("audio", "forvo", config)

    def test_create_media_provider_config_filtering(self):
        """Test _create_media_provider excludes registry metadata from config."""
        registry = ProviderRegistry()

        with patch("importlib.import_module") as mock_import:
            mock_module = Mock()
            mock_provider_class = Mock()
            mock_provider_instance = Mock()

            mock_module.ForvoProvider = mock_provider_class
            mock_provider_class.return_value = mock_provider_instance
            mock_import.return_value = mock_module

            config = {
                "api_key": "test_key",
                "timeout": 30,
                "type": "forvo",  # Should be excluded
                "pipelines": ["vocabulary"],  # Should be excluded
                "custom_setting": "value",
            }

            # This will fail initially since _create_media_provider doesn't exist yet
            registry._create_media_provider("audio", "forvo", config)

            # Verify only relevant config passed to provider
            expected_config = {
                "api_key": "test_key",
                "timeout": 30,
                "custom_setting": "value",
            }
            mock_provider_class.assert_called_once_with(expected_config)

    def test_extract_provider_configs(self):
        """Test _extract_provider_configs organizes config by provider type."""
        registry = ProviderRegistry()
        registry.config = {
            "providers": {
                "audio": {
                    "forvo": {"type": "forvo", "api_key": "test", "pipelines": ["*"]}
                },
                "image": {
                    "openai": {
                        "type": "openai",
                        "api_key": "test3",
                        "pipelines": ["*"],
                    },
                },
                "sync": {"anki": {"type": "anki", "deck": "test", "pipelines": ["*"]}},
                "data": {
                    "json": {"type": "json", "base_path": ".", "pipelines": ["*"]}
                },
            }
        }

        # This will fail initially since _extract_provider_configs doesn't exist yet
        result = registry._extract_provider_configs()

        # Verify structure
        assert "audio" in result
        assert "image" in result
        assert "sync" in result

        # Verify audio configs
        assert "forvo" in result["audio"]
        assert result["audio"]["forvo"]["api_key"] == "test"

        # Verify image configs
        assert "openai" in result["image"]
        assert result["image"]["openai"]["api_key"] == "test3"

        # Verify sync configs
        assert "anki" in result["sync"]
        assert result["sync"]["anki"]["deck"] == "test"

    def test_register_provider_by_type_audio(self):
        """Test _register_provider_by_type registers audio provider correctly."""
        registry = ProviderRegistry()
        mock_provider = Mock()

        # This will fail initially since _register_provider_by_type doesn't exist yet
        registry._register_provider_by_type("audio", "test_provider", mock_provider)

        # Verify provider was registered
        assert registry.get_audio_provider("test_provider") == mock_provider

    def test_register_provider_by_type_image(self):
        """Test _register_provider_by_type registers image provider correctly."""
        registry = ProviderRegistry()
        mock_provider = Mock()

        # This will fail initially since _register_provider_by_type doesn't exist yet
        registry._register_provider_by_type("image", "test_provider", mock_provider)

        # Verify provider was registered
        assert registry.get_image_provider("test_provider") == mock_provider

    def test_register_provider_by_type_sync(self):
        """Test _register_provider_by_type registers sync provider correctly."""
        registry = ProviderRegistry()
        mock_provider = Mock()

        # This will fail initially since _register_provider_by_type doesn't exist yet
        registry._register_provider_by_type("sync", "test_provider", mock_provider)

        # Verify provider was registered
        assert registry.get_sync_provider("test_provider") == mock_provider

    def test_register_provider_by_type_invalid(self):
        """Test _register_provider_by_type raises ValueError for invalid type."""
        registry = ProviderRegistry()
        mock_provider = Mock()

        # This will fail initially since _register_provider_by_type doesn't exist yet
        with pytest.raises(
            ValueError, match="Unknown provider type for registration: invalid"
        ):
            registry._register_provider_by_type(
                "invalid", "test_provider", mock_provider
            )

    def test_setup_media_providers_success(self):
        """Test _setup_media_providers creates all configured providers."""
        registry = ProviderRegistry()
        registry.config = {
            "providers": {
                "audio": {
                    "forvo": {"type": "audio", "api_key": "test1", "pipelines": ["*"]}
                },
                "image": {
                    "openai": {
                        "type": "image",
                        "api_key": "test2",
                        "pipelines": ["vocab"],
                    }
                },
                "sync": {"anki": {"type": "sync", "deck": "test", "pipelines": ["*"]}},
            }
        }

        # Mock all the methods that _setup_media_providers should call
        mock_audio_provider = Mock()
        mock_image_provider = Mock()
        mock_sync_provider = Mock()

        with (
            patch.object(registry, "_extract_provider_configs") as mock_extract,
            patch.object(registry, "_create_media_provider") as mock_create,
            patch.object(registry, "_register_provider_by_type") as mock_register,
        ):
            mock_extract.return_value = {
                "audio": {"forvo": {"api_key": "test1", "pipelines": ["*"]}},
                "image": {"openai": {"api_key": "test2", "pipelines": ["vocab"]}},
                "sync": {"anki": {"deck": "test", "pipelines": ["*"]}},
            }

            mock_create.side_effect = [
                mock_audio_provider,
                mock_image_provider,
                mock_sync_provider,
            ]

            # This will fail initially since _setup_media_providers doesn't exist yet
            registry._setup_media_providers()

            # Verify extract was called
            mock_extract.assert_called_once()

            # Verify create was called for each provider
            assert mock_create.call_count == 3
            mock_create.assert_any_call(
                "audio", "forvo", {"api_key": "test1", "pipelines": ["*"]}
            )
            mock_create.assert_any_call(
                "image", "openai", {"api_key": "test2", "pipelines": ["vocab"]}
            )
            mock_create.assert_any_call(
                "sync", "anki", {"deck": "test", "pipelines": ["*"]}
            )

            # Verify register was called for each provider
            assert mock_register.call_count == 3
            mock_register.assert_any_call("audio", "forvo", mock_audio_provider)
            mock_register.assert_any_call("image", "openai", mock_image_provider)
            mock_register.assert_any_call("sync", "anki", mock_sync_provider)

    def test_setup_media_providers_propagates_provider_creation_failures(self):
        """Test _setup_media_providers propagates provider creation failures (fail-fast behavior)."""
        registry = ProviderRegistry()

        with (
            patch.object(registry, "_extract_provider_configs") as mock_extract,
            patch.object(registry, "_create_media_provider") as mock_create,
            patch.object(registry, "_register_provider_by_type") as mock_register,
        ):
            mock_extract.return_value = {
                "audio": {"forvo": {"api_key": "test1", "pipelines": ["*"]}},
                "image": {},
                "sync": {},
            }

            # Provider creation fails
            mock_create.side_effect = Exception("API key invalid")

            # Should propagate the exception (fail-fast behavior)
            with pytest.raises(Exception, match="API key invalid"):
                registry._setup_media_providers()

            # Verify create was called once before failure
            assert mock_create.call_count == 1

            # Verify register was not called due to failure
            assert mock_register.call_count == 0

    def test_from_config_uses_unified_setup(self):
        """Test from_config uses new unified setup method instead of hardcoded logic."""
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        from src.core.config import Config

        config_data = {
            "providers": {
                "audio": {"forvo": {"type": "forvo", "pipelines": ["*"]}},
                "image": {"openai": {"type": "openai", "pipelines": ["*"]}},
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock _setup_media_providers to verify it gets called instead of hardcoded logic
            with patch.object(ProviderRegistry, "_setup_media_providers") as mock_setup:
                ProviderRegistry.from_config(config)

                # This will fail initially since from_config doesn't use _setup_media_providers yet
                mock_setup.assert_called_once()

        finally:
            Path(config_path).unlink()
