"""Unit tests for Provider Registry file conflict validation."""

import pytest
from src.providers.registry import ProviderRegistry

from tests.fixtures.mock_implementations import MockDataProvider


class TestRegistryFileConflicts:
    """Test cases for registry file conflict validation."""

    def test_validate_file_conflicts_no_conflicts(self):
        """Test validation passes when there are no file conflicts."""
        registry = ProviderRegistry()

        # Configure providers with different files
        registry._data_provider_configs = {
            "provider1": {"files": ["file1", "file2"]},
            "provider2": {"files": ["file3", "file4"]},
            "provider3": {"files": []},  # No restrictions
        }

        # Should not raise any exception
        registry._validate_file_conflicts()

    def test_validate_file_conflicts_with_conflicts(self):
        """Test validation fails when there are file conflicts."""
        registry = ProviderRegistry()

        # Configure providers with overlapping files
        registry._data_provider_configs = {
            "provider1": {"files": ["file1", "file2"]},
            "provider2": {"files": ["file2", "file3"]},  # file2 conflicts
        }

        with pytest.raises(
            ValueError, match="File conflicts detected.*file2.*provider1.*provider2"
        ):
            registry._validate_file_conflicts()

    def test_validate_file_conflicts_multiple_conflicts(self):
        """Test validation reports multiple file conflicts."""
        registry = ProviderRegistry()

        # Configure providers with multiple overlapping files
        registry._data_provider_configs = {
            "provider1": {"files": ["file1", "file2"]},
            "provider2": {"files": ["file2", "file3"]},
            "provider3": {"files": ["file3", "file4"]},
        }

        with pytest.raises(ValueError) as exc_info:
            registry._validate_file_conflicts()

        error_message = str(exc_info.value)
        assert "file2" in error_message
        assert "file3" in error_message

    def test_validate_file_conflicts_empty_files_ignored(self):
        """Test that providers with empty files list don't cause conflicts."""
        registry = ProviderRegistry()

        # Configure providers where some have empty files list
        registry._data_provider_configs = {
            "provider1": {"files": ["file1"]},
            "provider2": {"files": []},  # Empty = manage all files, no conflicts
            "provider3": {"files": ["file2"]},
        }

        # Should not raise exception - empty files lists don't participate in conflict detection
        registry._validate_file_conflicts()

    def test_register_data_provider_with_config(self):
        """Test registering data provider with configuration."""
        registry = ProviderRegistry()
        provider = MockDataProvider()
        config = {"files": ["file1", "file2"], "read_only": True}

        # Should register successfully
        registry.register_data_provider("test", provider, config)

        # Verify provider is registered
        assert registry.get_data_provider("test") is provider

        # Verify config is stored
        assert registry._data_provider_configs["test"] == config

    def test_register_data_provider_without_config(self):
        """Test registering data provider without configuration (backwards compatibility)."""
        registry = ProviderRegistry()
        provider = MockDataProvider()

        # Should register successfully without config
        registry.register_data_provider("test", provider)

        # Verify provider is registered
        assert registry.get_data_provider("test") is provider

        # Verify no config is stored
        assert "test" not in registry._data_provider_configs

    def test_register_multiple_providers_different_files_allowed(self):
        """Test registering multiple providers with different files is allowed."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()

        config1 = {"files": ["vocab", "dictionary"], "read_only": True}
        config2 = {"files": ["output", "cache"], "read_only": False}

        # Should register both successfully
        registry.register_data_provider("sources", provider1, config1)
        registry.register_data_provider("working", provider2, config2)

        # Verify both are registered
        assert registry.get_data_provider("sources") is provider1
        assert registry.get_data_provider("working") is provider2

    def test_register_multiple_providers_same_files_raises_error(self):
        """Test registering multiple providers with same files raises error."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()

        config1 = {"files": ["shared_file"], "read_only": True}
        config2 = {"files": ["shared_file"], "read_only": False}

        # First registration should succeed
        registry.register_data_provider("provider1", provider1, config1)

        # Second registration should fail due to file conflict
        with pytest.raises(
            ValueError,
            match="File conflicts detected.*shared_file.*provider1.*provider2",
        ):
            registry.register_data_provider("provider2", provider2, config2)

    def test_register_providers_partial_overlap_raises_error(self):
        """Test registering providers with partial file overlap raises error."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()

        config1 = {"files": ["file1", "file2", "file3"], "read_only": True}
        config2 = {"files": ["file3", "file4", "file5"], "read_only": False}

        # First registration should succeed
        registry.register_data_provider("provider1", provider1, config1)

        # Second registration should fail due to file3 conflict
        with pytest.raises(
            ValueError, match="File conflicts detected.*file3.*provider1.*provider2"
        ):
            registry.register_data_provider("provider2", provider2, config2)

    def test_register_providers_with_unrestricted_allowed(self):
        """Test that providers with no file restrictions can coexist."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()

        config1 = {"files": [], "read_only": True}  # No file restrictions
        config2 = {"files": [], "read_only": False}  # No file restrictions

        # Both should register successfully
        registry.register_data_provider("provider1", provider1, config1)
        registry.register_data_provider("provider2", provider2, config2)

        # Verify both are registered
        assert registry.get_data_provider("provider1") is provider1
        assert registry.get_data_provider("provider2") is provider2

    def test_register_mixed_restricted_unrestricted_providers(self):
        """Test registering mix of restricted and unrestricted providers."""
        registry = ProviderRegistry()
        provider1 = MockDataProvider()
        provider2 = MockDataProvider()
        provider3 = MockDataProvider()

        config1 = {"files": ["specific_file"], "read_only": True}
        config2 = {"files": [], "read_only": False}  # No restrictions
        # provider3 registered without config (backwards compatibility)

        # All should register successfully
        registry.register_data_provider("restricted", provider1, config1)
        registry.register_data_provider("unrestricted", provider2, config2)
        registry.register_data_provider("legacy", provider3)

        # Verify all are registered
        assert registry.get_data_provider("restricted") is provider1
        assert registry.get_data_provider("unrestricted") is provider2
        assert registry.get_data_provider("legacy") is provider3

    def test_clear_all_clears_configs(self):
        """Test that clear_all() also clears provider configurations."""
        registry = ProviderRegistry()
        provider = MockDataProvider()
        config = {"files": ["file1"], "read_only": True}

        # Register provider with config
        registry.register_data_provider("test", provider, config)

        # Verify it's registered
        assert registry.get_data_provider("test") is provider
        assert "test" in registry._data_provider_configs

        # Clear all
        registry.clear_all()

        # Verify everything is cleared
        assert registry.get_data_provider("test") is None
        assert "test" not in registry._data_provider_configs
        assert len(registry._data_provider_configs) == 0
