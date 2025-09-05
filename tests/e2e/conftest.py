#!/usr/bin/env python3
"""
E2E Test Configuration and Shared Fixtures

Provides mock infrastructure and shared fixtures for all E2E tests.
These mocks enable isolated testing of the pipeline system without
external dependencies.
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock, patch
import os


# Mock Data Fixtures
@pytest.fixture
def mock_vocabulary_data():
    """Mock vocabulary.json data for testing"""
    return {
        "metadata": {
            "created": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T00:00:00",
            "total_words": 2,
            "total_cards": 3,
            "source": "test"
        },
        "words": {
            "haber": {
                "word": "haber",
                "processed_date": "2024-01-01T00:00:00",
                "cards_created": 2,
                "meanings": [
                    {
                        "CardID": "haber_auxiliary",
                        "SpanishWord": "haber",
                        "IPA": "[a.βeɾ]",
                        "MeaningContext": "auxiliary_verb",
                        "MonolingualDef": "Verbo auxiliar para formar tiempos compuestos",
                        "ExampleSentence": "He comido tacos",
                        "GappedSentence": "____ comido tacos",
                        "ImageFile": "haber_auxiliary.png",
                        "WordAudio": "[sound:haber.mp3]",
                        "WordAudioAlt": "",
                        "UsageNote": "Used with past participle",
                        "MeaningID": "auxiliary_verb",
                        "prompt": "Boy eating tacos at table"
                    },
                    {
                        "CardID": "haber_exist",
                        "SpanishWord": "haber",
                        "IPA": "[a.βeɾ]",
                        "MeaningContext": "existence",
                        "MonolingualDef": "Expresar la existencia de algo",
                        "ExampleSentence": "Hay tacos en la mesa",
                        "GappedSentence": "____ tacos en la mesa",
                        "ImageFile": "haber_exist.png",
                        "WordAudio": "[sound:haber.mp3]",
                        "WordAudioAlt": "",
                        "UsageNote": "Impersonal use",
                        "MeaningID": "existence",
                        "prompt": "Tacos on table"
                    }
                ]
            },
            "casa": {
                "word": "casa",
                "processed_date": "2024-01-01T00:00:00",
                "cards_created": 1,
                "meanings": [
                    {
                        "CardID": "casa_house",
                        "SpanishWord": "la casa",
                        "IPA": "[ˈka.sa]",
                        "MeaningContext": "dwelling",
                        "MonolingualDef": "Edificio para habitar",
                        "ExampleSentence": "La casa tiene tres habitaciones",
                        "GappedSentence": "La ____ tiene tres habitaciones",
                        "ImageFile": "casa_house.png",
                        "WordAudio": "[sound:casa.mp3]",
                        "WordAudioAlt": "",
                        "UsageNote": "Always feminine",
                        "MeaningID": "dwelling",
                        "prompt": "Cozy house with three rooms"
                    }
                ]
            }
        },
        "skipped_words": ["difficult_word"]
    }


@pytest.fixture
def mock_conjugation_data():
    """Mock conjugations.json data for testing"""
    return {
        "conjugations": {
            "hablar_present_yo": {
                "CardID": "hablar_present_yo",
                "Front": "hablo",
                "Back": "hablar",
                "Add Reverse": "1",
                "Sentence": "Yo _____ español todos los días.",
                "Extra": "Present tense, first person singular",
                "Picture": "speaking.jpg"
            },
            "comer_preterite_tu": {
                "CardID": "comer_preterite_tu",
                "Front": "comiste",
                "Back": "comer",
                "Add Reverse": "1",
                "Sentence": "Tú _____ tacos ayer.",
                "Extra": "Preterite tense, second person singular",
                "Picture": "eating.jpg"
            }
        }
    }


@pytest.fixture
def mock_config_data():
    """Mock config.json data for testing"""
    return {
        "apis": {
            "openai": {
                "api_key": "test-key",
                "enabled": True,
                "model": "dall-e-3"
            },
            "forvo": {
                "api_key": "test-key",
                "enabled": True,
                "country_priorities": ["MX", "CO", "ES"]
            },
            "anki": {
                "url": "http://localhost:8765",
                "deck_name": "Test Deck",
                "note_type": "Fluent Forever"
            }
        },
        "image_generation": {
            "primary_provider": "openai",
            "providers": {
                "openai": {
                    "model": "dall-e-3",
                    "style": "Studio Ghibli animation style"
                }
            }
        },
        "paths": {
            "media_folder": "media",
            "vocabulary_db": "vocabulary.json"
        },
        "validation": {
            "vocabulary_schema": {
                "meaning_entry": {
                    "required_fields": ["CardID", "SpanishWord", "IPA"]
                }
            }
        }
    }


# Mock Infrastructure Classes
class MockPipeline:
    """Mock pipeline for testing pipeline contracts"""
    
    def __init__(self, name: str = "test_pipeline", stages: Optional[List[str]] = None):
        self.name = name
        self.stages = stages or ["stage1", "stage2", "stage3"]
        self.executed_stages = []
    
    def get_available_stages(self) -> List[str]:
        return self.stages
    
    def execute_stage(self, stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}")
        self.executed_stages.append(stage_name)
        return {"status": "success", "stage": stage_name, "data": context.get("data", {})}
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": f"Test pipeline: {self.name}",
            "stages": self.stages
        }


class MockStage:
    """Mock stage for testing stage contracts"""
    
    def __init__(self, name: str = "test_stage", should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.executed = False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.executed = True
        if self.should_fail:
            raise RuntimeError(f"Stage {self.name} failed")
        return {"status": "success", "stage": self.name, "output": "test_output"}


class MockProvider:
    """Mock provider for testing provider contracts"""
    
    def __init__(self, name: str = "test_provider", should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.calls = []
    
    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        self.calls.append({"operation": operation, "kwargs": kwargs})
        if self.should_fail:
            raise RuntimeError(f"Provider {self.name} failed on {operation}")
        return {"status": "success", "operation": operation, "result": "mock_result"}


class MockAnkiConnect:
    """Mock AnkiConnect client for testing"""
    
    def __init__(self):
        self.connected = True
        self.decks = ["Test Deck", "Another Deck"]
        self.note_types = ["Fluent Forever", "Conjugation"]
        self.cards = {}
        self.requests = []
    
    def request(self, action: str, **params) -> Any:
        self.requests.append({"action": action, "params": params})
        
        if action == "deckNames":
            return self.decks
        elif action == "modelNames":
            return self.note_types
        elif action == "addNote":
            note_id = f"note_{len(self.cards)}"
            self.cards[note_id] = params["note"]
            return note_id
        elif action == "updateNoteFields":
            note_id = params["note"]["id"]
            if note_id in self.cards:
                self.cards[note_id]["fields"].update(params["note"]["fields"])
                return None
            return {"error": "Note not found"}
        elif action == "version":
            return 6
        else:
            return {"result": "success"}


class MockOpenAI:
    """Mock OpenAI client for testing"""
    
    def __init__(self):
        self.requests = []
    
    def images_generate(self, **kwargs) -> Mock:
        self.requests.append(kwargs)
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].url = "https://example.com/test-image.png"
        return mock_response


class MockForvo:
    """Mock Forvo client for testing"""
    
    def __init__(self):
        self.requests = []
        self.audio_data = b"mock_audio_data"
    
    def get_pronunciations(self, word: str, language: str = "es") -> List[Dict[str, Any]]:
        self.requests.append({"word": word, "language": language})
        return [
            {
                "id": "123456",
                "word": word,
                "original": word,
                "addtime": "2024-01-01 00:00:00",
                "hits": 100,
                "username": "test_user",
                "sex": "m",
                "country": "MX",
                "code": "mx",
                "langname": "Spanish",
                "pathmp3": f"https://example.com/pronunciations/{word}.mp3",
                "pathogg": f"https://example.com/pronunciations/{word}.ogg"
            }
        ]
    
    def download_audio(self, url: str) -> bytes:
        return self.audio_data


# Test Environment Fixtures
@pytest.fixture
def temp_project_dir(mock_vocabulary_data, mock_conjugation_data, mock_config_data):
    """Create a temporary project directory with mock data files"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    (temp_dir / "media" / "images").mkdir(parents=True)
    (temp_dir / "media" / "audio").mkdir(parents=True)
    (temp_dir / "staging").mkdir()
    (temp_dir / "templates" / "anki" / "Fluent_Forever" / "templates").mkdir(parents=True)
    (temp_dir / "templates" / "anki" / "Conjugation" / "templates").mkdir(parents=True)
    
    # Write mock data files
    (temp_dir / "vocabulary.json").write_text(
        json.dumps(mock_vocabulary_data, ensure_ascii=False, indent=2)
    )
    (temp_dir / "conjugations.json").write_text(
        json.dumps(mock_conjugation_data, ensure_ascii=False, indent=2)
    )
    (temp_dir / "config.json").write_text(
        json.dumps(mock_config_data, ensure_ascii=False, indent=2)
    )
    
    # Create mock template files
    ff_templates_dir = temp_dir / "templates" / "anki" / "Fluent_Forever" / "templates"
    (ff_templates_dir / "Front.html").write_text("{{SpanishWord}}")
    (ff_templates_dir / "Back.html").write_text("{{FrontSide}}<hr>{{MonolingualDef}}")
    
    conj_templates_dir = temp_dir / "templates" / "anki" / "Conjugation" / "templates"
    (conj_templates_dir / "Card1_Front.html").write_text("{{Front}}")
    (conj_templates_dir / "Card1_Back.html").write_text("{{FrontSide}}<hr>{{Back}}")
    (conj_templates_dir / "Card2_Front.html").write_text("{{Back}}")
    (conj_templates_dir / "Card2_Back.html").write_text("{{FrontSide}}<hr>{{Sentence}}")
    
    # Create mock manifest files
    ff_manifest = {
        "note_type": "Fluent Forever",
        "fields": ["SpanishWord", "MonolingualDef", "ExampleSentence"],
        "templates": [{"name": "Card", "front": "Front.html", "back": "Back.html"}]
    }
    (temp_dir / "templates" / "anki" / "Fluent_Forever" / "manifest.json").write_text(
        json.dumps(ff_manifest, indent=2)
    )
    
    conj_manifest = {
        "note_type": "Conjugation", 
        "fields": ["Front", "Back", "Sentence", "Extra"],
        "templates": [
            {"name": "Card1", "front": "Card1_Front.html", "back": "Card1_Back.html"},
            {"name": "Card2", "front": "Card2_Front.html", "back": "Card2_Back.html"}
        ]
    }
    (temp_dir / "templates" / "anki" / "Conjugation" / "manifest.json").write_text(
        json.dumps(conj_manifest, indent=2)
    )
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_external_apis():
    """Mock all external APIs for isolated testing"""
    mocks = {}
    
    # Create mocks without patching non-existent classes for now
    # These can be patched when the actual classes are needed
    mocks['anki'] = MockAnkiConnect()
    mocks['openai'] = MockOpenAI()
    mocks['forvo'] = MockForvo()
    
    yield mocks


