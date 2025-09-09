"""Unit tests for data provider interface."""

import pytest
from src.providers.base.data_provider import DataProvider


class MockDataProvider(DataProvider):
    """Mock data provider for testing."""

    def __init__(self):
        self.data_store = {}

    def load_data(self, identifier: str) -> dict:
        if identifier not in self.data_store:
            raise ValueError(f"Data '{identifier}' not found")
        return self.data_store[identifier]

    def save_data(self, identifier: str, data: dict) -> bool:
        self.data_store[identifier] = data
        return True

    def exists(self, identifier: str) -> bool:
        return identifier in self.data_store

    def list_identifiers(self) -> list[str]:
        return list(self.data_store.keys())


class TestDataProvider:
    """Test cases for DataProvider interface."""

    def test_data_provider_interface(self):
        """Test data provider can be implemented."""
        provider = MockDataProvider()
        assert provider is not None

    def test_save_and_load_data(self):
        """Test saving and loading data."""
        provider = MockDataProvider()
        test_data = {"key": "value", "number": 42}

        # Save data
        result = provider.save_data("test", test_data)
        assert result is True

        # Load data
        loaded = provider.load_data("test")
        assert loaded == test_data

    def test_load_nonexistent_data(self):
        """Test loading non-existent data raises ValueError."""
        provider = MockDataProvider()

        with pytest.raises(ValueError):
            provider.load_data("nonexistent")

    def test_exists(self):
        """Test checking if data exists."""
        provider = MockDataProvider()
        test_data = {"key": "value"}

        assert not provider.exists("test")

        provider.save_data("test", test_data)
        assert provider.exists("test")

    def test_list_identifiers(self):
        """Test listing available data identifiers."""
        provider = MockDataProvider()

        # Initially empty
        assert provider.list_identifiers() == []

        # Add some data
        provider.save_data("test1", {"data": 1})
        provider.save_data("test2", {"data": 2})

        identifiers = provider.list_identifiers()
        assert "test1" in identifiers
        assert "test2" in identifiers
        assert len(identifiers) == 2
