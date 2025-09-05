#!/usr/bin/env python3
"""
Tests for the multi-card type Anki sync system
"""

import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path
import argparse

from cli.sync_anki_multi import sync_card_type, main


@pytest.fixture
def mock_anki_client():
    """Mock AnkiClient for testing"""
    mock = Mock()
    mock.test_connection.return_value = True
    mock.note_type = 'Test Note Type'
    return mock


@pytest.fixture 
def mock_logger():
    """Mock logger for testing"""
    mock = Mock()
    mock.info = Mock()
    mock.error = Mock()
    mock.warning = Mock()
    mock.getChild.return_value = mock
    return mock


class TestSyncCardType:
    """Test the sync_card_type function"""
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.load_local_templates')
    @patch('cli.sync_anki_multi.fetch_anki_templates')
    @patch('cli.sync_anki_multi.has_template_diffs')
    @patch('cli.sync_anki_multi.push_templates')
    def test_sync_card_type_success(self, mock_push, mock_has_diffs, mock_fetch, 
                                   mock_load, mock_anki_class, mock_registry,
                                   mock_setup_logging, tmp_path, setup_test_templates):
        # Setup mocks
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        mock_card_type = Mock()
        mock_card_type.name = 'TestType'
        mock_card_type.note_type = 'Test Note Type'
        mock_card_type.load_data.return_value = {'test': 'data'}
        mock_card_type.list_cards.return_value = [{'CardID': 'test1'}, {'CardID': 'test2'}]
        
        mock_reg = Mock()
        mock_reg.get.return_value = mock_card_type
        mock_registry.return_value = mock_reg
        
        mock_anki = Mock()
        mock_anki.note_type = 'Original Type'
        mock_anki_class.return_value = mock_anki
        
        mock_load.return_value = ([], '')
        mock_fetch.return_value = ({}, '')
        mock_has_diffs.return_value = False
        
        # Setup template directory
        tmpl_dir = setup_test_templates / 'templates' / 'anki' / 'TestType'
        tmpl_dir.mkdir(parents=True, exist_ok=True)
        
        # Run test
        result = sync_card_type('TestType', mock_anki, setup_test_templates, Mock())
        
        # Assertions
        assert result is True
        mock_card_type.load_data.assert_called_once_with(setup_test_templates)
        mock_card_type.list_cards.assert_called_once()
        
        # Check AnkiClient note type was temporarily changed
        assert mock_anki.note_type == 'Original Type'  # Should be restored
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    def test_sync_card_type_unknown_card_type(self, mock_registry, mock_setup_logging, tmp_path):
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        mock_reg = Mock()
        mock_reg.get.return_value = None
        mock_registry.return_value = mock_reg
        
        result = sync_card_type('NonExistent', Mock(), tmp_path, Mock())
        
        assert result is False
        mock_reg.get.assert_called_once_with('NonExistent')
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    def test_sync_card_type_missing_template_directory(self, mock_registry, mock_setup_logging, tmp_path):
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        mock_card_type = Mock()
        mock_card_type.name = 'TestType'
        mock_card_type.note_type = 'Test Note Type'
        
        mock_reg = Mock()
        mock_reg.get.return_value = mock_card_type
        mock_registry.return_value = mock_reg
        
        # Don't create template directory
        result = sync_card_type('TestType', Mock(), tmp_path, Mock())
        
        assert result is False
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.load_local_templates')
    def test_sync_card_type_template_sync_failure(self, mock_load, mock_anki_class, 
                                                 mock_registry, mock_setup_logging, 
                                                 tmp_path, setup_test_templates):
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        mock_card_type = Mock()
        mock_card_type.name = 'TestType'
        mock_card_type.note_type = 'Test Note Type'
        
        mock_reg = Mock()
        mock_reg.get.return_value = mock_card_type
        mock_registry.return_value = mock_reg
        
        mock_anki = Mock()
        mock_anki_class.return_value = mock_anki
        
        # Make template loading fail
        mock_load.side_effect = Exception("Template loading failed")
        
        # Setup template directory
        tmpl_dir = setup_test_templates / 'templates' / 'anki' / 'TestType'
        tmpl_dir.mkdir(parents=True, exist_ok=True)
        
        result = sync_card_type('TestType', mock_anki, setup_test_templates, Mock())
        
        assert result is False
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.load_local_templates')
    @patch('cli.sync_anki_multi.fetch_anki_templates')
    @patch('cli.sync_anki_multi.has_template_diffs')
    def test_sync_card_type_not_implemented_error(self, mock_has_diffs, mock_fetch, 
                                                 mock_load, mock_anki_class, 
                                                 mock_registry, mock_setup_logging, 
                                                 tmp_path, setup_test_templates):
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        mock_card_type = Mock()
        mock_card_type.name = 'TestType'
        mock_card_type.note_type = 'Test Note Type'
        mock_card_type.load_data.side_effect = NotImplementedError("Not implemented")
        
        mock_reg = Mock()
        mock_reg.get.return_value = mock_card_type
        mock_registry.return_value = mock_reg
        
        mock_anki = Mock()
        mock_anki_class.return_value = mock_anki
        
        mock_load.return_value = ([], '')
        mock_fetch.return_value = ({}, '')
        mock_has_diffs.return_value = False
        
        # Setup template directory
        tmpl_dir = setup_test_templates / 'templates' / 'anki' / 'TestType'
        tmpl_dir.mkdir(parents=True, exist_ok=True)
        
        result = sync_card_type('TestType', mock_anki, setup_test_templates, Mock())
        
        # Should still return True as NotImplementedError is handled
        assert result is True


