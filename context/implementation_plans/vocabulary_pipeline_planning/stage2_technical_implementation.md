# Stage 2 Technical Implementation Document

## Code Architecture

### File Structure
```
src/pipelines/vocabulary/stages/word_processing/
├── __init__.py
├── word_processor.py      # Main orchestrator class
├── dictionary_fetcher.py  # Fetch & validate from dictionary
├── sense_processor.py     # Sense grouping algorithm
├── ipa_selector.py        # IPA selection with scoring
├── card_generator.py      # CardID generation & filtering
├── queue_populator.py     # Word queue population
└── debug_output.py        # Debug/logging system
```

### Core Classes

#### WordProcessor (word_processor.py)
```python
class WordProcessor:
    def __init__(self, spanish_dict_provider, vocabulary_provider, word_queue_provider):
        self.spanish_dict_provider = spanish_dict_provider
        self.vocabulary_provider = vocabulary_provider
        self.word_queue_provider = word_queue_provider

    def process_words(self, word_list: List[str], debug_level: str = "basic") -> ProcessingResult:
        # Main orchestration logic using providers
    def _validate_inputs(self, word_list: List[str]) -> List[str]:
        # Input validation
    def _generate_debug_output(self, results: ProcessingResult) -> None:
        # Debug output coordination
```

#### DictionaryFetcher (dictionary_fetcher.py)
```python
class DictionaryFetcher:
    def __init__(self, jsonl_provider: JSONLDataProvider):
        self.jsonl_provider = jsonl_provider

    def fetch_word_data(self, word: str) -> DictionaryEntry:
        # Retrieve and validate word from Español.jsonl via provider
    def fetch_words_batch(self, words: List[str]) -> Dict[str, DictionaryEntry]:
        # Batch fetch using provider.get_words_batch() - see jsonl_provider_design.md
    def validate_entry(self, entry: dict) -> List[str]:
        # Validate required fields exist
```

#### SenseProcessor (sense_processor.py)
```python
class SenseProcessor:
    def group_senses_by_translations(self, senses: List[dict]) -> List[SenseGroup]:
        # Group senses with identical translations
    def eliminate_subset_groups(self, groups: List[SenseGroup]) -> List[SenseGroup]:
        # Remove subset groups
    def select_best_sense_per_group(self, groups: List[SenseGroup]) -> List[int]:
        # Select sense with example, fallback to first
```

#### IPASelector (ipa_selector.py)
```python
class IPASelector:
    def select_best_ipa(self, sounds_data: List[dict]) -> Optional[str]:
        # Score and select IPA pronunciation
    def _score_pronunciation(self, sound_entry: dict) -> int:
        # Scoring algorithm for Colombian accent
    def _parse_raw_tags(self, tags: List[str]) -> Dict[str, bool]:
        # Parse pronunciation tags
```

#### CardGenerator (card_generator.py)
```python
class CardGenerator:
    def __init__(self, vocabulary_provider, word_queue_provider):
        self.vocabulary_provider = vocabulary_provider
        self.word_queue_provider = word_queue_provider

    def generate_card_id(self, word: str, translations: List[str]) -> str:
        # Create unique CardID
    def filter_existing_cards(self, cards: List[dict]) -> List[dict]:
        # Filter against vocabulary.json and current queue via providers
    def _load_existing_card_ids(self) -> Set[str]:
        # Load existing CardIDs from both data sources via providers
```

#### QueuePopulator (queue_populator.py)
```python
class QueuePopulator:
    def __init__(self, word_queue_provider, prompts_staging_provider):
        self.word_queue_provider = word_queue_provider
        self.prompts_staging_provider = prompts_staging_provider

    def populate_queue(self, processed_data: List[dict]) -> None:
        # Add entries to word_queue.json via provider
    def update_prompts_staging(self, new_entries: List[dict]) -> None:
        # Update prompts_staging.json via provider
    def validate_queue_entry(self, entry: dict) -> List[str]:
        # Validate complete queue entry
```

## Launch Methods

Stage 2 supports two launch methods:

### 1. Automated Handover from Stage 1
**Input**: `List[str]` of Spanish words from Stage 1 via PipelineContext
**Trigger**: Automatic continuation after Stage 1 completion

### 2. Manual CLI Launch
**Input**: Command-line interface with word list
**Usage**: `python -m cli.pipeline run vocabulary --stage word_processing --words "word1,word2,word3"` or `--words-file path/to/words.txt`
**CLI Options** (handled via pipeline `validate_cli_args()` and `populate_context_from_cli()`):
- `--words`: Comma-separated list of Spanish words
- `--words-file`: Path to file containing words (one per line)
- `--debug-vocab-processing`: Enable detailed debug output
- `--debug-level`: Control verbosity (basic|detailed|verbose)
- `--debug-output`: Optional structured debug output file

