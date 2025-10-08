# Pipeline Context

## PipelineContext Class
**Location**: `src/core/context.py:9`

Central data container that flows through pipeline execution, maintaining state, configuration, and shared data between stages. Acts as the primary communication mechanism for pipeline workflows.

## Core Data Structure

### Required Fields
- **pipeline_name** (`context.py:13`): Identifies which pipeline is executing
- **project_root** (`context.py:14`): Path to project directory for file operations

### Mutable Collections
- **data** (`context.py:17`): Dict for inter-stage data sharing (stages read/write)
- **config** (`context.py:20`): Configuration dictionary from Config loader
- **completed_stages** (`context.py:23`): List tracking successfully completed stage names
- **errors** (`context.py:24`): Accumulated error messages from stages
- **args** (`context.py:27`): Command-line arguments dictionary

## Data Management Interface

### Data Access Methods
- **get()** (`context.py:29`): Retrieve data value with optional default
- **set()** (`context.py:33`): Store data value for sharing between stages

### Error Handling Methods
- **add_error()** (`context.py:37`): Append error message to errors list
- **has_errors()** (`context.py:42`): Boolean check for any accumulated errors

### Stage Tracking Methods
- **mark_stage_complete()** (`context.py:45`): Add stage name to completion list
- Completed stages list prevents duplicate execution and tracks progress

## Context Lifecycle

### Context Creation
Typically created by CLI or pipeline runner with:
- Pipeline name from user input
- Project root from current directory or config
- Initial configuration loaded from Config system

### Stage-to-Stage Flow
1. **Stage Reads**: Stage uses `context.get()` to retrieve input data
2. **Stage Processes**: Stage performs its specific transformation/processing
3. **Stage Writes**: Stage uses `context.set()` to store output data
4. **Completion Tracking**: Pipeline calls `mark_stage_complete()` on success
5. **Error Accumulation**: Errors added via `add_error()` if issues occur

### Context State Evolution
```
Initial Context → Stage 1 execution → Updated Context → Stage 2 execution → Final Context
    ↓                ↓                    ↓                ↓                    ↓
config data     reads/writes data    more data added   further processing   complete state
empty errors    potential errors     error accumulation  more errors        final errors
no completions  stage 1 complete     stage 1,2 complete  all stages done    full tracking
```

## Data Sharing Patterns

### Common Data Keys
Context data dictionary typically contains:
- Input data loaded by initial stages
- Processed results from transformation stages
- File paths for output files
- External service responses (API calls, file generation)
- Counts and statistics from processing

### Configuration Integration
- **config** field populated from `Config.to_dict()`
- Stages access provider settings: `context.config['providers']['anki']`
- System settings available: `context.config['system']`

## Integration Points

### CLI Integration
- **args** field contains parsed command-line arguments
- Pipelines populate context from CLI args via `populate_context_from_cli()`

### Stage Dependencies
- Stages check `completed_stages` list for dependency validation
- Error accumulation allows stages to fail gracefully while providing context

### Error Propagation
- Context errors aggregated across all stages
- Final pipeline result includes all context errors
- Allows debugging of multi-stage failures
