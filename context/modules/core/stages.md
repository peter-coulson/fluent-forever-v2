# Stage System

## Stage Abstract Base Class
**Location**: `src/core/stages.py:81`

Abstract base class for individual pipeline execution steps. Stages are the atomic units of work within pipelines, each responsible for a specific transformation or processing task.

## Core Interface

### Identity Properties
- **name** (`stages.py:86`): Unique stage identifier within pipeline
- **display_name** (`stages.py:92`): Human-readable name for UI display

### Execution Method
- **execute()** (`stages.py:97`): Main processing method, receives `PipelineContext`, returns `StageResult`

### Optional Overrides
- **dependencies** (`stages.py:102`): List of stage names that must complete first (default: empty)
- **validate_context()** (`stages.py:106`): Check context has required data (default: no validation)

## Stage Execution Model

### Execution Flow
1. **Dependency Check**: Pipeline verifies all dependent stages completed
2. **Context Validation**: `validate_context()` called before execution
3. **Stage Execution**: `execute()` method processes context data
4. **Result Return**: `StageResult` returned with outcome and any data/errors

### Context Interaction Pattern
```python
def execute(self, context: PipelineContext) -> StageResult:
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
- **success_result()** (`stages.py:45`): Create successful outcome with optional data
- **failure()** (`stages.py:54`): Create failure with error messages
- **partial()** (`stages.py:61`): Create partial success with data and errors
- **skipped()** (`stages.py:76`): Create skipped result with reason

### Convenience Access
- **success** (`stages.py:40`): Boolean property for success check
- Dict-like access: `result['key']`, `result.get('key', default)`

## StageStatus Enum
**Location**: `src/core/stages.py:12`

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
- Implement `execute()` method
- Use `context.get()` and `context.set()` for data flow
- Return appropriate `StageResult` factory method

### Complex Stage with Dependencies
- Override `dependencies` property
- Implement `validate_context()` for data requirements
- Handle partial failures with `StageResult.partial()`
