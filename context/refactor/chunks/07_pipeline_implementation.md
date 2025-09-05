# Session 7: Pipeline Implementation

## Mission
Implement the vocabulary pipeline using the new architecture, ensuring all existing functionality is preserved while demonstrating the new modular system.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/06_configuration_refactor_handoff.md` - Configuration system context
- `tests/e2e/06_vocabulary_pipeline/` - Validation gates for this session
- `src/core/`, `src/stages/`, `src/providers/` - Previous implementations
- Current vocabulary processing logic to migrate

## Objectives

### Primary Goal
Create a complete vocabulary pipeline implementation that demonstrates the new architecture while preserving all existing functionality.

### Target Architecture
```
src/
├── pipelines/
│   ├── __init__.py
│   ├── vocabulary/              # Vocabulary pipeline implementation
│   │   ├── __init__.py
│   │   ├── vocabulary_pipeline.py    # Main pipeline class
│   │   ├── stages/              # Vocabulary-specific stages
│   │   │   ├── __init__.py
│   │   │   ├── word_analysis.py # Word meaning analysis
│   │   │   ├── batch_creation.py # Claude batch creation
│   │   │   └── sentence_generation.py # Contextual sentences
│   │   ├── data/                # Data handling
│   │   │   ├── __init__.py
│   │   │   ├── vocabulary_data.py # Vocabulary.json handling  
│   │   │   └── word_queue.py    # Word queue management
│   │   └── validation/          # Vocabulary-specific validation
│   │       ├── __init__.py
│   │       ├── meaning_validator.py # Meaning validation
│   │       └── ipa_validator.py     # IPA validation
│   └── __template/              # Template for new pipelines
│       ├── __init__.py
│       ├── template_pipeline.py
│       ├── stages/
│       ├── data/
│       └── validation/
```

## Implementation Requirements

### 1. Main Pipeline Implementation (`src/pipelines/vocabulary/vocabulary_pipeline.py`)

```python
from typing import List, Dict, Any
from pathlib import Path

from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.context import PipelineContext
from stages import get_stage
from config.config_manager import get_config_manager

class VocabularyPipeline(Pipeline):
    """Fluent Forever vocabulary card pipeline"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._stages_cache: Dict[str, Stage] = {}
        
        # Load pipeline configuration
        config_manager = get_config_manager()
        self.pipeline_config = config_manager.load_config('pipeline', 'vocabulary')
    
    @property
    def name(self) -> str:
        return "vocabulary"
    
    @property
    def display_name(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('display_name', 'Vocabulary Cards')
    
    @property
    def stages(self) -> List[str]:
        """Available stages for vocabulary pipeline"""
        return [
            'analyze_words',      # Analyze word meanings (vocabulary-specific)
            'prepare_batch',      # Create Claude staging batch
            'ingest_batch',       # Ingest completed Claude batch
            'generate_media',     # Generate images and audio
            'validate_data',      # Validate card data
            'validate_ipa',       # Validate IPA pronunciation
            'sync_templates',     # Sync Anki templates
            'sync_cards'         # Sync cards to Anki
        ]
    
    @property
    def data_file(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('data_file', 'vocabulary.json')
    
    @property 
    def anki_note_type(self) -> str:
        return self.pipeline_config.get('pipeline', {}).get('anki_note_type', 'Fluent Forever')
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get stage instance by name"""
        if stage_name in self._stages_cache:
            return self._stages_cache[stage_name]
        
        # Create stage instance
        if stage_name == 'analyze_words':
            from .stages.word_analysis import VocabularyWordAnalysisStage
            stage = VocabularyWordAnalysisStage(self.pipeline_config)
        elif stage_name == 'prepare_batch':
            stage = get_stage('prepare_batch', pipeline_config=self.pipeline_config)
        elif stage_name == 'ingest_batch':
            stage = get_stage('ingest_batch', pipeline_config=self.pipeline_config)
        elif stage_name == 'generate_media':
            stage = get_stage('generate_media')
        elif stage_name == 'validate_data':
            from .validation.meaning_validator import VocabularyDataValidationStage
            stage = VocabularyDataValidationStage(self.pipeline_config)
        elif stage_name == 'validate_ipa':
            stage = get_stage('validate_ipa')
        elif stage_name == 'sync_templates':
            stage = get_stage('sync_templates', note_type=self.anki_note_type)
        elif stage_name == 'sync_cards':
            stage = get_stage('sync_cards', note_type=self.anki_note_type)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        self._stages_cache[stage_name] = stage
        return stage
    
    def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:
        """Execute a specific stage"""
        if stage_name not in self.stages:
            raise ValueError(f"Stage '{stage_name}' not available in vocabulary pipeline")
        
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

