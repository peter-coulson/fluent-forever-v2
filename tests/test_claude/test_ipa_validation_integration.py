#!/usr/bin/env python3
"""
Tests for IPA validation integration in Claude batch ingestion pipeline
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cli.ingest_claude_batch import main as ingest_main


@pytest.fixture
def test_config():
    """Standard test config for batch ingestion"""
    return {
        "validation": {
            "vocabulary_schema": {
                "metadata": {"required_fields": ["created","last_updated","total_words","total_cards","source"], "optional_fields": []},
                "word_entry": {"required_fields": ["word","processed_date","meanings","cards_created"], "optional_fields": []},
                "meaning_entry": {"required_fields": [
                    "CardID","SpanishWord","IPA","MeaningContext","MonolingualDef","ExampleSentence","GappedSentence","ImageFile","WordAudio","WordAudioAlt","UsageNote","MeaningID","prompt"
                ], "optional_fields": []}
            },
            "field_patterns": {
                "CardID": "^[a-z_0-9 ]+$",  # Allow spaces for multi-word
                "SpanishWord": "^[a-záéíóúñü ]+$",  # Allow spaces for multi-word
                "IPA": "^\\[.*\\]$|^/.*/$",
                "ImageFile": "^[a-z_]+\\.png$|^.*\\.png$",
                "WordAudio": "^\\[sound:.*\\.mp3\\]$",
                "MeaningID": "^[a-z_]+$"
            },
            "constraints": {"max_cards_per_word": 10, "min_definition_length": 1, "min_example_length": 1}
        },
        "apis": {"base": {"user_agent": "test", "timeout": 5, "max_retries": 1}},
        "paths": {"media_folder": "media"}
    }


@pytest.fixture
def empty_vocabulary():
    """Empty vocabulary.json for testing"""
    return {
        "metadata": {
            "created": "2025-01-01",
            "last_updated": "2025-01-01",
            "total_words": 0,
            "total_cards": 0,
            "source": "test"
        },
        "words": {}
    }


@pytest.fixture
def valid_staging_data():
    """Valid staging data with correct IPA"""
    return {
        "metadata": {"created": "2025-01-01", "batch_id": "test_batch"},
        "meanings": [
            {
                'SpanishWord': 'con',
                'MeaningID': 'instrument', 
                'MeaningContext': 'using a tool',
                'MonolingualDef': 'usar herramienta', 
                'ExampleSentence': 'Trabaja con un martillo.',
                'GappedSentence': 'Trabaja _____ un martillo.', 
                'IPA': '[kon]',  # This should pass validation
                'prompt': 'boy with hammer'
            }
        ]
    }


@pytest.fixture
def invalid_ipa_staging_data():
    """Staging data with invalid IPA that should fail validation"""
    return {
        "metadata": {"created": "2025-01-01", "batch_id": "test_batch"},
        "meanings": [
            {
                'SpanishWord': 'trabajo',
                'MeaningID': 'work', 
                'MeaningContext': 'employment',
                'MonolingualDef': 'empleo o labor', 
                'ExampleSentence': 'Tengo trabajo.',
                'GappedSentence': '_____ trabajo.', 
                'IPA': '[traWRONGxo]',  # This should fail validation
                'prompt': 'person at work'
            }
        ]
    }


@pytest.fixture
def multi_word_staging_data():
    """Staging data with multi-word entries"""
    return {
        "metadata": {"created": "2025-01-01", "batch_id": "test_batch"},
        "meanings": [
            {
                'SpanishWord': 'tener que',  # Multi-word
                'MeaningID': 'obligation', 
                'MeaningContext': 'must do something',
                'MonolingualDef': 'estar obligado a hacer algo', 
                'ExampleSentence': 'Tener que trabajar.',
                'GappedSentence': '_____ _____ trabajar.', 
                'IPA': '[teˈneɾ ke]',  # Should validate only 'tener'
                'prompt': 'person working reluctantly'
            }
        ]
    }


class TestIPAValidationIntegration:
    """Test IPA validation integration in batch ingestion"""
    
    def test_valid_ipa_passes_ingestion(self, tmp_path, test_config, empty_vocabulary, valid_staging_data):
        """Test that valid IPA passes through ingestion successfully"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(valid_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return True (valid)
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=True) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should succeed
        assert result == 0
        
        # Verify IPA validation was called
        mock_validate.assert_called_once_with('con', 'kon')
        
        # Verify vocabulary was updated
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert 'con' in vocab['words']
        assert vocab['words']['con']['meanings'][0]['IPA'] == '[kon]'
    
    def test_invalid_ipa_fails_ingestion(self, tmp_path, test_config, empty_vocabulary, invalid_ipa_staging_data):
        """Test that invalid IPA fails ingestion with proper error message"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(invalid_ipa_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return False (invalid)
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=False) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should fail
        assert result == 1
        
        # Verify IPA validation was called
        mock_validate.assert_called_once_with('trabajo', 'traWRONGxo')
        
        # Verify vocabulary was NOT updated (ingestion failed)
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert 'trabajo' not in vocab['words']
    
    def test_skip_ipa_validation_override(self, tmp_path, test_config, empty_vocabulary, invalid_ipa_staging_data):
        """Test that --skip-ipa-validation overrides validation failures"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(invalid_ipa_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return False, but skip validation should bypass it
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=False) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--skip-ipa-validation', '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should succeed despite invalid IPA
        assert result == 0
        
        # Verify IPA validation was NOT called (skipped)
        mock_validate.assert_not_called()
        
        # Verify vocabulary WAS updated (override worked)
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert 'trabajo' in vocab['words']
    
    def test_multi_word_ipa_validation(self, tmp_path, test_config, empty_vocabulary, multi_word_staging_data):
        """Test that multi-word IPA validation works correctly"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(multi_word_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return True
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=True) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should succeed
        assert result == 0
        
        # Verify IPA validation was called with the multi-word input
        mock_validate.assert_called_once_with('tener que', 'teˈneɾ ke')
        
        # Verify vocabulary was updated with multi-word key
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert 'tener que' in vocab['words']
    
    def test_ipa_validation_exception_handling(self, tmp_path, test_config, empty_vocabulary, valid_staging_data):
        """Test that IPA validation exceptions are handled gracefully"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(valid_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to raise an exception
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', side_effect=Exception("Dictionary error")) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should still succeed (exceptions are logged as warnings)
        assert result == 0
        
        # Verify IPA validation was attempted
        mock_validate.assert_called_once()
        
        # Verify vocabulary was updated (exception didn't halt ingestion)
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert 'con' in vocab['words']
    
    def test_multiple_words_validation_failure_reporting(self, tmp_path, test_config, empty_vocabulary):
        """Test that multiple IPA validation failures are reported correctly"""
        # Create staging data with multiple invalid IPA entries
        staging_data = {
            "metadata": {"created": "2025-01-01", "batch_id": "test_batch"},
            "meanings": [
                {
                    'SpanishWord': 'palabra1',
                    'MeaningID': 'meaning1', 
                    'MeaningContext': 'context1',
                    'MonolingualDef': 'definition1', 
                    'ExampleSentence': 'Sentence1.',
                    'GappedSentence': '_____.', 
                    'IPA': '[WRONG1]',
                    'prompt': 'prompt1'
                },
                {
                    'SpanishWord': 'palabra2',
                    'MeaningID': 'meaning2', 
                    'MeaningContext': 'context2',
                    'MonolingualDef': 'definition2', 
                    'ExampleSentence': 'Sentence2.',
                    'GappedSentence': '_____.', 
                    'IPA': '[WRONG2]',
                    'prompt': 'prompt2'
                }
            ]
        }
        
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return False for both
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=False) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--no-update-word-queue']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should fail
        assert result == 1
        
        # Verify both words were validated
        assert mock_validate.call_count == 2
        mock_validate.assert_any_call('palabra1', 'WRONG1')
        mock_validate.assert_any_call('palabra2', 'WRONG2')
    
    def test_dry_run_with_ipa_validation(self, tmp_path, test_config, empty_vocabulary, invalid_ipa_staging_data):
        """Test that dry-run mode still performs IPA validation"""
        # Setup test environment
        (tmp_path / 'config.json').write_text(json.dumps(test_config, ensure_ascii=False, indent=2))
        (tmp_path / 'vocabulary.json').write_text(json.dumps(empty_vocabulary, ensure_ascii=False, indent=2))
        
        staging_file = tmp_path / 'test_staging.json'
        staging_file.write_text(json.dumps(invalid_ipa_staging_data, ensure_ascii=False, indent=2))
        
        # Mock the IPA validation to return False
        with patch('cli.ingest_claude_batch.validate_spanish_ipa', return_value=False) as mock_validate:
            with patch('sys.argv', ['ingest_claude_batch', '--input', str(staging_file), '--dry-run']):
                with patch('os.getcwd', return_value=str(tmp_path)):
                    result = ingest_main()
        
        # Should fail even in dry-run (validation happens before dry-run check)
        assert result == 1
        
        # Verify IPA validation was called
        mock_validate.assert_called_once()
        
        # Verify vocabulary was NOT modified (dry-run)
        orig_vocab = json.loads((tmp_path / 'vocabulary.json').read_text())
        assert orig_vocab == empty_vocabulary


if __name__ == '__main__':
    pytest.main([__file__])