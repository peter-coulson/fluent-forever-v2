"""
Data Validation Stage

Validates card data structure and content. Ensures data conforms to expected
schemas and contains required fields.
"""

from typing import Any

from stages.base.validation_stage import ValidationStage
from utils.logging_config import get_logger


class DataValidationStage(ValidationStage):
    """Validate card data structure"""

    def __init__(self, data_key: str = "vocabulary", schema_type: str = "vocabulary"):
        """
        Initialize data validation stage

        Args:
            data_key: Key in context for data to validate
            schema_type: Type of schema validation to perform
        """
        super().__init__(data_key)
        self.schema_type = schema_type
        self.logger = get_logger("stages.validation.data")

    @property
    def name(self) -> str:
        return f"validate_{self.data_key}"

    @property
    def display_name(self) -> str:
        return f"Validate {self.data_key.replace('_', ' ').title()} Data"

    def execute(self, context):
        """Execute validation - supports both dict and PipelineContext"""
        # Convert dict context to PipelineContext if needed for compatibility
        if isinstance(context, dict):
            from pathlib import Path

            from core.context import PipelineContext

            project_root = Path(context.get("project_root", Path.cwd()))
            pipeline_name = context.get("pipeline_name", "test_pipeline")

            pipeline_context = PipelineContext(
                pipeline_name=pipeline_name, project_root=project_root
            )

            for key, value in context.items():
                pipeline_context.set(key, value)

            result = super().execute(pipeline_context)

            # Convert result back to dict for compatibility
            result_dict = {
                "status": "success" if result.status.value == "success" else "failure",
                "message": result.message,
                "data": result.data,
                "errors": result.errors,
            }

            # Copy input data to output for chaining
            result_dict.update(context)

            return result_dict

        # If it's already a PipelineContext, use normal flow
        return super().execute(context)

    def validate_data(self, data: dict[str, Any]) -> list[str]:
        """Validate data structure and content"""
        errors = []

        # Basic structure validation
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return errors

        # Schema-specific validation
        if self.schema_type == "vocabulary":
            errors.extend(self.validate_vocabulary_structure(data))
        elif self.schema_type == "cards":
            errors.extend(self.validate_cards_structure(data))
        elif self.schema_type == "staging":
            errors.extend(self.validate_staging_structure(data))
        else:
            errors.append(f"Unknown schema type: {self.schema_type}")

        return errors

    def validate_vocabulary_structure(self, vocab: dict[str, Any]) -> list[str]:
        """Validate vocabulary.json structure"""
        errors = []

        # Check required top-level keys
        required_keys = ["metadata", "words"]
        for key in required_keys:
            if key not in vocab:
                errors.append(f"Missing required key: {key}")

        # Validate metadata
        if "metadata" in vocab:
            metadata = vocab["metadata"]
            if not isinstance(metadata, dict):
                errors.append("Metadata must be a dictionary")
            else:
                required_meta = [
                    "created",
                    "last_updated",
                    "total_words",
                    "total_cards",
                ]
                for key in required_meta:
                    if key not in metadata:
                        errors.append(f"Missing metadata key: {key}")

        # Validate words structure
        if "words" in vocab:
            words = vocab["words"]
            if not isinstance(words, dict):
                errors.append("Words must be a dictionary")
            else:
                for word, word_data in words.items():
                    word_errors = self.validate_word_entry(word, word_data)
                    errors.extend(word_errors)

        # Validate skipped words
        if "skipped_words" in vocab:
            skipped = vocab["skipped_words"]
            if not isinstance(skipped, list):
                errors.append("Skipped words must be a list")

        return errors

    def validate_word_entry(self, word: str, word_data: dict[str, Any]) -> list[str]:
        """Validate individual word entry"""
        errors = []

        if not isinstance(word_data, dict):
            errors.append(f"Word '{word}' data must be a dictionary")
            return errors

        # Check required keys
        required_keys = ["word", "meanings"]
        for key in required_keys:
            if key not in word_data:
                errors.append(f"Word '{word}' missing required key: {key}")

        # Validate meanings
        if "meanings" in word_data:
            meanings = word_data["meanings"]
            if not isinstance(meanings, list):
                errors.append(f"Word '{word}' meanings must be a list")
            else:
                for i, meaning in enumerate(meanings):
                    meaning_errors = self.validate_meaning_entry(word, i, meaning)
                    errors.extend(meaning_errors)

        return errors

    def validate_meaning_entry(
        self, word: str, index: int, meaning: dict[str, Any]
    ) -> list[str]:
        """Validate individual meaning entry"""
        errors = []

        if not isinstance(meaning, dict):
            errors.append(f"Word '{word}' meaning {index} must be a dictionary")
            return errors

        # Check required fields for Fluent Forever cards
        required_fields = [
            "SpanishWord",
            "MeaningID",
            "MeaningContext",
            "MonolingualDef",
            "ExampleSentence",
            "GappedSentence",
            "IPA",
            "CardID",
            "ImageFile",
        ]

        for field in required_fields:
            if field not in meaning or not meaning[field]:
                errors.append(
                    f"Word '{word}' meaning {index} missing required field: {field}"
                )

        # Validate specific field formats
        if "GappedSentence" in meaning:
            gapped = meaning["GappedSentence"]
            if "_____" not in str(gapped):
                errors.append(
                    f"Word '{word}' meaning {index} GappedSentence must contain '_____'"
                )

        if "CardID" in meaning and "SpanishWord" in meaning and "MeaningID" in meaning:
            expected_id = f"{meaning['SpanishWord']}_{meaning['MeaningID']}"
            if meaning["CardID"] != expected_id:
                errors.append(
                    f"Word '{word}' meaning {index} CardID mismatch: expected '{expected_id}', got '{meaning['CardID']}'"
                )

        return errors

    def validate_cards_structure(self, cards: Any) -> list[str]:
        """Validate cards data structure"""
        errors = []

        if isinstance(cards, list):
            for i, card in enumerate(cards):
                if not isinstance(card, dict):
                    errors.append(f"Card {i} must be a dictionary")
                    continue

                # Validate card has required fields
                if "CardID" not in card:
                    errors.append(f"Card {i} missing CardID")
        else:
            errors.append("Cards must be a list")

        return errors

    def validate_staging_structure(self, staging: dict[str, Any]) -> list[str]:
        """Validate staging file structure"""
        errors = []

        # Check required keys
        required_keys = ["metadata", "words", "meanings"]
        for key in required_keys:
            if key not in staging:
                errors.append(f"Missing required staging key: {key}")

        # Validate meanings format
        if "meanings" in staging:
            meanings = staging["meanings"]
            if not isinstance(meanings, list):
                errors.append("Staging meanings must be a list")

        return errors
