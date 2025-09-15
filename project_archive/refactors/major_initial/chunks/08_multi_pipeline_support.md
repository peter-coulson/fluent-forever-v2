# Session 8: Multi-Pipeline Support

## Mission
Ensure the conjugation pipeline works correctly in the new architecture and validate that multiple pipelines can coexist without conflicts.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/07_pipeline_implementation_handoff.md` - Vocabulary pipeline context
- `tests/e2e/07_multi_pipeline/` - Validation gates for this session
- `src/utils/card_types.py` - Current conjugation implementation
- `conjugations.json` - Current conjugation data

## Objectives

### Primary Goal
Implement the conjugation pipeline using the new architecture and demonstrate that multiple pipelines can operate simultaneously without conflicts.

### Target Architecture
```
src/
├── pipelines/
│   ├── vocabulary/              # Vocabulary pipeline (already implemented)
│   ├── conjugation/             # Conjugation pipeline (implement this session)
│   │   ├── __init__.py
│   │   ├── conjugation_pipeline.py    # Main pipeline class
│   │   ├── stages/              # Conjugation-specific stages
│   │   │   ├── __init__.py
│   │   │   ├── verb_analysis.py # Verb form analysis
│   │   │   └── card_creation.py # Conjugation card creation
│   │   ├── data/                # Conjugation data handling
│   │   │   ├── __init__.py
│   │   │   └── conjugation_data.py # conjugations.json handling
│   │   └── validation/          # Conjugation-specific validation
│   │       ├── __init__.py
│   │       └── conjugation_validator.py
│   └── registry.py              # Pipeline discovery and management
```

## Implementation Requirements

### 1. Conjugation Pipeline (`src/pipelines/conjugation/conjugation_pipeline.py`)

```python
from typing import List, Dict, Any
from pathlib import Path

from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.context import PipelineContext
from stages import get_stage
from config.config_manager import get_config_manager

