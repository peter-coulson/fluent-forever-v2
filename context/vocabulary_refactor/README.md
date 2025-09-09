# Vocabulary Refactor Planning

## Refactor Goal

To eliminate all manual inputs and claude usage outside of prompt writing

## High Level Method

All required inputs should be available in the Español.jsonl dictionary. By pulling the pipeline inputs from the dictionary we can eliminate all generation. Improving performance and efficiency.

## Required from Dictionary per Sense:

- **Word**: Pulled from root key "word"
- **Sense ID**: For debugging purposes
- **IPA**: Pulled from root key "sounds" with the correct "raw_tags"
- **Monolingual Definition**: Pulled from root key "senses" dict "glosses" value
- **English Translation**: Pulled from root key "translations" dict "translations" value. Mapped from the "senses" key "sense_index". Pull all translations for the monolingual definition joined by ", ".
- **Example Sentence**: Pulled from root key "senses" dict "examples" value. If multiple examples pull the first.
- **Gapped Example Sentence**: Same as above, however, the word is removed from the sentence and replaced with a _____ using the "bold_text_offsets" value
- **Type**: Found under key "pos" as a string. Denotes tye type such as "noun"
- **Gender**: If gender applies to the word, it can be found under "tags" inside a list as ["masculine"] or ["feminine"]

## Pulled from APIs
- **Image from Prompt**: Generated per sense
- **Native Audio**: Generated per word

## Fields in vocabulary.json:
### Mappings from the dictionary
- "SpanishWord": word
- "MeaningID": Transliations field formatted to be all lowercase, commas removed, and spaces replaced with underscores
- "MonolingualDef": Spanish Definition
- "ExampleSentence": Spanish example from dictionary
- "GappedSentence": Spanish example from dictionary gapped
- "IPA": From Dict
- "Prompt": The prompt from the user
- "CardID": spanish word + meaning id joined by _
- "ImageFile": cardID + .png
- "WordAudio": SpanishWord + .mp3

## New Fields
- "Translations": Every translation that maps to the meaning id joined with commas. E.g. ""call, name, refer to""
- "Type": Pulled directly from Dictionary
- "Gender": Optional, pulled from the dictionary if it is the correct type
- "SenseID": For debugging or future reference, will not be visible

### Removals:
- "UsageNote"
- "WordAudioAlt"
- "MeaningContext"

## New Architecture & Workflow

### Integration with Core Pipeline Framework
The vocabulary pipeline implements the core framework's `Pipeline` abstract class and uses the `Stage` system for modular execution. This provides:
- **Unified CLI Interface**: `python -m cli.pipeline run vocabulary --stage word_selection`
- **Context Management**: Automatic provider integration (data, media, sync)
- **Error Handling**: Standardized `StageResult` with status/message/errors
- **Registry Integration**: Auto-discovery via `python -m cli.pipeline list`

### High-Level Code Structure
```
src/
├── core/              # Keep - pipeline framework (Stage, Pipeline, StageResult)
├── apis/              # Keep - external API clients
├── cli/               # Keep - unified CLI with pipeline runner
├── config/            # Keep - configuration management
├── utils/             # Keep - shared utilities
├── validation/        # Keep - validation framework
├── pipelines/
│   └── vocabulary/    # COMPLETELY REBUILT - implements core.Pipeline
│       ├── vocabulary_pipeline.py  # Main VocabularyPipeline class
│       ├── stages/                 # Individual Stage implementations
│       │   ├── word_selection.py      # Stage 1: Word Selection
│       │   ├── word_processing.py     # Stage 2: Word Processing
│       │   ├── prompt_creation.py     # Stage 3: Prompt Creation
│       │   ├── media_generation.py    # Stage 4: Media Generation
│       │   └── anki_sync.py           # Stage 5: Anki Sync
│       └── data/                   # Data models & validation
└── sync/              # Keep - sync utilities
```

### Pipeline Stage Architecture
The vocabulary pipeline divides processing into five modular stages:
1) **Stage 1**: Word Selection
2) **Stage 2**: Word Processing (Spanish dict to word queue)
3) **Stage 3**: Prompt Creation
4) **Stage 4**: Media Generation & Vocabulary Update
5) **Stage 5**: Anki Sync