@pytest.fixture(autouse=True)
def mock_file_system_operations():
    """Mock file system operations that could affect the host system"""
    with patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('pathlib.Path.write_text') as mock_write_text, \
         patch('pathlib.Path.write_bytes') as mock_write_bytes, \
         patch('shutil.copy2') as mock_copy, \
         patch('shutil.move') as mock_move:
        
        # Allow operations in temp directories and test fixtures - disable for now to avoid recursion
        def safe_mkdir(*args, **kwargs):
            # Allow all mkdir operations for tests
            return None
        
        def safe_write_text(*args, **kwargs):
            # Allow all write operations for tests
            return None
        
        def safe_write_bytes(*args, **kwargs):
            # Allow all write operations for tests
            return None
        
        mock_mkdir.side_effect = safe_mkdir
        mock_write_text.side_effect = safe_write_text
        mock_write_bytes.side_effect = safe_write_bytes
        
        yield {
            'mkdir': mock_mkdir,
            'write_text': mock_write_text,
            'write_bytes': mock_write_bytes,
            'copy': mock_copy,
            'move': mock_move
        }


# Test Utilities
def assert_mock_called_with_pattern(mock_obj, pattern: Dict[str, Any]):
    """Assert that a mock was called with arguments matching a pattern"""
    for call_args in mock_obj.call_args_list:
        args, kwargs = call_args
        matches = True
        for key, expected in pattern.items():
            if key not in kwargs or kwargs[key] != expected:
                matches = False
                break
        if matches:
            return True
    raise AssertionError(f"Mock was not called with pattern: {pattern}")


def get_project_root() -> Path:
    """Get the project root directory for tests"""
    return Path(__file__).parent.parent.parent