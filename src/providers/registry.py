"""
Provider Registry

Registry system for managing provider instances and creating provider factories.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from src.utils.logging_config import ICONS, get_logger, log_performance

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
        self._provider_pipeline_assignments: dict[str, list[str]] = {}
        self._data_provider_configs: dict[str, dict[str, Any]] = {}
        self.logger = get_logger("providers.registry")

    # Data Provider Methods
    def register_data_provider(
        self, name: str, provider: DataProvider, config: dict[str, Any] | None = None
    ) -> None:
        """Register a data provider

        Args:
            name: Provider name
            provider: DataProvider instance
            config: Optional provider configuration for file conflict validation
        """
        self._data_providers[name] = provider
        if config:
            self._data_provider_configs[name] = config
            self._validate_file_conflicts()

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
        self._provider_pipeline_assignments.clear()
        self._data_provider_configs.clear()

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

    # Pipeline Assignment Methods
    def set_pipeline_assignments(
        self, provider_type: str, provider_name: str, pipelines: list[str]
    ) -> None:
        """Set pipeline assignments for a provider.

        Args:
            provider_type: Type of provider ("data", "audio", "image", "sync")
            provider_name: Name of the provider
            pipelines: List of pipeline names or ["*"] for all pipelines
        """
        key = f"{provider_type}:{provider_name}"
        self._provider_pipeline_assignments[key] = pipelines

    def get_pipeline_assignments(
        self, provider_type: str, provider_name: str
    ) -> list[str]:
        """Get pipeline assignments for a provider.

        Args:
            provider_type: Type of provider ("data", "audio", "image", "sync")
            provider_name: Name of the provider

        Returns:
            List of pipeline names or ["*"] for universal access (default)
        """
        key = f"{provider_type}:{provider_name}"
        return self._provider_pipeline_assignments.get(key, ["*"])

    def get_providers_for_pipeline(
        self, pipeline_name: str
    ) -> dict[str, dict[str, Any]]:
        """Return filtered providers dict for specific pipeline.

        Args:
            pipeline_name: Name of the pipeline requesting providers

        Returns:
            Dictionary with filtered providers for each type
        """
        return {
            "data": self._get_filtered_data_providers(pipeline_name),
            "audio": self._get_filtered_audio_providers(pipeline_name),
            "image": self._get_filtered_image_providers(pipeline_name),
            "sync": self._get_filtered_sync_providers(pipeline_name),
        }

    def _get_filtered_data_providers(
        self, pipeline_name: str
    ) -> dict[str, DataProvider]:
        """Filter data providers by pipeline assignment."""
        filtered = {}
        for name, provider in self._data_providers.items():
            assignments = self.get_pipeline_assignments("data", name)
            if "*" in assignments or pipeline_name in assignments:
                filtered[name] = provider
        return filtered

    def _get_filtered_audio_providers(
        self, pipeline_name: str
    ) -> dict[str, MediaProvider]:
        """Filter audio providers by pipeline assignment."""
        filtered = {}
        for name, provider in self._audio_providers.items():
            assignments = self.get_pipeline_assignments("audio", name)
            if "*" in assignments or pipeline_name in assignments:
                filtered[name] = provider
        return filtered

    def _get_filtered_image_providers(
        self, pipeline_name: str
    ) -> dict[str, MediaProvider]:
        """Filter image providers by pipeline assignment."""
        filtered = {}
        for name, provider in self._image_providers.items():
            assignments = self.get_pipeline_assignments("image", name)
            if "*" in assignments or pipeline_name in assignments:
                filtered[name] = provider
        return filtered

    def _get_filtered_sync_providers(
        self, pipeline_name: str
    ) -> dict[str, SyncProvider]:
        """Filter sync providers by pipeline assignment."""
        filtered = {}
        for name, provider in self._sync_providers.items():
            assignments = self.get_pipeline_assignments("sync", name)
            if "*" in assignments or pipeline_name in assignments:
                filtered[name] = provider
        return filtered

    def _validate_file_conflicts(self) -> None:
        """Validate that no files are managed by multiple data providers

        Raises:
            ValueError: If file conflicts are detected
        """
        file_assignments: dict[str, str] = {}
        conflicts: list[str] = []

        for provider_name, config in self._data_provider_configs.items():
            managed_files = config.get("files", [])
            if not managed_files:  # Skip providers that manage all files
                continue

            for file_id in managed_files:
                if file_id in file_assignments:
                    conflicts.append(
                        f"File '{file_id}' managed by both '{file_assignments[file_id]}' and '{provider_name}'"
                    )
                else:
                    file_assignments[file_id] = provider_name

        if conflicts:
            raise ValueError(f"File conflicts detected: {'; '.join(conflicts)}")

    @classmethod
    @log_performance("fluent_forever.providers.registry")
    def from_config(cls, config: "Config") -> "ProviderRegistry":
        """Create and populate registry from configuration

        Args:
            config: Config instance with provider configuration

        Returns:
            ProviderRegistry instance with providers initialized

        Raises:
            ValueError: If configuration uses old format or is invalid
        """
        logger = get_logger("providers.registry")
        logger.info(f"{ICONS['gear']} Initializing providers from configuration...")

        registry = cls()

        # Get providers config - must exist
        providers_config = config.get("providers", {})
        if not providers_config:
            raise ValueError(
                "No providers configuration found. Please add 'providers' section to your configuration."
            )

        # Check for old configuration format and fail with helpful message
        for provider_type, provider_config in providers_config.items():
            if (
                provider_type in ["data", "audio", "image", "sync"]
                and isinstance(provider_config, dict)
                and "type" in provider_config
            ):  # Old format detection
                raise ValueError(
                    f"Configuration uses old format for '{provider_type}' provider. "
                    f"Please update to use named provider format: "
                    f"'{provider_type}': {{'provider_name': {{'type': 'provider_type', 'pipelines': ['pipeline1']}}}}"
                )

        # Initialize data providers
        logger.info(f"{ICONS['gear']} Setting up data providers...")
        data_configs = providers_config.get("data", {})
        if data_configs:
            for provider_name, data_config in data_configs.items():
                if "pipelines" not in data_config:
                    raise ValueError(
                        f"Provider '{provider_name}' is missing required 'pipelines' field"
                    )

                provider_type = data_config.get("type", "json")
                pipelines = data_config.get("pipelines", [])
                files = data_config.get("files", [])
                read_only = data_config.get("read_only", False)

                if provider_type == "json":
                    from .data.json_provider import JSONDataProvider

                    base_path = Path(data_config.get("base_path", "."))
                    provider = JSONDataProvider(
                        base_path, read_only=read_only, managed_files=files
                    )

                    registry.register_data_provider(
                        provider_name,
                        provider,
                        config={"files": files, "read_only": read_only},
                    )
                    registry.set_pipeline_assignments("data", provider_name, pipelines)
                    logger.info(
                        f"{ICONS['check']} Registered JSON data provider '{provider_name}' "
                        f"for pipelines {pipelines} (read_only={read_only}, files={files})"
                    )
                else:
                    raise ValueError(f"Unsupported data provider type: {provider_type}")
        else:
            # Create default data provider if none configured
            from .data.json_provider import JSONDataProvider

            registry.register_data_provider("default", JSONDataProvider(Path(".")))
            registry.set_pipeline_assignments("data", "default", ["*"])
            logger.info(
                f"{ICONS['check']} Registered default JSON data provider for all pipelines"
            )

        # Initialize audio providers (optional)
        logger.info(f"{ICONS['gear']} Setting up audio providers...")
        audio_configs = providers_config.get("audio", {})
        for provider_name, audio_config in audio_configs.items():
            if "pipelines" not in audio_config:
                raise ValueError(
                    f"Provider '{provider_name}' is missing required 'pipelines' field"
                )

            audio_type = audio_config.get("type", "forvo")
            pipelines = audio_config.get("pipelines", [])

            if audio_type == "forvo":
                from .audio.forvo_provider import ForvoProvider

                registry.register_audio_provider(provider_name, ForvoProvider())
                registry.set_pipeline_assignments("audio", provider_name, pipelines)
                logger.info(
                    f"{ICONS['check']} Registered {audio_type} audio provider '{provider_name}' for pipelines {pipelines}"
                )
            else:
                raise ValueError(
                    f"Unsupported audio provider type: {audio_type}. Supported: 'forvo'"
                )

        if not audio_configs:
            logger.info(f"{ICONS['info']} No audio providers configured")

        # Initialize image providers (optional)
        logger.info(f"{ICONS['gear']} Setting up image providers...")
        image_configs = providers_config.get("image", {})
        for provider_name, image_config in image_configs.items():
            if "pipelines" not in image_config:
                raise ValueError(
                    f"Provider '{provider_name}' is missing required 'pipelines' field"
                )

            image_type = image_config.get("type", "runware")
            pipelines = image_config.get("pipelines", [])

            if image_type == "runware":
                from .image.runware_provider import RunwareProvider

                registry.register_image_provider(provider_name, RunwareProvider())
                registry.set_pipeline_assignments("image", provider_name, pipelines)
                logger.info(
                    f"{ICONS['check']} Registered {image_type} image provider '{provider_name}' for pipelines {pipelines}"
                )
            elif image_type == "openai":
                from .image.openai_provider import OpenAIProvider

                registry.register_image_provider(provider_name, OpenAIProvider())
                registry.set_pipeline_assignments("image", provider_name, pipelines)
                logger.info(
                    f"{ICONS['check']} Registered {image_type} image provider '{provider_name}' for pipelines {pipelines}"
                )
            else:
                raise ValueError(
                    f"Unsupported image provider type: {image_type}. Supported: 'runware', 'openai'"
                )

        if not image_configs:
            logger.info(f"{ICONS['info']} No image providers configured")

        # Initialize sync providers (required)
        logger.info(f"{ICONS['gear']} Setting up sync providers...")
        sync_configs = providers_config.get("sync", {})
        if not sync_configs:
            # Create default sync provider if none configured
            from .sync.anki_provider import AnkiProvider

            registry.register_sync_provider("default", AnkiProvider())
            registry.set_pipeline_assignments("sync", "default", ["*"])
            logger.info(
                f"{ICONS['check']} Registered default anki sync provider for all pipelines"
            )
        else:
            for provider_name, sync_config in sync_configs.items():
                if "pipelines" not in sync_config:
                    raise ValueError(
                        f"Provider '{provider_name}' is missing required 'pipelines' field"
                    )

                sync_type = sync_config.get("type", "anki")
                pipelines = sync_config.get("pipelines", [])

                if sync_type == "anki":
                    from .sync.anki_provider import AnkiProvider

                    registry.register_sync_provider(provider_name, AnkiProvider())
                    registry.set_pipeline_assignments("sync", provider_name, pipelines)
                    logger.info(
                        f"{ICONS['check']} Registered {sync_type} sync provider '{provider_name}' for pipelines {pipelines}"
                    )
                else:
                    raise ValueError(
                        f"Unsupported sync provider type: {sync_type}. Only 'anki' is supported."
                    )

        logger.info(f"{ICONS['check']} All providers initialized successfully")
        return registry


# Global registry instance
_global_provider_registry = ProviderRegistry()


def get_provider_registry() -> ProviderRegistry:
    """Get the global provider registry

    Returns:
        Global ProviderRegistry instance
    """
    return _global_provider_registry
