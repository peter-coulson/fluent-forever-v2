#!/usr/bin/env python3
"""
Entry point for Anki Sync Validator
Runs the sync validation from the project root
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from validation.anki.sync_validator import validate_sync

if __name__ == "__main__":
    success = validate_sync()
    sys.exit(0 if success else 1)