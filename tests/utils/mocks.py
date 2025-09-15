"""Centralized mock factories for E2E tests."""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry
from tests.fixtures.pipelines import MockPipeline
from tests.fixtures.providers import (
    MockAudioProvider,
    MockDataProvider,
    MockImageProvider,
    MockSyncProvider,
)


class MockRegistryFactory:
    """Factory for creating mock registries with test data."""

    @staticmethod
    def create_pipeline_registry() -> PipelineRegistry:
        """Create pipeline registry with test pipelines."""
        registry = PipelineRegistry()
        
        # Register test pipelines
        test_pipeline = MockPipeline("test_pipeline")
        vocabulary_pipeline = MockPipeline("vocabulary", ["prepare", "validate", "sync"])
        conjugation_pipeline = MockPipeline("conjugation", ["analyze", "generate", "sync"])
        
        registry.register(test_pipeline)
        registry.register(vocabulary_pipeline)
        registry.register(conjugation_pipeline)
        
        return registry

    @staticmethod
    def create_provider_registry() -> ProviderRegistry:
        """Create provider registry with mock providers."""
        registry = ProviderRegistry()
        
        # Register data providers
        data_provider = MockDataProvider(Path("."), read_only=False)
        readonly_provider = MockDataProvider(Path("."), read_only=True, managed_files=["readonly.json"])
        
        registry.register_data_provider("test_data", data_provider)
        registry.register_data_provider("readonly_data", readonly_provider)
        
        # Register audio providers
        audio_provider = MockAudioProvider({"api_key": "test_key"})
        backup_audio = MockAudioProvider({"api_key": "backup_key"})
        
        registry.register_audio_provider("test_audio", audio_provider)
        registry.register_audio_provider("backup_audio", backup_audio)
        
        # Register image providers
        image_provider = MockImageProvider({"api_key": "test_key"})
        registry.register_image_provider("test_image", image_provider)
        
        # Register sync providers
        sync_provider = MockSyncProvider({"anki_connect_url": "http://localhost:8765"})
        registry.register_sync_provider("test_sync", sync_provider)
        
        # Set up pipeline assignments
        registry.set_pipeline_assignments("data", "test_data", ["test_pipeline", "vocabulary"])
        registry.set_pipeline_assignments("data", "readonly_data", ["*"])
        registry.set_pipeline_assignments("audio", "test_audio", ["test_pipeline"])
        registry.set_pipeline_assignments("audio", "backup_audio", ["vocabulary"])
        registry.set_pipeline_assignments("image", "test_image", ["test_pipeline", "vocabulary"])
        registry.set_pipeline_assignments("sync", "test_sync", ["*"])
        
        return registry


class MockFileSystem:
    """Mock file system operations for testing."""

    def __init__(self):
        self.files: dict[str, str] = {}
        self.directories: set[str] = set()

    def create_file(self, path: str, content: str) -> None:
        """Create a mock file with content."""
        self.files[path] = content
        # Create parent directories
        parent = str(Path(path).parent)
        if parent != ".":
            self.directories.add(parent)

    def file_exists(self, path: str) -> bool:
        """Check if mock file exists."""
        return path in self.files

    def read_file(self, path: str) -> str:
        """Read mock file content."""
        return self.files.get(path, "")

    def list_files(self, directory: str = ".") -> list[str]:
        """List files in mock directory."""
        return [f for f in self.files.keys() if f.startswith(directory)]


class MockExternalAPIs:
    """Mock external API responses for testing."""

    @staticmethod
    def create_forvo_response() -> dict[str, Any]:
        """Create mock Forvo API response."""
        return {
            "items": [
                {
                    "id": 12345,
                    "word": "casa",
                    "pathmp3": "https://forvo.com/casa.mp3",
                    "pathogge": "https://forvo.com/casa.ogg",
                    "username": "test_user",
                    "sex": "f",
                    "country": "Spain"
                }
            ]
        }

    @staticmethod
    def create_openai_response() -> dict[str, Any]:
        """Create mock OpenAI API response."""
        return {
            "data": [
                {
                    "url": "https://openai.com/generated_image.jpg",
                    "revised_prompt": "A realistic photo of a house"
                }
            ]
        }

    @staticmethod
    def create_anki_response() -> dict[str, Any]:
        """Create mock AnkiConnect response."""
        return {
            "result": 1234567890,
            "error": None
        }


