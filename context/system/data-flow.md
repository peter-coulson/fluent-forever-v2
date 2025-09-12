# Data Flow

## Execution Flow

### CLI Command → Pipeline Execution
1. **CLI Entry**: Command parsing and validation (`src/cli/`)
2. **Logging Setup**: `setup_logging()` with verbose mode and environment configuration
3. **Config Loading**: `Config.load()` with environment variable substitution
4. **Provider Registry**: `ProviderRegistry.from_config()` initializes providers with pipeline assignments
5. **Context Creation**: `PipelineContext` with `project_root`, `pipeline_name`
6. **Provider Filtering**: `registry.get_providers_for_pipeline()` injects only authorized providers
7. **Pipeline Selection**: Concrete pipeline instance (vocabulary/conjugation)
8. **Execution**: Single stage via `pipeline.execute_stage()` or multiple stages via `pipeline.execute_phase()` with performance timing

### Stage Execution Pattern (`src/core/stages.py:104`)
```
Context Validation → Logging Setup → Performance Timing → Stage._execute_impl() → Result Processing → Context Update
```

- **Input**: `PipelineContext` with accumulated data from previous stages
- **Pre-execution**: Context-aware logger created, validation via `stage.validate_context()`
- **Timing Start**: Performance timer started for execution monitoring
- **Core Execution**: `stage._execute_impl(context)` contains actual stage logic
- **Logging**: Success/failure status logged with performance duration and visual icons
- **State Update**: Success → `context.mark_stage_complete()`, failure → `context.add_error()`

### Phase Execution Pattern (`src/core/pipeline.py:49`)
```
Phase Validation → Sequential Stage Execution → Result Aggregation → Fail-Fast Logic → Context Accumulation
```

- **Input**: `PipelineContext` shared across all stages in phase
- **Validation**: Phase name validated against `pipeline.phases` dictionary
- **Sequential Processing**: Each stage in phase executed via `execute_stage()` with shared context
- **Fail-Fast**: Phase stops execution if any stage fails (unless partial success)
- **Result Aggregation**: List of `StageResult` objects returned for analysis
- **Context Efficiency**: Single context instance reused across all phase stages

### Context Management
**Data Accumulation**: Each stage adds data via `context.set(key, value)`
- Stage 1: Load vocabulary → `context.data['words']`
- Stage 2: Fetch audio → `context.data['audio_files']`
- Stage 3: Generate images → `context.data['image_files']`
- Stage N: Sync to Anki → `context.data['anki_cards']`

### Provider Interactions
**Pipeline-Filtered Access**: Only providers assigned to current pipeline via `context.get("providers")`
**Service Calls**: Provider methods called within stage execution using filtered provider dict
**Access Control**: Unauthorized providers not available to pipeline stages
**Permission Enforcement**: Data providers validate file access and read-only permissions on all operations
- Read-only providers reject write operations with `PermissionError`
- File-restricted providers validate access with `ValueError` for unauthorized files
- Permission validation occurs before data operations are attempted
**Error Handling**: Provider failures captured in `StageResult.failure()`

### Configuration Flow
- **Load Time**: JSON config → environment substitution → enhanced provider initialization
- **File Conflict Validation**: Registry validates data provider file assignments during initialization
- **Permission Setup**: Data providers configured with read-only and file access restrictions
- **Runtime**: `context.config` accessible to all stages
- **Provider Config**: `config.get_provider("forvo")` for service-specific settings
