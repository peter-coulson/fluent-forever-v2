# Core Module Overview

## Purpose
Implements the fundamental abstractions for the pipeline system: base classes for pipelines and stages, execution context management, configuration loading, and component registries.

## Implementation Architecture

### Registry Pattern (`src/core/registry.py:9`)
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

### Exception Hierarchy (`src/core/exceptions.py:4-37`)
**Structured error handling for pipeline operations**
- **Base exceptions**: `PipelineError`, `StageError`, `ContextError`
- **Specific errors**: `StageNotFoundError`, `ConfigurationError`, `ValidationError`
- **Error propagation**: Stage errors bubble up through pipeline execution

## Implementation Entry Points

### Pipeline Development
- **Base class**: Inherit from `Pipeline` abstract class
- **Required methods**: `get_stage()`, `validate_cli_args()`, `populate_context_from_cli()`
- **Registration**: Add to registry in initialization code
- **Stage management**: Implement stage discovery and instantiation

### Stage Development
- **Base class**: Inherit from `Stage` abstract class
- **Core methods**: Implement `execute()` and `validate_context()`
- **Dependencies**: Override `dependencies` property for stage ordering
- **Results**: Return `StageResult` with appropriate status and data

### Configuration Integration
- **Provider settings**: Use `config.get_provider(name)` for external service configuration
- **System settings**: Use `config.get_system_settings()` for application configuration
- **Environment**: Leverage `${VAR}` substitution for sensitive values like API keys

### Context Usage
- **Data flow**: Use `context.get()`/`context.set()` for inter-stage communication
- **Error handling**: Use `context.add_error()` for stage-level error accumulation
- **Completion tracking**: Automatic via `context.mark_stage_complete()`

See `context/system/core-concepts.md` for component definitions and relationships.
