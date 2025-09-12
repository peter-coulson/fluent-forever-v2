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
8. **Stage Execution**: Sequential `pipeline.execute_stage()` calls with performance timing

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
**Error Handling**: Provider failures captured in `StageResult.failure()`

### Configuration Flow
- **Load Time**: JSON config → environment substitution → provider initialization
- **Runtime**: `context.config` accessible to all stages
- **Provider Config**: `config.get_provider("forvo")` for service-specific settings
