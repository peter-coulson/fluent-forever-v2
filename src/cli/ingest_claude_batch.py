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
from utils.word_queue_manager import WordQueueManager
from apis.base_client import BaseAPIClient
from validation.internal.vocabulary_validator import VocabularyValidator
from validation.ipa_validator import validate_spanish_ipa


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
    parser.add_argument('--skip-ipa-validation', action='store_true', help='Skip IPA validation (override failures)')
    parser.add_argument('--update-word-queue', action='store_true', default=True, help='Update word_queue.json by removing processed/skipped words (default: True)')
    parser.add_argument('--no-update-word-queue', dest='update_word_queue', action='store_false', help='Do not update word_queue.json')
    args = parser.parse_args()

    logger = setup_logging()
    # Match prepare script: project root is current working directory
    project_root = Path.cwd()
    queue_manager = WordQueueManager(project_root)
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
    skipped_words = staging.get('skipped_words', [])
    
    if not isinstance(meanings, list) or (not meanings and not skipped_words):
        logger.error(f"{ICONS['cross']} Staging file has no meanings or skipped words to ingest")
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
    
    # IPA Validation (unless skipped)
    if not args.skip_ipa_validation:
        logger.info(f"{ICONS['search']} Validating IPA pronunciations against dictionary...")
        ipa_failures = []
        
        for word, meanings_list in derived.items():
            # Get IPA from first meaning (should be same for all meanings of same word)
            first_meaning = meanings_list[0]
            ipa_raw = first_meaning.get('IPA', '').strip('[]/')
            
            if ipa_raw:
                try:
                    is_valid = validate_spanish_ipa(word, ipa_raw)
                    if not is_valid:
                        ipa_failures.append({
                            'word': word,
                            'predicted_ipa': ipa_raw,
                            'meanings_count': len(meanings_list)
                        })
                except Exception as e:
                    logger.warning(f"{ICONS['warning']} IPA validation error for '{word}': {e}")
        
        if ipa_failures:
            logger.error(f"{ICONS['cross']} IPA validation failed for {len(ipa_failures)} words:")
            for failure in ipa_failures:
                logger.error(f"  - {failure['word']} → {failure['predicted_ipa']} ({failure['meanings_count']} meanings)")
            logger.error(f"\n{ICONS['info']} To override IPA validation failures, use --skip-ipa-validation")
            logger.error(f"Only use override if you're certain your IPA is correct and dictionary is wrong.")
            return 1
        
        logger.info(f"{ICONS['check']} All IPA pronunciations validated successfully")

    # Load existing vocabulary
    vocab_path = project_root / 'vocabulary.json'
    try:
        vocab = json.loads(vocab_path.read_text(encoding='utf-8'))
    except Exception:
        vocab = {"metadata": {"created": datetime.now().date().isoformat(), "last_updated": datetime.now().isoformat(), "total_words": 0, "total_cards": 0, "total_skipped": 0, "source": "claude-ingestion"}, "skipped_words": [], "words": {}}

    # Process skipped words
    if 'skipped_words' not in vocab:
        vocab['skipped_words'] = []
    
    existing_skipped = set(vocab['skipped_words'])
    new_skipped_count = 0
    for word in skipped_words:
        if isinstance(word, str) and word.strip() and word not in existing_skipped:
            vocab['skipped_words'].append(word.strip())
            new_skipped_count += 1

    # Merge meanings
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
    vocab['metadata']['total_skipped'] = len(vocab['skipped_words'])

    # Validate against full schema
    validator = VocabularyValidator(config)
    if not validator.validate(vocab):
        logger.error(validator.get_report())
        return 1

    if args.dry_run:
        logger.info(f"{ICONS['info']} DRY-RUN: would ingest {added_cards} meanings across {len(derived)} words, {new_skipped_count} new skipped words")
        if args.update_word_queue:
            processed_words = list(derived.keys())
            logger.info(f"{ICONS['info']} DRY-RUN: would remove from queue: {len(processed_words)} processed, {len(skipped_words)} skipped")
        return 0

    vocab_path.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding='utf-8')
    
    msg = f"{ICONS['check']} Ingested {added_cards} meanings across {len(derived)} words"
    if new_skipped_count > 0:
        msg += f", {new_skipped_count} new skipped words"
    msg += f" → updated {vocab_path}"
    logger.info(msg)

    # Update word queue by removing processed and skipped words
    if args.update_word_queue:
        processed_words = list(derived.keys())
        all_words_to_remove = processed_words + skipped_words
        
        if all_words_to_remove:
            logger.info(f"{ICONS['info']} Validating words exist in queue before removal...")
            
            # Validate all words exist in queue
            words_in_queue, words_not_in_queue = queue_manager.validate_words_in_queue(all_words_to_remove)
            
            if words_not_in_queue:
                logger.error(f"{ICONS['cross']} Words not found in queue: {', '.join(words_not_in_queue)}")
                logger.error(f"{ICONS['cross']} Cannot remove words that don't exist in queue")
                logger.error(f"{ICONS['info']} Words found in queue: {', '.join(words_in_queue) if words_in_queue else 'none'}")
                return 1
            
            logger.info(f"{ICONS['check']} All words validated in queue. Removing {len(processed_words)} processed and {len(skipped_words)} skipped words...")
            
            try:
                updated_queue = queue_manager.remove_words_from_queue(all_words_to_remove, "batch_processing", require_exists=True)
                queue_manager.save_word_queue(updated_queue)
                logger.info(f"{ICONS['check']} Word queue updated successfully")
            except ValueError as e:
                logger.error(f"{ICONS['cross']} Queue update failed: {e}")
                return 1
        else:
            logger.info(f"{ICONS['info']} No words to remove from queue")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())


