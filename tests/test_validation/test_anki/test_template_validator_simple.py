#!/usr/bin/env python3
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from validation.anki.template_validator import validate_templates_and_fields


class MockAPIResponse(SimpleNamespace):
    def __init__(self, success=True, data=None, error_message=""):
        super().__init__(success=success, data=data, error_message=error_message)


class MockAnkiClient:
    def __init__(self):
        self.note_type = "Test Model"

    def test_connection(self):
        return True

    def get_model_templates(self):
        return MockAPIResponse(True, {
            "Template A": {"Front": "{{SpanishWord}}", "Back": "{{ExampleSentence}}"}
        })

    def get_model_styling(self):
        return MockAPIResponse(True, {"css": ".card { font-size: 20px; }"})

    def get_model_field_names(self):
        return MockAPIResponse(True, [
            "CardID", "SpanishWord", "IPA", "MeaningContext", "MonolingualDef",
            "ExampleSentence", "GappedSentence", "ImageFile", "WordAudio",
            "WordAudioAlt", "UsageNote", "MeaningID"
        ])


def write_minimal_templates(project_root: Path):
    base = project_root / 'templates' / 'anki' / 'Test_Model'
    (base / 'templates').mkdir(parents=True, exist_ok=True)
    (base / 'styling.css').write_text(".card { font-size: 20px; }", encoding='utf-8')
    (base / 'templates' / 'Template_A_Front.html').write_text("{{SpanishWord}}", encoding='utf-8')
    (base / 'templates' / 'Template_A_Back.html').write_text("{{ExampleSentence}}", encoding='utf-8')
    manifest = {
        "note_type": "Test Model",
        "css": "styling.css",
        "templates": [
            {"name": "Template A", "front": "templates/Template_A_Front.html", "back": "templates/Template_A_Back.html"}
        ]
    }
    (base / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')


def write_minimal_config(project_root: Path):
    cfg = {
        "validation": {
            "vocabulary_schema": {
                "meaning_entry": {
                    "required_fields": [
                        "CardID", "SpanishWord", "IPA", "MeaningContext", "MonolingualDef",
                        "ExampleSentence", "GappedSentence", "ImageFile", "WordAudio",
                        "WordAudioAlt", "UsageNote", "MeaningID", "prompt"
                    ],
                    "optional_fields": []
                }
            }
        },
        "paths": {"media_folder": "media"},
        "apis": {"base": {"user_agent": "x", "timeout": 30, "max_retries": 1}}
    }
    (project_root / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')


def test_template_validator_pass(tmp_path):
    write_minimal_templates(tmp_path)
    write_minimal_config(tmp_path)
    with patch('validation.anki.template_validator.AnkiClient', MockAnkiClient):
        assert validate_templates_and_fields(tmp_path) is True


def test_template_validator_extra_field_fails(tmp_path):
    write_minimal_templates(tmp_path)
    write_minimal_config(tmp_path)

    class MockAnkiClientExtra(MockAnkiClient):
        def get_model_field_names(self):
            # Add an extra field not present in config
            base = super().get_model_field_names().data
            return MockAPIResponse(True, base + ["ExtraField"])

    with patch('validation.anki.template_validator.AnkiClient', MockAnkiClientExtra):
        assert validate_templates_and_fields(tmp_path) is False


