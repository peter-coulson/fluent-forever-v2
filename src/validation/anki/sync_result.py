#!/usr/bin/env python3
"""
SyncValidationResult - Structured result for Anki ↔ vocabulary.json sync validation
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class FieldDifference:
    word: str
    meaning_id: str
    field: str
    vocab_value: str
    anki_value: str


@dataclass
class SyncValidationResult:
    missing_words_in_anki: List[str]
    missing_words_in_vocab: List[str]
    missing_meanings_in_anki: Dict[str, List[str]]  # word -> [meaning_ids]
    missing_meanings_in_vocab: Dict[str, List[str]]  # word -> [meaning_ids]
    field_differences: List[FieldDifference]

    def is_synchronized(self) -> bool:
        return (
            not self.missing_words_in_anki
            and not self.missing_words_in_vocab
            and not any(self.missing_meanings_in_anki.values())
            and not any(self.missing_meanings_in_vocab.values())
            and not self.field_differences
        )


