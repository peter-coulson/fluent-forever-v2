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
        self._audio_providers: dict[str, MediaProvider] = {}
        self._image_providers: dict[str, MediaProvider] = {}
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

    # Audio Provider Methods
    def register_audio_provider(self, name: str, provider: MediaProvider) -> None:
        """Register an audio provider

        Args:
            name: Provider name
            provider: MediaProvider instance that supports audio
        """
        self._audio_providers[name] = provider

    def get_audio_provider(self, name: str) -> MediaProvider | None:
        """Get audio provider by name

        Args:
            name: Provider name

        Returns:
            MediaProvider instance if found, None otherwise
        """
        return self._audio_providers.get(name)

    def list_audio_providers(self) -> list[str]:
        """List all registered audio provider names"""
        return list(self._audio_providers.keys())

    # Image Provider Methods
    def register_image_provider(self, name: str, provider: MediaProvider) -> None:
        """Register an image provider

        Args:
            name: Provider name
            provider: MediaProvider instance that supports images
        """
        self._image_providers[name] = provider

    def get_image_provider(self, name: str) -> MediaProvider | None:
        """Get image provider by name

        Args:
            name: Provider name

        Returns:
            MediaProvider instance if found, None otherwise
        """
        return self._image_providers.get(name)

    def list_image_providers(self) -> list[str]:
        """List all registered image provider names"""
        return list(self._image_providers.keys())

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
        self._audio_providers.clear()
        self._image_providers.clear()
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
            "audio_providers": {
                "count": len(self._audio_providers),
                "names": list(self._audio_providers.keys()),
            },
            "image_providers": {
                "count": len(self._image_providers),
                "names": list(self._image_providers.keys()),
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

        # Initialize audio providers (optional)
        audio_config = config.get("providers.audio", {})
        if audio_config:  # Only create if configured
            audio_type = audio_config.get("type", "forvo")

            if audio_type == "forvo":
                from .audio.forvo_provider import ForvoProvider

                registry.register_audio_provider("default", ForvoProvider())
            else:
                raise ValueError(
                    f"Unsupported audio provider type: {audio_type}. Supported: 'forvo'"
                )

        # Initialize image providers (optional)
        image_config = config.get("providers.image", {})
        if image_config:  # Only create if configured
            image_type = image_config.get("type", "runware")

            if image_type == "runware":
                from .image.runware_provider import RunwareProvider

                registry.register_image_provider("default", RunwareProvider())
            elif image_type == "openai":
                from .image.openai_provider import OpenAIProvider

                registry.register_image_provider("default", OpenAIProvider())
            else:
                raise ValueError(
                    f"Unsupported image provider type: {image_type}. Supported: 'runware', 'openai'"
                )

        # Initialize sync providers
        sync_config = config.get("providers.sync", {})
        sync_type = sync_config.get("type", "anki")

        if sync_type == "anki":
            from .sync.anki_provider import AnkiProvider

            registry.register_sync_provider("default", AnkiProvider())
        else:
            raise ValueError(
                f"Unsupported sync provider type: {sync_type}. Only 'anki' is supported."
            )

        return registry


# Global registry instance
_global_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry

    Returns:
        Global ProviderRegistry instance
    """
    return _global_provider_registry
