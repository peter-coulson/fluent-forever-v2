#!/usr/bin/env python3
"""
Simplified tests for the multi-card type preview server focusing on core functionality
"""

import pytest
import json
from unittest.mock import patch, Mock
from pathlib import Path

from cli.preview_server_multi import create_app


class TestMultiCardPreviewServer:
    """Test essential functionality of the multi-card preview server"""
    
    def test_card_types_api(self):
        """Test the card types API endpoint"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            # Mock registry
            mock_registry = Mock()
            mock_registry.list_types.return_value = ['Fluent_Forever', 'Conjugation']
            
            mock_ff_type = Mock()
            mock_ff_type.note_type = 'Fluent Forever'
            mock_ff_type.data_file = 'vocabulary.json'
            
            mock_conj_type = Mock()
            mock_conj_type.note_type = 'Conjugation'
            mock_conj_type.data_file = 'conjugations.json'
            
            mock_registry.get.side_effect = lambda name: mock_ff_type if name == 'Fluent_Forever' else mock_conj_type if name == 'Conjugation' else None
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/card_types')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert isinstance(data, list)
                assert len(data) == 2
                
                names = [ct['name'] for ct in data]
                assert 'Fluent_Forever' in names
                assert 'Conjugation' in names
    
    def test_cards_api_fluent_forever(self):
        """Test listing Fluent Forever cards"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_card_type = Mock()
            mock_card_type.load_data.return_value = {'test': 'data'}
            mock_card_type.list_cards.return_value = [{'CardID': 'test1', 'SpanishWord': 'hola'}]
            
            mock_registry = Mock()
            mock_registry.get.return_value = mock_card_type
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/cards?card_type=Fluent_Forever')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['card_type'] == 'Fluent_Forever'
                assert 'cards' in data
                assert len(data['cards']) == 1
                assert data['cards'][0]['CardID'] == 'test1'
    
    def test_cards_api_conjugation(self):
        """Test listing Conjugation cards"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_card_type = Mock()
            mock_card_type.load_data.return_value = {'conjugations': {}}
            mock_card_type.list_cards.return_value = [{'CardID': 'hablar_yo', 'Front': 'hablo'}]
            
            mock_registry = Mock()
            mock_registry.get.return_value = mock_card_type
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/cards?card_type=Conjugation')
                assert response.status_code == 200
                
                data = json.loads(response.data)
                assert data['card_type'] == 'Conjugation'
                assert 'cards' in data
                assert len(data['cards']) == 1
                assert data['cards'][0]['CardID'] == 'hablar_yo'
    
    def test_cards_api_unknown_type(self):
        """Test handling of unknown card type"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.get.return_value = None
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/cards?card_type=NonExistent')
                assert response.status_code == 400
                assert b'Unknown card type: NonExistent' in response.data
    
    def test_cards_api_not_implemented_error(self):
        """Test handling of NotImplementedError in data loading"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_card_type = Mock()
            mock_card_type.load_data.side_effect = NotImplementedError("Test error")
            
            mock_registry = Mock()
            mock_registry.get.return_value = mock_card_type
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/cards?card_type=TestType')
                assert response.status_code == 501
                assert b'not yet implemented' in response.data
    
    def test_preview_endpoint_basic(self, setup_test_templates):
        """Test basic preview functionality"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_card_type = Mock()
            mock_card_type.name = 'Fluent_Forever'
            mock_card_type.load_data.return_value = {'test': 'data'}
            mock_card_type.find_card_by_id.return_value = {'CardID': 'test1', 'SpanishWord': 'hola'}
            mock_card_type.build_fields.return_value = {'SpanishWord': 'hola', 'CardID': 'test1'}
            
            mock_registry = Mock()
            mock_registry.get.return_value = mock_card_type
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', setup_test_templates):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/preview?card_id=test1&card_type=Fluent_Forever&side=front')
                assert response.status_code == 200
                assert response.content_type.startswith('text/html')
                
                html = response.data.decode('utf-8')
                assert 'hola' in html
    
    def test_preview_endpoint_unknown_card_type(self):
        """Test preview with unknown card type"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.get.return_value = None
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/preview?card_id=test&card_type=NonExistent')
                assert response.status_code == 400
                assert b'Unknown card type: NonExistent' in response.data
    
    def test_preview_endpoint_nonexistent_card_id(self, setup_test_templates):
        """Test preview with nonexistent card ID"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_card_type = Mock()
            mock_card_type.name = 'Fluent_Forever'
            mock_card_type.load_data.return_value = {'test': 'data'}
            mock_card_type.find_card_by_id.return_value = None  # Card not found
            
            mock_registry = Mock()
            mock_registry.get.return_value = mock_card_type
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', setup_test_templates):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/preview?card_id=nonexistent&card_type=Fluent_Forever')
                assert response.status_code == 404
                assert b'CardID not found: nonexistent' in response.data
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            mock_registry = Mock()
            mock_registry.list_types.return_value = ['Fluent_Forever', 'Conjugation']
            mock_get_registry.return_value = mock_registry
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/')
                assert response.status_code == 200
                assert response.content_type.startswith('text/html')
                
                html = response.data.decode('utf-8')
                assert 'Multi-Card Type Preview Server' in html
                assert 'Fluent_Forever' in html
                assert 'Conjugation' in html
    
    def test_error_handling_template_loading(self, setup_test_templates):
        """Test error handling for template loading failures"""
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            with patch('cli.preview_server_multi.load_local_templates') as mock_load:
                mock_card_type = Mock()
                mock_card_type.name = 'Fluent_Forever'
                
                mock_registry = Mock()
                mock_registry.get.return_value = mock_card_type
                mock_get_registry.return_value = mock_registry
                
                mock_load.side_effect = Exception("Template loading failed")
                
                with patch('cli.preview_server_multi.PROJECT_ROOT', setup_test_templates):
                    app = create_app()
                    app.config['TESTING'] = True
                    client = app.test_client()
                    
                    response = client.get('/preview?card_id=test&card_type=Fluent_Forever')
                    assert response.status_code == 500
                    assert b'Error loading templates' in response.data


class TestIntegration:
    """Integration tests using the real registry"""
    
    def test_real_registry_integration(self):
        """Test with the real card type registry"""
        with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
            app = create_app()
            app.config['TESTING'] = True
            client = app.test_client()
            
            # Should work with real registry
            response = client.get('/api/card_types')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) >= 2  # At least Fluent_Forever and Conjugation
            
            names = [ct['name'] for ct in data]
            assert 'Fluent_Forever' in names
            assert 'Conjugation' in names