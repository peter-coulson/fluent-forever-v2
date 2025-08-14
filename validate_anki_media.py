#!/usr/bin/env python3
"""
Entry point for Anki Media Validator
Validates that Anki media collection matches local media files
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from validation.anki.media_validator import validate_anki_vs_local
from utils.logging_config import setup_logging, ICONS

# Initialize logging
setup_logging()

if __name__ == "__main__":
    import logging
    logger = logging.getLogger('fluent_forever')
    
    result = validate_anki_vs_local()
    
    logger.info(f"{ICONS['search']} LOCAL MEDIA → ANKI MEDIA VALIDATOR")
    logger.info("=" * 42)
    logger.info(f"{ICONS['chart']} SUMMARY: {result.total_missing()} missing files")
    
    if result.missing_images:
        logger.error(f"{ICONS['cross']} LOCAL IMAGES MISSING IN ANKI:")
        for image in sorted(result.missing_images):
            logger.error(f"   • {image}")
    
    if result.missing_audio:
        logger.error(f"{ICONS['cross']} LOCAL AUDIO MISSING IN ANKI:")
        for audio in sorted(result.missing_audio):
            logger.error(f"   • {audio}")
    
    if result.has_missing_files():
        logger.error(f"{ICONS['cross']} VALIDATION FAILED")
        logger.error("   Some local media files are missing from Anki")
        sys.exit(1)
    else:
        logger.info(f"{ICONS['check']} VALIDATION PASSED")
        logger.info("   All local media files exist in Anki!")
        sys.exit(0)