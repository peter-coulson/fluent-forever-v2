"""
Test configuration architecture for MediaProvider base class (TDD - RED Phase).

These tests define the desired configuration injection pattern for MediaProvider.
All tests should initially FAIL until implementation is complete.
"""

import unittest
from typing import Any

from src.providers.base.media_provider import MediaProvider

from tests.unit.providers.refactor.fixtures.provider_configs import (
    INVALID_OPENAI_CONFIGS,
    MINIMAL_OPENAI_CONFIG,
    VALID_OPENAI_CONFIG,
)
from tests.unit.providers.refactor.utils.provider_test_base import ProviderTestBase


class TestMediaProviderConfiguration(ProviderTestBase):
    """Test configuration injection pattern for MediaProvider base class."""

    def test_constructor_accepts_config_parameter(self):
        """Test that MediaProvider constructor accepts optional config parameter."""
        # This test will FAIL until MediaProvider constructor is updated

        # Test with explicit config dict
        config = {"api_key": "test_key", "rate_limit_delay": 1.0}

        # Create concrete test provider class for testing
        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                # Simple validation for testing
                if "api_key" not in config:
                    raise ValueError("Missing required config key: api_key")

        # This should work when constructor is updated
        provider = TestProvider(config)
        self.assertEqual(provider.config, config)

    def test_constructor_accepts_none_config_for_backward_compatibility(self):
        """Test that MediaProvider constructor accepts None for backward compatibility."""
        # This test will FAIL until MediaProvider constructor is updated

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                # Allow empty config for backward compatibility
                pass

        # Should work with None (default parameter)
        provider = TestProvider()
        self.assertEqual(provider.config, {})

        # Should work with explicit None
        provider_explicit_none = TestProvider(None)
        self.assertEqual(provider_explicit_none.config, {})

    def test_constructor_calls_validate_config(self):
        """Test that constructor calls validate_config with provided config."""
        # This test will FAIL until MediaProvider constructor calls validate_config

        class TestProvider(MediaProvider):
            def __init__(self, config: dict[str, Any] = None):
                self.validation_called = False
                self.validation_config = None
                super().__init__(config)

            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                self.validation_called = True
                self.validation_config = config

        config = {"api_key": "test_key"}
        provider = TestProvider(config)

        # Should have called validate_config
        self.assertTrue(provider.validation_called)
        self.assertEqual(provider.validation_config, config)

    def test_constructor_calls_setup_from_config(self):
        """Test that constructor calls _setup_from_config after validation."""
        # This test will FAIL until MediaProvider constructor calls _setup_from_config

        class TestProvider(MediaProvider):
            def __init__(self, config: dict[str, Any] = None):
                self.setup_called = False
                super().__init__(config)

            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                pass

            def _setup_from_config(self) -> None:
                self.setup_called = True

        config = {"api_key": "test_key"}
        provider = TestProvider(config)

        # Should have called _setup_from_config
        self.assertTrue(provider.setup_called)


class TestMediaProviderAbstractMethods(ProviderTestBase):
    """Test abstract method enforcement for configuration."""

    def test_validate_config_is_abstract_method(self):
        """Test that validate_config is defined as abstract method."""
        # This test will FAIL until validate_config is added as abstract method

        # Try to create provider without implementing validate_config
        class IncompleteProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            # Missing validate_config implementation

        # Should raise TypeError when trying to instantiate
        with self.assertRaises(TypeError) as cm:
            IncompleteProvider()

        # Error message should mention validate_config
        self.assertIn("validate_config", str(cm.exception))

    def test_setup_from_config_method_exists(self):
        """Test that _setup_from_config method exists with default implementation."""
        # This test will FAIL until _setup_from_config is added to MediaProvider

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                pass

        provider = TestProvider({})

        # Should have _setup_from_config method
        self.assertTrue(hasattr(provider, "_setup_from_config"))
        self.assertTrue(callable(provider._setup_from_config))

        # Should be able to call it without error (default implementation)
        provider._setup_from_config()


