# Stage System

## Stage Abstract Base Class
**Location**: `src/core/stages.py:84`

Abstract base class for individual pipeline execution steps with built-in logging, timing, and validation. Stages are the atomic units of work within pipelines, each responsible for a specific transformation or processing task.

## Core Interface

### Identity Properties
- **name** (`stages.py:91`): Unique stage identifier within pipeline (abstract property)
- **display_name** (`stages.py:97`): Human-readable name for UI display (abstract property)

### Execution Methods
- **execute()** (`stages.py:104`): Concrete wrapper with logging, timing, and validation
- **_execute_impl()** (`stages.py:136`): Abstract method for stage implementation (must override)

### Optional Overrides
- **dependencies** (`stages.py:141`): List of stage names that must complete first (default: empty)
- **validate_context()** (`stages.py:145`): Check context has required data (default: no validation)

## Stage Execution Model

### Execution Flow
1. **Dependency Check**: Pipeline verifies all dependent stages completed
2. **Logging Setup**: Context-aware logger initialized for stage
3. **Context Validation**: `validate_context()` called with failure logging
4. **Performance Timing**: Execution timer started
5. **Stage Implementation**: `_execute_impl()` method processes context data
6. **Result Logging**: Success/failure logged with timing and visual icons
7. **Result Return**: `StageResult` returned with outcome and any data/errors

### Context Interaction Pattern
```python
def _execute_impl(self, context: PipelineContext) -> StageResult:
    # Built-in logging and timing handled by execute() wrapper
    # Implement core stage logic here

    # Read from context
    input_data = context.get('key', default_value)

    # Process data...

    # Write to context
    context.set('output_key', result_data)

    return StageResult.success_result("Processing complete", {"processed": count})
```

## StageResult Class
**Location**: `src/core/stages.py:22`

Container for stage execution outcomes with rich status information.

### Properties
- **status** (`stages.py:25`): `StageStatus` enum value
- **message** (`stages.py:26`): Human-readable outcome description
- **data** (`stages.py:27`): Dictionary of stage output data
- **errors** (`stages.py:28`): List of error messages

### Factory Methods
- **success_result()** (`stages.py:48`): Create successful outcome with optional data
- **failure()** (`stages.py:57`): Create failure with error messages
- **partial()** (`stages.py:64`): Create partial success with data and errors
- **skipped()** (`stages.py:79`): Create skipped result with reason

### Convenience Access
- **success** (`stages.py:43`): Boolean property for success check
- Dict-like access: `result['key']`, `result.get('key', default)`

## StageStatus Enum
**Location**: `src/core/stages.py:15`

Standardized execution outcome states:

| Status | Value | Meaning |
|--------|-------|---------|
| SUCCESS | "success" | Stage completed successfully |
| FAILURE | "failure" | Stage failed with errors |
| PARTIAL | "partial" | Stage partially succeeded |
| SKIPPED | "skipped" | Stage bypassed (conditions not met) |

## Dependencies and Validation

### Stage Dependencies
- Declared in `dependencies` property as list of stage names
- Pipeline automatically validates dependencies before execution
- Circular dependencies not explicitly prevented - implementation responsibility

### Context Validation
- `validate_context()` method checks required context data exists
- Returns list of error strings (empty list = valid)
- Called automatically by pipeline before stage execution
- Validation failures prevent stage execution

## Implementation Patterns

### Simple Processing Stage
- Implement `_execute_impl()` method (not `execute()`)
- Use `context.get()` and `context.set()` for data flow
- Return appropriate `StageResult` factory method
- Logging, timing, and validation handled automatically by base class

### Complex Stage with Dependencies
- Override `dependencies` property
- Implement `validate_context()` for data requirements
- Implement `_execute_impl()` with core stage logic
- Handle partial failures with `StageResult.partial()`
- Access stage logger via `self.logger` for custom logging
