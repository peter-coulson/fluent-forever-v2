#!/usr/bin/env python3
"""
Entry point for Vocabulary Structure Validator
Validates vocabulary.json structure and content against schema
"""

import sys
import json
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from validation.internal.vocabulary_validator import VocabularyValidator

def load_config() -> dict:
    """Load configuration"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config.json: {e}")
        sys.exit(1)

def load_vocabulary() -> dict:
    """Load vocabulary.json"""
    try:
        with open('vocabulary.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load vocabulary.json: {e}")
        sys.exit(1)

def main():
    """Main validation function"""
    print("🔍 VOCABULARY.JSON STRUCTURE VALIDATOR")
    print("=" * 45)
    
    try:
        # Load data
        config = load_config()
        vocab_data = load_vocabulary()
        
        # Create validator
        validator = VocabularyValidator(config)
        
        # Run validation
        print("🔍 Validating vocabulary.json structure and content...\n")
        is_valid = validator.validate(vocab_data)
        
        # Print report
        print(validator.get_report())
        
        # Exit with appropriate code
        if is_valid:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ VALIDATION FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()