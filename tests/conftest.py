#!/usr/bin/env python3
"""
Shared test fixtures and mocks
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

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
def mock_anki_connection():
    """Mock AnkiConnection class"""
    mock = Mock()
    mock.ensure_connection.return_value = True
    mock.request.return_value = []
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