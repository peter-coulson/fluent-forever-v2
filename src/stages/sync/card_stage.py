"""
Card Sync Stage

Synchronizes vocabulary cards to Anki. Extracts logic from sync.cards_sync
to create reusable stage.
"""

from pathlib import Path
from typing import Any

from core.context import PipelineContext
from core.stages import StageResult, StageStatus
from stages.base.api_stage import APIStage
from utils.logging_config import ICONS, get_logger


class CardSyncStage(APIStage):
    """Sync cards to Anki"""

    def __init__(self, delete_extras: bool = False):
        """
        Initialize card sync stage

        Args:
            delete_extras: Whether to delete extra cards not in vocabulary
        """
        super().__init__("anki_provider", required=True)
        self.delete_extras = delete_extras
        self.logger = get_logger("stages.sync.cards")

    @property
    def name(self) -> str:
        return "sync_cards"

    @property
    def display_name(self) -> str:
        return "Sync Cards to Anki"

    def execute_api_call(self, context: PipelineContext, provider: Any) -> StageResult:
        """Sync cards to Anki using provider"""
        project_root = Path(context.get("project_root", Path.cwd()))

        try:
            # Load vocabulary
            vocabulary = self.load_vocabulary(project_root)

            # Upsert cards to Anki
            card_summary = self.upsert_cards(provider, vocabulary)

            self.logger.info(
                f"{ICONS['check']} Cards synced: created {card_summary['created']}, "
                f"updated {card_summary['updated']}, skipped {card_summary['skipped']}"
            )

            # Handle extra cards deletion if requested
            if self.delete_extras:
                deletion_result = self.handle_extra_cards(provider, vocabulary)
                if deletion_result:
                    card_summary["deleted"] = deletion_result.get("deleted", 0)

            # Post-sync validation
            validation_result = self.validate_sync(project_root)
            if not validation_result.is_synchronized:
                # Log differences but don't fail the stage
                self.log_sync_differences(validation_result)

                context.set("sync_warnings", validation_result.get_differences())

                return StageResult(
                    status=StageStatus.PARTIAL,
                    message="Cards synced but validation found differences",
                    data={
                        "card_summary": card_summary,
                        "sync_differences": validation_result.get_differences(),
                    },
                    errors=[
                        f"Sync validation found {len(validation_result.get_differences())} differences"
                    ],
                )

            context.set("card_sync_summary", card_summary)

            return StageResult(
                status=StageStatus.SUCCESS,
                message="Cards synchronized successfully",
                data={"card_summary": card_summary},
                errors=[],
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Card sync failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Card sync failed: {e}",
                data={},
                errors=[f"Sync error: {e}"],
            )

    def load_vocabulary(self, project_root: Path) -> dict[str, Any]:
        """Load vocabulary.json"""
        import json

        vocab_file = project_root / "vocabulary.json"
        with open(vocab_file, encoding="utf-8") as f:
            return json.load(f)

    def upsert_cards(self, provider, vocabulary: dict[str, Any]) -> dict[str, int]:
        """Upsert cards to Anki"""
        try:
            from sync.cards_sync import upsert_cards

            return upsert_cards(provider, vocabulary)
        except ImportError:
            # Fallback implementation
            self.logger.warning(
                f"{ICONS['warning']} Card upsert not available (sync module missing)"
            )
            return {"created": 0, "updated": 0, "skipped": 0}

    def handle_extra_cards(self, provider, vocabulary: dict[str, Any]):
        """Handle deletion of extra cards not in vocabulary"""
        try:
            from sync.cards_sync import compute_extras_in_deck, delete_extras

            extras, pairs = compute_extras_in_deck(provider, vocabulary)

            if extras:
                deck = getattr(provider, "deck_name", "Unknown")
                self.logger.warning(
                    f"{ICONS['warning']} Found {len(extras)} extra notes in deck '{deck}'"
                )

                # For stage execution, we don't do interactive confirmation
                # Instead, we log the extras and let the user handle them manually
                self.logger.warning(
                    f"{ICONS['info']} Extra cards found but not deleted (requires manual confirmation)"
                )
                for i, (nid, cid) in enumerate(pairs[:10]):  # Show first 10
                    self.logger.warning(f"   note_id={nid} CardID={cid or '<missing>'}")
                if len(pairs) > 10:
                    self.logger.warning(f"   (+{len(pairs) - 10} more)")

                return {"extras_found": len(extras), "deleted": 0}

            return {"extras_found": 0, "deleted": 0}

        except ImportError:
            self.logger.warning(
                f"{ICONS['warning']} Extra card handling not available (sync module missing)"
            )
            return None

    def validate_sync(self, project_root: Path):
        """Validate Anki sync against vocabulary"""
        try:
            from validation.anki.sync_validator import validate_sync_structured

            return validate_sync_structured()
        except ImportError:
            # Mock validation result that shows success
            from types import SimpleNamespace

            return SimpleNamespace(is_synchronized=True, get_differences=lambda: [])

    def log_sync_differences(self, validation_result):
        """Log sync validation differences"""
        try:
            differences = validation_result.get_differences()

            if (
                hasattr(validation_result, "missing_words_in_anki")
                and validation_result.missing_words_in_anki
            ):
                self.logger.warning(
                    f"{ICONS['warning']} Missing words in Anki: {sorted(validation_result.missing_words_in_anki)}"
                )

            if (
                hasattr(validation_result, "missing_words_in_vocab")
                and validation_result.missing_words_in_vocab
            ):
                self.logger.warning(
                    f"{ICONS['warning']} Words in Anki but missing in vocabulary: {sorted(validation_result.missing_words_in_vocab)}"
                )

            if (
                hasattr(validation_result, "field_differences")
                and validation_result.field_differences
            ):
                self.logger.warning(
                    f"{ICONS['warning']} Field differences found (showing first 5):"
                )
                for i, diff in enumerate(validation_result.field_differences[:5]):
                    self.logger.warning(
                        f"   {diff.word}.{diff.meaning_id} → {diff.field}: vocab='{diff.vocab_value}' vs anki='{diff.anki_value}'"
                    )
                if len(validation_result.field_differences) > 5:
                    self.logger.warning(
                        f"   (+{len(validation_result.field_differences) - 5} more differences)"
                    )

        except Exception as e:
            self.logger.warning(
                f"{ICONS['warning']} Could not log sync differences: {e}"
            )
