#!/usr/bin/env python3
"""
Baseline test for current vocabulary system.
This test must continue passing throughout the refactor to prevent regressions.
"""

import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


def test_current_vocabulary_workflow():
    """
    Baseline test - current system must continue working during refactor.
    Tests the core vocabulary workflow:
    1. prepare_claude_batch creates staging file
    2. ingest_claude_batch validates and processes staging
    3. media_generate can preview media generation
    4. sync_anki_all can do dry-run sync
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Set up minimal test environment
        setup_test_environment(temp_path)
        
        # Change to test directory (CLI scripts expect to be run from project root)
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_path)
            
            # Test 1: prepare_claude_batch creates staging file
            result = subprocess.run([
                "python", "-c", 
                """
import sys
sys.path.insert(0, 'src')
from cli.prepare_claude_batch import main
import sys
sys.argv = ['prepare_claude_batch', '--words', 'casa']
exit(main())
                """
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"prepare_claude_batch failed: {result.stderr}"
            
            # Verify staging file was created
            staging_files = list((temp_path / 'staging').glob('claude_batch_*.json'))
            assert len(staging_files) == 1, "Expected one staging file"
            
            # Add minimal test data to staging file
            staging_file = staging_files[0]
            with open(staging_file, 'r', encoding='utf-8') as f:
                staging_data = json.load(f)
            
            # Add minimal test meaning
            staging_data['meanings'] = [{
                "SpanishWord": "casa",
                "MeaningID": "casa_house",
                "MeaningContext": "dwelling/house",
                "MonolingualDef": "edificio donde vive una persona o familia",
                "ExampleSentence": "Mi familia vive en una casa grande",
                "GappedSentence": "Mi familia vive en una _____ grande",
                "IPA": "[ˈka.sa]",
                "prompt": "A cozy house with garden, family home style"
            }]
            
            with open(staging_file, 'w', encoding='utf-8') as f:
                json.dump(staging_data, f, ensure_ascii=False, indent=2)
            
            # Test 2: ingest_claude_batch validates and processes
            result = subprocess.run([
                "python", "-c", 
                f"""
import sys
sys.path.insert(0, 'src')
from cli.ingest_claude_batch import main
import sys
sys.argv = ['ingest_claude_batch', '--input', '{staging_file}', '--dry-run']
exit(main())
                """
            ], capture_output=True, text=True)
            
            assert result.returncode == 0, f"ingest_claude_batch dry-run failed: {result.stderr}"
            
            # Test 3: media_generate can preview (no execution)
            result = subprocess.run([
                "python", "-c", 
                """
import sys
sys.path.insert(0, 'src')
from cli.media_generate import main
import sys
sys.argv = ['media_generate', '--cards', 'casa_house']
exit(main())
                """
            ], capture_output=True, text=True)
            
            # Should succeed or fail gracefully (not crash)
            assert result.returncode in [0, 1], f"media_generate crashed: {result.stderr}"
            
            # Test 4: sync_anki_all dry-run (will fail but shouldn't crash)
            with patch('apis.anki_client.AnkiClient.test_connection', return_value=False):
                result = subprocess.run([
                    "python", "-c", 
                    """
