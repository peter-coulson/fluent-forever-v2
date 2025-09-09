#!/usr/bin/env python3
"""
IPA Validation Stage
Validates Spanish IPA pronunciation against reference dictionary
Migrated from src/validation/ipa_validator.py to new stage structure
"""

from pathlib import Path
from typing import Any

from src.stages.base.validation_stage import ValidationStage
from src.utils.logging_config import get_logger

logger = get_logger("stages.validation.ipa")


class IPAValidationStage(ValidationStage):
    """Validates Spanish IPA pronunciation in pipeline data"""

    def __init__(self, data_key: str, dictionary_path: str | None = None):
        """
        Initialize IPA validation stage

        Args:
            data_key: Key in context for vocabulary data to validate
            dictionary_path: Path to Spanish IPA dictionary file
        """
        super().__init__(data_key)

        if dictionary_path is None:
            # Default to bundled dictionary
            current_dir = Path(__file__).parent.parent.parent
            resolved_path = (
                current_dir / "validation" / "data" / "spanish_ipa_dictionary.txt"
            )
        else:
            resolved_path = Path(dictionary_path)

        self.dictionary_path = resolved_path
        self.dictionary = self._load_dictionary()

    def validate_data(self, data: Any) -> list[str]:
        """
        Validate IPA data and return list of error messages

        Args:
            data: Vocabulary data with words containing IPA pronunciations

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not isinstance(data, dict):
            return ["Data must be a dictionary"]

        words = data.get("words", [])
        if not isinstance(words, list):
            return ["'words' must be a list"]

        for i, word_entry in enumerate(words):
            if not isinstance(word_entry, dict):
                errors.append(f"Word entry {i} must be a dictionary")
                continue

            word = word_entry.get("word", "").strip()
            predicted_ipa = word_entry.get("ipa", "").strip()

            if not word:
                errors.append(f"Word entry {i} missing 'word' field")
                continue

            if not predicted_ipa:
                errors.append(f"Word '{word}' missing IPA pronunciation")
                continue

            # Validate IPA against dictionary
            validation_result = self.validate_word_ipa(word, predicted_ipa)
            if not validation_result[0]:  # If validation failed
                errors.append(
                    f"IPA validation failed for '{word}': {validation_result[1]}"
                )

        return errors

    def validate_word_ipa(self, word: str, predicted_ipa: str) -> tuple[bool, str]:
        """
        Validate a single word's IPA pronunciation

        Args:
            word: Spanish word
            predicted_ipa: Predicted IPA pronunciation

        Returns:
            Tuple of (is_valid, message)
        """
        word = word.lower().strip()

        if word not in self.dictionary:
            # Not in dictionary - can't validate but not necessarily wrong
            logger.debug(f"Word '{word}' not found in reference dictionary")
            return True, "Word not in reference dictionary (unable to validate)"

        reference_ipa = self.dictionary[word]

        # Normalize both IPAs for comparison
        predicted_normalized = self._normalize_ipa(predicted_ipa)
        reference_normalized = self._normalize_ipa(reference_ipa)

        if predicted_normalized == reference_normalized:
            logger.debug(f"✓ IPA for '{word}' matches reference: {predicted_ipa}")
            return True, "IPA matches reference dictionary"

        # Check for stress-only differences
        predicted_no_stress = self._remove_stress_marks(predicted_normalized)
        reference_no_stress = self._remove_stress_marks(reference_normalized)

        if predicted_no_stress == reference_no_stress:
            logger.debug(
                f"~ IPA for '{word}' matches except for stress: predicted={predicted_ipa}, reference={reference_ipa}"
            )
            return True, "IPA matches reference except for stress placement"

        # Validation failed
        logger.warning(
            f"✗ IPA mismatch for '{word}': predicted='{predicted_ipa}' vs reference='{reference_ipa}'"
        )
        return (
            False,
            f"Predicted '{predicted_ipa}' differs from reference '{reference_ipa}'",
        )

    def _load_dictionary(self) -> dict[str, str]:
        """Load dictionary from file into memory"""
        if not self.dictionary_path.exists():
            logger.warning(f"Dictionary file not found: {self.dictionary_path}")
            return {}

        dictionary = {}
        try:
            with open(self.dictionary_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split("\t")
                    if len(parts) != 2:
                        logger.warning(f"Malformed line {line_num}: {line}")
                        continue

                    word, ipa = parts
                    dictionary[word.lower()] = ipa

            logger.debug(f"Loaded {len(dictionary)} entries from IPA dictionary")
            return dictionary

        except Exception as e:
            logger.error(f"Error loading dictionary: {e}")
            return {}

    def _normalize_ipa(self, ipa: str) -> str:
        """Normalize IPA for comparison by removing syllable markers"""
        # Remove syllable boundaries (periods)
        normalized = ipa.replace(".", "")
        return normalized.strip()

    def _remove_stress_marks(self, ipa: str) -> str:
        """Remove stress marks from IPA"""
        # Remove primary (ˈ) and secondary (ˌ) stress marks
        no_stress = ipa.replace("ˈ", "").replace("ˌ", "")
        return no_stress.strip()
