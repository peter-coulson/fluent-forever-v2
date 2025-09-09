"""
Configuration Manager for Fluent Forever V2

Provides hierarchical configuration loading with environment overrides.
"""

import copy
import json
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ConfigLevel(Enum):
    """Configuration level priority"""

    SYSTEM = "system"
    PIPELINE = "pipeline"
    PROVIDER = "provider"
    ENVIRONMENT = "environment"
    CLI = "cli"


@dataclass
class ConfigSource:
    """Configuration source information"""

    path: Path
    level: ConfigLevel
    priority: int  # Higher = more important


class ConfigManager:
    """Hierarchical configuration management"""

    def __init__(self, base_path: Path | None = None):
        if base_path is None:
            # Auto-detect project root by looking for config.json
            current_path = Path(__file__).parent
            while current_path.parent != current_path:
                if (current_path / "config.json").exists():
                    base_path = current_path
                    break
                current_path = current_path.parent
            else:
                # Fallback to two levels up from this file
                base_path = Path(__file__).parents[2]

        self.base_path = Path(base_path)
        self.config_cache: dict[str, dict[str, Any]] = {}
        self.sources: list[ConfigSource] = []

    def load_config(
        self, config_type: str = "system", name: str | None = None
    ) -> dict[str, Any]:
        """Load configuration with hierarchy resolution"""
        cache_key = f"{config_type}:{name or 'default'}"

        if cache_key in self.config_cache:
            return self.config_cache[cache_key]

        config = self._merge_configurations(config_type, name)
        self.config_cache[cache_key] = config
        return config

    def get_pipeline_config(self, pipeline_name: str) -> dict[str, Any]:
        """Get pipeline-specific configuration"""
        return self.load_config("pipeline", pipeline_name)

    def get_provider_config(self, provider_name: str) -> dict[str, Any]:
        """Get provider-specific configuration"""
        return self.load_config("provider", provider_name)

    def validate_config(self) -> bool:
        """Validate the loaded configuration"""
        try:
            # Load system config to test basic loading
            system_config = self.load_config("system")

            # Check for required system sections
            required_sections = ["system", "paths"]
            return all(section in system_config for section in required_sections)
        except Exception:
            return False

    def resolve_environment_variables(self, config: dict[str, Any]) -> dict[str, Any]:
        """Resolve environment variables in configuration"""
        resolved = copy.deepcopy(config)
        self._resolve_env_vars_recursive(resolved)
        return resolved

    def _resolve_env_vars_recursive(self, obj: Any) -> None:
        """Recursively resolve environment variables"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if (
                    isinstance(value, str)
                    and value.startswith("${")
                    and value.endswith("}")
                ):
                    env_var = value[2:-1]
                    obj[key] = os.getenv(env_var, value)
                elif isinstance(value, dict | list):
                    self._resolve_env_vars_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                self._resolve_env_vars_recursive(item)

    def _merge_configurations(
        self, config_type: str, name: str | None
    ) -> dict[str, Any]:
        """Merge configurations from all applicable sources"""
        merged_config: dict[str, Any] = {}

        # Load in priority order (lower priority first)
        sources = self._get_config_sources(config_type, name)

        for source in sorted(sources, key=lambda s: s.priority):
            if source.path.exists():
                try:
                    source_config = json.loads(source.path.read_text())
                    merged_config = self._deep_merge(merged_config, source_config)
                except (OSError, json.JSONDecodeError) as e:
                    print(f"Warning: Failed to load {source.path}: {e}")

        # For system config, also load all pipeline and provider configs to consolidate
        if config_type == "system":
            # Load all pipeline configs
            pipelines_dir = self.base_path / "config" / "pipelines"
            if pipelines_dir.exists():
                pipelines = {}
                for pipeline_file in pipelines_dir.glob("*.json"):
                    if pipeline_file.name.startswith("_"):
                        continue
                    try:
                        pipeline_config = json.loads(pipeline_file.read_text())
                        pipelines[pipeline_file.stem] = pipeline_config
                    except (OSError, json.JSONDecodeError):
                        continue
                if pipelines:
                    merged_config["pipelines"] = pipelines

            # Load all provider configs
            providers_dir = self.base_path / "config" / "providers"
            if providers_dir.exists():
                providers = {}
                for provider_file in providers_dir.glob("*.json"):
                    if provider_file.name.startswith("_"):
                        continue
                    try:
                        provider_config = json.loads(provider_file.read_text())
                        providers[provider_file.stem] = provider_config
                    except (OSError, json.JSONDecodeError):
                        continue
                if providers:
                    merged_config["providers"] = providers

            # Load stages config (empty for now but structure)
            merged_config["stages"] = {}

        # Apply environment variable overrides
        self._apply_env_overrides(merged_config)

        return merged_config

    def _get_config_sources(
        self, config_type: str, name: str | None
    ) -> list[ConfigSource]:
        """Get all applicable configuration sources"""
        sources = []

        # Core system config (lowest priority)
        core_path = self.base_path / "config" / "core.json"
        sources.append(ConfigSource(core_path, ConfigLevel.SYSTEM, 1))

        # Type-specific config
        if config_type == "pipeline" and name:
            pipeline_path = self.base_path / "config" / "pipelines" / f"{name}.json"
            sources.append(ConfigSource(pipeline_path, ConfigLevel.PIPELINE, 2))
        elif config_type == "provider" and name:
            provider_path = self.base_path / "config" / "providers" / f"{name}.json"
            sources.append(ConfigSource(provider_path, ConfigLevel.PROVIDER, 2))
        elif config_type == "cli":
            cli_path = self.base_path / "config" / "cli" / "defaults.json"
            sources.append(ConfigSource(cli_path, ConfigLevel.CLI, 2))

        # Environment-specific overrides (high priority, but not highest)
        env = os.getenv("FLUENT_ENV", "development")
        env_path = self.base_path / "config" / "environments" / f"{env}.json"
        sources.append(ConfigSource(env_path, ConfigLevel.ENVIRONMENT, 3))

        return sources

    def _deep_merge(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: dict[str, Any]) -> None:
        """Apply environment variable overrides with highest priority"""
        # Look for FF_ prefixed environment variables
        for env_key, env_value in os.environ.items():
            if env_key.startswith("FF_"):
                # Convert FF_SYSTEM_LOG_LEVEL -> system_log_level for proper nesting
                config_key = env_key[3:].lower()  # Remove FF_ and lowercase
                self._set_nested_config(config, config_key, env_value)

    def _set_nested_config(
        self, config: dict[str, Any], key_path: str, value: str
    ) -> None:
        """Set nested configuration value from underscore notation"""
        # Convert underscores to nested structure
        # system_log_level -> ['system', 'log_level']
        parts = key_path.split("_")

        # Special handling for known patterns
        if len(parts) >= 2:
            # Handle system_log_level pattern
            if parts[0] == "system" and len(parts) > 2:
                # system_log_level -> system.log_level
                section = parts[0]
                field = "_".join(parts[1:])
                keys = [section, field]
            elif len(parts) == 2:
                # Two parts: section_field
                keys = parts
            else:
                # Multiple parts: treat as nested
                keys = parts
        else:
            keys = [key_path]

        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # If it exists but isn't a dict, make it a dict
                current[key] = {}
            current = current[key]

        # Try to parse value as JSON, fall back to string
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value

        current[keys[-1]] = parsed_value

    def clear_cache(self) -> None:
        """Clear configuration cache"""
        self.config_cache.clear()


# Global configuration manager
_global_config_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager
