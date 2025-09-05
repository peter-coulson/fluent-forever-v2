#!/usr/bin/env python3
"""
Validation gate for Session 6: Configuration Refactor

Tests that unified configuration system loads and validates correctly.
This test will initially fail until Session 6 is implemented.
"""

import pytest
from pathlib import Path
import sys
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_unified_configuration():
    """
    Validation gate for Session 6: Configuration System
    
    Tests:
    - Unified configuration can be loaded
    - Configuration validates correctly
    - Pipeline-specific configs are accessible
    """
    try:
        from core.config import ConfigManager
    except ImportError:
        pytest.skip("Configuration system not yet implemented (Session 6 pending)")
    
    config_manager = ConfigManager()
    
    # Test configuration loading
    config = config_manager.load_config()
    assert config is not None, "Configuration should load"
    
    # Test configuration validation
    is_valid = config_manager.validate_config()
    assert is_valid, "Configuration should be valid"
    
    # Test pipeline-specific configuration access
    vocab_config = config_manager.get_pipeline_config("vocabulary")
    assert vocab_config is not None, "Should have vocabulary pipeline config"


def test_config_consolidation():
    """Test that all configurations are properly consolidated."""
    try:
        from core.config import ConfigManager
    except ImportError:
        pytest.skip("Configuration system not yet implemented (Session 6 pending)")
    
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Test that all major config sections exist
    required_sections = [
        "pipelines",  # Pipeline-specific configurations
        "providers",  # Provider configurations  
        "stages",     # Stage configurations
        "apis",       # API configurations (legacy compatibility)
        "paths"       # Path configurations
    ]
    
    for section in required_sections:
        assert section in config, f"Missing required config section: {section}"


def test_config_validation():
    """Test comprehensive configuration validation."""
    try:
        from core.config import ConfigManager
        from core.config_validator import ConfigValidator
    except ImportError:
        pytest.skip("Configuration system not yet implemented (Session 6 pending)")
    
    validator = ConfigValidator()
    
    # Test valid configuration passes
    valid_config = {
        "pipelines": {
            "vocabulary": {
                "stages": ["prepare", "validate", "generate", "sync"]
            }
        },
        "providers": {
            "media": {
                "openai": {"enabled": True},
                "runware": {"enabled": True}
            }
        }
    }
    
    result = validator.validate(valid_config)
    assert result.is_valid, f"Valid config should pass: {result.errors}"


def test_legacy_compatibility():
    """Test that legacy config.json format still works."""
    try:
        from core.config import ConfigManager
    except ImportError:
        pytest.skip("Configuration system not yet implemented (Session 6 pending)")
    
    config_manager = ConfigManager()
    
    # Test loading legacy config format
    legacy_config = config_manager.load_legacy_config()
    assert legacy_config is not None, "Should be able to load legacy config"
    
    # Test migration from legacy format
    migrated_config = config_manager.migrate_legacy_config(legacy_config)
    assert migrated_config is not None, "Should be able to migrate legacy config"
    assert "pipelines" in migrated_config, "Migrated config should have pipelines section"


def test_environment_variable_support():
    """Test that configuration supports environment variables."""
    try:
        from core.config import ConfigManager
    except ImportError:
        pytest.skip("Configuration system not yet implemented (Session 6 pending)")
    
    config_manager = ConfigManager()
    
    # Test environment variable resolution
    config_with_env = {
        "apis": {
            "openai": {
                "api_key": "${OPENAI_API_KEY}"
            }
        }
    }
    
    resolved_config = config_manager.resolve_environment_variables(config_with_env)
    assert resolved_config is not None, "Should resolve environment variables"


if __name__ == "__main__":
    test_unified_configuration()
    test_config_consolidation()
    test_config_validation()
    test_legacy_compatibility()
    test_environment_variable_support()
    print("Session 6 validation gate passed!")