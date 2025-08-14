#!/usr/bin/env python3
"""
End-to-end workflow: generate media for given CardIDs, then run Anki sync.

Only runs sync if media generation succeeds.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from sync.media_generation import run_media_generation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=str, required=True, help='Comma-separated CardIDs to process')
    parser.add_argument('--max', dest='max_new', type=int, default=5, help='Max new media to generate (default 5)')
    parser.add_argument('--no-images', action='store_true', help='Skip image generation')
    parser.add_argument('--no-audio', action='store_true', help='Skip audio generation')
    parser.add_argument('--force-regenerate', action='store_true', help='Regenerate even if provenance hash differs')
    parser.add_argument('--execute', action='store_true', help='Execute media generation (otherwise dry-run)')
    parser.add_argument('--delete-extras', action='store_true', help='During sync, prompt to delete notes not in vocabulary.json')

    args = parser.parse_args()
    setup_logging()

    card_ids = [c.strip() for c in args.cards.split(',') if c.strip()]
    if not card_ids:
        print(f"{ICONS['warning']} No CardIDs provided; nothing to do.")
        return 0

    ok = run_media_generation(
        project_root=PROJECT_ROOT,
        card_ids=card_ids,
        max_new=args.max_new,
        dry_run=not args.execute,
        force_regenerate=args.force_regenerate,
        skip_images=args.no_images,
        skip_audio=args.no_audio,
    )

    if not ok:
        print(f"{ICONS['cross']} Media generation failed; skipping Anki sync.")
        return 1

    # Chain to main sync script
    cmd = [sys.executable, str(PROJECT_ROOT / 'sync_anki_all.py')]
    if args.delete_extras:
        cmd.append('--delete-extras')
    print(f"{ICONS['gear']} Running: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    return res.returncode


if __name__ == '__main__':
    raise SystemExit(main())