## Processing Interface

**Output**: Complete word_queue.json entries (without prompts)

**Processing Flow**:
1. **DictionaryFetcher**: Batch fetch from Español.jsonl via JSONLDataProvider, validate entries
2. **Sense Processor**: Apply sense grouping algorithm, IPA selection
3. **CardID Generator**: Create unique CardID per selected sense
4. **CardID Filtering**: Filter duplicate CardIDs against vocabulary.json and current queue via JSONDataProvider

## 1. Sense Grouping Algorithm

### Algorithm Overview
Group senses by English translations, keeping only unique groups (no subsets):
- Group senses with identical English translations after normalization (lowercase, sorted)
- Eliminate subset groups using set operations (e.g., "call" is subset of "call, name, refer to")
- Example grouping: `[{1,2: "call, name, refer to"}, {3: "summon"}, {10: "knock, ring"}, {11: "attract, appeal"}]`

### Sense Selection Logic
For each group, select the first sense number that has an example sentence. If no senses in the group have examples, use the first sense number and log a warning.

### Examples
Simple string-based grouping where translation sets are identical after normalization:
- Senses 1,2 both have translations ["call", "name", "refer to"] → group together
- Sense 3 has translations ["summon"] → separate group
- Groups with translation sets that are complete subsets of others are eliminated

### Edge Cases
- Empty translations: Skip sense and log warning
- Malformed sense data: Continue processing, accumulate errors in list
- No example sentences in any sense of group: Use first sense, log warning

## 2. Error Handling for Malformed Dictionary Data

### Data Structure Validation
Follow existing validation pattern - return `List[str]` of error messages (empty list = valid)

### Missing Field Handling
- Required fields (word, senses, translations): Add to error list, skip entry
- Optional fields (gender): Continue processing, log warning

### Malformed Field Handling
- Use try-catch blocks with specific exception handling
- Accumulate errors in lists for batch reporting
- Continue processing remaining entries

### Recovery Strategies
- Log detailed error messages with sense IDs for debugging
- Skip malformed entries but continue processing
- Report summary of skipped entries at completion

## 3. CardID-Level Filtering and Validation

### CardID Generation
- Create unique CardID per selected sense: `spanish_word + "_" + meaning_id`
- `meaning_id`: translations field formatted to be all lowercase, commas removed, and spaces replaced with underscores

### Filtering Logic
**Always applied regardless of word source:**
- Filter duplicate CardIDs against vocabulary.json
- Filter duplicate CardIDs against current word queue
- Enables reprocessing words for new senses
- Provides safety net for all processing paths

### Validation Benefits
- Prevents duplicate cards in final vocabulary
- Allows word reprocessing when new meanings discovered
- Works with both automated and manual word selection

## 4. IPA Selection Algorithm

### Selection Criteria
Algorithm optimized for upper-class Bogota accent using priority-based scoring:

**Scoring System:**
- `seseante, yeísta`: 10 points (ideal Colombian combination)
- `seseante` only: 8 points (Colombian seseo standard)
- `yeísta` only: 6 points (modern Spanish yeísmo)
- No tags (default): 4 points (neutral pronunciation)
- `no seseante`: -2 points (penalty for distinción)
- `sheísta`/`zheísta`: -5 points (strong penalty for Rioplatense variants)

**Selection Logic:**
1. Score all valid IPA pronunciations from sounds data
2. Select highest-scoring pronunciation
3. On tie, select first occurrence for deterministic behavior
4. Require minimum score > 0 for selection

### Filtering Logic
Use `raw_tags` field to identify Colombian phonological features:

**Target Tags for Bogota:**
- `seseante`: Merges /s/ and /θ/ as /s/ (no "th" sound)
- `yeísta`: Merges /ʎ/ (ll) and /ʝ/ (y) as /ʝ/

**Avoided Tags:**
- `no seseante`: Peninsular Spanish distinción
- `sheísta`: Argentine /ʃ/ pronunciation of ll/y
- `zheísta`: Argentine /ʒ/ pronunciation of ll/y
- `no sheísta`: Explicitly non-/ʃ/ (still not Colombian)

**Tag Processing:**
- Parse `raw_tags` as list of strings
- Handle empty/missing tags as untagged (score: 4)
- Log malformed tag data and continue processing

### Fallback Strategy
**Primary Strategy:** Score-based selection with validation
1. Validate sounds data exists and is list
2. Filter entries with valid IPA field
3. Score each pronunciation by tag combination
4. Select highest score (>0 required)

