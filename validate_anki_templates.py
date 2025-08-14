#!/usr/bin/env python3
"""
Entry point to validate Anki templates via src/validation module.
Delegates to src/validation/anki/template_validator.py
"""

import sys
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from validation.anki.template_validator import validate_templates_and_fields  # noqa: E402


if __name__ == "__main__":
    ok = validate_templates_and_fields()
    sys.exit(0 if ok else 1)


