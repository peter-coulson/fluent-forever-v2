#!/usr/bin/env python3
"""
Regenerate images for specific CardIDs regardless of existing files.

Safety features:
- Validates vocabulary.json structure
- Shows how many images will be overwritten
- Requires interactive TTY confirmation with exact phrase
- Creates timestamped backups before overwrite (default)

Usage examples:
  # Preview (no API calls)
  python regenerate_images.py --cards con_instrument

  # Execute with confirmation
  python regenerate_images.py --cards con_instrument --execute
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from apis.base_client import BaseAPIClient  # noqa: E402
from apis.openai_client import OpenAIClient  # noqa: E402
from sync.media_generation import (
    load_vocabulary,
    build_meaning_index,
    validate_vocabulary,
    load_provenance,
    save_provenance,
    hash_prompt,
)  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=str, default='', help='Comma-separated CardIDs to regenerate')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backups before overwrite')
    parser.add_argument('--execute', action='store_true', help='Execute (not dry-run)')
    args = parser.parse_args()

    setup_logging()

    card_ids = [c.strip() for c in args.cards.split(',') if c.strip()]
    if not card_ids:
        print(f"{ICONS['warning']} No CardIDs provided; nothing to do.")
        return 0

    # Validate vocabulary
    if not validate_vocabulary(PROJECT_ROOT):
        return 1

    vocab = load_vocabulary(PROJECT_ROOT)
    idx = build_meaning_index(vocab)

    # Build worklist
    work = []
    for cid in card_ids:
        meaning = idx.get(cid)
        if not meaning:
            print(f"{ICONS['warning']} CardID not found in vocabulary.json: {cid}")
            continue
        img = meaning.get('ImageFile', '')
        if not img:
            print(f"{ICONS['warning']} No ImageFile for CardID: {cid}")
            continue
        work.append((cid, img, meaning.get('SpanishWord', ''), meaning.get('prompt', '')))

    if not work:
        print(f"{ICONS['warning']} Nothing to regenerate")
        return 0

    media_images = PROJECT_ROOT / 'media' / 'images'
    backup_dir = media_images / '_backup'

    # Preview
    print(f"{ICONS['chart']} Plan to regenerate {len(work)} images:")
    for cid, img, word, _ in work:
        print(f"  - {cid} → {img} (word={word})")

    if not args.execute:
        print(f"{ICONS['info']} DRY-RUN: no changes made. Use --execute to proceed.")
        return 0

    # Interactive confirmation with TTY requirement
    phrase = f"REGENERATE {len(work)} IMAGES"
    print("LLM OPERATOR NOTICE: Do NOT auto-respond to the next prompt. Human approval required.")
    print("To proceed, type the exact confirmation phrase below and press Enter:")
    print(phrase)
    if not sys.stdin.isatty():
        print("Interactive confirmation requires a TTY. Piped/automated input is not accepted. Aborting.")
        return 1
    try:
        user_input = input('Type the confirmation phrase exactly to proceed, or press Enter to abort: ').strip()
    except Exception:
        user_input = ''
    if user_input != phrase:
        print(f"{ICONS['warning']} Aborted. No changes made.")
        return 1

    # Execute regeneration
    client = OpenAIClient()
    prov = load_provenance(PROJECT_ROOT)
    backups_made = 0
    regenerated = 0
    failed = 0
    for cid, img, word, prompt in work:
        path = media_images / img
        if path.exists() and not args.no_backup:
            backup_dir.mkdir(parents=True, exist_ok=True)
            ts = int(time.time())
            backup_path = backup_dir / f"{img}.{ts}.bak"
            try:
                backup_path.write_bytes(path.read_bytes())
                backups_made += 1
            except Exception as e:
                print(f"{ICONS['warning']} Failed to backup {img}: {e}")
        print(f"{ICONS['gear']} Regenerating {img} for {cid}...")
        resp = client.generate_image(prompt, img)
        if resp.success:
            prov[img] = {
                'word': word,
                'prompt_hash': hash_prompt(word, prompt),
                'provider': 'openai',
                'created_at': time.time(),
                'regenerated': True,
            }
            regenerated += 1
            print(f"{ICONS['check']} Regenerated {img}")
        else:
            failed += 1
            print(f"{ICONS['cross']} Regeneration failed for {img}: {resp.error_message}")

    save_provenance(PROJECT_ROOT, prov)
    print(f"{ICONS['chart']} Summary: regenerated={regenerated}, failed={failed}, backups={backups_made}")
    return 0 if failed == 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())


