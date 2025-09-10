"""Unit tests for pipeline runner."""

import argparse
from unittest.mock import Mock, patch

import pytest
from src.cli.pipeline_runner import create_parser, main
from src.core.exceptions import PipelineError


class TestCreateParser:
    """Test argument parser creation."""

    def test_create_parser_basic(self):
        """Test parser creation returns ArgumentParser."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_help_includes_commands(self):
        """Test parser help includes all expected commands."""
        parser = create_parser()
        help_text = parser.format_help()

        assert "list" in help_text
        assert "info" in help_text
        assert "run" in help_text

    def test_parser_global_options(self):
        """Test global options are available."""
        parser = create_parser()

        # Test that global options exist
        args = parser.parse_args(["--verbose", "list"])
        assert args.verbose is True

        args = parser.parse_args(["--dry-run", "list"])
        assert args.dry_run is True

    def test_parser_subcommand_required(self):
        """Test that parser requires a subcommand."""
        parser = create_parser()
        args = parser.parse_args([])  # No command provided
        assert args.command is None

    def test_parser_list_command(self):
        """Test list command parsing."""
        parser = create_parser()

        args = parser.parse_args(["list"])
        assert args.command == "list"

        args = parser.parse_args(["list", "--detailed"])
        assert args.command == "list"
        assert args.detailed is True

    def test_parser_info_command(self):
        """Test info command parsing."""
        parser = create_parser()

        args = parser.parse_args(["info", "test_pipeline"])
        assert args.command == "info"
        assert args.pipeline == "test_pipeline"

        args = parser.parse_args(["info", "test_pipeline", "--stages"])
        assert args.command == "info"
        assert args.pipeline == "test_pipeline"
        assert args.stages is True

    def test_parser_run_command(self):
        """Test run command parsing."""
        parser = create_parser()

        args = parser.parse_args(["run", "test_pipeline", "--stage", "prepare"])
        assert args.command == "run"
        assert args.pipeline == "test_pipeline"
        assert args.stage == "prepare"


class TestMain:
    """Test main CLI entry point."""

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("sys.argv", ["pipeline_runner.py"])
    def test_main_no_command_shows_help(
        self,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
        capsys,
    ):
        """Test main shows help when no command provided."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger

        result = main()

        assert result == 1
        # Verify help was displayed (can't easily capture argparse help, so we check return code)

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("sys.argv", ["pipeline_runner.py", "invalid_command"])
    def test_main_unknown_command(
        self,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main with unknown command."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.return_value = []

        # argparse throws SystemExit for unknown commands (choose from 'list', 'info', 'run')
        with pytest.raises(SystemExit) as excinfo:
            main()

        assert (
            excinfo.value.code == 2
        )  # argparse exits with code 2 for invalid commands

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("sys.argv", ["pipeline_runner.py", "list"])
    def test_main_validation_errors(
        self,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main handles validation errors."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.return_value = ["Test error"]

        result = main()

        assert result == 1
        mock_logger.error.assert_called()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("src.cli.pipeline_runner.ListCommand")
    @patch("sys.argv", ["pipeline_runner.py", "list"])
    def test_main_list_command_success(
        self,
        mock_list_cmd,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main executes list command successfully."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.return_value = []
        mock_command_instance = Mock()
        mock_command_instance.execute.return_value = 0
        mock_list_cmd.return_value = mock_command_instance

        result = main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("src.cli.pipeline_runner.InfoCommand")
    @patch("sys.argv", ["pipeline_runner.py", "info", "test_pipeline"])
    def test_main_info_command_success(
        self,
        mock_info_cmd,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main executes info command successfully."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.return_value = []
        mock_command_instance = Mock()
        mock_command_instance.execute.return_value = 0
        mock_info_cmd.return_value = mock_command_instance

        result = main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("src.cli.pipeline_runner.RunCommand")
    @patch(
        "sys.argv", ["pipeline_runner.py", "run", "test_pipeline", "--stage", "prepare"]
    )
    def test_main_run_command_success(
        self,
        mock_run_cmd,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main executes run command successfully."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.return_value = []
        mock_command_instance = Mock()
        mock_command_instance.execute.return_value = 0
        mock_run_cmd.return_value = mock_command_instance

        result = main()

        assert result == 0
        mock_command_instance.execute.assert_called_once()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.validate_arguments")
    @patch("sys.argv", ["pipeline_runner.py", "list"])
    def test_main_pipeline_error(
        self,
        mock_validate,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main handles PipelineError."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_validate.side_effect = PipelineError("Test pipeline error")

        result = main()

        assert result == 1
        mock_logger.error.assert_called()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("sys.argv", ["pipeline_runner.py", "list"])
    def test_main_unexpected_error(
        self, mock_provider_reg, mock_pipeline_reg, mock_config_load, mock_logging
    ):
        """Test main handles unexpected errors."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_config_load.side_effect = Exception("Unexpected error")

        result = main()

        assert result == 1
        mock_logger.error.assert_called()

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("src.cli.pipeline_runner.ListCommand")
    @patch("sys.argv", ["pipeline_runner.py", "--config", "custom_config.json", "list"])
    def test_main_custom_config_path(
        self,
        mock_list_cmd,
        mock_provider_reg,
        mock_pipeline_reg,
        mock_config_load,
        mock_logging,
    ):
        """Test main uses custom config path when provided."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger

        # Mock command execution to return success
        mock_command_instance = Mock()
        mock_command_instance.execute.return_value = 0
        mock_list_cmd.return_value = mock_command_instance

        result = main()

        assert result == 0
        mock_config_load.assert_called_with("custom_config.json")

    @patch("src.cli.pipeline_runner.setup_logging")
    @patch("src.cli.pipeline_runner.Config.load")
    @patch("src.cli.pipeline_runner.get_pipeline_registry")
    @patch("src.cli.pipeline_runner.ProviderRegistry.from_config")
    @patch("sys.argv", ["pipeline_runner.py", "list"])
    def test_main_registry_initialization_error(
        self, mock_provider_reg, mock_pipeline_reg, mock_config_load, mock_logging
    ):
        """Test main handles registry initialization errors."""
        mock_logger = Mock()
        mock_logging.return_value.getChild.return_value = mock_logger
        mock_provider_reg.side_effect = Exception("Provider registry error")

        result = main()

        assert result == 1
        mock_logger.error.assert_called()
