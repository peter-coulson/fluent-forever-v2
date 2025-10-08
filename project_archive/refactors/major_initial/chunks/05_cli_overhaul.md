# Session 5: CLI Overhaul

## Mission
Replace all hardcoded CLI scripts with a universal pipeline runner that provides consistent commands for all card types.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/04_provider_system_handoff.md` - Provider system context
- `tests/e2e/04_cli_system/` - Validation gates for this session
- `src/cli/` - Current CLI scripts to replace
- `src/core/`, `src/stages/`, `src/providers/` - Previous implementations

## Objectives

### Primary Goal
Create a unified CLI experience where all pipelines use consistent command patterns and all existing functionality is accessible through the new system.

### Target CLI Experience
```bash
# Pipeline discovery
python -m cli.pipeline list
python -m cli.pipeline info vocabulary

# Stage execution (replaces all current scripts)
python -m cli.pipeline run vocabulary --stage prepare_batch --words por,para
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/batch.json
python -m cli.pipeline run vocabulary --stage generate_media --cards card1,card2
python -m cli.pipeline run vocabulary --stage sync_anki --execute

# Universal commands
python -m cli.pipeline preview vocabulary --card-id lo_neuter_article
python -m cli.pipeline preview conjugation --card-id hablar_present_yo
```

### Target Architecture
```
src/
├── cli/
│   ├── __init__.py
│   ├── pipeline_runner.py       # Main CLI entry point (enhance from Session 2)
│   ├── commands/                # Command implementations
│   │   ├── __init__.py
│   │   ├── list_command.py     # Pipeline discovery
│   │   ├── info_command.py     # Pipeline information
│   │   ├── run_command.py      # Stage execution
│   │   └── preview_command.py  # Preview functionality
│   ├── config/                 # CLI configuration
│   │   ├── __init__.py
│   │   └── cli_config.py       # CLI-specific configuration
│   └── utils/                  # CLI utilities
│       ├── __init__.py
│       ├── output.py          # Consistent output formatting
│       └── validation.py      # Command validation
```

## Implementation Requirements

### 1. Enhanced Pipeline Runner (`src/cli/pipeline_runner.py`)

Expand the basic runner from Session 2:

```python
#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
Replaces all hardcoded CLI scripts with unified command structure.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from core.registry import get_pipeline_registry
from providers.registry import get_provider_registry
from core.context import PipelineContext
from cli.commands import ListCommand, InfoCommand, RunCommand, PreviewCommand
from cli.config.cli_config import CLIConfig
from utils.logging_config import setup_logging

def create_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser"""
    parser = argparse.ArgumentParser(
        description='Universal pipeline runner for card creation workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discovery
  %(prog)s list
  %(prog)s info vocabulary

  # Execution
  %(prog)s run vocabulary --stage prepare_batch --words por,para
  %(prog)s run vocabulary --stage sync_anki --execute

  # Preview
  %(prog)s preview vocabulary --card-id lo_neuter_article
        """
    )

    # Global options
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List available pipelines')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed info')

    # Info command
    info_parser = subparsers.add_parser('info', help='Show pipeline information')
    info_parser.add_argument('pipeline', help='Pipeline name')
    info_parser.add_argument('--stages', action='store_true', help='Show available stages')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run pipeline stage')
    run_parser.add_argument('pipeline', help='Pipeline name')
    run_parser.add_argument('--stage', required=True, help='Stage to execute')

    # Common run arguments (extract from existing scripts)
    run_parser.add_argument('--words', help='Comma-separated word list')
    run_parser.add_argument('--cards', help='Comma-separated card IDs')
    run_parser.add_argument('--file', help='Input file path')
    run_parser.add_argument('--execute', action='store_true', help='Execute changes')
    run_parser.add_argument('--no-images', action='store_true', help='Skip image generation')
    run_parser.add_argument('--no-audio', action='store_true', help='Skip audio generation')

    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview cards')
    preview_parser.add_argument('pipeline', help='Pipeline name')
    preview_parser.add_argument('--card-id', help='Card ID to preview')
    preview_parser.add_argument('--port', type=int, default=8000, help='Preview server port')
    preview_parser.add_argument('--start-server', action='store_true', help='Start preview server')

    return parser

