# Core Concepts

**AUTHORITATIVE SOURCE**: This file contains the definitive definitions of all system components.

## Primary Components

### Pipeline (`src/core/pipeline.py:13`)
**Abstract base class for learning workflows**
- Orchestrates multi-stage learning processes (vocabulary, conjugation)
- Manages stage execution and data flow between processing steps
- Provides CLI integration with argument validation and dry-run support
- **Sequential Execution**: Phase support for executing multiple stages with shared context
- **Properties**: `name`, `display_name`, `stages`, `phases`, `data_file`, `anki_note_type`
- **Key methods**: `execute_stage()`, `execute_phase()`, `get_stage()`, `get_phase_info()`, `validate_cli_args()`

### Phase (Pipeline Concept)
**Named groupings of stages for sequential execution**
- Configurable stage collections defined by pipeline implementation
- Enable efficient batch processing with shared context between stages
- Support fail-fast behavior: phase stops if any stage fails (unless partial success)
- **Common patterns**: `preparation`, `media_generation`, `completion`, `full`
- **Properties**: `name`, `stages` (list), `stage_count`

### Stage (`src/core/stages.py:84`)
**Individual processing units within pipelines**
- Execute specific learning workflow tasks (prepare data, generate media, sync)
- Built-in logging, performance timing, and validation via concrete `execute()` wrapper
- Subclasses implement abstract `_execute_impl()` for core stage logic
- Return structured results with status (SUCCESS, FAILURE, PARTIAL, SKIPPED)
- **Properties**: `name`, `display_name`, `dependencies`
- **Key methods**: `execute()` (concrete), `_execute_impl()` (abstract), `validate_context()`

### PipelineContext (`src/core/context.py:11`)
**Execution state container passed between stages**
- Maintains data flow between pipeline stages via `get()`/`set()` methods
- Tracks stage completion status and error accumulation
- Contains configuration, CLI arguments, and provider references
- **Properties**: `pipeline_name`, `project_root`, `data`, `completed_stages`, `errors`

### StageResult (`src/core/stages.py:25`)
**Result container for stage execution outcomes**
- Encapsulates execution status, messages, data, and errors
- **Factory methods**: `success_result()`, `failure()`, `partial()`, `skipped()`
- **Properties**: `status`, `message`, `data`, `errors`, `success`

## Logging System (`src/utils/logging_config.py`)
**Comprehensive logging infrastructure with performance monitoring**
- Context-aware logging with pipeline-specific identification via `get_context_logger()`
- Performance timing decorators for method execution monitoring via `log_performance()`
- Environment-based configuration with module-specific log levels
- Colored console output with icons for visual status indicators
- **Key functions**: `setup_logging()`, `get_logger()`, `get_context_logger()`, `log_performance()`
- **Components**: `ColoredFormatter`, `PerformanceFormatter`, `ContextualError`

## Provider System

### Provider Registry (`src/providers/registry.py:35`)
**Central management with dynamic loading and configuration injection**
- **Dynamic Loading**: `MEDIA_PROVIDER_REGISTRY` mapping enables runtime provider instantiation via `_create_media_provider()`
- **Configuration Processing**: `_extract_provider_configs()` validates and organizes provider configurations by type
- **Error Handling**: Strict validation with clear error messages for unsupported provider types
- Type-specific registries: data, media (audio/image), sync providers
- **Pipeline Assignment System**: Providers can be restricted to specific pipelines via `pipelines` config
- **Filtered Access**: `get_providers_for_pipeline()` returns only authorized providers
- **File Conflict Validation**: `_validate_file_conflicts()` prevents overlapping data provider file assignments
- Global singleton access via `get_provider_registry()`

### Provider Types
- **DataProvider** (`src/providers/base/data_provider.py:13`): JSON storage with permission system
  - **Permission Control**: `is_read_only` property, `set_read_only()` method for write protection
  - **File Management**: `managed_files` property, `set_managed_files()` for file-specific access control
  - **Access Validation**: `validate_file_access()`, `_check_write_permission()` methods
- **MediaProvider** (`src/providers/base/media_provider.py:46`): **Configuration injection pattern for media generation services**
  - **Constructor Injection**: `__init__(config)` with fail-fast validation via abstract `validate_config()`
  - **Setup Pattern**: `_setup_from_config()` initializes provider state from validated configuration
  - **Batch Processing**: `generate_batch()` with sequential processing and configurable rate limiting
  - **Core Methods**: `generate_media()`, `get_cost_estimate()`, `supports_type()`, `test_connection()`
  - **Abstract Interface**: Concrete providers implement validation, media generation, and cost estimation
- **SyncProvider** (`src/providers/base/sync_provider.py:47`): Anki, flashcard system integration

## Configuration System (`src/core/config.py:13`)
**Environment-aware settings management**
- JSON-based configuration with `${VAR}` and `${VAR:default}` substitution
- **Named Provider Format**: `providers.{type}.{name}` structure with required `pipelines` field
- **Data Provider Extensions**: Optional `files` array for file-specific assignments, `read_only` boolean for write protection
- Recursive processing of nested dictionaries and lists
- Provider-specific settings via `get_provider()` method
- Graceful degradation for missing configuration files
