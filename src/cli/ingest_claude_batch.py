#!/usr/bin/env python3
"""
Ingest a Claude staging file into vocabulary.json after validation and derivation.

Schema Claude must provide for each meaning:
  - SpanishWord, MeaningID, MeaningContext, MonolingualDef,
    ExampleSentence, GappedSentence (must contain "_____"), IPA, prompt

We derive:
  - CardID = f"{SpanishWord}_{MeaningID}"
  - ImageFile = f"{SpanishWord}_{MeaningID}.png"
  - WordAudio = f"[sound:{SpanishWord}.mp3]"
  - WordAudioAlt = ""

Merges into vocabulary.json per word, updating cards_created and metadata.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from utils.logging_config import setup_logging, ICONS
from apis.base_client import BaseAPIClient
from validation.internal.vocabulary_validator import VocabularyValidator


def derive_fields(m: Dict[str, Any]) -> Dict[str, Any]:
    spanish = str(m['SpanishWord']).strip()
    meaning_id = str(m['MeaningID']).strip()
    card_id = f"{spanish}_{meaning_id}"
    return {
        **m,
        'CardID': card_id,
        'ImageFile': f"{spanish}_{meaning_id}.png",
        'WordAudio': f"[sound:{spanish}.mp3]",
        'WordAudioAlt': "",
        'UsageNote': m.get('UsageNote', '')
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Path to Claude staging JSON')
    parser.add_argument('--dry-run', action='store_true', help='Validate and preview without writing')
    args = parser.parse_args()

    logger = setup_logging()
    # Match prepare script: project root is current working directory
    project_root = Path.cwd()
    config = BaseAPIClient.load_config(project_root / 'config.json')

    staging_path = Path(args.input)
    if not staging_path.exists():
        logger.error(f"{ICONS['cross']} Staging file not found: {staging_path}")
        return 1

    try:
        staging = json.loads(staging_path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to read staging: {e}")
        return 1

    meanings = staging.get('meanings', [])
    if not isinstance(meanings, list) or not meanings:
        logger.error(f"{ICONS['cross']} Staging file has no meanings to ingest")
        return 1

    # Derive and group by word
    derived: Dict[str, list[Dict[str, Any]]] = {}
    for m in meanings:
        required = ['SpanishWord','MeaningID','MeaningContext','MonolingualDef','ExampleSentence','GappedSentence','IPA','prompt']
        missing = [k for k in required if not m.get(k)]
        if missing:
            logger.error(f"{ICONS['cross']} Missing fields in meaning: {missing}")
            return 1
        if '_____' not in str(m['GappedSentence']):
            logger.error(f"{ICONS['cross']} GappedSentence must contain '_____': {m['GappedSentence']}")
            return 1
        d = derive_fields(m)
        derived.setdefault(d['SpanishWord'], []).append(d)

    # Load existing vocabulary
    vocab_path = project_root / 'vocabulary.json'
    try:
        vocab = json.loads(vocab_path.read_text(encoding='utf-8'))
    except Exception:
        vocab = {"metadata": {"created": datetime.now().date().isoformat(), "last_updated": datetime.now().isoformat(), "total_words": 0, "total_cards": 0, "source": "claude-ingestion"}, "words": {}}

    # Merge
    added_cards = 0
    for word, new_meanings in derived.items():
        entry = vocab['words'].get(word, {"word": word, "processed_date": datetime.now().isoformat(), "meanings": [], "cards_created": 0})
        # Merge by MeaningID
        existing_by_id = {m['MeaningID']: m for m in entry.get('meanings', [])}
        for nm in new_meanings:
            existing_by_id[nm['MeaningID']] = nm
        merged = list(existing_by_id.values())
        entry['meanings'] = merged
        entry['cards_created'] = len(merged)
        vocab['words'][word] = entry
        added_cards += len(new_meanings)

    # Update metadata
    vocab['metadata']['last_updated'] = datetime.now().isoformat()
    vocab['metadata']['total_words'] = len(vocab['words'])
    vocab['metadata']['total_cards'] = sum(len(e['meanings']) for e in vocab['words'].values())

    # Validate against full schema
    validator = VocabularyValidator(config)
    if not validator.validate(vocab):
        logger.error(validator.get_report())
        return 1

    if args.dry_run:
        logger.info(f"{ICONS['info']} DRY-RUN: would ingest {added_cards} meanings across {len(derived)} words")
        return 0

    vocab_path.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info(f"{ICONS['check']} Ingested {added_cards} meanings across {len(derived)} words → updated {vocab_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


