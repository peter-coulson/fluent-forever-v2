"""
Mock Sync Provider

Mock provider for testing that simulates sync operations without actual syncing.
"""

import time
from pathlib import Path
from typing import Dict, List, Any
from providers.base.sync_provider import SyncProvider, SyncRequest, SyncResult


class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing"""
    
    def __init__(self, should_fail: bool = False):
        """Initialize mock sync provider
        
        Args:
            should_fail: If True, operations will always fail (for error testing)
        """
        self.should_fail = should_fail
        self.connection_available = True
        
        # Track operations for testing verification
        self.synced_templates: List[Dict] = []
        self.synced_cards: List[Dict] = []
        self.synced_media: List[Path] = []
        self.existing_cards: List[Dict] = []
        
        # Counters
        self.template_sync_count = 0
        self.card_sync_count = 0
        self.media_sync_count = 0
    
    def test_connection(self) -> bool:
        """Test mock connection
        
        Returns:
            True if connection is available
        """
        return self.connection_available
    
    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        """Mock template sync
        
        Args:
            note_type: Note type/model name
            templates: List of template dictionaries
            
        Returns:
            SyncResult with mock data
        """
        self.template_sync_count += 1
        
        # Simulate failure if configured
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={'mock': True, 'failure_mode': True},
                error_message="Mock provider configured to fail"
            )
        
        # Simulate some processing time
        time.sleep(0.05)
        
        # Store templates for verification
        for template in templates:
            self.synced_templates.append({
                'note_type': note_type,
                'template': template,
                'sync_count': self.template_sync_count
            })
        
        return SyncResult(
            success=True,
            processed_count=len(templates),
            metadata={
                'mock': True,
                'template_count': len(templates),
                'note_type': note_type,
                'sync_id': self.template_sync_count,
                'target_id': note_type
            }
        )
    
    def sync_media(self, media_files: List[Path]) -> SyncResult:
        """Mock media sync
        
        Args:
            media_files: List of media file paths
            
        Returns:
            SyncResult with mock data
        """
        self.media_sync_count += 1
        
        # Simulate failure if configured
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={'mock': True, 'failure_mode': True},
                error_message="Mock provider configured to fail"
            )
        
        # Simulate processing time based on file count
        time.sleep(len(media_files) * 0.01)
        
        # Track synced files
        self.synced_media.extend(media_files)
        
        return SyncResult(
            success=True,
            processed_count=len(media_files),
            metadata={
                'mock': True,
                'total_files': len(media_files),
                'synced_files': [f.name for f in media_files],
                'success_count': len(media_files),
                'failed_count': 0,
                'sync_id': self.media_sync_count,
                'target_id': "mock_media"
            }
        )
    
    def sync_cards(self, cards: List[Dict]) -> SyncResult:
        """Mock card sync
        
        Args:
            cards: List of card dictionaries
            
        Returns:
            SyncResult with mock data
        """
        self.card_sync_count += 1
        
        # Simulate failure if configured
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={'mock': True, 'failure_mode': True},
                error_message="Mock provider configured to fail"
            )
        
        # Simulate processing time based on card count
        time.sleep(len(cards) * 0.02)
        
        # Store cards and generate mock note IDs
        synced_cards = []
        created_note_ids = []
        
        for i, card_data in enumerate(cards):
            # Add sync metadata
            card_with_meta = card_data.copy()
            card_with_meta['mock_note_id'] = f"mock_note_{self.card_sync_count}_{i}"
            card_with_meta['sync_timestamp'] = time.time()
            
            self.synced_cards.append(card_with_meta)
            synced_cards.append(card_data.get('CardID', f'card_{i}'))
            created_note_ids.append(card_with_meta['mock_note_id'])
        
        return SyncResult(
            success=True,
            processed_count=len(cards),
            metadata={
                'mock': True,
                'total_cards': len(cards),
                'synced_cards': synced_cards,
                'success_count': len(cards),
                'failed_count': 0,
                'sync_id': self.card_sync_count,
                'target_id': "mock_deck"
            },
            created_ids=created_note_ids
        )
    
    def list_existing(self, note_type: str) -> List[Dict]:
        """List existing mock cards
        
        Args:
            note_type: Note type to query
            
        Returns:
            List of existing cards
        """
        # Return configured existing cards, filtered by note_type if specified
        if note_type and note_type != "mock":
            # Return empty list for non-mock note types
            return []
        
        return self.existing_cards.copy()
    
    # Testing utility methods
    def clear_history(self) -> None:
        """Clear all sync history (testing utility)"""
        self.synced_templates.clear()
        self.synced_cards.clear()
        self.synced_media.clear()
        self.template_sync_count = 0
        self.card_sync_count = 0
        self.media_sync_count = 0
    
    def set_existing_cards(self, cards: List[Dict]) -> None:
        """Set mock existing cards (testing utility)"""
        self.existing_cards = cards.copy()
    
    def get_synced_templates(self) -> List[Dict]:
        """Get all synced templates (testing utility)"""
        return self.synced_templates.copy()
    
    def get_synced_cards(self) -> List[Dict]:
        """Get all synced cards (testing utility)"""
        return self.synced_cards.copy()
    
    def get_synced_media(self) -> List[Path]:
        """Get all synced media files (testing utility)"""
        return self.synced_media.copy()
    
    def set_failure_mode(self, should_fail: bool) -> None:
        """Enable/disable failure mode (testing utility)"""
        self.should_fail = should_fail
    
    def set_connection_available(self, available: bool) -> None:
        """Set connection availability (testing utility)"""
        self.connection_available = available
    
    def get_sync_counts(self) -> Dict[str, int]:
        """Get sync operation counts (testing utility)"""
        return {
            'template_syncs': self.template_sync_count,
            'card_syncs': self.card_sync_count,
            'media_syncs': self.media_sync_count,
            'total_templates': len(self.synced_templates),
            'total_cards': len(self.synced_cards),
            'total_media': len(self.synced_media)
        }