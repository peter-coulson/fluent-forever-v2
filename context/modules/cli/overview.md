# CLI Module Overview

## Architecture

Universal pipeline runner with command-based structure providing consistent interface for all learning workflow operations. Built around three core commands (run, info, list) that interact with the pipeline registry system.

## Command Structure

- **Entry Point**: `src/cli/pipeline_runner.py:main()` - Universal CLI coordinator
- **Command Classes**: Separate implementations in `src/cli/commands/` for each command type
- **Registry Integration**: Direct connection to pipeline registry for discovery and execution

## Main Commands

| Command | Purpose | Key Features |
|---------|---------|--------------|
| `run` | Execute pipeline stages | Context creation, provider injection, dry-run support |
| `info` | Show pipeline details | Stage listing, metadata display, detailed stage info |
| `list` | Discover pipelines | Simple/detailed views, registry enumeration |

## Integration Patterns

### Pipeline System Integration
- **Context Creation**: `src/cli/commands/run_command.py:86-113` creates `PipelineContext` with providers
- **Stage Execution**: Delegates to pipeline's `execute_stage()` method
- **Validation**: Two-tier validation (CLI args + pipeline-specific args)

### Provider System Integration
- **Registry Access**: Gets providers from `ProviderRegistry.from_config()`
- **Context Injection**: Adds data/audio/image/sync providers to execution context
- **Default Provider Selection**: Uses "default" provider for each category

## User Interaction Patterns

### Discovery Workflow
```bash
# List available pipelines
cli list --detailed

# Get pipeline information
cli info vocabulary --stages
```

### Execution Workflow
```bash
# Dry run to preview
cli run vocabulary --stage prepare --words por,para --dry-run

# Execute stage
cli run vocabulary --stage prepare --words por,para
```

### Error Handling
- **Validation Errors**: Pre-execution validation with clear error messages
- **Pipeline Errors**: Wrapped exceptions with contextual information
- **Icon-based Output**: Visual feedback using emoji icons for success/error/warning states

## Key Features

- **Unified Interface**: Single entry point replaces hardcoded pipeline scripts
- **Dynamic Discovery**: Pipeline registration enables runtime discovery
- **Configurable**: Supports custom config files and verbose output
- **Dry-run Support**: Preview execution plans without side effects
- **Extensible**: New commands can be added via command class pattern
