"""
Word Analysis Stage

Analyzes word meanings for vocabulary pipeline. This stage is responsible for
taking a list of words and determining their distinct meanings that need
separate cards.
"""

from pathlib import Path
from typing import Any

from src.core.context import PipelineContext
from src.core.stages import Stage, StageResult, StageStatus
from src.utils.logging_config import ICONS, get_logger


class WordAnalysisStage(Stage):
    """Analyze word meanings (vocabulary pipeline specific)"""

    def __init__(self):
        self.logger = get_logger("stages.claude.analysis")

    @property
    def name(self) -> str:
        return "analyze_words"

    @property
    def display_name(self) -> str:
        return "Analyze Word Meanings"

    def execute(self, context: PipelineContext) -> StageResult:
        """Analyze words and extract distinct meanings"""
        words = context.get("words", [])
        if not words:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No words provided for analysis",
                data={},
                errors=["Missing 'words' in context"],
            )

        # Validate words are in proper format
        if isinstance(words, str):
            # Convert comma-separated string to list
            words = [w.strip() for w in words.split(",") if w.strip()]
        elif not isinstance(words, list):
            return StageResult(
                status=StageStatus.FAILURE,
                message="Words must be a list or comma-separated string",
                data={},
                errors=["Invalid words format"],
            )

        # Check against existing vocabulary to avoid duplicates
        project_root = Path(context.get("project_root", Path.cwd()))
        vocabulary_file = project_root / "vocabulary.json"

        try:
            # Load existing vocabulary to check for already processed words
            existing_words = set()
            skipped_words = set()

            if vocabulary_file.exists():
                import json

                with open(vocabulary_file, encoding="utf-8") as f:
                    vocab_data = json.load(f)
                    existing_words = set(vocab_data.get("words", {}).keys())
                    skipped_words = set(vocab_data.get("skipped_words", []))

            # Filter out already processed words
            new_words = []
            already_processed = []
            already_skipped = []

            for word in words:
                word = word.strip()
                if word in existing_words:
                    already_processed.append(word)
                elif word in skipped_words:
                    already_skipped.append(word)
                else:
                    new_words.append(word)

            # Log filtering results
            if already_processed:
                self.logger.info(
                    f"{ICONS['info']} Skipping {len(already_processed)} already processed words: {already_processed}"
                )
            if already_skipped:
                self.logger.info(
                    f"{ICONS['info']} Skipping {len(already_skipped)} previously skipped words: {already_skipped}"
                )

            if not new_words:
                self.logger.warning(
                    f"{ICONS['warning']} All words have already been processed or skipped"
                )
                return StageResult(
                    status=StageStatus.SUCCESS,
                    message="All words already processed or skipped",
                    data={
                        "analyzed_words": [],
                        "already_processed": already_processed,
                        "already_skipped": already_skipped,
                    },
                    errors=[],
                )

            # For now, this is a placeholder for actual analysis
            # In a real implementation, this would do semantic analysis
            analyzed_meanings = self.analyze_meanings(new_words)

            # Store results in context
            context.set("analyzed_meanings", analyzed_meanings)
            context.set("words_to_process", new_words)
            context.set("already_processed_words", already_processed)
            context.set("already_skipped_words", already_skipped)

            self.logger.info(
                f"{ICONS['check']} Analyzed {len(new_words)} words with {len(analyzed_meanings)} total meanings"
            )

            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Analyzed {len(new_words)} words with {len(analyzed_meanings)} meanings",
                data={
                    "analyzed_meanings": analyzed_meanings,
                    "words_to_process": new_words,
                    "already_processed": already_processed,
                    "already_skipped": already_skipped,
                },
                errors=[],
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Analysis failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Analysis failed: {e}",
                data={},
                errors=[f"Analysis error: {e}"],
            )

    def analyze_meanings(self, words: list[str]) -> list[dict[str, Any]]:
        """
        Analyze words and extract distinct meanings

        This is a placeholder implementation. In the real system, this would
        involve sophisticated analysis to identify distinct semantic meanings
        that require separate memory anchors.

        Args:
            words: List of Spanish words to analyze

        Returns:
            List of meaning dictionaries with placeholder data
        """
        meanings = []

        for word in words:
            # Placeholder: assume each word has one meaning for now
            # Real implementation would identify multiple meanings per word
            meaning = {
                "word": word,
                "meaning_id": "primary",
                "description": f"Primary meaning of {word}",
                "example": f"Example sentence with {word}",
                "context": "General usage",
            }
            meanings.append(meaning)

        return meanings
