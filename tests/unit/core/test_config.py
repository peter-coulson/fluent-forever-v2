"""Unit tests for configuration system."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from src.core.config import ConfigLevel, ConfigManager, ConfigSource, get_config_manager


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_config_manager_creation_with_valid_path(self, tmp_path):
        """Test config manager creation with valid base path."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        manager = ConfigManager(tmp_path)

        assert manager.base_path == tmp_path
        assert manager.config_cache == {}
        assert manager.sources == []

    def test_config_manager_missing_base_path(self):
        """Test ConfigManager with non-existent base path auto-detection."""
        # Test auto-detection fallback when no config.json found
        manager = ConfigManager()

        # Should fallback to two levels up from config.py file location
        # config.py is at src/core/config.py, so parents[2] goes to project root
        import sys

        config_module_path = Path(sys.modules["src.core.config"].__file__)
        expected_base = config_module_path.parents[2]
        assert manager.base_path == expected_base

    def test_config_manager_explicit_nonexistent_path(self):
        """Test ConfigManager with explicit non-existent base path."""
        nonexistent_path = Path("/this/path/does/not/exist")

        # Should not raise error during creation
        manager = ConfigManager(nonexistent_path)
        assert manager.base_path == nonexistent_path

    def test_config_manager_malformed_json_handling(self, tmp_path):
        """Test ConfigManager handling of malformed JSON files."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create malformed JSON file
        core_config = config_dir / "core.json"
        core_config.write_text(
            '{"system": {"log_level": "debug"'
        )  # Missing closing brace

        manager = ConfigManager(tmp_path)

        # Should handle malformed JSON gracefully by skipping the malformed file
        with patch("builtins.print"):  # Suppress warning output
            config = manager.load_config("system")

        # System config should still include default structure even with malformed core config
        # The system config loading always adds stages section, providers only if provider configs exist
        assert "stages" in config
        # The malformed core config should be skipped, so no system.log_level from malformed file
        assert config.get("system", {}).get("log_level") != "debug"
        # Config should be minimal when core config fails to load
        assert len(config) >= 1  # At least stages

    def test_environment_variable_resolution_basic(self, tmp_path, monkeypatch):
        """Test basic environment variable resolution."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Set test environment variable
        monkeypatch.setenv("TEST_VALUE", "resolved")

        # Create config with environment variable
        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"value": "${TEST_VALUE}"}}')

        manager = ConfigManager(tmp_path)
        config = manager.load_config("system")

        resolved = manager.resolve_environment_variables(config)
        assert resolved["system"]["value"] == "resolved"

    def test_environment_variable_circular_resolution(self, tmp_path, monkeypatch):
        """Test environment variable circular resolution detection."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create circular reference: VAR1 -> VAR2 -> VAR1
        monkeypatch.setenv("VAR1", "${VAR2}")
        monkeypatch.setenv("VAR2", "${VAR1}")

        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"value": "${VAR1}"}}')

        manager = ConfigManager(tmp_path)
        config = manager.load_config("system")

        # Should not resolve circular references, leave as-is
        resolved = manager.resolve_environment_variables(config)
        assert resolved["system"]["value"] == "${VAR2}"  # Stopped at first resolution

    def test_deep_merge_type_conflicts(self, tmp_path):
        """Test deep merge behavior with type conflicts."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create core config with dict value
        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"setting": {"nested": "value1"}}}')

        # Create environment config that tries to override with string
        env_dir = config_dir / "environments"
        env_dir.mkdir()
        env_config = env_dir / "development.json"
        env_config.write_text('{"system": {"setting": "string_value"}}')

        with patch.dict(os.environ, {"FLUENT_ENV": "development"}):
            manager = ConfigManager(tmp_path)
            config = manager.load_config("system")

        # String should override dict (last wins in deep merge)
        assert config["system"]["setting"] == "string_value"

    def test_deep_merge_nested_conflicts(self, tmp_path):
        """Test deep merge with nested structure conflicts."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Core config
        core_config = config_dir / "core.json"
        core_config.write_text(
            json.dumps(
                {
                    "system": {
                        "database": {
                            "host": "localhost",
                            "port": 5432,
                            "credentials": {"user": "admin"},
                        }
                    }
                }
            )
        )

        # Environment override
        env_dir = config_dir / "environments"
        env_dir.mkdir()
        env_config = env_dir / "development.json"
        env_config.write_text(
            json.dumps(
                {
                    "system": {
                        "database": {
                            "host": "dev.example.com",
                            "credentials": {"user": "dev_user", "password": "secret"},
                        }
                    }
                }
            )
        )

        with patch.dict(os.environ, {"FLUENT_ENV": "development"}):
            manager = ConfigManager(tmp_path)
            config = manager.load_config("system")

        # Should properly merge nested structures
        db_config = config["system"]["database"]
        assert db_config["host"] == "dev.example.com"  # Override
        assert db_config["port"] == 5432  # Preserved from core
        assert db_config["credentials"]["user"] == "dev_user"  # Override
        assert db_config["credentials"]["password"] == "secret"  # Added

    def test_config_source_priority_ordering(self, tmp_path):
        """Test correct priority ordering between config sources."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create all config levels with same key but different values
        # Core (priority 1)
        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"priority_test": "core"}}')

        # Environment (priority 3) - higher than core
        env_dir = config_dir / "environments"
        env_dir.mkdir()
        env_config = env_dir / "development.json"
        env_config.write_text('{"system": {"priority_test": "environment"}}')

        # Test without FF_ env var first
        with patch.dict(os.environ, {"FLUENT_ENV": "development"}, clear=True):
            manager = ConfigManager(tmp_path)
            system_config = manager.load_config("system")
            # Environment config should override core config
            assert system_config["system"]["priority_test"] == "environment"

        # Test with FF_ env var (highest priority)
        with patch.dict(
            os.environ,
            {"FLUENT_ENV": "development", "FF_SYSTEM_PRIORITY_TEST": "env_var"},
            clear=True,
        ):
            manager = ConfigManager(tmp_path)
            manager.clear_cache()  # Clear any cached config
            system_config = manager.load_config("system")
            # FF_ env var should have highest priority
            assert system_config["system"]["priority_test"] == "env_var"

    def test_environment_override_validation(self, tmp_path, monkeypatch):
        """Test FF_ prefix variable parsing edge cases."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"log_level": "info"}}')

        # Test various FF_ environment variable patterns
        monkeypatch.setenv("FF_SYSTEM_LOG_LEVEL", "debug")
        monkeypatch.setenv("FF_SYSTEM_DATABASE_HOST", "override.example.com")
        monkeypatch.setenv("FF_PROVIDERS_API_TIMEOUT", "30")
        monkeypatch.setenv("NOT_FF_VAR", "should_be_ignored")

        manager = ConfigManager(tmp_path)
        config = manager.load_config("system")

        # Should apply FF_ overrides
        assert config["system"]["log_level"] == "debug"
        assert config["system"]["database_host"] == "override.example.com"
        # FF_PROVIDERS_API_TIMEOUT becomes providers -> api -> timeout (3-part nested)
        # Values are parsed as JSON, so "30" becomes integer 30
        assert config["providers"]["api"]["timeout"] == 30

        # Should ignore non-FF variables
        assert "not_ff_var" not in str(config)

    def test_nested_config_key_parsing(self, tmp_path, monkeypatch):
        """Test nested configuration key parsing from environment variables."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        core_config = config_dir / "core.json"
        core_config.write_text("{}")

        # Test complex nested key parsing - based on actual _set_nested_config logic
        # FF_SYSTEM_DATABASE_CREDENTIALS_USERNAME -> system.database_credentials_username (special system handling)
        monkeypatch.setenv("FF_SYSTEM_DATABASE_CREDENTIALS_USERNAME", "admin")
        # FF_PROVIDERS_API_CLIENT_TIMEOUT -> providers.api_client_timeout (2 parts)
        monkeypatch.setenv("FF_PROVIDERS_API_CLIENT_TIMEOUT", "60")
        # FF_STAGES_PROCESS_MAX_RETRIES -> stages.process_max_retries (2 parts)
        monkeypatch.setenv("FF_STAGES_PROCESS_MAX_RETRIES", "5")

        manager = ConfigManager(tmp_path)
        config = manager.load_config("system")

        # Should create proper nested structure based on actual parsing logic
        # System with >2 parts gets special handling: system.{remaining_parts_joined}
        assert config["system"]["database_credentials_username"] == "admin"
        # 4-part keys get fully nested: providers.api.client.timeout
        assert config["providers"]["api"]["client"]["timeout"] == 60
        # 4-part keys get fully nested: stages.process.max.retries
        assert config["stages"]["process"]["max"]["retries"] == 5

    def test_json_value_parsing_in_env_vars(self, tmp_path, monkeypatch):
        """Test JSON value parsing in environment variables."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        core_config = config_dir / "core.json"
        core_config.write_text("{}")

        # Test JSON parsing in environment variables
        monkeypatch.setenv("FF_SYSTEM_ENABLED", "true")  # Should become boolean
        monkeypatch.setenv("FF_SYSTEM_COUNT", "42")  # Should become integer
        monkeypatch.setenv("FF_SYSTEM_LIST", '["item1", "item2"]')  # Should become list
        monkeypatch.setenv("FF_SYSTEM_DICT", '{"key": "value"}')  # Should become dict
        monkeypatch.setenv("FF_SYSTEM_STRING", "plain_string")  # Should stay string

        manager = ConfigManager(tmp_path)
        config = manager.load_config("system")

        assert config["system"]["enabled"] is True
        assert config["system"]["count"] == 42
        assert config["system"]["list"] == ["item1", "item2"]
        assert config["system"]["dict"] == {"key": "value"}
        assert config["system"]["string"] == "plain_string"


class TestConfigCache:
    """Test configuration caching behavior."""

    def test_config_caching(self, tmp_path):
        """Test configuration caching works correctly."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"value": "cached"}}')

        manager = ConfigManager(tmp_path)

        # First load
        config1 = manager.load_config("system")

        # Modify file after first load
        core_config.write_text('{"system": {"value": "modified"}}')

        # Second load should return cached version
        config2 = manager.load_config("system")

        assert config1 is config2  # Same object reference
        assert config2["system"]["value"] == "cached"  # Not modified

    def test_cache_clearing(self, tmp_path):
        """Test cache clearing functionality."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        core_config = config_dir / "core.json"
        core_config.write_text('{"system": {"value": "initial"}}')

        manager = ConfigManager(tmp_path)

        # Load and cache
        config1 = manager.load_config("system")
        assert config1["system"]["value"] == "initial"

        # Modify file and clear cache
        core_config.write_text('{"system": {"value": "updated"}}')
        manager.clear_cache()

        # Should load fresh config
        config2 = manager.load_config("system")
        assert config2["system"]["value"] == "updated"


class TestConfigValidation:
    """Test configuration validation functionality."""

    def test_valid_config_validation(self, tmp_path):
        """Test validation of valid configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create valid system config with required sections
        core_config = config_dir / "core.json"
        core_config.write_text(
            json.dumps({"system": {"log_level": "info"}, "paths": {"data_dir": "/tmp"}})
        )

        manager = ConfigManager(tmp_path)
        assert manager.validate_config() is True

    def test_invalid_config_validation_missing_sections(self, tmp_path):
        """Test validation failure with missing required sections."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create config missing required sections
        core_config = config_dir / "core.json"
        core_config.write_text('{"other": {"value": "test"}}')

        manager = ConfigManager(tmp_path)
        assert manager.validate_config() is False

    def test_invalid_config_validation_json_error(self, tmp_path):
        """Test validation failure with JSON parsing error."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create malformed JSON
        core_config = config_dir / "core.json"
        core_config.write_text('{"system": ')

        manager = ConfigManager(tmp_path)
        assert manager.validate_config() is False


class TestGlobalConfigManager:
    """Test global configuration manager."""

    def test_global_manager_singleton(self):
        """Test global manager singleton behavior."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()

        assert manager1 is manager2

    def test_global_manager_initialization(self):
        """Test global manager initializes correctly."""
        manager = get_config_manager()

        assert isinstance(manager, ConfigManager)
        assert manager.base_path is not None


class TestConfigSource:
    """Test ConfigSource dataclass."""

    def test_config_source_creation(self):
        """Test ConfigSource creation and properties."""
        path = Path("/test/config.json")
        level = ConfigLevel.SYSTEM
        priority = 1

        source = ConfigSource(path, level, priority)

        assert source.path == path
        assert source.level == level
        assert source.priority == priority


class TestConfigLevel:
    """Test ConfigLevel enum."""

    def test_config_level_values(self):
        """Test all ConfigLevel enum values."""
        assert ConfigLevel.SYSTEM.value == "system"
        assert ConfigLevel.PIPELINE.value == "pipeline"
        assert ConfigLevel.PROVIDER.value == "provider"
        assert ConfigLevel.ENVIRONMENT.value == "environment"
        assert ConfigLevel.CLI.value == "cli"
