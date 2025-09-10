# Pipeline Implementations Overview

## Current Implementation Status

**No concrete pipeline implementations exist yet** - the pipeline system is architectural foundation waiting for learning workflow implementations.

## Pipeline Framework Structure

### Abstract Pipeline Base (`src/core/pipeline.py`)
- **Pipeline Class**: ABC defining pipeline interface and execution patterns
- **Required Properties**: `name`, `display_name`, `stages`, `data_file`, `anki_note_type`
- **Execution Model**: Stage-based workflow with context validation and error handling

### Registry System (`src/core/registry.py`)
- **PipelineRegistry**: Central registration and discovery system
- **Global Instance**: `_global_registry` provides singleton access via `get_pipeline_registry()`
- **Discovery Methods**: `list_pipelines()`, `get_pipeline_info()`, `has_pipeline()`

## Learning Workflow Patterns

Based on CLI validation patterns and system architecture, pipelines should support these learning workflows:

### Vocabulary Learning Pipeline
- **Data Source**: `vocabulary.json` data file
- **Anki Integration**: Custom note type for vocabulary cards
- **Stages**: prepare, media, sync workflow pattern
- **CLI Arguments**: `--words` for prepare stage, `--cards` for media stage

### Conjugation Learning Pipeline
- **Data Source**: Conjugation-specific data file
- **Anki Integration**: Verb conjugation note type
- **Stages**: Similar staged approach for verb conjugation learning
- **CLI Arguments**: Verb-specific arguments for conjugation practice

## Pipeline Implementation Requirements

### Abstract Methods Implementation
- **`get_stage(stage_name)`**: Return `Stage` instance for execution
- **`validate_cli_args(args)`**: Pipeline-specific argument validation
- **`populate_context_from_cli(context, args)`**: Extract CLI data into pipeline context
- **`show_cli_execution_plan(context, args)`**: Dry-run preview display

### Stage Integration Pattern
- **Stage Discovery**: Pipeline maintains list of available stage names
- **Stage Instantiation**: `get_stage()` creates executable stage instances
- **Context Validation**: Each stage validates required context data
- **Result Handling**: Success/failure/partial results with error collection

## Data Flow Architecture

### Context-Driven Execution
1. **Context Creation**: CLI creates `PipelineContext` with providers and configuration
2. **CLI Population**: Pipeline extracts CLI arguments into context using `populate_context_from_cli()`
3. **Stage Execution**: Pipeline delegates to stage with populated context
4. **Result Processing**: Stage results bubble up through pipeline to CLI

### Provider Integration
- **Provider Injection**: CLI injects data/audio/image/sync providers into context
- **Default Selection**: Uses "default" provider configuration for each type
- **Provider Access**: Stages access providers through context for external operations

## Future Pipeline Types

### Expected Pipeline Implementations
- **Vocabulary Pipeline**: Spanish vocabulary with definitions, audio, images
- **Conjugation Pipeline**: Verb conjugation patterns and practice
- **Grammar Pipeline**: Grammar concepts and examples
- **Phrase Pipeline**: Common phrases and usage patterns

### Registration Pattern
```python
# Future pipeline registration
from src.pipelines.vocabulary import VocabularyPipeline
from src.pipelines.conjugation import ConjugationPipeline

registry = get_pipeline_registry()
registry.register(VocabularyPipeline())
registry.register(ConjugationPipeline())
```

## Extension Guidelines

### Creating New Pipelines
1. **Inherit from Pipeline**: Extend abstract base class in `src/core/pipeline.py`
2. **Implement Abstract Methods**: All required methods and properties
3. **Define Stages**: Create stage classes and stage discovery logic
4. **Register Pipeline**: Add to registry in `src/pipelines/__init__.py`
5. **CLI Integration**: Ensure CLI arguments match validation patterns

### Stage Design Patterns
- **Stage Inheritance**: Extend `Stage` from `src/core/stages.py`
- **Context Validation**: Implement `validate_context()` with specific requirements
- **Provider Usage**: Access providers through context for external operations
- **Error Handling**: Return `StageResult` with appropriate status and messages
