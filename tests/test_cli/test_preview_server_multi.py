#!/usr/bin/env python3
"""
Tests for the multi-card type preview server
"""

import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from pathlib import Path

from cli.preview_server_multi import create_app


@pytest.fixture
def app(tmp_path, setup_test_templates, mock_vocabulary, mock_conjugations):
    """Create test Flask app with mocked data"""
    
    # Setup data files in the test template path
    (setup_test_templates / 'vocabulary.json').write_text(json.dumps(mock_vocabulary))
    (setup_test_templates / 'conjugations.json').write_text(json.dumps(mock_conjugations))
    
    # Mock the card type registry to use our test data
    with patch('cli.preview_server_multi.PROJECT_ROOT', setup_test_templates):
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_get_registry:
            # Create mock card types
            mock_ff_type = Mock()
            mock_ff_type.name = 'Fluent_Forever'
            mock_ff_type.note_type = 'Fluent Forever'
            mock_ff_type.data_file = 'vocabulary.json'
            mock_ff_type.load_data.return_value = mock_vocabulary
            mock_ff_type.list_cards.return_value = [{'CardID': 'test_meaning1', 'SpanishWord': 'test', 'MeaningID': '', 'MeaningContext': ''}]
            mock_ff_type.find_card_by_id.return_value = {'CardID': 'test_meaning1', 'SpanishWord': 'test', 'ImageFile': 'test_image.png'}
            mock_ff_type.build_fields.return_value = {'SpanishWord': 'test', 'CardID': 'test_meaning1', 'ImageFile': 'media/images/test_image.png'}
            
            mock_conj_type = Mock()
            mock_conj_type.name = 'Conjugation'
            mock_conj_type.note_type = 'Conjugation'
            mock_conj_type.data_file = 'conjugations.json'
            mock_conj_type.load_data.return_value = mock_conjugations
            mock_conj_type.list_cards.return_value = [
                {'CardID': 'hablar_present_yo', 'Front': 'hablo', 'Back': 'hablar', 'Sentence': 'Yo _____ español todos los días.'},
                {'CardID': 'comer_preterite_el', 'Front': 'comió', 'Back': 'comer', 'Sentence': 'Él _____ una manzana ayer.'}
            ]
            mock_conj_type.find_card_by_id.side_effect = lambda data, card_id: mock_conjugations['conjugations'].get(card_id)
            mock_conj_type.build_fields.side_effect = lambda card_data: {k: str(v) if v is not None else '' for k, v in card_data.items()}
            
            # Mock registry
            mock_registry = Mock()
            mock_registry.list_types.return_value = ['Fluent_Forever', 'Conjugation']
            mock_registry.get.side_effect = lambda name: mock_ff_type if name == 'Fluent_Forever' else mock_conj_type if name == 'Conjugation' else None
            mock_get_registry.return_value = mock_registry
            
            app = create_app()
            app.config['TESTING'] = True
            return app


@pytest.fixture
def client(app):
    """Test client for the Flask app"""
    return app.test_client()


class TestCardTypesAPI:
    """Test the card types API endpoint"""
    
    def test_list_card_types(self, client):
        response = client.get('/api/card_types')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check structure
        names = [ct['name'] for ct in data]
        assert 'Fluent_Forever' in names
        assert 'Conjugation' in names
        
        # Check each type has required fields
        for card_type in data:
            assert 'name' in card_type
            assert 'note_type' in card_type
            assert 'data_file' in card_type


