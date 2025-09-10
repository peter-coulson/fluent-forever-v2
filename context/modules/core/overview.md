# Core Module Overview

## Purpose
Core module provides fundamental abstractions for the Fluent Forever V2 pipeline system. Defines base classes, execution context, configuration management, and registry patterns used throughout the application.

## Key Classes

### Pipeline System
- **Pipeline** (`src/core/pipeline.py:11`): Abstract base class for learning workflows
- **PipelineRegistry** (`src/core/registry.py:9`): Registry for managing pipeline implementations
- **Stage** (`src/core/stages.py:81`): Abstract base class for pipeline execution steps

### Data Management
- **PipelineContext** (`src/core/context.py:9`): Execution context for data flow between stages
- **StageResult** (`src/core/stages.py:22`): Result container for stage execution outcomes
- **Config** (`src/core/config.py:13`): Configuration loader with environment variable substitution

### Status & Error Handling
- **StageStatus** (`src/core/stages.py:12`): Enum for stage execution states (SUCCESS, FAILURE, PARTIAL, SKIPPED)
- **Core exceptions** (`src/core/exceptions.py:4-37`): Hierarchy of pipeline, stage, and context errors

## Component Relationships

```
Pipeline -> executes -> Stages -> produce -> StageResults
    ↓                      ↓                     ↓
PipelineContext <- shared data <- StageStatus/Errors
    ↓
Config (provides provider/system settings)
```

## Entry Points

### Working with Pipelines
- Pipeline registration: `PipelineRegistry.register()` (`src/core/registry.py:15`)
- Stage execution: `Pipeline.execute_stage()` (`src/core/pipeline.py:37`)
- Global registry access: `get_pipeline_registry()` (`src/core/registry.py:63`)

### Extending the System
- New pipeline types: Inherit from `Pipeline` abstract class
- New stage types: Inherit from `Stage` abstract class
- Configuration access: `Config.get()` and `Config.get_provider()` methods

### Context Flow
All pipeline execution flows through `PipelineContext` which maintains:
- Stage completion tracking
- Error accumulation
- Shared data between stages
- Configuration and CLI arguments