### Stage 1 & 2: Word Selection and Processing
#### Word Queue Structure
- The word queue entries will be a sequencial list of meanings with the same keys the meanings for words in vocabulary.json
- Every entry will be filled with the exception of Prompt and Gender which is an optional field that may be empty

#### Modular Architecture
The word queue population is divided into two distinct stages:

**Stage 1: Word Selection**
Two separate pipelines for word selection:

*Rank-Based/Filter Pipeline:*
- Input number of words, pulls by rank order (default)
- Apply custom filters: word type, frequency range, etc.
- Filter out words already processed (word-level check against vocabulary.json)
- Filter out explicitly skipped words
- Output: Clean word list

*Direct Word Input Pipeline:*
- Input specific word list (comma-separated or file)
- Basic word existence check in dictionary
- No filtering against vocabulary (allows reprocessing)
- Output: Raw word list

**Stage 2: Word Processing**
Universal processing regardless of Stage 1 source:
- **DictionaryFetcher**: Retrieves and validates word entries from spanish_dictionary.json
- **Sense Processor**: Applies sense grouping algorithm and IPA selection
- **WordQueuePopulator**: Creates queue entries, filters duplicate CardIDs
- Appends new meaning instances to word_queue.json with vocabulary.json field structure

#### Stage 1: Word Selection Workflows

**Rank-Based/Filter Workflow:**
- Input the number of new words and optional filters
- Apply filters to spanish_dictionary.json (word type, frequency range, etc.)
- Sort by rank and select top N words
- Filter out words already processed (any CardID exists in vocabulary.json)
- Filter out explicitly skipped words
- Output: Clean word list → Stage 2

**Direct Word Input Workflow:**
- Input specific word list (comma-separated or file)
- Basic word existence check in dictionary
- No vocabulary filtering (enables reprocessing)
- Output: Raw word list → Stage 2

#### Stage 2: Universal Word Processing
- **DictionaryFetcher**: Retrieves and validates each word's dictionary data
- **Sense Processing**: Apply sense grouping algorithm
  - **Critical Problem**: Dictionary contains all possible senses. We need only the most essential ones.
  - **Solution**: Group senses by English translations, keeping only unique groups (no subsets):
    - Group senses with identical English translations
    - Eliminate subset groups (e.g., "call" is subset of "call, name, refer to")
    - Example grouping: [{1,2: "call, name, refer to"}, {3: "summon"}, {10: "knock, ring"}, {11: "attract, appeal"}]
  - **Sense Selection**: For each group, select the first sense number that has an example sentence. If no senses in the group have examples, use the first sense number and log a warning.
- **WordQueuePopulator**: Creates queue entries, filters duplicate CardIDs against vocabulary.json and current queue
- For each selected sense, appends a new meaning instance to word_queue.json with vocabulary.json field structure

### Stage 3: Prompt Creation
Will leave undefined for now. Options are either the user directly editing the word queue and calling a sync script that checks for any words where the prompt value is filled. Or we create some other batch file where the user inputs the CardID: "prompt". We also need some skip word function. I think this would probably be easiest to have some cli script for skipping word queue where we input the words to be skipped --skipped-words ya,yo,hay

### Stage 4: Media Generation & Vocabulary Update
We generate the media as part of this pipeline. This would constitue a form of sync as described above. It should validate prompts are a certain number of characters to prevent accidental typos. Then it should validate that the media with the same name is not already in the media folder and the CardID is not already in vocabulary. Then proceed to generate all media. Once all media is generated, update vocabulary.

### Stage 5: Anki Sync
This logic will remain largely unchanged

## Core Pipeline Integration

### VocabularyPipeline Implementation
The main pipeline class implements the core framework's abstract `Pipeline` class:

```python
# src/pipelines/vocabulary/vocabulary_pipeline.py
from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.context import PipelineContext

class VocabularyPipeline(Pipeline):
    @property
    def name(self) -> str:
        return "vocabulary"

    @property
    def display_name(self) -> str:
        return "Spanish Vocabulary Cards"

    @property
    def stages(self) -> List[str]:
        return ["word_selection", "word_processing", "prompt_creation",
                "media_generation", "anki_sync"]

    @property
    def data_file(self) -> str:
        return "vocabulary.json"

    @property
    def anki_note_type(self) -> str:
        return "Spanish Vocabulary"

    def get_stage(self, stage_name: str) -> Stage:
        # Return appropriate stage implementation
        if stage_name == "word_selection":
            return WordSelectionStage()
        elif stage_name == "word_processing":
            return WordProcessingStage()  # Complex orchestrator
        # ... etc
```

