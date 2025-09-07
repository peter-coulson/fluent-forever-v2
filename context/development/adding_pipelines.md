# Adding New Pipelines

Learn how to extend the system with new card types using the pipeline-centric architecture.

## Overview

Adding a new pipeline involves:
1. **Pipeline Implementation**: Core pipeline class with stage definitions
2. **Stage Development**: Custom stages for your card type
3. **Configuration**: Pipeline-specific settings
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

from src.core.pipeline import Pipeline
from pathlib import Path
import json

class YourPipeline(Pipeline):
    
    def __init__(self, config: dict):
        super().__init__("your_pipeline", "Your Pipeline Description", config)
        self.data_file = Path(config.get('data_file', 'your_data.json'))
    
    def get_stages(self) -> dict:
        """Define pipeline stages and their dependencies"""
        return {
            'your_analysis': {
                'description': 'Analyze input data for your card type',
                'dependencies': []
            },
            'generate_media': {
                'description': 'Generate images and audio',
                'dependencies': ['your_analysis']
            },
            'sync_cards': {
                'description': 'Sync cards to Anki',
                'dependencies': ['generate_media']
            }
        }
    
    def get_media_paths(self) -> dict:
        """Get pipeline-specific media paths"""
        return {
            'base': f'media/{self.pipeline_type}/',
            'images': f'media/{self.pipeline_type}/images/',
            'audio': f'media/{self.pipeline_type}/audio/'
        }
    
    def get_anki_config(self) -> dict:
        """Get Anki integration configuration"""
        return {
            'note_type': 'Your Pipeline',
            'deck_name': 'Your Pipeline::Cards'
        }
    
    def load_data(self) -> dict:
        """Load pipeline data"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_data(self, data: dict) -> None:
        """Save pipeline data"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
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
- **Conjugation Pipeline**: `src/pipelines/conjugation/`

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