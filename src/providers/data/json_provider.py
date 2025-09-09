"""
JSON Data Provider

Provides data from JSON files on the filesystem.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from providers.base.data_provider import DataProvider


class JSONDataProvider(DataProvider):
    """Provide data from JSON files"""

    def __init__(self, base_path: Path):
        """Initialize JSON data provider

        Args:
            base_path: Directory containing JSON files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load_data(self, identifier: str) -> dict[str, Any]:
        """Load data from JSON file

        Args:
            identifier: Filename without .json extension

        Returns:
            Dictionary containing the loaded data

        Raises:
            ValueError: If file doesn't exist or contains invalid JSON
        """
        file_path = self.base_path / f"{identifier}.json"
        if not file_path.exists():
            return {}

        try:
            text_content = file_path.read_text(encoding="utf-8")
            if not text_content.strip():
                return {}
            return json.loads(text_content)
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading {identifier}: {e}")

    def save_data(self, identifier: str, data: dict[str, Any]) -> bool:
        """Save data to JSON file

        Args:
            identifier: Filename without .json extension
            data: Dictionary data to save

        Returns:
            True if save was successful, False otherwise
        """
        file_path = self.base_path / f"{identifier}.json"

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Pretty-print JSON with consistent formatting
            json_content = json.dumps(
                data, indent=2, ensure_ascii=False, sort_keys=True
            )

            file_path.write_text(json_content + "\n", encoding="utf-8")
            return True
        except (OSError, TypeError) as e:
            # TypeError can occur if data contains non-serializable objects
            print(f"Error saving {identifier}: {e}")
            return False

    def exists(self, identifier: str) -> bool:
        """Check if JSON file exists

        Args:
            identifier: Filename without .json extension

        Returns:
            True if file exists, False otherwise
        """
        return (self.base_path / f"{identifier}.json").exists()

    def list_identifiers(self) -> list[str]:
        """List all JSON files (without .json extension)

        Returns:
            List of identifiers for all JSON files
        """
        if not self.base_path.exists():
            return []

        return [f.stem for f in self.base_path.glob("*.json")]

    def backup_data(self, identifier: str) -> str | None:
        """Create backup of JSON file

        Args:
            identifier: Filename without .json extension

        Returns:
            Backup identifier if successful, None if failed
        """
        source = self.base_path / f"{identifier}.json"
        if not source.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{identifier}_backup_{timestamp}"
        backup_path = self.base_path / f"{backup_name}.json"

        try:
            backup_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            return backup_name
        except OSError:
            return None

    def get_file_path(self, identifier: str) -> Path:
        """Get full file path for identifier (utility method)

        Args:
            identifier: Filename without .json extension

        Returns:
            Path object for the JSON file
        """
        return self.base_path / f"{identifier}.json"

    def get_modification_time(self, identifier: str) -> datetime | None:
        """Get last modification time for file

        Args:
            identifier: Filename without .json extension

        Returns:
            Datetime of last modification, None if file doesn't exist
        """
        file_path = self.get_file_path(identifier)
        if not file_path.exists():
            return None

        return datetime.fromtimestamp(file_path.stat().st_mtime)
