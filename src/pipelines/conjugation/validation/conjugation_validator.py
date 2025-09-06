"""Validation stages for conjugation pipeline data."""

from typing import List, Dict, Any
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from ..data.conjugation_data import ConjugationDataManager


class ConjugationDataValidationStage(Stage):
    """Validate conjugation card data integrity"""
    
    def __init__(self, pipeline_config: Dict[str, Any]):
        self.config = pipeline_config
        self.validation_config = pipeline_config.get('validation', {})
    
    @property
    def name(self) -> str:
        return "validate_data"
    
    @property
    def display_name(self) -> str:
        return "Validate Conjugation Data"
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context has required data"""
        errors = []
        
        # Check for cards to validate
        cards = context.get('cards') or context.get('created_cards')
        if not cards:
            errors.append("No cards provided for validation")
        
        return errors
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute conjugation data validation"""
        cards = context.get('cards') or context.get('created_cards', [])
        
        if not cards:
            return StageResult.failure(
                "No cards available for validation",
                ["Missing cards in context"]
            )
        
        validation_errors = []
        validation_warnings = []
        valid_cards = []
        
        for card in cards:
            card_errors, card_warnings = self._validate_card(card)
            
            if card_errors:
                validation_errors.extend([
                    f"Card {card.get('CardID', 'unknown')}: {error}"
                    for error in card_errors
                ])
            else:
                valid_cards.append(card)
            
            if card_warnings:
                validation_warnings.extend([
                    f"Card {card.get('CardID', 'unknown')}: {warning}"
                    for warning in card_warnings
                ])
        
        # Update context with valid cards
        context.set('validated_cards', valid_cards)
        
        # Determine result status
        if validation_errors:
            if valid_cards:
                # Some cards are valid
                return StageResult.partial(
                    f"Validation completed with errors. {len(valid_cards)}/{len(cards)} cards valid",
                    {'valid_cards': valid_cards, 'warnings': validation_warnings},
                    validation_errors
                )
            else:
                # No valid cards
                return StageResult.failure(
                    "All cards failed validation",
                    validation_errors
                )
        else:
            # All cards valid
            message = f"Validation successful. All {len(cards)} cards are valid"
            if validation_warnings:
                message += f" (with {len(validation_warnings)} warnings)"
            
            return StageResult.success(
                message,
                {'valid_cards': valid_cards, 'warnings': validation_warnings}
            )
    
    def _validate_card(self, card: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate a single conjugation card"""
        errors = []
        warnings = []
        
        # Required fields validation
        if self.validation_config.get('require_all_fields', True):
            required_fields = [
                'CardID', 'Front', 'Back', 'Sentence', 'Extra',
                'InfinitiveVerb', 'ConjugatedForm', 'Tense', 'Person'
            ]
            
            for field in required_fields:
                if not card.get(field):
                    errors.append(f"Missing required field: {field}")
        
        # CardID format validation
        card_id = card.get('CardID', '')
        if card_id:
            # Should follow pattern: verb_tense_person
            parts = card_id.split('_')
            if len(parts) < 3:
                warnings.append(f"CardID '{card_id}' doesn't follow expected pattern 'verb_tense_person'")
        
        # Conjugation logic validation
        infinitive = card.get('InfinitiveVerb', '')
        conjugated = card.get('ConjugatedForm', '')
        tense = card.get('Tense', '')
        person = card.get('Person', '')
        
        if infinitive and conjugated:
            # Basic sanity checks
            if infinitive == conjugated:
                warnings.append(f"Conjugated form '{conjugated}' is same as infinitive '{infinitive}'")
            
            if not infinitive.endswith(('ar', 'er', 'ir')):
                warnings.append(f"Infinitive '{infinitive}' doesn't end with ar/er/ir")
        
        # Tense validation
        valid_tenses = ['present', 'preterite', 'imperfect', 'future', 'conditional', 'subjunctive']
        if tense and tense not in valid_tenses:
            warnings.append(f"Unusual tense '{tense}', expected one of: {valid_tenses}")
        
        # Person validation
        valid_persons = ['yo', 'tú', 'él', 'nosotros', 'vosotros', 'ellos']
        if person and person not in valid_persons:
            warnings.append(f"Unusual person '{person}', expected one of: {valid_persons}")
        
        # Front/Back consistency
        front = card.get('Front', '')
        back = card.get('Back', '')
        if front and back and conjugated and infinitive:
            if front != conjugated:
                warnings.append(f"Front '{front}' doesn't match ConjugatedForm '{conjugated}'")
            if back != infinitive:
                warnings.append(f"Back '{back}' doesn't match InfinitiveVerb '{infinitive}'")
        
        # Sentence validation
        sentence = card.get('Sentence', '')
        if sentence:
            if '_____' not in sentence:
                warnings.append("Sentence doesn't contain blank '_____ for practice")
            
            # Check if sentence contains the conjugated form (potential spoiler)
            if conjugated and conjugated.lower() in sentence.lower():
                warnings.append(f"Sentence contains conjugated form '{conjugated}' which spoils the answer")
        
        # Media validation (optional)
        if self.validation_config.get('check_media_exists', False):
            picture = card.get('Picture', '')
            if picture:
                # Would check if image file exists - placeholder for now
                if not picture.endswith(('.jpg', '.png', '.gif')):
                    warnings.append(f"Picture '{picture}' doesn't have standard image extension")
        
        return errors, warnings
    
    def _validate_conjugation_data_file(self, context: PipelineContext) -> tuple[List[str], List[str]]:
        """Validate the conjugations.json data file integrity"""
        errors = []
        warnings = []
        
        try:
            data_manager = ConjugationDataManager(project_root=context.project_root)
            conj_data = data_manager.load_conjugations()
            
            # Check basic structure
            if 'conjugations' not in conj_data:
                errors.append("Missing 'conjugations' key in data file")
                return errors, warnings
            
            # Check metadata
            if 'metadata' not in conj_data:
                warnings.append("Missing metadata in conjugation data file")
            
            # Check for duplicate CardIDs
            card_ids = list(conj_data['conjugations'].keys())
            duplicate_ids = [card_id for card_id in set(card_ids) if card_ids.count(card_id) > 1]
            if duplicate_ids:
                errors.append(f"Duplicate CardIDs found: {duplicate_ids}")
            
            # Get statistics
            stats = data_manager.get_stats()
            if stats['total_cards'] == 0:
                warnings.append("No conjugation cards found in data file")
            
        except Exception as e:
            errors.append(f"Failed to validate conjugation data file: {e}")
        
        return errors, warnings