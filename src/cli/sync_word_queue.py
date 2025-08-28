#!/usr/bin/env python3
"""
Word Queue Synchronization and Management CLI

Provides commands for manually managing word_queue.json:
- Sync with vocabulary.json (remove all processed/skipped words)
- Show queue status and statistics
- Remove specific words from queue
"""

import argparse
import sys
from pathlib import Path
from typing import List

from utils.logging_config import setup_logging, ICONS
from utils.word_queue_manager import WordQueueManager


def cmd_sync(queue_manager: WordQueueManager, args) -> int:
    """Synchronize word queue with vocabulary by removing processed/skipped words."""
    logger = setup_logging()
    
    logger.info(f"{ICONS['info']} Synchronizing word queue with vocabulary...")
    queue_manager.sync_queue_with_vocabulary()
    return 0


def cmd_status(queue_manager: WordQueueManager, args) -> int:
    """Show current word queue status and statistics."""
    logger = setup_logging()
    
    status = queue_manager.get_queue_status()
    
    logger.info(f"{ICONS['info']} Word Queue Status:")
    logger.info(f"  📋 Total words in queue: {status['total_in_queue']}")
    logger.info(f"  ✅ Total processed words: {status['total_processed']}")
    logger.info(f"  ⏭️  Total skipped words: {status['total_skipped']}")
    
    if status['next_5_words']:
        logger.info(f"  🔜 Next {len(status['next_5_words'])} words: {', '.join(status['next_5_words'])}")
    else:
        logger.info(f"  🔚 Queue is empty")
    
    metadata = status.get('metadata', {})
    if 'created' in metadata:
        logger.info(f"  📅 Queue created: {metadata['created']}")
    if 'last_updated' in metadata:
        logger.info(f"  🔄 Last updated: {metadata['last_updated']}")
    
    return 0


def cmd_remove(queue_manager: WordQueueManager, args) -> int:
    """Remove specific words from the queue."""
    logger = setup_logging()
    
    if not args.words:
        logger.error(f"{ICONS['cross']} No words provided to remove")
        return 1
    
    words_to_remove = [w.strip() for w in args.words.split(',') if w.strip()]
    if not words_to_remove:
        logger.error(f"{ICONS['cross']} No valid words provided")
        return 1
    
    logger.info(f"{ICONS['info']} Removing {len(words_to_remove)} words from queue...")
    updated_queue = queue_manager.remove_words_from_queue(words_to_remove, "manual_removal")
    queue_manager.save_word_queue(updated_queue)
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Word queue synchronization and management")
    
    # Resolve project root
    project_root = Path.cwd()
    queue_manager = WordQueueManager(project_root)
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize queue with vocabulary (remove processed/skipped words)')
    sync_parser.set_defaults(func=lambda args: cmd_sync(queue_manager, args))
    
    # Status command  
    status_parser = subparsers.add_parser('status', help='Show queue status and statistics')
    status_parser.set_defaults(func=lambda args: cmd_status(queue_manager, args))
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove specific words from queue')
    remove_parser.add_argument('--words', type=str, required=True, 
                              help='Comma-separated list of words to remove from queue')
    remove_parser.set_defaults(func=lambda args: cmd_remove(queue_manager, args))
    
    args = parser.parse_args()
    
    try:
        return args.func(args)
    except Exception as e:
        logger = setup_logging()
        logger.error(f"{ICONS['cross']} Command failed: {e}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())