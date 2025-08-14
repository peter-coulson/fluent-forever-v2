#!/usr/bin/env python3
"""
Entry point: Generate missing media for given CardIDs, then (optionally) run Anki sync.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from sync.media_generation import run_media_generation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=str, default='', help='Comma-separated CardIDs to consider')
    parser.add_argument('--max', dest='max_new', type=int, default=5, help='Max new media to generate (default 5)')
    parser.add_argument('--no-images', action='store_true', help='Skip image generation')
    parser.add_argument('--no-audio', action='store_true', help='Skip audio generation')
    parser.add_argument('--force-regenerate', action='store_true', help='Regenerate even if provenance hash differs')
    parser.add_argument('--execute', action='store_true', help='Execute (not dry-run)')
    parser.add_argument('--then-sync', action='store_true', help='If media generation succeeds, run sync_anki_all.py next')

    args = parser.parse_args()
    setup_logging()

    card_ids = [c.strip() for c in args.cards.split(',') if c.strip()] if args.cards else []
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
        return 1

    if args.then_sync:
        # Chain to main sync
        import subprocess
        cmd = [sys.executable, str(PROJECT_ROOT / 'sync_anki_all.py')]
        print(f"{ICONS['gear']} Running: {' '.join(cmd)}")
        res = subprocess.run(cmd)
        return res.returncode

    return 0


if __name__ == '__main__':
    raise SystemExit(main())


