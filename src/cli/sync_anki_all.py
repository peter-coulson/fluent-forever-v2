#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from utils.logging_config import setup_logging, ICONS
from apis.anki_client import AnkiClient
from sync.templates_sync import load_local_templates, fetch_anki_templates, has_template_diffs, push_templates
from sync.media_sync import load_vocabulary, referenced_media, list_anki_media, compute_missing, push_missing_media
from sync.cards_sync import upsert_cards, compute_extras_in_deck, delete_extras
from validation.anki.template_validator import validate_templates_and_fields
from validation.anki.sync_validator import validate_sync_structured


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--force-media', action='store_true', help='Force re-upload all referenced media')
    parser.add_argument('--delete-extras', action='store_true', help='Identify notes not present in vocabulary.json and prompt for deletion')
    args = parser.parse_args()

    logger = setup_logging()
    anki = AnkiClient()
    if not anki.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to AnkiConnect.")
        return 1

    project_root = Path(__file__).parents[2]
    note_type_folder = anki.note_type.replace(' ', '_')
    tmpl_dir = project_root / 'templates' / 'anki' / note_type_folder
    vocab_path = project_root / 'vocabulary.json'

    # 1) Templates
    try:
        local_templates, local_css = load_local_templates(tmpl_dir)
        anki_map, anki_css = fetch_anki_templates(anki)
        if has_template_diffs(local_templates, anki_map, local_css, anki_css):
            push_templates(anki, local_templates, local_css)
        # Validate placeholders and exact match; hard-fail on mismatch
        if not validate_templates_and_fields(project_root):
            logger.error(f"{ICONS['cross']} Template validation failed. Please fix errors and re-run.")
            return 1
    except Exception as e:
        logger.error(f"{ICONS['cross']} Template sync failed: {e}")
        return 1

    # 2) Media
    try:
        vocab = load_vocabulary(vocab_path)
        ref_images, ref_audio = referenced_media(vocab)
        if args.force_media:
            # Force: push all referenced media regardless of Anki state
            push_missing_media(anki, project_root, ref_images, ref_audio)
        else:
            anki_images, anki_audio = list_anki_media(anki)
            missing_images, missing_audio = compute_missing(ref_images, ref_audio, anki_images, anki_audio)
            push_missing_media(anki, project_root, missing_images, missing_audio)
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

    # 3b) Optional: delete extras not in vocabulary.json
    if args.delete_extras:
        extras, pairs = compute_extras_in_deck(anki, vocab)
        if extras:
            deck = anki.deck_name
            logger.warning(f"{ICONS['warning']} Found {len(extras)} notes in deck not present in vocabulary.json:")
            # Show up to 20 items for safety review
            to_show = pairs[:20]
            for nid, cid in to_show:
                logger.warning(f"   note_id={nid} CardID={cid or '<missing>'}")
            if len(pairs) > len(to_show):
                logger.warning(f"   (+{len(pairs) - len(to_show)} more)")

            # Explicit human confirmation required
            phrase = f"DELETE {len(extras)} NOTES IN DECK '{deck}'"
            logger.error("LLM OPERATOR NOTICE: Do NOT auto-respond to the next prompt. Human approval required.")
            logger.error("To proceed with deletion, type the exact confirmation phrase below and press Enter:")
            logger.error(phrase)
            # Require a real TTY to approve deletion. If stdin is not a TTY, abort.
            if not sys.stdin.isatty():
                logger.error("Interactive confirmation requires a TTY. Piped/automated input is not accepted. Aborting deletion.")
                user_input = ''
            else:
                try:
                    user_input = input('Type the confirmation phrase exactly to proceed, or press Enter to abort: ').strip()
                except Exception:
                    user_input = ''
            if user_input != phrase:
                logger.warning(f"{ICONS['warning']} Deletion aborted. No changes made to Anki.")
            else:
                logger.warning(f"{ICONS['warning']} Proceeding to delete {len(extras)} notes from '{deck}'...")
                ok = delete_extras(anki, extras)
                if not ok:
                    logger.error(f"{ICONS['cross']} Failed to delete extras")
                    return 1
                logger.info(f"{ICONS['check']} Deleted {len(extras)} notes")

    # 4) Post-validate Anki vs vocabulary
    result = validate_sync_structured()
    if not result.is_synchronized():
        logger.error(f"{ICONS['cross']} Post-sync validation found differences.")
        # Log specific diffs for quick diagnosis
        if result.missing_words_in_anki:
            logger.error(f"   Missing words in Anki: {sorted(result.missing_words_in_anki)}")
        if result.missing_words_in_vocab:
            logger.error(f"   Words present in Anki but missing in vocabulary.json: {sorted(result.missing_words_in_vocab)}")
        if result.missing_meanings_in_anki:
            for w, ms in result.missing_meanings_in_anki.items():
                logger.error(f"   Missing meanings in Anki for '{w}': {ms}")
        if result.missing_meanings_in_vocab:
            for w, ms in result.missing_meanings_in_vocab.items():
                logger.error(f"   Meanings in Anki but missing in vocabulary.json for '{w}': {ms}")
        # Limit field diffs output to avoid spam
        if result.field_differences:
            max_show = 10
            logger.error(f"   Field differences (showing up to {max_show}):")
            for i, d in enumerate(result.field_differences[:max_show]):
                logger.error(f"     {d.word}.{d.meaning_id} → {d.field}: vocab='{d.vocab_value}' vs anki='{d.anki_value}'")
            if len(result.field_differences) > max_show:
                logger.error(f"   (+{len(result.field_differences) - max_show} more field diffs)")
        return 2

    logger.info(f"{ICONS['check']} Anki is synchronized with local templates, media, and vocabulary.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


