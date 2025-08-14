#!/usr/bin/env python3
"""
Tests for sync_validator.py - focused on specific failure cases
"""

import pytest
from unittest.mock import patch, Mock
from validation.anki.sync_validator import compare_card_fields

class TestSyncValidator:
    
    def test_field_value_mismatch(self):
        """FAILURE CASE: Field values don't match between vocabulary and Anki"""
        vocab_card = {
            "SpanishWord": "test",
            "IPA": "/test/",
            "ExampleSentence": "This is a test."
        }
        
        anki_card = {
            "SpanishWord": "test", 
            "IPA": "/test/",
            "ExampleSentence": "This is different."  # Mismatch here
        }
        
        differences = compare_card_fields(vocab_card, anki_card, "test", "meaning1")
        
        # Should detect the mismatch
        assert len(differences) > 0
        assert any("ExampleSentence" in str(diff) for diff in differences)
        
    def test_missing_field_in_anki(self):
        """FAILURE CASE: Field exists in vocabulary but missing from Anki card"""
        vocab_card = {
            "SpanishWord": "test",
            "IPA": "/test/",
            "ExampleSentence": "This is a test."
        }
        
        anki_card = {
            "SpanishWord": "test",
            "IPA": "/test/"
            # Missing ExampleSentence field
        }
        
        differences = compare_card_fields(vocab_card, anki_card, "test", "meaning1")
        
        # Should detect missing field
        assert len(differences) > 0
        assert any(diff.get('anki_value') == 'MISSING_IN_ANKI' and diff.get('field') == 'ExampleSentence' for diff in differences)
        
    def test_config_file_load_error(self):
        """FAILURE CASE: config.json cannot be loaded"""
        from validation.anki.sync_validator import load_config
        
        with patch('builtins.open', side_effect=FileNotFoundError("config.json not found")):
            with pytest.raises(FileNotFoundError):
                load_config()