class TestCardsAPI:
    """Test the cards listing API endpoint"""
    
    def test_list_fluent_forever_cards(self, client):
        response = client.get('/api/cards?card_type=Fluent_Forever')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['card_type'] == 'Fluent_Forever'
        assert 'cards' in data
        assert len(data['cards']) == 1
        
        card = data['cards'][0]
        assert card['CardID'] == 'test_meaning1'
        assert card['SpanishWord'] == 'test'
    
    def test_list_conjugation_cards(self, client):
        response = client.get('/api/cards?card_type=Conjugation')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['card_type'] == 'Conjugation'
        assert 'cards' in data
        assert len(data['cards']) == 2
        
        card_ids = [card['CardID'] for card in data['cards']]
        assert 'hablar_present_yo' in card_ids
        assert 'comer_preterite_el' in card_ids
    
    def test_list_cards_default_type(self, client):
        # Should default to Fluent_Forever
        response = client.get('/api/cards')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['card_type'] == 'Fluent_Forever'
    
    def test_list_cards_unknown_type(self, client):
        response = client.get('/api/cards?card_type=NonExistent')
        assert response.status_code == 400
        assert b'Unknown card type: NonExistent' in response.data
    
    def test_list_cards_not_implemented_error(self):
        # Test this behavior independently to avoid app fixture conflicts
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_registry:
            mock_card_type = Mock()
            mock_card_type.load_data.side_effect = NotImplementedError("Test error")
            
            mock_reg = Mock()
            mock_reg.get.return_value = mock_card_type
            mock_registry.return_value = mock_reg
            
            with patch('cli.preview_server_multi.PROJECT_ROOT', Path('/tmp')):
                app = create_app()
                app.config['TESTING'] = True
                client = app.test_client()
                
                response = client.get('/api/cards?card_type=TestType')
                assert response.status_code == 501
                assert b'not yet implemented' in response.data


class TestPreviewEndpoint:
    """Test the card preview endpoint"""
    
    def test_preview_fluent_forever_front(self, client):
        response = client.get('/preview?card_id=test_meaning1&card_type=Fluent_Forever&side=front')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        
        html = response.data.decode('utf-8')
        assert 'test' in html  # Should contain the Spanish word
        assert 'Test_Front.html' not in html  # Should be rendered, not raw template
    
    def test_preview_conjugation_front(self, client):
        response = client.get('/preview?card_id=hablar_present_yo&card_type=Conjugation&side=front')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        
        html = response.data.decode('utf-8')
        assert 'hablo' in html  # Should contain the conjugated form
    
    def test_preview_conjugation_back(self, client):
        response = client.get('/preview?card_id=hablar_present_yo&card_type=Conjugation&side=back')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        
        html = response.data.decode('utf-8')
        assert 'hablar' in html  # Should contain the infinitive
    
    def test_preview_default_card_type(self, client):
        # Should default to Fluent_Forever
        response = client.get('/preview?card_id=test_meaning1')
        assert response.status_code == 200
    
    def test_preview_unknown_card_type(self, client):
        response = client.get('/preview?card_id=test&card_type=NonExistent')
        assert response.status_code == 400
        assert b'Unknown card type: NonExistent' in response.data
    
    def test_preview_nonexistent_card_id(self, client):
        response = client.get('/preview?card_id=nonexistent&card_type=Fluent_Forever')
        assert response.status_code == 404
        assert b'CardID not found: nonexistent' in response.data
    
    def test_preview_missing_template_directory(self, client, tmp_path):
        # Remove template directory
        template_dir = tmp_path / 'templates' / 'anki' / 'Fluent_Forever'
        if template_dir.exists():
            import shutil
            shutil.rmtree(template_dir)
        
        response = client.get('/preview?card_id=test_meaning1&card_type=Fluent_Forever')
        assert response.status_code == 404
        assert b'Template directory not found' in response.data
    
    def test_preview_with_theme_dark(self, client):
        response = client.get('/preview?card_id=test_meaning1&card_type=Fluent_Forever&theme=dark')
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'rgb(37, 150, 190)' in html  # Should contain dark theme CSS
    
    def test_preview_with_custom_bg(self, client):
        response = client.get('/preview?card_id=test_meaning1&card_type=Fluent_Forever&bg=rgb(255,0,0)')
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'rgb(255,0,0)' in html  # Should contain custom background
    
    def test_preview_not_implemented_error(self, client):
        # Mock a card type that raises NotImplementedError for data loading
        mock_card_type = Mock()
        mock_card_type.load_data.side_effect = NotImplementedError("Test error")
        
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_registry:
            mock_reg = Mock()
            mock_reg.get.return_value = mock_card_type
            mock_registry.return_value = mock_reg
            
            response = client.get('/preview?card_id=test&card_type=TestType')
            assert response.status_code == 501
            assert b'not yet implemented' in response.data
    
    def test_preview_field_building_not_implemented(self, client):
        # Mock a card type that raises NotImplementedError for field building
        mock_card_type = Mock()
        mock_card_type.load_data.return_value = {'test': 'data'}
        mock_card_type.find_card_by_id.return_value = {'CardID': 'test'}
        mock_card_type.build_fields.side_effect = NotImplementedError("Test error")
        
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_registry:
            mock_reg = Mock()
            mock_reg.get.return_value = mock_card_type
            mock_registry.return_value = mock_reg
            
            with patch('cli.preview_server_multi.load_local_templates') as mock_load:
                mock_load.return_value = ([], '')
                
                response = client.get('/preview?card_id=test&card_type=TestType')
                assert response.status_code == 501
                assert b'not yet implemented' in response.data


