"""
Provider Context Helper

Utilities for integrating providers with the stage system.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from core.context import PipelineContext
from .registry import (
    MediaProviderFactory, 
    DataProviderFactory, 
    SyncProviderFactory,
    get_provider_registry
)
from utils.logging_config import get_logger, ICONS

logger = get_logger('providers.context_helper')


def setup_providers_in_context(context: PipelineContext, config: Optional[Dict] = None) -> None:
    """Setup default providers in pipeline context
    
    Args:
        context: Pipeline context to add providers to
        config: Optional configuration dictionary
    """
    if config is None:
        config = _load_default_config()
    
    try:
        # Create factories
        media_factory = MediaProviderFactory(config)
        data_factory = DataProviderFactory(config)
        sync_factory = SyncProviderFactory(config)
        
        # Set up data providers
        _setup_data_providers(context, data_factory, config)
        
        # Set up media providers
        _setup_media_providers(context, media_factory, config)
        
        # Set up sync providers
        _setup_sync_providers(context, sync_factory, config)
        
        logger.info(f"{ICONS['check']} Provider setup completed for pipeline context")
        
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to setup providers: {e}")
        raise


def _setup_data_providers(context: PipelineContext, factory: DataProviderFactory, config: Dict) -> None:
    """Setup data providers in context"""
    # Default JSON provider for project data
    project_root = context.get('project_root', Path.cwd())
    json_provider = factory.create_json_provider(project_root)
    
    context.set('providers.data', json_provider)
    context.set('providers.vocabulary_data', json_provider)
    context.set('providers.staging_data', json_provider)
    
    # Memory provider for testing
    memory_provider = factory.create_memory_provider()
    context.set('providers.memory_data', memory_provider)


def _setup_media_providers(context: PipelineContext, factory: MediaProviderFactory, config: Dict) -> None:
    """Setup media providers in context"""
    # Get primary image provider from config
    image_config = config.get('image_generation', {})
    primary_provider = image_config.get('primary_provider', 'openai')
    
    # Create primary provider
    try:
        primary_media_provider = factory.create_provider(primary_provider)
        if primary_media_provider:
            context.set('providers.media', primary_media_provider)
            context.set('providers.image', primary_media_provider)
            logger.info(f"{ICONS['check']} Primary media provider: {primary_provider}")
        else:
            logger.warning(f"{ICONS['warning']} Failed to create primary media provider: {primary_provider}")
    except Exception as e:
        logger.warning(f"{ICONS['warning']} Error creating {primary_provider}: {e}")
    
    # Create audio provider (Forvo)
    try:
        audio_provider = factory.create_forvo_provider()
        context.set('providers.audio', audio_provider)
        logger.info(f"{ICONS['check']} Audio provider: Forvo")
    except Exception as e:
        logger.warning(f"{ICONS['warning']} Error creating Forvo provider: {e}")
    
    # Create fallback providers
    _setup_fallback_providers(context, factory, primary_provider)
    
    # Always create mock provider for testing
    mock_provider = factory.create_mock_provider()
    context.set('providers.mock_media', mock_provider)


def _setup_fallback_providers(context: PipelineContext, factory: MediaProviderFactory, primary: str) -> None:
    """Setup fallback media providers"""
    fallback_providers = ['openai', 'runware']
    
    for provider_name in fallback_providers:
        if provider_name == primary:
            continue  # Skip primary provider
        
        try:
            provider = factory.create_provider(provider_name)
            if provider:
                context.set(f'providers.{provider_name}', provider)
                logger.debug(f"Fallback provider available: {provider_name}")
        except Exception as e:
            logger.debug(f"Fallback provider {provider_name} not available: {e}")


def _setup_sync_providers(context: PipelineContext, factory: SyncProviderFactory, config: Dict) -> None:
    """Setup sync providers in context"""
    # Anki provider
    try:
        anki_provider = factory.create_anki_provider()
        context.set('providers.sync', anki_provider)
        context.set('providers.anki', anki_provider)
        logger.info(f"{ICONS['check']} Sync provider: Anki")
    except Exception as e:
        logger.warning(f"{ICONS['warning']} Error creating Anki provider: {e}")
    
    # Mock sync provider for testing
    mock_sync = factory.create_mock_provider()
    context.set('providers.mock_sync', mock_sync)


def get_provider_from_context(context: PipelineContext, provider_type: str, provider_name: Optional[str] = None) -> Any:
    """Get provider from context
    
    Args:
        context: Pipeline context
        provider_type: Type of provider ('media', 'data', 'sync')
        provider_name: Specific provider name (optional)
        
    Returns:
        Provider instance or None if not found
    """
    if provider_name:
        key = f'providers.{provider_name}'
    else:
        key = f'providers.{provider_type}'
    
    return context.get(key)


def register_provider_in_context(context: PipelineContext, provider_key: str, provider: Any) -> None:
    """Register a provider in context
    
    Args:
        context: Pipeline context
        provider_key: Key for provider (without 'providers.' prefix)
        provider: Provider instance
    """
    full_key = f'providers.{provider_key}'
    context.set(full_key, provider)
    
    # Also register in global registry
    registry = get_provider_registry()
    
    # Determine provider type and register appropriately
    from .base.media_provider import MediaProvider
    from .base.data_provider import DataProvider
    from .base.sync_provider import SyncProvider
    
    if isinstance(provider, MediaProvider):
        registry.register_media_provider(provider_key, provider)
    elif isinstance(provider, DataProvider):
        registry.register_data_provider(provider_key, provider)
    elif isinstance(provider, SyncProvider):
        registry.register_sync_provider(provider_key, provider)


def _load_default_config() -> Dict[str, Any]:
    """Load default configuration"""
    try:
        import json
        config_path = Path(__file__).parent.parent.parent / 'config.json'
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning("config.json not found, using minimal defaults")
            return _get_minimal_config()
    except Exception as e:
        logger.warning(f"Error loading config: {e}, using minimal defaults")
        return _get_minimal_config()


def _get_minimal_config() -> Dict[str, Any]:
    """Get minimal default configuration"""
    return {
        'apis': {
            'openai': {'env_var': 'OPENAI_API_KEY'},
            'runware': {'env_var': 'RUNWARE_API_KEY'},
            'forvo': {'env_var': 'FORVO_API_KEY'},
        },
        'image_generation': {
            'primary_provider': 'openai'
        }
    }