# Session 3: Stage System

## Mission
Extract common processing logic into pluggable stages that can be mixed and matched across different pipelines.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/02_core_architecture_handoff.md` - Core architecture context
- `tests/e2e/02_stage_system/` - Validation gates for this session
- `src/core/` - Core pipeline architecture from Session 2
- Current processing scripts to extract common patterns

## Objectives

### Primary Goal
Create a library of reusable stages that handle common operations (media generation, validation, sync, etc.) that can be shared across all pipelines.

### Target Architecture
```
src/
├── stages/
│   ├── __init__.py
│   ├── base/                    # Base stage implementations
│   │   ├── __init__.py
│   │   ├── file_stage.py       # File I/O operations
│   │   ├── validation_stage.py  # Data validation
│   │   └── api_stage.py        # External API calls
│   ├── claude/                  # Claude interaction stages
│   │   ├── __init__.py
│   │   ├── analysis_stage.py   # Word/meaning analysis
│   │   ├── batch_stage.py      # Batch preparation
│   │   └── ingestion_stage.py  # Batch ingestion
│   ├── media/                   # Media generation stages
│   │   ├── __init__.py
│   │   ├── image_stage.py      # Image generation
│   │   ├── audio_stage.py      # Audio generation
│   │   └── media_stage.py      # Combined media generation
│   ├── sync/                    # Synchronization stages
│   │   ├── __init__.py
│   │   ├── template_stage.py   # Template sync
│   │   ├── media_sync_stage.py # Media sync
│   │   └── card_stage.py       # Card sync
│   └── validation/              # Validation stages
│       ├── __init__.py
│       ├── data_stage.py       # Data validation
│       ├── ipa_stage.py        # IPA validation
│       └── media_stage.py      # Media validation
```

## Implementation Requirements

### 1. Base Stage Classes (`src/stages/base/`)

Concrete base implementations for common patterns:

#### File Operations (`file_stage.py`)
```python
from pathlib import Path
from typing import Dict, Any
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext

class FileLoadStage(Stage):
    """Load data from JSON file"""

    def __init__(self, file_key: str, required: bool = True):
        self.file_key = file_key  # Key in context for file path
        self.required = required

    @property
    def name(self) -> str:
        return f"load_{self.file_key}"

    @property
    def display_name(self) -> str:
        return f"Load {self.file_key}"

    def execute(self, context: PipelineContext) -> StageResult:
        # Implementation...
        pass

class FileSaveStage(Stage):
    """Save data to JSON file"""
    # Similar pattern...
```

#### Validation Base (`validation_stage.py`)
```python
class ValidationStage(Stage):
    """Base class for validation stages"""

    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        """Return list of validation errors"""
        pass

    def execute(self, context: PipelineContext) -> StageResult:
        data = context.get(self.data_key)
        errors = self.validate_data(data)

        if errors:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Validation failed: {len(errors)} errors",
                data={},
                errors=errors
            )

        return StageResult(
            status=StageStatus.SUCCESS,
            message="Validation passed",
            data={},
            errors=[]
        )
```

#### API Base (`api_stage.py`)
```python
class APIStage(Stage):
    """Base class for external API operations"""

    def __init__(self, provider_key: str):
        self.provider_key = provider_key

    def execute(self, context: PipelineContext) -> StageResult:
        provider = context.get(f"providers.{self.provider_key}")
        if not provider:
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Provider {self.provider_key} not available",
                data={},
                errors=[f"Missing provider: {self.provider_key}"]
            )

        return self.execute_api_call(context, provider)

    @abstractmethod
    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        """Execute the API call with provider"""
        pass