class TestMainFunction:
    """Test the main CLI function"""
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('sys.argv', ['sync_anki_multi', '--list-types'])
    def test_main_list_types(self, mock_anki_class, mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_card_type1 = Mock()
        mock_card_type1.note_type = 'Type 1'
        mock_card_type2 = Mock()
        mock_card_type2.note_type = 'Type 2'
        
        mock_reg = Mock()
        mock_reg.list_types.return_value = ['Type1', 'Type2']
        mock_reg.get.side_effect = lambda x: mock_card_type1 if x == 'Type1' else mock_card_type2
        mock_registry.return_value = mock_reg
        
        result = main()
        
        assert result == 0
        mock_reg.list_types.assert_called_once()
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('sys.argv', ['sync_anki_multi'])
    def test_main_anki_connection_failure(self, mock_anki_class, mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = False
        mock_anki_class.return_value = mock_anki
        
        result = main()
        
        assert result == 1
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.sync_card_type')
    @patch('sys.argv', ['sync_anki_multi', '--card-type', 'TestType'])
    def test_main_specific_card_type_success(self, mock_sync, mock_anki_class, 
                                           mock_registry, mock_setup_logging, tmp_path):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = True
        mock_anki_class.return_value = mock_anki
        
        mock_card_type = Mock()
        mock_reg = Mock()
        mock_reg.get.return_value = mock_card_type
        mock_registry.return_value = mock_reg
        
        mock_sync.return_value = True
        
        # Mock the project root calculation
        with patch('cli.sync_anki_multi.Path') as mock_path_class:
            mock_path_obj = Mock()
            mock_path_obj.parents = [tmp_path, tmp_path.parent]
            mock_path_class.return_value = mock_path_obj
            mock_path_class.__file__ = 'dummy'
            
            result = main()
            
            assert result == 0
            mock_sync.assert_called_once()
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('sys.argv', ['sync_anki_multi', '--card-type', 'NonExistent'])
    def test_main_unknown_card_type(self, mock_anki_class, mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = True
        mock_anki_class.return_value = mock_anki
        
        mock_reg = Mock()
        mock_reg.get.return_value = None
        mock_registry.return_value = mock_reg
        
        result = main()
        
        assert result == 1
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.sync_card_type')
    @patch('cli.sync_anki_multi.Path')
    @patch('sys.argv', ['sync_anki_multi'])
    def test_main_all_card_types_mixed_results(self, mock_path, mock_sync, mock_anki_class, 
                                              mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = True
        mock_anki_class.return_value = mock_anki
        
        mock_reg = Mock()
        mock_reg.list_types.return_value = ['Type1', 'Type2', 'Type3']
        mock_reg.get.return_value = Mock()  # All types exist
        mock_registry.return_value = mock_reg
        
        # Mock sync results: 2 success, 1 failure
        mock_sync.side_effect = [True, False, True]
        mock_path.return_value.parents = [Mock(), Mock()]
        
        result = main()
        
        assert result == 1  # Should return 1 because not all syncs succeeded
        assert mock_sync.call_count == 3
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.sync_card_type')
    @patch('cli.sync_anki_multi.Path')
    @patch('sys.argv', ['sync_anki_multi'])
    def test_main_all_card_types_success(self, mock_path, mock_sync, mock_anki_class, 
                                        mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = True
        mock_anki_class.return_value = mock_anki
        
        mock_reg = Mock()
        mock_reg.list_types.return_value = ['Type1', 'Type2']
        mock_reg.get.return_value = Mock()
        mock_registry.return_value = mock_reg
        
        mock_sync.return_value = True  # All syncs succeed
        mock_path.return_value.parents = [Mock(), Mock()]
        
        result = main()
        
        assert result == 0
        assert mock_sync.call_count == 2
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.get_card_type_registry')
    @patch('cli.sync_anki_multi.AnkiClient')
    @patch('cli.sync_anki_multi.sync_card_type')
    @patch('cli.sync_anki_multi.Path')
    @patch('sys.argv', ['sync_anki_multi'])
    def test_main_sync_exception(self, mock_path, mock_sync, mock_anki_class, 
                                mock_registry, mock_setup_logging):
        mock_setup_logging.return_value = Mock()
        
        mock_anki = Mock()
        mock_anki.test_connection.return_value = True
        mock_anki_class.return_value = mock_anki
        
        mock_reg = Mock()
        mock_reg.list_types.return_value = ['Type1']
        mock_reg.get.return_value = Mock()
        mock_registry.return_value = mock_reg
        
        # Mock sync to raise exception
        mock_sync.side_effect = Exception("Unexpected error")
        mock_path.return_value.parents = [Mock(), Mock()]
        
        result = main()
        
        assert result == 1  # Should handle exception and return error code


class TestArgumentParsing:
    """Test command line argument parsing"""
    
    def test_parse_list_types_argument(self):
        # This tests the argument parser configuration indirectly
        # by testing the main function's behavior with different arguments
        with patch('sys.argv', ['sync_anki_multi', '--list-types']):
            with patch('cli.sync_anki_multi.setup_logging'):
                with patch('cli.sync_anki_multi.get_card_type_registry') as mock_registry:
                    mock_reg = Mock()
                    mock_reg.list_types.return_value = []
                    mock_registry.return_value = mock_reg
                    
                    result = main()
                    assert result == 0
    
    def test_parse_card_type_argument(self):
        with patch('sys.argv', ['sync_anki_multi', '--card-type', 'TestType']):
            with patch('cli.sync_anki_multi.setup_logging'):
                with patch('cli.sync_anki_multi.get_card_type_registry') as mock_registry:
                    with patch('cli.sync_anki_multi.AnkiClient') as mock_anki_class:
                        mock_anki = Mock()
                        mock_anki.test_connection.return_value = False
                        mock_anki_class.return_value = mock_anki
                        
                        result = main()
                        # Should fail at connection, but argument parsing worked
                        assert result == 1


class TestIntegration:
    """Integration tests for the sync system"""
    
    @patch('cli.sync_anki_multi.setup_logging')
    @patch('cli.sync_anki_multi.AnkiClient')
    def test_integration_with_real_registry(self, mock_anki_class, mock_setup_logging, 
                                           tmp_path, setup_test_templates, 
                                           mock_vocabulary, mock_conjugations):
        mock_setup_logging.return_value.getChild.return_value = Mock()
        
        # Setup data files
        (tmp_path / 'vocabulary.json').write_text(json.dumps(mock_vocabulary))
        (tmp_path / 'conjugations.json').write_text(json.dumps(mock_conjugations))
        
        # Setup Anki client mock
        mock_anki = Mock()
        mock_anki.note_type = 'Test Type'
        mock_anki_class.return_value = mock_anki
        
        # Mock template sync functions
        with patch('cli.sync_anki_multi.load_local_templates') as mock_load:
            with patch('cli.sync_anki_multi.fetch_anki_templates') as mock_fetch:
                with patch('cli.sync_anki_multi.has_template_diffs') as mock_has_diffs:
                    mock_load.return_value = ([], '')
                    mock_fetch.return_value = ({}, '')
                    mock_has_diffs.return_value = False
                    
                    # Create template directories
                    ff_dir = setup_test_templates / 'templates' / 'anki' / 'Fluent_Forever'
                    conj_dir = setup_test_templates / 'templates' / 'anki' / 'Conjugation'
                    
                    # Test Fluent Forever sync
                    result = sync_card_type('Fluent_Forever', mock_anki, setup_test_templates, Mock())
                    assert result is True
                    
                    # Test Conjugation sync
                    result = sync_card_type('Conjugation', mock_anki, setup_test_templates, Mock())
                    assert result is True