"""
E2E Test Scenario 4: Configuration System and Environment Integration

Purpose: Validate configuration loading, environment substitution, and error handling
"""

import json
from pathlib import Path

import pytest
from src.core.config import Config

from tests.fixtures.configs import (
    ConfigFixture,
    create_env_var_config,
    create_invalid_json_file,
    create_minimal_working_config,
)
from tests.utils.assertions import (
    assert_config_loaded_correctly,
)


class TestConfigurationIntegration:
    """Test configuration system and environment integration."""

    def test_config_loading_basic(self):
        """Test basic configuration loading."""
        config_data = create_minimal_working_config()

        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            # Validate basic structure
            assert_config_loaded_correctly(config, ["providers"])

            # Check provider structure
            providers = config.get("providers")
            assert "data" in providers
            assert "test_data" in providers["data"]

    def test_environment_variable_substitution(self):
        """Test environment variable substitution in configuration."""
        config_data = create_env_var_config()

        # Set test environment variables
        test_env = {
            "DATA_PATH": "/custom/data/path",
            "READ_ONLY": "true",
            "FORVO_API_KEY": "env_forvo_key",
            "PIPELINE_NAME": "custom_pipeline",
            "LANGUAGE": "french",
            "FALLBACK_URL": "https://custom-fallback.com",
            "LOG_LEVEL": "WARNING",
            "DEBUG": "true",
            "API_TIMEOUT": "60",
        }

        with pytest.MonkeyPatch().context() as mp:
            for key, value in test_env.items():
                mp.setenv(key, value)

            with ConfigFixture(config_data) as config_path:
                config = Config.load(str(config_path))

                # Test data provider substitution
                data_config = config.get("providers.data.test_data")
                assert data_config["base_path"] == "/custom/data/path"
                assert data_config["read_only"] == "true"

                # Test audio provider substitution
                audio_config = config.get("providers.audio.forvo_provider")
                assert audio_config["api_key"] == "env_forvo_key"
                assert audio_config["pipelines"] == ["custom_pipeline"]
                assert audio_config["language"] == "french"
                assert audio_config["fallback_url"] == "https://custom-fallback.com"

                # Test system settings substitution
                assert config.get("system.log_level") == "WARNING"
                assert config.get("system.debug_mode") == "true"
                assert config.get("system.api_timeout") == "60"

    def test_environment_variable_defaults(self):
        """Test environment variable substitution with default values."""
        config_data = create_env_var_config()

        # Don't set any environment variables to test defaults
        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            # Should use default values
            data_config = config.get("providers.data.test_data")
            assert data_config["base_path"] == "./data"  # Default value
            assert data_config["read_only"] == "false"  # Default value

            audio_config = config.get("providers.audio.forvo_provider")
            assert audio_config["pipelines"] == ["test_pipeline"]  # Default value
            assert audio_config["language"] == "spanish"  # Default value

            # Test system defaults
            assert config.get("system.log_level") == "INFO"  # Default value
            assert config.get("system.debug_mode") == "false"  # Default value
            assert config.get("system.api_timeout") == "30"  # Default value

    def test_missing_environment_variable_without_default(self):
        """Test handling of missing environment variables without defaults."""
        import os

        # Ensure FORVO_API_KEY is not set
        original_value = os.environ.pop("FORVO_API_KEY", None)
        try:
            config_data = create_env_var_config()

            with ConfigFixture(config_data) as config_path:
                config = Config.load(str(config_path))

                # FORVO_API_KEY has no default, should remain as placeholder
                audio_config = config.get("providers.audio.forvo_provider")
                assert audio_config["api_key"] == "${FORVO_API_KEY}"
        finally:
            # Restore original value if it existed
            if original_value is not None:
                os.environ["FORVO_API_KEY"] = original_value

    def test_nested_environment_substitution(self):
        """Test environment variable substitution in nested structures."""
        config_data = {
            "providers": {
                "data": {
                    "nested_provider": {
                        "type": "json",
                        "pipelines": [
                            "${PIPELINE_1:default1}",
                            "${PIPELINE_2:default2}",
                        ],
                        "config": {
                            "nested_setting": "${NESTED_VAR:nested_default}",
                            "deep": {"value": "${DEEP_VAR:deep_default}"},
                        },
                    }
                }
            }
        }

        test_env = {
            "PIPELINE_1": "custom_pipeline_1",
            "NESTED_VAR": "custom_nested_value",
            "DEEP_VAR": "custom_deep_value",
        }

        with pytest.MonkeyPatch().context() as mp:
            for key, value in test_env.items():
                mp.setenv(key, value)

            with ConfigFixture(config_data) as config_path:
                config = Config.load(str(config_path))

                provider_config = config.get("providers.data.nested_provider")
                assert provider_config["pipelines"] == ["custom_pipeline_1", "default2"]
                assert (
                    provider_config["config"]["nested_setting"] == "custom_nested_value"
                )
                assert provider_config["config"]["deep"]["value"] == "custom_deep_value"

    def test_config_file_not_found(self):
        """Test graceful handling of missing configuration file."""
        nonexistent_path = "/nonexistent/config.json"
        config = Config.load(nonexistent_path)

        # Should create empty config without error
        assert config.get("providers") is None
        assert config.to_dict() == {}

    def test_invalid_json_configuration(self):
        """Test error handling for invalid JSON configuration."""
        invalid_json_path = create_invalid_json_file()

        try:
            with pytest.raises(json.JSONDecodeError):
                Config.load(str(invalid_json_path))
        finally:
            # Cleanup
            Path(invalid_json_path).unlink()

    def test_config_dot_notation_access(self):
        """Test configuration access using dot notation."""
        config_data = {
            "level1": {"level2": {"level3": "deep_value"}, "simple": "simple_value"},
            "root": "root_value",
        }

        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            # Test various access patterns
            assert config.get("root") == "root_value"
            assert config.get("level1.simple") == "simple_value"
            assert config.get("level1.level2.level3") == "deep_value"

            # Test nonexistent keys
            assert config.get("nonexistent") is None
            assert config.get("level1.nonexistent") is None
            assert config.get("level1.level2.nonexistent") is None

            # Test with default values
            assert config.get("nonexistent", "default") == "default"

    def test_provider_configuration_access(self):
        """Test provider-specific configuration access methods."""
        config_data = {
            "providers": {
                "data": {"test_provider": {"type": "json", "base_path": "test_path"}},
                "audio": {"forvo": {"type": "forvo", "api_key": "test_key"}},
            }
        }

        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            # Test provider access
            data_provider = config.get_provider("data.test_provider")
            assert data_provider["type"] == "json"
            assert data_provider["base_path"] == "test_path"

            audio_provider = config.get_provider("audio.forvo")
            assert audio_provider["type"] == "forvo"
            assert audio_provider["api_key"] == "test_key"

            # Test nonexistent provider
            nonexistent = config.get_provider("nonexistent.provider")
            assert nonexistent == {}

    def test_system_settings_access(self):
        """Test system settings configuration access."""
        config_data = {
            "system": {"log_level": "DEBUG", "max_retries": 5, "timeout": 30}
        }

        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            system_settings = config.get_system_settings()
            assert system_settings["log_level"] == "DEBUG"
            assert system_settings["max_retries"] == 5
            assert system_settings["timeout"] == 30

    def test_config_to_dict(self):
        """Test configuration serialization to dictionary."""
        config_data = create_minimal_working_config()

        with ConfigFixture(config_data) as config_path:
            config = Config.load(str(config_path))

            config_dict = config.to_dict()
            assert isinstance(config_dict, dict)
            assert "providers" in config_dict
            assert config_dict["providers"] == config_data["providers"]

    def test_environment_substitution_edge_cases(self):
        """Test edge cases in environment variable substitution."""
        config_data = {
            "test_cases": {
                "empty_default": "${EMPTY_VAR:}",
                "no_colon": "${NO_COLON_VAR}",
                "multiple_vars": "${VAR1:default1}_${VAR2:default2}",
                "nested_braces": "${OUTER:${INNER:default}}",
                "special_chars": "${SPECIAL:default!@#$%^&*()}",
            }
        }

        test_env = {"VAR1": "value1", "SPECIAL": "special_value"}

        with pytest.MonkeyPatch().context() as mp:
            for key, value in test_env.items():
                mp.setenv(key, value)

            with ConfigFixture(config_data) as config_path:
                config = Config.load(str(config_path))

                test_cases = config.get("test_cases")

                # Empty default should work
                assert test_cases["empty_default"] == ""

                # No colon should preserve original if var not set
                assert test_cases["no_colon"] == "${NO_COLON_VAR}"

                # Multiple variables in one string
                assert test_cases["multiple_vars"] == "value1_default2"

                # Special characters in default
                assert test_cases["special_chars"] == "special_value"

    def test_recursive_environment_substitution(self):
        """Test that environment substitution works recursively through data structures."""
        config_data = {
            "list_with_env": [
                "${LIST_VAR1:item1}",
                "${LIST_VAR2:item2}",
                {"nested_in_list": "${NESTED_LIST_VAR:nested_default}"},
            ],
            "dict_with_env": {
                "key1": "${DICT_VAR1:dict_value1}",
                "key2": {"nested_key": "${DICT_VAR2:dict_value2}"},
            },
        }

        test_env = {
            "LIST_VAR1": "custom_item1",
            "DICT_VAR1": "custom_dict_value1",
            "NESTED_LIST_VAR": "custom_nested",
        }

        with pytest.MonkeyPatch().context() as mp:
            for key, value in test_env.items():
                mp.setenv(key, value)

            with ConfigFixture(config_data) as config_path:
                config = Config.load(str(config_path))

                # Test list substitution
                list_data = config.get("list_with_env")
                assert list_data[0] == "custom_item1"
                assert list_data[1] == "item2"  # Default value
                assert list_data[2]["nested_in_list"] == "custom_nested"

                # Test dict substitution
                dict_data = config.get("dict_with_env")
                assert dict_data["key1"] == "custom_dict_value1"
                assert dict_data["key2"]["nested_key"] == "dict_value2"  # Default value

    def test_config_class_methods(self):
        """Test Config class methods and initialization patterns."""
        config_data = create_minimal_working_config()

        with ConfigFixture(config_data) as config_path:
            # Test direct initialization
            config1 = Config(str(config_path))

            # Test class method
            config2 = Config.load(str(config_path))

            # Should be equivalent
            assert config1.to_dict() == config2.to_dict()

            # Test default path behavior
            current_dir = Path.cwd()
            if (current_dir / "config.json").exists():
                config3 = Config()
                assert config3.config_path == current_dir / "config.json"
