# Pipeline Implementations Overview

## Current Status

**No concrete pipeline implementations exist yet** - the pipeline system provides architectural foundation awaiting learning workflow implementations.

## Framework Structure

### Abstract Base Class
- **Pipeline interface** defined in `src/core/pipeline.py`
- **Required properties**: `name`, `display_name`, `stages`, `data_file`, `anki_note_type`
- **Abstract methods**: `get_stage()`, `validate_cli_args()`, `populate_context_from_cli()`

### Registry System
- **Central registration** via `PipelineRegistry` in `src/core/registry.py`
- **Discovery methods**: `list_pipelines()`, `get_pipeline_info()`, `has_pipeline()`
- **Global access**: Singleton pattern via `get_pipeline_registry()`

## Expected Learning Workflows

### Vocabulary Pipeline Pattern
- **Data source**: `vocabulary.json` file format
- **Stage sequence**: prepare → media → sync workflow
- **Anki integration**: Custom note type for vocabulary cards
- **CLI arguments**: `--words` for prepare, `--cards` for media stages

### Conjugation Pipeline Pattern
- **Data source**: Conjugation-specific data files
- **Stage sequence**: Similar multi-stage approach for verb learning
- **Anki integration**: Verb conjugation note type
- **CLI arguments**: Verb-specific parameters for conjugation practice

See `context/workflows/extending.md` for pipeline implementation guidelines.
