#!/usr/bin/env python3
"""
Synchronize Anki with local sources:
 - Update templates if changed
 - Push missing media
 - Upsert cards from vocabulary.json

Usage:
  python sync_anki_all.py [--force-media] [--delete-extras]
"""

import argparse
import sys
from pathlib import Path

# Add src
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from apis.anki_client import AnkiClient  # noqa: E402
from sync.templates_sync import load_local_templates, fetch_anki_templates, has_template_diffs, push_templates  # noqa: E402
from sync.media_sync import load_vocabulary, referenced_media, list_anki_media, compute_missing, push_missing_media  # noqa: E402
from sync.cards_sync import upsert_cards  # noqa: E402
from validation.anki.template_validator import validate_templates_and_fields  # noqa: E402
from validation.anki.sync_validator import validate_sync_structured  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-media', action='store_true', help='Force re-upload all referenced media')
    args = parser.parse_args()

    logger = setup_logging()
    anki = AnkiClient()
    if not anki.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to AnkiConnect.")
        return 1

    note_type_folder = anki.note_type.replace(' ', '_')
    tmpl_dir = PROJECT_ROOT / 'templates' / 'anki' / note_type_folder
    vocab_path = PROJECT_ROOT / 'vocabulary.json'

    # 1) Templates
    try:
        local_templates, local_css = load_local_templates(tmpl_dir)
        anki_map, anki_css = fetch_anki_templates(anki)
        if has_template_diffs(local_templates, anki_map, local_css, anki_css):
            push_templates(anki, local_templates, local_css)
        # Validate placeholders and exact match
        validate_templates_and_fields(PROJECT_ROOT)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Template sync failed: {e}")
        return 1

    # 2) Media
    try:
        vocab = load_vocabulary(vocab_path)
        ref_images, ref_audio = referenced_media(vocab)
        if args.force_media:
            # Force: push all referenced media regardless of Anki state
            push_missing_media(anki, PROJECT_ROOT, ref_images, ref_audio)
        else:
            anki_images, anki_audio = list_anki_media(anki)
            missing_images, missing_audio = compute_missing(ref_images, ref_audio, anki_images, anki_audio)
            push_missing_media(anki, PROJECT_ROOT, missing_images, missing_audio)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Media sync failed: {e}")
        return 1

    # 3) Cards (upsert)
    try:
        card_summary = upsert_cards(anki, vocab)
        logger.info(f"{ICONS['check']} Cards upsert → created: {card_summary['created']}, updated: {card_summary['updated']}, skipped: {card_summary['skipped']}")
    except Exception as e:
        logger.error(f"{ICONS['cross']} Card sync failed: {e}")
        return 1

    # 4) Post-validate Anki vs vocabulary
    result = validate_sync_structured()
    if not result.is_synchronized():
        logger.error(f"{ICONS['cross']} Post-sync validation found differences. Please run validate_anki_sync.py for details.")
        return 2

    logger.info(f"{ICONS['check']} Anki is synchronized with local templates, media, and vocabulary.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


