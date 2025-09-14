"""Integration tests for CLI command integration with registries."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.cli.commands.info_command import InfoCommand
from src.cli.commands.list_command import ListCommand
from src.cli.commands.run_command import RunCommand
from src.core.config import Config
from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry

from tests.fixtures.mock_implementations import MockPipeline


class TestCLIRegistryIntegration:
    """Test CLI command integration with registries."""

    @pytest.fixture
    def empty_registry(self):
        """Create empty pipeline registry for testing."""
        return PipelineRegistry()

    @pytest.fixture
    def populated_registry(self):
        """Create pipeline registry with test pipelines."""
        registry = PipelineRegistry()
        registry.register(MockPipeline("vocabulary"))
        registry.register(MockPipeline("grammar"))
        return registry

    @pytest.fixture
    def empty_config(self):
        """Create empty config for testing."""
        config = Config()
        config._config_data = {}
        return config

    @pytest.fixture
    def mock_args(self):
        """Create mock args for testing."""
        return MagicMock()

    def test_list_command_empty_registry(
        self, empty_registry, empty_config, mock_args, capsys
    ):
        """Test list command with empty registry."""
        command = ListCommand(empty_registry, empty_config)

        # Execute command
        result = command.execute(mock_args)

        # Verify successful execution
        assert result == 0

        # Check output
        captured = capsys.readouterr()
        assert "No pipelines registered" in captured.out

    def test_list_command_populated_registry(
        self, populated_registry, empty_config, mock_args, capsys
    ):
        """Test list command with populated registry."""
        command = ListCommand(populated_registry, empty_config)

        # Execute command
        result = command.execute(mock_args)

        # Verify successful execution
        assert result == 0

        # Check output contains pipeline names
        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "grammar" in captured.out

    def test_list_command_detailed(
        self, populated_registry, empty_config, mock_args, capsys
    ):
        """Test list command with detailed output."""
        # Set detailed flag
        mock_args.detailed = True

        command = ListCommand(populated_registry, empty_config)
        result = command.execute(mock_args)

        assert result == 0

        # Detailed output should include more information
        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "grammar" in captured.out
        # Should contain headers from table format
        assert "Name" in captured.out or "Display Name" in captured.out

    def test_info_command_existing_pipeline(
        self, populated_registry, empty_config, mock_args, capsys
    ):
        """Test info command with existing pipeline."""
        mock_args.pipeline = "vocabulary"
        mock_args.stages = False

        command = InfoCommand(populated_registry, empty_config)
        result = command.execute(mock_args)

        assert result == 0

        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "Mock Vocabulary Pipeline" in captured.out

    def test_info_command_non_existent_pipeline(
        self, empty_registry, empty_config, mock_args, capsys
    ):
        """Test info command with non-existent pipeline."""
        mock_args.pipeline = "non_existent"

        command = InfoCommand(empty_registry, empty_config)
        result = command.execute(mock_args)

        assert result == 1  # Error exit code

        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_info_command_with_stages(
        self, populated_registry, empty_config, mock_args, capsys
    ):
        """Test info command with stages details."""
        mock_args.pipeline = "vocabulary"
        mock_args.stages = True

        command = InfoCommand(populated_registry, empty_config)
        result = command.execute(mock_args)

        assert result == 0

        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "Available Stages" in captured.out

    def test_run_command_no_pipelines(self, empty_registry, empty_config, mock_args):
        """Test run command with empty registry."""
        mock_args.pipeline = "non_existent"
        mock_args.stage = "test_stage"
        mock_args.dry_run = False

        provider_registry = ProviderRegistry()
        project_root = Path(".")

        command = RunCommand(
            empty_registry, provider_registry, project_root, empty_config
        )
        result = command.execute(mock_args)

        assert result == 1  # Error exit code

    def test_run_command_dry_run(
        self, populated_registry, empty_config, mock_args, capsys
    ):
        """Test run command with dry-run mode."""
        mock_args.pipeline = "vocabulary"
        mock_args.stage = "prepare"
        mock_args.dry_run = True

        provider_registry = ProviderRegistry()
        project_root = Path(".")

        command = RunCommand(
            populated_registry, provider_registry, project_root, empty_config
        )
        result = command.execute(mock_args)

        assert result == 0

        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "vocabulary" in captured.out
        assert "prepare" in captured.out

    def test_run_command_pipeline_validation_error(
        self, populated_registry, empty_config, mock_args
    ):
        """Test run command with pipeline validation errors."""
        # Create args that will fail pipeline validation
        mock_args.pipeline = "vocabulary"
        mock_args.stage = "test_stage"
        mock_args.dry_run = False
        mock_args.required_arg = (
            None  # This will cause validation failure in MockPipeline
        )

        provider_registry = ProviderRegistry()
        project_root = Path(".")

        command = RunCommand(
            populated_registry, provider_registry, project_root, empty_config
        )
        result = command.execute(mock_args)

        # Should fail due to validation error
        assert result == 1

    def test_run_command_context_creation(
        self, populated_registry, empty_config, mock_args
    ):
        """Test that run command creates context with providers."""
        mock_args.pipeline = "vocabulary"
        mock_args.stage = "prepare"
        mock_args.dry_run = True  # Use dry-run to avoid actual execution

        # Create provider registry with minimal setup
        provider_registry = ProviderRegistry()
        project_root = Path(".")

        command = RunCommand(
            populated_registry, provider_registry, project_root, empty_config
        )

        # Execute dry run (which creates context but doesn't execute)
        result = command.execute(mock_args)

        assert result == 0

    def test_cli_error_propagation(self, empty_config, mock_args):
        """Test that registry errors propagate to CLI with user-friendly messages."""
        # Create registry that will raise exception
        problematic_registry = MagicMock()
        problematic_registry.get.side_effect = Exception("Registry internal error")

        mock_args.pipeline = "test"
        mock_args.stage = "test"
        mock_args.dry_run = False

        provider_registry = ProviderRegistry()
        project_root = Path(".")

        command = RunCommand(
            problematic_registry, provider_registry, project_root, empty_config
        )
        result = command.execute(mock_args)

        # Should handle error gracefully
        assert result == 1

    def test_cli_commands_with_real_registries(self, tmp_path):
        """Test CLI commands work with real registry instances."""
        # Create config file
        config_path = tmp_path / "test_config.json"
        config_content = """{
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": "./test_data",
                        "pipelines": ["*"]
                    }
                }
            }
        }"""
        config_path.write_text(config_content)

        # Load real config
        config = Config.load(str(config_path))

        # Create real registries
        pipeline_registry = PipelineRegistry()
        provider_registry = ProviderRegistry.from_config(config)

        # Add test pipeline
        pipeline_registry.register(MockPipeline("test_pipeline"))

        # Test list command
        mock_args = MagicMock()
        list_command = ListCommand(pipeline_registry, config)
        assert list_command.execute(mock_args) == 0

        # Test info command
        mock_args.pipeline = "test_pipeline"
        mock_args.stages = False
        info_command = InfoCommand(pipeline_registry, config)
        assert info_command.execute(mock_args) == 0

        # Test run command (dry-run)
        mock_args.stage = "prepare"
        mock_args.dry_run = True
        project_root = Path(".")
        run_command = RunCommand(
            pipeline_registry, provider_registry, project_root, config
        )
        assert run_command.execute(mock_args) == 0