class ConjugationPipeline(Pipeline):
    """Spanish verb conjugation practice pipeline"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._stages_cache: Dict[str, Stage] = {}

        # Load pipeline configuration
        config_manager = get_config_manager()
        self.pipeline_config = config_manager.load_config('pipeline', 'conjugation')

    @property
    def name(self) -> str:
        return "conjugation"

    @property
    def display_name(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('display_name', 'Conjugation Practice')

    @property
    def stages(self) -> List[str]:
        """Available stages for conjugation pipeline"""
        return [
            'analyze_verbs',      # Analyze verb forms (conjugation-specific)
            'create_cards',       # Create conjugation card pairs
            'generate_media',     # Generate images (shared with vocabulary)
            'validate_data',      # Validate conjugation data
            'sync_templates',     # Sync Anki templates (shared)
            'sync_cards'         # Sync cards to Anki (shared)
        ]

    @property
    def data_file(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('data_file', 'conjugations.json')

    @property
    def anki_note_type(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('anki_note_type', 'Conjugation')

    def get_stage(self, stage_name: str) -> Stage:
        """Get stage instance by name"""
        if stage_name in self._stages_cache:
            return self._stages_cache[stage_name]

        # Create stage instance
        if stage_name == 'analyze_verbs':
            from .stages.verb_analysis import VerbAnalysisStage
            stage = VerbAnalysisStage(self.pipeline_config)
        elif stage_name == 'create_cards':
            from .stages.card_creation import ConjugationCardCreationStage
            stage = ConjugationCardCreationStage(self.pipeline_config)
        elif stage_name == 'generate_media':
            # Reuse shared media generation stage
            stage = get_stage('generate_media')
        elif stage_name == 'validate_data':
            from .validation.conjugation_validator import ConjugationDataValidationStage
            stage = ConjugationDataValidationStage(self.pipeline_config)
        elif stage_name == 'sync_templates':
            # Reuse shared template sync stage with conjugation note type
            stage = get_stage('sync_templates', note_type=self.anki_note_type)
        elif stage_name == 'sync_cards':
            # Reuse shared card sync stage with conjugation note type
            stage = get_stage('sync_cards', note_type=self.anki_note_type)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

        self._stages_cache[stage_name] = stage
        return stage

    def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:
        """Execute a specific stage"""
        if stage_name not in self.stages:
            raise ValueError(f"Stage '{stage_name}' not available in conjugation pipeline")

        stage = self.get_stage(stage_name)

        # Validate stage can run with current context
        validation_errors = stage.validate_context(context)
        if validation_errors:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Stage validation failed: {len(validation_errors)} errors",
                data={},
                errors=validation_errors
            )

        # Execute stage
        try:
            return stage.execute(context)
        except Exception as e:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Stage execution failed: {str(e)}",
                data={},
                errors=[str(e)]
            )
```

### 2. Conjugation-Specific Stages (`src/pipelines/conjugation/stages/`)

#### Verb Analysis Stage (`verb_analysis.py`)
```python
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

        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Analyzed {len(verbs)} verbs, created {len(analyzed_conjugations)} conjugation pairs",
            data={
                'conjugation_count': len(analyzed_conjugations),
                'conjugations': analyzed_conjugations
            },
            errors=[]
        )

    def _analyze_verb_conjugations(self, verb: str, context: PipelineContext) -> List[Dict[str, Any]]:
        """Analyze a verb and create conjugation pairs"""
        conjugations = []

        # Define conjugation patterns to practice
        # Based on Fluent Forever methodology for grammar cards
        patterns = [
            {'tense': 'present', 'person': 'yo', 'form': self._conjugate(verb, 'present', 'yo')},
            {'tense': 'present', 'person': 'tú', 'form': self._conjugate(verb, 'present', 'tú')},
            {'tense': 'present', 'person': 'él', 'form': self._conjugate(verb, 'present', 'él')},
            {'tense': 'preterite', 'person': 'yo', 'form': self._conjugate(verb, 'preterite', 'yo')},
            {'tense': 'preterite', 'person': 'tú', 'form': self._conjugate(verb, 'preterite', 'tú')},
        ]

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
                'RequiresMedia': True
            }

            conjugations.append(conjugation)

        return conjugations

    def _conjugate(self, verb: str, tense: str, person: str) -> str:
        """Conjugate verb for given tense and person"""
        # Simplified conjugation logic
        # In reality, this would use a comprehensive conjugation engine

        if verb == 'hablar':
            conjugations = {
                ('present', 'yo'): 'hablo',
                ('present', 'tú'): 'hablas',
                ('present', 'él'): 'habla',
                ('preterite', 'yo'): 'hablé',
                ('preterite', 'tú'): 'hablaste',
            }
            return conjugations.get((tense, person), verb)

        # Add more verbs or integrate with conjugation library
        return f"{verb}_conjugated"

    def _create_example_sentence(self, verb: str, pattern: Dict[str, Any]) -> str:
        """Create example sentence for conjugation"""
        # Create contextual sentence showing the conjugation in use
        templates = {
            ('hablar', 'present', 'yo'): 'Yo _____ español todos los días.',
            ('hablar', 'present', 'tú'): '¿Tú _____ inglés?',
            ('hablar', 'present', 'él'): 'Él _____ muy rápido.',
            ('hablar', 'preterite', 'yo'): 'Ayer yo _____ con mi madre.',
            ('hablar', 'preterite', 'tú'): '¿Tú _____ con el profesor?',
        }

        key = (verb, pattern['tense'], pattern['person'])
        return templates.get(key, f"_____ es la forma correcta.")

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
```

#### Card Creation Stage (`card_creation.py`)
```python
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext

class ConjugationCardCreationStage(Stage):
    """Create final conjugation cards from analyzed data"""

    def execute(self, context: PipelineContext) -> StageResult:
        """Create conjugation cards"""
        analyzed_conjugations = context.get('analyzed_conjugations', [])

        if not analyzed_conjugations:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No analyzed conjugations available",
                data={},
                errors=["Missing analyzed conjugations"]
            )

        created_cards = []
        for conjugation in analyzed_conjugations:
            # Process conjugation into card format
            card = self._create_card_from_conjugation(conjugation)
            created_cards.append(card)

        context.set('created_cards', created_cards)

        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Created {len(created_cards)} conjugation cards",
            data={'cards': created_cards},
            errors=[]
        )

    def _create_card_from_conjugation(self, conjugation: Dict[str, Any]) -> Dict[str, Any]:
        """Create card from conjugation data"""
        # Convert conjugation analysis into final card format
        return {
            'CardID': conjugation['CardID'],
            'Front': conjugation['Front'],
            'Back': conjugation['Back'],
            'Add Reverse': conjugation['Add Reverse'],
            'Sentence': conjugation['Sentence'],
            'Extra': conjugation['Extra'],
            'Picture': f"{conjugation['CardID']}.jpg"  # Will be generated by media stage
        }
```

### 3. Data Handling (`src/pipelines/conjugation/data/conjugation_data.py`)

```python
from typing import Dict, Any, List
from datetime import datetime

class ConjugationDataManager:
    """Manage conjugations.json data operations"""

    def __init__(self, data_provider):
        self.data_provider = data_provider

    def load_conjugations(self) -> Dict[str, Any]:
        """Load conjugation data"""
        return self.data_provider.load_data('conjugations')

    def save_conjugations(self, data: Dict[str, Any]) -> bool:
        """Save conjugation data"""
        data['metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'version': '2.0'
        }

        return self.data_provider.save_data('conjugations', data)

    def add_conjugations(self, conjugations: List[Dict[str, Any]]) -> bool:
        """Add new conjugations to data"""
        conj_data = self.load_conjugations()

        if 'conjugations' not in conj_data:
            conj_data['conjugations'] = {}

        for conjugation in conjugations:
            card_id = conjugation['CardID']
            conj_data['conjugations'][card_id] = conjugation

        return self.save_conjugations(conj_data)

    def conjugation_exists(self, card_id: str) -> bool:
        """Check if conjugation already exists"""
        conj_data = self.load_conjugations()
        return card_id in conj_data.get('conjugations', {})
```

### 4. Configuration Files

#### Conjugation Pipeline Config (`config/pipelines/conjugation.json`)
```json
{
  "pipeline": {
    "name": "conjugation",
    "display_name": "Conjugation Practice Cards",
    "data_file": "conjugations.json",
    "anki_note_type": "Conjugation",
    "stages": [
      "analyze_verbs",
      "create_cards",
      "generate_media",
      "validate_data",
      "sync_templates",
      "sync_cards"
    ]
  },
  "stage_providers": {
    "generate_media": "openai",
    "sync_templates": "anki",
    "sync_cards": "anki"
  },
  "conjugation_settings": {
    "tenses": ["present", "preterite", "imperfect", "future"],
    "persons": ["yo", "tú", "él", "nosotros", "vosotros", "ellos"],
    "max_forms_per_verb": 12,
    "include_reverse_cards": true
  },
  "validation": {
    "require_all_fields": true,
    "check_media_exists": false
  }
}
```

### 5. Multi-Pipeline Registry (`src/pipelines/registry.py`)

```python
from typing import Dict, List, Type
from core.registry import get_pipeline_registry
from core.pipeline import Pipeline

def register_all_pipelines():
    """Register all available pipelines"""
    registry = get_pipeline_registry()

    # Import and register all pipelines
    from .vocabulary.vocabulary_pipeline import VocabularyPipeline
    from .conjugation.conjugation_pipeline import ConjugationPipeline

    registry.register(VocabularyPipeline())
    registry.register(ConjugationPipeline())

def discover_pipelines() -> List[str]:
    """Discover all available pipeline names"""
    registry = get_pipeline_registry()
    return registry.list_pipelines()

def create_pipeline(name: str) -> Pipeline:
    """Create pipeline instance by name"""
    registry = get_pipeline_registry()
    return registry.get(name)

# Auto-register all pipelines when module is imported
register_all_pipelines()
```

### 6. Multi-Pipeline CLI Integration

Update CLI to handle multiple pipelines seamlessly:

```python
# In cli/commands/run_command.py - enhance existing implementation

def execute(self, args) -> int:
    """Execute run command with multi-pipeline support"""
    try:
        pipeline = self.pipeline_registry.get(args.pipeline)
    except Exception as e:
        # Provide helpful error with available pipelines
        available = self.pipeline_registry.list_pipelines()
        print(f"Error: Pipeline '{args.pipeline}' not found")
        print(f"Available pipelines: {', '.join(available)}")
        return 1

    # Create pipeline-specific context
    context = self._create_pipeline_context(args, pipeline)

    # Execute with pipeline-specific providers
    return self._execute_pipeline_stage(pipeline, args.stage, context)

def _create_pipeline_context(self, args, pipeline: Pipeline) -> PipelineContext:
    """Create context specific to pipeline type"""
    context = PipelineContext(
        pipeline_name=pipeline.name,
        project_root=self.project_root,
        config=self.config.to_dict(),
        args=vars(args)
    )

    # Add pipeline-specific providers
    providers = self._get_pipeline_providers(pipeline)
    context.set('providers', providers)

    # Add pipeline-specific data parsing
    if pipeline.name == 'vocabulary':
        self._populate_vocabulary_context(context, args)
    elif pipeline.name == 'conjugation':
        self._populate_conjugation_context(context, args)

    return context

def _populate_conjugation_context(self, context: PipelineContext, args) -> None:
    """Add conjugation-specific context data"""
    if args.words:  # Treat words as verbs for conjugation
        context.set('verbs', [w.strip() for w in args.words.split(',')])
    if hasattr(args, 'verbs') and args.verbs:
        context.set('verbs', [v.strip() for v in args.verbs.split(',')])
```

### 7. Conflict Prevention

Ensure pipelines don't interfere with each other:

#### Template Isolation (`src/sync/templates_sync.py`)
```python
def load_local_templates(template_dir: Path, pipeline_name: str = None) -> Tuple[List[Dict], str]:
    """Load templates with pipeline isolation"""
    # Existing logic but add pipeline-specific validation

    manifest_path = template_dir / 'manifest.json'
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest.json found in {template_dir}")

    manifest = json.loads(manifest_path.read_text())

    # Validate pipeline isolation
    if pipeline_name:
        expected_note_type = get_expected_note_type(pipeline_name)
        actual_note_type = manifest.get('note_type')

        if actual_note_type != expected_note_type:
            raise ValueError(f"Note type mismatch: expected '{expected_note_type}' for {pipeline_name}, got '{actual_note_type}'")

    # Continue with existing template loading...
```

#### Media Isolation
```python
# Ensure media files don't conflict between pipelines
def generate_media_path(card_id: str, pipeline_name: str, media_type: str) -> Path:
    """Generate pipeline-isolated media paths"""
    return Path(f"media/{pipeline_name}/{media_type}/{card_id}.{get_extension(media_type)}")
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/07_multi_pipeline/` pass
- [ ] Multiple pipelines can coexist without conflicts
- [ ] Pipeline isolation works correctly
- [ ] Shared resources work across pipelines

### Implementation Quality
- [ ] Conjugation pipeline fully functional
- [ ] Stages reused appropriately between pipelines
- [ ] Configuration system supports multiple pipelines
- [ ] CLI works seamlessly with multiple pipelines

### Conflict Prevention
- [ ] Templates don't conflict between pipelines
- [ ] Media files are properly isolated
- [ ] Data files remain separate
- [ ] Anki note types don't interfere

## Deliverables

### 1. Complete Conjugation Pipeline
- Full conjugation pipeline implementation
- All conjugation-specific stages
- Data handling and validation
- Configuration integration

### 2. Multi-Pipeline Support
- Registry system for multiple pipelines
- CLI integration for all pipelines
- Resource isolation between pipelines
- Shared resource management

### 3. Conflict Prevention
- Template isolation mechanisms
- Media path segregation
- Data file separation
- Provider isolation

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/08_multi_pipeline_support_handoff.md` with:
- Overview of multi-pipeline architecture
- How conjugation pipeline was implemented
- Resource isolation strategies
- CLI multi-pipeline patterns
- Guidance for documentation organization session

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 8 E2E tests pass
3. ✅ Vocabulary and conjugation pipelines work independently
4. ✅ Shared resources work correctly across pipelines
5. ✅ No conflicts between pipeline operations

### Quality Validation
- Multiple pipelines can be used simultaneously
- Resource sharing works without conflicts
- CLI provides consistent experience across pipelines
- Adding new pipelines doesn't affect existing ones

## Notes for Implementation

### Resource Sharing Strategy
- Stages are shared where appropriate (media generation, sync)
- Providers are shared but configured per pipeline
- Templates and data remain isolated
- CLI commands work uniformly

### Design Principles
- **Isolation** - Pipelines don't interfere with each other
- **Sharing** - Common functionality is reused
- **Consistency** - Same patterns across all pipelines
- **Extensibility** - Easy to add more pipelines

---

**Remember: This session proves that the architecture truly supports multiple card types. Focus on demonstrating clean coexistence and resource sharing.**