```

### 2. Claude Interaction Stages (`src/stages/claude/`)

#### Word Analysis (`analysis_stage.py`)
```python
class WordAnalysisStage(Stage):
    """Analyze word meanings (vocabulary pipeline specific)"""

    @property
    def name(self) -> str:
        return "analyze_words"

    @property
    def display_name(self) -> str:
        return "Analyze Word Meanings"

    def execute(self, context: PipelineContext) -> StageResult:
        words = context.get('words', [])
        if not words:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No words provided for analysis",
                data={},
                errors=["Missing 'words' in context"]
            )

        # Analysis logic (extracted from current system)
        analyzed_meanings = self.analyze_meanings(words)

        context.set('analyzed_meanings', analyzed_meanings)
        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Analyzed {len(analyzed_meanings)} meanings",
            data={'meanings': analyzed_meanings},
            errors=[]
        )

    def analyze_meanings(self, words: List[str]) -> List[Dict[str, Any]]:
        """Analyze words and extract distinct meanings"""
        # Extract from existing vocabulary logic
        pass
```

#### Batch Preparation (`batch_stage.py`)
```python
class BatchPreparationStage(Stage):
    """Prepare Claude staging batch"""

    def execute(self, context: PipelineContext) -> StageResult:
        # Extract from cli/prepare_claude_batch.py
        pass
```

#### Batch Ingestion (`ingestion_stage.py`)
```python
class BatchIngestionStage(Stage):
    """Ingest completed Claude batch"""

    def execute(self, context: PipelineContext) -> StageResult:
        # Extract from cli/ingest_claude_batch.py
        pass
```

### 3. Media Generation Stages (`src/stages/media/`)

#### Image Generation (`image_stage.py`)
```python
from stages.base.api_stage import APIStage

class ImageGenerationStage(APIStage):
    """Generate images using configured provider"""

    def __init__(self):
        super().__init__('image_provider')

    @property
    def name(self) -> str:
        return "generate_images"

    @property
    def display_name(self) -> str:
        return "Generate Images"

    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        cards = context.get('cards', [])
        results = []

        for card in cards:
            if 'prompt' in card:
                image_result = provider.generate_image(card['prompt'])
                results.append(image_result)

        context.set('generated_images', results)
        return StageResult(
            status=StageStatus.SUCCESS,
            message=f"Generated {len(results)} images",
            data={'images': results},
            errors=[]
        )
```

#### Audio Generation (`audio_stage.py`)
```python
class AudioGenerationStage(APIStage):
    """Generate audio using configured provider"""
    # Similar pattern to image generation
```

#### Combined Media (`media_stage.py`)
```python
class MediaGenerationStage(Stage):
    """Generate both images and audio"""

    def __init__(self):
        self.image_stage = ImageGenerationStage()
        self.audio_stage = AudioGenerationStage()

    @property
    def dependencies(self) -> List[str]:
        return []  # Can run independently

    def execute(self, context: PipelineContext) -> StageResult:
        # Execute both image and audio generation
        image_result = self.image_stage.execute(context)
        audio_result = self.audio_stage.execute(context)

        # Combine results
        success = (image_result.status == StageStatus.SUCCESS and
                  audio_result.status == StageStatus.SUCCESS)

        return StageResult(
            status=StageStatus.SUCCESS if success else StageStatus.PARTIAL,
            message="Media generation completed",
            data={'image_result': image_result, 'audio_result': audio_result},
            errors=image_result.errors + audio_result.errors
        )
```

### 4. Sync Stages (`src/stages/sync/`)

#### Template Sync (`template_stage.py`)
```python
class TemplateSyncStage(APIStage):
    """Sync templates to Anki"""

    def __init__(self):
        super().__init__('anki_provider')

    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        # Extract from existing sync/templates_sync.py
        pass
```

#### Card Sync (`card_stage.py`)
```python
class CardSyncStage(APIStage):
    """Sync cards to Anki"""

    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        # Extract from existing sync/cards_sync.py
        pass
```

### 5. Validation Stages (`src/stages/validation/`)

#### Data Validation (`data_stage.py`)
```python
from stages.base.validation_stage import ValidationStage

class DataValidationStage(ValidationStage):
    """Validate card data structure"""

    @property
    def name(self) -> str:
        return "validate_data"

    @property
    def display_name(self) -> str:
        return "Validate Data Structure"

    def __init__(self, data_key: str):
        self.data_key = data_key

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        errors = []

        # Extract validation logic from existing system
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")

        # Additional validation rules...

        return errors
