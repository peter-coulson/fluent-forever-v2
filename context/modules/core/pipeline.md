# Pipeline System

## Pipeline Abstract Base Class
**Location**: `src/core/pipeline.py:11`

Abstract base class defining the interface for all learning workflow pipelines (vocabulary, conjugation, etc.). Each pipeline orchestrates a series of stages to process learning materials.

## Core Interface

### Identity Properties
- **name** (`pipeline.py:16`): Unique pipeline identifier (e.g. 'vocabulary', 'conjugation')
- **display_name** (`pipeline.py:22`): Human-readable name for UI display
- **stages** (`pipeline.py:28`): List of available stage names for this pipeline

### Data Configuration
- **data_file** (`pipeline.py:69`): Primary JSON data file (e.g. 'vocabulary.json')
- **anki_note_type** (`pipeline.py:75`): Anki note type name for card creation

## Pipeline Execution Lifecycle

### Stage Execution Flow
1. **Stage Retrieval**: `get_stage()` (`pipeline.py:33`) - Get stage instance by name
2. **Context Validation**: `stage.validate_context()` called automatically (`pipeline.py:44`)
3. **Stage Execution**: `stage.execute()` called with pipeline context (`pipeline.py:52`)
4. **Completion Tracking**: Successful stages marked complete in context (`pipeline.py:56`)
5. **Error Handling**: Exceptions converted to failure `StageResult` (`pipeline.py:60-65`)

### Key Method: execute_stage()
**Location**: `src/core/pipeline.py:37`

Main execution method that:
- Validates context requirements for the target stage
- Executes the stage with proper error handling
- Tracks completion state in pipeline context
- Returns `StageResult` with execution outcome

## CLI Integration

### Abstract CLI Methods
All pipeline implementations must provide:

- **validate_cli_args()** (`pipeline.py:96`): Validate command-line arguments
- **populate_context_from_cli()** (`pipeline.py:108`): Transfer CLI args to pipeline context
- **show_cli_execution_plan()** (`pipeline.py:118`): Display dry-run execution plan

## Stage Management

### Stage Discovery
- `get_stage()` method must be implemented by concrete pipelines
- `get_stage_info()` (`pipeline.py:83`) provides stage metadata (name, dependencies)
- Stage dependencies automatically validated before execution

### Error Handling
- **StageNotFoundError**: Invalid stage name requested (`pipeline.py:60`)
- **Context Validation**: Stage requirements not met (`pipeline.py:45-49`)
- **Execution Errors**: Unexpected stage failures (`pipeline.py:62-65`)

## Registry Integration
Pipelines are managed via `PipelineRegistry` (`src/core/registry.py`). Global registry accessible through `get_pipeline_registry()` for registration and retrieval of pipeline implementations.
