#!/usr/bin/env python3
"""
Word Queue Management Utility

Provides programmatic management of word_queue.json including:
- Removing processed words from the queue
- Removing skipped words from the queue
- Updating queue metadata
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.logging_config import ICONS, setup_logging


class WordQueueManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.word_queue_path = project_root / "word_queue.json"
        self.vocabulary_path = project_root / "vocabulary.json"
        self.logger = setup_logging()

    def load_word_queue(self) -> dict[str, Any]:
        """Load word_queue.json or return empty structure if not found."""
        if not self.word_queue_path.exists():
            self.logger.warning(
                f"{ICONS['warning']} Word queue file not found: {self.word_queue_path}"
            )
            return {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "source": "empty",
                    "total_words": 0,
                    "excluded_processed": 0,
                    "excluded_skipped": 0,
                },
                "words": [],
            }

        try:
            return json.loads(self.word_queue_path.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to load word queue: {e}")
            raise

    def load_vocabulary(self) -> dict[str, Any]:
        """Load vocabulary.json or return empty structure if not found."""
        if not self.vocabulary_path.exists():
            return {"words": {}, "skipped_words": []}

        try:
            return json.loads(self.vocabulary_path.read_text(encoding="utf-8"))
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to load vocabulary: {e}")
            raise

    def get_processed_and_skipped_words(self) -> tuple[set[str], set[str]]:
        """Get sets of processed and skipped words from vocabulary.json."""
        vocab = self.load_vocabulary()
        processed = set(vocab.get("words", {}).keys())
        skipped = set(vocab.get("skipped_words", []))
        return processed, skipped

    def validate_words_in_queue(
        self, words_to_check: list[str]
    ) -> tuple[list[str], list[str]]:
        """
        Check which words exist in the queue and which don't.

        Args:
            words_to_check: List of words to validate

        Returns:
            Tuple of (words_in_queue, words_not_in_queue)
        """
        if not words_to_check:
            return [], []

        queue = self.load_word_queue()
        queue_words_set = set(queue.get("words", []))

        words_in_queue = [word for word in words_to_check if word in queue_words_set]
        words_not_in_queue = [
            word for word in words_to_check if word not in queue_words_set
        ]

        return words_in_queue, words_not_in_queue

    def remove_words_from_queue(
        self,
        words_to_remove: list[str],
        reason: str = "processed",
        require_exists: bool = False,
    ) -> dict[str, Any]:
        """
        Remove specified words from word_queue.json and return updated queue.

        Args:
            words_to_remove: List of words to remove from queue
            reason: Reason for removal (for logging)
            require_exists: If True, raise error if any words are not in queue

        Returns:
            Updated word queue dictionary

        Raises:
            ValueError: If require_exists=True and words are not found in queue
        """
        if not words_to_remove:
            return self.load_word_queue()

        # Validate words exist if required
        if require_exists:
            words_in_queue, words_not_in_queue = self.validate_words_in_queue(
                words_to_remove
            )
            if words_not_in_queue:
                raise ValueError(
                    f"Words not found in queue: {', '.join(words_not_in_queue)}"
                )

        queue = self.load_word_queue()
        original_words = queue.get("words", [])
        words_to_remove_set = set(words_to_remove)

        # Filter out words to remove
        updated_words = [
            word for word in original_words if word not in words_to_remove_set
        ]
        removed_count = len(original_words) - len(updated_words)

        if removed_count > 0:
            # Update queue structure
            queue["words"] = updated_words

            # Update metadata
            metadata = queue.get("metadata", {})
            metadata["last_updated"] = datetime.now().isoformat()
            metadata["total_words"] = len(updated_words)
            metadata[f"removed_{reason}"] = (
                metadata.get(f"removed_{reason}", 0) + removed_count
            )
            queue["metadata"] = metadata

            self.logger.info(
                f"{ICONS['check']} Removed {removed_count} {reason} words from queue"
            )
        else:
            self.logger.info(
                f"{ICONS['info']} No {reason} words found in queue to remove"
            )

        return queue

    def update_queue_after_batch_processing(
        self, processed_words: list[str], skipped_words: list[str] = None
    ) -> None:
        """
        Update word_queue.json after batch processing by removing processed and skipped words.

        Args:
            processed_words: Words that were successfully processed
            skipped_words: Words that were skipped in this batch (optional)
        """
        if skipped_words is None:
            skipped_words = []

        all_words_to_remove = processed_words + skipped_words

        if not all_words_to_remove:
            self.logger.info(f"{ICONS['info']} No words to remove from queue")
            return

        # Remove all words from queue
        updated_queue = self.remove_words_from_queue(
            all_words_to_remove, "batch_processing"
        )

        # Save updated queue
        self.save_word_queue(updated_queue)

        # Log summary
        processed_count = len(processed_words)
        skipped_count = len(skipped_words)
        total_removed = len(all_words_to_remove)

        self.logger.info(
            f"{ICONS['check']} Queue updated: removed {total_removed} words "
            f"({processed_count} processed, {skipped_count} skipped)"
        )

    def sync_queue_with_vocabulary(self) -> None:
        """
        Synchronize word_queue.json with vocabulary.json by removing all processed and skipped words.
        This is useful for cleanup and ensuring consistency.
        """
        processed_words, skipped_words = self.get_processed_and_skipped_words()
        all_words_to_remove = list(processed_words | skipped_words)

        if not all_words_to_remove:
            self.logger.info(
                f"{ICONS['info']} Queue is already synchronized with vocabulary"
            )
            return

        updated_queue = self.remove_words_from_queue(
            all_words_to_remove, "synchronization"
        )
        self.save_word_queue(updated_queue)

        self.logger.info(
            f"{ICONS['check']} Queue synchronized: removed {len(processed_words)} processed "
            f"and {len(skipped_words)} skipped words"
        )

    def save_word_queue(self, queue: dict[str, Any]) -> None:
        """Save word queue to disk."""
        try:
            self.word_queue_path.write_text(
                json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            self.logger.info(
                f"{ICONS['check']} Word queue saved: {self.word_queue_path}"
            )
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to save word queue: {e}")
            raise

    def get_next_words(self, count: int = 5) -> list[str]:
        """Get the next N words from the queue."""
        queue = self.load_word_queue()
        words = queue.get("words", [])
        return words[:count]

    def get_queue_status(self) -> dict[str, Any]:
        """Get current queue status and statistics."""
        queue = self.load_word_queue()
        processed_words, skipped_words = self.get_processed_and_skipped_words()

        return {
            "total_in_queue": len(queue.get("words", [])),
            "total_processed": len(processed_words),
            "total_skipped": len(skipped_words),
            "next_5_words": self.get_next_words(5),
            "metadata": queue.get("metadata", {}),
        }
