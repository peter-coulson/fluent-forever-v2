import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any


class ProviderTestBase(unittest.TestCase):
    """Base class for provider testing with common utilities."""

    def setUp(self):
        """Common setup for provider tests."""
        self.mock_config = self.get_test_config()
        self.temp_dir = self.create_temp_directory()

    def tearDown(self):
        """Common cleanup for provider tests."""
        if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def get_test_config(self) -> dict[str, Any]:
        """Get standard test configuration."""
        return {"api_key": "test_api_key", "rate_limit_delay": 0.1, "max_retries": 2}

    def create_temp_directory(self) -> str:
        """Create temporary directory for test files."""
        return tempfile.mkdtemp(prefix="provider_test_")

    def assert_config_validation_error(
        self, config: dict[str, Any], expected_error: str
    ):
        """Assert that config validation raises expected error."""
        with self.assertRaises(ValueError) as cm:
            # This will be filled in during implementation stages
            # when we have actual provider classes to test
            pass

        if expected_error:
            self.assertIn(expected_error, str(cm.exception))

    def create_test_file(self, filename: str, content: bytes = b"test content") -> str:
        """Create a test file in the temporary directory."""
        file_path = Path(self.temp_dir) / filename
        file_path.write_bytes(content)
        return str(file_path)

    def assert_file_exists(self, file_path: str):
        """Assert that a file exists."""
        self.assertTrue(Path(file_path).exists(), f"File does not exist: {file_path}")

    def assert_file_contains(self, file_path: str, expected_content: bytes):
        """Assert that a file contains expected content."""
        self.assert_file_exists(file_path)
        actual_content = Path(file_path).read_bytes()
        self.assertEqual(actual_content, expected_content)
