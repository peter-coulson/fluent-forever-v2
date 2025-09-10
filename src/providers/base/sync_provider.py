"""
Sync Provider Interface

Abstract interface for sync targets (Anki, other flashcard systems, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.logging_config import ICONS, get_logger


@dataclass
class SyncRequest:
    """Request for sync operation"""

    target: str  # Target identifier (anki, etc.)
    data: Any  # Data to sync
    params: dict[str, Any] | None = None  # Additional parameters

    def __post_init__(self) -> None:
        """Validate request after initialization"""
        if not self.target:
            raise ValueError("Sync target cannot be empty")
        if self.data is None:
            raise ValueError("Sync data cannot be None")
        if self.params is None:
            self.params = {}


@dataclass
class SyncResult:
    """Result of sync operation"""

    success: bool
    processed_count: int
    metadata: dict[str, Any]
    error_message: str = ""
    created_ids: list[Any] | None = None

    def __post_init__(self) -> None:
        """Validate result after initialization"""
        if self.created_ids is None:
            self.created_ids = []


class SyncProvider(ABC):
    """Abstract interface for sync targets"""

    def __init__(self) -> None:
        self.logger = get_logger(f"providers.sync.{self.__class__.__name__.lower()}")

    def test_connection(self) -> bool:
        """Test connection to sync target

        Returns:
            True if connection is successful
        """
        self.logger.info(f"{ICONS['gear']} Testing connection to sync service...")

        try:
            result = self._test_connection_impl()

            if result:
                self.logger.info(f"{ICONS['check']} Connection test successful")
            else:
                self.logger.error(f"{ICONS['cross']} Connection test failed")

            return result
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Connection test error: {e}")
            return False

    @abstractmethod
    def _test_connection_impl(self) -> bool:
        """Implementation-specific connection test"""
        pass

    @abstractmethod
    def sync_templates(self, note_type: str, templates: list[dict]) -> SyncResult:
        """Sync templates to target

        Args:
            note_type: Note type/model name
            templates: List of template dictionaries with Front/Back HTML

        Returns:
            SyncResult indicating success/failure
        """
        pass

    @abstractmethod
    def sync_media(self, media_files: list[Path]) -> SyncResult:
        """Sync media files to target

        Args:
            media_files: List of media file paths to sync

        Returns:
            SyncResult indicating success/failure
        """
        pass

    def sync_cards(self, cards: list[dict]) -> SyncResult:
        """Sync card data to target

        Args:
            cards: List of card dictionaries with field data

        Returns:
            SyncResult indicating success/failure
        """
        card_count = len(cards)
        self.logger.info(f"{ICONS['gear']} Syncing {card_count} cards...")

        try:
            result = self._sync_cards_impl(cards)

            if result.success:
                self.logger.info(
                    f"{ICONS['check']} Sync completed: {result.processed_count}/{card_count} cards processed"
                )
                if hasattr(result, "metadata") and result.metadata:
                    self.logger.debug(f"Sync stats: {result.metadata}")
            else:
                self.logger.error(
                    f"{ICONS['cross']} Sync failed: {result.error_message}"
                )

            return result
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Sync operation failed: {e}")
            return SyncResult(
                success=False, processed_count=0, metadata={}, error_message=str(e)
            )

    @abstractmethod
    def _sync_cards_impl(self, cards: list[dict]) -> SyncResult:
        """Implementation-specific card syncing"""
        pass

    @abstractmethod
    def list_existing(self, note_type: str) -> list[dict]:
        """List existing items of specified type

        Args:
            note_type: Note type to query

        Returns:
            List of existing items with their data
        """
        pass

    def sync_single_card(self, card_data: dict[str, Any]) -> SyncResult:
        """Sync a single card (convenience method)

        Args:
            card_data: Single card dictionary

        Returns:
            SyncResult for the single card sync
        """
        result = self.sync_cards([card_data])
        if result.success and result.metadata:
            # If batch sync succeeded, create single-card result
            return SyncResult(
                success=True,
                processed_count=1,
                metadata={"cards_synced": 1, **result.metadata},
            )
        return result
