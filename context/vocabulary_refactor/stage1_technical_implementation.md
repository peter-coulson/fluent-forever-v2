# Stage 1 Technical Implementation Document

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

## 3. Stage Separation and Validation Logic

### Clear Stage Handover Points

**Stage 1a: Word Selection**
- **Input**: CLI parameters (count, filters, etc.) OR direct word list
- **Processing**: Generate word list through rank-based/filter logic OR direct input
- **Output**: List of words to process
- **Handover**: Word list → Stage 1b

**Stage 1b: Word Processing** 
- **Input**: Word list (from Stage 1a or direct CLI)
- **Processing**: Dictionary fetching, sense processing, CardID generation
- **Output**: word_queue.json entries
- **Handover**: Complete word_queue.json entries (without prompts)

### Stage 1a: Word Selection Logic

**Rank-Based/Filter Pipeline:**
- Validate CLI parameters (count, word types, frequency ranges)
- Apply filters to spanish_dictionary.json
- Sort by rank and select top N words
- Filter out words already processed (word-level check against vocabulary.json)
- Filter out explicitly skipped words
- Output: Clean word list

**Direct Word Input Pipeline:**
- Validate CLI word list format
- Basic word existence check in dictionary
- No filtering against vocabulary (allows reprocessing)
- Output: Raw word list

### Stage 1b: Word Processing Logic

**Universal Entry Point** (same regardless of Stage 1a source):
- **DictionaryFetcher**: Validate word exists, extract all required fields
- **Sense Processor**: Apply sense grouping algorithm, IPA selection
- **CardID Generator**: Create unique CardID per selected sense
- **CardID Filtering**: Filter duplicate CardIDs against vocabulary.json and current queue

### Validation Separation Benefits

**Word-Level Filtering (Stage 1a Rank-Based only):**
- Prevents reprocessing entire words unnecessarily
- Applies only to automated selection, not direct CLI input

**CardID-Level Filtering (Stage 1b):**
- Always applied regardless of word source
- Enables reprocessing words for new senses
- Allows override of word-level filtering via direct CLI input

**Override Capability:**
- Direct CLI word input bypasses Stage 1a filtering
- Still applies Stage 1b CardID filtering for safety
- Enables forced reprocessing of words with new meanings

## 4. WordSelector Configuration Options and Interfaces

### Input Strategies
- **Rank-based**: Input number of words, pulls by rank order (default)
- **Specific words**: Input specific word list (comma-separated or file)  
- **Custom filters**: Filter by word type, frequency range, etc.

### Interface Design
Simple CLI arguments following existing patterns:
- `--count N` for rank-based selection
- `--words word1,word2` for specific words
- `--type noun` for type filtering

### Configuration Options
- Default: rank-based selection
- Validation: sanitize inputs with strip() and filter empty values
- Error handling: return `List[str]` validation errors

## 5. IPA Selection Algorithm

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

## 6. Debugging Output System

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

## 7. Data Validation Rules and Edge Cases

### Field Requirements
From spec - required fields per sense:
- Word (from root key "word")
- Sense ID
- IPA (from "sounds" with correct "raw_tags")
- Monolingual Definition (from "senses" → "glosses")
- English Translation (from "translations" mapped by "sense_index" - supports comma-separated lists "1,2,4" and range notation "1–2")
- Example Sentence (from "senses" → "examples", first if multiple)
- Type (from "pos")
- Gender (from "tags", optional)

### Stage-Specific Validation Summary

**Stage 1a (Word Selection):**
- CLI input format validation
- Word count/filter parameter validation
- Word existence checks (for rank-based selection only)
- Word-level filtering against existing vocabulary (rank-based only)

**Stage 1b (Word Processing):**
- Dictionary field validation (senses, translations, sounds, pos)
- Sense processing validation
- CardID uniqueness validation against vocabulary.json and current queue
- Field completeness validation

### Edge Cases
- Words without examples: Use first sense, log warning
- Missing gender information: Leave empty, continue processing
- Translation sense_index parsing: Handle comma-separated ("1,2,4"), ranges ("1–2"), and mixed ("1,2,4,5,8") patterns
- Sorting algorithm: Simple `sorted(words, key=lambda w: w['rank'])`

### Ranking/Sorting Implementation
Use existing "rank" field in dictionary with simple numeric sort: `sorted(words, key=lambda w: w['rank'])`