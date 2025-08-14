#!/usr/bin/env python3
"""
Entry point for Local Media Validator
Validates that local media files match vocabulary.json references
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from validation.internal.media_validator import validate_local_vs_vocabulary
from utils.logging_config import setup_logging, ICONS

# Initialize logging
setup_logging()

if __name__ == "__main__":
    import logging
    logger = logging.getLogger('fluent_forever')
    
    result = validate_local_vs_vocabulary()
    
    logger.info(f"{ICONS['search']} LOCAL MEDIA ↔ VOCABULARY.JSON VALIDATOR")
    logger.info("=" * 48)
    logger.info(f"{ICONS['chart']} SUMMARY: {result.total_missing()} missing files")
    
    if result.missing_images:
        logger.error(f"{ICONS['cross']} IMAGES REFERENCED BUT MISSING LOCALLY:")
        for image in sorted(result.missing_images):
            logger.error(f"   • {image}")
    
    if result.missing_audio:
        logger.error(f"{ICONS['cross']} AUDIO REFERENCED BUT MISSING LOCALLY:")
        for audio in sorted(result.missing_audio):
            logger.error(f"   • {audio}")
    
    if result.has_missing_files():
        logger.error(f"{ICONS['cross']} VALIDATION FAILED")
        logger.error("   Differences found between local media and vocabulary.json references")
        sys.exit(1)
    else:
        logger.info(f"{ICONS['check']} VALIDATION PASSED")
        logger.info("   Local media and vocabulary.json references are perfectly synchronized!")
        sys.exit(0)