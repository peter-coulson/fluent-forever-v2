"""CLI configuration management."""

import json
from pathlib import Path
from typing import Any

from src.providers.registry import ProviderRegistry


class CLIConfig:
    """CLI configuration management."""

    def __init__(self, config_data: dict[str, Any]):
        """Initialize configuration.

        Args:
            config_data: Configuration dictionary
        """
        self.data = config_data

    @classmethod
    def load(cls, config_path: str | None = None) -> "CLIConfig":
        """Load configuration from file or defaults.

        Args:
            config_path: Optional path to config file

        Returns:
            CLIConfig instance
        """
        if config_path:
            path = Path(config_path)
            if path.exists():
                return cls(json.loads(path.read_text()))
        else:
            # Look for config in standard locations
            candidates = [
                Path.cwd() / "config.json",
                Path.home() / ".fluent-forever" / "config.json",
            ]
            for candidate in candidates:
                if candidate.exists():
                    return cls(json.loads(candidate.read_text()))

        # Return default configuration
        return cls(cls._default_config())

    @staticmethod
    def _default_config() -> dict[str, Any]:
        """Default CLI configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "providers": {
                "data": {"type": "json", "base_path": "."},
                "media": {"type": "openai"},
                "sync": {"type": "anki"},
            },
            "output": {"format": "table", "verbose": False, "use_colors": True},
            "cli": {"default_pipeline": "vocabulary", "default_port": 8000},
        }

    def initialize_providers(self, registry: ProviderRegistry) -> None:
        """Initialize providers from configuration.

        Args:
            registry: Provider registry to populate
        """
        providers_config = self.data.get("providers", {})

        # Initialize data providers
        data_config = providers_config.get("data", {})
        if data_config.get("type") == "json":
            from providers.data.json_provider import JSONDataProvider

            base_path = Path(data_config.get("base_path", "."))
            registry.register_data_provider("default", JSONDataProvider(base_path))

        # Initialize media providers
        media_config = providers_config.get("media", {})
        media_type = media_config.get("type", "openai")

        if media_type == "openai":
            from providers.media.openai_provider import OpenAIProvider

            try:
                provider = OpenAIProvider()
                registry.register_media_provider("default", provider)
            except Exception:
                # Fall back to mock provider if real one fails
                from providers.media.mock_provider import MockMediaProvider

                registry.register_media_provider("default", MockMediaProvider())
        else:
            # Default to mock provider
            from providers.media.mock_provider import MockMediaProvider

            registry.register_media_provider("default", MockMediaProvider())

        # Initialize sync providers
        sync_config = providers_config.get("sync", {})
        if sync_config.get("type") == "anki":
            from providers.sync.anki_provider import AnkiSyncProvider

            try:
                provider = AnkiSyncProvider()
                registry.register_sync_provider("default", provider)
            except Exception:
                # Fall back to mock provider if real one fails
                from providers.sync.mock_provider import MockSyncProvider

                registry.register_sync_provider("default", MockSyncProvider())
        else:
            from providers.sync.mock_provider import MockSyncProvider

            registry.register_sync_provider("default", MockSyncProvider())

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        data = self.data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return self.data.copy()

    def save(self, config_path: str) -> None:
        """Save configuration to file.

        Args:
            config_path: Path to save config file
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.data, indent=2))

    def is_verbose(self) -> bool:
        """Check if verbose output is enabled.

        Returns:
            True if verbose mode enabled
        """
        return self.get("output.verbose", False)

    def use_colors(self) -> bool:
        """Check if colored output is enabled.

        Returns:
            True if colors should be used
        """
        return self.get("output.use_colors", True)

    def get_default_pipeline(self) -> str:
        """Get default pipeline name.

        Returns:
            Default pipeline name
        """
        return self.get("cli.default_pipeline", "vocabulary")

    def get_default_port(self) -> int:
        """Get default preview server port.

        Returns:
            Default port number
        """
        return self.get("cli.default_port", 8000)
