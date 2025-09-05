#!/usr/bin/env python3
"""
Shared test fixtures and mocks
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

@pytest.fixture
def mock_config():
    """Mock config.json data"""
    return {
        "apis": {
            "anki": {
                "url": "http://localhost:8765"
            }
        },
        "validation": {
            "vocabulary_schema": {
                "metadata": {
                    "required_fields": ["created", "last_updated", "total_words", "total_cards"]
                },
                "word_entry": {
                    "required_fields": ["word", "meanings"]
                },
                "meaning_entry": {
                    "required_fields": ["CardID", "SpanishWord"]
                }
            },
            "field_patterns": {
                "SpanishWord": "^[a-záéíóúñü]+$"
            },
            "constraints": {
                "min_lengths": {
                    "SpanishWord": 1
                },
                "max_cards_per_word": 10
            }
        }
    }

@pytest.fixture
def mock_vocabulary():
    """Mock vocabulary.json data"""
    return {
        "metadata": {
            "created": "2024-01-01",
            "last_updated": "2024-01-02", 
            "total_words": 2,
            "total_cards": 3
        },
        "words": {
            "test": {
                "meanings": [
                    {
                        "CardID": "test_meaning1",
                        "SpanishWord": "test",
                        "ImageFile": "test_image.png",
                        "WordAudio": "[sound:test.mp3]"
                    }
                ]
            }
        }
    }

@pytest.fixture
def mock_anki_client():
    """Mock AnkiClient class"""
    mock = Mock()
    mock.test_connection.return_value = True
    mock.get_media_files.return_value = Mock(success=True, data=[])
    mock.get_deck_cards.return_value = Mock(success=True, data={})
    return mock

@pytest.fixture
def local_media_files():
    """Mock local media file sets"""
    return (
        {"test_image.png", "other_image.png"},  # images
        {"test.mp3", "other.mp3"}  # audio
    )

@pytest.fixture
def anki_media_files():
    """Mock Anki media file sets"""  
    return (
        {"test_image.png", "anki_only_image.png"},  # images
        {"test.mp3", "anki_only.mp3"}  # audio
    )

@pytest.fixture
def mock_conjugations():
    """Mock conjugations.json data"""
    return {
        "conjugations": {
            "hablar_present_yo": {
                "CardID": "hablar_present_yo",
                "Front": "hablo",
                "Back": "hablar",
                "Add Reverse": "1",
                "Sentence": "Yo _____ español todos los días.",
                "Extra": "Present tense, first person singular",
                "Picture": ""
            },
            "comer_preterite_el": {
                "CardID": "comer_preterite_el",
                "Front": "comió",
                "Back": "comer",
                "Add Reverse": "1",
                "Sentence": "Él _____ una manzana ayer.",
                "Extra": "Preterite tense, third person singular",
                "Picture": ""
            }
        },
        "metadata": {
            "created": "2024-01-01T00:00:00Z",
            "description": "Spanish verb conjugation practice cards",
            "total_cards": 2
        }
    }

@pytest.fixture
def setup_test_templates(tmp_path):
    """Setup test template directories for multiple card types"""
    # Fluent Forever templates
    ff_dir = tmp_path / 'templates' / 'anki' / 'Fluent_Forever'
    ff_templates_dir = ff_dir / 'templates'
    ff_templates_dir.mkdir(parents=True)
    
    # Create manifest
    ff_manifest = {
        "note_type": "Fluent Forever",
        "templates": [
            {
                "name": "Test Template",
                "front": "templates/Test_Front.html",
                "back": "templates/Test_Back.html"
            }
        ],
        "css": "styling.css",
        "fields": ["CardID", "SpanishWord", "ExampleSentence"]
    }
    (ff_dir / 'manifest.json').write_text(json.dumps(ff_manifest))
    (ff_dir / 'styling.css').write_text('.card { color: white; }')
    (ff_templates_dir / 'Test_Front.html').write_text('<div>{{SpanishWord}}</div>')
    (ff_templates_dir / 'Test_Back.html').write_text('<div>{{ExampleSentence}}</div>')
    
    # Conjugation templates
    conj_dir = tmp_path / 'templates' / 'anki' / 'Conjugation'
    conj_templates_dir = conj_dir / 'templates'
    conj_templates_dir.mkdir(parents=True)
    
    # Create manifest
    conj_manifest = {
        "note_type": "Conjugation",
        "templates": [
            {
                "name": "Card 1",
                "front": "templates/Card1_Front.html",
                "back": "templates/Card1_Back.html"
            }
        ],
        "css": "styling.css",
        "fields": ["Front", "Back", "Sentence"]
    }
    (conj_dir / 'manifest.json').write_text(json.dumps(conj_manifest))
    (conj_dir / 'styling.css').write_text('.card { color: white; }')
    (conj_templates_dir / 'Card1_Front.html').write_text('<div>{{Front}}</div>')
    (conj_templates_dir / 'Card1_Back.html').write_text('<div>{{Back}}</div>')
    
    return tmp_path