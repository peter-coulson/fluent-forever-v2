"""
Unit tests for provider registry and factory system
"""

from pathlib import Path

from providers.data.memory_provider import MemoryDataProvider
from providers.media.mock_provider import MockMediaProvider
from providers.registry import (
    DataProviderFactory,
    MediaProviderFactory,
    ProviderRegistry,
    SyncProviderFactory,
)
from providers.sync.mock_provider import MockSyncProvider


class TestProviderRegistry:
    """Test provider registry functionality"""

    def setup_method(self):
        """Set up test registry"""
        self.registry = ProviderRegistry()

    def test_data_provider_registration(self):
        """Test data provider registration and retrieval"""
        # Create and register provider
        provider = MemoryDataProvider()
        self.registry.register_data_provider("test", provider)

        # Test retrieval
        retrieved = self.registry.get_data_provider("test")
        assert retrieved is provider

        # Test listing
        assert "test" in self.registry.list_data_providers()

    def test_media_provider_registration(self):
        """Test media provider registration and retrieval"""
        # Create and register provider
        provider = MockMediaProvider()
        self.registry.register_media_provider("test", provider)

        # Test retrieval
        retrieved = self.registry.get_media_provider("test")
        assert retrieved is provider

        # Test listing
        assert "test" in self.registry.list_media_providers()

    def test_sync_provider_registration(self):
        """Test sync provider registration and retrieval"""
        # Create and register provider
        provider = MockSyncProvider()
        self.registry.register_sync_provider("test", provider)

        # Test retrieval
        retrieved = self.registry.get_sync_provider("test")
        assert retrieved is provider

        # Test listing
        assert "test" in self.registry.list_sync_providers()

    def test_provider_info(self):
        """Test provider info retrieval"""
        # Register providers
        self.registry.register_data_provider("data1", MemoryDataProvider())
        self.registry.register_media_provider("media1", MockMediaProvider(["image"]))
        self.registry.register_media_provider("media2", MockMediaProvider(["audio"]))
        self.registry.register_sync_provider("sync1", MockSyncProvider())

        # Get info
        info = self.registry.get_provider_info()

        assert info["data_providers"]["count"] == 1
        assert info["media_providers"]["count"] == 2
        assert info["sync_providers"]["count"] == 1
        assert "media1" in info["media_providers"]["by_type"]["image"]
        assert "media2" in info["media_providers"]["by_type"]["audio"]

    def test_clear_all(self):
        """Test clearing all providers"""
        # Register providers
        self.registry.register_data_provider("test", MemoryDataProvider())
        self.registry.register_media_provider("test", MockMediaProvider())
        self.registry.register_sync_provider("test", MockSyncProvider())

        # Clear all
        self.registry.clear_all()

        # Verify empty
        assert len(self.registry.list_data_providers()) == 0
        assert len(self.registry.list_media_providers()) == 0
        assert len(self.registry.list_sync_providers()) == 0


class TestDataProviderFactory:
    """Test data provider factory"""

    def setup_method(self):
        """Set up test factory"""
        self.factory = DataProviderFactory()

    def test_json_provider_creation(self):
        """Test JSON provider creation"""
        provider = self.factory.create_json_provider(Path("/tmp/test"))
        assert provider is not None
        assert hasattr(provider, "load_data")
        assert hasattr(provider, "save_data")

    def test_memory_provider_creation(self):
        """Test memory provider creation"""
        provider = self.factory.create_memory_provider()
        assert provider is not None
        assert hasattr(provider, "load_data")
        assert hasattr(provider, "save_data")


class TestMediaProviderFactory:
    """Test media provider factory"""

    def setup_method(self):
        """Set up test factory"""
        self.factory = MediaProviderFactory()

    def test_mock_provider_creation(self):
        """Test mock provider creation"""
        provider = self.factory.create_mock_provider()
        assert provider is not None
        assert hasattr(provider, "generate_media")
        assert hasattr(provider, "generate_image")

    def test_provider_creation_by_name(self):
        """Test provider creation by name"""
        # Test known providers
        mock = self.factory.create_provider("mock")
        assert mock is not None

        # Test unknown provider
        unknown = self.factory.create_provider("unknown")
        assert unknown is None

    def test_fallback_configuration(self):
        """Test fallback provider configuration"""
        config = {"primary": "unknown_provider", "fallback": ["mock"]}

        provider = self.factory.create_provider_with_fallback(config)
        assert provider is not None
        assert isinstance(provider, MockMediaProvider)


class TestSyncProviderFactory:
    """Test sync provider factory"""

    def setup_method(self):
        """Set up test factory"""
        self.factory = SyncProviderFactory()

    def test_mock_provider_creation(self):
        """Test mock sync provider creation"""
        provider = self.factory.create_mock_provider()
        assert provider is not None
        assert hasattr(provider, "test_connection")
        assert hasattr(provider, "sync_cards")
        assert hasattr(provider, "sync_templates")
        assert hasattr(provider, "sync_media")
