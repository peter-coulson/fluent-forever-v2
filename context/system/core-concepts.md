# Core Concepts

## Essential Abstractions

### Pipeline (`src/core/pipeline.py:11`)
**Abstract workflow orchestrator**
- Properties: `name`, `display_name`, `stages`, `data_file`, `anki_note_type`
- Methods: `execute_stage()`, `get_stage()`, `validate_cli_args()`
- Manages stage execution order and context validation
- Concrete implementations define vocabulary/conjugation workflows

### Stage (`src/core/stages.py:81`)
**Individual processing unit**
- Properties: `name`, `display_name`, `dependencies`
- Methods: `execute()`, `validate_context()`
- Returns `StageResult` with status (SUCCESS/FAILURE/PARTIAL/SKIPPED)
- Base classes: `APIStage`, `ValidationStage`, `FileStage`

### PipelineContext (`src/core/context.py:8`)
**Runtime state container**
- Core: `pipeline_name`, `project_root`
- Data: `data` dict modified by stages, `config` dict
- Tracking: `completed_stages`, `errors`, CLI `args`
- Methods: `get()`, `set()`, `add_error()`, `mark_stage_complete()`

### Provider (`src/providers/registry.py:18`)
**External service abstraction**
- Types: `DataProvider`, `MediaProvider`, `SyncProvider`
- Registry pattern for discovery: `get_audio_provider()`, `get_sync_provider()`
- Factory method: `ProviderRegistry.from_config()`
- Concrete: JSONDataProvider, ForvoProvider, AnkiProvider, RunwareProvider

### Configuration
**Environment-aware settings** (`src/core/config.py:13`)
- JSON-based with `${VAR}` or `${VAR:default}` substitution
- Dot notation access: `config.get("providers.audio.type")`
- Provider-specific: `get_provider()`, `get_system_settings()`
