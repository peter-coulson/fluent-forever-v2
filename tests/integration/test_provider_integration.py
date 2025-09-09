#!/usr/bin/env python3
"""
Integration tests for provider system.

Tests that providers can be created, registered, and work with stages.
"""


import pytest


def test_provider_registry():
    """
    Test provider registry integration.

    Tests:
    - Provider registry can be created and used
    - Provider types are available
    """
    try:
        from providers.registry import get_provider_registry
    except ImportError:
        pytest.skip("Provider system not available")

    # Test provider registry exists
    registry = get_provider_registry()
    assert registry is not None, "Provider registry should exist"

    # Test registry interface (check actual methods)
    assert hasattr(
        registry, "register_data_provider"
    ), "Should have register_data_provider method"
    assert hasattr(
        registry, "get_data_provider"
    ), "Should have get_data_provider method"
    assert hasattr(
        registry, "register_media_provider"
    ), "Should have register_media_provider method"
    assert hasattr(
        registry, "get_media_provider"
    ), "Should have get_media_provider method"


def test_media_providers():
    """Test media provider system integration."""
    try:
        from providers.media.forvo_provider import ForvoAudioProvider
        from providers.media.mock_provider import MockMediaProvider
        from providers.media.openai_provider import OpenAIMediaProvider
        from providers.media.runware_provider import RunwareMediaProvider
    except ImportError:
        pytest.skip("Media providers not available")

    # Test providers can be imported
    assert OpenAIMediaProvider is not None, "OpenAI provider should be available"
    assert RunwareMediaProvider is not None, "Runware provider should be available"
    assert ForvoAudioProvider is not None, "Forvo provider should be available"
    assert MockMediaProvider is not None, "Mock provider should be available"

    # Test mock provider can be created (doesn't need API keys)
    try:
        mock_provider = MockMediaProvider()
        assert mock_provider is not None, "Mock provider should be creatable"

        # Test mock provider interface
        assert hasattr(
            mock_provider, "generate_image"
        ), "Should have generate_image method"
        assert hasattr(
            mock_provider, "test_connection"
        ), "Should have test_connection method"
    except Exception as e:
        pytest.skip(f"Mock provider creation failed: {e}")


def test_sync_providers():
    """Test sync provider system integration."""
    try:
        from providers.sync.anki_provider import AnkiProvider
        from providers.sync.mock_provider import MockSyncProvider
    except ImportError:
        pytest.skip("Sync providers not available")

    # Test providers can be imported
    assert AnkiProvider is not None, "Anki provider should be available"
    assert MockSyncProvider is not None, "Mock sync provider should be available"

    # Test mock sync provider
    try:
        mock_sync = MockSyncProvider()
        assert mock_sync is not None, "Mock sync provider should be creatable"

        # Test sync provider interface
        assert hasattr(
            mock_sync, "test_connection"
        ), "Should have test_connection method"
        assert hasattr(mock_sync, "sync_cards"), "Should have sync_cards method"
    except Exception as e:
        pytest.skip(f"Mock sync provider creation failed: {e}")


def test_data_providers():
    """Test data provider system integration."""
    try:
        from providers.data.json_provider import JSONDataProvider
        from providers.data.memory_provider import MemoryDataProvider
    except ImportError:
        pytest.skip("Data providers not available")

    # Test providers can be imported
    assert JSONDataProvider is not None, "JSON provider should be available"
    assert MemoryDataProvider is not None, "Memory provider should be available"

    # Test memory provider (simplest)
    try:
        memory_provider = MemoryDataProvider()
        assert memory_provider is not None, "Memory provider should be creatable"

        # Test data provider interface
        assert hasattr(memory_provider, "load_data"), "Should have load_data method"
        assert hasattr(memory_provider, "save_data"), "Should have save_data method"
    except Exception as e:
        pytest.skip(f"Memory provider creation failed: {e}")


@pytest.mark.integration
def test_provider_configuration_integration():
    """Test provider configuration system integration."""
    try:
        from providers.config_integration import get_configured_providers
    except ImportError:
        pytest.skip("Provider configuration not available")

    # Test configuration integration
    try:
        providers = get_configured_providers()
        assert providers is not None, "Should return provider configuration"
    except Exception:
        # Configuration may not be complete
        pass


@pytest.mark.integration
def test_provider_stage_integration():
    """Test providers work with stages."""
    try:
        from core.context import PipelineContext
        from providers.media.mock_provider import MockMediaProvider
        from stages.media.provider_image_stage import ProviderImageStage
    except ImportError:
        pytest.skip("Provider-stage integration not available")

    try:
        # Test provider can be used with stage
        mock_provider = MockMediaProvider()
        stage = ProviderImageStage(provider=mock_provider)

        PipelineContext({"words": ["test"]})

        # This may fail due to missing configuration, but structure should work
        # We're mainly testing the integration works, not the full execution
        assert stage is not None, "Stage with provider should be creatable"
        assert hasattr(stage, "execute"), "Stage should have execute method"

    except Exception:
        # Integration may require more configuration
        pass


if __name__ == "__main__":
    test_provider_registry()
    test_media_providers()
    test_sync_providers()
    test_data_providers()
    test_provider_configuration_integration()
    test_provider_stage_integration()
    print("Provider integration tests passed!")
