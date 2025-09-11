# Core Concepts

**AUTHORITATIVE SOURCE**: This file contains the definitive definitions of all system components.

## Primary Components

### Pipeline (`src/core/pipeline.py:13`)
**Abstract base class for learning workflows**
- Orchestrates multi-stage learning processes (vocabulary, conjugation)
- Manages stage execution and data flow between processing steps
- Provides CLI integration with argument validation and dry-run support
- **Properties**: `name`, `display_name`, `stages`, `data_file`, `anki_note_type`
- **Key methods**: `execute_stage()`, `get_stage()`, `validate_cli_args()`

### Stage (`src/core/stages.py:81`)
**Individual processing units within pipelines**
- Execute specific learning workflow tasks (prepare data, generate media, sync)
- Validate required context data before execution
- Return structured results with status (SUCCESS, FAILURE, PARTIAL, SKIPPED)
- **Properties**: `name`, `display_name`, `dependencies`
- **Key methods**: `execute()`, `validate_context()`

### PipelineContext (`src/core/context.py:11`)
**Execution state container passed between stages**
- Maintains data flow between pipeline stages via `get()`/`set()` methods
- Tracks stage completion status and error accumulation
- Contains configuration, CLI arguments, and provider references
- **Properties**: `pipeline_name`, `project_root`, `data`, `completed_stages`, `errors`

### StageResult (`src/core/stages.py:22`)
**Result container for stage execution outcomes**
- Encapsulates execution status, messages, data, and errors
- **Factory methods**: `success_result()`, `failure()`, `partial()`, `skipped()`
- **Properties**: `status`, `message`, `data`, `errors`, `success`

## Provider System

### Provider Registry (`src/providers/registry.py:18`)
**Central management for external service integrations**
- Factory pattern for creating provider instances from configuration
- Type-specific registries: data, media (audio/image), sync providers
- Global singleton access via `get_provider_registry()`
- Default provider selection and configuration-based instantiation

### Provider Types
- **DataProvider** (`src/providers/base/data_provider.py:11`): JSON, database, memory storage
- **MediaProvider** (`src/providers/base/media_provider.py:44`): Audio/image generation APIs
- **SyncProvider** (`src/providers/base/sync_provider.py:47`): Anki, flashcard system integration

## Configuration System (`src/core/config.py:13`)
**Environment-aware settings management**
- JSON-based configuration with `${VAR}` and `${VAR:default}` substitution
- Recursive processing of nested dictionaries and lists
- Provider-specific settings via `get_provider()` method
- Graceful degradation for missing configuration files
