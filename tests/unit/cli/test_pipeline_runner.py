"""Unit tests for CLI pipeline runner."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import argparse
from pathlib import Path
from cli.pipeline_runner import create_base_parser, cmd_list, cmd_info, cmd_run
from core.registry import PipelineRegistry
from core.pipeline import Pipeline
from core.stages import StageResult, StageStatus
from core.exceptions import PipelineNotFoundError


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""
    
    @property
    def name(self) -> str:
        return "mock"
    
    @property
    def display_name(self) -> str:
        return "Mock Pipeline"
    
    @property
    def stages(self) -> list:
        return ["prepare", "process", "finish"]
    
    def get_stage(self, stage_name: str):
        return Mock()
    
    def execute_stage(self, stage_name: str, context):
        return StageResult.success(f"Executed {stage_name}", {"test": True})
    
    @property
    def data_file(self) -> str:
        return "mock.json"
    
    @property
    def anki_note_type(self) -> str:
        return "Mock"


class TestPipelineRunnerParser:
    """Test cases for argument parser."""
    
    def test_create_base_parser(self):
        """Test base parser creation."""
        parser = create_base_parser()
        
        assert isinstance(parser, argparse.ArgumentParser)
        assert "pipeline runner" in parser.description.lower()
    
    def test_list_command_parsing(self):
        """Test parsing list command."""
        parser = create_base_parser()
        args = parser.parse_args(['list'])
        
        assert args.command == 'list'
    
    def test_info_command_parsing(self):
        """Test parsing info command."""
        parser = create_base_parser()
        args = parser.parse_args(['info', 'vocabulary'])
        
        assert args.command == 'info'
        assert args.pipeline == 'vocabulary'
    
    def test_run_command_parsing(self):
        """Test parsing run command."""
        parser = create_base_parser()
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare'])
        
        assert args.command == 'run'
        assert args.pipeline == 'vocabulary'
        assert args.stage == 'prepare'
        assert not args.dry_run
    
    def test_run_command_with_dry_run(self):
        """Test parsing run command with dry-run."""
        parser = create_base_parser()
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare', '--dry-run'])
        
        assert args.command == 'run'
        assert args.pipeline == 'vocabulary'
        assert args.stage == 'prepare'
        assert args.dry_run
    
    def test_run_command_with_config(self):
        """Test parsing run command with config override."""
        parser = create_base_parser()
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare', '--config', 'custom.json'])
        
        assert args.command == 'run'
        assert args.pipeline == 'vocabulary'
        assert args.stage == 'prepare'
        assert args.config == 'custom.json'


class TestCommandFunctions:
    """Test cases for command execution functions."""
    
    def test_cmd_list_empty_registry(self):
        """Test list command with empty registry."""
        registry = PipelineRegistry()
        
        with patch('builtins.print') as mock_print:
            result = cmd_list(registry)
        
        assert result == 0
        mock_print.assert_called_with("No pipelines registered.")
    
    def test_cmd_list_with_pipelines(self):
        """Test list command with pipelines."""
        registry = PipelineRegistry()
        pipeline = MockPipeline()
        registry.register(pipeline)
        
        with patch('builtins.print') as mock_print:
            result = cmd_list(registry)
        
        assert result == 0
        # Check that pipeline info was printed
        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Available pipelines:" in call for call in calls)
        assert any("mock:" in call for call in calls)
    
    def test_cmd_info_existing_pipeline(self):
        """Test info command for existing pipeline."""
        registry = PipelineRegistry()
        pipeline = MockPipeline()
        registry.register(pipeline)
        
        with patch('builtins.print') as mock_print:
            result = cmd_info(registry, "mock")
        
        assert result == 0
        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("Pipeline: mock" in call for call in calls)
        assert any("Display Name: Mock Pipeline" in call for call in calls)
    
    def test_cmd_info_nonexistent_pipeline(self):
        """Test info command for non-existent pipeline."""
        registry = PipelineRegistry()
        
        with patch('builtins.print') as mock_print:
            result = cmd_info(registry, "nonexistent")
        
        assert result == 1
        mock_print.assert_called_with("Error: Pipeline 'nonexistent' not found")
    
    def test_cmd_run_dry_run(self):
        """Test run command with dry-run."""
        registry = PipelineRegistry()
        pipeline = MockPipeline()
        registry.register(pipeline)
        
        args = Mock()
        args.dry_run = True
        
        with patch('builtins.print') as mock_print:
            result = cmd_run(registry, "mock", "prepare", Path("/test"), args)
        
        assert result == 0
        mock_print.assert_called_with("Would execute stage 'prepare' on pipeline 'mock'")
    
    def test_cmd_run_success(self):
        """Test successful run command execution."""
        registry = PipelineRegistry()
        pipeline = MockPipeline()
        registry.register(pipeline)
        
        args = Mock()
        args.dry_run = False
        
        with patch('builtins.print') as mock_print:
            result = cmd_run(registry, "mock", "prepare", Path("/test"), args)
        
        assert result == 0
        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("completed with status: success" in call for call in calls)
    
    def test_cmd_run_failure(self):
        """Test failed run command execution."""
        registry = PipelineRegistry()
        pipeline = MockPipeline()
        # Mock execute_stage to return failure
        pipeline.execute_stage = Mock(return_value=StageResult.failure("Stage failed", ["Error"]))
        registry.register(pipeline)
        
        args = Mock()
        args.dry_run = False
        
        with patch('builtins.print') as mock_print:
            result = cmd_run(registry, "mock", "prepare", Path("/test"), args)
        
        assert result == 1
        calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("completed with status: failure" in call for call in calls)
        assert any("Errors:" in call for call in calls)
    
    def test_cmd_run_nonexistent_pipeline(self):
        """Test run command for non-existent pipeline."""
        registry = PipelineRegistry()
        args = Mock()
        
        with patch('builtins.print') as mock_print:
            result = cmd_run(registry, "nonexistent", "prepare", Path("/test"), args)
        
        assert result == 1
        mock_print.assert_called_with("Error: Pipeline 'nonexistent' not found")