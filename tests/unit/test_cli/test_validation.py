"""Unit tests for CLI validation utilities."""

import pytest
from unittest.mock import Mock

from cli.utils.validation import (
    validate_arguments,
    validate_file_path,
    validate_word_list,
    validate_card_list,
    validate_port,
    parse_and_validate_config
)


class TestValidateArguments:
    """Test validate_arguments function."""
    
    def test_info_command_valid(self):
        """Test valid info command arguments."""
        args = Mock(pipeline='vocabulary')
        errors = validate_arguments('info', args)
        assert errors == []
    
    def test_info_command_missing_pipeline(self):
        """Test info command with missing pipeline."""
        args = Mock(pipeline='')
        errors = validate_arguments('info', args)
        assert len(errors) == 1
        assert 'Pipeline name is required' in errors[0]
    
    def test_run_command_valid(self):
        """Test valid run command arguments."""
        args = Mock(pipeline='vocabulary', stage='prepare', dry_run=False, words='test1,test2')
        errors = validate_arguments('run', args)
        assert errors == []
    
    def test_run_command_missing_pipeline(self):
        """Test run command with missing pipeline."""
        args = Mock(pipeline='', stage='prepare', dry_run=False)
        errors = validate_arguments('run', args)
        assert len(errors) == 1
        assert 'Pipeline name is required' in errors[0]
    
    def test_run_command_missing_stage(self):
        """Test run command with missing stage."""
        args = Mock(pipeline='vocabulary', stage='', dry_run=False)
        errors = validate_arguments('run', args)
        assert len(errors) == 1
        assert 'Stage name is required' in errors[0]
    
    def test_run_command_prepare_missing_words(self):
        """Test prepare stage with missing words."""
        args = Mock(pipeline='vocabulary', stage='prepare', dry_run=False, words='')
        errors = validate_arguments('run', args)
        assert len(errors) == 1
        assert '--words is required for prepare stage' in errors[0]
    
    def test_run_command_media_missing_cards(self):
        """Test media stage with missing cards."""
        args = Mock(pipeline='vocabulary', stage='media', dry_run=False, cards='')
        errors = validate_arguments('run', args)
        assert len(errors) == 1
        assert '--cards is required for media stage' in errors[0]
    
    def test_run_command_dry_run_skips_validation(self):
        """Test dry-run skips stage-specific validation."""
        args = Mock(pipeline='vocabulary', stage='prepare', dry_run=True, words='')
        errors = validate_arguments('run', args)
        assert errors == []
    
    def test_preview_command_valid(self):
        """Test valid preview command arguments."""
        args = Mock(pipeline='vocabulary', card_id='test_card', start_server=False)
        errors = validate_arguments('preview', args)
        assert errors == []
    
    def test_preview_command_missing_pipeline(self):
        """Test preview command with missing pipeline."""
        args = Mock(pipeline='', card_id='test_card', start_server=False)
        errors = validate_arguments('preview', args)
        assert len(errors) == 1
        assert 'Pipeline name is required' in errors[0]
    
    def test_preview_command_missing_card_and_server(self):
        """Test preview command with neither card-id nor start-server."""
        args = Mock(pipeline='vocabulary', card_id='', start_server=False)
        errors = validate_arguments('preview', args)
        assert len(errors) == 1
        assert 'Either --start-server or --card-id must be specified' in errors[0]


class TestValidateFilePath:
    """Test validate_file_path function."""
    
    def test_valid_file_path(self, tmp_path):
        """Test validation of valid file path."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"test": true}')
        
        error = validate_file_path(str(test_file))
        assert error is None
    
    def test_nonexistent_file_path(self):
        """Test validation of nonexistent file path."""
        error = validate_file_path('/nonexistent/file.json')
        assert error is not None
        assert 'File does not exist' in error
    
    def test_directory_path(self, tmp_path):
        """Test validation of directory path (should fail)."""
        error = validate_file_path(str(tmp_path))
        assert error is not None
        assert 'Path is not a file' in error


class TestValidateWordList:
    """Test validate_word_list function."""
    
    def test_valid_word_list(self):
        """Test validation of valid word list."""
        errors = validate_word_list('word1,word2,word3')
        assert errors == []
    
    def test_empty_word_list(self):
        """Test validation of empty word list."""
        errors = validate_word_list('')
        assert len(errors) == 1
        assert 'Word list cannot be empty' in errors[0]
    
    def test_whitespace_only_word_list(self):
        """Test validation of whitespace-only word list."""
        errors = validate_word_list(' , , ')
        assert len(errors) == 1
        assert 'No valid words found' in errors[0]
    
    def test_word_list_with_whitespace(self):
        """Test validation of word list with whitespace."""
        errors = validate_word_list(' word1 , word2 , word3 ')
        assert errors == []


class TestValidateCardList:
    """Test validate_card_list function."""
    
    def test_valid_card_list(self):
        """Test validation of valid card list."""
        errors = validate_card_list('card1,card2,card3')
        assert errors == []
    
    def test_empty_card_list(self):
        """Test validation of empty card list."""
        errors = validate_card_list('')
        assert len(errors) == 1
        assert 'Card list cannot be empty' in errors[0]
    
    def test_whitespace_only_card_list(self):
        """Test validation of whitespace-only card list."""
        errors = validate_card_list(' , , ')
        assert len(errors) == 1
        assert 'No valid card IDs found' in errors[0]


class TestValidatePort:
    """Test validate_port function."""
    
    def test_valid_port(self):
        """Test validation of valid port."""
        assert validate_port(8000) is None
        assert validate_port(1) is None
        assert validate_port(65535) is None
    
    def test_invalid_port_too_low(self):
        """Test validation of port too low."""
        error = validate_port(0)
        assert error is not None
        assert 'Port must be between 1 and 65535' in error
    
    def test_invalid_port_too_high(self):
        """Test validation of port too high."""
        error = validate_port(65536)
        assert error is not None
        assert 'Port must be between 1 and 65535' in error


class TestParseAndValidateConfig:
    """Test parse_and_validate_config function."""
    
    def test_valid_config(self):
        """Test validation of valid configuration."""
        config = {
            'providers': {
                'data': {'type': 'json'},
                'media': {'type': 'openai'}
            },
            'output': {
                'format': 'table',
                'verbose': False
            }
        }
        errors = parse_and_validate_config(config)
        assert errors == []
    
    def test_invalid_providers_type(self):
        """Test validation of invalid providers type."""
        config = {'providers': 'not a dict'}
        errors = parse_and_validate_config(config)
        assert len(errors) == 1
        assert "'providers' must be a dictionary" in errors[0]
    
    def test_invalid_output_type(self):
        """Test validation of invalid output type."""
        config = {'output': 'not a dict'}
        errors = parse_and_validate_config(config)
        assert len(errors) == 1
        assert "'output' must be a dictionary" in errors[0]
    
    def test_empty_config(self):
        """Test validation of empty configuration."""
        config = {}
        errors = parse_and_validate_config(config)
        assert errors == []