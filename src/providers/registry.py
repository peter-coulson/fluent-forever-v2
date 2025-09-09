"""
Provider Registry

Registry system for managing provider instances and creating provider factories.
"""

from pathlib import Path
from typing import Any

from .base.data_provider import DataProvider
from .base.media_provider import MediaProvider
from .base.sync_provider import SyncProvider


class ProviderRegistry:
    """Registry for provider instances"""

    def __init__(self):
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


# Global registry instance
_global_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry

    Returns:
        Global ProviderRegistry instance
    """
    return _global_provider_registry


# Factory Classes for Provider Creation
class DataProviderFactory:
    """Factory for creating data providers"""

    def __init__(self, config: dict | None = None):
        """Initialize factory with configuration

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def create_json_provider(self, base_path: Path) -> DataProvider:
        """Create JSON data provider

        Args:
            base_path: Base directory for JSON files

        Returns:
            JSONDataProvider instance
        """
        from .data.json_provider import JSONDataProvider

        return JSONDataProvider(base_path)

    def create_memory_provider(self) -> DataProvider:
        """Create memory data provider

        Returns:
            MemoryDataProvider instance
        """
        from .data.memory_provider import MemoryDataProvider

        return MemoryDataProvider()


class MediaProviderFactory:
    """Factory for creating media providers"""

    def __init__(self, config: dict | None = None):
        """Initialize factory with configuration

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def create_provider(self, provider_name: str, **kwargs) -> MediaProvider | None:
        """Create media provider by name

        Args:
            provider_name: Name of provider ('openai', 'runware', 'forvo', 'mock')
            **kwargs: Additional arguments for provider constructor

        Returns:
            MediaProvider instance if successful, None otherwise
        """
        if provider_name.lower() == "openai":
            return self.create_openai_provider(**kwargs)
        elif provider_name.lower() == "runware":
            return self.create_runware_provider(**kwargs)
        elif provider_name.lower() == "forvo":
            return self.create_forvo_provider(**kwargs)
        elif provider_name.lower() == "mock":
            return self.create_mock_provider(**kwargs)
        else:
            return None

    def create_openai_provider(self, api_key: str | None = None) -> MediaProvider:
        """Create OpenAI media provider

        Args:
            api_key: Optional API key

        Returns:
            OpenAIMediaProvider instance
        """
        from .media.openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=api_key, config=self.config)

    def create_runware_provider(self, api_key: str | None = None) -> MediaProvider:
        """Create Runware media provider

        Args:
            api_key: Optional API key

        Returns:
            RunwareMediaProvider instance
        """
        from .media.runware_provider import RunwareProvider

        return RunwareProvider(api_key=api_key, config=self.config)

    def create_forvo_provider(self, api_key: str | None = None) -> MediaProvider:
        """Create Forvo media provider

        Args:
            api_key: Optional API key

        Returns:
            ForvoMediaProvider instance
        """
        from .media.forvo_provider import ForvoProvider

        return ForvoProvider(api_key=api_key, config=self.config)

    def create_mock_provider(
        self, supported_types: list[str] | None = None, should_fail: bool = False
    ) -> MediaProvider:
        """Create mock media provider

        Args:
            supported_types: List of supported media types
            should_fail: Whether provider should simulate failures

        Returns:
            MockMediaProvider instance
        """
        from .media.mock_provider import MockMediaProvider

        return MockMediaProvider(
            supported_types=supported_types, should_fail=should_fail
        )

    def create_provider_with_fallback(
        self, config: dict[str, Any]
    ) -> MediaProvider | None:
        """Create media provider with fallback configuration

        Args:
            config: Configuration with 'primary' and 'fallback' providers

        Returns:
            Primary provider if successful, otherwise first working fallback
        """
        primary = config.get("primary")
        fallbacks = config.get("fallback", [])

        # Try primary provider first
        if primary:
            try:
                provider = self.create_provider(primary)
                if provider:
                    return provider
            except Exception:
                pass

        # Try fallback providers
        for fallback_name in fallbacks:
            try:
                provider = self.create_provider(fallback_name)
                if provider:
                    return provider
            except Exception:
                continue

        return None

    def get_primary_provider(self) -> MediaProvider | None:
        """Get primary provider from configuration

        Returns:
            Primary MediaProvider based on config
        """
        image_config = self.config.get("image_generation", {})
        primary_provider = image_config.get("primary_provider", "openai")
        return self.create_provider(primary_provider)


class SyncProviderFactory:
    """Factory for creating sync providers"""

    def __init__(self, config: dict | None = None):
        """Initialize factory with configuration

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def create_anki_provider(self) -> SyncProvider:
        """Create Anki sync provider

        Returns:
            AnkiSyncProvider instance
        """
        from .sync.anki_provider import AnkiProvider

        return AnkiProvider()

    def create_mock_provider(
        self, provider_name: str = "anki", should_fail: bool = False
    ) -> SyncProvider:
        """Create mock sync provider

        Args:
            provider_name: Name of provider being mocked
            should_fail: Whether provider should simulate failures

        Returns:
            MockSyncProvider instance
        """
        from .sync.mock_provider import MockSyncProvider

        return MockSyncProvider(should_fail=should_fail)