def mock_requests_session():
    """Create a mock requests session for API testing."""
    session_mock = Mock()
    
    def get_side_effect(url, **kwargs):
        response_mock = Mock()
        response_mock.status_code = 200
        
        if "forvo" in url:
            response_mock.json.return_value = MockExternalAPIs.create_forvo_response()
        elif "openai" in url:
            response_mock.json.return_value = MockExternalAPIs.create_openai_response()
        elif "anki" in url:
            response_mock.json.return_value = MockExternalAPIs.create_anki_response()
        else:
            response_mock.json.return_value = {"status": "ok"}
        
        return response_mock
    
    def post_side_effect(url, **kwargs):
        response_mock = Mock()
        response_mock.status_code = 200
        
        if "anki" in url:
            response_mock.json.return_value = MockExternalAPIs.create_anki_response()
        else:
            response_mock.json.return_value = {"status": "created"}
        
        return response_mock
    
    session_mock.get.side_effect = get_side_effect
    session_mock.post.side_effect = post_side_effect
    
    return session_mock


class MockEnvironment:
    """Mock environment variables for testing."""

    def __init__(self, env_vars: dict[str, str] | None = None):
        self.env_vars = env_vars or {}

    def __enter__(self):
        self.patcher = patch.dict('os.environ', self.env_vars)
        self.patcher.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.patcher.stop()


def create_mock_cli_args(**kwargs) -> Mock:
    """Create mock CLI arguments."""
    args = Mock()
    
    # Default values
    args.command = kwargs.get('command', 'run')
    args.pipeline = kwargs.get('pipeline', 'test_pipeline')
    args.stage = kwargs.get('stage', None)
    args.phase = kwargs.get('phase', None)
    args.dry_run = kwargs.get('dry_run', False)
    args.verbose = kwargs.get('verbose', False)
    args.config = kwargs.get('config', None)
    args.detailed = kwargs.get('detailed', False)
    args.stages = kwargs.get('stages', False)
    
    # Add any additional arguments
    for key, value in kwargs.items():
        if not hasattr(args, key):
            setattr(args, key, value)
    
    return args


def mock_performance_logging():
    """Mock performance logging decorators for testing."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


class MockLogging:
    """Mock logging system for testing."""

    def __init__(self):
        self.log_messages: list[dict[str, Any]] = []

    def log(self, level: str, message: str, **kwargs) -> None:
        """Capture log message."""
        self.log_messages.append({
            "level": level,
            "message": message,
            "kwargs": kwargs
        })

    def info(self, message: str, **kwargs) -> None:
        self.log("INFO", message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        self.log("DEBUG", message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self.log("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.log("WARNING", message, **kwargs)

    def get_messages(self, level: str | None = None) -> list[dict[str, Any]]:
        """Get logged messages, optionally filtered by level."""
        if level:
            return [msg for msg in self.log_messages if msg["level"] == level]
        return self.log_messages.copy()

    def clear(self) -> None:
        """Clear logged messages."""
        self.log_messages.clear()


def create_comprehensive_mocks():
    """Create comprehensive mock setup for full E2E testing."""
    return {
        "pipeline_registry": MockRegistryFactory.create_pipeline_registry(),
        "provider_registry": MockRegistryFactory.create_provider_registry(),
        "requests_session": mock_requests_session(),
        "file_system": MockFileSystem(),
        "logging": MockLogging(),
        "environment": MockEnvironment({
            "FORVO_API_KEY": "test_forvo_key",
            "OPENAI_API_KEY": "test_openai_key",
            "LOG_LEVEL": "DEBUG",
            "DATA_PATH": "./test_data",
        })
    }


class E2ETestMocks:
    """Comprehensive mock manager for E2E tests."""

    def __init__(self):
        self.active_patches: list[Any] = []
        self.mock_registries = MockRegistryFactory()

    def setup_all_mocks(self) -> dict[str, Any]:
        """Set up all mocks for E2E testing."""
        # Mock external dependencies
        requests_patch = patch('requests.Session', return_value=mock_requests_session())
        self.active_patches.append(requests_patch)
        
        # Mock file operations
        pathlib_patch = patch('pathlib.Path.exists', return_value=True)
        self.active_patches.append(pathlib_patch)
        
        # Mock performance logging
        perf_patch = patch('src.utils.logging_config.log_performance', side_effect=mock_performance_logging())
        self.active_patches.append(perf_patch)
        
        # Start all patches
        mocks = {}
        for patch_obj in self.active_patches:
            mock_obj = patch_obj.start()
            mocks[patch_obj.attribute] = mock_obj
        
        return mocks

    def teardown_all_mocks(self) -> None:
        """Tear down all active mocks."""
        for patch_obj in self.active_patches:
            patch_obj.stop()
        self.active_patches.clear()

    def __enter__(self):
        return self.setup_all_mocks()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown_all_mocks()