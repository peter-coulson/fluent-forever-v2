"""
Core Configuration Module

Compatibility layer for validation gates that expect core.config module.
This module re-exports the main configuration system.
"""

# Re-export main configuration system for compatibility
from config.config_manager import ConfigManager, get_config_manager
from config.config_validator import ConfigValidator
from config import *

# Make validator available as core.config_validator
import config.config_validator as config_validator

__all__ = ['ConfigManager', 'ConfigValidator', 'get_config_manager', 'config_validator']