```

#### IPA Validation (`ipa_stage.py`)
```python
class IPAValidationStage(ValidationStage):
    """Validate IPA pronunciation"""

    def validate_data(self, data: Dict[str, Any]) -> List[str]:
        # Extract from validation/ipa_validator.py
        pass
```

### 6. Stage Factory (`src/stages/__init__.py`)

Provide easy access to all stages:

```python
from typing import Dict, Type
from core.stages import Stage

# Import all stage classes
from .claude.analysis_stage import WordAnalysisStage
from .claude.batch_stage import BatchPreparationStage
from .claude.ingestion_stage import BatchIngestionStage
from .media.image_stage import ImageGenerationStage
from .media.audio_stage import AudioGenerationStage
from .media.media_stage import MediaGenerationStage
from .sync.template_stage import TemplateSyncStage
from .sync.card_stage import CardSyncStage
from .validation.data_stage import DataValidationStage
from .validation.ipa_stage import IPAValidationStage

# Stage registry for easy lookup
STAGE_REGISTRY: Dict[str, Type[Stage]] = {
    'analyze_words': WordAnalysisStage,
    'prepare_batch': BatchPreparationStage,
    'ingest_batch': BatchIngestionStage,
    'generate_images': ImageGenerationStage,
    'generate_audio': AudioGenerationStage,
    'generate_media': MediaGenerationStage,
    'sync_templates': TemplateSyncStage,
    'sync_cards': CardSyncStage,
    'validate_data': DataValidationStage,
    'validate_ipa': IPAValidationStage,
}

def get_stage(stage_name: str, **kwargs) -> Stage:
    """Get stage instance by name"""
    if stage_name not in STAGE_REGISTRY:
        raise ValueError(f"Unknown stage: {stage_name}")

    stage_class = STAGE_REGISTRY[stage_name]
    return stage_class(**kwargs)

def list_stages() -> List[str]:
    """List all available stage names"""
    return list(STAGE_REGISTRY.keys())
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/02_stage_system/` pass
- [ ] Stage execution works correctly
- [ ] Stage chaining executes in proper order
- [ ] Error handling propagates correctly

### Implementation Quality
- [ ] All common processing patterns extracted into reusable stages
- [ ] Base classes provide clean extension points
- [ ] Stage registry supports dynamic stage discovery
- [ ] Context system enables data flow between stages

### Code Quality
- [ ] Consistent error handling across all stages
- [ ] Clear logging and debugging information
- [ ] Type hints and docstrings throughout
- [ ] Unit tests for all stage implementations

## Deliverables

### 1. Complete Stage Library
- All stage categories implemented as outlined
- Base classes for common patterns
- Stage registry for dynamic discovery
- Integration with core pipeline system

### 2. Extracted Processing Logic
- Move existing logic from CLI scripts into appropriate stages
- Maintain functionality while improving modularity
- Clean interfaces between stages

### 3. Unit Tests
- Comprehensive unit tests for all stages
- Mock external dependencies (APIs, file system)
- Error handling and edge case coverage

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/03_stage_system_handoff.md` with:
- Overview of implemented stage library
- Available stages and their capabilities
- How to create new stages
- Integration points for provider system
- Any implementation insights for Session 4

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 3 E2E tests pass
3. ✅ Stage library covers all major processing operations
4. ✅ Stages can be chained together successfully
5. ✅ Error handling works across stage boundaries

### Quality Validation
- Stage interfaces are clean and consistent
- Common patterns are properly abstracted
- Stages can be mixed and matched between pipelines
- Error messages provide actionable debugging information

## Notes for Implementation

### Extraction Strategy
- Identify common patterns in existing CLI scripts
- Extract business logic while preserving functionality
- Create clean interfaces between stages
- Maintain existing error handling and logging

### Design Principles
- **Single Responsibility** - Each stage does one thing well
- **Composability** - Stages can be combined in different ways
- **Testability** - Easy to test stages in isolation
- **Reusability** - Stages work across multiple pipelines

---

**Remember: These stages will be the building blocks that all pipelines use. Focus on creating clean, reusable components that can be mixed and matched.**