### 2. Vocabulary-Specific Stages (`src/pipelines/vocabulary/stages/`)

#### Word Analysis Stage (`word_analysis.py`)
```python
from typing import List, Dict, Any
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext

class VocabularyWordAnalysisStage(Stage):
    """Analyze Spanish words and identify distinct meanings"""
    
    def __init__(self, pipeline_config: Dict[str, Any]):
        self.config = pipeline_config
        self.max_meanings_per_word = self.config.get('batch_settings', {}).get('max_meanings_per_word', 5)
    
    @property
    def name(self) -> str:
        return "analyze_words"
    
    @property
    def display_name(self) -> str:
        return "Analyze Word Meanings"
    
    def validate_context(self, context: PipelineContext) -> List[str]:
        """Validate context has required data"""
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
        """Execute word analysis"""
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
        
        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Analyzed {len(words)} words, found {len(analyzed_meanings)} meanings",
            data={
                'meanings_count': len(analyzed_meanings),
                'skipped_count': len(skipped_words),
                'meanings': analyzed_meanings
            },
            errors=[]
        )
    
    def _analyze_word_meanings(self, word: str, context: PipelineContext) -> List[Dict[str, Any]]:
        """Analyze a single word for distinct meanings"""
        # Extract the existing word analysis logic from:
        # - Current vocabulary system
        # - Claude operational guidelines
        # - Meaning identification patterns
        
        # This is where the sophisticated meaning analysis happens
        # Based on the 4-step process defined in CLAUDE.md:
        # 1. Grammatical Category Check
        # 2. Multi-Context Analysis  
        # 3. Distinct Meaning Verification
        # 4. Final Count Verification
        
        meanings = []
        
        # Check if word already exists in vocabulary
        vocabulary_data = self._load_vocabulary_data(context)
        if word in vocabulary_data.get('words', {}):
            # Word already processed, skip
            return []
        
        # Perform meaning analysis (implement the systematic analysis from CLAUDE.md)
        # This would include:
        # - Grammatical category identification
        # - Context analysis
        # - Meaning distinction
        # - Example generation
        
        # For now, return placeholder structure
        meaning_id = f"{word}_meaning_1"
        meaning = {
            'SpanishWord': word,
            'MeaningID': meaning_id,
            'MeaningContext': f"Primary meaning of {word}",
            'CardID': f"{word}_{meaning_id}",
            'RequiresPrompt': True
        }
        meanings.append(meaning)
        
        return meanings
    
    def _load_vocabulary_data(self, context: PipelineContext) -> Dict[str, Any]:
        """Load current vocabulary data"""
        data_provider = context.get('providers', {}).get('data')
        if data_provider:
            return data_provider.load_data('vocabulary')
        return {}
```

#### Batch Creation Stage (`batch_creation.py`)
```python
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext

class VocabularyBatchCreationStage(Stage):
    """Create Claude staging batch for vocabulary meanings"""
    
    def execute(self, context: PipelineContext) -> StageResult:
        """Create staging batch from analyzed meanings"""
        analyzed_meanings = context.get('analyzed_meanings', [])
        
        if not analyzed_meanings:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No analyzed meanings available for batch creation",
                data={},
                errors=["Missing analyzed meanings"]
            )
        
        # Create staging batch structure
        # Extract logic from cli/prepare_claude_batch.py
        
        batch_data = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'meanings': []
        }
        
        for meaning in analyzed_meanings:
            batch_meaning = {
                'SpanishWord': meaning['SpanishWord'],
                'MeaningID': meaning['MeaningID'], 
                'MeaningContext': meaning['MeaningContext'],
                'CardID': meaning['CardID'],
                # Fields for Claude to fill
                'MonolingualDef': '',
                'ExampleSentence': '',
                'GappedSentence': '',
                'IPA': '',
                'prompt': ''
            }
            batch_data['meanings'].append(batch_meaning)
        
        # Save to staging directory
        staging_file = self._save_batch_file(batch_data, context)
        
        context.set('batch_file', staging_file)
        context.set('batch_data', batch_data)
        
        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Created batch with {len(batch_data['meanings'])} meanings",
            data={'batch_file': str(staging_file), 'meaning_count': len(batch_data['meanings'])},
            errors=[]
        )
```

