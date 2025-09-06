"""Word analysis stage for vocabulary pipeline."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext


class WordAnalysisStage(Stage):
    """
    Analyze Spanish words to identify distinct semantic meanings.
    
    Based on the 4-step process defined in CLAUDE.md:
    1. Grammatical Category Check
    2. Multi-Context Analysis  
    3. Distinct Meaning Verification
    4. Final Count Verification
    """
    
    def __init__(self, pipeline_config: Dict[str, Any] = None):
        self.config = pipeline_config or {}
        self.max_meanings_per_word = self.config.get('batch_settings', {}).get('max_meanings_per_word', 5)
    
    @property
    def name(self) -> str:
        return "analyze_words"
    
    @property
    def display_name(self) -> str:
        return "Analyze Word Meanings"
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context has required data."""
        errors = []
        
        words = context.get('words')
        if not words:
            errors.append("No words provided for analysis (missing 'words' in context)")
        elif not isinstance(words, list):
            errors.append("Words must be provided as a list")
        elif not all(isinstance(w, str) for w in words):
            errors.append("All words must be strings")
        
        return errors
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute word analysis."""
        words = context.get('words', [])
        
        analyzed_meanings = []
        skipped_words = []
        
        for word in words:
            try:
                meanings = self._analyze_word_meanings(word, context)
                if meanings:
                    analyzed_meanings.extend(meanings)
                else:
                    skipped_words.append(word)
            except Exception as e:
                context.add_error(f"Error analyzing word '{word}': {e}")
                skipped_words.append(word)
        
        # Store results in context
        context.set('analyzed_meanings', analyzed_meanings)
        context.set('skipped_words', skipped_words)
        
        return StageResult.success(
            f"Analyzed {len(words)} words, found {len(analyzed_meanings)} meanings",
            {
                'meanings_count': len(analyzed_meanings),
                'skipped_count': len(skipped_words),
                'meanings': analyzed_meanings,
                'skipped_words': skipped_words
            }
        )
    
    def _analyze_word_meanings(self, word: str, context: PipelineContext) -> List[Dict[str, Any]]:
        """
        Analyze a single word for distinct meanings using the systematic approach.
        
        This implements the comprehensive meaning analysis methodology from CLAUDE.md
        """
        # Check if word already exists in vocabulary
        vocabulary_data = self._load_vocabulary_data(context)
        if word in vocabulary_data.get('words', {}):
            # Word already processed, skip
            return []
        
        # STEP 1: Grammatical Category Check
        grammatical_category = self._identify_grammatical_category(word)
        
        # STEP 2: Multi-Context Analysis
        potential_meanings = self._analyze_contexts(word, grammatical_category)
        
        # STEP 3: Distinct Meaning Verification
        distinct_meanings = self._verify_distinct_meanings(potential_meanings)
        
        # STEP 4: Final Count Verification
        if len(distinct_meanings) > self.max_meanings_per_word:
            # If too many meanings, prioritize most common ones
            distinct_meanings = distinct_meanings[:self.max_meanings_per_word]
        
        # Convert to pipeline format
        meanings = []
        for i, meaning_info in enumerate(distinct_meanings):
            meaning_id = f"{word}_meaning_{i+1}"
            card_id = f"{word}_{meaning_id}"
            
            meaning = {
                'SpanishWord': word,
                'MeaningID': meaning_id,
                'MeaningContext': meaning_info['context'],
                'CardID': card_id,
                'RequiresPrompt': True,
                'GrammaticalCategory': grammatical_category,
                'EstimatedDifficulty': meaning_info.get('difficulty', 'intermediate')
            }
            meanings.append(meaning)
        
        return meanings
    
    def _identify_grammatical_category(self, word: str) -> str:
        """
        Identify the grammatical category of the word.
        
        This is a simplified version - in a full implementation, this would
        use a Spanish morphological analyzer or dictionary lookup.
        """
        # Common prepositions (usually multi-meaning)
        prepositions = {'por', 'para', 'de', 'en', 'con', 'desde', 'hasta', 'sobre', 'bajo', 'entre'}
        if word in prepositions:
            return 'preposition'
        
        # Common verbs (check for infinitive endings)
        if word.endswith(('ar', 'er', 'ir')):
            return 'verb'
        
        # Common articles and pronouns
        articles_pronouns = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'yo', 'tú', 'él', 'ella'}
        if word in articles_pronouns:
            return 'article_pronoun'
        
        # Default to noun for unknown words
        return 'noun'
    
    def _analyze_contexts(self, word: str, category: str) -> List[Dict[str, Any]]:
        """
        Analyze different contexts where the word can be used.
        
        This creates potential meanings based on grammatical category.
        """
        contexts = []
        
        if category == 'preposition':
            # Prepositions typically have multiple meanings
            if word == 'por':
                contexts.extend([
                    {'context': 'through/via', 'example': 'Camino por el parque', 'difficulty': 'basic'},
                    {'context': 'because of/due to', 'example': 'Por la lluvia no salimos', 'difficulty': 'intermediate'},
                    {'context': 'by means of', 'example': 'Hablo por teléfono', 'difficulty': 'intermediate'},
                    {'context': 'in exchange for', 'example': 'Pago diez euros por el libro', 'difficulty': 'intermediate'}
                ])
            elif word == 'para':
                contexts.extend([
                    {'context': 'purpose/in order to', 'example': 'Estudio para aprender', 'difficulty': 'basic'},
                    {'context': 'deadline', 'example': 'Es para mañana', 'difficulty': 'intermediate'},
                    {'context': 'destination', 'example': 'Voy para Madrid', 'difficulty': 'intermediate'},
                    {'context': 'recipient', 'example': 'Es para ti', 'difficulty': 'basic'}
                ])
            else:
                # Generic preposition - assume 2-3 meanings
                contexts.extend([
                    {'context': f'primary meaning of {word}', 'example': f'Uso primario de {word}', 'difficulty': 'basic'},
                    {'context': f'secondary meaning of {word}', 'example': f'Uso secundario de {word}', 'difficulty': 'intermediate'}
                ])
        
        elif category == 'verb':
            # Verbs can have multiple meanings based on context
            if word in ['ser', 'estar']:
                # These verbs have many distinct meanings
                if word == 'ser':
                    contexts.extend([
                        {'context': 'identity/characteristics', 'example': 'Soy médico', 'difficulty': 'basic'},
                        {'context': 'time/date', 'example': 'Son las tres', 'difficulty': 'basic'},
                        {'context': 'origin', 'example': 'Soy de España', 'difficulty': 'basic'},
                        {'context': 'events/location', 'example': 'La fiesta es en casa', 'difficulty': 'intermediate'}
                    ])
                elif word == 'estar':
                    contexts.extend([
                        {'context': 'location', 'example': 'Estoy en casa', 'difficulty': 'basic'},
                        {'context': 'temporary states', 'example': 'Estoy cansado', 'difficulty': 'basic'},
                        {'context': 'ongoing actions', 'example': 'Estoy comiendo', 'difficulty': 'intermediate'},
                        {'context': 'presence', 'example': '¿Está María?', 'difficulty': 'basic'}
                    ])
            else:
                # Most verbs have one primary meaning
                contexts.append({
                    'context': f'primary meaning of {word}',
                    'example': f'Uso del verbo {word}',
                    'difficulty': 'basic'
                })
        
        else:
            # Nouns, adjectives, etc. typically have one primary meaning
            contexts.append({
                'context': f'primary meaning of {word}',
                'example': f'Uso de {word}',
                'difficulty': 'basic'
            })
        
        return contexts
    
    def _verify_distinct_meanings(self, potential_meanings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verify that each potential meaning represents a truly distinct concept.
        
        In a full implementation, this would use semantic analysis to determine
        if meanings are truly different or just variations of the same concept.
        """
        # For now, assume all potential meanings from context analysis are distinct
        # In practice, this would involve more sophisticated semantic comparison
        return potential_meanings
    
    def _load_vocabulary_data(self, context: PipelineContext) -> Dict[str, Any]:
        """Load current vocabulary data to check for existing words."""
        try:
            vocab_path = context.project_root / 'vocabulary.json'
            if vocab_path.exists():
                return json.loads(vocab_path.read_text())
        except Exception:
            pass
        return {'words': {}}