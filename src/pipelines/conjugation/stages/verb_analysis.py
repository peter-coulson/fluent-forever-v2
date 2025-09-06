"""Analyze verb conjugations and create practice pairs."""

from typing import List, Dict, Any
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext


class VerbAnalysisStage(Stage):
    """Analyze verb conjugations and create practice pairs"""
    
    def __init__(self, pipeline_config: Dict[str, Any]):
        self.config = pipeline_config
    
    @property
    def name(self) -> str:
        return "analyze_verbs"
    
    @property
    def display_name(self) -> str:
        return "Analyze Verb Conjugations"
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context has required data"""
        errors = []
        
        verbs = context.get('verbs')
        if not verbs:
            errors.append("No verbs provided for analysis (missing 'verbs' in context)")
        elif not isinstance(verbs, list):
            errors.append("Verbs must be provided as a list")
        
        return errors
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Execute verb analysis"""
        verbs = context.get('verbs', [])
        
        analyzed_conjugations = []
        
        for verb in verbs:
            try:
                conjugations = self._analyze_verb_conjugations(verb, context)
                analyzed_conjugations.extend(conjugations)
            except Exception as e:
                context.add_error(f"Error analyzing verb '{verb}': {e}")
        
        context.set('analyzed_conjugations', analyzed_conjugations)
        
        return StageResult.success(
            f"Analyzed {len(verbs)} verbs, created {len(analyzed_conjugations)} conjugation pairs",
            {
                'conjugation_count': len(analyzed_conjugations),
                'conjugations': analyzed_conjugations
            }
        )
    
    def _analyze_verb_conjugations(self, verb: str, context: PipelineContext) -> List[Dict[str, Any]]:
        """Analyze a verb and create conjugation pairs"""
        conjugations = []
        
        # Get configuration settings
        conjugation_settings = self.config.get('conjugation_settings', {})
        tenses = conjugation_settings.get('tenses', ['present', 'preterite'])
        persons = conjugation_settings.get('persons', ['yo', 'tú', 'él'])
        max_forms = conjugation_settings.get('max_forms_per_verb', 6)
        
        # Define conjugation patterns to practice
        # Based on Fluent Forever methodology for grammar cards
        patterns = []
        count = 0
        
        for tense in tenses:
            for person in persons:
                if count >= max_forms:
                    break
                    
                conjugated_form = self._conjugate(verb, tense, person)
                if conjugated_form != verb:  # Only add if conjugation was successful
                    patterns.append({
                        'tense': tense,
                        'person': person, 
                        'form': conjugated_form
                    })
                    count += 1
            if count >= max_forms:
                break
        
        for pattern in patterns:
            # Create card pair for this conjugation
            card_id = f"{verb}_{pattern['tense']}_{pattern['person']}"
            
            conjugation = {
                'CardID': card_id,
                'InfinitiveVerb': verb,
                'ConjugatedForm': pattern['form'],
                'Tense': pattern['tense'],
                'Person': pattern['person'],
                'Front': pattern['form'],  # Show conjugated form
                'Back': verb,              # Reveal infinitive
                'Add Reverse': '1',        # Create reverse card
                'Sentence': self._create_example_sentence(verb, pattern),
                'Extra': f"{pattern['tense'].title()} tense, {pattern['person']} ({self._get_english_translation(pattern)})",
                'RequiresMedia': True,
                'Picture': ''  # Will be generated later
            }
            
            conjugations.append(conjugation)
        
        return conjugations
    
    def _conjugate(self, verb: str, tense: str, person: str) -> str:
        """Conjugate verb for given tense and person"""
        # Comprehensive conjugation logic for common verbs
        # In a production system, this would use a full conjugation engine
        
        conjugations = {
            # hablar (to speak/talk)
            'hablar': {
                ('present', 'yo'): 'hablo',
                ('present', 'tú'): 'hablas', 
                ('present', 'él'): 'habla',
                ('present', 'nosotros'): 'hablamos',
                ('present', 'vosotros'): 'habláis',
                ('present', 'ellos'): 'hablan',
                ('preterite', 'yo'): 'hablé',
                ('preterite', 'tú'): 'hablaste',
                ('preterite', 'él'): 'habló',
                ('preterite', 'nosotros'): 'hablamos',
                ('preterite', 'vosotros'): 'hablasteis',
                ('preterite', 'ellos'): 'hablaron',
                ('imperfect', 'yo'): 'hablaba',
                ('imperfect', 'tú'): 'hablabas',
                ('imperfect', 'él'): 'hablaba',
                ('future', 'yo'): 'hablaré',
                ('future', 'tú'): 'hablarás',
                ('future', 'él'): 'hablará',
            },
            # comer (to eat)
            'comer': {
                ('present', 'yo'): 'como',
                ('present', 'tú'): 'comes',
                ('present', 'él'): 'come',
                ('preterite', 'yo'): 'comí',
                ('preterite', 'tú'): 'comiste', 
                ('preterite', 'él'): 'comió',
                ('imperfect', 'yo'): 'comía',
                ('future', 'yo'): 'comeré',
            },
            # vivir (to live)
            'vivir': {
                ('present', 'yo'): 'vivo',
                ('present', 'tú'): 'vives',
                ('present', 'él'): 'vive',
                ('present', 'nosotros'): 'vivimos',
                ('preterite', 'yo'): 'viví',
                ('preterite', 'él'): 'vivió',
                ('future', 'nosotros'): 'viviremos',
            },
            # ser (to be)
            'ser': {
                ('present', 'yo'): 'soy',
                ('present', 'tú'): 'eres',
                ('present', 'él'): 'es',
                ('preterite', 'yo'): 'fui',
                ('preterite', 'tú'): 'fuiste',
                ('preterite', 'él'): 'fue',
                ('imperfect', 'yo'): 'era',
                ('imperfect', 'tú'): 'eras',
                ('imperfect', 'él'): 'era',
            }
        }
        
        # Return conjugated form if available, otherwise return the infinitive
        return conjugations.get(verb, {}).get((tense, person), verb)
    
    def _create_example_sentence(self, verb: str, pattern: Dict[str, Any]) -> str:
        """Create example sentence for conjugation"""
        # Create contextual sentence showing the conjugation in use
        templates = {
            ('hablar', 'present', 'yo'): 'Yo _____ español todos los días.',
            ('hablar', 'present', 'tú'): '¿Tú _____ inglés?',
            ('hablar', 'present', 'él'): 'Él _____ muy rápido.',
            ('hablar', 'preterite', 'yo'): 'Ayer yo _____ con mi madre.',
            ('hablar', 'preterite', 'tú'): '¿Tú _____ con el profesor?',
            ('comer', 'present', 'yo'): 'Yo _____ mucha fruta.',
            ('comer', 'preterite', 'él'): 'Él _____ una manzana ayer.',
            ('vivir', 'present', 'yo'): 'Yo _____ en Madrid.',
            ('vivir', 'future', 'nosotros'): 'Nosotros _____ en España el próximo año.',
            ('ser', 'present', 'yo'): 'Yo _____ estudiante.',
            ('ser', 'imperfect', 'él'): 'Ella _____ muy inteligente cuando era niña.',
        }
        
        key = (verb, pattern['tense'], pattern['person'])
        template = templates.get(key)
        
        # If no specific template, create a generic one
        if not template:
            person_pronouns = {
                'yo': 'Yo',
                'tú': 'Tú', 
                'él': 'Él/Ella',
                'nosotros': 'Nosotros',
                'vosotros': 'Vosotros',
                'ellos': 'Ellos'
            }
            pronoun = person_pronouns.get(pattern['person'], pattern['person'])
            template = f"{pronoun} _____ (conjugate {verb})."
        
        return template
    
    def _get_english_translation(self, pattern: Dict[str, Any]) -> str:
        """Get English translation for person"""
        translations = {
            'yo': 'I',
            'tú': 'you (informal)',
            'él': 'he/she',
            'nosotros': 'we',
            'vosotros': 'you all (informal)',
            'ellos': 'they'
        }
        return translations.get(pattern['person'], pattern['person'])