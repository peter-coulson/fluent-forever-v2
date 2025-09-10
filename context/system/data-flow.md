# Data Flow

## Execution Flow

### CLI Command → Pipeline Execution
1. **CLI Entry**: Command parsing and validation (`src/cli/`)
2. **Config Loading**: `Config.load()` with environment variable substitution
3. **Provider Registry**: `ProviderRegistry.from_config()` initializes providers
4. **Context Creation**: `PipelineContext` with `project_root`, `pipeline_name`
5. **Pipeline Selection**: Concrete pipeline instance (vocabulary/conjugation)
6. **Stage Execution**: Sequential `pipeline.execute_stage()` calls

### Stage Execution Pattern (`src/core/pipeline.py:37`)
```
Context Validation → Stage.execute() → Result Processing → Context Update
```

- **Input**: `PipelineContext` with accumulated data from previous stages
- **Validation**: `stage.validate_context()` checks required data/dependencies
- **Execution**: `stage.execute(context)` returns `StageResult`
- **State Update**: Success → `context.mark_stage_complete()`, failure → `context.add_error()`

### Context Management
**Data Accumulation**: Each stage adds data via `context.set(key, value)`
- Stage 1: Load vocabulary → `context.data['words']`
- Stage 2: Fetch audio → `context.data['audio_files']`
- Stage 3: Generate images → `context.data['image_files']`
- Stage N: Sync to Anki → `context.data['anki_cards']`

### Provider Interactions
**Registry Lookup**: `registry.get_audio_provider("default")`
**Service Calls**: Provider methods called within stage execution
**Error Handling**: Provider failures captured in `StageResult.failure()`

### Configuration Flow
- **Load Time**: JSON config → environment substitution → provider initialization
- **Runtime**: `context.config` accessible to all stages
- **Provider Config**: `config.get_provider("forvo")` for service-specific settings
