# Extending CLI Commands

Patterns for adding new CLI commands to the system.

## Adding New CLI Commands

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

## Command Implementation Patterns

### Command Class Structure
```python
class CustomCommand:
    def __init__(self, pipeline_registry, provider_registry, project_root, config):
        self.pipeline_registry = pipeline_registry
        self.provider_registry = provider_registry
        self.project_root = project_root
        self.config = config

    def execute(self, args) -> int:
        # Command implementation
        return 0  # Success exit code
```

### Integration Points
- **Registry Access**: All commands receive pipeline and provider registries
- **Configuration**: Access to system configuration via constructor
- **Validation**: Leverage `src/cli/utils/validation.py` utilities
- **Output**: Use `src/cli/utils/output.py` for consistent formatting

## Argument Parsing

### Global Arguments
- `--config`: Custom configuration file path
- `--verbose`: Enable verbose output
- `--dry-run`: Preview mode without execution

### Command-Specific Arguments
Design arguments based on command functionality:
- Use descriptive names with clear help text
- Implement validation for required arguments
- Provide sensible defaults where appropriate

### Validation Patterns
```python
def validate_custom_args(args):
    errors = []
    if not args.required_param:
        errors.append("Missing required parameter")
    return errors
```

## Error Handling Strategy

### Validation Errors
- Pre-execution validation with clear error messages
- Command-specific argument validation
- User feedback with actionable guidance

### Execution Errors
- Exception wrapping with context
- Status code mapping to shell exit codes
- Progress feedback with success/warning/error icons

## Output Formatting

### Consistent Messaging
Use utilities from `src/cli/utils/output.py`:
- `print_success()` for successful operations
- `print_warning()` for warnings
- `print_error()` for errors
- `print_info()` for informational messages

### Structured Output
For complex data, use formatting utilities:
- `format_table()` for tabular data
- `format_key_value_pairs()` for metadata
- Progress indicators for long-running operations

## Command Integration

### Registry Integration
Commands integrate with the pipeline and provider systems:
- Access pipelines via `pipeline_registry.get(name)`
- Access providers via `provider_registry.get_*_provider(name)`
- Use registries for discovery and validation

### Configuration Access
Commands can access configuration:
- Global configuration via `self.config`
- Provider-specific configuration via `config.get_provider(name)`
- Environment variables for runtime settings

### Context Creation
For commands that execute pipelines:
- Create `PipelineContext` with appropriate data
- Inject providers and configuration
- Handle context validation and error propagation

## Testing CLI Commands

### Unit Testing
```python
def test_custom_command():
    command = CustomCommand(mock_registry, mock_providers, Path("."), mock_config)
    result = command.execute(mock_args)
    assert result == 0
```

### Integration Testing
- Test command registration and discovery
- Validate argument parsing and validation
- Check error handling and output formatting
- Test integration with pipeline and provider systems

## Extension Best Practices

### Command Design
- Single responsibility per command
- Clear, descriptive command names
- Comprehensive help text and examples
- Consistent argument naming conventions

### User Experience
- Provide meaningful error messages
- Implement progress indicators for long operations
- Support both interactive and scripted usage
- Follow Unix command-line conventions

### Integration
- Leverage existing utilities and patterns
- Maintain consistency with existing commands
- Use common validation and formatting functions
- Follow established error handling patterns
