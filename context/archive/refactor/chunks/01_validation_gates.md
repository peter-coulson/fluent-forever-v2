# Session 1: Validation Gates Setup

## Mission
Create minimal, focused validation gates that ensure each refactor session delivers working functionality. These tests validate real implementations, not mocks.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `src/cli/` - Current CLI commands to preserve functionality
- `vocabulary.json` - Current data structure to maintain compatibility

## Objectives

### Primary Goal
Create **lightweight integration tests** that validate each stage of the refactor works correctly. Focus on **user workflows**, not internal architecture details.

### Testing Philosophy
- **Minimal tests** - Only what's needed to catch breaking changes
- **Real implementations** - Test actual code, not mocks
- **User-focused** - Test CLI commands and file outputs users care about
- **Fast feedback** - All tests run in <10 seconds

## Implementation Requirements

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures, minimal mocking
├── test_current_system.py   # Validate current vocabulary system works
└── validation_gates/        # One simple test per refactor session
    ├── test_session2_core.py      # Core architecture validation
    ├── test_session3_stages.py    # Stage system validation  
    ├── test_session4_providers.py # Provider system validation
    ├── test_session5_cli.py       # CLI system validation
    ├── test_session6_config.py    # Configuration validation
    ├── test_session7_vocabulary.py # Vocabulary pipeline validation
    ├── test_session8_multi.py     # Multi-pipeline validation
    └── test_session9_docs.py      # Documentation validation
```

### Test Implementation Pattern

Each session gets **exactly one focused test** that validates the key deliverable:

```python
# tests/validation_gates/test_session2_core.py
def test_core_architecture():
    """Validation gate for Session 2: Core Architecture"""
    # Test that pipeline registry and basic execution works
    from src.core.registry import get_pipeline_registry
    from src.pipelines.vocabulary import VocabularyPipeline
    
    registry = get_pipeline_registry()
    pipeline = VocabularyPipeline()
    
    # Can register pipeline
    registry.register(pipeline)
    assert "vocabulary" in registry.list_pipelines()
    
    # Can execute a basic stage
    context = {"test": "data"}
    result = pipeline.execute_stage("prepare", context)
    assert result["status"] == "success"

# tests/validation_gates/test_session7_vocabulary.py  
def test_vocabulary_pipeline_migration():
    """Validation gate for Session 7: Complete vocabulary workflow through new architecture"""
    # Test full word-to-card workflow using new pipeline system
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "run", "vocabulary",
        "--stage", "claude_batch", "--words", "test_word"
    ], capture_output=True)
    
    assert result.returncode == 0
    # Verify vocabulary.json updated correctly
    # Verify can generate media and sync to Anki
```

### Current System Baseline Test

```python
# tests/test_current_system.py
def test_current_vocabulary_workflow():
    """Baseline test - current system must continue working during refactor"""
    with temp_workspace():
        # Test key current commands still work
        commands = [
            ["python", "-m", "cli.prepare_claude_batch", "--words", "casa"],
            ["python", "-m", "cli.media_generate", "--cards", "test_card", "--no-execute"],
            ["python", "-m", "cli.sync_anki_all", "--dry-run"]
        ]
        
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True)
            assert result.returncode == 0, f"Command failed: {' '.join(cmd)}"
```

## Validation Strategy Per Session

### Session 2 (Core Architecture)
**One test**: Can create, register, and execute basic pipeline stages

### Session 3 (Stage System)  
**One test**: Can chain stages and pass data between them

### Session 4 (Provider System)
**One test**: Can abstract external APIs and switch providers

### Session 5 (CLI System)
**One test**: Universal CLI can discover and execute pipelines

### Session 6 (Configuration)
**One test**: Unified configuration system loads and validates correctly

### Session 7 (Vocabulary Pipeline)
**One test**: Complete vocabulary workflow works through new architecture

### Session 8 (Multi-Pipeline)
**One test**: Both vocabulary and conjugation pipelines work simultaneously

### Session 9 (Documentation)
**One test**: All documentation files are valid and accessible

## Mock Strategy

**Minimal mocking** - Only mock what's absolutely necessary:
- External APIs (OpenAI, Forvo, AnkiConnect) 
- File system operations that would affect host system
- Network requests

**Don't mock** internal architecture - test real implementations.

## Success Criteria

### Must Pass Before Session Completion
1. ✅ Current system baseline test passes (no regressions)
2. ✅ Session-specific validation gate passes
3. ✅ All previous session validation gates still pass
4. ✅ Tests run in <10 seconds total

### Quality Validation
- Tests fail appropriately when implementations are wrong
- Tests use real implementations, not mocks
- Each test focuses on one key capability per session
- Fast feedback for development

## Deliverables

### 1. Lightweight Test Suite
- ~10 focused integration tests total
- Real implementation testing
- Fast execution (<10 seconds)

### 2. Current System Baseline
- Comprehensive test of existing vocabulary functionality
- Ensures no regressions during refactor
- Documents current behavior as specification

### 3. Per-Session Validation Gates
- One focused test per refactor session
- Tests key deliverable of each session
- Progressive validation (later tests include earlier functionality)

## Implementation Notes

### Focus Areas
- **Real workflows** - Test actual CLI commands and file outputs
- **Key integrations** - Test that stages work together correctly  
- **User impact** - Test functionality users depend on
- **Fast feedback** - Keep total test time under 10 seconds

### Avoid
- Testing internal implementation details
- Over-mocking (test real code when possible)
- Comprehensive edge case testing (that's for unit tests)
- Slow tests that depend on external services

---

**This approach provides validation gates without over-engineering. Each session gets exactly the testing it needs to ensure quality delivery.**