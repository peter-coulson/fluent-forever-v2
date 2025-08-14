#!/usr/bin/env python3
"""
Sync Validator
Compares vocabulary.json with Anki cards field-by-field to ensure perfect synchronization
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from apis.anki_client import AnkiClient
from utils.logging_config import get_logger, ICONS
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
    """Main sync validation function"""
    print("🔍 ANKI ↔ VOCABULARY.JSON SYNC VALIDATOR")
    print("=" * 50)
    
    # Initialize Anki client
    anki_client = AnkiClient()
    
    # Ensure Anki connection
    if not anki_client.test_connection():
        print("\n❌ VALIDATION FAILED")
        print("   Cannot connect to Anki")
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
    
    # Load data
    vocab_data = load_vocabulary()
    
    try:
        response = anki_client.get_deck_cards()
        if not response.success:
            print(f"❌ Failed to get Anki cards: {response.error_message}")
            return False
        anki_cards = response.data
    except Exception as e:
        print(f"❌ Failed to get Anki cards: {e}")
        return False
    
    # Print summary
    vocab_total_cards = sum(len(word_data['meanings']) for word_data in vocab_data['words'].values())
    anki_total_cards = sum(len(meanings) for meanings in anki_cards.values())
    
    print(f"📊 SUMMARY:")
    print(f"   vocabulary.json: {len(vocab_data['words'])} words, {vocab_total_cards} cards")
    print(f"   Anki:           {len(anki_cards)} words, {anki_total_cards} cards")
    print()
    
    print("🔍 Validating vocabulary.json vs Anki cards...\n")
    
    # Track validation results
    differences_found = False
    
    vocab_words = set(vocab_data['words'].keys())
    anki_words = set(anki_cards.keys())
    
    # Check for missing words
    missing_in_anki = vocab_words - anki_words
    missing_in_vocab = anki_words - vocab_words
    
    if missing_in_anki:
        differences_found = True
        print("❌ WORDS MISSING IN ANKI:")
        for word in sorted(missing_in_anki):
            print(f"   • {word}")
        print()
    
    if missing_in_vocab:
        differences_found = True
        print("❌ WORDS MISSING IN VOCABULARY.JSON:")
        for word in sorted(missing_in_vocab):
            print(f"   • {word}")
        print()
    
    # Check words that exist in both systems
    common_words = vocab_words & anki_words
    
    for word in sorted(common_words):
        vocab_meanings = {m['MeaningID']: m for m in vocab_data['words'][word]['meanings']}
        anki_meanings = anki_cards[word]
        
        vocab_meaning_ids = set(vocab_meanings.keys())
        anki_meaning_ids = set(anki_meanings.keys())
        
        # Check for missing meanings
        missing_meanings_in_anki = vocab_meaning_ids - anki_meaning_ids
        missing_meanings_in_vocab = anki_meaning_ids - vocab_meaning_ids
        
        if missing_meanings_in_anki:
            differences_found = True
            print(f"❌ MEANINGS MISSING IN ANKI for '{word}':")
            for meaning in sorted(missing_meanings_in_anki):
                print(f"   • {meaning}")
            print()
        
        if missing_meanings_in_vocab:
            differences_found = True
            print(f"❌ MEANINGS MISSING IN VOCABULARY.JSON for '{word}':")
            for meaning in sorted(missing_meanings_in_vocab):
                print(f"   • {meaning}")
            print()
        
        # Compare fields for common meanings
        common_meanings = vocab_meaning_ids & anki_meaning_ids
        
        for meaning_id in sorted(common_meanings):
            vocab_card = vocab_meanings[meaning_id]
            anki_card = anki_meanings[meaning_id]
            
            field_differences = compare_card_fields(vocab_card, anki_card, word, meaning_id)
            
            if field_differences:
                differences_found = True
                print(f"❌ FIELD DIFFERENCES for '{word}.{meaning_id}':")
                for diff in field_differences:
                    print(f"   📝 {diff['field']}:")
                    print(f"      vocabulary.json: \"{diff['vocab_value']}\"")
                    print(f"      Anki:           \"{diff['anki_value']}\"")
                print()
    
    # Final verdict
    if not differences_found:
        print("✅ VALIDATION PASSED")
        print("   vocabulary.json and Anki are perfectly synchronized!")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("   Differences found between vocabulary.json and Anki")
        print("   Run sync script to resolve discrepancies")
        return False