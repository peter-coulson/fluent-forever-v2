"""
Anki Sync Provider

Provides sync operations with Anki via AnkiConnect API.
"""

import os
import time
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from providers.base.sync_provider import SyncProvider, SyncRequest, SyncResult
from apis.anki_client import AnkiClient
from utils.logging_config import get_logger, ICONS

logger = get_logger('providers.sync.anki')


class AnkiSyncProvider(SyncProvider):
    """AnkiConnect-based sync provider"""
    
    def __init__(self, anki_client: Optional[AnkiClient] = None):
        """Initialize Anki sync provider
        
        Args:
            anki_client: Optional AnkiClient instance (creates new one if None)
        """
        self.anki = anki_client or AnkiClient()
    
    def test_connection(self) -> bool:
        """Test AnkiConnect connection
        
        Returns:
            True if connection is successful
        """
        return self.anki.test_connection()
    
    def sync_templates(self, note_type: str, templates: List[Dict]) -> SyncResult:
        """Sync templates to Anki
        
        Args:
            note_type: Note type/model name
            templates: List of template dictionaries with Front/Back HTML
            
        Returns:
            SyncResult indicating success/failure
        """
        try:
            logger.info(f"{ICONS['gear']} Syncing templates for note type: {note_type}")
            
            response = self.anki.update_model_templates(templates, note_type)
            
            if response.success:
                logger.info(f"{ICONS['check']} Templates synced successfully")
                return SyncResult(
                    success=True,
                    target_id=note_type,
                    metadata={
                        'template_count': len(templates),
                        'note_type': note_type
                    }
                )
            else:
                error_msg = response.error_message or "Unknown error syncing templates"
                logger.error(f"{ICONS['cross']} Template sync failed: {error_msg}")
                return SyncResult(
                    success=False,
                    target_id=None,
                    metadata={},
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"Failed to sync templates: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return SyncResult(
                success=False,
                target_id=None,
                metadata={},
                error=error_msg
            )
    
    def sync_media(self, media_files: List[Path]) -> SyncResult:
        """Sync media files to Anki
        
        Args:
            media_files: List of media file paths to sync
            
        Returns:
            SyncResult indicating success/failure
        """
        try:
            logger.info(f"{ICONS['gear']} Syncing {len(media_files)} media files to Anki")
            
            synced_files = []
            failed_files = []
            
            for file_path in media_files:
                if not file_path.exists():
                    logger.warning(f"{ICONS['warning']} Media file not found: {file_path}")
                    failed_files.append(str(file_path))
                    continue
                
                filename = file_path.name
                response = self.anki.store_media_file(file_path, filename)
                
                if response.success:
                    synced_files.append(filename)
                    logger.debug(f"Synced media file: {filename}")
                else:
                    failed_files.append(filename)
                    logger.warning(f"{ICONS['warning']} Failed to sync {filename}: {response.error_message}")
            
            success = len(failed_files) == 0
            
            if success:
                logger.info(f"{ICONS['check']} All media files synced successfully")
            else:
                logger.warning(f"{ICONS['warning']} {len(synced_files)}/{len(media_files)} media files synced")
            
            return SyncResult(
                success=success,
                target_id="anki_media",
                metadata={
                    'total_files': len(media_files),
                    'synced_files': synced_files,
                    'failed_files': failed_files,
                    'success_count': len(synced_files),
                    'failed_count': len(failed_files)
                },
                error=f"{len(failed_files)} files failed to sync" if failed_files else None
            )
            
        except Exception as e:
            error_msg = f"Failed to sync media files: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return SyncResult(
                success=False,
                target_id=None,
                metadata={},
                error=error_msg
            )
    
    def sync_cards(self, cards: List[Dict]) -> SyncResult:
        """Sync card data to Anki
        
        Args:
            cards: List of card dictionaries with field data
            
        Returns:
            SyncResult indicating success/failure
        """
        try:
            logger.info(f"{ICONS['gear']} Syncing {len(cards)} cards to Anki")
            
            synced_cards = []
            failed_cards = []
            created_note_ids = []
            
            for card_data in cards:
                card_id = card_data.get('CardID', 'unknown')
                
                try:
                    # Create card in Anki
                    response = self.anki.create_card(card_data)
                    
                    if response.success:
                        note_id = response.data.get('note_id') if response.data else None
                        synced_cards.append(card_id)
                        if note_id:
                            created_note_ids.append(note_id)
                        logger.debug(f"Synced card: {card_id}")
                    else:
                        failed_cards.append({
                            'card_id': card_id,
                            'error': response.error_message
                        })
                        logger.warning(f"{ICONS['warning']} Failed to sync {card_id}: {response.error_message}")
                        
                except Exception as e:
                    failed_cards.append({
                        'card_id': card_id,
                        'error': str(e)
                    })
                    logger.warning(f"{ICONS['warning']} Exception syncing {card_id}: {e}")
            
            success = len(failed_cards) == 0
            
            if success:
                logger.info(f"{ICONS['check']} All cards synced successfully")
            else:
                logger.warning(f"{ICONS['warning']} {len(synced_cards)}/{len(cards)} cards synced")
            
            return SyncResult(
                success=success,
                target_id=self.anki.deck_name,
                metadata={
                    'total_cards': len(cards),
                    'synced_cards': synced_cards,
                    'failed_cards': failed_cards,
                    'created_note_ids': created_note_ids,
                    'success_count': len(synced_cards),
                    'failed_count': len(failed_cards)
                },
                error=f"{len(failed_cards)} cards failed to sync" if failed_cards else None
            )
            
        except Exception as e:
            error_msg = f"Failed to sync cards: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return SyncResult(
                success=False,
                target_id=None,
                metadata={},
                error=error_msg
            )
    
    def list_existing(self, note_type: str) -> List[Dict]:
        """List existing cards from Anki deck
        
        Args:
            note_type: Note type to query (not used - uses deck instead)
            
        Returns:
            List of existing cards with their data
        """
        try:
            response = self.anki.get_deck_cards()
            
            if response.success:
                cards_data = response.data
                # Flatten the nested structure word -> meaning -> fields
                existing_cards = []
                for word, meanings in cards_data.items():
                    for meaning_id, fields in meanings.items():
                        existing_cards.append(fields)
                
                return existing_cards
            else:
                logger.error(f"{ICONS['cross']} Failed to list existing cards: {response.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"{ICONS['cross']} Error listing existing cards: {e}")
            return []
    
    def sync_styling(self, css: str, note_type: Optional[str] = None) -> SyncResult:
        """Sync CSS styling to Anki note type
        
        Args:
            css: CSS styling content
            note_type: Note type name (uses default if None)
            
        Returns:
            SyncResult indicating success/failure
        """
        try:
            if note_type is None:
                note_type = self.anki.note_type
            
            logger.info(f"{ICONS['gear']} Syncing styling for note type: {note_type}")
            
            response = self.anki.update_model_styling(css, note_type)
            
            if response.success:
                logger.info(f"{ICONS['check']} Styling synced successfully")
                return SyncResult(
                    success=True,
                    target_id=note_type,
                    metadata={
                        'note_type': note_type,
                        'css_length': len(css)
                    }
                )
            else:
                error_msg = response.error_message or "Unknown error syncing styling"
                logger.error(f"{ICONS['cross']} Styling sync failed: {error_msg}")
                return SyncResult(
                    success=False,
                    target_id=None,
                    metadata={},
                    error=error_msg
                )
                
        except Exception as e:
            error_msg = f"Failed to sync styling: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return SyncResult(
                success=False,
                target_id=None,
                metadata={},
                error=error_msg
            )
    
    def get_note_type_info(self, note_type: Optional[str] = None) -> Dict[str, Any]:
        """Get information about Anki note type
        
        Args:
            note_type: Note type name (uses default if None)
            
        Returns:
            Dictionary with note type information
        """
        try:
            if note_type is None:
                note_type = self.anki.note_type
            
            # Get field names
            fields_response = self.anki.get_model_field_names(note_type)
            field_names = fields_response.data if fields_response.success else []
            
            # Get templates
            templates_response = self.anki.get_model_templates(note_type)
            templates = templates_response.data if templates_response.success else {}
            
            # Get styling
            styling_response = self.anki.get_model_styling(note_type)
            styling = styling_response.data if styling_response.success else ""
            
            return {
                'note_type': note_type,
                'field_names': field_names,
                'templates': templates,
                'styling': styling,
                'deck_name': self.anki.deck_name
            }
            
        except Exception as e:
            logger.error(f"{ICONS['cross']} Error getting note type info: {e}")
            return {
                'note_type': note_type,
                'error': str(e)
            }