#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from sync.media_generation import run_media_generation  # noqa: E402
from apis.base_client import BaseAPIClient  # noqa: E402


def main() -> int:
    # Load config to get default max_new_items
    config = BaseAPIClient.load_config(PROJECT_ROOT / 'config.json')
    default_max = config.get('media_generation', {}).get('max_new_items', 5)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cards', type=str, default='', help='Comma-separated CardIDs to consider')
    parser.add_argument('--max', dest='max_new', type=int, default=default_max, help=f'Max new media to generate (default {default_max})')
    parser.add_argument('--no-images', action='store_true', help='Skip image generation')
    parser.add_argument('--no-audio', action='store_true', help='Skip audio generation')
    parser.add_argument('--force-regenerate', action='store_true', help='Regenerate even if provenance hash differs')
    parser.add_argument('--execute', action='store_true', help='Execute (not dry-run)')

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
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())


