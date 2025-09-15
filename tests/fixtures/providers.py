"""Mock provider implementations for E2E testing."""

from pathlib import Path
from typing import Any

from src.providers.base.data_provider import DataProvider
from src.providers.base.media_provider import MediaProvider
from src.providers.base.sync_provider import SyncProvider


class MockDataProvider(DataProvider):
    """Mock data provider for testing."""

    def __init__(self, base_path: Path, read_only: bool = False, managed_files: list[str] | None = None):
        super().__init__(base_path, read_only, managed_files)
        self._data: dict[str, Any] = {}

    def load_data(self, file_id: str) -> dict[str, Any]:
        """Load mock data."""
        return self._data.get(file_id, {"mock": "data", "file_id": file_id})

    def save_data(self, file_id: str, data: dict[str, Any]) -> None:
        """Save mock data."""
        if self.read_only:
            raise ValueError("Cannot save data: provider is read-only")
        self._data[file_id] = data

    def list_files(self) -> list[str]:
        """List available mock files."""
        return list(self._data.keys()) or ["mock_file.json"]

    def get_file_path(self, file_id: str) -> Path:
        """Get path for mock file."""
        return self.base_path / f"{file_id}.json"

    def file_exists(self, file_id: str) -> bool:
        """Check if mock file exists."""
        return file_id in self._data


class MockAudioProvider(MediaProvider):
    """Mock audio provider for testing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.api_calls: list[dict[str, Any]] = []

    async def get_audio_url(self, word: str, **kwargs: Any) -> str | None:
        """Return mock audio URL."""
        self.api_calls.append({"method": "get_audio_url", "word": word, "kwargs": kwargs})
        return f"https://mock-audio.com/{word}.mp3"

    async def download_audio(self, word: str, target_path: Path, **kwargs: Any) -> bool:
        """Mock audio download."""
        self.api_calls.append({"method": "download_audio", "word": word, "target_path": str(target_path), "kwargs": kwargs})
        # Simulate file creation
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(f"mock audio data for {word}")
        return True

    async def batch_download_audio(self, requests: list[dict[str, Any]]) -> dict[str, bool]:
        """Mock batch audio download."""
        self.api_calls.append({"method": "batch_download_audio", "requests": requests})
        results = {}
        for req in requests:
            word = req["word"]
            target_path = Path(req["target_path"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(f"mock batch audio data for {word}")
            results[word] = True
        return results

    def get_api_call_count(self) -> int:
        """Get number of API calls made."""
        return len(self.api_calls)

    def clear_api_calls(self) -> None:
        """Clear API call history."""
        self.api_calls.clear()


class MockImageProvider(MediaProvider):
    """Mock image provider for testing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.api_calls: list[dict[str, Any]] = []

    async def get_image_url(self, query: str, **kwargs: Any) -> str | None:
        """Return mock image URL."""
        self.api_calls.append({"method": "get_image_url", "query": query, "kwargs": kwargs})
        return f"https://mock-images.com/{query.replace(' ', '_')}.jpg"

    async def download_image(self, query: str, target_path: Path, **kwargs: Any) -> bool:
        """Mock image download."""
        self.api_calls.append({"method": "download_image", "query": query, "target_path": str(target_path), "kwargs": kwargs})
        # Simulate file creation
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(f"mock image data for {query}")
        return True

    async def batch_download_images(self, requests: list[dict[str, Any]]) -> dict[str, bool]:
        """Mock batch image download."""
        self.api_calls.append({"method": "batch_download_images", "requests": requests})
        results = {}
        for req in requests:
            query = req["query"]
            target_path = Path(req["target_path"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(f"mock batch image data for {query}")
            results[query] = True
        return results

    def get_api_call_count(self) -> int:
        """Get number of API calls made."""
        return len(self.api_calls)

    def clear_api_calls(self) -> None:
        """Clear API call history."""
        self.api_calls.clear()


class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.sync_calls: list[dict[str, Any]] = []
        self.notes: list[dict[str, Any]] = []

    async def sync_note(self, note_data: dict[str, Any]) -> bool:
        """Mock note sync."""
        self.sync_calls.append({"method": "sync_note", "note_data": note_data})
        self.notes.append(note_data)
        return True

    async def batch_sync_notes(self, notes: list[dict[str, Any]]) -> dict[str, bool]:
        """Mock batch note sync."""
        self.sync_calls.append({"method": "batch_sync_notes", "notes": notes})
        results = {}
        for note in notes:
            note_id = note.get("id", f"note_{len(self.notes)}")
            self.notes.append(note)
            results[note_id] = True
        return results

    def get_sync_call_count(self) -> int:
        """Get number of sync calls made."""
        return len(self.sync_calls)

    def get_synced_notes(self) -> list[dict[str, Any]]:
        """Get all synced notes."""
        return self.notes.copy()

    def clear_sync_history(self) -> None:
        """Clear sync call history."""
        self.sync_calls.clear()
        self.notes.clear()


def create_mock_data_provider(config: dict[str, Any]) -> MockDataProvider:
    """Factory for creating mock data providers."""
    base_path = Path(config.get("base_path", "."))
    read_only = config.get("read_only", False)
    managed_files = config.get("files", [])
    return MockDataProvider(base_path, read_only, managed_files)


def create_mock_audio_provider(config: dict[str, Any]) -> MockAudioProvider:
    """Factory for creating mock audio providers."""
    return MockAudioProvider(config)


def create_mock_image_provider(config: dict[str, Any]) -> MockImageProvider:
    """Factory for creating mock image providers."""
    return MockImageProvider(config)


def create_mock_sync_provider(config: dict[str, Any]) -> MockSyncProvider:
    """Factory for creating mock sync providers."""
    return MockSyncProvider(config)


class FailingProvider(MediaProvider):
    """Provider that fails for error testing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    async def get_audio_url(self, word: str, **kwargs: Any) -> str | None:
        raise RuntimeError("Provider failure")

    async def download_audio(self, word: str, target_path: Path, **kwargs: Any) -> bool:
        raise RuntimeError("Download failure")

    async def batch_download_audio(self, requests: list[dict[str, Any]]) -> dict[str, bool]:
        raise RuntimeError("Batch download failure")


class ConfigurableProvider(MediaProvider):
    """Provider with configurable behavior for testing."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.should_fail = config.get("should_fail", False)
        self.delay = config.get("delay", 0)
        self.api_calls: list[dict[str, Any]] = []

    async def get_audio_url(self, word: str, **kwargs: Any) -> str | None:
        self.api_calls.append({"method": "get_audio_url", "word": word})
        if self.should_fail:
            raise RuntimeError("Configured to fail")
        return f"https://configurable.com/{word}.mp3"

    async def download_audio(self, word: str, target_path: Path, **kwargs: Any) -> bool:
        self.api_calls.append({"method": "download_audio", "word": word})
        if self.should_fail:
            return False
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(f"configurable audio for {word}")
        return True

    async def batch_download_audio(self, requests: list[dict[str, Any]]) -> dict[str, bool]:
        self.api_calls.append({"method": "batch_download_audio", "count": len(requests)})
        results = {}
        for req in requests:
            word = req["word"]
            if self.should_fail:
                results[word] = False
            else:
                target_path = Path(req["target_path"])
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(f"configurable batch audio for {word}")
                results[word] = True
        return results