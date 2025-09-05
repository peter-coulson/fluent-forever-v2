#!/usr/bin/env python3
"""
Tests for the modular card type system
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, Mock

from utils.card_types import (
    CardType, FluentForeverCardType, ConjugationCardType, 
    CardTypeRegistry, get_card_type_registry
)


class TestFluentForeverCardType:
    """Test Fluent Forever card type implementation"""
    
    def test_properties(self):
        card_type = FluentForeverCardType()
        assert card_type.name == 'Fluent_Forever'
        assert card_type.note_type == 'Fluent Forever'
        assert card_type.data_file == 'vocabulary.json'
    
    def test_load_data_existing_file(self, tmp_path, mock_vocabulary):
        vocab_file = tmp_path / 'vocabulary.json'
        vocab_file.write_text(json.dumps(mock_vocabulary))
        
        card_type = FluentForeverCardType()
        data = card_type.load_data(tmp_path)
        
        assert data == mock_vocabulary
        assert 'words' in data
        assert 'metadata' in data
    
    def test_load_data_missing_file(self, tmp_path):
        card_type = FluentForeverCardType()
        data = card_type.load_data(tmp_path)
        
        assert data == {}
    
    def test_find_card_by_id(self, mock_vocabulary):
        card_type = FluentForeverCardType()
        
        # Find existing card
        card = card_type.find_card_by_id(mock_vocabulary, "test_meaning1")
        assert card is not None
        assert card['CardID'] == "test_meaning1"
        assert card['SpanishWord'] == "test"
        
        # Card not found
        card = card_type.find_card_by_id(mock_vocabulary, "nonexistent")
        assert card is None
    
    def test_list_cards(self, mock_vocabulary):
        card_type = FluentForeverCardType()
        cards = card_type.list_cards(mock_vocabulary)
        
        assert len(cards) == 1
        card = cards[0]
        assert card['CardID'] == "test_meaning1"
        assert card['SpanishWord'] == "test"
        assert 'MeaningID' in card
        assert 'MeaningContext' in card
    
    def test_build_fields(self):
        card_type = FluentForeverCardType()
        
        # Mock the build_fields_from_meaning function
        with patch('utils.template_render.build_fields_from_meaning') as mock_build:
            mock_build.return_value = {'SpanishWord': 'test', 'CardID': 'test_id'}
            
            card_data = {'SpanishWord': 'test', 'CardID': 'test_id'}
            result = card_type.build_fields(card_data)
            
            mock_build.assert_called_once_with(card_data)
            assert result == {'SpanishWord': 'test', 'CardID': 'test_id'}


class TestConjugationCardType:
    """Test Conjugation card type implementation"""
    
    def test_properties(self):
        card_type = ConjugationCardType()
        assert card_type.name == 'Conjugation'
        assert card_type.note_type == 'Conjugation'
        assert card_type.data_file == 'conjugations.json'
    
    def test_load_data_existing_file(self, tmp_path, mock_conjugations):
        conj_file = tmp_path / 'conjugations.json'
        conj_file.write_text(json.dumps(mock_conjugations))
        
        card_type = ConjugationCardType()
        data = card_type.load_data(tmp_path)
        
        assert data == mock_conjugations
        assert 'conjugations' in data
        assert 'metadata' in data
    
    def test_load_data_missing_file_returns_placeholder(self, tmp_path):
        card_type = ConjugationCardType()
        data = card_type.load_data(tmp_path)
        
        assert 'conjugations' in data
        assert 'hablar_present_yo' in data['conjugations']
        # Verify it's placeholder data
        assert data['conjugations']['hablar_present_yo']['Front'] == 'hablo'
    
    def test_find_card_by_id(self, mock_conjugations):
        card_type = ConjugationCardType()
        
        # Find existing card
        card = card_type.find_card_by_id(mock_conjugations, "hablar_present_yo")
        assert card is not None
        assert card['CardID'] == "hablar_present_yo"
        assert card['Front'] == "hablo"
        assert card['Back'] == "hablar"
        
        # Card not found
        card = card_type.find_card_by_id(mock_conjugations, "nonexistent")
        assert card is None
    
    def test_list_cards(self, mock_conjugations):
        card_type = ConjugationCardType()
        cards = card_type.list_cards(mock_conjugations)
        
        assert len(cards) == 2
        card_ids = [card['CardID'] for card in cards]
        assert "hablar_present_yo" in card_ids
        assert "comer_preterite_el" in card_ids
        
        # Check structure
        card = cards[0]
        assert 'Front' in card
        assert 'Back' in card
        assert 'Sentence' in card
    
    def test_build_fields(self):
        card_type = ConjugationCardType()
        
        card_data = {
            'CardID': 'test_id',
            'Front': 'hablo',
            'Back': 'hablar',
            'Picture': 'test.jpg',
            'Add Reverse': 1,
            'Extra': None
        }
        
        fields = card_type.build_fields(card_data)
        
        # Check all fields are converted to strings
        assert fields['CardID'] == 'test_id'
        assert fields['Front'] == 'hablo'
        assert fields['Back'] == 'hablar'
        assert fields['Add Reverse'] == '1'
        assert fields['Extra'] == ''  # None converted to empty string
        
        # Check image path handling
        assert fields['Picture'] == 'media/images/test.jpg'
    
    def test_build_fields_picture_path_handling(self):
        card_type = ConjugationCardType()
        
        # Test various picture path scenarios
        test_cases = [
            ('test.jpg', 'media/images/test.jpg'),
            ('media/images/test.jpg', 'media/images/test.jpg'),
            ('path/to/test.jpg', 'path/to/test.jpg'),
            ('', ''),
            (None, '')
        ]
        
        for input_pic, expected_pic in test_cases:
            card_data = {'Picture': input_pic}
            fields = card_type.build_fields(card_data)
            assert fields['Picture'] == expected_pic


class TestCardTypeRegistry:
    """Test the card type registry system"""
    
    def test_registry_initialization(self):
        registry = CardTypeRegistry()
        
        # Should have built-in types
        types = registry.list_types()
        assert 'Fluent_Forever' in types
        assert 'Conjugation' in types
        assert len(types) >= 2
    
    def test_get_existing_card_type(self):
        registry = CardTypeRegistry()
        
        ff_type = registry.get('Fluent_Forever')
        assert ff_type is not None
        assert isinstance(ff_type, FluentForeverCardType)
        
        conj_type = registry.get('Conjugation')
        assert conj_type is not None
        assert isinstance(conj_type, ConjugationCardType)
    
    def test_get_nonexistent_card_type(self):
        registry = CardTypeRegistry()
        
        result = registry.get('NonExistent')
        assert result is None
    
    def test_get_default(self):
        registry = CardTypeRegistry()
        
        default = registry.get_default()
        assert isinstance(default, FluentForeverCardType)
        assert default.name == 'Fluent_Forever'
    
    def test_register_new_card_type(self):
        registry = CardTypeRegistry()
        
        # Create mock card type
        mock_type = Mock(spec=CardType)
        mock_type.name = 'TestType'
        
        # Register it
        registry.register(mock_type)
        
        # Should be available
        assert 'TestType' in registry.list_types()
        assert registry.get('TestType') == mock_type


class TestGlobalRegistry:
    """Test the global registry function"""
    
    def test_get_card_type_registry_returns_same_instance(self):
        registry1 = get_card_type_registry()
        registry2 = get_card_type_registry()
        
        # Should be the same instance (singleton-like behavior)
        assert registry1 is registry2
    
    def test_global_registry_has_built_in_types(self):
        registry = get_card_type_registry()
        
        assert registry.get('Fluent_Forever') is not None
        assert registry.get('Conjugation') is not None


class TestCardTypeABC:
    """Test the abstract base class behavior"""
    
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            CardType()
    
    def test_concrete_class_must_implement_abstract_methods(self):
        # Try to create incomplete implementation
        class IncompleteCardType(CardType):
            @property
            def name(self):
                return "Incomplete"
        
        with pytest.raises(TypeError):
            IncompleteCardType()


class TestIntegration:
    """Integration tests for the card type system"""
    
    def test_end_to_end_fluent_forever_workflow(self, tmp_path, mock_vocabulary):
        # Setup data file
        vocab_file = tmp_path / 'vocabulary.json'
        vocab_file.write_text(json.dumps(mock_vocabulary))
        
        # Get card type from registry
        registry = get_card_type_registry()
        card_type = registry.get('Fluent_Forever')
        
        # Load data
        data = card_type.load_data(tmp_path)
        assert data == mock_vocabulary
        
        # List cards
        cards = card_type.list_cards(data)
        assert len(cards) == 1
        
        # Find specific card
        card = card_type.find_card_by_id(data, "test_meaning1")
        assert card is not None
        
        # Build fields
        with patch('utils.template_render.build_fields_from_meaning') as mock_build:
            mock_build.return_value = {'test': 'field'}
            fields = card_type.build_fields(card)
            assert fields == {'test': 'field'}
    
    def test_end_to_end_conjugation_workflow(self, tmp_path, mock_conjugations):
        # Setup data file
        conj_file = tmp_path / 'conjugations.json'
        conj_file.write_text(json.dumps(mock_conjugations))
        
        # Get card type from registry
        registry = get_card_type_registry()
        card_type = registry.get('Conjugation')
        
        # Load data
        data = card_type.load_data(tmp_path)
        assert data == mock_conjugations
        
        # List cards
        cards = card_type.list_cards(data)
        assert len(cards) == 2
        
        # Find specific card
        card = card_type.find_card_by_id(data, "hablar_present_yo")
        assert card is not None
        assert card['Front'] == 'hablo'
        
        # Build fields
        fields = card_type.build_fields(card)
        assert 'Front' in fields
        assert 'Back' in fields
        assert fields['Front'] == 'hablo'