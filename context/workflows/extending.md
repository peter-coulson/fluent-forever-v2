# Extending the System

Patterns and workflows for extending Fluent Forever V2 with new functionality.

## Adding New Pipeline Types

### 1. Create Pipeline Class
```python
class CustomPipeline(Pipeline):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.stages = [CustomStage1(), CustomStage2()]
```

**Location**: Create in `src/core/pipelines/` directory
**Base class**: `src/core/pipeline.py:15`

### 2. Register Pipeline
Add to pipeline factory in `src/core/pipelines/__init__.py`:
```python
PIPELINE_REGISTRY = {
    'custom': CustomPipeline,
    # existing pipelines...
}
```

### 3. Configuration Template
Create YAML config in `config/` directory following existing patterns.

For pipeline architecture, see: `context/modules/core/pipeline.md`

## Implementing New Stage Types

### Stage Implementation Pattern
```python
class CustomStage(Stage):
    def execute(self, context: PipelineContext) -> PipelineContext:
        # Implementation here
        return context

    def validate_inputs(self, context: PipelineContext) -> bool:
        # Validation logic
        pass
```

### Stage Dependencies
- Override `get_dependencies()` for stage ordering
- Use `context.get()` and `context.set()` for data passing
- Implement error handling and logging

**Base stage**: `src/core/stage.py:10`
**Context handling**: See `context/modules/core/context.md`

## Creating New Provider Integrations

### 1. Implement Provider Interface
Choose appropriate base class:
- **DataProvider**: For data sources
- **AudioProvider**: For audio generation
- **ImageProvider**: For image generation
- **SyncProvider**: For external service sync

**Location**: `src/providers/<type>/<provider_name>_provider.py`

### 2. Provider Implementation
```python
class CustomProvider(DataProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def fetch_data(self, query: str) -> List[Dict]:
        # Implementation here
        pass
```

### 3. Register Provider
Add to `src/providers/registry.py:45`:
```python
'custom_data': CustomProvider,
```

**Provider patterns**: See `context/modules/providers/base.md`

## Extending CLI Commands

### 1. Create Command Module
```python
@click.command()
@click.option('--param', help='Parameter description')
def custom_command(param):
    """Custom command description."""
    # Implementation
```

**Location**: `src/cli/commands/custom_command.py`

### 2. Register Command
Add to `src/cli/main.py` command group:
```python
cli.add_command(custom_command)
```

### 3. Command Patterns
- Use click decorators for argument parsing
- Implement proper error handling
- Follow existing logging patterns

**CLI structure**: See `context/modules/cli/overview.md`

## Configuration Patterns

### Environment Variables
Add new variables to:
1. `.env.example` with documentation
2. `src/core/config.py` validation
3. Provider initialization code

### YAML Configuration
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
    context = PipelineContext({'input': 'test'})
    result = stage.execute(context)
    assert result.get('output') == 'expected'
```

**Location**: `tests/unit/test_<component>.py`

### Integration Tests
- Test provider connections
- Validate pipeline execution
- Check CLI command functionality

**Location**: `tests/integration/`

### Provider Mock Tests
Create mocks for external services in `tests/mocks/`

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
- Connection pooling for external services
- Efficient data processing patterns

## Common Extension Patterns

### Adding New Learning Content Types
1. Define content schema
2. Create processing stages
3. Implement provider integrations
4. Add CLI commands
5. Create configuration templates

### External Service Integration
1. Abstract service behind provider interface
2. Implement authentication/authorization
3. Add retry logic and error handling
4. Create provider registry entry
5. Add configuration validation

### Pipeline Stage Composition
- Reuse existing stages where possible
- Create atomic, testable stage units
- Use context for clean data passing
- Implement proper stage dependencies

For implementation details, see:
- `context/modules/core/overview.md`
- `context/modules/providers/overview.md`
- `context/modules/cli/overview.md`