import sys
sys.path.insert(0, 'src')
from cli.sync_anki_all import main
import sys
sys.argv = ['sync_anki_all']
exit(main())
                    """
                ], capture_output=True, text=True)
            
            # Should fail but not crash (return code 1 for connection failure)
            assert result.returncode in [0, 1], f"sync_anki_all crashed: {result.stderr}"
            
        finally:
            os.chdir(original_cwd)


def setup_test_environment(temp_path: Path):
    """Set up minimal test environment with required files and directories."""
    
    # Create required directories
    (temp_path / 'src').mkdir(exist_ok=True)
    (temp_path / 'staging').mkdir(exist_ok=True)
    (temp_path / 'media').mkdir(exist_ok=True)
    (temp_path / 'media' / 'images').mkdir(exist_ok=True)
    (temp_path / 'media' / 'audio').mkdir(exist_ok=True)
    
    # Copy source code to temp directory
    project_root = Path(__file__).parent.parent
    src_dir = project_root / 'src'
    if src_dir.exists():
        shutil.copytree(src_dir, temp_path / 'src', dirs_exist_ok=True)
    
    # Create minimal config.json
    config = {
        "apis": {
            "base": {
                "user_agent": "FluentForever-test/1.0",
                "timeout": 30,
                "max_retries": 3
            },
            "anki": {
                "url": "http://localhost:8765",
                "deck_name": "Test Deck",
                "note_type": "Fluent Forever"
            }
        },
        "validation": {
            "vocabulary_schema": {
                "metadata": {
                    "required_fields": ["created", "last_updated", "total_words", "total_cards", "source"],
                    "optional_fields": []
                },
                "word_entry": {
                    "required_fields": ["word", "processed_date", "meanings", "cards_created"],
                    "optional_fields": []
                },
                "meaning_entry": {
                    "required_fields": [
                        "CardID", "SpanishWord", "IPA", "MeaningContext", "MonolingualDef",
                        "ExampleSentence", "GappedSentence", "ImageFile", "WordAudio", "WordAudioAlt",
                        "UsageNote", "MeaningID", "prompt"
                    ],
                    "optional_fields": []
                }
            },
            "field_patterns": {
                "CardID": "^[a-záéíóúñü_0-9]+$",
                "SpanishWord": "^[a-záéíóúñü]+$",
                "IPA": "^\\[.*\\]$|^/.*/$",
                "ImageFile": "^[a-záéíóúñü_]+\\.png$",
                "WordAudio": "^\\[sound:[a-záéíóúñü_]+\\.mp3\\]$",
                "MeaningID": "^[a-záéíóúñü_]+$"
            },
            "constraints": {
                "max_cards_per_word": 10,
                "min_definition_length": 5,
                "min_example_length": 3
            }
        },
        "paths": {
            "media_folder": "media",
            "vocabulary_db": "vocabulary.json"
        },
        "media_generation": {
            "max_new_items": 5
        }
    }
    
    with open(temp_path / 'config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    # Create minimal vocabulary.json
    vocabulary = {
        "metadata": {
            "created": "2025-01-01",
            "last_updated": "2025-01-01T00:00:00.000000",
            "total_words": 0,
            "total_cards": 0,
            "source": "test"
        },
        "skipped_words": [],
        "words": {}
    }
    
    with open(temp_path / 'vocabulary.json', 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)


def test_key_cli_commands_exist():
    """Test that all key CLI commands can be imported."""
    project_root = Path(__file__).parent.parent
    
    # Key CLI commands that must exist
    commands = [
        'cli.prepare_claude_batch',
        'cli.ingest_claude_batch',
        'cli.media_generate',
        'cli.sync_anki_all',
        'cli.run_media_then_sync'
    ]
    
    import sys
    sys.path.insert(0, str(project_root / 'src'))
    
    for command in commands:
        try:
            __import__(command)
        except ImportError as e:
            pytest.fail(f"Could not import {command}: {e}")


def test_vocabulary_json_structure():
    """Test that vocabulary.json has expected structure."""
    project_root = Path(__file__).parent.parent
    vocab_file = project_root / 'vocabulary.json'
    
    if not vocab_file.exists():
        pytest.skip("vocabulary.json not found - this is acceptable for fresh installations")
        
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    
    # Check required top-level keys
    assert 'metadata' in vocab
    assert 'words' in vocab
    
    # Check metadata structure
    metadata = vocab['metadata']
    required_fields = ['created', 'last_updated', 'total_words', 'total_cards']
    for field in required_fields:
        assert field in metadata, f"Missing required metadata field: {field}"


def test_config_json_structure():
    """Test that config.json has expected structure."""
    project_root = Path(__file__).parent.parent
    config_file = project_root / 'config.json'
    
    assert config_file.exists(), "config.json must exist"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Check required top-level keys
    required_sections = ['apis', 'validation', 'paths']
    for section in required_sections:
        assert section in config, f"Missing required config section: {section}"
    
    # Check validation schema exists
    assert 'vocabulary_schema' in config['validation']
    assert 'field_patterns' in config['validation']


if __name__ == "__main__":
    test_current_vocabulary_workflow()
    test_key_cli_commands_exist()
    test_vocabulary_json_structure()
    test_config_json_structure()
    print("All baseline tests passed!")