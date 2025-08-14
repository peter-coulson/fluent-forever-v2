#!/usr/bin/env python3
"""
Tests for vocabulary_validator.py - focused on specific failure cases
"""

import pytest
from unittest.mock import patch
from validation.internal.vocabulary_validator import VocabularyValidator, ValidationError

class TestVocabularyValidator:
    
    def test_missing_required_metadata_field(self, mock_config):
        """FAILURE CASE: Required metadata field is missing"""
        # Mock vocabulary missing required field
        invalid_vocab = {
            "metadata": {
                "created": "2024-01-01",
                # Missing "last_updated" required field
                "total_words": 1,
                "total_cards": 1
            },
            "words": {}
        }
        
        validator = VocabularyValidator(mock_config)
        result = validator.validate(invalid_vocab)
        
        # Should fail validation
        assert not result
        # Should have validation errors
        assert len(validator.errors) > 0
        assert any("last_updated" in str(error) for error in validator.errors)
        
    def test_invalid_spanish_word_pattern(self, mock_config):
        """FAILURE CASE: Spanish word contains invalid characters"""
        # Mock vocabulary with invalid Spanish word
        invalid_vocab = {
            "metadata": {
                "created": "2024-01-01",
                "last_updated": "2024-01-02",
                "total_words": 1,
                "total_cards": 1
            },
            "words": {
                "test123": {  # Numbers not allowed in Spanish words
                    "meanings": [
                        {
                            "CardID": "test_meaning1",
                            "SpanishWord": "test123"  # Invalid pattern
                        }
                    ]
                }
            }
        }
        
        # Add pattern validation to config
        config_with_patterns = {
            **mock_config,
            "validation": {
                **mock_config["validation"],
                "field_patterns": {
                    "SpanishWord": "^[a-záéíóúñü]+$"  # Only Spanish letters allowed
                }
            }
        }
        
        validator = VocabularyValidator(config_with_patterns)
        result = validator.validate(invalid_vocab)
        
        # Should fail validation due to invalid pattern
        assert not result
        assert len(validator.errors) > 0
        
    def test_missing_words_section(self, mock_config):
        """FAILURE CASE: vocabulary.json missing 'words' section"""
        invalid_vocab = {
            "metadata": {
                "created": "2024-01-01", 
                "last_updated": "2024-01-02",
                "total_words": 0,
                "total_cards": 0
            }
            # Missing "words" section entirely
        }
        
        validator = VocabularyValidator(mock_config)
        result = validator.validate(invalid_vocab)
        
        # Should fail validation
        assert not result
        assert len(validator.errors) > 0