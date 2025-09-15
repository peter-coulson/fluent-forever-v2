"""
E2E Test Scenario 1: CLI Pipeline Discovery and Information Flow

Purpose: Validate complete CLI → Registry → Provider workflow without business logic
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from src.cli.pipeline_runner import main
from src.core.config import Config
from src.core.registry import get_pipeline_registry
from src.providers.registry import ProviderRegistry
from tests.fixtures.configs import ConfigFixture, create_base_config
from tests.fixtures.pipelines import MockPipeline
from tests.utils.assertions import (
    assert_cli_output_contains,
    assert_config_loaded_correctly,
    assert_pipeline_info_complete,
    assert_providers_registered,
)
from tests.utils.mocks import MockEnvironment, create_mock_cli_args


class TestCLIPipelineIntegration:
    """Test CLI pipeline discovery and information flow."""

    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return create_base_config()

    @pytest.fixture
    def config_file(self, test_config):
        """Create temporary config file."""
        with ConfigFixture(test_config) as config_path:
            yield config_path

    @pytest.fixture
    def pipeline_registry(self):
        """Create pipeline registry with test pipelines."""
        registry = get_pipeline_registry()
        # Clear any existing pipelines
        registry._pipelines.clear()
        
        # Register test pipelines
        test_pipeline = MockPipeline("test_pipeline")
        vocabulary_pipeline = MockPipeline("vocabulary", ["prepare", "validate", "sync"])
        
        registry.register(test_pipeline)
        registry.register(vocabulary_pipeline)
        
        yield registry
        
        # Cleanup
        registry._pipelines.clear()

    @pytest.fixture
    def provider_registry(self, config_file):
        """Create provider registry from config."""
        config = Config.load(str(config_file))
        return ProviderRegistry.from_config(config)

    def test_cli_list_command_basic(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test basic CLI list command execution."""
        # Prepare CLI arguments
        test_args = ["--config", str(config_file), "list"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Validate CLI output contains pipeline information
        assert_cli_output_contains(captured.out, "test_pipeline")
        assert_cli_output_contains(captured.out, "vocabulary")

    def test_cli_list_command_detailed(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test detailed CLI list command execution."""
        test_args = ["--config", str(config_file), "list", "--detailed"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Validate detailed output
        assert_cli_output_contains(captured.out, "Test Pipeline")
        assert_cli_output_contains(captured.out, "test_data.json")

    def test_cli_info_command_pipeline(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test CLI info command for pipeline information."""
        test_args = ["--config", str(config_file), "info", "test_pipeline"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Validate pipeline info output
        assert_cli_output_contains(captured.out, "test_pipeline")
        assert_cli_output_contains(captured.out, "Test Pipeline")

    def test_cli_info_command_stages(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test CLI info command with stages flag."""
        test_args = ["--config", str(config_file), "info", "vocabulary", "--stages"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Validate stage information is displayed
        assert_cli_output_contains(captured.out, "prepare")
        assert_cli_output_contains(captured.out, "validate")
        assert_cli_output_contains(captured.out, "sync")

    def test_configuration_loading(self, config_file):
        """Test configuration loading with environment substitution."""
        with MockEnvironment({"FORVO_API_KEY": "env_test_key", "LOG_LEVEL": "DEBUG"}):
            config = Config.load(str(config_file))
            
            # Validate configuration loaded correctly
            assert_config_loaded_correctly(config, ["providers", "system"])
            
            # Check environment variable substitution
            forvo_config = config.get("providers.audio.test_audio")
            assert forvo_config["api_key"] == "env_test_key"

    def test_pipeline_registry_initialization(self, pipeline_registry):
        """Test pipeline registry initialization and discovery."""
        # Validate pipelines are registered
        pipeline_names = pipeline_registry.list_pipelines()
        assert "test_pipeline" in pipeline_names
        assert "vocabulary" in pipeline_names
        
        # Validate pipeline info retrieval
        test_info = pipeline_registry.get_pipeline_info("test_pipeline")
        assert_pipeline_info_complete(test_info)

    def test_provider_registry_creation(self, provider_registry):
        """Test provider registry creation from configuration."""
        # Validate providers are registered
        assert_providers_registered(provider_registry, "data", ["test_data"])
        assert_providers_registered(provider_registry, "audio", ["test_audio"])
        assert_providers_registered(provider_registry, "image", ["test_image"])
        assert_providers_registered(provider_registry, "sync", ["test_sync"])

    def test_logging_system_initialization(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test logging system initialization and context handling."""
        test_args = ["--config", str(config_file), "--verbose", "list"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Check for logging output (icons and context-aware messages)
        output = captured.out + captured.err
        # In verbose mode, we should see logging output
        assert "Starting Fluent Forever" in output or "Command:" in output

    def test_cli_error_handling_invalid_command(self, config_file, capsys):
        """Test CLI error handling for invalid commands."""
        test_args = ["--config", str(config_file), "invalid_command"]
        
        import pytest
        with pytest.raises(SystemExit) as exc_info:
            main(test_args)
        
        assert exc_info.value.code == 2  # argparse exits with 2 for invalid commands
        captured = capsys.readouterr()
        
        # Should show help or error message
        assert "invalid_command" in captured.err or "help" in captured.out.lower()

    def test_cli_error_handling_missing_pipeline(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test CLI error handling for missing pipeline."""
        test_args = ["--config", str(config_file), "info", "nonexistent_pipeline"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 1
        captured = capsys.readouterr()
        
        # Should contain error about pipeline not found
        error_output = captured.err
        assert "not found" in error_output.lower() or "nonexistent_pipeline" in error_output

    def test_environment_variable_handling(self, config_file):
        """Test environment variable processing in configuration."""
        env_vars = {
            "FORVO_API_KEY": "production_key",
            "OPENAI_API_KEY": "production_openai_key",
            "LOG_LEVEL": "WARNING"
        }
        
        with MockEnvironment(env_vars):
            config = Config.load(str(config_file))
            
            # Validate environment variables were substituted
            audio_config = config.get("providers.audio.test_audio")
            assert audio_config["api_key"] == "production_key"
            
            image_config = config.get("providers.image.test_image") 
            assert image_config["api_key"] == "production_openai_key"

    def test_cli_argument_validation(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test CLI argument validation."""
        # Test missing required arguments
        test_args = ["--config", str(config_file), "run"]  # Missing pipeline and stage/phase
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                import pytest
                with pytest.raises(SystemExit) as exc_info:
                    main(test_args)
        
        assert exc_info.value.code == 2  # argparse exits with 2 for argument errors
        captured = capsys.readouterr()
        
        # Should contain argument validation error
        error_output = captured.err
        assert "required" in error_output.lower() or "argument" in error_output.lower()

    def test_complete_discovery_workflow(self, config_file, pipeline_registry, provider_registry):
        """Test complete discovery workflow: Config → Registry → Provider setup."""
        # Test the complete workflow from configuration loading to provider setup
        
        # 1. Configuration loading
        config = Config.load(str(config_file))
        assert config.get("providers") is not None
        
        # 2. Pipeline registry setup
        assert len(pipeline_registry.list_pipelines()) >= 2
        
        # 3. Provider registry creation and validation
        provider_info = provider_registry.get_provider_info()
        assert provider_info["data_providers"]["count"] >= 1
        assert provider_info["audio_providers"]["count"] >= 1
        assert provider_info["image_providers"]["count"] >= 1
        assert provider_info["sync_providers"]["count"] >= 1
        
        # 4. Pipeline-provider integration
        test_providers = provider_registry.get_providers_for_pipeline("test_pipeline")
        assert "test_data" in test_providers["data"]
        assert "test_audio" in test_providers["audio"]
        assert "test_image" in test_providers["image"]
        assert "test_sync" in test_providers["sync"]

    def test_output_formatting(self, config_file, pipeline_registry, provider_registry, capsys):
        """Test CLI output formatting and display."""
        test_args = ["--config", str(config_file), "list", "--detailed"]
        
        with patch('src.cli.pipeline_runner.get_pipeline_registry', return_value=pipeline_registry):
            with patch('src.cli.pipeline_runner.ProviderRegistry.from_config', return_value=provider_registry):
                result = main(test_args)
        
        assert result == 0
        captured = capsys.readouterr()
        
        # Validate structured output
        output_lines = [line.strip() for line in captured.out.split('\n') if line.strip()]
        assert len(output_lines) > 0
        
        # Should contain formatted pipeline information
        pipeline_info_found = any("pipeline" in line.lower() for line in output_lines)
        assert pipeline_info_found