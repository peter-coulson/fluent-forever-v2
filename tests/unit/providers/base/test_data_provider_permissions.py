"""Unit tests for DataProvider permission and file management functionality."""

import pytest
from src.providers.base.data_provider import DataProvider


class MockDataProvider(DataProvider):
    """Mock implementation of DataProvider for testing permissions."""

    def __init__(self):
        super().__init__()
        self.data_store = {}

    def _load_data_impl(self, identifier: str) -> dict[str, any]:
        return self.data_store.get(identifier, {})

    def _save_data_impl(self, identifier: str, data: dict[str, any]) -> bool:
        self.data_store[identifier] = data
        return True

    def exists(self, identifier: str) -> bool:
        return identifier in self.data_store

    def list_identifiers(self) -> list[str]:
        return list(self.data_store.keys())


class TestDataProviderPermissions:
    """Test cases for DataProvider permission system."""

    def test_read_only_property_default_false(self):
        """Test read_only property defaults to False."""
        provider = MockDataProvider()
        assert provider.is_read_only is False

    def test_set_read_only_true(self):
        """Test setting read_only to True."""
        provider = MockDataProvider()
        provider.set_read_only(True)
        assert provider.is_read_only is True

    def test_set_read_only_false(self):
        """Test setting read_only to False."""
        provider = MockDataProvider()
        provider.set_read_only(True)
        provider.set_read_only(False)
        assert provider.is_read_only is False

    def test_managed_files_property_default_empty(self):
        """Test managed_files property defaults to empty list."""
        provider = MockDataProvider()
        assert provider.managed_files == []

    def test_set_managed_files(self):
        """Test setting managed files list."""
        provider = MockDataProvider()
        files = ["file1", "file2", "file3"]
        provider.set_managed_files(files)
        assert provider.managed_files == files

    def test_validate_file_access_no_restrictions(self):
        """Test file access validation with no managed files (unrestricted)."""
        provider = MockDataProvider()
        # Should not raise any exception for any file
        provider.validate_file_access("any_file")
        provider.validate_file_access("another_file")

    def test_validate_file_access_allowed_file(self):
        """Test file access validation for allowed file."""
        provider = MockDataProvider()
        provider.set_managed_files(["allowed_file", "another_allowed"])

        # Should not raise exception for allowed file
        provider.validate_file_access("allowed_file")
        provider.validate_file_access("another_allowed")

    def test_validate_file_access_denied_file(self):
        """Test file access validation for denied file."""
        provider = MockDataProvider()
        provider.set_managed_files(["allowed_file"])

        # Should raise ValueError for non-managed file
        with pytest.raises(
            ValueError, match="File 'denied_file' not managed by this provider"
        ):
            provider.validate_file_access("denied_file")

    def test_check_write_permission_allowed(self):
        """Test write permission check when provider is not read-only."""
        provider = MockDataProvider()
        provider.set_read_only(False)

        # Should not raise any exception
        provider._check_write_permission("test_file")

    def test_check_write_permission_denied(self):
        """Test write permission check when provider is read-only."""
        provider = MockDataProvider()
        provider.set_read_only(True)

        # Should raise PermissionError
        with pytest.raises(
            PermissionError, match="Cannot write to 'test_file': provider is read-only"
        ):
            provider._check_write_permission("test_file")

    def test_save_data_read_only_raises_permission_error(self):
        """Test that save_data raises PermissionError for read-only provider."""
        provider = MockDataProvider()
        provider.set_read_only(True)

        test_data = {"key": "value"}

        # Should raise PermissionError when trying to save to read-only provider
        with pytest.raises(
            PermissionError, match="Cannot write to 'test_file': provider is read-only"
        ):
            provider.save_data("test_file", test_data)

    def test_save_data_file_access_validation(self):
        """Test that save_data validates file access permissions."""
        provider = MockDataProvider()
        provider.set_managed_files(["allowed_file"])

        test_data = {"key": "value"}

        # Should succeed for allowed file
        result = provider.save_data("allowed_file", test_data)
        assert result is True

        # Should raise ValueError for non-managed file
        with pytest.raises(
            ValueError, match="File 'denied_file' not managed by this provider"
        ):
            provider.save_data("denied_file", test_data)

    def test_save_data_both_validations_work(self):
        """Test that both read-only and file access validations work together."""
        provider = MockDataProvider()
        provider.set_read_only(True)
        provider.set_managed_files(["allowed_file"])

        test_data = {"key": "value"}

        # Should raise PermissionError first (read-only check comes before file validation)
        with pytest.raises(
            PermissionError,
            match="Cannot write to 'allowed_file': provider is read-only",
        ):
            provider.save_data("allowed_file", test_data)

    def test_load_data_file_access_validation(self):
        """Test that load_data validates file access permissions."""
        provider = MockDataProvider()
        provider.set_managed_files(["allowed_file"])

        # Pre-populate data for testing
        provider.data_store["allowed_file"] = {"key": "value"}

        # Should succeed for allowed file
        result = provider.load_data("allowed_file")
        assert result == {"key": "value"}

        # Should raise ValueError for non-managed file
        with pytest.raises(
            ValueError, match="File 'denied_file' not managed by this provider"
        ):
            provider.load_data("denied_file")

    def test_load_data_no_file_restrictions(self):
        """Test that load_data works without file restrictions."""
        provider = MockDataProvider()
        # No managed files set (empty list means no restrictions)

        # Should succeed for any file
        result = provider.load_data("any_file")
        assert (
            result == {}
        )  # MockDataProvider returns empty dict for non-existent files
