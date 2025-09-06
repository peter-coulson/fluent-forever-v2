"""
Provider Configuration Integration

Initializes providers from unified configuration system.
"""

from pathlib import Path
from config.config_manager import get_config_manager
from providers.registry import get_provider_registry
import os


def initialize_providers_from_config() -> None:
    """Initialize all providers from configuration"""
    config_manager = get_config_manager()
    provider_registry = get_provider_registry()
    
    # Load provider configurations
    try:
        openai_config = config_manager.get_provider_config('openai')
        forvo_config = config_manager.get_provider_config('forvo')
        anki_config = config_manager.get_provider_config('anki')
        runware_config = config_manager.get_provider_config('runware')
    except Exception as e:
        print(f"Warning: Failed to load provider configs: {e}")
        # Fall back to legacy config
        system_config = config_manager.load_config('system')
        legacy_apis = system_config.get('apis', {})
        openai_config = {'provider': legacy_apis.get('openai', {})}
        forvo_config = {'provider': legacy_apis.get('forvo', {})}
        anki_config = {'provider': legacy_apis.get('anki', {})}
        runware_config = {'provider': legacy_apis.get('runware', {})}
    
    # Create and register providers
    from providers.media.openai_provider import OpenAIMediaProvider
    from providers.media.forvo_provider import ForvoMediaProvider  
    from providers.sync.anki_provider import AnkiSyncProvider
    from providers.data.json_provider import JSONDataProvider
    
    try:
        from providers.media.runware_provider import RunwareMediaProvider
    except ImportError:
        print("Warning: Runware provider not available")
        RunwareMediaProvider = None
    
    # Data provider
    system_config = config_manager.load_config('system')
    paths = system_config.get('paths', {})
    project_root = Path(config_manager.base_path)
    data_provider = JSONDataProvider(project_root)
    provider_registry.register_data_provider('default', data_provider)
    
    # Media providers
    if openai_config.get('provider', {}).get('enabled', True):
        try:
            openai_provider = OpenAIMediaProvider(
                api_key=os.getenv('OPENAI_API_KEY'),
                config=openai_config
            )
            provider_registry.register_media_provider('openai', openai_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI provider: {e}")
    
    if RunwareMediaProvider and runware_config.get('provider', {}).get('enabled', True):
        try:
            runware_provider = RunwareMediaProvider(
                api_key=os.getenv('RUNWARE_API_KEY'),
                config=runware_config
            )
            provider_registry.register_media_provider('runware', runware_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Runware provider: {e}")
    
    # Audio providers
    if forvo_config.get('provider', {}).get('enabled', True):
        try:
            forvo_provider = ForvoMediaProvider(
                api_key=os.getenv('FORVO_API_KEY'),
                config=forvo_config
            )
            provider_registry.register_media_provider('forvo', forvo_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Forvo provider: {e}")
    
    # Sync providers  
    if anki_config.get('provider', {}).get('enabled', True):
        try:
            anki_provider = AnkiSyncProvider(config=anki_config)
            provider_registry.register_sync_provider('anki', anki_provider)
        except Exception as e:
            print(f"Warning: Failed to initialize Anki provider: {e}")


def create_pipeline_from_config(pipeline_name: str):
    """Create pipeline instance from configuration"""
    config_manager = get_config_manager()
    pipeline_config = config_manager.get_pipeline_config(pipeline_name)
    
    if pipeline_name == 'vocabulary':
        # For now, return configuration - actual pipeline creation will be in Session 7
        return pipeline_config
    else:
        raise ValueError(f"Unknown pipeline: {pipeline_name}")