### 3. Data Handling (`src/pipelines/vocabulary/data/`)

#### Vocabulary Data Manager (`vocabulary_data.py`)
```python
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

class VocabularyDataManager:
    """Manage vocabulary.json data operations"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def load_vocabulary(self) -> Dict[str, Any]:
        """Load vocabulary data"""
        return self.data_provider.load_data('vocabulary')
    
    def save_vocabulary(self, data: Dict[str, Any]) -> bool:
        """Save vocabulary data"""
        # Add metadata
        data['metadata'] = {
            'last_updated': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        return self.data_provider.save_data('vocabulary', data)
    
    def add_meanings(self, meanings: List[Dict[str, Any]]) -> bool:
        """Add new meanings to vocabulary"""
        vocab_data = self.load_vocabulary()
        
        if 'words' not in vocab_data:
            vocab_data['words'] = {}
        
        for meaning in meanings:
            spanish_word = meaning['SpanishWord']
            
            if spanish_word not in vocab_data['words']:
                vocab_data['words'][spanish_word] = {
                    'meanings': [],
                    'created': datetime.now().isoformat()
                }
            
            vocab_data['words'][spanish_word]['meanings'].append(meaning)
        
        return self.save_vocabulary(vocab_data)
    
    def get_word_meanings(self, word: str) -> List[Dict[str, Any]]:
        """Get all meanings for a word"""
        vocab_data = self.load_vocabulary()
        word_data = vocab_data.get('words', {}).get(word, {})
        return word_data.get('meanings', [])
    
    def card_exists(self, card_id: str) -> bool:
        """Check if card already exists"""
        vocab_data = self.load_vocabulary()
        
        for word_data in vocab_data.get('words', {}).values():
            for meaning in word_data.get('meanings', []):
                if meaning.get('CardID') == card_id:
                    return True
        return False
```

### 4. Validation (`src/pipelines/vocabulary/validation/`)

#### Meaning Validator (`meaning_validator.py`)
```python
from typing import List, Dict, Any
from core.stages import Stage, StageResult, StageStatus
from stages.base.validation_stage import ValidationStage

class VocabularyDataValidationStage(ValidationStage):
    """Validate vocabulary-specific data requirements"""
    
    @property
    def name(self) -> str:
        return "validate_vocabulary_data"
    
    @property
    def display_name(self) -> str:
        return "Validate Vocabulary Data"
    
    def __init__(self, pipeline_config: Dict[str, Any]):
        self.config = pipeline_config
        self.data_key = 'vocabulary_data'
    
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate vocabulary data structure"""
        errors = []
        
        if 'words' not in data:
            errors.append("Vocabulary data must contain 'words' section")
            return errors
        
        words_data = data['words']
        if not isinstance(words_data, dict):
            errors.append("'words' must be a dictionary")
            return errors
        
        for word, word_data in words_data.items():
            word_errors = self._validate_word_data(word, word_data)
            errors.extend(word_errors)
        
        return errors
    
    def _validate_word_data(self, word: str, word_data: Dict[str, Any]) -> List[str]:
        """Validate individual word data"""
        errors = []
        
        if 'meanings' not in word_data:
            errors.append(f"Word '{word}' missing 'meanings' section")
            return errors
        
        meanings = word_data['meanings']
        if not isinstance(meanings, list):
            errors.append(f"Word '{word}' meanings must be a list")
            return errors
        
        for i, meaning in enumerate(meanings):
            meaning_errors = self._validate_meaning_data(word, i, meaning)
            errors.extend(meaning_errors)
        
        return errors
    
    def _validate_meaning_data(self, word: str, index: int, meaning: Dict[str, Any]) -> List[str]:
        """Validate individual meaning data"""
        errors = []
        
        required_fields = ['SpanishWord', 'MeaningID', 'CardID', 'MeaningContext']
        for field in required_fields:
            if field not in meaning:
                errors.append(f"Meaning {index} for word '{word}' missing required field: {field}")
        
        # Validate specific field formats
        if 'GappedSentence' in meaning:
            if '_____' not in meaning['GappedSentence']:
                errors.append(f"GappedSentence for {word}:{index} must contain '_____'")
        
        if 'IPA' in meaning:
            ipa = meaning['IPA']
            if not (ipa.startswith('[') and ipa.endswith(']')):
                errors.append(f"IPA for {word}:{index} must be in bracket notation [...]")
        
        return errors
```

