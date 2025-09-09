# Adding New Pipelines

Learn how to extend the system with new card types using the pipeline-centric architecture.

## Overview

Adding a new pipeline involves:
1. **Pipeline Implementation**: Core pipeline class with CLI integration methods
2. **Stage Development**: Custom stages for your card type
3. **CLI Integration**: Implement validation, context population, and dry-run display
4. **Registration**: Auto-registration with the system
5. **Testing**: Comprehensive test coverage

## Quick Start Template

### 1. Create Pipeline Structure

```
src/pipelines/your_pipeline/
├── your_pipeline.py          # Main pipeline class
├── stages/                   # Pipeline-specific stages
│   ├── __init__.py
│   ├── analysis_stage.py     # Custom analysis logic
│   └── generation_stage.py   # Custom generation logic
├── data/                     # Data management
│   └── data_manager.py       # Data operations
└── validation/               # Validation logic
    └── validator.py          # Card validation
```

### 2. Basic Pipeline Implementation

```python
# src/pipelines/your_pipeline/your_pipeline.py

from typing import Any
from pathlib import Path

from src.core.pipeline import Pipeline
from src.core.context import PipelineContext
from src.core.stages import Stage


class YourPipeline(Pipeline):
    """Your pipeline implementation."""

    @property
    def name(self) -> str:
        return "your_pipeline"

    @property
    def display_name(self) -> str:
        return "Your Pipeline"

    @property
    def stages(self) -> list[str]:
        return ["analysis", "generation", "sync"]

    @property
    def data_file(self) -> str:
        return "your_data.json"

    @property
    def anki_note_type(self) -> str:
        return "Your Pipeline"

    def get_stage(self, stage_name: str) -> Stage:
        """Get stage implementation by name."""
        if stage_name == "analysis":
            from .stages.analysis_stage import YourAnalysisStage
            return YourAnalysisStage()
        elif stage_name == "generation":
            from .stages.generation_stage import YourGenerationStage
            return YourGenerationStage()
        elif stage_name == "sync":
            from src.stages.sync.anki_sync_stage import AnkiSyncStage
            return AnkiSyncStage()
        else:
            raise StageNotFoundError(f"Stage '{stage_name}' not found in {self.name}")

    def validate_cli_args(self, args: Any) -> list[str]:
        """Validate CLI arguments specific to this pipeline."""
        errors = []

        # Example validation
        if args.stage == "analysis" and not getattr(args, "input_data", None):
            errors.append("--input-data is required for analysis stage")

        return errors

    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        """Populate context from CLI arguments."""
        # Parse your pipeline-specific CLI arguments
        if getattr(args, "input_data", None):
            data_items = [item.strip() for item in args.input_data.split(",") if item.strip()]
            context.set("input_items", data_items)

        # Common flags
        context.set("execute", getattr(args, "execute", False))
        context.set("skip_images", getattr(args, "no_images", False))
        context.set("skip_audio", getattr(args, "no_audio", False))
        context.set("force_regenerate", getattr(args, "force_regenerate", False))

    def show_cli_execution_plan(self, context: PipelineContext, args: Any) -> None:
        """Show execution plan for dry run."""
        print("\nExecution Plan:")
        print(f"  Pipeline: {self.display_name}")
        print(f"  Stage: {args.stage}")

        if context.get("input_items"):
            print(f"  Input items: {', '.join(context.get('input_items'))}")

        # Show relevant flags
        flags = []
        if context.get("execute"):
            flags.append("execute")
        if context.get("skip_images"):
            flags.append("skip-images")
        if context.get("skip_audio"):
            flags.append("skip-audio")
        if context.get("force_regenerate"):
            flags.append("force-regenerate")

        if flags:
            print(f"  Flags: {', '.join(flags)}")

        print()  # Empty line for readability
```

### 3. Create Configuration

```json
// config/pipelines/your_pipeline.json
{
  "name": "your_pipeline",
  "description": "Your Pipeline Description",
  "data_file": "your_data.json",
  "settings": {
    "max_cards_per_batch": 10
  },
  "anki": {
    "note_type": "Your Pipeline",
    "deck_name": "Your Pipeline::Cards"
  },
  "media": {
    "generate_images": true,
    "generate_audio": true
  }
}
```

### 4. Register Pipeline

Add your pipeline to auto-registration:

```python
# src/pipelines/__init__.py

def register_all_pipelines():
    from .vocabulary.vocabulary_pipeline import VocabularyPipeline
    from .conjugation.conjugation_pipeline import ConjugationPipeline
    from .your_pipeline.your_pipeline import YourPipeline  # Add this
    # Registration happens automatically through imports
```

### 5. Test Your Pipeline

```bash
# Discover your pipeline
python -m cli.pipeline list

# Get information
python -m cli.pipeline info your_pipeline

# Execute stages
python -m cli.pipeline run your_pipeline --stage your_analysis --input-data item1,item2
```

## Advanced Features

### Custom Stages

```python
from src.core.stage import Stage
from src.core.context import Context

class CustomAnalysisStage(Stage):

    def execute(self, context: Context) -> Context:
        """Implement your custom analysis logic"""
        input_data = context.get('input_data')

        # Your processing logic here
        processed_data = self._process(input_data)

        context.set('analyzed_data', processed_data)
        return context
```

### Resource Isolation

Your pipeline automatically gets:
- **Isolated media paths**: `media/your_pipeline/`
- **Separate data files**: `your_data.json`
- **Independent configuration**: `config/pipelines/your_pipeline.json`
- **Template isolation**: `templates/anki/your_pipeline/`

### CLI Integration

Your pipeline automatically supports:
- **Discovery**: `python -m cli.pipeline list`
- **Information**: `python -m cli.pipeline info your_pipeline`
- **Execution**: `python -m cli.pipeline run your_pipeline --stage <stage>`
- **Preview**: `python -m cli.pipeline preview your_pipeline`

## Examples

See existing pipelines for reference:
- **Vocabulary Pipeline**: `src/pipelines/vocabulary/`

## Best Practices

### Pipeline Design
- **Single Purpose**: Each pipeline serves one card type
- **Clear Stages**: Break processing into logical stages
- **Error Handling**: Handle errors gracefully
- **Configuration**: Make behavior configurable

### Resource Management
- **Use Provided Paths**: Don't hardcode media/data paths
- **Clean Up**: Remove temporary files after processing
- **Efficient Processing**: Process in reasonable batches
- **Respect Limits**: Honor API rate limits and cost controls

### Testing
- **Unit Tests**: Test each component individually
- **Integration Tests**: Test stage interactions
- **E2E Tests**: Test complete workflows
- **Mock External Services**: Use mocks for APIs

## Troubleshooting

### Common Issues
- **Import Errors**: Check `__init__.py` files and module structure
- **Registration Problems**: Ensure pipeline is imported in `src/pipelines/__init__.py`
- **Configuration Errors**: Validate JSON syntax and required fields
- **Path Issues**: Use pipeline-provided paths, not hardcoded ones

### Getting Help
- **Check existing pipelines** for implementation patterns
- **Use CLI help**: `python -m cli.pipeline --help`
- **Test incrementally**: Build and test one stage at a time
- **Review logs**: Check detailed execution logs for debugging

---

With this guide, you can create powerful new card types that integrate seamlessly with the existing system!
