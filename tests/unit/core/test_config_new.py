"""Unit tests for simplified Config class."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from src.core.config import Config


class TestConfig:
    """Test cases for simplified Config class."""

    def test_config_loads_default_file(self, tmp_path):
        """Test config loads from default config.json location"""
        config_file = tmp_path / "config.json"
        config_data = {
            "system": {"log_level": "info"},
            "providers": {"media": {"type": "openai"}},
        }
        config_file.write_text(json.dumps(config_data))

        with patch.object(Path, "cwd", return_value=tmp_path):
            config = Config()
            assert config.get("system.log_level") == "info"
            assert config.get("providers.media.type") == "openai"

    def test_config_loads_custom_path(self, tmp_path):
        """Test config loads from specified file path"""
        config_file = tmp_path / "custom.json"
        config_data = {"custom": {"value": "test"}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("custom.value") == "test"

    def test_config_handles_missing_file(self, tmp_path):
        """Test config gracefully handles missing file with defaults"""
        nonexistent_file = tmp_path / "missing.json"

        config = Config(str(nonexistent_file))
        assert config.get("missing.key", "default") == "default"

    def test_config_validates_json_syntax(self, tmp_path):
        """Test config raises appropriate error for malformed JSON"""
        config_file = tmp_path / "malformed.json"
        config_file.write_text('{"invalid": json}')

        with pytest.raises(json.JSONDecodeError):
            Config(str(config_file))

    def test_env_var_substitution_basic(self, tmp_path, monkeypatch):
        """Test ${VAR} gets replaced with environment variable value"""
        monkeypatch.setenv("TEST_VAR", "resolved_value")

        config_file = tmp_path / "config.json"
        config_data = {"system": {"path": "${TEST_VAR}/data"}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("system.path") == "resolved_value/data"

    def test_env_var_substitution_missing(self, tmp_path):
        """Test missing env vars remain as literal ${VAR} strings"""
        config_file = tmp_path / "config.json"
        config_data = {"system": {"path": "${MISSING_VAR}/data"}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("system.path") == "${MISSING_VAR}/data"

    def test_get_method_dot_notation(self, tmp_path):
        """Test config.get('providers.media.type') returns correct nested value"""
        config_file = tmp_path / "config.json"
        config_data = {"providers": {"media": {"type": "openai", "timeout": 30}}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("providers.media.type") == "openai"
        assert config.get("providers.media.timeout") == 30

    def test_get_method_with_defaults(self, tmp_path):
        """Test config.get('missing.key', 'default') returns default value"""
        config_file = tmp_path / "config.json"
        config_data = {"existing": {"key": "value"}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("missing.key", "default") == "default"
        assert config.get("existing.missing", "default") == "default"

    def test_get_provider_returns_dict(self, tmp_path):
        """Test get_provider('openai') returns provider configuration dict"""
        config_file = tmp_path / "config.json"
        config_data = {
            "providers": {
                "media": {
                    "type": "openai",
                    "api_key": "${OPENAI_API_KEY}",
                    "timeout": 30,
                }
            }
        }
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        provider_config = config.get_provider("media")
        assert isinstance(provider_config, dict)
        assert provider_config["type"] == "openai"
        assert provider_config["timeout"] == 30

    def test_get_system_settings(self, tmp_path):
        """Test get_system_settings() returns system section as dict"""
        config_file = tmp_path / "config.json"
        config_data = {"system": {"log_level": "debug", "max_workers": 4}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        system_settings = config.get_system_settings()
        assert isinstance(system_settings, dict)
        assert system_settings["log_level"] == "debug"
        assert system_settings["max_workers"] == 4

    def test_config_with_empty_file(self, tmp_path):
        """Test behavior with completely empty JSON file"""
        config_file = tmp_path / "empty.json"
        config_file.write_text("{}")

        config = Config(str(config_file))
        assert config.get("any.key", "default") == "default"

    def test_config_with_null_values(self, tmp_path):
        """Test handling of null values in configuration"""
        config_file = tmp_path / "config.json"
        config_data = {"system": {"nullable": None, "string": "value"}}
        config_file.write_text(json.dumps(config_data))

        config = Config(str(config_file))
        assert config.get("system.nullable") is None
        assert config.get("system.string") == "value"
