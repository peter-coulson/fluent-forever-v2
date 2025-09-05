#!/usr/bin/env python3
import json
from pathlib import Path
from unittest.mock import patch

from cli.prepare_claude_batch import main as prepare_main
from cli.ingest_claude_batch import main as ingest_main


def test_prepare_and_ingest(tmp_path, monkeypatch):
    # Prepare staging
    staging_dir = tmp_path / 'staging'
    staging_dir.mkdir()
    # Create minimal config and vocab to satisfy validators
    cfg = {
        "validation": {
            "vocabulary_schema": {
                "metadata": {"required_fields": ["created","last_updated","total_words","total_cards","source"], "optional_fields": []},
                "word_entry": {"required_fields": ["word","processed_date","meanings","cards_created"], "optional_fields": []},
                "meaning_entry": {"required_fields": [
                    "CardID","SpanishWord","IPA","MeaningContext","MonolingualDef","ExampleSentence","GappedSentence","ImageFile","WordAudio","WordAudioAlt","UsageNote","MeaningID","prompt"
                ], "optional_fields": []}
            },
            "field_patterns": {
                "CardID": "^[a-z_0-9]+$",
                "SpanishWord": "^[a-záéíóúñü]+$",
                "IPA": "^\\[.*\\]$|^/.*/$",
                "ImageFile": "^[a-z_]+\\.png$|^.*\\.png$",
                "WordAudio": "^\\[sound:.*\\.mp3\\]$",
                "MeaningID": "^[a-z_]+$"
            },
            "constraints": {"max_cards_per_word": 10, "min_definition_length": 1, "min_example_length": 1}
        },
        "apis": {"base": {"user_agent": "x", "timeout": 5, "max_retries": 1}},
        "paths": {"media_folder": str(tmp_path / 'media')}
    }
    (tmp_path / 'config.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding='utf-8')
    (tmp_path / 'vocabulary.json').write_text(json.dumps({"metadata": {"created":"2025-01-01","last_updated":"2025-01-01","total_words":0,"total_cards":0,"source":"test"},"words":{}}, ensure_ascii=False, indent=2), encoding='utf-8')

    # Patch project_root resolution to tmp_path by adjusting __file__ access via changing cwd
    orig_cwd = Path.cwd()
    try:
        import os
        os.chdir(tmp_path)
        # Prepare
        with patch('sys.argv', ['prepare_claude_batch', '--words', 'con']):
            assert prepare_main() == 0
        # Fill staging with one meaning
        staging_files = list((tmp_path / 'staging').glob('claude_batch_*.json'))
        assert staging_files
        s_path = staging_files[0]
        s = json.loads(s_path.read_text(encoding='utf-8'))
        s['meanings'] = [{
            'SpanishWord': 'con', 'MeaningID': 'instrument', 'MeaningContext': 'using a tool',
            'MonolingualDef': 'usar herramienta', 'ExampleSentence': 'Trabaja con un martillo.',
            'GappedSentence': 'Trabaja _____ un martillo.', 'IPA': '[kon]', 'prompt': 'boy hammer'
        }]
        s_path.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')
        # Ingest
        with patch('sys.argv', ['ingest_claude_batch', '--input', str(s_path), '--no-update-word-queue']):
            assert ingest_main() == 0
        vocab = json.loads((tmp_path / 'vocabulary.json').read_text(encoding='utf-8'))
        assert 'con' in vocab['words']
        meanings = vocab['words']['con']['meanings']
        assert any(m.get('CardID') == 'con_instrument' for m in meanings)
    finally:
        import os
        os.chdir(orig_cwd)


