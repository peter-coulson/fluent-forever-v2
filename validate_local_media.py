#!/usr/bin/env python3
"""
Entry point for Local Media Validator
Validates that local media files match vocabulary.json references
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from validation.local_media_validator import validate_local_vs_vocabulary
from utils.logging_config import setup_logging

# Initialize logging
setup_logging()

if __name__ == "__main__":
    success = validate_local_vs_vocabulary()
    sys.exit(0 if success else 1)