### Stage Data Handoffs via PipelineContext

**Stage 1 → Stage 2 Handoff:**
```python
# Stage 1 (WordSelectionStage) produces:
context.set("selected_words", ["por", "para", "cuando"])
context.set("selection_method", "rank_based")  # or "direct_input"
context.set("filters_applied", {"pos": ["noun", "verb"], "frequency_min": 100})

# Stage 2 (WordProcessingStage) consumes:
selected_words = context.get("selected_words")
# Returns:
context.set("processed_entries", [
    {
        "SpanishWord": "por",
        "MeaningID": "by_for_through",
        "MonolingualDef": "Para indicar causa...",
        "CardID": "por_by_for_through",
        # ... complete vocabulary.json structure minus prompt
    }
])
context.set("word_queue_updated", True)
```

**Stage 2 → Stage 3 Handoff:**
```python
# Stage 2 output available in word_queue.json
# Stage 3 (PromptCreationStage) processes queue entries with empty prompts:
context.set("pending_prompts", ["por_by_for_through", "para_for_to"])
# After user input:
context.set("prompts_completed", ["por_by_for_through"])
context.set("prompts_skipped", ["para_for_to"])
```

**Stage 3 → Stage 4 Handoff:**
```python
# Stage 4 (MediaGenerationStage) processes entries with prompts:
ready_cards = context.get("prompts_completed", [])
# Validates prompts, generates media, updates vocabulary.json:
context.set("media_generated", {
    "images": ["por_by_for_through.png"],
    "audio": ["por.mp3"]
})
context.set("vocabulary_updated", True)
```

**Stage 4 → Stage 5 Handoff:**
```python
# Stage 5 (AnkiSyncStage) syncs completed vocabulary entries:
completed_cards = context.get("media_generated", {})
# Syncs to Anki and returns results:
context.set("anki_sync_results", {
    "cards_added": 1,
    "cards_updated": 0,
    "errors": []
})
```

### CLI Integration Examples

**Run individual stages:**
```bash
# Stage 1: Select words
python -m cli.pipeline run vocabulary --stage word_selection --words "por,para,cuando"

# Stage 2: Process dictionary data
python -m cli.pipeline run vocabulary --stage word_processing

# Stage 3: Create prompts (manual intervention)
python -m cli.pipeline run vocabulary --stage prompt_creation

# Stage 4: Generate media and update vocabulary
python -m cli.pipeline run vocabulary --stage media_generation --execute

# Stage 5: Sync to Anki
python -m cli.pipeline run vocabulary --stage anki_sync --execute
```

**Pipeline info and discovery:**
```bash
# List all available pipelines
python -m cli.pipeline list

# Get vocabulary pipeline information
python -m cli.pipeline info vocabulary --stages

# Preview cards
python -m cli.pipeline preview vocabulary --card-id por_by_for_through
```

### Error Handling and Validation
Each stage implements standardized error handling via `StageResult`:

```python
class WordProcessingStage(Stage):
    def execute(self, context: PipelineContext) -> StageResult:
        try:
            # Complex Phase 2 processing logic here
            processor = WordProcessor()
            result = processor.process_words(context.get("selected_words"))

            return StageResult.success(
                f"Processed {len(result.entries)} word entries",
                {"processed_entries": result.entries}
            )
        except ValidationError as e:
            return StageResult.failure(
                "Word processing validation failed",
                errors=e.errors
            )
        except Exception as e:
            return StageResult.failure(f"Unexpected error: {str(e)}")
```

### Stage Dependencies and Validation
Stages can declare dependencies and validate context:

```python
class MediaGenerationStage(Stage):
    @property
    def dependencies(self) -> List[str]:
        return ["word_processing", "prompt_creation"]

    def validate_context(self, context: PipelineContext) -> List[str]:
        errors = []
        if not context.get("prompts_completed"):
            errors.append("No completed prompts found")
        if not Path("word_queue.json").exists():
            errors.append("word_queue.json not found")
        return errors
```

This architecture provides the flexibility needed for vocabulary's complex processing while integrating cleanly with the core pipeline framework.
