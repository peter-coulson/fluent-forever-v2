#!/usr/bin/env python3
"""
Generate word queue from spanish_dictionary.json based on frequency ranking.

Selects N words that are not already processed (in vocabulary.json words) 
or skipped (in vocabulary.json skipped_words) and creates a word_queue.json file.
"""

from __future__ import annotations

import argparse
import json
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from utils.logging_config import setup_logging, ICONS
from apis.base_client import BaseAPIClient


def normalize_for_comparison(word: str) -> str:
    """Normalize word by removing accents for comparison purposes."""
    # Remove accents but keep ñ
    normalized = unicodedata.normalize('NFD', word.lower())
    # Remove combining characters (accents) but keep ñ
    without_accents = ''.join(
        c for c in normalized 
        if not unicodedata.combining(c) or c in 'ñ'
    )
    return without_accents


def load_spanish_dictionary(dict_path: Path) -> List[Dict[str, Any]]:
    """Load and parse spanish_dictionary.json."""
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise ValueError(f"Failed to load dictionary: {e}")


def load_vocabulary(vocab_path: Path) -> Dict[str, Any]:
    """Load existing vocabulary.json."""
    if not vocab_path.exists():
        return {"words": {}, "skipped_words": []}
    
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load vocabulary: {e}")


def extract_clean_word(word_entry: Dict[str, Any]) -> str | None:
    """Extract clean Spanish word from dictionary entry."""
    word = word_entry.get("word", "").strip()
    definition = word_entry.get("definition", "").strip()
    
    # Skip if empty
    if not word:
        return None
    
    # Skip English words or corrupted entries
    english_indicators = [
        'directly', 'Radio', 'huevos', 'vecinos', 'exporting', 'minister', 
        'ceremony', 'was', 'charge', 'insignificant', 'mother', 'neighbors'
    ]
    if any(indicator in word or indicator in definition for indicator in english_indicators):
        return None
    
    # Skip if word looks like English (contains common English patterns)
    if any(pattern in word.lower() for pattern in ['ing', 'tion', 'ly', 'ed']):
        return None
    
    # Handle compound entries like "el/la" - take first part
    if '/' in word:
        word = word.split('/')[0]
    
    # Basic validation: should contain only Spanish letters/accents/ñ
    import re
    if not re.match(r'^[a-záéíóúüñ]+$', word.lower()):
        return None
        
    return word.lower()


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate word queue from spanish_dictionary.json')
    parser.add_argument('--count', '-n', type=int, default=50, 
                       help='Number of words to add to queue (default: 50)')
    parser.add_argument('--output', '-o', type=str, default='word_queue.json',
                       help='Output file name (default: word_queue.json)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be generated without creating file')
    args = parser.parse_args()

    logger = setup_logging()
    project_root = Path.cwd()
    
    # Load files
    dict_path = project_root / 'spanish_dictionary.json'
    vocab_path = project_root / 'vocabulary.json'
    output_path = project_root / args.output
    
    if not dict_path.exists():
        logger.error(f"{ICONS['cross']} Dictionary file not found: {dict_path}")
        return 1

    try:
        dictionary = load_spanish_dictionary(dict_path)
        vocabulary = load_vocabulary(vocab_path)
    except ValueError as e:
        logger.error(f"{ICONS['cross']} {e}")
        return 1

    # Get existing processed and skipped words (normalized for comparison)
    processed_words = set(vocabulary.get("words", {}).keys())
    skipped_words = set(vocabulary.get("skipped_words", []))
    excluded_words = processed_words | skipped_words
    excluded_normalized = {normalize_for_comparison(word) for word in excluded_words}
    
    logger.info(f"{ICONS['info']} Found {len(processed_words)} processed words, {len(skipped_words)} skipped words")

    # Extract clean words from dictionary, sorted by rank
    clean_entries = []
    seen_words_normalized = set()
    
    for entry in dictionary:
        clean_word = extract_clean_word(entry)
        if clean_word:
            clean_word_normalized = normalize_for_comparison(clean_word)
            if (clean_word_normalized not in excluded_normalized and 
                clean_word_normalized not in seen_words_normalized):
                clean_entries.append({
                    'word': clean_word,
                    'rank': entry.get('rank', 999999),
                    'partOfSpeech': entry.get('partOfSpeech', ''),
                    'definition': entry.get('definition', '')
                })
                seen_words_normalized.add(clean_word_normalized)
    
    # Sort by rank and take requested count
    clean_entries.sort(key=lambda x: x['rank'])
    selected_words = [entry['word'] for entry in clean_entries[:args.count]]
    
    if len(selected_words) < args.count:
        logger.warning(f"{ICONS['warning']} Only found {len(selected_words)} available words (requested {args.count})")
    
    # Create word queue structure
    word_queue = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "source": "spanish_dictionary.json",
            "total_words": len(selected_words),
            "excluded_processed": len(processed_words),
            "excluded_skipped": len(skipped_words)
        },
        "words": selected_words
    }

    if args.dry_run:
        logger.info(f"{ICONS['info']} DRY-RUN: Would generate queue with {len(selected_words)} words:")
        for i, word in enumerate(selected_words[:10], 1):
            logger.info(f"  {i}. {word}")
        if len(selected_words) > 10:
            logger.info(f"  ... and {len(selected_words) - 10} more words")
        return 0

    # Write word queue
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(word_queue, f, ensure_ascii=False, indent=2)
    
    logger.info(f"{ICONS['check']} Generated word queue with {len(selected_words)} words → {output_path}")
    logger.info(f"{ICONS['info']} First 10 words: {', '.join(selected_words[:10])}")
    
    return 0


if __name__ == '__main__':
    raise SystemExit(main())