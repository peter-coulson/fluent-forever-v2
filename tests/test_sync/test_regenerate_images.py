#!/usr/bin/env python3
import json
from pathlib import Path
from unittest.mock import patch

from sync.media_generation import build_meaning_index


def write_minimal_project(tmp_path: Path):
    cfg = {
        "apis": {"base": {"user_agent": "x", "timeout": 5, "max_retries": 1}},
        "paths": {"media_folder": str(tmp_path / 'media')},
        "validation": {"vocabulary_schema": {"meaning_entry": {"required_fields": [
            "CardID","SpanishWord","IPA","MeaningContext","MonolingualDef","ExampleSentence","GappedSentence","ImageFile","WordAudio","WordAudioAlt","UsageNote","MeaningID","prompt"
        ], "optional_fields": []}}}
    }
    (tmp_path / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    vocab = {
        "metadata": {"created":"2025-01-01","last_updated":"2025-01-01","total_words":1,"total_cards":1,"source":"test"},
        "words": {"con": {"word":"con","processed_date":"2025-01-01","cards_created":1,
                   "meanings":[{"CardID":"con_instrument","SpanishWord":"con","IPA":"[kon]","MeaningContext":"i","MonolingualDef":"d","ExampleSentence":"e","GappedSentence":"g","ImageFile":"con_instrument.png","WordAudio":"[sound:con.mp3]","WordAudioAlt":"","UsageNote":"","MeaningID":"instrument","prompt":"hammer"}]}}}
    (tmp_path / 'vocabulary.json').write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding='utf-8')


def test_build_meaning_index(tmp_path):
    write_minimal_project(tmp_path)
    from sync import media_generation
    v = json.loads((tmp_path / 'vocabulary.json').read_text(encoding='utf-8'))
    idx = build_meaning_index(v)
    assert 'con_instrument' in idx


