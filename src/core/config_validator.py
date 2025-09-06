"""
Core Configuration Validator Module

Compatibility layer that re-exports the configuration validator.
"""

# Re-export for compatibility
from config.config_validator import ConfigValidator, ValidationResult

__all__ = ['ConfigValidator', 'ValidationResult']