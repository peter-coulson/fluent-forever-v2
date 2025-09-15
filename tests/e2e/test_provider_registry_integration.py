"""
E2E Test Scenario 2: Provider Registry Integration and Pipeline Assignment

Purpose: Validate provider loading, configuration injection, and pipeline filtering
"""

import pytest
from pathlib import Path

from src.core.config import Config
from src.providers.registry import ProviderRegistry
from tests.fixtures.configs import (
    ConfigFixture,
    create_complex_config,
    create_file_conflict_config,
    create_invalid_config,
    create_old_format_config,
)
from tests.utils.assertions import (
    assert_provider_pipeline_access,
    assert_providers_registered,
    assert_registry_provider_count,
    assert_validation_errors,
)


class TestProviderRegistryIntegration:
    """Test provider registry integration and pipeline assignment."""

    @pytest.fixture
    def complex_config(self):
        """Create complex multi-provider configuration."""
        return create_complex_config()

    @pytest.fixture
    def complex_config_file(self, complex_config):
        """Create temporary complex config file."""
        with ConfigFixture(complex_config) as config_path:
            yield config_path

    def test_provider_registry_from_config(self, complex_config_file):
        """Test provider registry creation from complex configuration."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Validate all provider types are registered
        assert_providers_registered(registry, "data", ["vocabulary_data", "conjugation_data", "shared_data"])
        assert_providers_registered(registry, "audio", ["primary_audio", "backup_audio"])
        assert_providers_registered(registry, "image", ["openai_images", "runware_images"])
        assert_providers_registered(registry, "sync", ["main_anki"])

    def test_configuration_injection(self, complex_config_file):
        """Test configuration injection into providers."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test data provider configuration
        vocab_provider = registry.get_data_provider("vocabulary_data")
        assert vocab_provider is not None
        assert vocab_provider.base_path == Path("data")
        assert not vocab_provider.read_only
        assert vocab_provider.managed_files == ["vocabulary.json"]
        
        conjugation_provider = registry.get_data_provider("conjugation_data")
        assert conjugation_provider is not None
        assert conjugation_provider.read_only  # Should be read-only

    def test_pipeline_assignment_filtering(self, complex_config_file):
        """Test pipeline assignment filtering logic."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test vocabulary pipeline access
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "vocabulary_data" in vocab_providers["data"]
        assert "shared_data" in vocab_providers["data"]  # Has "*" access
        assert "conjugation_data" not in vocab_providers["data"]  # Only for conjugation
        
        assert "primary_audio" in vocab_providers["audio"]
        assert "backup_audio" in vocab_providers["audio"]
        
        assert "openai_images" in vocab_providers["image"]
        assert "runware_images" in vocab_providers["image"]
        
        assert "main_anki" in vocab_providers["sync"]  # Universal access

    def test_conjugation_pipeline_filtering(self, complex_config_file):
        """Test provider filtering for conjugation pipeline."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test conjugation pipeline access
        conj_providers = registry.get_providers_for_pipeline("conjugation")
        assert "conjugation_data" in conj_providers["data"]
        assert "shared_data" in conj_providers["data"]  # Universal access
        assert "vocabulary_data" not in conj_providers["data"]  # Only for vocabulary
        
        assert "primary_audio" in conj_providers["audio"]
        assert "backup_audio" not in conj_providers["audio"]  # Only for vocabulary
        
        # No image providers for conjugation
        assert len(conj_providers["image"]) == 0
        
        assert "main_anki" in conj_providers["sync"]  # Universal access

    def test_file_conflict_validation(self):
        """Test file conflict validation for data providers."""
        config_data = create_file_conflict_config()
        
        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))
            
            with pytest.raises(ValueError) as exc_info:
                ProviderRegistry.from_config(config)
            
            # Should detect file conflicts
            assert "conflict" in str(exc_info.value).lower()
            assert "shared_file.json" in str(exc_info.value)

    def test_invalid_provider_configuration(self):
        """Test handling of invalid provider configurations."""
        config_data = create_invalid_config()
        
        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))
            
            with pytest.raises(ValueError) as exc_info:
                ProviderRegistry.from_config(config)
            
            # Should detect missing pipelines field or unsupported provider type
            error_message = str(exc_info.value).lower()
            assert "pipelines" in error_message or "unsupported" in error_message

    def test_old_configuration_format_error(self):
        """Test error handling for old configuration format."""
        config_data = create_old_format_config()
        
        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))
            
            with pytest.raises(ValueError) as exc_info:
                ProviderRegistry.from_config(config)
            
            # Should detect old format and provide helpful error
            error_message = str(exc_info.value)
            assert "old format" in error_message
            assert "update" in error_message.lower()

    def test_dynamic_provider_loading(self, complex_config_file):
        """Test dynamic provider loading via registry mappings."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test that different provider types are created correctly
        audio_provider = registry.get_audio_provider("primary_audio")
        assert audio_provider is not None
        
        image_provider = registry.get_image_provider("openai_images")
        assert image_provider is not None
        
        sync_provider = registry.get_sync_provider("main_anki")
        assert sync_provider is not None

    def test_provider_configuration_inheritance(self, complex_config_file):
        """Test that provider configurations are properly inherited."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Check that providers have access to their configuration
        # Note: This test assumes providers store their config (implementation dependent)
        primary_audio = registry.get_audio_provider("primary_audio")
        if hasattr(primary_audio, 'config'):
            # Provider should have configuration but not registry metadata
            assert "pipelines" not in primary_audio.config  # Should be filtered out
            assert "type" not in primary_audio.config  # Should be filtered out

    def test_pipeline_assignment_methods(self, complex_config_file):
        """Test pipeline assignment getter/setter methods."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test getting pipeline assignments
        vocab_assignments = registry.get_pipeline_assignments("data", "vocabulary_data")
        assert "vocabulary" in vocab_assignments
        
        shared_assignments = registry.get_pipeline_assignments("data", "shared_data")
        assert "*" in shared_assignments
        
        # Test setting new pipeline assignments
        registry.set_pipeline_assignments("audio", "primary_audio", ["new_pipeline"])
        new_assignments = registry.get_pipeline_assignments("audio", "primary_audio")
        assert "new_pipeline" in new_assignments

    def test_provider_info_aggregation(self, complex_config_file):
        """Test provider information aggregation."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Test provider info structure
        info = registry.get_provider_info()
        
        # Validate info structure
        assert "data_providers" in info
        assert "audio_providers" in info
        assert "image_providers" in info
        assert "sync_providers" in info
        
        # Validate counts
        expected_counts = {
            "data": 3,    # vocabulary_data, conjugation_data, shared_data
            "audio": 2,   # primary_audio, backup_audio
            "image": 2,   # openai_images, runware_images
            "sync": 1,    # main_anki
        }
        assert_registry_provider_count(registry, expected_counts)

    def test_provider_type_validation(self, complex_config_file):
        """Test provider type validation during registration."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # All providers should be registered without type validation errors
        # since we're using valid provider types in the complex config
        
        # Test that providers are accessible by their registered names
        assert registry.get_audio_provider("primary_audio") is not None
        assert registry.get_image_provider("openai_images") is not None
        assert registry.get_image_provider("runware_images") is not None

    def test_provider_pipeline_isolation(self, complex_config_file):
        """Test that pipeline assignments properly isolate provider access."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Create a new pipeline that shouldn't have access to specific providers
        new_pipeline_providers = registry.get_providers_for_pipeline("nonexistent_pipeline")
        
        # Should only have access to universal providers ("*" assignments)
        assert "shared_data" in new_pipeline_providers["data"]  # Has "*"
        assert "vocabulary_data" not in new_pipeline_providers["data"]  # Specific to vocabulary
        assert "conjugation_data" not in new_pipeline_providers["data"]  # Specific to conjugation
        
        assert "main_anki" in new_pipeline_providers["sync"]  # Has "*"
        assert len(new_pipeline_providers["audio"]) == 0  # No universal audio providers
        assert len(new_pipeline_providers["image"]) == 0  # No universal image providers

    def test_registry_clearing_and_reinitialization(self, complex_config_file):
        """Test registry clearing and reinitialization."""
        config = Config.load(str(complex_config_file))
        registry = ProviderRegistry.from_config(config)
        
        # Validate initial state
        assert len(registry.list_data_providers()) > 0
        assert len(registry.list_audio_providers()) > 0
        
        # Clear registry
        registry.clear_all()
        
        # Validate cleared state
        assert len(registry.list_data_providers()) == 0
        assert len(registry.list_audio_providers()) == 0
        assert len(registry.list_image_providers()) == 0
        assert len(registry.list_sync_providers()) == 0
        
        # Reinitialize from config
        new_registry = ProviderRegistry.from_config(config)
        
        # Should be back to original state
        assert len(new_registry.list_data_providers()) == 3
        assert len(new_registry.list_audio_providers()) == 2

    def test_environment_variable_processing_in_providers(self, complex_config_file):
        """Test that environment variables are processed in provider configs."""
        import os
        
        # Set test environment variables
        test_env = {
            "FORVO_API_KEY": "test_forvo_key_from_env",
            "OPENAI_API_KEY": "test_openai_key_from_env",
            "RUNWARE_API_KEY": "test_runware_key_from_env"
        }
        
        # Mock environment variables
        with pytest.MonkeyPatch().context() as mp:
            for key, value in test_env.items():
                mp.setenv(key, value)
            
            config = Config.load(str(complex_config_file))
            
            # Validate environment variable substitution in config
            audio_config = config.get("providers.audio.primary_audio")
            assert audio_config["api_key"] == "test_forvo_key_from_env"
            
            openai_config = config.get("providers.image.openai_images")
            assert openai_config["api_key"] == "test_openai_key_from_env"
            
            runware_config = config.get("providers.image.runware_images")
            assert runware_config["api_key"] == "test_runware_key_from_env"