#!/usr/bin/env python3
"""
Prepare a Claude staging file for a new batch.

- Takes a list of words and writes staging/claude_batch_YYYYMMDD_HHMM.json
  with an empty meanings array for Claude to fill.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

from utils.logging_config import setup_logging, ICONS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--words', type=str, required=True, help='Comma-separated list of words for this batch')
    parser.add_argument('--output', type=str, default='', help='Optional output path (defaults to staging/claude_batch_*.json)')
    args = parser.parse_args()

    logger = setup_logging()

    words: List[str] = [w.strip() for w in args.words.split(',') if w.strip()]
    if not words:
        logger.error(f"{ICONS['cross']} No words provided")
        return 1

    # Resolve project root as current working directory so tests can chdir into tmp projects
    project_root = Path.cwd()
    staging_dir = project_root / 'staging'
    staging_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = Path(args.output) if args.output else (staging_dir / f'claude_batch_{ts}.json')

    doc = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "source": "claude-staging",
            "instructions": "Claude: enumerate distinct meanings for each word, and fill the 'meanings' array below with entries conforming to the schema in CLAUDE.md and config.json (meaning_entry). Add any words to skip to the 'skipped_words' array."
        },
        "words": words,
        "meanings": [],
        "skipped_words": []
    }

    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    logger.info(f"{ICONS['check']} Staging file created: {out_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


