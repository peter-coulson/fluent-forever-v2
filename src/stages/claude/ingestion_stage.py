"""
Batch Ingestion Stage

Ingests completed Claude batch files into vocabulary.json. Extracts logic from
cli.ingest_claude_batch to create reusable stage.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.core.context import PipelineContext
from src.core.stages import Stage, StageResult, StageStatus
from src.utils.logging_config import ICONS, get_logger


class BatchIngestionStage(Stage):
    """Ingest completed Claude batch"""

    def __init__(
        self, skip_ipa_validation: bool = False, update_word_queue: bool = True
    ):
        """
        Initialize batch ingestion stage

        Args:
            skip_ipa_validation: Skip IPA validation (override failures)
            update_word_queue: Update word_queue.json by removing processed words
        """
        self.skip_ipa_validation = skip_ipa_validation
        self.update_word_queue = update_word_queue
        self.logger = get_logger("stages.claude.ingestion")

    @property
    def name(self) -> str:
        return "ingest_batch"

    @property
    def display_name(self) -> str:
        return "Ingest Claude Batch"

    def execute(self, context: PipelineContext) -> StageResult:
        """Ingest Claude batch file into vocabulary"""
        staging_file_path = context.get("staging_file")
        if not staging_file_path:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No staging file path provided",
                data={},
                errors=["Missing 'staging_file' in context"],
            )

        staging_file = Path(staging_file_path)
        if not staging_file.exists():
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Staging file not found: {staging_file}",
                data={},
                errors=[f"File does not exist: {staging_file}"],
            )

        project_root = Path(context.get("project_root", Path.cwd()))

        try:
            # Load staging file
            with open(staging_file, encoding="utf-8") as f:
                staging = json.load(f)

            meanings = staging.get("meanings", [])
            skipped_words = staging.get("skipped_words", [])

            if not isinstance(meanings, list) or (not meanings and not skipped_words):
                return StageResult(
                    status=StageStatus.FAILURE,
                    message="Staging file has no meanings or skipped words to ingest",
                    data={},
                    errors=["Empty staging file"],
                )

            # Validate and derive fields for each meaning
            derived: dict[str, list[dict[str, Any]]] = {}
            validation_errors = []

            for meaning in meanings:
                # Validate required fields (from ingest_claude_batch.py)
                required = [
                    "SpanishWord",
                    "MeaningID",
                    "MeaningContext",
                    "MonolingualDef",
                    "ExampleSentence",
                    "GappedSentence",
                    "IPA",
                    "prompt",
                ]
                missing = [k for k in required if not meaning.get(k)]
                if missing:
                    validation_errors.append(f"Missing fields in meaning: {missing}")
                    continue

                # Validate GappedSentence contains blank
                if "_____" not in str(meaning["GappedSentence"]):
                    validation_errors.append(
                        f"GappedSentence must contain '_____': {meaning['GappedSentence']}"
                    )
                    continue

                # Derive additional fields
                derived_meaning = self.derive_fields(meaning)
                word = derived_meaning["SpanishWord"]
                derived.setdefault(word, []).append(derived_meaning)

            if validation_errors:
                self.logger.error(f"{ICONS['cross']} Validation failed:")
                for error in validation_errors:
                    self.logger.error(f"  - {error}")
                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"Validation failed: {len(validation_errors)} errors",
                    data={},
                    errors=validation_errors,
                )

            # IPA validation (if not skipped)
            if not self.skip_ipa_validation:
                ipa_result = self.validate_ipa(derived)
                if not ipa_result.success:
                    return ipa_result

            # Load existing vocabulary
            vocab_file = project_root / "vocabulary.json"
            vocab = self.load_vocabulary(vocab_file)

            # Process skipped words
            new_skipped_count = self.process_skipped_words(vocab, skipped_words)

            # Merge meanings into vocabulary
            added_cards = self.merge_meanings(vocab, derived)

            # Update metadata
            self.update_vocabulary_metadata(vocab)

            # Validate against schema (if validator available)
            schema_result = self.validate_vocabulary_schema(vocab, project_root)
            if not schema_result.success:
                return schema_result

            # Save vocabulary
            with open(vocab_file, "w", encoding="utf-8") as f:
                json.dump(vocab, f, ensure_ascii=False, indent=2)

            # Update word queue if requested
            if self.update_word_queue:
                queue_result = self.update_word_queue_file(
                    project_root, derived, skipped_words
                )
                if not queue_result.success:
                    self.logger.warning(
                        f"{ICONS['warning']} Word queue update failed: {queue_result.message}"
                    )

            # Store results in context
            context.set("ingested_words", list(derived.keys()))
            context.set("added_cards", added_cards)
            context.set("skipped_words", skipped_words)

            message = f"Ingested {added_cards} meanings across {len(derived)} words"
            if new_skipped_count > 0:
                message += f", {new_skipped_count} new skipped words"

            self.logger.info(f"{ICONS['check']} {message}")

            return StageResult(
                status=StageStatus.SUCCESS,
                message=message,
                data={
                    "ingested_words": list(derived.keys()),
                    "added_cards": added_cards,
                    "skipped_words": skipped_words,
                },
                errors=[],
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Ingestion failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Ingestion failed: {e}",
                data={},
                errors=[f"Ingestion error: {e}"],
            )

    def derive_fields(self, meaning: dict[str, Any]) -> dict[str, Any]:
        """Derive additional fields from meaning (from ingest_claude_batch.py)"""
        spanish = str(meaning["SpanishWord"]).strip()
        meaning_id = str(meaning["MeaningID"]).strip()
        card_id = f"{spanish}_{meaning_id}"

        return {
            **meaning,
            "CardID": card_id,
            "ImageFile": f"{spanish}_{meaning_id}.png",
            "WordAudio": f"[sound:{spanish}.mp3]",
            "WordAudioAlt": "",
            "UsageNote": meaning.get("UsageNote", ""),
        }

    def validate_ipa(self, derived: dict[str, list[dict[str, Any]]]) -> StageResult:
        """Validate IPA pronunciations"""
        try:
            from validation.ipa_validator import validate_spanish_ipa

            self.logger.info(f"{ICONS['search']} Validating IPA pronunciations...")
            ipa_failures = []

            for word, meanings_list in derived.items():
                # Get IPA from first meaning
                first_meaning = meanings_list[0]
                ipa_raw = first_meaning.get("IPA", "").strip("[]/")

                if ipa_raw:
                    try:
                        is_valid = validate_spanish_ipa(word, ipa_raw)
                        if not is_valid:
                            ipa_failures.append(
                                {
                                    "word": word,
                                    "predicted_ipa": ipa_raw,
                                    "meanings_count": len(meanings_list),
                                }
                            )
                    except Exception as e:
                        self.logger.warning(
                            f"{ICONS['warning']} IPA validation error for '{word}': {e}"
                        )

            if ipa_failures:
                self.logger.error(
                    f"{ICONS['cross']} IPA validation failed for {len(ipa_failures)} words:"
                )
                for failure in ipa_failures:
                    self.logger.error(
                        f"  - {failure['word']} → {failure['predicted_ipa']} ({failure['meanings_count']} meanings)"
                    )

                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"IPA validation failed for {len(ipa_failures)} words",
                    data={},
                    errors=[
                        f"IPA validation failed for: {[f['word'] for f in ipa_failures]}"
                    ],
                )

            self.logger.info(
                f"{ICONS['check']} All IPA pronunciations validated successfully"
            )
            return StageResult(
                status=StageStatus.SUCCESS,
                message="IPA validation passed",
                data={},
                errors=[],
            )

        except ImportError:
            self.logger.warning(
                f"{ICONS['warning']} IPA validator not available, skipping validation"
            )
            return StageResult(
                status=StageStatus.SUCCESS,
                message="IPA validation skipped",
                data={},
                errors=[],
            )

    def load_vocabulary(self, vocab_file: Path) -> dict[str, Any]:
        """Load existing vocabulary or create new one"""
        try:
            with open(vocab_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "metadata": {
                    "created": datetime.now().date().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_words": 0,
                    "total_cards": 0,
                    "total_skipped": 0,
                    "source": "claude-ingestion",
                },
                "skipped_words": [],
                "words": {},
            }

    def process_skipped_words(
        self, vocab: dict[str, Any], skipped_words: list[str]
    ) -> int:
        """Process skipped words into vocabulary"""
        if "skipped_words" not in vocab:
            vocab["skipped_words"] = []

        existing_skipped = set(vocab["skipped_words"])
        new_skipped_count = 0

        for word in skipped_words:
            if isinstance(word, str) and word.strip() and word not in existing_skipped:
                vocab["skipped_words"].append(word.strip())
                new_skipped_count += 1

        return new_skipped_count

    def merge_meanings(
        self, vocab: dict[str, Any], derived: dict[str, list[dict[str, Any]]]
    ) -> int:
        """Merge new meanings into vocabulary"""
        added_cards = 0

        for word, new_meanings in derived.items():
            entry = vocab["words"].get(
                word,
                {
                    "word": word,
                    "processed_date": datetime.now().isoformat(),
                    "meanings": [],
                    "cards_created": 0,
                },
            )

            # Merge by MeaningID
            existing_by_id = {m["MeaningID"]: m for m in entry.get("meanings", [])}
            for meaning in new_meanings:
                existing_by_id[meaning["MeaningID"]] = meaning

            merged = list(existing_by_id.values())
            entry["meanings"] = merged
            entry["cards_created"] = len(merged)
            vocab["words"][word] = entry
            added_cards += len(new_meanings)

        return added_cards

    def update_vocabulary_metadata(self, vocab: dict[str, Any]) -> None:
        """Update vocabulary metadata"""
        vocab["metadata"]["last_updated"] = datetime.now().isoformat()
        vocab["metadata"]["total_words"] = len(vocab["words"])
        vocab["metadata"]["total_cards"] = sum(
            len(e["meanings"]) for e in vocab["words"].values()
        )
        vocab["metadata"]["total_skipped"] = len(vocab["skipped_words"])

    def validate_vocabulary_schema(
        self, vocab: dict[str, Any], project_root: Path
    ) -> StageResult:
        """Validate vocabulary against schema"""
        try:
            from apis.base_client import BaseAPIClient
            from validation.internal.vocabulary_validator import VocabularyValidator

            config = BaseAPIClient.load_config(project_root / "config.json")
            validator = VocabularyValidator(config)

            if not validator.validate(vocab):
                return StageResult(
                    status=StageStatus.FAILURE,
                    message="Vocabulary schema validation failed",
                    data={},
                    errors=[validator.get_report()],
                )

            return StageResult(
                status=StageStatus.SUCCESS,
                message="Schema validation passed",
                data={},
                errors=[],
            )

        except ImportError:
            self.logger.warning(
                f"{ICONS['warning']} Vocabulary validator not available, skipping schema validation"
            )
            return StageResult(
                status=StageStatus.SUCCESS,
                message="Schema validation skipped",
                data={},
                errors=[],
            )

    def update_word_queue_file(
        self,
        project_root: Path,
        derived: dict[str, list[dict[str, Any]]],
        skipped_words: list[str],
    ) -> StageResult:
        """Update word queue by removing processed words"""
        try:
            from utils.word_queue_manager import WordQueueManager

            queue_manager = WordQueueManager(project_root)
            processed_words = list(derived.keys())
            all_words_to_remove = processed_words + skipped_words

            if all_words_to_remove:
                # Validate words exist in queue
                (
                    words_in_queue,
                    words_not_in_queue,
                ) = queue_manager.validate_words_in_queue(all_words_to_remove)

                if words_not_in_queue:
                    return StageResult(
                        status=StageStatus.FAILURE,
                        message=f"Words not found in queue: {', '.join(words_not_in_queue)}",
                        data={},
                        errors=[f"Missing from queue: {words_not_in_queue}"],
                    )

                # Remove words from queue
                updated_queue = queue_manager.remove_words_from_queue(
                    all_words_to_remove, "batch_processing", require_exists=True
                )
                queue_manager.save_word_queue(updated_queue)
                self.logger.info(f"{ICONS['check']} Word queue updated successfully")

            return StageResult(
                status=StageStatus.SUCCESS,
                message="Word queue updated",
                data={},
                errors=[],
            )

        except Exception as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Word queue update failed: {e}",
                data={},
                errors=[f"Queue update error: {e}"],
            )
