"""Unit tests for Memory data provider."""

from src.providers.data.memory_provider import MemoryDataProvider


class TestMemoryDataProvider:
    """Test cases for MemoryDataProvider."""

    def test_provider_creation(self):
        """Test memory provider creation."""
        provider = MemoryDataProvider()
        assert provider is not None
        assert provider.list_identifiers() == []

    def test_save_and_load_data(self):
        """Test saving and loading data in memory."""
        provider = MemoryDataProvider()
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        # Save data
        result = provider.save_data("test", test_data)
        assert result is True

        # Load data back
        loaded = provider.load_data("test")
        assert loaded == test_data

    def test_load_nonexistent_data(self):
        """Test loading non-existent data returns empty dict."""
        provider = MemoryDataProvider()

        result = provider.load_data("nonexistent")
        assert result == {}

    def test_data_isolation(self):
        """Test that changes to returned data don't affect stored data."""
        provider = MemoryDataProvider()
        original_data = {"list": [1, 2, 3], "dict": {"nested": "value"}}

        provider.save_data("test", original_data)

        # Modify returned data
        loaded1 = provider.load_data("test")
        loaded1["list"].append(4)
        loaded1["dict"]["new"] = "added"

        # Original stored data should be unchanged
        loaded2 = provider.load_data("test")
        assert loaded2 == original_data
        assert len(loaded2["list"]) == 3
        assert "new" not in loaded2["dict"]

    def test_exists(self):
        """Test checking if data exists."""
        provider = MemoryDataProvider()
        test_data = {"key": "value"}

        assert not provider.exists("test")

        provider.save_data("test", test_data)
        assert provider.exists("test")

    def test_list_identifiers(self):
        """Test listing available data identifiers."""
        provider = MemoryDataProvider()

        # Initially empty
        assert provider.list_identifiers() == []

        # Add some data
        provider.save_data("test1", {"data": 1})
        provider.save_data("test2", {"data": 2})

        identifiers = provider.list_identifiers()
        assert "test1" in identifiers
        assert "test2" in identifiers
        assert len(identifiers) == 2

    def test_backup_data(self):
        """Test backup functionality."""
        provider = MemoryDataProvider()
        test_data = {"important": "data"}

        provider.save_data("original", test_data)

        # Create backup
        backup_id = provider.backup_data("original")
        assert backup_id is not None
        assert backup_id.startswith("original_backup_")

        # Verify backup exists and contains same data
        assert provider.exists(backup_id)
        backup_data = provider.load_data(backup_id)
        assert backup_data == test_data

    def test_backup_nonexistent_data(self):
        """Test backup of non-existent data returns None."""
        provider = MemoryDataProvider()

        backup_id = provider.backup_data("nonexistent")
        assert backup_id is None

    def test_clear_functionality(self):
        """Test clearing all data."""
        provider = MemoryDataProvider()

        # Add some data
        provider.save_data("test1", {"data": 1})
        provider.save_data("test2", {"data": 2})
        assert len(provider.list_identifiers()) == 2

        # Clear all data
        provider.clear()
        assert provider.list_identifiers() == []
        assert not provider.exists("test1")
        assert not provider.exists("test2")

    def test_get_data_copy(self):
        """Test getting copy of all stored data."""
        provider = MemoryDataProvider()

        provider.save_data("test1", {"data": 1})
        provider.save_data("test2", {"data": 2})

        all_data = provider.get_data_copy()
        assert "test1" in all_data
        assert "test2" in all_data
        assert all_data["test1"] == {"data": 1}
        assert all_data["test2"] == {"data": 2}

        # Modify copy shouldn't affect original
        all_data["test1"]["modified"] = True
        original = provider.load_data("test1")
        assert "modified" not in original

    def test_set_data(self):
        """Test setting all data at once."""
        provider = MemoryDataProvider()

        initial_data = {"item1": {"value": 1}, "item2": {"value": 2}}

        provider.set_data(initial_data)

        assert provider.exists("item1")
        assert provider.exists("item2")
        assert provider.load_data("item1") == {"value": 1}
        assert provider.load_data("item2") == {"value": 2}
