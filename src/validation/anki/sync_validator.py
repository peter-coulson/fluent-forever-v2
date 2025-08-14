#!/usr/bin/env python3
"""
Sync Validator
Compares vocabulary.json with Anki cards field-by-field to ensure perfect synchronization
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from apis.anki_client import AnkiClient
from utils.logging_config import get_logger, setup_logging, ICONS
from .sync_result import SyncValidationResult, FieldDifference

logger = get_logger('validation.anki.sync')

def load_vocabulary() -> dict:
    """Load vocabulary.json"""
    vocab_path = Path(__file__).parent.parent.parent.parent / 'vocabulary.json'
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to load vocabulary.json: {e}")
        raise

def compare_card_fields(vocab_card: dict, anki_card: dict, word: str, meaning: str) -> list:
    """Compare all fields between vocabulary card and Anki card"""
    differences = []
    
    # Get all fields from both sources
    vocab_fields = set(vocab_card.keys())
    anki_fields = set(anki_card.keys())
    
    # Skip 'prompt' field as it's vocabulary-only
    vocab_comparable_fields = vocab_fields - {'prompt'}
    
    # Check for fields missing in Anki
    missing_in_anki = vocab_comparable_fields - anki_fields
    for field in missing_in_anki:
        differences.append({
            'field': field,
            'vocab_value': vocab_card.get(field, ''),
            'anki_value': 'MISSING_IN_ANKI'
        })
    
    # Check for fields missing in vocabulary
    missing_in_vocab = anki_fields - vocab_fields
    for field in missing_in_vocab:
        differences.append({
            'field': field,
            'vocab_value': 'MISSING_IN_VOCAB',
            'anki_value': anki_card.get(field, '')
        })
    
    # Compare values for common fields
    common_fields = vocab_comparable_fields & anki_fields
    for field in common_fields:
        vocab_value = str(vocab_card.get(field, '')).strip()
        anki_value = str(anki_card.get(field, '')).strip()
        
        if vocab_value != anki_value:
            differences.append({
                'field': field,
                'vocab_value': vocab_value,
                'anki_value': anki_value
            })
    
    return differences

def validate_sync() -> bool:
    """Main sync validation function (logs instead of prints)."""
    setup_logging()
    logger.info("🔍 ANKI ↔ VOCABULARY.JSON SYNC VALIDATOR")
    logger.info("=" * 50)
    
    # Initialize Anki client
    anki_client = AnkiClient()
    
    # Ensure Anki connection
    if not anki_client.test_connection():
        logger.error("❌ VALIDATION FAILED")
        logger.error("   Cannot connect to Anki")
        return False


def validate_sync_structured() -> SyncValidationResult:
    """Return a structured diff for consumption by sync scripts."""
    anki_client = AnkiClient()
    if not anki_client.test_connection():
        return SyncValidationResult([], [], {}, {}, [])

    vocab_data = load_vocabulary()
    response = anki_client.get_deck_cards()
    anki_cards = response.data if response.success else {}

    missing_words_in_anki = []
    missing_words_in_vocab = []
    missing_meanings_in_anki: dict[str, list[str]] = {}
    missing_meanings_in_vocab: dict[str, list[str]] = {}
    field_differences: list[FieldDifference] = []

    vocab_words = set(vocab_data['words'].keys())
    anki_words = set(anki_cards.keys())

    missing_words_in_anki = sorted(vocab_words - anki_words)
    missing_words_in_vocab = sorted(anki_words - vocab_words)

    for word in sorted(vocab_words & anki_words):
        vocab_meanings = {m['MeaningID']: m for m in vocab_data['words'][word]['meanings']}
        anki_meanings = anki_cards[word]

        vocab_meaning_ids = set(vocab_meanings.keys())
        anki_meaning_ids = set(anki_meanings.keys())

        mm_anki = sorted(vocab_meaning_ids - anki_meaning_ids)
        if mm_anki:
            missing_meanings_in_anki[word] = mm_anki

        mm_vocab = sorted(anki_meaning_ids - vocab_meaning_ids)
        if mm_vocab:
            missing_meanings_in_vocab[word] = mm_vocab

        for meaning_id in sorted(vocab_meaning_ids & anki_meaning_ids):
            vocab_card = vocab_meanings[meaning_id]
            anki_card = anki_meanings[meaning_id]
            diffs = compare_card_fields(vocab_card, anki_card, word, meaning_id)
            for d in diffs:
                field_differences.append(
                    FieldDifference(
                        word=word,
                        meaning_id=meaning_id,
                        field=d['field'],
                        vocab_value=d['vocab_value'],
                        anki_value=d['anki_value'],
                    )
                )

    return SyncValidationResult(
        missing_words_in_anki=missing_words_in_anki,
        missing_words_in_vocab=missing_words_in_vocab,
        missing_meanings_in_anki=missing_meanings_in_anki,
        missing_meanings_in_vocab=missing_meanings_in_vocab,
        field_differences=field_differences,
    )