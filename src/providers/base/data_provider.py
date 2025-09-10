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