def main() -> int:
    """Main CLI entry point"""
    setup_logging()

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load configuration
    config = CLIConfig.load(args.config)

    # Setup registries
    pipeline_registry = get_pipeline_registry()
    provider_registry = get_provider_registry()

    # Initialize providers from config
    config.initialize_providers(provider_registry)

    project_root = Path(__file__).parents[2]

    try:
        # Execute command
        if args.command == 'list':
            command = ListCommand(pipeline_registry, config)
            return command.execute(args)
        elif args.command == 'info':
            command = InfoCommand(pipeline_registry, config)
            return command.execute(args)
        elif args.command == 'run':
            command = RunCommand(pipeline_registry, provider_registry, project_root, config)
            return command.execute(args)
        elif args.command == 'preview':
            command = PreviewCommand(pipeline_registry, provider_registry, project_root, config)
            return command.execute(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
```

### 2. Command Implementations (`src/cli/commands/`)

#### List Command (`list_command.py`)
```python
from typing import List
from core.registry import PipelineRegistry
from cli.config.cli_config import CLIConfig
from cli.utils.output import format_table, print_success

class ListCommand:
    """List available pipelines"""

    def __init__(self, registry: PipelineRegistry, config: CLIConfig):
        self.registry = registry
        self.config = config

    def execute(self, args) -> int:
        """Execute list command"""
        pipelines = self.registry.list_pipelines()

        if not pipelines:
            print("No pipelines registered")
            return 0

        if args.detailed:
            return self._list_detailed(pipelines)
        else:
            return self._list_simple(pipelines)

    def _list_simple(self, pipelines: List[str]) -> int:
        """Simple pipeline listing"""
        print("Available pipelines:")
        for pipeline in pipelines:
            print(f"  - {pipeline}")
        return 0

    def _list_detailed(self, pipelines: List[str]) -> int:
        """Detailed pipeline listing"""
        rows = []
        for pipeline_name in pipelines:
            pipeline = self.registry.get(pipeline_name)
            rows.append([
                pipeline_name,
                pipeline.display_name,
                len(pipeline.stages),
                pipeline.anki_note_type
            ])

        headers = ['Name', 'Display Name', 'Stages', 'Anki Note Type']
        print(format_table(headers, rows))
        return 0
```

#### Info Command (`info_command.py`)
```python
class InfoCommand:
    """Show pipeline information"""

    def execute(self, args) -> int:
        """Execute info command"""
        try:
            pipeline = self.registry.get(args.pipeline)
        except Exception as e:
            print(f"Error: {e}")
            return 1

        print(f"Pipeline: {pipeline.name}")
        print(f"Display Name: {pipeline.display_name}")
        print(f"Data File: {pipeline.data_file}")
        print(f"Anki Note Type: {pipeline.anki_note_type}")

        if args.stages:
            print(f"\nAvailable Stages:")
            for stage_name in pipeline.stages:
                stage = pipeline.get_stage(stage_name)
                print(f"  - {stage_name}: {stage.display_name}")

        return 0
```

#### Run Command (`run_command.py`)
```python
from pathlib import Path
from core.registry import PipelineRegistry
from providers.registry import ProviderRegistry
from core.context import PipelineContext

class RunCommand:
    """Execute pipeline stages"""

    def __init__(self, pipeline_registry: PipelineRegistry,
                 provider_registry: ProviderRegistry,
                 project_root: Path, config: CLIConfig):
        self.pipeline_registry = pipeline_registry
        self.provider_registry = provider_registry
        self.project_root = project_root
        self.config = config

    def execute(self, args) -> int:
        """Execute run command"""
        try:
            pipeline = self.pipeline_registry.get(args.pipeline)
        except Exception as e:
            print(f"Error: Pipeline '{args.pipeline}' not found")
            return 1

        # Create execution context
        context = PipelineContext(
            pipeline_name=args.pipeline,
            project_root=self.project_root,
            config=self.config.to_dict(),
            args=vars(args)
        )

        # Add providers to context
        context.set('providers', {
            'data': self.provider_registry.get_data_provider('default'),
            'media': self.provider_registry.get_media_provider('default'),
            'sync': self.provider_registry.get_sync_provider('default')
        })

        # Parse command arguments into context
        self._populate_context(context, args)

        # Execute stage
        try:
            result = pipeline.execute_stage(args.stage, context)

            if result.status.success:
                print(f"✅ {result.message}")
                return 0
            else:
                print(f"❌ {result.message}")
                for error in result.errors:
                    print(f"  - {error}")
                return 1

        except Exception as e:
            print(f"Error executing stage '{args.stage}': {e}")
            return 1

    def _populate_context(self, context: PipelineContext, args) -> None:
        """Populate context from command arguments"""
        if args.words:
            context.set('words', [w.strip() for w in args.words.split(',')])
        if args.cards:
            context.set('cards', [c.strip() for c in args.cards.split(',')])
        if args.file:
            context.set('input_file', Path(args.file))

        # Set execution flags
        context.set('execute', args.execute)
        context.set('skip_images', args.no_images)
        context.set('skip_audio', args.no_audio)
        context.set('dry_run', args.dry_run)
```

#### Preview Command (`preview_command.py`)
```python
class PreviewCommand:
    """Preview card functionality"""

    def execute(self, args) -> int:
        """Execute preview command"""
        if args.start_server:
            return self._start_preview_server(args)
        elif args.card_id:
            return self._preview_card(args)
        else:
            print("Error: Must specify --card-id or --start-server")
            return 1

    def _start_preview_server(self, args) -> int:
        """Start multi-card preview server"""
        from cli.preview_server_multi import create_app

        app = create_app()
        print(f"Starting preview server on http://127.0.0.1:{args.port}")
        app.run(host='127.0.0.1', port=args.port, debug=True)
        return 0

    def _preview_card(self, args) -> int:
        """Open specific card in browser"""
        import webbrowser
        url = f"http://127.0.0.1:8000/preview?card_id={args.card_id}&card_type={args.pipeline}"
        webbrowser.open(url)
        print(f"Opening {url}")
        return 0
```

### 3. CLI Configuration (`src/cli/config/cli_config.py`)

```python
import json
from pathlib import Path
from typing import Dict, Any, Optional
from providers.registry import ProviderRegistry

class CLIConfig:
    """CLI configuration management"""

    def __init__(self, config_data: Dict[str, Any]):
        self.data = config_data

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'CLIConfig':
        """Load configuration from file or defaults"""
        if config_path:
            path = Path(config_path)
        else:
            # Look for config in standard locations
            candidates = [
                Path.cwd() / 'config.json',
                Path.home() / '.fluent-forever' / 'config.json'
            ]
            path = next((p for p in candidates if p.exists()), None)

        if path and path.exists():
            return cls(json.loads(path.read_text()))
        else:
            return cls(cls._default_config())

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Default CLI configuration"""
        return {
            'providers': {
                'data': {'type': 'json', 'base_path': '.'},
                'media': {'type': 'openai'},
                'sync': {'type': 'anki'}
            },
            'output': {
                'format': 'table',
                'verbose': False
            }
        }

    def initialize_providers(self, registry: ProviderRegistry) -> None:
        """Initialize providers from configuration"""
        # Create and register providers based on config
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.data.copy()
```

### 4. CLI Utilities (`src/cli/utils/`)

#### Output Formatting (`output.py`)
```python
from typing import List, Dict, Any

def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Format data as a table"""
    if not rows:
        return "No data"

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    # Create format string
    format_str = "  ".join(f"{{:<{w}}}" for w in widths)

    # Build table
    lines = [format_str.format(*headers)]
    lines.append("  ".join("-" * w for w in widths))

    for row in rows:
        lines.append(format_str.format(*[str(cell) for cell in row]))

    return "\n".join(lines)

def print_success(message: str) -> None:
    """Print success message with icon"""
    print(f"✅ {message}")

def print_error(message: str) -> None:
    """Print error message with icon"""
    print(f"❌ {message}")

def print_warning(message: str) -> None:
    """Print warning message with icon"""
    print(f"⚠️ {message}")
```

## Script Migration Mapping

Map existing CLI scripts to new commands:

```bash
# OLD → NEW
python -m cli.prepare_claude_batch --words por,para
→ python -m cli.pipeline run vocabulary --stage prepare_batch --words por,para

python -m cli.ingest_claude_batch --input staging/batch.json
→ python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/batch.json

python -m cli.media_generate --cards card1,card2 --execute
→ python -m cli.pipeline run vocabulary --stage generate_media --cards card1,card2 --execute

python -m cli.sync_anki_all
→ python -m cli.pipeline run vocabulary --stage sync_anki --execute

python -m cli.preview_server --port 8001
→ python -m cli.pipeline preview vocabulary --start-server --port 8001
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/04_cli_system/` pass
- [ ] Universal pipeline runner works correctly
- [ ] Command discovery functions properly
- [ ] All existing CLI functionality accessible through new commands

### Backward Compatibility
- [ ] All existing CLI operations can be performed with new commands
- [ ] Command output maintains useful information
- [ ] Error handling provides clear guidance
- [ ] Help system is comprehensive

### Code Quality
- [ ] Consistent command structure across all operations
- [ ] Clear error messages with actionable information
- [ ] Comprehensive argument validation
- [ ] Clean separation between CLI and business logic

## Deliverables

### 1. Universal CLI System
- Complete pipeline runner with all commands
- Command implementations for all operations
- CLI configuration system
- Output formatting utilities

### 2. Script Migration
- All existing CLI functionality available through new system
- Clear mapping documentation
- Consistent command patterns
- Preserved functionality

### 3. Unit Tests
- Unit tests for all CLI commands
- Mock-based testing for pipeline interactions
- Error handling and edge case coverage
- Command validation tests

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/05_cli_overhaul_handoff.md` with:
- Overview of new CLI system
- Command mapping from old to new
- Configuration system capabilities
- Extension points for new commands
- Guidance for configuration refactor session

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 5 E2E tests pass
3. ✅ All existing CLI functionality accessible through new commands
4. ✅ Command system is consistent and extensible
5. ✅ Error handling provides clear debugging information

### Quality Validation
- CLI commands are intuitive and consistent
- All existing workflows can be completed with new commands
- Error messages provide actionable guidance
- Help system is comprehensive and useful

## Notes for Implementation

### Migration Strategy
- Implement new CLI system alongside existing scripts
- Verify each command provides equivalent functionality
- Test all argument combinations and edge cases
- Maintain output format compatibility where practical

### Design Principles
- **Consistency** - All commands follow same patterns
- **Discoverability** - Easy to find available options
- **Extensibility** - Easy to add new commands and options
- **Usability** - Clear, actionable error messages

---

**Remember: This CLI system will be the primary user interface. Focus on consistency, discoverability, and clear error messages.**