**Fallback Hierarchy:**
1. If no positive-scoring pronunciations: select any untagged IPA, log warning
2. If no valid IPA pronunciations: return None, log error
3. If sounds field missing/empty: return None, log error

**Error Handling:**
- Continue processing on malformed entries
- Accumulate warnings for batch logging
- Log all selection decisions with sense_id for debugging
- Never crash on invalid data - always return None or valid result

**Validation Requirements:**
- IPA field must be non-empty string
- sounds must be non-empty list
- Log warnings for: missing sounds, malformed entries, fallback usage
- Log info for: multiple equal-priority selections

## 5. Debugging Output System

### CLI Debug Flag Implementation
Add comprehensive debugging output with CLI flag `--debug-vocab-processing` or `--debug-level=verbose`:

**Core Integration Example:**
```bash
python -m cli.pipeline run vocabulary --stage word_processing --debug-level verbose
```

### Core Debug Information
- **Sense-level details**: Complete formatted vocabulary output for each sense
- **Translation maps**: Full mapping from sense_index to translations showing grouping logic
- **Translation groups**: How senses were grouped by identical translations and subset elimination

### Extended Debug Information
- **IPA Selection Details**: All available pronunciations with raw_tags, scoring breakdown, selected IPA with reasoning, fallback warnings
- **Sense Grouping Algorithm**: Raw translations, normalization steps, group formation, subset elimination decisions, final sense selection reasoning
- **Validation Results**: Field validation per sense, malformed data handling, missing field warnings, character limit checks
- **Filtering Logic**: Words filtered (already in vocabulary/queue), conflict detection, skipped entries with reasons
- **Quality Metrics**: Processing statistics, coverage metrics, warning summaries

### Debug Output Options
```bash
--debug-vocab-processing          # Enable detailed debug output
--debug-level=basic|detailed|verbose  # Control debug verbosity
--debug-output=/path/to/debug.json    # Optional structured output file
```

## 6. Data Validation Rules and Edge Cases

### Field Requirements
Required fields per sense:
- Word (from root key "word")
- Sense ID
- IPA (from "sounds" with correct "raw_tags")
- Monolingual Definition (from "senses" → "glosses")
- English Translation (from "translations" mapped by "sense_index" - supports comma-separated lists "1,2,4" and range notation "1–2")
- Example Sentence (from "senses" → "examples", first if multiple)
- Type (from "pos")
- Gender (from "tags", optional)

### Phase 2 Validation Summary
- Dictionary field validation (senses, translations, sounds, pos)
- Sense processing validation
- CardID uniqueness validation against vocabulary.json and current queue
- Field completeness validation

### Edge Cases
- Words without examples: Use first sense, log warning
- Missing gender information: Leave empty, continue processing
- Translation sense_index parsing: Handle comma-separated ("1,2,4"), ranges ("1–2"), and mixed ("1,2,4,5,8") patterns

### Processing Algorithm
- Continue processing on validation failures
- Accumulate all errors for batch reporting
- Log detailed error context with word and sense identifiers
- Never crash on malformed data - always return partial results or skip gracefully

## Core Pipeline Integration

