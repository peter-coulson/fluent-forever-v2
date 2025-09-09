#!/usr/bin/env python3
"""
Unit tests for ConfigManager

Tests hierarchical configuration loading, environment overrides, and validation.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from core.config import ConfigManager, ConfigLevel, ConfigSource
from core.config_validator import ConfigValidator


class TestConfigManager:
    """Test ConfigManager functionality"""
    
    def setup_method(self):
        """Set up test configuration"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.config_manager = ConfigManager(self.config_dir)
        
        # Create test configuration structure
        (self.config_dir / 'config').mkdir()
        (self.config_dir / 'config' / 'pipelines').mkdir()
        (self.config_dir / 'config' / 'providers').mkdir()
        (self.config_dir / 'config' / 'environments').mkdir()
        (self.config_dir / 'config' / 'cli').mkdir()
        
        # Create test config files
        self._create_test_configs()
    
    def teardown_method(self):
        """Clean up test configuration"""
        self.temp_dir.cleanup()
    
    def _create_test_configs(self):
        """Create test configuration files"""
        # Core config
        core_config = {
            "system": {
                "log_level": "INFO",
                "cache_enabled": True,
                "max_concurrent_requests": 5
            },
            "paths": {
                "media_base": "media"
            }
        }
        (self.config_dir / 'config' / 'core.json').write_text(json.dumps(core_config))
        
        # Pipeline config
        pipeline_config = {
            "pipeline": {
                "name": "test_pipeline",
                "stages": ["stage1", "stage2"]
            }
        }
        (self.config_dir / 'config' / 'pipelines' / 'test_pipeline.json').write_text(
            json.dumps(pipeline_config)
        )
        
        # Provider config
        provider_config = {
            "provider": {
                "type": "test_provider",
                "enabled": True
            }
        }
        (self.config_dir / 'config' / 'providers' / 'test_provider.json').write_text(
            json.dumps(provider_config)
        )
        
        # Environment config
        env_config = {
            "system": {
                "log_level": "DEBUG"
            }
        }
        (self.config_dir / 'config' / 'environments' / 'development.json').write_text(
            json.dumps(env_config)
        )
        
        # Legacy config for migration testing
        legacy_config = {
            "apis": {
                "openai": {"enabled": True},
                "anki": {"enabled": True}
            },
            "paths": {
                "vocabulary_db": "vocabulary.json"
            }
        }
        (self.config_dir / 'config.json').write_text(json.dumps(legacy_config))
    
    def test_load_system_config(self):
        """Test loading system configuration"""
        config = self.config_manager.load_config('system')
        
        assert config is not None
        assert 'system' in config
        assert config['system']['log_level'] == 'DEBUG'  # Should use environment override
        assert config['system']['cache_enabled'] is True
    
    def test_load_pipeline_config(self):
        """Test loading pipeline-specific configuration"""
        config = self.config_manager.get_pipeline_config('test_pipeline')
        
        assert config is not None
        assert 'pipeline' in config
        assert config['pipeline']['name'] == 'test_pipeline'
        assert config['pipeline']['stages'] == ['stage1', 'stage2']
    
    def test_load_provider_config(self):
        """Test loading provider-specific configuration"""
        config = self.config_manager.get_provider_config('test_provider')
        
        assert config is not None
        assert 'provider' in config
        assert config['provider']['type'] == 'test_provider'
        assert config['provider']['enabled'] is True
    
    def test_environment_override(self):
        """Test environment variable overrides"""
        os.environ['FF_SYSTEM_LOG_LEVEL'] = 'ERROR'
        self.config_manager.clear_cache()
        
        config = self.config_manager.load_config('system')
        assert config['system']['log_level'] == 'ERROR'
        
        # Clean up
        os.environ.pop('FF_SYSTEM_LOG_LEVEL', None)
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        is_valid = self.config_manager.validate_config()
        assert is_valid is True
    
    def test_legacy_config_migration(self):
        """Test legacy configuration migration"""
        legacy_config = self.config_manager.load_legacy_config()
        assert legacy_config is not None
        assert 'apis' in legacy_config
        
        migrated_config = self.config_manager.migrate_legacy_config(legacy_config)
        assert migrated_config is not None
        assert 'pipelines' in migrated_config
        assert 'providers' in migrated_config
    
    def test_cache_functionality(self):
        """Test configuration caching"""
        # Load config to populate cache
        config1 = self.config_manager.load_config('system')
        
        # Load again - should come from cache
        config2 = self.config_manager.load_config('system')
        
        assert config1 is config2  # Should be same object from cache
        
        # Clear cache and reload
        self.config_manager.clear_cache()
        config3 = self.config_manager.load_config('system')
        
        assert config1 is not config3  # Should be different object


class TestConfigValidator:
    """Test ConfigValidator functionality"""
    
    def setup_method(self):
        """Set up test validator"""
        self.validator = ConfigValidator()
    
    def test_valid_configuration(self):
        """Test validation of valid configuration"""
        valid_config = {
            "system": {
                "log_level": "INFO",
                "cache_enabled": True,
                "max_concurrent_requests": 5
            },
            "paths": {
                "media_base": "media"
            },
            "pipelines": {
                "test": {
                    "stages": ["stage1", "stage2"]
                }
            },
            "providers": {
                "test_provider": {}
            }
        }
        
        result = self.validator.validate(valid_config)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_invalid_configuration(self):
        """Test validation of invalid configuration"""
        invalid_config = {
            "system": {
                "cache_enabled": True
                # Missing required log_level
            },
            "pipelines": {
                "test": {
                    # Missing required stages
                }
            }
        }
        
        result = self.validator.validate(invalid_config)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Check for specific errors
        error_messages = ' '.join(result.errors)
        assert 'log_level' in error_messages
        assert 'stages' in error_messages
    
    def test_missing_sections(self):
        """Test validation with missing required sections"""
        incomplete_config = {
            "system": {
                "log_level": "INFO",
                "cache_enabled": True,
                "max_concurrent_requests": 5
            }
            # Missing paths, pipelines, providers
        }
        
        result = self.validator.validate(incomplete_config)
        assert result.is_valid is False
        assert 'paths' in ' '.join(result.errors)
        assert 'pipelines' in ' '.join(result.errors)
        assert 'providers' in ' '.join(result.errors)


class TestConfigSource:
    """Test ConfigSource functionality"""
    
    def test_config_source_creation(self):
        """Test creating ConfigSource objects"""
        path = Path('/test/path')
        source = ConfigSource(path, ConfigLevel.SYSTEM, 1)
        
        assert source.path == path
        assert source.level == ConfigLevel.SYSTEM
        assert source.priority == 1
    
    def test_config_level_enum(self):
        """Test ConfigLevel enum values"""
        assert ConfigLevel.SYSTEM.value == 'system'
        assert ConfigLevel.PIPELINE.value == 'pipeline'
        assert ConfigLevel.PROVIDER.value == 'provider'
        assert ConfigLevel.ENVIRONMENT.value == 'environment'
        assert ConfigLevel.CLI.value == 'cli'


if __name__ == "__main__":
    pytest.main([__file__])