# Vocabulary System Creation Planning

## Project Overview

### Creation Goal
To build an automated vocabulary flashcard creation system, that requires manual user prompts for image generation as a deliberate feature to improve memorability of flashcard generation.

### System Overview
The system processes Spanish vocabulary through a multi-stage pipeline, transforming dictionary data into flashcards with generated media content.

## Data Architecture

### Data Sources and Providers
- **Español.jsonl**: A read only spanish dictionary containing all vocabualry related data inputs for the cards
- **vocabulary.json**: An internal database storing all card information including all field values.
- **word_queue.json**: An internal database storing the upcoming words to process in the queue. Contains nearly filled cards, missing only the prompts for media generation.
- **prompts_staging.json**: Where the user inputs media prompts to be generated for the cards.
- **spanish_dictionary.json**: A frequency dictionary of Spanish, used for deciding the order of the word queue based on utility of each word.

### External Data Sources
- **Image from Prompt**: Generated per sense
- **Native Audio**: Generated per word

### Data Schema and Field Mappings

#### Required from Dictionary per Sense:
- **Word**: Pulled from root key "word"
- **Sense ID**: For debugging purposes
- **IPA**: Pulled from root key "sounds" with the correct "raw_tags"
- **Monolingual Definition**: Pulled from root key "senses" dict "glosses" value
- **English Translation**: Pulled from root key "translations" dict "translations" value. Mapped from the "senses" key "sense_index". Pull all translations for the monolingual definition joined by ", ".
- **Example Sentence**: Pulled from root key "senses" dict "examples" value. If multiple examples pull the first.
- **Gapped Example Sentence**: Same as above, however, the word is removed from the sentence and replaced with a _____ using the "bold_text_offsets" value
- **Type**: Found under key "pos" as a string. Denotes tye type such as "noun"
- **Gender**: If gender applies to the word, it can be found under "tags" inside a list as ["masculine"] or ["feminine"]

#### Updated Fields and Sources for vocabulary.json Cards:
**Existing fields:**
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

**New Fields:**
- "Translations": Every translation that maps to the meaning id joined with commas. E.g. ""call, name, refer to""
- "Type": Pulled directly from Dictionary
- "Gender": Optional, pulled from the dictionary if it is the correct type
- "SenseID": For debugging or future reference, will not be visible

**Removals:**
- "UsageNote"
- "WordAudioAlt"
- "MeaningContext"

## Pipeline Architecture

### Processing Stages Overview
The vocabulary pipeline divides processing into five modular stages:
1) **Stage 1**: Word Selection
2) **Stage 2**: Word Processing (Spanish dict to word queue + prompt staging)
3) **Stage 3**: Media Generation
4) **Stage 4**: Vocabulary Sync
5) **Stage 5**: Anki Sync

## Implementation Details

### Stage 1 & 2: Word Selection and Processing
#### Word Queue Structure
- The word queue entries will be a sequencial list of meanings with the same keys the meanings for words in vocabulary.json
- Every entry will be filled with the exception of Prompt and Gender which is an optional field that may be empty

#### Processing Architecture
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

#### Stage 1 Detailed Workflows

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

#### Stage 2 Detailed Processing
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
- **Prompt Staging Update**: Automatically updates prompts_staging.json after word_queue.json changes
  - **Staging Format**: `{"CardID": "prompt text"}` (ready), `{"CardID": ""}` (waiting), `{"CardID": null}` (skip)
  - Preserve existing prompts for unchanged CardIDs
  - Add new entries as `"CardID": ""` for newly added words
  - Validate staging keys match current queue CardIDs
  - Remove obsolete entries from staging file

### Stage 3: Media Generation
#### Processing Flow:
- **Prompt Validation & Import**:
  - Load and validate `prompts_staging.json` format and content
  - **Validation Rules**: minimum/maximum prompt length, JSON syntax, CardID existence
  - **Skip Processing**: Process entries where `value === null`
    - Move corresponding words to `vocabulary.json.skipped_words` array
    - Update `total_skipped` count in vocabulary metadata
    - Remove from both `word_queue.json` and staging file
  - **Prompt Import**: Import validated prompts into `word_queue.json` where prompt is non-empty string
- **Media Generation & Regeneration**:
  - Process queue entries with filled prompts
  - **Regeneration Logic**: Detect existing media files and prompt changes
    - If media exists and prompt changed: regenerate media files
    - If media missing: generate new media files
    - Log regeneration activities for user visibility
  - Generate images using validated prompts via image providers
  - Generate audio using word data via audio providers
  - Update `word_queue.json` with actual prompts used and `status: "media_generated"`
- **Queue Status Update**:
  - Update processed entries with `status: "media_generated"` and timestamp
  - Entries remain in `word_queue.json` for review/approval workflow

#### Enhanced Data Structure
Add status tracking to `word_queue.json` entries:
```json
{
  "CardID": "llamar_call_name_refer_to",
  "status": "media_generated",
  "media_generated_at": "2024-01-15T10:30:00Z",
  // ... existing fields
}
```

Status values: `"pending_prompts"` → `"media_generated"` → (Stage 4 processing)

### Stage 4: Vocabulary Sync
#### Processing Flow:
- **Review & Approval Processing**:
  - Process queue entries with `status: "media_generated"`
  - Apply approval workflow (CLI review commands, bulk approval, etc.)
  - Future: Frontend integration for image review interface
- **Vocabulary Update**:
  - Move approved entries from `word_queue.json` to `vocabulary.json`
  - Update vocabulary metadata (total cards, last updated, etc.)
  - Remove processed entries from word queue
- **Staging Cleanup**:
  - Synchronize `prompts_staging.json` with current `word_queue.json` state
  - Remove entries for completed/approved cards
  - Maintain staging file for remaining unprocessed entries
  - Add new entries as `"CardID": ""` for newly queued words

#### Review Commands (CLI Interface)
```bash
# Review pending media
pipeline review-media

# Regenerate specific card media
pipeline regenerate-media llamar_call_name_refer_to

# Bulk approve all pending
pipeline approve-media --all

# Interactive approval workflow
pipeline approve-media --interactive
```

### Stage 5: Anki Sync
To be decided
