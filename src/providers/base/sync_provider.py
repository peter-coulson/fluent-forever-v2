"""
Sync Provider Interface

Abstract interface for sync targets (Anki, other flashcard systems, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SyncRequest:
    """Request for sync operation"""
    operation: str  # 'create', 'update', 'delete', 'sync_templates', 'sync_media'
    target: str     # Target identifier (note type, deck, etc.)
    data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request after initialization"""
        if not self.operation:
            raise ValueError("Sync operation cannot be empty")
        if not self.target:
            raise ValueError("Sync target cannot be empty")
        if self.data is None:
            self.data = {}
        if self.options is None:
            self.options = {}


@dataclass  
class SyncResult:
    """Result of sync operation"""
    success: bool
    target_id: Optional[str]  # ID of created/updated item
    metadata: Dict[str, Any]
    error: Optional[str] = None
    
    def __post_init__(self):
        """Validate result after initialization"""
        if self.metadata is None:
            self.metadata = {}


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
    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        """Sync templates to target
        
        Args:
            note_type: Note type/model name
            templates: List of template dictionaries with Front/Back HTML
            
        Returns:
            SyncResult indicating success/failure
        """
        pass
    
    @abstractmethod
    def sync_media(self, media_files: List[Path]) -> SyncResult:
        """Sync media files to target
        
        Args:
            media_files: List of media file paths to sync
            
        Returns:
            SyncResult indicating success/failure
        """
        pass
    
    @abstractmethod
    def sync_cards(self, cards: List[Dict]) -> SyncResult:
        """Sync card data to target
        
        Args:
            cards: List of card dictionaries with field data
            
        Returns:
            SyncResult indicating success/failure
        """
        pass
    
    @abstractmethod
    def list_existing(self, note_type: str) -> List[Dict]:
        """List existing items of specified type
        
        Args:
            note_type: Note type to query
            
        Returns:
            List of existing items with their data
        """
        pass
    
    def sync_single_card(self, card_data: Dict[str, Any]) -> SyncResult:
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
                target_id=result.target_id,
                metadata={"cards_synced": 1, **result.metadata},
                error=None
            )
        return result