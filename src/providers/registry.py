"""
Provider Registry

Registry system for managing provider instances and creating provider factories.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .base.data_provider import DataProvider

if TYPE_CHECKING:
    from src.core.config import Config
from .base.media_provider import MediaProvider
from .base.sync_provider import SyncProvider


class ProviderRegistry:
    """Registry for provider instances"""

    def __init__(self) -> None:
        self._data_providers: dict[str, DataProvider] = {}
        self._media_providers: dict[str, MediaProvider] = {}
        self._sync_providers: dict[str, SyncProvider] = {}

    # Data Provider Methods
    def register_data_provider(self, name: str, provider: DataProvider) -> None:
        """Register a data provider

        Args:
            name: Provider name
            provider: DataProvider instance
        """
        self._data_providers[name] = provider

    def get_data_provider(self, name: str) -> DataProvider | None:
        """Get data provider by name

        Args:
            name: Provider name

        Returns:
            DataProvider instance if found, None otherwise
        """
        return self._data_providers.get(name)

    def list_data_providers(self) -> list[str]:
        """List all registered data provider names"""
        return list(self._data_providers.keys())

    # Media Provider Methods
    def register_media_provider(self, name: str, provider: MediaProvider) -> None:
        """Register a media provider

        Args:
            name: Provider name
            provider: MediaProvider instance
        """
        self._media_providers[name] = provider

    def get_media_provider(self, name: str) -> MediaProvider | None:
        """Get media provider by name

        Args:
            name: Provider name

        Returns:
            MediaProvider instance if found, None otherwise
        """
        return self._media_providers.get(name)

    def list_media_providers(self) -> list[str]:
        """List all registered media provider names"""
        return list(self._media_providers.keys())

    def get_media_providers_by_type(self, media_type: str) -> list[MediaProvider]:
        """Get all media providers that support a specific media type

        Args:
            media_type: Media type to filter by ('image', 'audio', etc.)

        Returns:
            List of MediaProvider instances that support the type
        """
        return [
            provider
            for provider in self._media_providers.values()
            if provider.supports_type(media_type)
        ]

    # Sync Provider Methods
    def register_sync_provider(self, name: str, provider: SyncProvider) -> None:
        """Register a sync provider

        Args:
            name: Provider name
            provider: SyncProvider instance
        """
        self._sync_providers[name] = provider

    def get_sync_provider(self, name: str) -> SyncProvider | None:
        """Get sync provider by name

        Args:
            name: Provider name

        Returns:
            SyncProvider instance if found, None otherwise
        """
        return self._sync_providers.get(name)

    def list_sync_providers(self) -> list[str]:
        """List all registered sync provider names"""
        return list(self._sync_providers.keys())

    # Utility Methods
    def clear_all(self) -> None:
        """Clear all registered providers"""
        self._data_providers.clear()
        self._media_providers.clear()
        self._sync_providers.clear()

    def get_provider_info(self) -> dict[str, Any]:
        """Get information about all registered providers

        Returns:
            Dictionary with provider counts and names
        """
        return {
            "data_providers": {
                "count": len(self._data_providers),
                "names": list(self._data_providers.keys()),
            },
            "media_providers": {
                "count": len(self._media_providers),
                "names": list(self._media_providers.keys()),
                "by_type": {
                    "image": [
                        name
                        for name, provider in self._media_providers.items()
                        if provider.supports_type("image")
                    ],
                    "audio": [
                        name
                        for name, provider in self._media_providers.items()
                        if provider.supports_type("audio")
                    ],
                },
            },
            "sync_providers": {
                "count": len(self._sync_providers),
                "names": list(self._sync_providers.keys()),
            },
        }

    @classmethod
    def from_config(cls, config: "Config") -> "ProviderRegistry":
        """Create and populate registry from configuration

        Args:
            config: Config instance with provider configuration

        Returns:
            ProviderRegistry instance with providers initialized
        """
        registry = cls()

        # Initialize data providers
        data_config = config.get("providers.data", {})
        if data_config.get("type") == "json":
            from .data.json_provider import JSONDataProvider

            base_path = Path(data_config.get("base_path", "."))
            registry.register_data_provider("default", JSONDataProvider(base_path))

        # Initialize media providers with fallback handling
        media_config = config.get("providers.media", {})
        media_type = media_config.get("type", "openai")

        if media_type == "openai":
            from .media.openai_provider import OpenAIProvider

            try:
                registry.register_media_provider("default", OpenAIProvider())
            except Exception:
                # Fallback to mock provider
                from .media.mock_provider import MockMediaProvider

                registry.register_media_provider("default", MockMediaProvider())
        else:
            # Default to mock provider
            from .media.mock_provider import MockMediaProvider

            registry.register_media_provider("default", MockMediaProvider())

        # Initialize sync providers with fallback handling
        sync_config = config.get("providers.sync", {})
        if sync_config.get("type") == "anki":
            from .sync.anki_provider import AnkiProvider

            try:
                registry.register_sync_provider("default", AnkiProvider())
            except Exception:
                # Fallback to mock provider
                from .sync.mock_provider import MockSyncProvider

                registry.register_sync_provider("default", MockSyncProvider())
        else:
            from .sync.mock_provider import MockSyncProvider

            registry.register_sync_provider("default", MockSyncProvider())

        return registry


# Global registry instance
_global_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry

    Returns:
        Global ProviderRegistry instance
    """
    return _global_provider_registry
