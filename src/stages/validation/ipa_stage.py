"""
IPA Validation Stage

Validates IPA pronunciation against authoritative dictionary. Extracts logic 
from validation.ipa_validator to create reusable stage.
"""

from typing import Dict, Any, List

from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from stages.base.validation_stage import ValidationStage
from utils.logging_config import get_logger, ICONS


class IPAValidationStage(ValidationStage):
    """Validate IPA pronunciation"""
    
    def __init__(self, data_key: str = 'vocabulary', skip_failures: bool = False):
        """
        Initialize IPA validation stage
        
        Args:
            data_key: Key in context for data containing IPA
            skip_failures: Skip validation failures (just log warnings)
        """
        super().__init__(data_key)
        self.skip_failures = skip_failures
        self.logger = get_logger('stages.validation.ipa')
    
    @property
    def name(self) -> str:
        return f"validate_ipa"
    
    @property  
    def display_name(self) -> str:
        return "Validate IPA Pronunciations"
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate IPA pronunciations in data"""
        errors = []
        
        # Load IPA validator
        validator = self.get_ipa_validator()
        if not validator:
            if self.skip_failures:
                self.logger.warning(f"{ICONS['warning']} IPA validator not available, skipping validation")
                return []
            else:
                errors.append("IPA validator not available")
                return errors
        
        # Extract words and IPA from data
        word_ipa_pairs = self.extract_ipa_data(data)
        
        if not word_ipa_pairs:
            self.logger.info(f"{ICONS['info']} No IPA data found to validate")
            return []
        
        self.logger.info(f"{ICONS['search']} Validating {len(word_ipa_pairs)} IPA pronunciations...")
        
        # Validate each word/IPA pair
        validation_failures = []
        
        for word, ipa, context_info in word_ipa_pairs:
            try:
                is_valid = validator.validate_ipa(word, ipa)
                if not is_valid:
                    validation_failures.append({
                        'word': word,
                        'ipa': ipa,
                        'context': context_info
                    })
            except Exception as e:
                error_msg = f"IPA validation error for '{word}': {e}"
                if self.skip_failures:
                    self.logger.warning(f"{ICONS['warning']} {error_msg}")
                else:
                    errors.append(error_msg)
        
        # Handle validation failures
        if validation_failures:
            failure_msg = f"IPA validation failed for {len(validation_failures)} words"
            
            for failure in validation_failures:
                detail = f"  - {failure['word']} → {failure['ipa']}"
                if failure['context']:
                    detail += f" ({failure['context']})"
                
                if self.skip_failures:
                    self.logger.warning(f"{ICONS['warning']} {detail}")
                else:
                    self.logger.error(f"{ICONS['cross']} {detail}")
            
            if not self.skip_failures:
                errors.append(failure_msg)
                errors.append("Use skip_failures=True to treat IPA validation failures as warnings")
        else:
            self.logger.info(f"{ICONS['check']} All IPA pronunciations validated successfully")
        
        return errors
    
    def get_ipa_validator(self):
        """Get IPA validator instance"""
        try:
            from validation.ipa_validator import SpanishIPAValidator
            return SpanishIPAValidator()
        except ImportError:
            self.logger.warning(f"{ICONS['warning']} IPA validator module not available")
            return None
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to initialize IPA validator: {e}")
            return None
    
    def extract_ipa_data(self, data: Dict[str, Any]) -> List[tuple[str, str, str]]:
        """Extract word/IPA pairs from data structure"""
        word_ipa_pairs = []
        
        if 'words' in data:
            # Vocabulary format
            for word, word_data in data['words'].items():
                if 'meanings' in word_data:
                    for meaning in word_data['meanings']:
                        ipa = meaning.get('IPA', '').strip('[]/')
                        if ipa:
                            meaning_id = meaning.get('MeaningID', 'unknown')
                            context = f"meaning {meaning_id}"
                            word_ipa_pairs.append((word, ipa, context))
        
        elif 'meanings' in data:
            # Staging format
            for meaning in data['meanings']:
                word = meaning.get('SpanishWord', '').strip()
                ipa = meaning.get('IPA', '').strip('[]/')
                if word and ipa:
                    meaning_id = meaning.get('MeaningID', 'unknown')
                    context = f"meaning {meaning_id}"
                    word_ipa_pairs.append((word, ipa, context))
        
        elif isinstance(data, list):
            # List of cards/meanings
            for i, item in enumerate(data):
                word = item.get('SpanishWord', '').strip()
                ipa = item.get('IPA', '').strip('[]/')
                if word and ipa:
                    context = f"item {i}"
                    word_ipa_pairs.append((word, ipa, context))
        
        # Remove duplicates (same word might appear multiple times)
        seen = set()
        unique_pairs = []
        for word, ipa, context in word_ipa_pairs:
            key = (word, ipa)
            if key not in seen:
                seen.add(key)
                unique_pairs.append((word, ipa, context))
        
        return unique_pairs