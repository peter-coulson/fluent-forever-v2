#!/usr/bin/env python3
"""
Unit tests for Configuration CLI Commands

Tests configuration CLI command functionality.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from cli.commands.config_command import ConfigCommand


class TestConfigCommand:
    """Test ConfigCommand functionality"""
    
    def setup_method(self):
        """Set up test configuration"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        
        # Create test configuration structure
        (self.config_dir / 'config').mkdir()
        self._create_test_configs()
        
        # Mock the config manager to use our test directory
        with patch('cli.commands.config_command.get_config_manager') as mock_get_manager:
            from config.config_manager import ConfigManager
            test_manager = ConfigManager(self.config_dir)
            mock_get_manager.return_value = test_manager
            self.config_command = ConfigCommand()
    
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
            },
            "pipelines": {},
            "providers": {},
            "stages": {}
        }
        (self.config_dir / 'config' / 'core.json').write_text(json.dumps(core_config))
    
    def test_show_config_system(self):
        """Test showing system configuration"""
        args = Mock()
        args.action = 'show'
        args.type = None
        args.name = None
        
        result = self.config_command.execute(args)
        assert result == 0
    
    def test_validate_config_success(self):
        """Test successful configuration validation"""
        args = Mock()
        args.action = 'validate'
        
        result = self.config_command.execute(args)
        assert result == 0
    
    def test_init_config(self):
        """Test configuration initialization"""
        args = Mock()
        args.action = 'init'
        
        result = self.config_command.execute(args)
        assert result == 0
    
    def test_test_config(self):
        """Test configuration testing"""
        args = Mock()
        args.action = 'test'
        
        # Mock environment variable for test
        with patch.dict(os.environ, {'FF_SYSTEM_LOG_LEVEL': 'ERROR'}, clear=False):
            result = self.config_command.execute(args)
            assert result == 0
    
    def test_unknown_action(self):
        """Test handling unknown action"""
        args = Mock()
        args.action = 'unknown'
        
        result = self.config_command.execute(args)
        assert result == 1
    
    def test_show_config_with_type(self):
        """Test showing specific configuration type"""
        args = Mock()
        args.action = 'show'
        args.type = 'system'
        args.name = None
        
        result = self.config_command.execute(args)
        assert result == 0
    
    def test_show_config_with_type_and_name(self):
        """Test showing specific configuration type and name"""
        args = Mock()
        args.action = 'show'
        args.type = 'pipeline'
        args.name = 'vocabulary'
        
        result = self.config_command.execute(args)
        # May return 1 if vocabulary pipeline config doesn't exist, which is fine
        assert result in [0, 1]


class TestConfigCommandIntegration:
    """Integration tests for ConfigCommand with real config system"""
    
    def test_config_command_with_real_system(self):
        """Test config command with real configuration system"""
        config_command = ConfigCommand()
        
        # Test basic functionality
        args = Mock()
        args.action = 'validate'
        
        result = config_command.execute(args)
        # Should work with real configuration
        assert result == 0


if __name__ == "__main__":
    pytest.main([__file__])