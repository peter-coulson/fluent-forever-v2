"""Unit tests for enhanced JSONDataProvider functionality."""


import pytest
from src.providers.data.json_provider import JSONDataProvider


class TestJSONProviderEnhanced:
    """Test cases for enhanced JSONDataProvider functionality."""

    def test_init_with_read_only_true(self, tmp_path):
        """Test JSONDataProvider initialization with read_only=True."""
        provider = JSONDataProvider(tmp_path, read_only=True)

        assert provider.base_path == tmp_path
        assert provider.is_read_only is True
        assert provider.managed_files == []

    def test_init_with_read_only_false(self, tmp_path):
        """Test JSONDataProvider initialization with read_only=False."""
        provider = JSONDataProvider(tmp_path, read_only=False)

        assert provider.base_path == tmp_path
        assert provider.is_read_only is False
        assert provider.managed_files == []

    def test_init_with_managed_files(self, tmp_path):
        """Test JSONDataProvider initialization with managed files."""
        files = ["file1", "file2", "config"]
        provider = JSONDataProvider(tmp_path, managed_files=files)

        assert provider.base_path == tmp_path
        assert provider.managed_files == files
        assert provider.is_read_only is False  # default

    def test_init_with_no_managed_files(self, tmp_path):
        """Test JSONDataProvider initialization with no managed files restriction."""
        provider = JSONDataProvider(tmp_path, managed_files=None)

        assert provider.base_path == tmp_path
        assert provider.managed_files == []

    def test_init_with_all_options(self, tmp_path):
        """Test JSONDataProvider initialization with all options."""
        files = ["dictionary", "vocabulary"]
        provider = JSONDataProvider(tmp_path, read_only=True, managed_files=files)

        assert provider.base_path == tmp_path
        assert provider.is_read_only is True
        assert provider.managed_files == files

    def test_load_data_file_access_validation_allowed(self, tmp_path):
        """Test load_data with file access validation for allowed file."""
        provider = JSONDataProvider(tmp_path, managed_files=["allowed"])

        # Create test file
        test_file = tmp_path / "allowed.json"
        test_file.write_text('{"key": "value"}')

        result = provider.load_data("allowed")
        assert result == {"key": "value"}

    def test_load_data_file_access_validation_denied(self, tmp_path):
        """Test load_data with file access validation for denied file."""
        provider = JSONDataProvider(tmp_path, managed_files=["allowed"])

        # Create test file that's not in managed files
        test_file = tmp_path / "denied.json"
        test_file.write_text('{"key": "value"}')

        with pytest.raises(
            ValueError, match="File 'denied' not managed by this provider"
        ):
            provider.load_data("denied")

    def test_load_data_no_file_restrictions(self, tmp_path):
        """Test load_data with no file restrictions."""
        provider = JSONDataProvider(tmp_path)  # No managed files = no restrictions

        # Create test file
        test_file = tmp_path / "anyfile.json"
        test_file.write_text('{"key": "value"}')

        result = provider.load_data("anyfile")
        assert result == {"key": "value"}

    def test_save_data_read_only_provider_raises_error(self, tmp_path):
        """Test save_data raises error for read-only provider."""
        provider = JSONDataProvider(tmp_path, read_only=True)

        test_data = {"key": "value"}

        with pytest.raises(
            PermissionError, match="Cannot write to 'test': provider is read-only"
        ):
            provider.save_data("test", test_data)

    def test_save_data_write_allowed_succeeds(self, tmp_path):
        """Test save_data succeeds when write is allowed."""
        provider = JSONDataProvider(tmp_path, read_only=False)

        test_data = {"key": "value", "number": 42}
        result = provider.save_data("test", test_data)

        assert result is True

        # Verify file was created with correct content
        test_file = tmp_path / "test.json"
        assert test_file.exists()

        # Load and verify content
        loaded_data = provider.load_data("test")
        assert loaded_data == test_data

    def test_save_data_unmanaged_file_denied(self, tmp_path):
        """Test save_data denied for unmanaged file."""
        provider = JSONDataProvider(tmp_path, managed_files=["allowed"])

        test_data = {"key": "value"}

        # Should succeed for allowed file
        result = provider.save_data("allowed", test_data)
        assert result is True

        # Should fail for unmanaged file
        with pytest.raises(
            ValueError, match="File 'denied' not managed by this provider"
        ):
            provider.save_data("denied", test_data)

    def test_save_data_managed_file_list_validation(self, tmp_path):
        """Test save_data validation with multiple managed files."""
        provider = JSONDataProvider(
            tmp_path, managed_files=["file1", "file2", "config"]
        )

        test_data = {"key": "value"}

        # Should succeed for all managed files
        assert provider.save_data("file1", test_data) is True
        assert provider.save_data("file2", test_data) is True
        assert provider.save_data("config", test_data) is True

        # Should fail for unmanaged file
        with pytest.raises(
            ValueError, match="File 'unmanaged' not managed by this provider"
        ):
            provider.save_data("unmanaged", test_data)

    def test_backwards_compatibility_existing_constructor(self, tmp_path):
        """Test that existing constructor usage still works (backwards compatibility)."""
        # This should work exactly as before
        provider = JSONDataProvider(tmp_path)

        assert provider.base_path == tmp_path
        assert provider.is_read_only is False
        assert provider.managed_files == []

        # Should be able to save/load any file
        test_data = {"key": "value"}
        assert provider.save_data("anyfile", test_data) is True
        assert provider.load_data("anyfile") == test_data

    def test_exists_file_access_validation(self, tmp_path):
        """Test exists method respects file access validation."""
        provider = JSONDataProvider(tmp_path, managed_files=["allowed"])

        # Create files
        allowed_file = tmp_path / "allowed.json"
        denied_file = tmp_path / "denied.json"
        allowed_file.write_text('{"key": "value"}')
        denied_file.write_text('{"key": "value"}')

        # Should work for managed file
        assert provider.exists("allowed") is True

        # Should raise error for unmanaged file
        with pytest.raises(
            ValueError, match="File 'denied' not managed by this provider"
        ):
            provider.exists("denied")

    def test_list_identifiers_file_access_validation(self, tmp_path):
        """Test list_identifiers respects file access validation."""
        provider = JSONDataProvider(tmp_path, managed_files=["file1", "file2"])

        # Create multiple files
        (tmp_path / "file1.json").write_text("{}")
        (tmp_path / "file2.json").write_text("{}")
        (tmp_path / "unmanaged.json").write_text("{}")

        identifiers = provider.list_identifiers()

        # Should only return managed files that exist
        assert "file1" in identifiers
        assert "file2" in identifiers
        assert "unmanaged" not in identifiers
        assert len(identifiers) == 2

    def test_list_identifiers_no_restrictions(self, tmp_path):
        """Test list_identifiers with no file restrictions."""
        provider = JSONDataProvider(tmp_path)  # No managed files

        # Create multiple files
        (tmp_path / "file1.json").write_text("{}")
        (tmp_path / "file2.json").write_text("{}")
        (tmp_path / "file3.json").write_text("{}")

        identifiers = provider.list_identifiers()

        # Should return all files
        assert "file1" in identifiers
        assert "file2" in identifiers
        assert "file3" in identifiers
        assert len(identifiers) == 3
