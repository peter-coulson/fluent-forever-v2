"""
Memory Data Provider

In-memory data provider for testing and temporary storage.
"""

import copy
from typing import Any

from src.providers.base.data_provider import DataProvider


class MemoryDataProvider(DataProvider):
    """In-memory data provider for testing"""

    def __init__(self) -> None:
        """Initialize memory data provider"""
        self._data: dict[str, dict[str, Any]] = {}

    def load_data(self, identifier: str) -> dict[str, Any]:
        """Load data from memory

        Args:
            identifier: Data key

        Returns:
            Deep copy of stored data, or empty dict if not found
        """
        if identifier in self._data:
            return copy.deepcopy(self._data[identifier])
        return {}

    def save_data(self, identifier: str, data: dict[str, Any]) -> bool:
        """Save data to memory

        Args:
            identifier: Data key
            data: Dictionary data to save

        Returns:
            Always True (memory saves don't fail)
        """
        self._data[identifier] = copy.deepcopy(data)
        return True

    def exists(self, identifier: str) -> bool:
        """Check if data exists in memory

        Args:
            identifier: Data key to check

        Returns:
            True if identifier exists
        """
        return identifier in self._data

    def list_identifiers(self) -> list[str]:
        """List all stored identifiers

        Returns:
            List of all stored keys
        """
        return list(self._data.keys())

    def backup_data(self, identifier: str) -> str | None:
        """Create backup of data (in memory)

        Args:
            identifier: Data key to backup

        Returns:
            Backup identifier if successful
        """
        if identifier not in self._data:
            return None

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{identifier}_backup_{timestamp}"

        self._data[backup_name] = copy.deepcopy(self._data[identifier])
        return backup_name

    def clear(self) -> None:
        """Clear all data (testing utility)

        Note: This method is specific to MemoryDataProvider
        and is useful for test cleanup.
        """
        self._data.clear()

    def get_data_copy(self) -> dict[str, dict[str, Any]]:
        """Get copy of all stored data (testing utility)

        Returns:
            Deep copy of all stored data

        Note: This method is specific to MemoryDataProvider
        and is useful for test verification.
        """
        return copy.deepcopy(self._data)

    def set_data(self, data: dict[str, dict[str, Any]]) -> None:
        """Set all data at once (testing utility)

        Args:
            data: Dictionary of identifier -> data mappings

        Note: This method is specific to MemoryDataProvider
        and is useful for test setup.
        """
        self._data = copy.deepcopy(data)
