# Stage 1a Technical Implementation Document

## Handover Interface

**Input**: CLI parameters (count, filters, etc.) OR direct word list
**Output**: `List[str]` of Spanish words → Stage 1b

**Processing Flow**:
- Generate word list through rank-based/filter logic OR direct input
- Apply word-level filtering (rank-based only)
- Return clean word list for Stage 1b processing

## 1. Word Selection Pipelines

### Clear Stage Handover Point

**Stage 1a: Word Selection**
- **Input**: CLI parameters (count, filters, etc.) OR direct word list
- **Processing**: Generate word list through rank-based/filter logic OR direct input
- **Output**: `List[str]` of words to process
- **Handover**: Word list → Stage 1b

### Pipeline Types

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

## 2. WordSelector Configuration Options and Interfaces

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

## 3. Filtering Logic and Validation

### Word-Level Filtering (Rank-Based Pipeline Only)
**Purpose**: Prevents reprocessing entire words unnecessarily
**Applied to**: Automated selection only, not direct CLI input

**Filtering Rules:**
- Check if any CardID for the word exists in vocabulary.json
- Filter out words in explicit skip list
- Apply only to rank-based selection

**Benefits:**
- Improves performance by avoiding unnecessary dictionary lookups
- Focuses processing on genuinely new words
- Provides coarse-grained deduplication

### Override Capability
**Direct CLI Word Input:**
- Bypasses Stage 1a word-level filtering
- Enables forced reprocessing of words with new meanings
- Still subject to Stage 1b CardID filtering for safety
- Allows manual override of automated filtering decisions

### Validation Separation Benefits
**Word-Level Filtering (Stage 1a Rank-Based only):**
- Prevents reprocessing entire words unnecessarily
- Applies only to automated selection, not direct CLI input

**CardID-Level Filtering (Stage 1b):**
- Always applied regardless of word source
- Enables reprocessing words for new senses
- Allows override of word-level filtering via direct CLI input

## 4. Ranking and Sorting Implementation

### Sorting Algorithm
Use existing "rank" field in dictionary with simple numeric sort:
```python
sorted(words, key=lambda w: w['rank'])
```

### Selection Logic
1. Apply filters to spanish_dictionary.json entries
2. Sort filtered results by rank (ascending - lower rank = higher priority)
3. Select top N words from sorted list
4. Apply word-level filtering against existing vocabulary
5. Return final word list

### Edge Cases
- Missing rank field: Assign maximum rank value, log warning
- Duplicate ranks: Maintain deterministic order using secondary sort key
- Empty results after filtering: Return empty list, log warning
- Invalid count parameter: Return validation error

## 5. CLI Parameter Validation

### Required Parameters
- Either `--count N` (for rank-based) OR `--words word1,word2` (for direct input)
- Cannot specify both count and words simultaneously

### Optional Parameters
- `--type noun|verb|adj|adv`: Filter by word type
- `--min-rank N`: Minimum rank threshold
- `--max-rank N`: Maximum rank threshold
- `--skip-words word1,word2`: Explicitly skip these words

### Validation Rules
- Count must be positive integer
- Words must be comma-separated, non-empty strings
- Type must be valid POS tag from dictionary
- Rank ranges must be numeric and logical (min < max)

### Error Handling
- Return `List[str]` of validation errors (empty list = valid)
- Sanitize inputs with strip() and filter empty values
- Provide clear error messages for invalid parameters
- Fail fast on configuration errors before dictionary processing