class TestMediaEndpoints:
    """Test media serving endpoints"""
    
    def test_media_images_endpoint(self, client, tmp_path):
        # Create test image
        media_dir = tmp_path / 'media' / 'images'
        media_dir.mkdir(parents=True)
        (media_dir / 'test.png').write_bytes(b'fake image data')
        
        response = client.get('/media/images/test.png')
        assert response.status_code == 200
        assert response.data == b'fake image data'
    
    def test_media_audio_endpoint(self, client, tmp_path):
        # Create test audio
        media_dir = tmp_path / 'media' / 'audio'
        media_dir.mkdir(parents=True)
        (media_dir / 'test.mp3').write_bytes(b'fake audio data')
        
        response = client.get('/media/audio/test.mp3')
        assert response.status_code == 200
        assert response.data == b'fake audio data'
    
    def test_media_not_found(self, client):
        response = client.get('/media/images/nonexistent.png')
        assert response.status_code == 404


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_endpoint(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
        
        html = response.data.decode('utf-8')
        assert 'Multi-Card Type Preview Server' in html
        assert 'Fluent_Forever' in html
        assert 'Conjugation' in html
        assert '/preview?' in html  # Should contain example links


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_template_loading_error(self, client):
        # Mock template loading to raise an exception
        with patch('cli.preview_server_multi.load_local_templates') as mock_load:
            mock_load.side_effect = Exception("Template loading failed")
            
            response = client.get('/preview?card_id=test_meaning1&card_type=Fluent_Forever')
            assert response.status_code == 500
            assert b'Error loading templates' in response.data
    
    def test_card_data_loading_error(self, client):
        # Mock card data loading to raise a general exception
        mock_card_type = Mock()
        mock_card_type.load_data.side_effect = Exception("Data loading failed")
        
        with patch('cli.preview_server_multi.get_card_type_registry') as mock_registry:
            mock_reg = Mock()
            mock_reg.get.return_value = mock_card_type
            mock_registry.return_value = mock_reg
            
            response = client.get('/preview?card_id=test&card_type=TestType')
            assert response.status_code == 500
            assert b'Error loading card data' in response.data


class TestIntegration:
    """Integration tests for the preview server"""
    
    def test_full_workflow_fluent_forever(self, client):
        # Test complete workflow: list types -> list cards -> preview card
        
        # 1. List card types
        response = client.get('/api/card_types')
        assert response.status_code == 200
        types = json.loads(response.data)
        ff_type = next(t for t in types if t['name'] == 'Fluent_Forever')
        assert ff_type['data_file'] == 'vocabulary.json'
        
        # 2. List cards
        response = client.get('/api/cards?card_type=Fluent_Forever')
        assert response.status_code == 200
        cards_data = json.loads(response.data)
        assert len(cards_data['cards']) > 0
        card_id = cards_data['cards'][0]['CardID']
        
        # 3. Preview front
        response = client.get(f'/preview?card_id={card_id}&card_type=Fluent_Forever&side=front')
        assert response.status_code == 200
        
        # 4. Preview back
        response = client.get(f'/preview?card_id={card_id}&card_type=Fluent_Forever&side=back')
        assert response.status_code == 200
    
    def test_full_workflow_conjugation(self, client):
        # Test complete workflow for conjugation cards
        
        # 1. List cards
        response = client.get('/api/cards?card_type=Conjugation')
        assert response.status_code == 200
        cards_data = json.loads(response.data)
        assert len(cards_data['cards']) > 0
        card_id = cards_data['cards'][0]['CardID']
        
        # 2. Preview front
        response = client.get(f'/preview?card_id={card_id}&card_type=Conjugation&side=front')
        assert response.status_code == 200
        
        # 3. Preview back
        response = client.get(f'/preview?card_id={card_id}&card_type=Conjugation&side=back')
        assert response.status_code == 200