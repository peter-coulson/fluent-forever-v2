# CLI Commands Implementation

## Command Architecture

Commands implemented as classes following command pattern. Each command receives registries and config in constructor, executes via `execute(args)` method returning exit codes (0=success, 1=error).

## Run Command (`src/cli/commands/run_command.py`)

### Core Functionality
- **Purpose**: Execute specific pipeline stages with full context setup
- **Key Method**: `execute(args)` - Main execution coordinator
- **Context Creation**: `_create_context()` builds `PipelineContext` with providers and configuration

### Execution Flow
1. **Validation**: `validate_arguments()` for CLI args, `pipeline.validate_cli_args()` for pipeline-specific args
2. **Context Setup**: Creates context with providers, project root, config, and args
3. **Pipeline Integration**: `pipeline.populate_context_from_cli()` adds pipeline-specific data
4. **Stage Execution**: Delegates to `pipeline.execute_stage()` with prepared context

### Dry-run Functionality
- **Activation**: `--dry-run` flag skips validation and execution
- **Preview**: `pipeline.show_cli_execution_plan()` displays planned operations
- **Safety**: Prevents accidental execution of destructive operations

### Context Creation (`_create_context()`)
```python
# Key components injected into context
context = PipelineContext(
    pipeline_name=args.pipeline,
    project_root=self.project_root,
    config=self.config.to_dict(),
    args=vars(args)
)

# Provider injection
providers = {
    "data": provider_registry.get_data_provider("default"),
    "audio": provider_registry.get_audio_provider("default"),
    "image": provider_registry.get_image_provider("default"),
    "sync": provider_registry.get_sync_provider("default")
}
```

## Info Command (`src/cli/commands/info_command.py`)

### Core Functionality
- **Purpose**: Display pipeline metadata and stage information
- **Data Source**: `registry.get_pipeline_info()` for basic info, pipeline instances for detailed stage info

### Output Modes
- **Basic Info**: Pipeline name, display name, description, data file, Anki note type
- **Stage Info**: With `--stages` flag, shows stage names, display names, dependencies

### Information Display
- **Metadata**: Key-value pairs using `format_key_value_pairs()`
- **Stage List**: Simple list or detailed per-stage information
- **Error Handling**: Graceful fallbacks for missing stage information

### Implementation Details
```python
# Basic pipeline information structure
info = {
    "name": pipeline.name,
    "display_name": pipeline.display_name,
    "description": pipeline.get_description(),
    "stages": pipeline.stages,
    "data_file": pipeline.data_file,
    "anki_note_type": pipeline.anki_note_type
}
```

## List Command (`src/cli/commands/list_command.py`)

### Core Functionality
- **Purpose**: Enumerate and describe available pipelines
- **Data Source**: `registry.list_pipelines()` for names, `registry.get_pipeline_info()` for details

### Display Modes
- **Simple Mode**: Pipeline names with brief descriptions
- **Detailed Mode**: Table format with name, display name, stage count, Anki note type, data file

### Table Formatting
- **Headers**: Name, Display Name, Stages, Anki Note Type, Data File
- **Data Extraction**: Pulls info from registry, handles missing data gracefully
- **Formatting**: Uses `format_table()` utility for aligned output

## Command Argument Patterns

### Global Arguments
- `--config`: Custom configuration file path
- `--verbose`: Enable verbose output
- `--dry-run`: Preview mode without execution

### Command-Specific Arguments
- **run**: `pipeline`, `--stage`, command arguments passed through to pipeline
- **info**: `pipeline`, `--stages` for detailed stage information
- **list**: `--detailed` for table format output

## Error Handling Strategy

### Validation Errors
- **Pre-execution**: CLI argument validation before expensive operations
- **Pipeline-specific**: Each pipeline validates its required arguments
- **User Feedback**: Clear error messages with actionable guidance

### Execution Errors
- **Exception Wrapping**: Catch and re-present errors with context
- **Status Code Mapping**: Pipeline result status to shell exit codes
- **Progress Feedback**: Success/warning/error icons with descriptive messages

## Extension Patterns

### Adding New Commands
1. Create command class in `src/cli/commands/`
2. Implement `execute(args)` method
3. Add argument parser in `src/cli/pipeline_runner.py:create_parser()`
4. Add execution branch in `main()`

### Command Integration Points
- **Registry Access**: All commands receive pipeline and provider registries
- **Configuration**: Access to system configuration via constructor
- **Validation**: Leverage `src/cli/utils/validation.py` utilities
- **Output**: Use `src/cli/utils/output.py` for consistent formatting
