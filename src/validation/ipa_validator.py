#!/usr/bin/env python3
"""
Spanish IPA Validator

Validates predicted Spanish IPA against a reference dictionary.
Compares predicted IPA with dictionary entries, handling:
- Syllable markers (.) removal for comparison
- Stress marks only compared if present in dictionary
- Detailed logging of differences
"""

import logging
import os
import sys
from typing import Optional, Tuple, Dict
from pathlib import Path

from utils.logging_config import get_logger, setup_logging, ICONS


class SpanishIPAValidator:
    """Validates Spanish IPA pronunciation against reference dictionary"""
    
    def __init__(self, dictionary_path: Optional[str] = None):
        """
        Initialize the validator with dictionary data
        
        Args:
            dictionary_path: Path to Spanish IPA dictionary file
        """
        if dictionary_path is None:
            # Default to bundled dictionary
            current_dir = Path(__file__).parent
            dictionary_path = current_dir / "data" / "spanish_ipa_dictionary.txt"
        
        self.dictionary_path = Path(dictionary_path)
        
        # Setup logging using project pattern
        self.logger = get_logger('validation.ipa_validator')
        
        self.dictionary = self._load_dictionary()
    
    def _load_dictionary(self) -> Dict[str, str]:
        """Load dictionary from file into memory"""
        if not self.dictionary_path.exists():
            raise FileNotFoundError(f"Dictionary file not found: {self.dictionary_path}")
        
        dictionary = {}
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        word, ipa = line.split('\t', 1)
                        # Remove surrounding slashes if present
                        ipa = ipa.strip('/')
                        dictionary[word.lower()] = ipa
                    except ValueError:
                        self.logger.warning(f"Invalid line {line_num} in dictionary: {line}")
                        
        except Exception as e:
            raise RuntimeError(f"Failed to load dictionary: {e}")
        
        self.logger.info(f"{ICONS['file']} Loaded {len(dictionary)} entries from Spanish IPA dictionary")
        return dictionary
    
    def _normalize_ipa_for_comparison(self, ipa: str, remove_stress: bool = False) -> str:
        """
        Normalize IPA for comparison by removing syllable markers and optionally stress
        
        Args:
            ipa: IPA string to normalize
            remove_stress: Whether to remove stress marks
            
        Returns:
            Normalized IPA string
        """
        # Remove syllable markers (dots)
        normalized = ipa.replace('.', '')
        
        # Remove stress marks if requested
        if remove_stress:
            normalized = normalized.replace('ˈ', '').replace('ˌ', '')
        
        return normalized
    
    def _has_stress_marks(self, ipa: str) -> bool:
        """Check if IPA contains stress marks"""
        return 'ˈ' in ipa or 'ˌ' in ipa
    
    def validate_ipa(self, word: str, predicted_ipa: str) -> bool:
        """
        Validate predicted IPA against dictionary
        
        Args:
            word: Spanish word to validate (may be single word or phrase)
            predicted_ipa: Predicted IPA transcription (may be multi-word)
            
        Returns:
            True if IPA matches dictionary (within comparison rules), False otherwise
        """
        word_lower = word.strip().lower()
        predicted_ipa = predicted_ipa.strip()
        
        # Handle multi-word cases - extract first word for validation
        first_word = word_lower.split()[0] if word_lower else ''
        
        # For multi-word IPA, try to extract the first word's IPA
        if ' ' in word_lower and ' ' in predicted_ipa:
            # Multi-word case: validate only the first word
            predicted_parts = predicted_ipa.split()
            if predicted_parts:
                predicted_first = predicted_parts[0]
                self.logger.debug(f"{ICONS['info']} Multi-word input: using first word '{first_word}' with IPA '{predicted_first}'")
                return self._validate_single_word(first_word, predicted_first)
        elif ' ' in word_lower:
            # Word has spaces but IPA doesn't - use first word and full IPA
            self.logger.debug(f"{ICONS['info']} Multi-word input: using first word '{first_word}' with full IPA '{predicted_ipa}'")
            return self._validate_single_word(first_word, predicted_ipa)
        
        # Single word case
        return self._validate_single_word(word_lower, predicted_ipa)
    
    def _validate_single_word(self, word_lower: str, predicted_ipa: str) -> bool:
        """Validate a single word against dictionary"""
        
        # Check if word exists in dictionary
        if word_lower not in self.dictionary:
            self.logger.warning(f"{ICONS['warning']} Word '{word_lower}' not found in dictionary")
            return False
        
        dictionary_ipa = self.dictionary[word_lower]
        
        # Log the raw comparison
        self.logger.debug(f"{ICONS['search']} Validating '{word_lower}': predicted='{predicted_ipa}' vs dictionary='{dictionary_ipa}'")
        
        # Determine comparison strategy based on stress in dictionary
        dict_has_stress = self._has_stress_marks(dictionary_ipa)
        pred_has_stress = self._has_stress_marks(predicted_ipa)
        
        if dict_has_stress:
            # Dictionary has stress marks - compare including stress
            dict_normalized = self._normalize_ipa_for_comparison(dictionary_ipa, remove_stress=False)
            pred_normalized = self._normalize_ipa_for_comparison(predicted_ipa, remove_stress=False)
            comparison_type = "with stress"
        else:
            # Dictionary has no stress marks - ignore stress in comparison
            dict_normalized = self._normalize_ipa_for_comparison(dictionary_ipa, remove_stress=True)
            pred_normalized = self._normalize_ipa_for_comparison(predicted_ipa, remove_stress=True)
            comparison_type = "without stress"
        
        # Compare normalized versions
        matches = dict_normalized == pred_normalized
        
        # Log detailed comparison results
        if matches:
            self.logger.info(f"{ICONS['check']} MATCH: '{word_lower}' ({comparison_type})")
            if dict_has_stress != pred_has_stress:
                stress_info = f"(dict stress: {dict_has_stress}, pred stress: {pred_has_stress})"
                self.logger.debug(f"{ICONS['info']} Note: Stress presence differs {stress_info}")
        else:
            self.logger.error(f"{ICONS['cross']} MISMATCH: '{word_lower}' ({comparison_type})")
            self.logger.error(f"   Dictionary: '{dictionary_ipa}' → normalized: '{dict_normalized}'")
            self.logger.error(f"   Predicted:  '{predicted_ipa}' → normalized: '{pred_normalized}'")
            
            # Analyze specific differences
            self._log_differences(dict_normalized, pred_normalized)
        
        return matches
    
    def _log_differences(self, expected: str, actual: str):
        """Log character-by-character differences between IPA strings"""
        if len(expected) != len(actual):
            self.logger.error(f"   Length difference: expected {len(expected)} chars, got {len(actual)} chars")
        
        differences = []
        max_len = max(len(expected), len(actual))
        
        for i in range(max_len):
            exp_char = expected[i] if i < len(expected) else '∅'
            act_char = actual[i] if i < len(actual) else '∅'
            
            if exp_char != act_char:
                differences.append(f"pos {i}: '{exp_char}' vs '{act_char}'")
        
        if differences:
            self.logger.error(f"   Character differences: {', '.join(differences[:5])}")
            if len(differences) > 5:
                self.logger.error(f"   ... and {len(differences) - 5} more differences")


