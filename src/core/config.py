"""Simplified Configuration Manager for Fluent Forever V2

Provides simple configuration loading with environment variable substitution.
"""

import json
import os
import re
from pathlib import Path
from typing import Any


class Config:
    """Simplified configuration management with environment variable substitution"""

    def __init__(self, config_path: str | None = None):
        """Initialize config with optional custom path"""
        if config_path is None:
            # Use default config.json in project root
            self.config_path = Path.cwd() / "config.json"
        else:
            self.config_path = Path(config_path)

        self._config_data: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file"""
        if not self.config_path.exists():
            # Gracefully handle missing file with empty config
            self._config_data = {}
            return

        try:
            with open(self.config_path) as f:
                self._config_data = json.load(f)
        except json.JSONDecodeError:
            # Re-raise JSON decode errors to caller
            raise
        except OSError:
            # Handle file system errors gracefully
            self._config_data = {}

        # Apply environment variable substitution
        self._substitute_env_vars(self._config_data)

    def _substitute_env_vars(self, obj: Any) -> None:
        """Recursively substitute environment variables in configuration"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    obj[key] = self._resolve_env_string(value)
                elif isinstance(value, dict | list):
                    self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str):
                    obj[i] = self._resolve_env_string(item)
                elif isinstance(item, dict | list):
                    self._substitute_env_vars(item)

    def _resolve_env_string(self, value: str) -> str:
        """Resolve environment variables in a string"""
        # Pattern matches ${VAR} or ${VAR:default}
        pattern = r"\$\{([^}:]+)(?::([^}]*))?\}"

        def replace_env(match: re.Match[str]) -> str:
            env_var = match.group(1)
            default_value = (
                match.group(2) if match.group(2) is not None else match.group(0)
            )
            return os.getenv(env_var, default_value)

        return re.sub(pattern, replace_env, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split(".")
        current = self._config_data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def get_provider(self, name: str) -> dict[str, Any]:
        """Get provider configuration dictionary"""
        provider_config = self.get(f"providers.{name}", {})
        if not isinstance(provider_config, dict):
            return {}
        return provider_config

    def get_system_settings(self) -> dict[str, Any]:
        """Get system settings dictionary"""
        system_settings = self.get("system", {})
        if not isinstance(system_settings, dict):
            return {}
        return system_settings

    def to_dict(self) -> dict[str, Any]:
        """Return configuration as dictionary"""
        return self._config_data.copy()

    @classmethod
    def load(cls, config_path: str | None = None) -> "Config":
        """Class method to load config (for compatibility)"""
        return cls(config_path)
