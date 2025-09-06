"""Unit tests for pipeline runner."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from cli.pipeline_runner import PipelineRunner, create_parser
from cli.config.cli_config import CLIConfig


class TestPipelineRunner:
    """Test PipelineRunner class."""
    
    @patch('cli.pipeline_runner.get_pipeline_registry')
    @patch('cli.pipeline_runner.get_provider_registry')
    def test_init(self, mock_provider_registry, mock_pipeline_registry):
        """Test PipelineRunner initialization."""
        # Setup mocks
        mock_pipeline_reg = Mock()
        mock_provider_reg = Mock()
        mock_pipeline_registry.return_value = mock_pipeline_reg
        mock_provider_registry.return_value = mock_provider_reg
        
        # Test initialization
        config = CLIConfig({})
        runner = PipelineRunner(config)
        
        # Verify initialization
        assert runner.config == config
        assert runner.pipeline_registry == mock_pipeline_reg
        assert runner.provider_registry == mock_provider_reg
        assert isinstance(runner.project_root, Path)
    
    @patch('cli.pipeline_runner.get_pipeline_registry')
    @patch('cli.pipeline_runner.get_provider_registry')
    def test_list_pipelines(self, mock_provider_registry, mock_pipeline_registry):
        """Test listing pipelines."""
        # Setup mocks
        mock_pipeline_reg = Mock()
        mock_pipeline_reg.list_pipelines.return_value = ['vocabulary', 'conjugation']
        mock_pipeline_registry.return_value = mock_pipeline_reg
        mock_provider_registry.return_value = Mock()
        
        # Test
        runner = PipelineRunner()
        result = runner.list_pipelines()
        
        # Verify
        assert result == ['vocabulary', 'conjugation']
        mock_pipeline_reg.list_pipelines.assert_called_once()
    
    @patch('cli.pipeline_runner.get_pipeline_registry')
    @patch('cli.pipeline_runner.get_provider_registry')
    def test_get_pipeline_info(self, mock_provider_registry, mock_pipeline_registry):
        """Test getting pipeline info."""
        # Setup mocks
        mock_pipeline_reg = Mock()
        expected_info = {'name': 'vocabulary', 'stages': ['prepare', 'media']}
        mock_pipeline_reg.get_pipeline_info.return_value = expected_info
        mock_pipeline_registry.return_value = mock_pipeline_reg
        mock_provider_registry.return_value = Mock()
        
        # Test
        runner = PipelineRunner()
        result = runner.get_pipeline_info('vocabulary')
        
        # Verify
        assert result == expected_info
        mock_pipeline_reg.get_pipeline_info.assert_called_once_with('vocabulary')


class TestCreateParser:
    """Test create_parser function."""
    
    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        
        # Test basic structure
        assert parser is not None
        assert parser.description is not None
        
        # Test help output (should not raise exception)
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])
    
    def test_list_command(self):
        """Test list command parsing."""
        parser = create_parser()
        
        # Basic list command
        args = parser.parse_args(['list'])
        assert args.command == 'list'
        assert not hasattr(args, 'detailed') or not args.detailed
        
        # List with detailed flag
        args = parser.parse_args(['list', '--detailed'])
        assert args.command == 'list'
        assert args.detailed
    
    def test_info_command(self):
        """Test info command parsing."""
        parser = create_parser()
        
        # Basic info command
        args = parser.parse_args(['info', 'vocabulary'])
        assert args.command == 'info'
        assert args.pipeline == 'vocabulary'
        assert not hasattr(args, 'stages') or not args.stages
        
        # Info with stages flag
        args = parser.parse_args(['info', 'vocabulary', '--stages'])
        assert args.command == 'info'
        assert args.pipeline == 'vocabulary'
        assert args.stages
    
    def test_run_command(self):
        """Test run command parsing."""
        parser = create_parser()
        
        # Basic run command
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare'])
        assert args.command == 'run'
        assert args.pipeline == 'vocabulary'
        assert args.stage == 'prepare'
        
        # Run with words
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare', '--words', 'test1,test2'])
        assert args.command == 'run'
        assert args.words == 'test1,test2'
        
        # Run with dry-run
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'prepare', '--dry-run'])
        assert args.command == 'run'
        assert args.dry_run
        
        # Run with execute flag
        args = parser.parse_args(['run', 'vocabulary', '--stage', 'media', '--cards', 'card1', '--execute'])
        assert args.command == 'run'
        assert args.cards == 'card1'
        assert args.execute
    
    def test_preview_command(self):
        """Test preview command parsing."""
        parser = create_parser()
        
        # Preview with card ID
        args = parser.parse_args(['preview', 'vocabulary', '--card-id', 'test_card'])
        assert args.command == 'preview'
        assert args.pipeline == 'vocabulary'
        assert args.card_id == 'test_card'
        
        # Preview with start server
        args = parser.parse_args(['preview', 'vocabulary', '--start-server', '--port', '8001'])
        assert args.command == 'preview'
        assert args.start_server
        assert args.port == 8001
    
    def test_global_flags(self):
        """Test global flags."""
        parser = create_parser()
        
        # Verbose flag
        args = parser.parse_args(['--verbose', 'list'])
        assert args.verbose
        assert args.command == 'list'
        
        # Config flag
        args = parser.parse_args(['--config', 'myconfig.json', 'info', 'vocabulary'])
        assert args.config == 'myconfig.json'
        assert args.command == 'info'
    
    def test_missing_required_args(self):
        """Test missing required arguments."""
        parser = create_parser()
        
        # Missing pipeline for info
        with pytest.raises(SystemExit):
            parser.parse_args(['info'])
        
        # Missing stage for run
        with pytest.raises(SystemExit):
            parser.parse_args(['run', 'vocabulary'])
        
        # Missing pipeline for run
        with pytest.raises(SystemExit):
            parser.parse_args(['run', '--stage', 'prepare'])