def validate_spanish_ipa(word: str, predicted_ipa: str, dictionary_path: Optional[str] = None) -> bool:
    """
    Convenience function to validate Spanish IPA
    
    Args:
        word: Spanish word to validate
        predicted_ipa: Predicted IPA transcription
        dictionary_path: Optional path to dictionary file
        
    Returns:
        True if IPA matches dictionary, False otherwise
    """
    validator = SpanishIPAValidator(dictionary_path)
    return validator.validate_ipa(word, predicted_ipa)


def main():
    """Command line interface for IPA validation"""
    if len(sys.argv) != 3:
        print("Usage: python ipa_validator.py <word> <predicted_ipa>")
        print("Example: python ipa_validator.py trabajo tɾaβaxo")
        sys.exit(1)
    
    word = sys.argv[1]
    predicted_ipa = sys.argv[2]
    
    # Setup logging using project pattern
    logger = setup_logging(level=logging.INFO)
    
    try:
        is_valid = validate_spanish_ipa(word, predicted_ipa)
        
        if is_valid:
            logger.info(f"{ICONS['check']} VALID: '{word}' → '{predicted_ipa}'")
            sys.exit(0)
        else:
            logger.error(f"{ICONS['cross']} INVALID: '{word}' → '{predicted_ipa}'")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"{ICONS['cross']} Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()