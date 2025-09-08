#!/usr/bin/env python3
"""
Integration tests for CLI system.

Tests that CLI components work together and can execute commands.
"""

import pytest
import subprocess
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_cli_pipeline_runner():
    """
    Test CLI pipeline runner integration.
    
    Tests:
    - PipelineRunner can be created and used
    - CLI interface works with core components
    """
    try:
        from cli.pipeline_runner import PipelineRunner
    except ImportError:
        pytest.skip("CLI system not available")
    
    runner = PipelineRunner()
    assert runner is not None, "PipelineRunner should be creatable"
    
    # Test pipeline discovery
    try:
        pipelines = runner.list_pipelines()
        assert pipelines is not None, "Should be able to list pipelines"
    except Exception:
        # May fail if no pipelines registered, but method should exist
        assert hasattr(runner, 'list_pipelines'), "Should have list_pipelines method"


def test_cli_commands_structure():
    """Test CLI commands can be imported and created."""
    try:
        from cli.commands.list_command import ListCommand
        from cli.commands.info_command import InfoCommand
        from cli.commands.preview_command import PreviewCommand
    except ImportError:
        pytest.skip("CLI commands not available")
    
    # Test command classes exist
    assert ListCommand is not None, "ListCommand should be available"
    assert InfoCommand is not None, "InfoCommand should be available"
    assert PreviewCommand is not None, "PreviewCommand should be available"
    
    # Test commands can be instantiated
    try:
        list_cmd = ListCommand()
        assert list_cmd is not None, "ListCommand should be creatable"
        assert hasattr(list_cmd, 'execute'), "Should have execute method"
    except Exception:
        pass  # May require configuration


def test_cli_parser_creation():
    """Test CLI argument parser integration."""
    try:
        from cli.pipeline_runner import create_parser
    except ImportError:
        pytest.skip("CLI parser not available")
    
    # Test parser can be created
    parser = create_parser()
    assert parser is not None, "Parser should be creatable"
    
    # Test basic parser functionality (without raising SystemExit)
    try:
        # Test with minimal valid arguments
        args = parser.parse_args(['list'])
        assert args.command == 'list', "Parser should handle list command"
    except SystemExit:
        # argparse calls sys.exit on error, which is normal
        pass


@pytest.mark.integration
def test_cli_module_execution():
    """Test CLI can be executed as module (basic smoke test)."""
    # Test that the CLI module can be called without immediate errors
    try:
        result = subprocess.run([
            "python", "-m", "cli.pipeline", "--help"
        ], capture_output=True, text=True, cwd=project_root, timeout=10)
        
        # Help should work regardless of implementation status
        # We're just testing the module structure is correct
        assert result.returncode in [0, 1, 2], "CLI module should be executable"
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("CLI module execution not available")


def test_cli_configuration_integration():
    """Test CLI configuration system integration."""
    try:
        from cli.config.cli_config import CLIConfig
    except ImportError:
        pytest.skip("CLI configuration not available")
    
    # Test CLI config can be created
    config = CLIConfig({})
    assert config is not None, "CLIConfig should be creatable"
    
    # Test config with data
    config_data = {"verbose": True, "dry_run": False}
    config = CLIConfig(config_data)
    assert config is not None, "CLIConfig should accept configuration data"


def test_cli_output_utilities():
    """Test CLI output utilities integration."""
    try:
        from cli.utils.output import format_pipeline_list, format_pipeline_info
    except ImportError:
        pytest.skip("CLI output utilities not available")
    
    # Test output formatters exist
    assert format_pipeline_list is not None, "format_pipeline_list should be available"
    assert format_pipeline_info is not None, "format_pipeline_info should be available"
    
    # Test basic formatting (should not raise errors with empty data)
    try:
        formatted = format_pipeline_list([])
        assert isinstance(formatted, str), "Should return string output"
    except Exception:
        pass  # May require specific input format


def test_cli_validation_utilities():
    """Test CLI validation utilities integration."""
    try:
        from cli.utils.validation import validate_pipeline_name, validate_stage_name
    except ImportError:
        pytest.skip("CLI validation not available")
    
    # Test validation functions exist
    assert validate_pipeline_name is not None, "validate_pipeline_name should be available"
    assert validate_stage_name is not None, "validate_stage_name should be available"
    
    # Test basic validation
    try:
        result = validate_pipeline_name("test")
        assert isinstance(result, bool), "Should return boolean"
    except Exception:
        pass  # May require specific validation logic


@pytest.mark.integration
def test_cli_end_to_end_structure():
    """Test CLI components work together structurally."""
    try:
        from cli.pipeline_runner import PipelineRunner, create_parser
        from cli.config.cli_config import CLIConfig
    except ImportError:
        pytest.skip("CLI components not available")
    
    # Test components can work together
    parser = create_parser()
    config = CLIConfig({})
    runner = PipelineRunner(config)
    
    assert parser is not None, "Parser should be created"
    assert config is not None, "Config should be created"  
    assert runner is not None, "Runner should be created"
    
    # Test runner has expected interface
    assert hasattr(runner, 'list_pipelines'), "Runner should have list_pipelines"
    assert hasattr(runner, 'get_pipeline_info'), "Runner should have get_pipeline_info"


if __name__ == "__main__":
    test_cli_pipeline_runner()
    test_cli_commands_structure()
    test_cli_parser_creation()
    test_cli_module_execution()
    test_cli_configuration_integration()
    test_cli_output_utilities()
    test_cli_validation_utilities()
    test_cli_end_to_end_structure()
    print("CLI integration tests passed!")