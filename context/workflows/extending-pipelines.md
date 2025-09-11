# Extending Pipelines

Patterns for adding new pipeline types to the system.

## Adding New Pipeline Types

### 1. Create Pipeline Class
```python
class CustomPipeline(Pipeline):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.stages = [CustomStage1(), CustomStage2()]
```

**Location**: Create in `src/core/pipelines/` directory
**Base class**: `src/core/pipeline.py:13`

### 2. Register Pipeline
Add to pipeline factory in `src/core/pipelines/__init__.py`:
```python
PIPELINE_REGISTRY = {
    'custom': CustomPipeline,
    # existing pipelines...
}
```

### 3. Configuration Template
Create JSON config in `config/` directory following existing patterns.

For pipeline architecture, see: `context/modules/core/pipeline.md`

## Implementing New Stage Types

### Stage Implementation Pattern
```python
class CustomStage(Stage):
    def _execute_impl(self, context: PipelineContext) -> StageResult:
        # Core implementation here - logging/timing handled by base class
        # Get input data
        input_data = context.get('input_key', default_value)

        # Process data...

        # Store result
        context.set('output_key', processed_data)

        return StageResult.success_result("Stage completed successfully")

    def validate_context(self, context: PipelineContext) -> list[str]:
        # Return list of error strings (empty = valid)
        errors = []
        if not context.get('required_key'):
            errors.append("Missing required_key in context")
        return errors
```

### Stage Dependencies
- Override `dependencies` property for stage ordering
- Use `context.get()` and `context.set()` for data passing
- Built-in logging and timing via `self.logger` and `execute()` wrapper
- Implement `_execute_impl()` for core logic, not `execute()`

**Base stage**: `src/core/stages.py:84`
**Context handling**: See `context/modules/core/context.md`

## Configuration Patterns

### Environment Variables
Add new variables to:
1. `.env.example` with documentation
2. `src/core/config.py` validation
3. Pipeline initialization code

### JSON Configuration
Follow existing patterns:
- Pipeline-specific configs in `config/`
- Provider settings in dedicated sections
- Environment variable interpolation support

**Config system**: See `context/modules/core/config.md`

## Testing New Components

### Unit Tests
```python
def test_custom_stage():
    stage = CustomStage()
    context = PipelineContext(pipeline_name="test", project_root=Path("/tmp"))
    context.set('input_key', 'test_value')

    result = stage.execute(context)  # Uses built-in wrapper with logging/timing

    assert result.success
    assert context.get('output_key') == 'expected_value'
```

**Location**: `tests/unit/test_<component>.py`

### Integration Tests
- Test pipeline execution
- Validate stage dependencies
- Check CLI command functionality

**Location**: `tests/integration/`

## Extension Best Practices

### Code Organization
- Single responsibility per component
- Clear separation of concerns
- Consistent error handling patterns
- Comprehensive logging

### Configuration Management
- Environment variable validation
- Graceful degradation for missing config
- Clear configuration documentation

### Error Handling
- Specific exception types
- Meaningful error messages
- Proper cleanup in failure scenarios

### Performance Considerations
- Lazy loading for expensive resources
- Efficient data processing patterns
- Memory usage optimization

## Common Extension Patterns

### Adding New Learning Content Types
1. Define content schema
2. Create processing stages
3. Add CLI commands
4. Create configuration templates

### Pipeline Stage Composition
- Reuse existing stages where possible
- Create atomic, testable stage units
- Use context for clean data passing
- Implement proper stage dependencies
