# JSONL Data Provider Design

## Purpose
Efficient data provider for large JSONL dictionary files (1GB+), specifically designed for the Español.jsonl Spanish dictionary. Provides memory-efficient access patterns for pipeline operations.

## Provider Overview

### Core Interface (Minimal Implementation)
```python
class JSONLDataProvider(DataProvider):
    """Memory-efficient JSONL data provider for large dictionary files"""

    def get_word(self, word: str) -> dict | None:
        """Get single word entry by exact match"""

    def get_words_batch(self, words: list[str]) -> dict[str, dict]:
        """Get multiple words efficiently - core method for vocabulary pipeline"""

    def exists_word(self, word: str) -> bool:
        """Check if word exists without loading full entry"""
```

## Architecture Design

### Indexing Strategy
**Index Structure** (`.español_index.json`):
```json
{
  "metadata": {
    "file_path": "Español.jsonl",
    "total_entries": 850000,
    "index_version": "1.0",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "word_index": {
    "llamar": 12485760,
    "casa": 8294850,
    // word -> byte position mapping
  }
}
```

### Memory Efficiency
- **Index Only**: Keep only word→position mapping in memory (~50MB for 800k words)
- **Streaming Access**: Read individual entries using file seek operations
- **Batch Optimization**: Group seeks by file position for batch queries
- **No Full Load**: Never load entire 1GB file into memory

### File Access Pattern
1. **Build Index** (first run): Stream through JSONL, record word positions
2. **Load Index** (subsequent runs): Load lightweight position mapping
3. **Query Access**: Seek to position, read single JSON line, parse entry
4. **Batch Access**: Sort positions, sequential reads to minimize seeks

## Implementation Details

### Index Building (One-time Setup)
```python
def _build_index(self) -> dict[str, int]:
    """Build word->position index by streaming through JSONL"""
    index = {}
    with open(self.jsonl_path, 'rb') as file:
        position = 0
        for line in file:
            entry = json.loads(line.decode('utf-8'))
            if 'word' in entry:
                index[entry['word']] = position
            position = file.tell()
    return index
```

### Efficient Word Lookup
```python
def get_word(self, word: str) -> dict | None:
    """O(1) word lookup using index"""
    if word not in self.index:
        return None

    position = self.index[word]
    with open(self.jsonl_path, 'rb') as file:
        file.seek(position)
        line = file.readline()
        return json.loads(line.decode('utf-8'))
```

### Batch Access Optimization
```python
def get_words_batch(self, words: list[str]) -> dict[str, dict]:
    """Optimized batch access with position sorting"""
    # Get positions for existing words
    positions = []
    for word in words:
        if word in self.index:
            positions.append((word, self.index[word]))

    # Sort by file position for sequential access
    positions.sort(key=lambda x: x[1])

    # Sequential reads
    results = {}
    with open(self.jsonl_path, 'rb') as file:
        for word, position in positions:
            file.seek(position)
            line = file.readline()
            results[word] = json.loads(line.decode('utf-8'))

    return results
```

## Configuration Integration

### Provider Configuration (`config.json`)
```json
{
  "providers": {
    "data": {
      "spanish_dictionary": {
        "type": "jsonl",
        "file_path": "data/Español.jsonl",
        "pipelines": ["vocabulary", "conjugation"],
        "read_only": true,
        "build_index": true,
        "index_cache_path": "data/.español_index.json"
      }
    }
  }
}
```

### Provider Registry Integration
```python
# src/providers/data/jsonl_provider.py
class JSONLDataProvider(DataProvider):
    def __init__(self, config: dict):
        super().__init__()
        self.jsonl_path = Path(config["file_path"])
        self.index_path = Path(config.get("index_cache_path", f".{self.jsonl_path.stem}_index.json"))
        self.build_index = config.get("build_index", True)
        self.index = self._load_or_build_index()
```

## Error Handling

### Robust Access Patterns
- **Missing Words**: Return `None` instead of exceptions
- **Corrupted Lines**: Skip and log warnings, continue processing
- **File Access Errors**: Graceful degradation with clear error messages
- **Index Corruption**: Rebuild index automatically on validation failure

### Validation Strategy
```python
def _validate_index(self) -> bool:
    """Validate index integrity"""
    try:
        # Check if JSONL file modified since index creation
        jsonl_mtime = self.jsonl_path.stat().st_mtime
        index_mtime = self.index_path.stat().st_mtime
        return index_mtime > jsonl_mtime
    except (OSError, KeyError):
        return False
```

## Performance Characteristics

### Expected Performance
- **Index Load Time**: ~100ms for 800k entries
- **Single Lookup**: ~1-2ms (disk seek + JSON parse)
- **Batch Lookup (100 words)**: ~50-100ms (optimized sequential reads)
- **Memory Usage**: ~50MB index + minimal per-query overhead

### Scalability
- **File Size**: Scales to multi-GB JSONL files
- **Query Volume**: Efficient for both single and batch queries
- **Concurrent Access**: Thread-safe read operations

## Integration Points

### Stage 2 Usage Pattern
```python
def _execute_impl(self, context: PipelineContext) -> StageResult:
    providers = context.get("providers", {})
    spanish_dict = providers.get("data", {}).get("spanish_dictionary")

    if not spanish_dict:
        return StageResult.failure("Spanish dictionary provider not configured")

    selected_words = context.get("selected_words", [])
    dictionary_data = spanish_dict.get_words_batch(selected_words)

    # Process dictionary_data...
```

### Future Extension Points
When other pipelines need additional functionality:
- `get_words_by_frequency_range()` - for frequency-based selection
- `get_words_by_pos()` - for part-of-speech filtering
- `stream_all_entries()` - for full dataset analysis
- Extended indexing (POS, frequency, etc.)

## File Structure
```
src/providers/data/
├── __init__.py
├── json_provider.py     # Existing JSON provider
└── jsonl_provider.py    # New JSONL provider implementation
```
