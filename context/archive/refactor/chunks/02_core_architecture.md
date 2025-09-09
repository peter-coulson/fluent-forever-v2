# Session 2: Core Architecture

## Mission
Create the fundamental pipeline architecture and registry system that will serve as the foundation for all card types.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/chunks/01_validation_gates.md` - Validation gate approach
- `tests/validation_gates/test_session2_core.py` - Validation gate for this session
- `src/utils/card_types.py` - Current card type system to evolve

## Objectives

### Primary Goal
Build the core pipeline system that enables any card type to define its complete processing workflow through a consistent interface.

### Target Architecture
```
src/
├── core/
│   ├── __init__.py
│   ├── pipeline.py              # Abstract pipeline definition
│   ├── stages.py               # Stage base classes and interfaces
│   ├── registry.py             # Pipeline registry system
│   ├── context.py              # Pipeline execution context
│   └── exceptions.py           # Core exception hierarchy
└── cli/
    ├── __init__.py
    ├── pipeline_runner.py       # Universal CLI entry point
    └── base_commands.py         # Base command classes
```

## Implementation Requirements

### 1. Pipeline Abstraction (`src/core/pipeline.py`)

Create the fundamental pipeline interface:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

class Pipeline(ABC):
    """Abstract base class for all card type pipelines"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Pipeline identifier (e.g., 'vocabulary', 'conjugation')"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable pipeline name"""
        pass

    @property
    @abstractmethod
    def stages(self) -> List[str]:
        """List of available stage names for this pipeline"""
        pass

    @abstractmethod
    def get_stage(self, stage_name: str) -> 'Stage':
        """Get a stage instance by name"""
        pass

    @abstractmethod
    def execute_stage(self, stage_name: str, context: 'PipelineContext') -> 'StageResult':
        """Execute a specific stage with context"""
        pass

    @property
    @abstractmethod
    def data_file(self) -> str:
        """Primary data file for this pipeline (e.g., 'vocabulary.json')"""
        pass

    @property
    @abstractmethod
    def anki_note_type(self) -> str:
        """Anki note type name for this pipeline"""
        pass
```

### 2. Stage System (`src/core/stages.py`)

Define the stage interface and base classes:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class StageStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"

@dataclass
class StageResult:
    status: StageStatus
    message: str
    data: Dict[str, Any]
    errors: List[str]

