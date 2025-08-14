# Workflow Refactor - New System Design

## Problem Summary
Original `generate_batch.py` had several critical issues:
- **Hardcoded batch data** - only worked for su + para
- **Missing CardID field** - Anki rejected cards as empty
- **Wrong image format** - HTML tags vs filename-only
- **Media not stored** - files existed locally but not in Anki
- **Rigid architecture** - couldn't handle dynamic word processing

## New Workflow Design

### Phase 1: Content Generation (Claude)
1. **User provides image prompts** for each meaning
2. **Claude analyzes** word meanings and creates batch plan
3. **Claude updates vocabulary.json** with:
   - User prompts for each meaning
   - Generated sentences using internal knowledge
   - IPA pronunciations using internal knowledge
   - All required card fields (matching Anki exactly)
4. **Schema synchronization**: vocabulary.json now mirrors Anki field structure

### Phase 2: Media Sync Script
- **Script**: `media_sync.py` (planned)
- **Function**: Validates vocabulary.json vs local media files
- **Logic**:
  - Check missing images/audio against vocabulary.json
  - If >5 missing → hard fail, raise to user
  - Generate missing media via OpenAI/Forvo APIs
  - Wait 5 seconds for completion, then validate
  - If failures → raise to user

### Phase 3: Anki Sync Script  
- **Script**: `anki_sync.py` (planned)
- **Function**: Syncs local media and cards to Anki
- **Logic**:
  - vocabulary.json is golden source
  - Check Anki media directory and cards
  - Store missing media files via base64
  - Create missing cards with proper formatting
  - If Anki unavailable → auto-launch and retry
  - If inconsistencies → vocabulary overwrites Anki

## Implemented Architecture

### Modular Code Structure
```
src/
├── anki/
│   ├── connection.py          # Anki connection & setup utilities
│   └── __init__.py
├── validation/
│   ├── vocabulary_validator.py # Structure validation against schema
│   ├── sync_validator.py      # Sync validation between systems
│   └── __init__.py
└── __init__.py

# Entry points
validate_vocabulary.py         # Validates vocabulary.json structure
validate_anki_sync.py         # Validates sync between systems
```

### Configuration-Driven Validation
- **Schema definitions** in `config.json` for all validation rules
- **Field patterns** with regex validation for data integrity
- **Business constraints** for content quality checks
- **Separation of concerns** - Anki connection vs validation logic

### Data Schema Synchronization
- **Perfect field mapping** - vocabulary.json matches Anki card structure exactly
- **All 13 Anki fields** included: CardID, SpanishWord, IPA, MeaningContext, etc.
- **New prompt field** added for image generation workflow
- **Unicode handling** fixed for proper character display

## Key Improvements

### Flexibility
- No hardcoded data - fully dynamic processing
- Claude handles content generation via system instructions
- Scripts handle technical sync only
- Modular architecture allows targeted fixes

### Error Recovery
- Individual validation scripts for different concerns
- 5-file limit prevents token waste
- Clear failure points with detailed error reporting
- Field-by-field comparison for precise troubleshooting

### Validation & Quality Assurance
- **Structure validation** - vocabulary.json schema compliance
- **Sync validation** - vocabulary.json ↔ Anki consistency
- **Pattern validation** - field formats (IPA, CardID, etc.)
- **Content validation** - minimum lengths, required blanks, etc.

### Robustness
- Configuration-driven validation rules
- Proper CardID and image formatting
- Integrated media storage pipeline
- Connection handling with auto-launch

## Validation Results

### Current System Status
- **✅ Sync Validation**: vocabulary.json and Anki perfectly synchronized (45 cards)
- **✅ Structure Validation**: vocabulary.json schema compliant after haber fixes
- **✅ Field Mapping**: All Anki fields properly represented in vocabulary.json
- **✅ Data Integrity**: All patterns, constraints, and cross-references valid

### Fixed Issues
1. **CardID pattern** - Updated regex to allow numbers (fixed 22 format errors)
2. **GappedSentence blanks** - Fixed 3 haber cards missing `_____` placeholders
3. **Field synchronization** - vocabulary.json now has exact Anki field structure
4. **Unicode encoding** - Proper display of Spanish characters (ó, é, ñ, etc.)

## Implementation Notes
- **Validation architecture** - Separate modules for different validation types
- **Configuration management** - All validation rules externalized to config
- **Error reporting** - Detailed, actionable error messages with locations
- **Path handling** - Scripts work from any directory with proper imports
- **Type safety** - Full type hints and structured error handling

## Current Status
- **✅ Architecture refactored** with proper separation of concerns
- **✅ Validation system** implemented and working perfectly
- **✅ Data schema** synchronized between vocabulary.json and Anki
- **✅ Como batch** completed successfully (4 cards)
- **🔄 Ready** for new workflow implementation
- **📋 Next word**: **tener** (ready for new workflow)

## Workflow Integration
The new system supports the planned workflow:
1. **Claude content generation** → updates vocabulary.json with proper schema
2. **Media sync validation** → checks/generates missing media files
3. **Anki sync validation** → ensures perfect system synchronization
4. **Continuous validation** → maintains data integrity throughout process