#!/usr/bin/env python3
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from sync.media_generation import run_media_generation


def write_minimal_project(tmp_path: Path):
    # Minimal config
    cfg = {
        "apis": {
            "base": {"user_agent": "x", "timeout": 5, "max_retries": 1},
            "openai": {"env_var": "OPENAI_API_KEY", "model": "dall-e-3", "base_url": "https://api.openai.com/v1", "cost_per_image": 0.04},
            "forvo": {"env_var": "FORVO_API_KEY", "base_url": "https://apifree.forvo.com", "country_priorities": ["MX", "CO", "ES"], "priority_groups": [["MX", "CO"], ["ES"], []]},
            "anki": {"url": "http://localhost:8765", "deck_name": "Test", "note_type": "Fluent Forever", "launch_wait_time": 1}
        },
        "image_generation": {"style": "test", "width": 1024, "height": 1024},
        "paths": {"media_folder": str(tmp_path / 'media'), "vocabulary_db": str(tmp_path / 'vocabulary.json'), "word_queue": str(tmp_path / 'word_queue.txt'), "downloads": str(tmp_path)},
        "validation": {"vocabulary_schema": {
            "metadata": {"required_fields": ["created","last_updated","total_words","total_cards","source"], "optional_fields": []},
            "word_entry": {"required_fields": ["word","processed_date","meanings","cards_created"], "optional_fields": []},
            "meaning_entry": {"required_fields": [
            "CardID","SpanishWord","IPA","MeaningContext","MonolingualDef","ExampleSentence","GappedSentence","ImageFile","WordAudio","WordAudioAlt","UsageNote","MeaningID","prompt"
        ], "optional_fields": []}}
        , "field_patterns": {"CardID": "^[a-z_0-9]+$", "SpanishWord": "^[a-záéíóúñü]+$", "ImageFile": "^.*\\.png$", "WordAudio":"^\\[sound:.*\\.mp3\\]$", "MeaningID": "^[a-z_]+$"}, "constraints": {"max_cards_per_word": 10, "min_definition_length": 1, "min_example_length": 1}}}
    (tmp_path / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    # Minimal vocabulary with one card
    vocab = {
        "metadata": {"created":"2025-01-01","last_updated":"2025-01-01","total_words":1,"total_cards":1,"source":"test"},
        "words": {
            "con": {
                "word":"con", "processed_date":"2025-01-01", "cards_created":1,
                "meanings": [{
                    "CardID":"con_instrument", "SpanishWord":"con", "IPA":"[kon]", "MeaningContext":"instr", "MonolingualDef":"d","ExampleSentence":"e","GappedSentence":"_____",
                    "ImageFile":"con_instrument.png", "WordAudio":"[sound:con.mp3]", "WordAudioAlt":"", "UsageNote":"", "MeaningID":"instrument", "prompt":"hammer"
                }]
            }
        }
    }
    (tmp_path / 'vocabulary.json').write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding='utf-8')
    # Media dirs
    (tmp_path / 'media' / 'images').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'media' / 'audio').mkdir(parents=True, exist_ok=True)


def test_media_generation_dry_run_no_missing(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    # Mock internal validator to report no missing
    class MockResult(SimpleNamespace):
        def __init__(self):
            super().__init__(missing_images=[], missing_audio=[])
    with patch('validation.internal.media_validator.validate_local_vs_vocabulary', return_value=MockResult()):
        ok = run_media_generation(project_root=tmp_path, card_ids=['con_instrument'], dry_run=True)
        assert ok is True


def test_media_generation_dry_run_missing_returns_false(tmp_path, monkeypatch):
    write_minimal_project(tmp_path)
    class MockResult(SimpleNamespace):
        def __init__(self):
            super().__init__(missing_images=['con_instrument.png'], missing_audio=['con.mp3'])
    with patch('validation.internal.media_validator.validate_local_vs_vocabulary', return_value=MockResult()):
        ok = run_media_generation(project_root=tmp_path, card_ids=['con_instrument'], dry_run=True)
        assert ok is False


