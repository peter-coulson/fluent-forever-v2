"""Integration tests for Provider Registry functionality."""

import os

import pytest
from src.core.config import Config
from src.providers.registry import ProviderRegistry

from tests.fixtures.mock_implementations import MockDataProvider


class TestProviderRegistryIntegration:
    """Test provider registry configuration and setup integration."""

    def test_provider_registry_from_minimal_config(self, tmp_path):
        """Test loading providers from minimal configuration."""
        # Create minimal config
        config_path = tmp_path / "minimal_config.json"
        config_content = """{
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": "./test_data",
                        "pipelines": ["*"]
                    }
                },
                "sync": {
                    "default": {
                        "type": "anki",
                        "pipelines": ["*"]
                    }
                }
            }
        }"""
        config_path.write_text(config_content)

        # Load config and create registry
        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Verify data provider was created
        data_provider = registry.get_data_provider("default")
        assert data_provider is not None
        assert data_provider.__class__.__name__ == "JSONDataProvider"

        # Verify sync provider was created
        sync_provider = registry.get_sync_provider("default")
        assert sync_provider is not None
        assert sync_provider.__class__.__name__ == "AnkiProvider"

        # Verify optional providers not created
        assert registry.get_audio_provider("default") is None
        assert registry.get_image_provider("default") is None

    def test_provider_registry_from_full_config(self, tmp_path):
        """Test loading providers from full configuration."""
        # Create full config
        config_path = tmp_path / "full_config.json"
        config_content = """{
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": "./test_data",
                        "pipelines": ["*"]
                    }
                },
                "audio": {
                    "default": {
                        "type": "forvo",
                        "pipelines": ["*"]
                    }
                },
                "image": {
                    "default": {
                        "type": "runware",
                        "pipelines": ["*"]
                    }
                },
                "sync": {
                    "default": {
                        "type": "anki",
                        "pipelines": ["*"]
                    }
                }
            }
        }"""
        config_path.write_text(config_content)

        # Load config and create registry
        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Verify all providers were created
        assert registry.get_data_provider("default") is not None
        assert registry.get_audio_provider("default") is not None
        assert registry.get_image_provider("default") is not None
        assert registry.get_sync_provider("default") is not None

    def test_provider_registry_missing_config(self, tmp_path):
        """Test error handling for missing configuration file."""
        # Use non-existent config path
        non_existent_path = tmp_path / "missing_config.json"

        # Load config (should create empty config)
        config = Config.load(str(non_existent_path))

        # Should raise ValueError for missing providers configuration
        with pytest.raises(ValueError, match="No providers configuration found"):
            ProviderRegistry.from_config(config)

    def test_provider_registry_optional_providers(self, tmp_path):
        """Test that audio/image providers are optional, data/sync required."""
        # Create config with only data provider
        config_path = tmp_path / "data_only_config.json"
        config_content = """{
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": "./test_data",
                        "pipelines": ["*"]
                    }
                }
            }
        }"""
        config_path.write_text(config_content)

        # Load config and create registry
        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Data provider should be present
        assert registry.get_data_provider("default") is not None

        # Optional providers should be None
        assert registry.get_audio_provider("default") is None
        assert registry.get_image_provider("default") is None

        # Sync provider should be present (default)
        assert registry.get_sync_provider("default") is not None

    def test_provider_registry_invalid_provider_type(self, tmp_path):
        """Test failure on unsupported provider types."""
        # Create config with invalid audio provider type
        config_path = tmp_path / "invalid_config.json"
        config_content = """{
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": "./test_data",
                        "pipelines": ["*"]
                    }
                },
                "audio": {
                    "default": {
                        "type": "unsupported_audio_type",
                        "pipelines": ["*"]
                    }
                }
            }
        }"""
        config_path.write_text(config_content)

        # Load config and attempt to create registry
        config = Config.load(str(config_path))

        # Should raise ValueError for unsupported provider type
        with pytest.raises(ValueError, match="Unsupported audio provider type"):
            ProviderRegistry.from_config(config)

    def test_provider_registry_environment_substitution(self, tmp_path):
        """Test that environment variables are properly substituted."""
        # Set environment variable
        test_env_value = "test_environment_value"
        os.environ["TEST_DATA_PATH"] = test_env_value

        try:
            # Create config with environment variable
            config_path = tmp_path / "env_config.json"
            config_content = """{
                "providers": {
                    "data": {
                        "default": {
                            "type": "json",
                            "base_path": "${TEST_DATA_PATH}",
                            "pipelines": ["*"]
                        }
                    }
                }
            }"""
            config_path.write_text(config_content)

            # Load config and create registry
            config = Config.load(str(config_path))
            registry = ProviderRegistry.from_config(config)

            # Verify data provider was created with substituted path
            data_provider = registry.get_data_provider("default")
            assert data_provider is not None

            # Check if the base_path was substituted
            assert hasattr(data_provider, "base_path")
            assert str(data_provider.base_path) == test_env_value

        finally:
            # Clean up environment variable
            os.environ.pop("TEST_DATA_PATH", None)

    def test_provider_registry_manual_registration(self):
        """Test manual provider registration and retrieval."""
        registry = ProviderRegistry()

        # Create mock provider
        mock_provider = MockDataProvider()

        # Register provider
        registry.register_data_provider("test", mock_provider)

        # Verify registration
        retrieved_provider = registry.get_data_provider("test")
        assert retrieved_provider is mock_provider

        # Verify listing
        assert "test" in registry.list_data_providers()

    def test_provider_registry_info(self):
        """Test provider registry information retrieval."""
        registry = ProviderRegistry()

        # Add some mock providers
        registry.register_data_provider("data1", MockDataProvider())
        registry.register_data_provider("data2", MockDataProvider())

        # Get provider info
        info = registry.get_provider_info()

        assert info["data_providers"]["count"] == 2
        assert "data1" in info["data_providers"]["names"]
        assert "data2" in info["data_providers"]["names"]

        # Other provider types should be empty
        assert info["audio_providers"]["count"] == 0
        assert info["image_providers"]["count"] == 0
        assert info["sync_providers"]["count"] == 0

    def test_provider_registry_clear_all(self):
        """Test clearing all providers from registry."""
        registry = ProviderRegistry()

        # Add providers
        registry.register_data_provider("test", MockDataProvider())

        # Verify provider exists
        assert registry.get_data_provider("test") is not None

        # Clear all
        registry.clear_all()

        # Verify all providers cleared
        assert registry.get_data_provider("test") is None
        assert len(registry.list_data_providers()) == 0
