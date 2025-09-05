#!/usr/bin/env python3
"""
Multi-Card Type Anki Sync

Extended sync system that supports multiple card types (Fluent Forever, Conjugation, etc.)
while maintaining backwards compatibility.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from utils.logging_config import setup_logging, ICONS
from utils.card_types import get_card_type_registry
from apis.anki_client import AnkiClient
from sync.templates_sync import load_local_templates, fetch_anki_templates, has_template_diffs, push_templates
from sync.media_sync import load_vocabulary, referenced_media, list_anki_media, compute_missing, push_missing_media
from validation.anki.template_validator import validate_templates_and_fields


def sync_card_type(card_type_name: str, anki: AnkiClient, project_root: Path, args) -> bool:
    """Sync a specific card type to Anki"""
    logger = setup_logging().getChild(f'sync.{card_type_name}')
    card_registry = get_card_type_registry()
    
    # Get card type
    card_type = card_registry.get(card_type_name)
    if not card_type:
        logger.error(f"{ICONS['cross']} Unknown card type: {card_type_name}")
        return False
    
    logger.info(f"{ICONS['gear']} Syncing card type: {card_type_name} → {card_type.note_type}")
    
    # Setup paths
    tmpl_dir = project_root / 'templates' / 'anki' / card_type.name
    if not tmpl_dir.exists():
        logger.error(f"{ICONS['cross']} Template directory not found: {tmpl_dir}")
        return False
    
    # Create AnkiClient configured for this card type
    anki_for_type = AnkiClient()
    # Override the note type for this sync
    original_note_type = anki_for_type.note_type
    anki_for_type.note_type = card_type.note_type
    
    try:
        # 1) Templates
        try:
            local_templates, local_css = load_local_templates(tmpl_dir)
            anki_map, anki_css = fetch_anki_templates(anki_for_type)
            if has_template_diffs(local_templates, anki_map, local_css, anki_css):
                if not push_templates(anki_for_type, local_templates, local_css):
                    return False
                logger.info(f"{ICONS['check']} Templates synced for {card_type_name}")
            else:
                logger.info(f"{ICONS['check']} Templates up to date for {card_type_name}")
        except Exception as e:
            logger.error(f"{ICONS['cross']} Template sync failed for {card_type_name}: {e}")
            return False

        # 2) Cards - placeholder for now since we need to implement card sync logic
        try:
            # Load card data
            data = card_type.load_data(project_root) 
            cards = card_type.list_cards(data)
            logger.info(f"{ICONS['check']} Found {len(cards)} cards for {card_type_name}")
            
            # TODO: Implement card upsert logic for different card types
            # For now, just log the cards that would be synced
            if cards:
                logger.info(f"{ICONS['gear']} Cards ready for sync:")
                for card in cards[:3]:  # Show first 3
                    card_id = card.get('CardID', 'unknown')
                    logger.info(f"   - {card_id}")
                if len(cards) > 3:
                    logger.info(f"   ... and {len(cards) - 3} more")
            else:
                logger.warning(f"{ICONS['warning']} No cards found for {card_type_name}")
                
        except NotImplementedError:
            logger.warning(f"{ICONS['warning']} Card data loading not yet implemented for {card_type_name}")
        except Exception as e:
            logger.error(f"{ICONS['cross']} Card sync failed for {card_type_name}: {e}")
            return False

        logger.info(f"{ICONS['check']} Sync completed for {card_type_name}")
        return True
        
    finally:
        # Restore original note type
        anki_for_type.note_type = original_note_type


def main() -> int:
    parser = argparse.ArgumentParser(description='Multi-card type Anki sync')
    parser.add_argument('--card-type', help='Specific card type to sync (default: all)')
    parser.add_argument('--list-types', action='store_true', help='List available card types')
    parser.add_argument('--force-media', action='store_true', help='Force re-upload all referenced media')
    parser.add_argument('--delete-extras', action='store_true', help='Identify and delete extra notes')
    args = parser.parse_args()

    logger = setup_logging()
    card_registry = get_card_type_registry()
    
    # List available card types
    if args.list_types:
        logger.info(f"{ICONS['info']} Available card types:")
        for type_name in card_registry.list_types():
            card_type = card_registry.get(type_name)
            logger.info(f"   - {type_name} → Anki note type: '{card_type.note_type}'")
        return 0
    
    # Connect to Anki
    anki = AnkiClient()
    if not anki.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to AnkiConnect.")
        return 1

    project_root = Path(__file__).parents[2]
    
    # Determine which card types to sync
    if args.card_type:
        card_types_to_sync = [args.card_type]
        if not card_registry.get(args.card_type):
            logger.error(f"{ICONS['cross']} Unknown card type: {args.card_type}")
            return 1
    else:
        card_types_to_sync = card_registry.list_types()
    
    # Sync each card type
    success_count = 0
    for card_type_name in card_types_to_sync:
        try:
            if sync_card_type(card_type_name, anki, project_root, args):
                success_count += 1
            else:
                logger.error(f"{ICONS['cross']} Failed to sync {card_type_name}")
        except Exception as e:
            logger.error(f"{ICONS['cross']} Unexpected error syncing {card_type_name}: {e}")
    
    total_types = len(card_types_to_sync)
    if success_count == total_types:
        logger.info(f"{ICONS['check']} Successfully synced all {total_types} card types")
        return 0
    else:
        logger.error(f"{ICONS['cross']} Synced {success_count}/{total_types} card types")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())