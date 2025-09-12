"""Test to validate the new test infrastructure works correctly."""

from pathlib import Path

from tests.unit.providers.refactor.fixtures.mock_responses import (
    FORVO_SUCCESS_RESPONSE,
    OPENAI_DALLE_SUCCESS_RESPONSE,
)
from tests.unit.providers.refactor.fixtures.provider_configs import (
    INVALID_OPENAI_CONFIGS,
    VALID_OPENAI_CONFIG,
)
from tests.unit.providers.refactor.utils.mock_factories import MockAPIFactory
from tests.unit.providers.refactor.utils.provider_test_base import ProviderTestBase


class TestInfrastructureValidation(ProviderTestBase):
    """Validate that the new test infrastructure works as expected."""

    def test_provider_test_base_setup_creates_temp_directory(self):
        """Test that setUp creates a temporary directory."""
        self.assertIsNotNone(self.temp_dir)
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue(Path(self.temp_dir).is_dir())

    def test_provider_test_base_get_test_config_returns_dict(self):
        """Test that get_test_config returns expected configuration."""
        config = self.get_test_config()
        self.assertIsInstance(config, dict)
        self.assertIn("api_key", config)
        self.assertIn("rate_limit_delay", config)
        self.assertIn("max_retries", config)

    def test_provider_test_base_create_test_file_works(self):
        """Test that create_test_file creates files correctly."""
        content = b"test file content"
        file_path = self.create_test_file("test.txt", content)

        self.assert_file_exists(file_path)
        self.assert_file_contains(file_path, content)

    def test_mock_api_factory_creates_openai_success_response(self):
        """Test that MockAPIFactory creates valid OpenAI responses."""
        urls = ["https://test1.png", "https://test2.png"]
        response = MockAPIFactory.create_openai_success_response(urls)

        self.assertIsNotNone(response)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].url, urls[0])
        self.assertEqual(response.data[1].url, urls[1])

    def test_mock_api_factory_creates_openai_error_response(self):
        """Test that MockAPIFactory creates error responses."""
        error_msg = "Test error message"
        response = MockAPIFactory.create_openai_error_response(error_msg)

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.side_effect)

        with self.assertRaises(Exception) as cm:
            raise response.side_effect
        self.assertEqual(str(cm.exception), error_msg)

    def test_mock_api_factory_creates_forvo_success_response(self):
        """Test that MockAPIFactory creates valid Forvo responses."""
        audio_data = b"fake audio content"
        response = MockAPIFactory.create_forvo_success_response(audio_data)

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, audio_data)
        self.assertEqual(response.headers["Content-Type"], "audio/mpeg")

    def test_provider_configs_are_available(self):
        """Test that provider configuration fixtures are accessible."""
        self.assertIsInstance(VALID_OPENAI_CONFIG, dict)
        self.assertIn("api_key", VALID_OPENAI_CONFIG)

        self.assertIsInstance(INVALID_OPENAI_CONFIGS, dict)
        self.assertIn("missing_api_key", INVALID_OPENAI_CONFIGS)

    def test_mock_responses_are_available(self):
        """Test that mock response fixtures are accessible."""
        self.assertIsInstance(OPENAI_DALLE_SUCCESS_RESPONSE, dict)
        self.assertIn("data", OPENAI_DALLE_SUCCESS_RESPONSE)

        self.assertIsInstance(FORVO_SUCCESS_RESPONSE, dict)
        self.assertIn("items", FORVO_SUCCESS_RESPONSE)

    def test_teardown_cleans_up_temp_directory(self):
        """Test that tearDown properly cleans up."""
        # Create a file to ensure directory has content
        test_file = self.create_test_file("cleanup_test.txt")
        temp_dir_path = Path(self.temp_dir)

        # Verify directory and file exist
        self.assertTrue(temp_dir_path.exists())
        self.assertTrue(Path(test_file).exists())

        # Manually call tearDown to test cleanup
        # Note: This will be called again automatically, but that's okay
        self.tearDown()

        # Verify cleanup worked
        self.assertFalse(temp_dir_path.exists())


class TestNamingConventionExample(ProviderTestBase):
    """Example test class following naming conventions."""

    def test_constructor_with_valid_config_succeeds(self):
        """Test that valid config would create provider successfully."""
        config = VALID_OPENAI_CONFIG
        # This test demonstrates the naming pattern
        # Implementation will be added in later stages
        self.assertIsInstance(config, dict)

    def test_constructor_with_invalid_config_raises_value_error(self):
        """Test that invalid config would raise ValueError."""
        invalid_config = INVALID_OPENAI_CONFIGS["missing_api_key"]
        # This test demonstrates the naming pattern
        # Implementation will be added in later stages
        self.assertNotIn("api_key", invalid_config)
