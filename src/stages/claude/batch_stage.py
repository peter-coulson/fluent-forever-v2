"""
Batch Preparation Stage

Prepares Claude staging files for batch processing. Extracts logic from
cli.prepare_claude_batch to create reusable stage.
"""

import json
from datetime import datetime
from pathlib import Path

from core.context import PipelineContext
from core.stages import Stage, StageResult, StageStatus
from utils.logging_config import ICONS, get_logger


class BatchPreparationStage(Stage):
    """Prepare Claude staging batch"""

    def __init__(self):
        self.logger = get_logger("stages.claude.batch_preparation")

    @property
    def name(self) -> str:
        return "prepare_batch"

    @property
    def display_name(self) -> str:
        return "Prepare Claude Batch"

    def execute(self, context: PipelineContext) -> StageResult:
        """Prepare staging file for Claude to fill"""
        words = context.get("words", [])
        if not words:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No words provided for batch preparation",
                data={},
                errors=["Missing 'words' in context"],
            )

        # Handle string input (comma-separated)
        if isinstance(words, str):
            words = [w.strip() for w in words.split(",") if w.strip()]

        if not words:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No valid words after parsing",
                data={},
                errors=["No valid words found"],
            )

        # Get project root and create staging directory
        project_root = Path(context.get("project_root", Path.cwd()))
        staging_dir = project_root / "staging"
        staging_dir.mkdir(exist_ok=True)

        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = context.get("output_path")

        if output_path:
            staging_file = Path(output_path)
        else:
            staging_file = staging_dir / f"claude_batch_{timestamp}.json"

        # Create staging document structure (from prepare_claude_batch.py)
        staging_doc = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "source": "claude-staging",
                "instructions": (
                    "Claude: enumerate distinct meanings for each word, and fill the 'meanings' array below "
                    "with entries conforming to the schema in CLAUDE.md and config.json (meaning_entry). "
                    "Add any words to skip to the 'skipped_words' array."
                ),
            },
            "words": words,
            "meanings": [],
            "skipped_words": [],
        }

        try:
            # Write staging file
            with open(staging_file, "w", encoding="utf-8") as f:
                json.dump(staging_doc, f, ensure_ascii=False, indent=2)

            # Store results in context
            context.set("staging_file", str(staging_file))
            context.set("batch_words", words)
            context.set("batch_timestamp", timestamp)

            self.logger.info(f"{ICONS['check']} Staging file created: {staging_file}")

            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Created staging file: {staging_file}",
                data={
                    "staging_file": str(staging_file),
                    "words": words,
                    "timestamp": timestamp,
                },
                errors=[],
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to create staging file: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Failed to create staging file: {e}",
                data={},
                errors=[f"File creation error: {e}"],
            )
