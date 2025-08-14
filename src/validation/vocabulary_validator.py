#!/usr/bin/env python3
"""
Vocabulary Validator
Validates vocabulary.json structure, fields, and content against configuration schema
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from utils.logging_config import get_logger, ICONS

logger = get_logger('validation.vocabulary')

class ValidationError:
    """Represents a validation error"""
    
    def __init__(self, error_type: str, location: str, message: str, severity: str = "error"):
        self.error_type = error_type
        self.location = location
        self.message = message
        self.severity = severity
    
    def __str__(self):
        emoji = "❌" if self.severity == "error" else "⚠️"
        return f"{emoji} {self.error_type.upper()} in {self.location}: {self.message}"

class VocabularyValidator:
    """Validates vocabulary.json against schema and business rules"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.schema = config['validation']['vocabulary_schema']
        self.patterns = config['validation']['field_patterns']
        self.constraints = config['validation']['constraints']
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def add_error(self, error_type: str, location: str, message: str):
        """Add a validation error"""
        self.errors.append(ValidationError(error_type, location, message, "error"))
    
    def add_warning(self, error_type: str, location: str, message: str):
        """Add a validation warning"""
        self.warnings.append(ValidationError(error_type, location, message, "warning"))
    
    def validate_structure(self, vocab_data: Dict[str, Any]) -> bool:
        """Validate top-level structure"""
        if not isinstance(vocab_data, dict):
            self.add_error("structure", "root", "vocabulary.json must be a JSON object")
            return False
        
        # Check for required top-level keys
        if 'metadata' not in vocab_data:
            self.add_error("structure", "root", "Missing 'metadata' section")
        
        if 'words' not in vocab_data:
            self.add_error("structure", "root", "Missing 'words' section")
        
        return len(self.errors) == 0
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Validate metadata section"""
        if not isinstance(metadata, dict):
            self.add_error("structure", "metadata", "metadata must be an object")
            return False
        
        # Check required fields
        required_fields = self.schema['metadata']['required_fields']
        for field in required_fields:
            if field not in metadata:
                self.add_error("missing_field", f"metadata.{field}", f"Required field '{field}' is missing")
            elif not metadata[field]:
                self.add_error("empty_field", f"metadata.{field}", f"Required field '{field}' is empty")
        
        # Validate data types
        if 'total_words' in metadata and not isinstance(metadata['total_words'], int):
            self.add_error("type_error", "metadata.total_words", "total_words must be an integer")
        
        if 'total_cards' in metadata and not isinstance(metadata['total_cards'], int):
            self.add_error("type_error", "metadata.total_cards", "total_cards must be an integer")
        
        # Validate date format
        if 'last_updated' in metadata:
            try:
                datetime.fromisoformat(metadata['last_updated'].replace('Z', '+00:00'))
            except ValueError:
                self.add_error("format_error", "metadata.last_updated", "Invalid ISO date format")
        
        return True
    
    def validate_word_entry(self, word_key: str, word_data: Dict[str, Any]) -> bool:
        """Validate individual word entry"""
        location = f"words.{word_key}"
        
        if not isinstance(word_data, dict):
            self.add_error("structure", location, "Word entry must be an object")
            return False
        
        # Check required fields
        required_fields = self.schema['word_entry']['required_fields']
        for field in required_fields:
            if field not in word_data:
                self.add_error("missing_field", f"{location}.{field}", f"Required field '{field}' is missing")
        
        # Validate word matches key
        if 'word' in word_data and word_data['word'] != word_key:
            self.add_error("consistency", f"{location}.word", f"Word field '{word_data['word']}' doesn't match key '{word_key}'")
        
        # Validate meanings
        if 'meanings' in word_data:
            if not isinstance(word_data['meanings'], list):
                self.add_error("type_error", f"{location}.meanings", "meanings must be a list")
            else:
                if len(word_data['meanings']) == 0:
                    self.add_error("empty_field", f"{location}.meanings", "meanings list cannot be empty")
                elif len(word_data['meanings']) > self.constraints['max_cards_per_word']:
                    self.add_warning("constraint", f"{location}.meanings", 
                                   f"Word has {len(word_data['meanings'])} meanings, exceeds recommended maximum of {self.constraints['max_cards_per_word']}")
                
                # Validate each meaning
                for i, meaning in enumerate(word_data['meanings']):
                    self.validate_meaning_entry(f"{location}.meanings[{i}]", meaning, word_key)
        
        # Validate cards_created consistency
        if 'meanings' in word_data and 'cards_created' in word_data:
            expected_cards = len(word_data['meanings'])
            actual_cards = word_data['cards_created']
            if expected_cards != actual_cards:
                self.add_error("consistency", f"{location}.cards_created", 
                             f"cards_created ({actual_cards}) doesn't match meanings count ({expected_cards})")
        
        return True
    
    def validate_meaning_entry(self, location: str, meaning_data: Dict[str, Any], word: str) -> bool:
        """Validate individual meaning entry"""
        if not isinstance(meaning_data, dict):
            self.add_error("structure", location, "Meaning entry must be an object")
            return False
        
        # Check required fields
        required_fields = self.schema['meaning_entry']['required_fields']
        for field in required_fields:
            if field not in meaning_data:
                self.add_error("missing_field", f"{location}.{field}", f"Required field '{field}' is missing")
        
        # Validate field patterns
        for field, pattern in self.patterns.items():
            if field in meaning_data and meaning_data[field]:
                value = str(meaning_data[field])
                if not re.match(pattern, value):
                    self.add_error("format_error", f"{location}.{field}", 
                                 f"Field '{field}' value '{value}' doesn't match expected pattern")
        
        # Validate SpanishWord consistency
        if 'SpanishWord' in meaning_data and meaning_data['SpanishWord'] != word:
            self.add_error("consistency", f"{location}.SpanishWord", 
                         f"SpanishWord '{meaning_data['SpanishWord']}' doesn't match word '{word}'")
        
        # Validate CardID format
        if 'CardID' in meaning_data and 'MeaningID' in meaning_data:
            expected_card_id = f"{word}_{meaning_data['MeaningID']}"
            actual_card_id = meaning_data['CardID']
            if not actual_card_id.startswith(expected_card_id):
                self.add_warning("format", f"{location}.CardID", 
                               f"CardID '{actual_card_id}' doesn't follow expected pattern '{expected_card_id}'")
        
        # Validate content length constraints
        if 'MonolingualDef' in meaning_data:
            definition = meaning_data['MonolingualDef'].strip()
            if len(definition) < self.constraints['min_definition_length']:
                self.add_warning("content", f"{location}.MonolingualDef", 
                               f"Definition is very short ({len(definition)} chars)")
        
        if 'ExampleSentence' in meaning_data:
            example = meaning_data['ExampleSentence'].strip()
            if len(example) < self.constraints['min_example_length']:
                self.add_warning("content", f"{location}.ExampleSentence", 
                               f"Example sentence is very short ({len(example)} chars)")
        
        # Validate GappedSentence has blanks
        if 'GappedSentence' in meaning_data and 'ExampleSentence' in meaning_data:
            gapped = meaning_data['GappedSentence']
            if '_____' not in gapped:
                self.add_error("content", f"{location}.GappedSentence", 
                             "GappedSentence must contain '_____' placeholder")
        
        return True
    
    def validate_cross_references(self, vocab_data: Dict[str, Any]) -> bool:
        """Validate cross-references and uniqueness constraints"""
        card_ids = set()
        meaning_ids_per_word = {}
        
        for word_key, word_data in vocab_data.get('words', {}).items():
            meaning_ids_per_word[word_key] = set()
            
            for meaning in word_data.get('meanings', []):
                # Check CardID uniqueness
                card_id = meaning.get('CardID')
                if card_id:
                    if card_id in card_ids:
                        self.add_error("uniqueness", f"words.{word_key}", 
                                     f"Duplicate CardID '{card_id}' found")
                    else:
                        card_ids.add(card_id)
                
                # Check MeaningID uniqueness within word
                meaning_id = meaning.get('MeaningID')
                if meaning_id:
                    if meaning_id in meaning_ids_per_word[word_key]:
                        self.add_error("uniqueness", f"words.{word_key}", 
                                     f"Duplicate MeaningID '{meaning_id}' within word")
                    else:
                        meaning_ids_per_word[word_key].add(meaning_id)
        
        return True
    
    def validate(self, vocab_data: Dict[str, Any]) -> bool:
        """Run complete validation"""
        self.errors.clear()
        self.warnings.clear()
        
        # Validate structure
        if not self.validate_structure(vocab_data):
            return False
        
        # Validate metadata
        if 'metadata' in vocab_data:
            self.validate_metadata(vocab_data['metadata'])
        
        # Validate words
        if 'words' in vocab_data:
            for word_key, word_data in vocab_data['words'].items():
                self.validate_word_entry(word_key, word_data)
        
        # Validate cross-references
        self.validate_cross_references(vocab_data)
        
        return len(self.errors) == 0
    
    def get_report(self) -> str:
        """Generate validation report"""
        report = []
        
        if self.errors:
            report.append("❌ VALIDATION ERRORS:")
            for error in self.errors:
                report.append(f"   {error}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️  VALIDATION WARNINGS:")
            for warning in self.warnings:
                report.append(f"   {warning}")
            report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✅ VALIDATION PASSED")
            report.append("   vocabulary.json structure and content are valid!")
        elif not self.errors:
            report.append("✅ VALIDATION PASSED (with warnings)")
            report.append("   vocabulary.json is valid but has some warnings to address")
        else:
            report.append("❌ VALIDATION FAILED")
            report.append(f"   Found {len(self.errors)} errors and {len(self.warnings)} warnings")
        
        return "\n".join(report)