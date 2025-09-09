#!/usr/bin/env python3
"""
Unit tests for Sync Providers after migration from APIs

Tests sync provider functionality in the new provider structure.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from providers.sync.anki_provider import AnkiProvider
from providers.base.sync_provider import SyncRequest, SyncResult


class TestAnkiProvider:
    """Test Anki sync provider"""
    
    def setup_method(self):
        """Set up test provider"""
        self.provider = AnkiProvider()
    
    def test_supported_targets(self):
        """Test supported sync targets"""
        assert 'anki' in self.provider.supported_targets
    
    @patch('requests.post')
    def test_test_connection(self, mock_post):
        """Test Anki connection"""
        # Mock successful Anki Connect response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 6,  # Anki version
            'error': None
        }
        mock_post.return_value = mock_response
        
        result = self.provider.test_connection()
        
        assert result.success is True
        assert 'version' in result.data
    
    @patch('requests.post')
    def test_sync_cards(self, mock_post):
        """Test card synchronization"""
        # Mock successful note creation
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': [1001, 1002],  # Note IDs
            'error': None
        }
        mock_post.return_value = mock_response
        
        cards = [
            {
                'front': 'hola',
                'back': 'hello',
                'deck': 'Spanish'
            },
            {
                'front': 'gracias', 
                'back': 'thank you',
                'deck': 'Spanish'
            }
        ]
        
        request = SyncRequest(
            target='anki',
            data=cards,
            params={'deck': 'Spanish'}
        )
        
        result = self.provider.sync_data(request)
        
        assert isinstance(result, SyncResult)
        assert result.success is True
        assert result.processed_count == 2
    
    @patch('requests.post')
    def test_sync_templates(self, mock_post):
        """Test template synchronization"""
        # Mock successful model update
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': None,  # Void response for model update
            'error': None
        }
        mock_post.return_value = mock_response
        
        template_data = {
            'model_name': 'FluentForever',
            'fields': ['Front', 'Back', 'Audio', 'Image'],
            'templates': [
                {
                    'name': 'Card 1',
                    'front': '{{Front}}',
                    'back': '{{Back}}'
                }
            ]
        }
        
        request = SyncRequest(
            target='anki',
            data=template_data,
            params={'operation': 'update_templates'}
        )
        
        result = self.provider.sync_templates(request)
        
        assert isinstance(result, SyncResult)
    
    @patch('requests.post')  
    def test_sync_media(self, mock_post):
        """Test media synchronization"""
        # Mock successful media store
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': None,
            'error': None
        }
        mock_post.return_value = mock_response
        
        media_files = [
            {'filename': 'audio1.mp3', 'path': '/path/to/audio1.mp3'},
            {'filename': 'image1.jpg', 'path': '/path/to/image1.jpg'}
        ]
        
        request = SyncRequest(
            target='anki',
            data=media_files,
            params={'operation': 'store_media'}
        )
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b'fake_data'
            result = self.provider.sync_media(request)
            
            assert isinstance(result, SyncResult)
    
    @patch('requests.post')
    def test_list_existing_decks(self, mock_post):
        """Test listing existing decks"""
        # Mock deck names response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': ['Default', 'Spanish', 'French'],
            'error': None
        }
        mock_post.return_value = mock_response
        
        decks = self.provider.list_existing_decks()
        
        assert 'Spanish' in decks
        assert 'French' in decks
        assert len(decks) >= 2
    
    def test_connection_error_handling(self):
        """Test connection error handling"""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Connection failed")
            
            result = self.provider.test_connection()
            
            assert not result.success
            assert 'Connection failed' in result.error_message
    
    def test_anki_error_response(self):
        """Test Anki error response handling"""
        with patch('requests.post') as mock_post:
            # Mock Anki error response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'result': None,
                'error': 'deck was not found'
            }
            mock_post.return_value = mock_response
            
            request = SyncRequest(
                target='anki',
                data=[],
                params={'deck': 'NonexistentDeck'}
            )
            
            result = self.provider.sync_data(request)
            
            assert not result.success
            assert 'deck was not found' in result.error_message


class TestSyncRequest:
    """Test SyncRequest data structure"""
    
    def test_sync_request_creation(self):
        """Test SyncRequest object creation"""
        data = [{'front': 'test', 'back': 'test'}]
        request = SyncRequest(
            target='anki',
            data=data,
            params={'deck': 'TestDeck'}
        )
        
        assert request.target == 'anki'
        assert request.data == data
        assert request.params['deck'] == 'TestDeck'
    
    def test_sync_request_validation(self):
        """Test SyncRequest validation"""
        # Should raise ValueError for empty target
        with pytest.raises(ValueError, match="Sync target cannot be empty"):
            SyncRequest(target='', data=[], params={})
        
        # Should raise ValueError for None data
        with pytest.raises(ValueError, match="Sync data cannot be None"):
            SyncRequest(target='anki', data=None, params={})
    
    def test_sync_request_defaults(self):
        """Test SyncRequest default values"""
        request = SyncRequest(
            target='anki',
            data=[],
            params=None
        )
        
        assert request.params == {}


class TestSyncResult:
    """Test SyncResult data structure"""
    
    def test_sync_result_creation(self):
        """Test SyncResult object creation"""
        result = SyncResult(
            success=True,
            processed_count=5,
            metadata={'deck': 'Spanish'},
            created_ids=[1001, 1002, 1003, 1004, 1005]
        )
        
        assert result.success is True
        assert result.processed_count == 5
        assert len(result.created_ids) == 5
        assert result.metadata['deck'] == 'Spanish'
        assert result.error_message == ""
    
    def test_sync_result_failure(self):
        """Test SyncResult for failed operation"""
        result = SyncResult(
            success=False,
            processed_count=0,
            metadata={},
            error_message="Connection failed"
        )
        
        assert not result.success
        assert result.processed_count == 0
        assert result.error_message == "Connection failed"
        assert result.created_ids == []
    
    def test_sync_result_defaults(self):
        """Test SyncResult default values"""
        result = SyncResult(
            success=True,
            processed_count=3,
            metadata=None
        )
        
        assert result.metadata == {}
        assert result.created_ids == []
        assert result.error_message == ""


if __name__ == "__main__":
    pytest.main([__file__])