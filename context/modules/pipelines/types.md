# Pipeline Types and Implementations

## Implementation Status

**No concrete pipelines currently exist** - `src/pipelines/__init__.py:9` shows empty `register_all_pipelines()` function with comment "No pipelines currently implemented".

## Planned Pipeline Architecture

Based on CLI validation patterns and system design, the following pipeline types are expected:

## Vocabulary Pipeline

### Pipeline Specification
- **Name**: `vocabulary`
- **Data File**: `vocabulary.json`
- **Anki Note Type**: Spanish vocabulary card type
- **Display Name**: "Spanish Vocabulary"

### Stage Definitions
| Stage | Purpose | CLI Arguments | Provider Dependencies |
|-------|---------|---------------|----------------------|
| `prepare` | Load and validate vocabulary data | `--words` (comma-separated) | data provider |
| `media` | Generate audio/image for cards | `--cards` (comma-separated) | audio, image providers |
| `sync` | Upload to Anki | `--execute` flag | sync provider |

### Data Requirements
- **Input Format**: JSON vocabulary entries with Spanish words and definitions
- **Word Selection**: CLI `--words` parameter filters specific vocabulary items
- **Media Generation**: Audio pronunciations and visual images for vocabulary cards

### Anki Integration
- **Card Creation**: Generate Anki cards with Spanish/English pairs
- **Media Attachments**: Associate audio files and images with cards
- **Deck Management**: Organize cards into vocabulary-specific Anki decks

## Conjugation Pipeline

### Pipeline Specification
- **Name**: `conjugation`
- **Data File**: Conjugation-specific data file (format TBD)
- **Anki Note Type**: Verb conjugation card type
- **Display Name**: "Spanish Verb Conjugation"

### Expected Stages
- **prepare**: Load verb conjugation data and patterns
- **generate**: Create conjugation exercises and examples
- **sync**: Upload conjugation cards to Anki

### Learning Focus
- **Verb Forms**: Present, past, future tense conjugations
- **Person/Number**: First, second, third person variations
- **Practice Patterns**: Generate exercises for conjugation memorization

## Grammar Pipeline (Future)

### Potential Implementation
- **Focus**: Spanish grammar concepts and rules
- **Data**: Grammar explanations, examples, exercises
- **Anki Cards**: Grammar rule cards with examples

## Implementation Patterns

### Abstract Method Requirements

#### `validate_cli_args(args)` Implementation
```python
# Vocabulary pipeline validation example
def validate_cli_args(self, args: Any) -> list[str]:
    errors = []
    if args.stage == "prepare" and not getattr(args, 'words', None):
        errors.append("--words required for prepare stage")
    if args.stage == "media" and not getattr(args, 'cards', None):
        errors.append("--cards required for media stage")
    return errors
```

#### `populate_context_from_cli(context, args)` Implementation
```python
# Context population pattern
def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
    if hasattr(args, 'words'):
        word_list = [w.strip() for w in args.words.split(',')]
        context.set('selected_words', word_list)
    if hasattr(args, 'cards'):
        card_list = [c.strip() for c in args.cards.split(',')]
        context.set('selected_cards', card_list)
```

### Stage Implementation Patterns

#### Context Dependencies
- **Data Provider**: Access to vocabulary/conjugation data sources
- **Audio Provider**: Forvo or other pronunciation services
- **Image Provider**: Image generation for visual learning aids
- **Sync Provider**: Anki Connect for card synchronization

#### Error Handling
- **Validation Errors**: Missing required CLI arguments or malformed data
- **Provider Errors**: External service failures (API limits, network issues)
- **Data Errors**: Invalid vocabulary entries or missing media

### Registration Process

#### Future Pipeline Registration
```python
# In src/pipelines/__init__.py
from src.pipelines.vocabulary import VocabularyPipeline
from src.pipelines.conjugation import ConjugationPipeline

def register_all_pipelines() -> None:
    registry = get_pipeline_registry()
    registry.register(VocabularyPipeline())
    registry.register(ConjugationPipeline())
    # Additional pipelines...
```

## CLI Integration Expectations

### Usage Patterns
```bash
# Vocabulary pipeline usage
cli run vocabulary --stage prepare --words por,para,que
cli run vocabulary --stage media --cards 1,2,3
cli run vocabulary --stage sync --execute

# Conjugation pipeline usage
cli run conjugation --stage prepare --verbs ser,estar,tener
cli run conjugation --stage generate --tenses present,past
```

### Validation Integration
- **CLI Validation**: `src/cli/utils/validation.py:31-34` shows stage-specific validation
- **Pipeline Validation**: Each pipeline implements additional validation logic
- **Error Feedback**: Consistent error reporting through CLI utilities

## Development Priorities

1. **Vocabulary Pipeline**: Primary learning workflow implementation
2. **Core Stage Library**: Reusable stages for data loading, media generation, Anki sync
3. **Conjugation Pipeline**: Secondary learning workflow
4. **Testing Framework**: Pipeline and stage testing patterns
