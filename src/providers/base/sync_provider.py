"""
Sync Provider Interface

Abstract interface for sync targets (Anki, other flashcard systems, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


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
    created_ids: Optional[list[Any]] = None

    def __post_init__(self) -> None:
        """Validate result after initialization"""
        if self.metadata is None:
            self.metadata = {}
        if self.created_ids is None:
            self.created_ids = []


class SyncProvider(ABC):
    """Abstract interface for sync targets"""

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to sync target

        Returns:
            True if connection is successful
        """
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

    @abstractmethod
    def sync_cards(self, cards: list[dict]) -> SyncResult:
        """Sync card data to target

        Args:
            cards: List of card dictionaries with field data

        Returns:
            SyncResult indicating success/failure
        """
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
