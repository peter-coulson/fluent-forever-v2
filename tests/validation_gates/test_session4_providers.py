#!/usr/bin/env python3
"""
Validation gate for Session 4: Provider System

Tests that external APIs can be abstracted and providers can be switched.
This test will initially fail until Session 4 is implemented.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_provider_system():
    """
    Validation gate for Session 4: Provider System
    
    Tests:
    - Providers can be created and registered
    - Provider abstraction works
    - Providers can be switched dynamically
    """
    try:
        from providers.media import MediaProviderFactory
        from providers.data import DataProviderFactory
    except ImportError:
        pytest.skip("Provider system not yet implemented (Session 4 pending)")
    
    # Test media provider factory
    media_factory = MediaProviderFactory()
    assert media_factory is not None, "MediaProviderFactory should be creatable"
    
    # Test provider creation
    openai_provider = media_factory.create_provider("openai")
    runware_provider = media_factory.create_provider("runware")
    
    assert openai_provider is not None, "OpenAI provider should be creatable"
    assert runware_provider is not None, "Runware provider should be creatable"
    
    # Test provider abstraction - both should have same interface
    assert hasattr(openai_provider, 'generate_image'), "Provider should have generate_image method"
    assert hasattr(runware_provider, 'generate_image'), "Provider should have generate_image method"


def test_provider_failover():
    """Test that provider system supports failover."""
    try:
        from providers.media import MediaProviderFactory
    except ImportError:
        pytest.skip("Provider system not yet implemented (Session 4 pending)")
    
    factory = MediaProviderFactory()
    
    # Test fallback configuration
    config = {
        "primary": "openai",
        "fallback": ["runware"]
    }
    
    provider = factory.create_provider_with_fallback(config)
    assert provider is not None, "Provider with fallback should be creatable"


def test_provider_mocking():
    """Test that providers can be mocked for testing."""
    try:
        from providers.media import MediaProviderFactory
        from providers.sync import SyncProviderFactory
    except ImportError:
        pytest.skip("Provider system not yet implemented (Session 4 pending)")
    
    # Test mock provider creation
    media_factory = MediaProviderFactory()
    mock_provider = media_factory.create_mock_provider()
    
    assert mock_provider is not None, "Mock provider should be creatable"
    
    # Test sync provider mocking (for AnkiConnect)
    sync_factory = SyncProviderFactory()
    mock_anki = sync_factory.create_mock_provider("anki")
    
    assert mock_anki is not None, "Mock Anki provider should be creatable"
    assert hasattr(mock_anki, 'test_connection'), "Mock should have expected methods"


def test_provider_configuration():
    """Test that providers can be configured from config.json."""
    try:
        from providers.media import MediaProviderFactory
    except ImportError:
        pytest.skip("Provider system not yet implemented (Session 4 pending)")
    
    # Test loading providers from configuration
    config = {
        "image_generation": {
            "primary_provider": "runware",
            "providers": {
                "openai": {"model": "dall-e-3"},
                "runware": {"model": "runware:101@1"}
            }
        }
    }
    
    factory = MediaProviderFactory(config=config)
    primary_provider = factory.get_primary_provider()
    
    assert primary_provider is not None, "Primary provider should be available"


if __name__ == "__main__":
    test_provider_system()
    test_provider_failover()
    test_provider_mocking()
    test_provider_configuration()
    print("Session 4 validation gate passed!")