### WordProcessingStage Implementation
```python
# src/pipelines/vocabulary/stages/word_processing.py
from typing import List, Any
from src.core.stages import Stage, StageResult
from src.core.context import PipelineContext
from src.core.exceptions import ValidationError
from .word_processing.word_processor import WordProcessor

class WordProcessingStage(Stage):
    """Stage 2: Process dictionary data for selected words"""

    @property
    def name(self) -> str:
        return "word_processing"

    @property
    def display_name(self) -> str:
        return "Word Processing"

    @property
    def dependencies(self) -> List[str]:
        return ["word_selection"]  # Requires Stage 1 output

    def validate_context(self, context: PipelineContext) -> List[str]:
        errors = []

        # Validate input data
        selected_words = context.get("selected_words")
        if not selected_words:
            errors.append("No selected_words found in context")
        if not isinstance(selected_words, list):
            errors.append("selected_words must be a list")

        # Validate provider access
        providers = context.get("providers", {})
        data_providers = providers.get("data", {})

        if "spanish_dictionary" not in data_providers:
            errors.append("spanish_dictionary provider not configured")
        if "vocabulary_data" not in data_providers:
            errors.append("vocabulary_data provider not configured")
        if "word_queue_data" not in data_providers:
            errors.append("word_queue_data provider not configured")

        return errors

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        """Execute the complex Stage 2 word processing pipeline"""
        try:
            # Get providers from context (configured via registry)
            providers = context.get("providers", {})
            data_providers = providers.get("data", {})

            spanish_dict_provider = data_providers["spanish_dictionary"]
            vocabulary_provider = data_providers["vocabulary_data"]
            word_queue_provider = data_providers["word_queue_data"]

            # Get input from Stage 1 or CLI
            selected_words = context.get("selected_words", [])
            debug_level = context.get("debug_level", "basic")

            # Initialize the complex word processor orchestrator with providers
            processor = WordProcessor(
                spanish_dict_provider=spanish_dict_provider,
                vocabulary_provider=vocabulary_provider,
                word_queue_provider=word_queue_provider
            )

            # Execute the full Stage 2 pipeline
            result = processor.process_words(
                word_list=selected_words,
                debug_level=debug_level
            )

            # Handle partial failures
            if result.errors and result.entries:
                context.add_error(f"Partial processing: {len(result.errors)} words failed")

            # Update context for Stage 3
            context.set("processed_entries", result.entries)
            context.set("word_queue_updated", True)
            context.set("processing_stats", result.stats)

            # Return appropriate result based on success/partial/failure
            if result.entries and not result.errors:
                return StageResult.success_result(
                    f"Successfully processed {len(result.entries)} word entries",
                    {
                        "processed_entries": result.entries,
                        "stats": result.stats,
                        "warnings": result.warnings
                    }
                )
            elif result.entries and result.errors:
                return StageResult.partial(
                    f"Processed {len(result.entries)} entries with {len(result.errors)} errors",
                    {
                        "processed_entries": result.entries,
                        "stats": result.stats,
                        "warnings": result.warnings
                    },
                    result.errors
                )
            else:
                return StageResult.failure(
                    "No entries processed successfully",
                    result.errors
                )

        except ValidationError as e:
            return StageResult.failure(
                "Dictionary validation failed",
                errors=e.errors
            )
        except Exception as e:
            self.logger.exception("Unexpected error in word processing")
            return StageResult.failure(
                f"Word processing failed: {str(e)}"
            )
```

### Pipeline-Level CLI Integration

**Vocabulary Pipeline Class** (must be implemented):
```python
# src/pipelines/vocabulary/pipeline.py
from typing import Any, List
from src.core.pipeline import Pipeline
from src.core.context import PipelineContext

class VocabularyPipeline(Pipeline):
    """Vocabulary card creation pipeline"""

    def validate_cli_args(self, args: Any) -> List[str]:
        """Validate CLI arguments for vocabulary pipeline"""
        errors = []

        # Validate word processing stage arguments
        if hasattr(args, 'stage') and args.stage == 'word_processing':
            if not hasattr(args, 'words') and not hasattr(args, 'words_file'):
                errors.append("Either --words or --words-file required for word_processing stage")

            if hasattr(args, 'words') and hasattr(args, 'words_file'):
                if args.words and args.words_file:
                    errors.append("Cannot specify both --words and --words-file")

            if hasattr(args, 'words_file') and args.words_file:
                from pathlib import Path
                if not Path(args.words_file).exists():
                    errors.append(f"Words file not found: {args.words_file}")

        return errors

    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        """Populate context with CLI arguments"""
        # Handle word list input
        if hasattr(args, 'words') and args.words:
            selected_words = [w.strip() for w in args.words.split(',')]
            context.set("selected_words", selected_words)

        elif hasattr(args, 'words_file') and args.words_file:
            from pathlib import Path
            words_file = Path(args.words_file)
            selected_words = [line.strip() for line in words_file.read_text().splitlines() if line.strip()]
            context.set("selected_words", selected_words)

        # Handle debug settings
        if hasattr(args, 'debug_level'):
            context.set("debug_level", args.debug_level)
        elif hasattr(args, 'debug_vocab_processing') and args.debug_vocab_processing:
            context.set("debug_level", "verbose")

        if hasattr(args, 'debug_output') and args.debug_output:
            context.set("debug_output_path", args.debug_output)
```

### Data Provider Configuration Integration

**Required Configuration** (`config.json`):
```json
{
  "providers": {
    "data": {
      "spanish_dictionary": {
        "type": "jsonl",
        "file_path": "data/Español.jsonl",
        "pipelines": ["vocabulary"],
        "read_only": true,
        "build_index": true
      },
      "vocabulary_data": {
        "type": "json",
        "base_path": "data/",
        "files": ["vocabulary"],
        "pipelines": ["vocabulary"],
        "read_only": false
      },
      "word_queue_data": {
        "type": "json",
        "base_path": "data/",
        "files": ["word_queue", "prompts_staging"],
        "pipelines": ["vocabulary"],
        "read_only": false
      }
    }
  }
}
```