### 5. Pipeline Registration

Update the global registry to include the vocabulary pipeline:

```python
# In src/pipelines/__init__.py
from core.registry import get_pipeline_registry
from .vocabulary.vocabulary_pipeline import VocabularyPipeline

def register_builtin_pipelines():
    """Register all built-in pipelines"""
    registry = get_pipeline_registry()
    
    # Register vocabulary pipeline
    vocabulary_pipeline = VocabularyPipeline()
    registry.register(vocabulary_pipeline)

# Auto-register when module is imported
register_builtin_pipelines()
```

### 6. Pipeline Template (`src/pipelines/__template/`)

Create template for future pipelines:

#### Template Pipeline (`template_pipeline.py`)
```python
from typing import List, Dict, Any
from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.context import PipelineContext

class TemplatePipeline(Pipeline):
    """Template pipeline for creating new card types"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @property
    def name(self) -> str:
        return "template"  # Change this
    
    @property
    def display_name(self) -> str:
        return "Template Pipeline"  # Change this
    
    @property
    def stages(self) -> List[str]:
        return [
            'stage1',  # Define your stages
            'stage2',
            'stage3'
        ]
    
    @property
    def data_file(self) -> str:
        return "template.json"  # Change this
    
    @property
    def anki_note_type(self) -> str:
        return "Template Note Type"  # Change this
    
    def get_stage(self, stage_name: str) -> Stage:
        """Get stage instance by name"""
        # Implement stage creation logic
        pass
    
    def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:
        """Execute a specific stage"""
        # Implement stage execution logic
        pass
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/06_vocabulary_pipeline/` pass
- [ ] Complete vocabulary workflow functions end-to-end
- [ ] All existing vocabulary functionality preserved
- [ ] New architecture properly demonstrated

### Implementation Quality
- [ ] All vocabulary processing logic migrated to new architecture
- [ ] Pipeline uses configuration system correctly
- [ ] Stages integrate properly with provider system
- [ ] Data handling maintains existing format compatibility

### Code Quality
- [ ] Clean separation between pipeline logic and core system
- [ ] Comprehensive error handling and validation
- [ ] Consistent with architecture patterns
- [ ] Well-documented extension points

## Deliverables

### 1. Complete Vocabulary Pipeline
- Full pipeline implementation using new architecture
- All vocabulary-specific stages implemented
- Data handling and validation components
- Configuration integration

### 2. Functionality Migration
- All existing vocabulary processing logic preserved
- Claude batch workflow functional
- Media generation integration
- Anki sync integration

### 3. Pipeline Template
- Complete template for creating new pipelines
- Documentation on how to use template
- Example implementations for key patterns

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/07_pipeline_implementation_handoff.md` with:
- Overview of vocabulary pipeline implementation
- Key architectural patterns used
- How template can be used for new pipelines
- Integration points for multi-pipeline support
- Any implementation insights for next session

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 7 E2E tests pass
3. ✅ Complete vocabulary workflow works with new architecture
4. ✅ All existing vocabulary functionality preserved
5. ✅ Pipeline template ready for future card types

### Quality Validation
- Vocabulary pipeline demonstrates architectural benefits
- All existing workflows continue to work
- Code is well-organized and maintainable
- Template makes new pipeline creation straightforward

## Notes for Implementation

### Migration Strategy
- Implement new pipeline alongside existing system
- Migrate functionality incrementally
- Thoroughly test each component
- Preserve all existing data formats

### Design Principles
- **Modularity** - Clean separation of concerns
- **Reusability** - Stages and components can be shared
- **Testability** - Easy to test individual components
- **Extensibility** - Easy to add new functionality

---

**Remember: This vocabulary pipeline implementation serves as the proof-of-concept for the entire refactor. It must demonstrate all the architectural benefits while preserving existing functionality.**