# CLI Module Overview

## Architecture

Universal command-line interface providing consistent access to all pipeline operations. Built around three core commands (`run`, `info`, `list`) that interact with the pipeline and provider registry systems.

## Command Structure

### Entry Point
**Universal CLI coordinator** (`src/cli/pipeline_runner.py:main()`)
- Command registration and argument parsing with verbose mode support
- Enhanced logging setup with environment configuration and file output
- Global configuration and registry initialization with comprehensive logging
- Consistent error handling and output formatting with visual status indicators

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
- **Registry Access**: Retrieves providers from `ProviderRegistry.from_config()` with pipeline assignments
- **Filtered Context Injection**: Injects only pipeline-authorized providers via `get_providers_for_pipeline()`
- **Named Provider Support**: Uses named provider configuration with required `pipelines` field

## User Experience

### Key Features
- **Discovery**: `cli list --detailed` shows available pipelines
- **Execution**: `cli run pipeline --stage name` executes with context
- **Preview**: `--dry-run` flag previews operations safely
- **Validation**: Pre-execution validation with clear error messages

### Error Handling
- **Progress Feedback**: Visual icons and status indicators
- **Structured Output**: Consistent formatting for all states
- **Verbose Mode**: Debug logging via `--verbose` or `FLUENT_FOREVER_DEBUG`
- **Performance Tracking**: Execution timing when verbose enabled

See `context/modules/cli/commands.md` for implementation details and `context/workflows/extending-cli.md` for extension patterns.
