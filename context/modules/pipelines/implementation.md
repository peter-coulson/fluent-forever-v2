# Pipeline Implementation Guide

## Implementation Requirements

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

## Creating New Pipelines

### Development Steps
1. **Inherit from Pipeline**: Extend abstract base class in `src/core/pipeline.py`
2. **Implement Abstract Methods**: All required methods and properties
3. **Define Stages**: Create stage classes and stage discovery logic
4. **Register Pipeline**: Add to registry in `src/pipelines/__init__.py`
5. **CLI Integration**: Ensure CLI arguments match validation patterns

### Registration Pattern
```python
# Future pipeline registration
from src.pipelines.vocabulary import VocabularyPipeline
from src.pipelines.conjugation import ConjugationPipeline

registry = get_pipeline_registry()
registry.register(VocabularyPipeline())
registry.register(ConjugationPipeline())
```

### Stage Design Patterns
- **Stage Inheritance**: Extend `Stage` from `src/core/stages.py`
- **Context Validation**: Implement `validate_context()` with specific requirements
- **Provider Usage**: Access providers through context for external operations
- **Error Handling**: Return `StageResult` with appropriate status and messages

## Future Pipeline Types

### Expected Implementations
- **Vocabulary Pipeline**: Spanish vocabulary with definitions, audio, images
- **Conjugation Pipeline**: Verb conjugation patterns and practice
- **Grammar Pipeline**: Grammar concepts and examples
- **Phrase Pipeline**: Common phrases and usage patterns
