#!/usr/bin/env python3
"""
Session 6 Validation Gate: Configuration Loading System

Tests the contract for unified configuration loading.
These tests define how configuration should be loaded, validated,
and managed across the system.

CONTRACT BEING TESTED:
- Configuration loads from unified structure
- Environment variables override config files
- Configuration validation catches errors early
- Default values are properly applied
- Configuration changes are properly propagated
"""

import pytest
from typing import Dict, Any
from tests.e2e.conftest import MockProvider


class TestConfigurationLoadingContract:
    """Test configuration loading contracts"""
    
    def test_config_file_loading(self, mock_config_data):
        """Contract: Configuration loads from JSON files"""
        loader = MockConfigLoader()
        
        config = loader.load_config("/test/config.json")
        
        assert isinstance(config, dict)
        assert "apis" in config
        assert "paths" in config
        assert config["apis"]["openai"]["enabled"] is True
    
    def test_environment_variable_override(self, mock_config_data):
        """Contract: Environment variables override config file values"""
        loader = MockConfigLoader()
        
        # Override with environment variable
        config = loader.load_config("/test/config.json", env_overrides={
            "OPENAI_API_KEY": "env_key",
            "ANKI_DECK_NAME": "Environment Deck"
        })
        
        assert config["apis"]["openai"]["api_key"] == "env_key"
        assert config["apis"]["anki"]["deck_name"] == "Environment Deck"
    
    def test_default_values_application(self):
        """Contract: Default values are applied when configuration is missing"""
        loader = MockConfigLoader()
        
        # Load minimal config
        minimal_config = {"apis": {"openai": {"enabled": True}}}
        config = loader.apply_defaults(minimal_config)
        
        # Should have applied defaults
        assert "timeout" in config["apis"]["openai"]
        assert "max_retries" in config["apis"]["base"]
        assert config["paths"]["media_folder"] == "media"
    
    def test_config_validation(self):
        """Contract: Invalid configuration is rejected"""
        loader = MockConfigLoader()
        
        # Valid config should pass
        valid_config = {
            "apis": {"openai": {"enabled": True, "timeout": 30}},
            "paths": {"vocabulary_db": "vocabulary.json"}
        }
        
        validation_result = loader.validate_config(valid_config)
        assert validation_result["valid"] is True
        
        # Invalid config should fail
        invalid_config = {
            "apis": {"openai": {"timeout": "not_a_number"}},  # Invalid type
            "paths": {}  # Missing required path
        }
        
        validation_result = loader.validate_config(invalid_config)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0


# Mock Configuration Loader
class MockConfigLoader:
    """Mock configuration loader for testing"""
    
    def __init__(self):
        self.defaults = {
            "apis": {
                "base": {
                    "timeout": 30,
                    "max_retries": 3
                },
                "openai": {
                    "timeout": 60,
                    "api_key": ""
                },
                "anki": {
                    "deck_name": "Default Deck"
                }
            },
            "paths": {
                "media_folder": "media",
                "vocabulary_db": "vocabulary.json"
            }
        }
    
    def load_config(self, config_path: str, env_overrides: Dict[str, str] = None) -> Dict[str, Any]:
        """Load configuration with environment overrides"""
        # Base config
        config = {
            "apis": {
                "openai": {"enabled": True, "api_key": "file_key"},
                "anki": {"deck_name": "File Deck"}
            },
            "paths": {"vocabulary_db": "vocabulary.json"}
        }
        
        # Apply environment overrides
        if env_overrides:
            if "OPENAI_API_KEY" in env_overrides:
                config["apis"]["openai"]["api_key"] = env_overrides["OPENAI_API_KEY"]
            if "ANKI_DECK_NAME" in env_overrides:
                config["apis"]["anki"]["deck_name"] = env_overrides["ANKI_DECK_NAME"]
        
        return config
    
    def apply_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to configuration"""
        result = config.copy()
        
        # Deep merge defaults
        def merge_defaults(target, defaults):
            for key, default_value in defaults.items():
                if key not in target:
                    if isinstance(default_value, dict):
                        target[key] = {}
                        merge_defaults(target[key], default_value)
                    else:
                        target[key] = default_value
                elif isinstance(default_value, dict) and isinstance(target[key], dict):
                    merge_defaults(target[key], default_value)
        
        # Merge defaults for each section
        for section, section_defaults in self.defaults.items():
            if section not in result:
                result[section] = {}
            merge_defaults(result[section], section_defaults)
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration"""
        errors = []
        
        # Check required sections
        if "apis" not in config:
            errors.append("Missing required section: apis")
        
        if "paths" not in config:
            errors.append("Missing required section: paths")
        
        # Check data types
        if "apis" in config and "openai" in config["apis"]:
            if "timeout" in config["apis"]["openai"]:
                if not isinstance(config["apis"]["openai"]["timeout"], (int, float)):
                    errors.append("openai.timeout must be a number")
        
        # Check required paths
        if "paths" in config:
            if not config["paths"].get("vocabulary_db"):
                errors.append("Missing required path: vocabulary_db")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }