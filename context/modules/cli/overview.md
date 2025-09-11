# CLI Module Overview

## Architecture

Universal command-line interface providing consistent access to all pipeline operations. Built around three core commands (`run`, `info`, `list`) that interact with the pipeline and provider registry systems.

## Command Structure

### Entry Point
**Universal CLI coordinator** (`src/cli/pipeline_runner.py:main()`)
- Command registration and argument parsing
- Global configuration and registry initialization
- Consistent error handling and output formatting

### Command Classes
**Separate implementations** in `src/cli/commands/` for each command type:
- Dependency injection of registries and configuration
- Consistent `execute(args)` interface returning exit codes
- Shared validation and output utilities

## Core Commands

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `run` | Execute pipeline stages | Context creation, provider injection, dry-run support |
| `info` | Show pipeline details | Stage listing, metadata display, detailed stage info |
| `list` | Discover pipelines | Simple/detailed views, registry enumeration |

## System Integration

### Pipeline System Integration
- **Context Creation**: Builds `PipelineContext` with providers and configuration
- **Stage Execution**: Delegates to pipeline's `execute_stage()` method with proper error handling
- **Validation**: Two-tier validation (CLI arguments + pipeline-specific validation)

### Provider System Integration
- **Registry Access**: Retrieves providers from `ProviderRegistry.from_config()`
- **Context Injection**: Injects data/audio/image/sync providers into execution context
- **Default Selection**: Uses "default" provider configuration for each provider type

## User Experience

### Discovery and Execution
```bash
# Discover available pipelines
cli list --detailed

# Get detailed pipeline information
cli info vocabulary --stages

# Preview execution without side effects
cli run vocabulary --stage prepare --words por,para --dry-run

# Execute pipeline stage
cli run vocabulary --stage prepare --words por,para
```

### Error Handling and Output
- **Validation**: Pre-execution validation with actionable error messages
- **Progress Feedback**: Visual icons and progress indicators for long operations
- **Structured Output**: Consistent formatting for success, warning, and error states
- **Verbose Mode**: Detailed logging and execution information when requested

## Extension Support

- **Unified Interface**: Single entry point for all pipeline operations
- **Dynamic Discovery**: Runtime pipeline and provider discovery via registries
- **Command Pattern**: New commands can be added following established patterns
- **Configuration-Driven**: Behavior controlled via JSON configuration files

See `context/modules/cli/commands.md` for implementation details and `context/workflows/extending-cli.md` for extension patterns.
