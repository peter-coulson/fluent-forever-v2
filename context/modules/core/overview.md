# Core Module Overview

## Purpose
Implements the fundamental abstractions for the pipeline system: base classes for pipelines and stages, execution context management, configuration loading, and component registries.

## Implementation Architecture

### Registry Pattern (`src/core/registry.py:11`)
**Central component discovery and management**
- **PipelineRegistry**: Registers and provides access to pipeline implementations
- **Global instance**: Singleton pattern via `get_pipeline_registry()`
- **Discovery methods**: `list_pipelines()`, `get_pipeline_info()`, `has_pipeline()`
- **Registration**: `register()` method for adding new pipeline types

### Configuration System (`src/core/config.py:13`)
**JSON-based configuration with environment variable support**
- **Loading**: Automatic `config.json` detection with fallback handling
- **Environment substitution**: `${VAR}` and `${VAR:default}` pattern processing
- **Access patterns**: Dot notation via `get()`, provider-specific via `get_provider()`
- **Integration**: Injected into `PipelineContext` for stage access

### Exception Hierarchy (`src/core/exceptions.py:4-34`)
**Structured error handling for pipeline operations**
- **Base exceptions**: `PipelineError`, `StageError`, `ContextError`
- **Specific errors**: `StageNotFoundError`, `ConfigurationError`, `ValidationError`
- **Error propagation**: Stage errors bubble up through pipeline execution

### Logging Integration (`src/utils/logging_config.py`)
**Context-aware logging with performance monitoring and environment detection**
- **Configuration Templates**: `get_logging_config()` for dictConfig-based setup
- **Test Environment Detection**: Automatic detection with file logging disabled in tests
- **Stage logging**: Automatic logger creation for each stage instance
- **Context logging**: Pipeline-specific loggers via `get_context_logger()`
- **Performance tracking**: Built-in timing for stage execution
- **Visual indicators**: Icons and colored output for status display

## Implementation Entry Points

### Pipeline Development
- **Base class**: Inherit from `Pipeline` abstract class
- **Required methods**: `get_stage()`, `validate_cli_args()`, `populate_context_from_cli()`
- **Registration**: Add to registry in initialization code
- **Stage management**: Implement stage discovery and instantiation

### Stage Development
- **Base class**: Inherit from `Stage` abstract class
- **Core methods**: Implement `_execute_impl()` (not `execute()`) and `validate_context()`
- **Built-in features**: Automatic logging, timing, and validation via `execute()` wrapper
- **Dependencies**: Override `dependencies` property for stage ordering
- **Results**: Return `StageResult` with appropriate status and data
- **Logging**: Access stage logger via `self.logger` for custom logging

### Configuration Integration
- **Provider settings**: Use `config.get_provider(name)` for external service configuration
- **System settings**: Use `config.get_system_settings()` for application configuration
- **Environment**: Leverage `${VAR}` substitution for sensitive values like API keys

### Context Usage
- **Data flow**: Use `context.get()`/`context.set()` for inter-stage communication
- **Error handling**: Use `context.add_error()` for stage-level error accumulation
- **Completion tracking**: Automatic via `context.mark_stage_complete()`

## Testing Integration

**Risk Assessment**: Core pipeline components require testing assessment using `context/testing/meta/decision-framework.md` criteria:
- **Pipeline execution**: High-risk for context flow and stage orchestration
- **Configuration system**: High-risk for validation and environment substitution
- **Registry pattern**: Medium-risk for component discovery and registration

**Testing Strategy**: Reference `context/testing/strategy/risk-based-testing.md` for core component testing approaches and `context/testing/strategy/mock-boundaries.md` for internal vs external testing boundaries.

See `context/system/core-concepts.md` for component definitions and relationships.
