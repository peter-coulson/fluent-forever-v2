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

## 3. Filtering Logic for Existing Entries

### Current Implementation
Filter out words already in vocabulary or current queue using existing CardID field.

### Exact Filtering Rules
- Check word exists in vocabulary.json using set lookup for O(1) performance
- No separate skipped words file - use existing vocabulary.json entries for filtering

### Word Conflict Handling
- If word already exists in vocabulary.json, skip and log
- If word already exists in current queue, skip and log duplicate

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

## 6. Data Validation Rules and Edge Cases

### Field Requirements
From spec - required fields per sense:
- Word (from root key "word")
- Sense ID
- IPA (from "sounds" with correct "raw_tags")
- Monolingual Definition (from "senses" → "glosses")
- English Translation (from "translations" mapped by "sense_index")
- Example Sentence (from "senses" → "examples", first if multiple)
- Type (from "pos")
- Gender (from "tags", optional)

### Validation Rules
- Character limits for prompts to prevent typos (validate minimum length)
- Media name conflict checking before generation
- CardID uniqueness validation against vocabulary.json

### Edge Cases
- Words without examples: Use first sense, log warning
- Missing gender information: Leave empty, continue processing
- Sorting algorithm: Simple `sorted(words, key=lambda w: w['rank'])`

### Ranking/Sorting Implementation
Use existing "rank" field in dictionary with simple numeric sort: `sorted(words, key=lambda w: w['rank'])`