class Stage(ABC):
    """Abstract base class for pipeline stages"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stage identifier"""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable stage name"""
        pass

    @abstractmethod
    def execute(self, context: 'PipelineContext') -> StageResult:
        """Execute this stage with the given context"""
        pass

    @property
    def dependencies(self) -> List[str]:
        """List of stage names that must complete before this stage"""
        return []

    def validate_context(self, context: 'PipelineContext') -> List[str]:
        """Validate context has required data. Return list of errors."""
        return []
```

### 3. Pipeline Context (`src/core/context.py`)

Create execution context for pipelines:

```python
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class PipelineContext:
    """Execution context passed between pipeline stages"""

    # Core context
    pipeline_name: str
    project_root: Path

    # Stage data (modified by stages during execution)
    data: Dict[str, Any] = field(default_factory=dict)

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    completed_stages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Command arguments
    args: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get data value with default"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set data value"""
        self.data[key] = value

    def add_error(self, error: str) -> None:
        """Add error to context"""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if context has errors"""
        return len(self.errors) > 0
```

### 4. Registry System (`src/core/registry.py`)

Enhanced registry supporting full pipelines:

```python
from typing import Dict, List, Optional
from .pipeline import Pipeline
from .exceptions import PipelineNotFoundError, PipelineAlreadyRegisteredError

class PipelineRegistry:
    """Registry for managing pipeline implementations"""

    def __init__(self):
        self._pipelines: Dict[str, Pipeline] = {}

    def register(self, pipeline: Pipeline) -> None:
        """Register a pipeline"""
        if pipeline.name in self._pipelines:
            raise PipelineAlreadyRegisteredError(f"Pipeline '{pipeline.name}' already registered")

        self._pipelines[pipeline.name] = pipeline

    def get(self, name: str) -> Pipeline:
        """Get pipeline by name"""
        if name not in self._pipelines:
            raise PipelineNotFoundError(f"Pipeline '{name}' not found")

        return self._pipelines[name]

    def list_pipelines(self) -> List[str]:
        """List all registered pipeline names"""
        return list(self._pipelines.keys())

    def has_pipeline(self, name: str) -> bool:
        """Check if pipeline is registered"""
        return name in self._pipelines

# Global registry instance
_global_registry = PipelineRegistry()

def get_pipeline_registry() -> PipelineRegistry:
    """Get the global pipeline registry"""
    return _global_registry
```

### 5. Exception Hierarchy (`src/core/exceptions.py`)

Define core exceptions:

```python
class PipelineError(Exception):
    """Base exception for all pipeline errors"""
    pass

class PipelineNotFoundError(PipelineError):
    """Pipeline not found in registry"""
    pass

class PipelineAlreadyRegisteredError(PipelineError):
    """Pipeline already registered"""
    pass

class StageError(PipelineError):
    """Stage execution error"""
    pass

class StageNotFoundError(StageError):
    """Stage not found in pipeline"""
    pass

class ContextValidationError(PipelineError):
    """Pipeline context validation error"""
    pass
```

### 6. Basic CLI Framework (`src/cli/pipeline_runner.py`)

Universal CLI entry point:

```python
#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from core.registry import get_pipeline_registry
from core.context import PipelineContext
from core.exceptions import PipelineError
from utils.logging_config import setup_logging, ICONS

def create_base_parser() -> argparse.ArgumentParser:
    """Create base argument parser"""
    parser = argparse.ArgumentParser(
        description='Universal pipeline runner for card creation workflows'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List available pipelines')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show pipeline information')
    info_parser.add_argument('pipeline', help='Pipeline name')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run pipeline stage')
    run_parser.add_argument('pipeline', help='Pipeline name')
    run_parser.add_argument('--stage', required=True, help='Stage to execute')
    run_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    run_parser.add_argument('--config', help='Override config file')

    return parser

def main() -> int:
    """Main CLI entry point"""
    setup_logging()
    logger = setup_logging().getChild('cli.pipeline_runner')

    parser = create_base_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    registry = get_pipeline_registry()
    project_root = Path(__file__).parents[2]

    try:
        if args.command == 'list':
            return cmd_list(registry)
        elif args.command == 'info':
            return cmd_info(registry, args.pipeline)
        elif args.command == 'run':
            return cmd_run(registry, args.pipeline, args.stage, project_root, args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

    except PipelineError as e:
        logger.error(f"{ICONS['cross']} {e}")
        return 1
    except Exception as e:
        logger.error(f"{ICONS['cross']} Unexpected error: {e}")
        return 1

def cmd_list(registry: 'PipelineRegistry') -> int:
    """List available pipelines"""
    # Implementation details...
    pass

def cmd_info(registry: 'PipelineRegistry', pipeline_name: str) -> int:
    """Show pipeline information"""
    # Implementation details...
    pass

def cmd_run(registry: 'PipelineRegistry', pipeline_name: str, stage_name: str,
           project_root: Path, args) -> int:
    """Run pipeline stage"""
    # Implementation details...
    pass

if __name__ == '__main__':
    raise SystemExit(main())
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/01_core_architecture/` pass
- [ ] Pipeline registry functionality works as specified
- [ ] Basic pipeline execution patterns work
- [ ] Pipeline interface compliance is enforced

### Implementation Quality
- [ ] All abstract base classes defined with clear interfaces
- [ ] Registry supports pipeline registration and discovery
- [ ] Context system allows data flow between stages
- [ ] Exception hierarchy provides clear error handling
- [ ] CLI framework has consistent command structure

### Code Quality
- [ ] Type hints on all public interfaces
- [ ] Docstrings on all classes and methods
- [ ] Clear error messages with actionable information
- [ ] Logging integrated throughout

## Deliverables

### 1. Core Architecture Implementation
- Complete `src/core/` module with all components
- Basic `src/cli/` framework for universal commands
- Integration with existing logging and utilities

### 2. Unit Tests
- Comprehensive unit tests for all core components
- Mock-based testing for external dependencies
- Error handling and edge case coverage

### 3. Documentation Updates
- Update docstrings and type hints throughout
- Add examples of pipeline implementation
- Document extension points for new pipelines

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/02_core_architecture_handoff.md` with:
- Overview of implemented architecture
- Key design decisions and trade-offs
- Extension points for future sessions
- Any implementation challenges or solutions
- Guidance for implementing the stage system

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All Session 1 E2E tests continue to pass
2. ✅ All Session 2 E2E tests pass
3. ✅ Unit test coverage >90% for all core components
4. ✅ CLI framework can list and inspect (mock) pipelines
5. ✅ Registry system works with basic pipeline implementations

### Quality Validation
- Pipeline interface is clean and extensible
- Context system supports data flow requirements
- Error handling provides clear debugging information
- CLI follows consistent patterns for all commands

## Notes for Implementation

### Integration Points
- Extend existing `utils/card_types.py` functionality
- Integrate with existing logging configuration
- Maintain compatibility with current project structure

### Design Principles
- **Interface Segregation** - Clean, focused interfaces
- **Dependency Inversion** - Abstract external dependencies
- **Open/Closed** - Extensible without modification
- **Fail Fast** - Clear error messages at boundaries

---

**Remember: This session creates the foundation that all future card types will build on. Focus on clean interfaces and extensible design.**
