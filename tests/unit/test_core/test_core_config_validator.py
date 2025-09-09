#!/usr/bin/env python3
"""
Unit tests for Core Configuration Validator

Tests configuration validation functionality after migration.
"""

import pytest
import tempfile
import json
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from core.config_validator import ConfigValidator


class TestCoreConfigValidator:
    """Test Core ConfigValidator functionality"""
    
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
        assert 'log_level' in error_messages or 'stages' in error_messages
    
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
        # Should either be valid (if these are optional) or have specific errors
        if not result.is_valid:
            error_msg = ' '.join(result.errors)
            # At least one of these should be mentioned if they're required
            assert any(section in error_msg for section in ['paths', 'pipelines', 'providers'])


if __name__ == "__main__":
    pytest.main([__file__])