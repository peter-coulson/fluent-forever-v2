"""Unit tests for JSON data provider."""


import pytest
from src.providers.data.json_provider import JSONDataProvider


class TestJSONDataProvider:
    """Test cases for JSONDataProvider."""

    def test_provider_creation(self, tmp_path):
        """Test JSON provider creation."""
        provider = JSONDataProvider(tmp_path)
        assert provider.base_path == tmp_path
        assert provider.base_path.exists()

    def test_save_and_load_data(self, tmp_path):
        """Test saving and loading JSON data."""
        provider = JSONDataProvider(tmp_path)
        test_data = {"key": "value", "number": 42, "list": [1, 2, 3]}

        # Save data
        result = provider.save_data("test", test_data)
        assert result is True

        # Verify file was created
        json_file = tmp_path / "test.json"
        assert json_file.exists()

        # Load data back
        loaded = provider.load_data("test")
        assert loaded == test_data

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading non-existent file returns empty dict."""
        provider = JSONDataProvider(tmp_path)

        result = provider.load_data("nonexistent")
        assert result == {}

    def test_save_invalid_json(self, tmp_path):
        """Test saving data that cannot be JSON serialized returns False."""
        provider = JSONDataProvider(tmp_path)
        invalid_data = {"function": lambda x: x}  # Functions can't be serialized

        result = provider.save_data("invalid", invalid_data)
        assert result is False

    def test_load_corrupted_json(self, tmp_path):
        """Test loading corrupted JSON file."""
        provider = JSONDataProvider(tmp_path)

        # Create corrupted JSON file
        json_file = tmp_path / "corrupted.json"
        json_file.write_text("{ invalid json content")

        with pytest.raises(ValueError):
            provider.load_data("corrupted")

    def test_exists(self, tmp_path):
        """Test checking if data exists."""
        provider = JSONDataProvider(tmp_path)
        test_data = {"key": "value"}

        assert not provider.exists("test")

        provider.save_data("test", test_data)
        assert provider.exists("test")

    def test_list_identifiers(self, tmp_path):
        """Test listing available data files."""
        provider = JSONDataProvider(tmp_path)

        # Initially empty
        assert provider.list_identifiers() == []

        # Add some files
        provider.save_data("file1", {"data": 1})
        provider.save_data("file2", {"data": 2})

        identifiers = provider.list_identifiers()
        assert "file1" in identifiers
        assert "file2" in identifiers
        assert len(identifiers) == 2

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test provider creates base directory if it doesn't exist."""
        nested_path = tmp_path / "nested" / "directory"
        JSONDataProvider(nested_path)

        assert nested_path.exists()
        assert nested_path.is_dir()

    def test_unicode_data(self, tmp_path):
        """Test saving and loading unicode data."""
        provider = JSONDataProvider(tmp_path)
        unicode_data = {"spanish": "niño", "emoji": "🚀", "chinese": "你好"}

        provider.save_data("unicode", unicode_data)
        loaded = provider.load_data("unicode")

        assert loaded == unicode_data