class TestConfigurationValidation(ProviderTestBase):
    """Test configuration validation scenarios."""

    def test_valid_configuration_scenarios(self):
        """Test that valid configurations are accepted."""
        # This test will FAIL until configuration validation is implemented

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                if "api_key" not in config or not config["api_key"]:
                    raise ValueError("Missing required config key: api_key")

        # Should work with minimal valid config
        provider1 = TestProvider(MINIMAL_OPENAI_CONFIG)
        self.assertEqual(provider1.config, MINIMAL_OPENAI_CONFIG)

        # Should work with full valid config
        provider2 = TestProvider(VALID_OPENAI_CONFIG)
        self.assertEqual(provider2.config, VALID_OPENAI_CONFIG)

    def test_invalid_configuration_error_handling(self):
        """Test that invalid configurations raise appropriate errors."""
        # This test will FAIL until configuration validation is implemented

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                if "api_key" not in config or not config["api_key"]:
                    raise ValueError("Missing required config key: api_key")

                if "model" in config and config["model"] not in [
                    "dall-e-2",
                    "dall-e-3",
                ]:
                    raise ValueError(f"Invalid model: {config['model']}")

        # Should raise ValueError for missing api_key
        with self.assertRaises(ValueError) as cm:
            TestProvider(INVALID_OPENAI_CONFIGS["missing_api_key"])
        self.assertIn("Missing required config key: api_key", str(cm.exception))

        # Should raise ValueError for invalid model
        with self.assertRaises(ValueError) as cm:
            TestProvider(INVALID_OPENAI_CONFIGS["invalid_model"])
        self.assertIn("Invalid model:", str(cm.exception))

    def test_config_validation_with_empty_dict(self):
        """Test configuration validation with empty dictionary."""
        # This test will FAIL until configuration validation handles empty dict

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                # For this test, allow empty config
                if config and "api_key" in config and not config["api_key"]:
                    raise ValueError("api_key cannot be empty")

        # Should work with empty dict (backward compatibility)
        provider = TestProvider({})
        self.assertEqual(provider.config, {})


class TestBackwardCompatibility(ProviderTestBase):
    """Test backward compatibility with existing providers."""

    def test_existing_provider_instantiation_still_works(self):
        """Test that existing providers can still be instantiated without config."""
        # This test will FAIL if changes break existing provider instantiation

        class LegacyProvider(MediaProvider):
            """Simulates existing provider that doesn't use config."""

            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                # Legacy providers might have minimal validation
                pass

        # Should work without any parameters (existing pattern)
        provider = LegacyProvider()
        self.assertEqual(provider.config, {})

        # Should still have logger (existing functionality)
        self.assertTrue(hasattr(provider, "logger"))

    def test_constructor_signature_is_backward_compatible(self):
        """Test that constructor signature maintains backward compatibility."""
        # This test will FAIL if constructor signature is not backward compatible

        # Should be able to inspect constructor and see optional config parameter
        import inspect

        sig = inspect.signature(MediaProvider.__init__)
        params = list(sig.parameters.keys())

        # Should have 'self' and 'config' parameters
        self.assertIn("config", params)

        # Config parameter should have default value (None or empty dict)
        config_param = sig.parameters["config"]
        self.assertTrue(config_param.default is not inspect.Parameter.empty)


class TestConfigurationFlow(ProviderTestBase):
    """Test the complete configuration flow from constructor to setup."""

    def test_configuration_flow_order(self):
        """Test that configuration methods are called in correct order."""
        # This test will FAIL until the complete flow is implemented

        call_order = []

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                call_order.append("validate_config")
                if "api_key" not in config:
                    raise ValueError("Missing api_key")

            def _setup_from_config(self) -> None:
                call_order.append("_setup_from_config")

        config = {"api_key": "test_key"}
        provider = TestProvider(config)

        # Should have called methods in correct order
        expected_order = ["validate_config", "_setup_from_config"]
        self.assertEqual(call_order, expected_order)

        # Should have stored config
        self.assertEqual(provider.config, config)

    def test_validation_failure_prevents_setup(self):
        """Test that validation failure prevents _setup_from_config from being called."""
        # This test will FAIL until proper error handling flow is implemented

        setup_called = False

        class TestProvider(MediaProvider):
            @property
            def supported_types(self) -> list[str]:
                return ["test"]

            def _generate_media_impl(self, request):
                pass

            def get_cost_estimate(self, requests):
                return {"total": 0.0}

            def validate_config(self, config: dict[str, Any]) -> None:
                if "api_key" not in config:
                    raise ValueError("Missing required config key: api_key")

            def _setup_from_config(self) -> None:
                nonlocal setup_called
                setup_called = True

        # Should raise ValueError and not call _setup_from_config
        invalid_config = {"invalid": "config"}
        with self.assertRaises(ValueError):
            TestProvider(invalid_config)

        # Setup should not have been called due to validation failure
        self.assertFalse(setup_called)


if __name__ == "__main__":
    unittest.main()
