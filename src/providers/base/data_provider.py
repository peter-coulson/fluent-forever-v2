"""
Data Provider Interface

Abstract interface for data sources (JSON files, databases, memory, etc.)
"""

from abc import ABC, abstractmethod
from typing import Any

from src.utils.logging_config import ICONS, get_logger


class DataProvider(ABC):
    """Abstract interface for data sources"""

    def __init__(self) -> None:
        self.logger = get_logger(f"providers.data.{self.__class__.__name__.lower()}")
        self.read_only = False
        self._managed_files: list[str] = []

    def load_data(self, identifier: str) -> dict[str, Any]:
        """Load data by identifier (e.g., filename, key)

        Args:
            identifier: Data identifier (filename without extension, key, etc.)

        Returns:
            Dictionary containing the loaded data

        Raises:
            ValueError: If data cannot be loaded or doesn't exist
        """
        self.logger.info(f"{ICONS['file']} Loading data from {identifier}")

        try:
            self.validate_file_access(identifier)
            data = self._load_data_impl(identifier)
            record_count = len(data) if isinstance(data, dict) else "unknown"
            self.logger.debug(f"Loaded {record_count} records from {identifier}")
            return data
        except Exception as e:
            self.logger.error(
                f"{ICONS['cross']} Failed to load data from {identifier}: {e}"
            )
            raise

    @abstractmethod
    def _load_data_impl(self, identifier: str) -> dict[str, Any]:
        """Implementation-specific data loading"""
        pass

    def save_data(self, identifier: str, data: dict[str, Any]) -> bool:
        """Save data to identifier. Return True if successful.

        Args:
            identifier: Data identifier to save to
            data: Dictionary data to save

        Returns:
            True if save was successful, False otherwise
        """
        self.logger.info(f"{ICONS['file']} Saving data to {identifier}")

        try:
            self._check_write_permission(identifier)
            self.validate_file_access(identifier)
            result = self._save_data_impl(identifier, data)
            record_count = len(data) if isinstance(data, dict) else "unknown"
            self.logger.debug(f"Saved {record_count} records to {identifier}")

            if result:
                self.logger.info(
                    f"{ICONS['check']} Data saved successfully to {identifier}"
                )
            else:
                self.logger.warning(
                    f"{ICONS['warning']} Save operation returned False for {identifier}"
                )

            return result
        except (PermissionError, ValueError):
            # Re-raise permission and validation errors
            raise
        except Exception as e:
            self.logger.error(
                f"{ICONS['cross']} Failed to save data to {identifier}: {e}"
            )
            return False

    @abstractmethod
    def _save_data_impl(self, identifier: str, data: dict[str, Any]) -> bool:
        """Implementation-specific data saving"""
        pass

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if data exists for identifier

        Args:
            identifier: Data identifier to check

        Returns:
            True if data exists, False otherwise
        """
        pass

    @abstractmethod
    def list_identifiers(self) -> list[str]:
        """List all available data identifiers

        Returns:
            List of all available identifiers
        """
        pass

    def backup_data(self, identifier: str) -> str | None:
        """Create backup of data. Return backup identifier if successful.

        Args:
            identifier: Data identifier to backup

        Returns:
            Backup identifier if successful, None if backup failed or not supported
        """
        return None  # Optional for providers

    @property
    def is_read_only(self) -> bool:
        """Check if provider is read-only"""
        return self.read_only

    @property
    def managed_files(self) -> list[str]:
        """Get list of files managed by this provider"""
        return self._managed_files

    def set_read_only(self, read_only: bool) -> None:
        """Set read-only status"""
        self.read_only = read_only

    def set_managed_files(self, files: list[str]) -> None:
        """Set list of files managed by this provider"""
        self._managed_files = files

    def validate_file_access(self, identifier: str) -> None:
        """Validate file access permissions

        Args:
            identifier: File identifier to check

        Raises:
            ValueError: If file is not managed by this provider
        """
        if self._managed_files and identifier not in self._managed_files:
            raise ValueError(
                f"File '{identifier}' not managed by this provider. "
                f"Managed files: {self._managed_files}"
            )

    def _check_write_permission(self, identifier: str) -> None:
        """Check if write operations are allowed

        Args:
            identifier: File identifier being written to

        Raises:
            PermissionError: If provider is read-only
        """
        if self.read_only:
            raise PermissionError(
                f"Cannot write to '{identifier}': provider is read-only"
            )
