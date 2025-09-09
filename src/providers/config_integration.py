"""
Provider Configuration Integration

Initializes providers from unified configuration system.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.providers.media.runware_provider import (
        RunwareProvider as RunwareProviderType,
    )

from src.core.config import ConfigManager, get_config_manager
from src.providers.registry import get_provider_registry


def initialize_providers_from_config() -> None:
    """Initialize all providers from configuration"""
    config_manager = ConfigManager()
    provider_registry = get_provider_registry()

    # Load provider configurations
    try:
        openai_config = config_manager.get_provider_config("openai")
        forvo_config = config_manager.get_provider_config("forvo")
        anki_config = config_manager.get_provider_config("anki")
        runware_config = config_manager.get_provider_config("runware")
    except Exception as e:
        print(f"Warning: Failed to load provider configs: {e}")
        # Fall back to legacy config
        system_config = config_manager.load_config("system")
        legacy_apis = system_config.get("apis", {})
        openai_config = {"provider": legacy_apis.get("openai", {})}
        forvo_config = {"provider": legacy_apis.get("forvo", {})}
        anki_config = {"provider": legacy_apis.get("anki", {})}
        runware_config = {"provider": legacy_apis.get("runware", {})}

    # Create and register providers
    from src.providers.data.json_provider import JSONDataProvider
    from src.providers.media.forvo_provider import ForvoProvider
    from src.providers.media.openai_provider import OpenAIProvider
    from src.providers.sync.anki_provider import AnkiProvider

    RunwareProviderClass: type[RunwareProviderType] | None
    try:
        from src.providers.media.runware_provider import RunwareProvider

        RunwareProviderClass = RunwareProvider
    except ImportError:
        print("Warning: Runware provider not available")
        RunwareProviderClass = None

    # Data provider
    system_config = config_manager.load_config("system")
    project_root = Path(config_manager.base_path)
    data_provider = JSONDataProvider(project_root)
    provider_registry.register_data_provider("default", data_provider)

    # Media providers
    if openai_config.get("provider", {}).get("enabled", True):
        try:
            openai_provider = OpenAIProvider()
            provider_registry.register_media_provider("openai", openai_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI provider: {e}")

    if RunwareProviderClass and runware_config.get("provider", {}).get("enabled", True):
        try:
            runware_provider = RunwareProviderClass()
            provider_registry.register_media_provider("runware", runware_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Runware provider: {e}")

    # Audio providers
    if forvo_config.get("provider", {}).get("enabled", True):
        try:
            forvo_provider = ForvoProvider()
            provider_registry.register_media_provider("forvo", forvo_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Forvo provider: {e}")

    # Sync providers
    if anki_config.get("provider", {}).get("enabled", True):
        try:
            anki_provider = AnkiProvider()
            provider_registry.register_sync_provider("anki", anki_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Anki provider: {e}")


def create_pipeline_from_config(pipeline_name: str) -> dict | None:
    """Create pipeline instance from configuration"""
    config_manager = get_config_manager()
    pipeline_config = config_manager.get_pipeline_config(pipeline_name)

    if pipeline_name == "vocabulary":
        # For now, return configuration - actual pipeline creation will be in Session 7
        return pipeline_config
    else:
        raise ValueError(f"Unknown pipeline: {pipeline_name}")
