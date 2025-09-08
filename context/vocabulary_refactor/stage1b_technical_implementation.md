# Stage 1b Technical Implementation Document

## Launch Methods

Stage 1b supports two launch methods:

### 1. Automated Handover from Stage 1a
**Input**: `List[str]` of Spanish words from Stage 1a
**Trigger**: Automatic continuation after Stage 1a completion

### 2. Manual CLI Launch
**Input**: Command-line interface with word list
**Usage**: `python -m vocab_processor stage1b --words "word1,word2,word3"` or `--words-file path/to/words.txt`
**CLI Options**:
- `--words`: Comma-separated list of Spanish words
- `--words-file`: Path to file containing words (one per line)
- `--debug-vocab-processing`: Enable detailed debug output
- `--debug-level`: Control verbosity (basic|detailed|verbose)
- `--debug-output`: Optional structured debug output file

## Processing Interface

**Output**: Complete word_queue.json entries (without prompts)

**Processing Flow**:
1. **DictionaryFetcher**: Validate word exists, extract all required fields
2. **Sense Processor**: Apply sense grouping algorithm, IPA selection
3. **CardID Generator**: Create unique CardID per selected sense
4. **CardID Filtering**: Filter duplicate CardIDs against vocabulary.json and current queue

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

### Stage 1b Validation Summary
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