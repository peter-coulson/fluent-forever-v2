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
   - All required card fields
4. **Migration strategy**: Fill empty prompts for existing words

### Phase 2: Media Sync Script
- **Script**: `media_sync.py`
- **Function**: Validates vocabulary.json vs local media files
- **Logic**:
  - Check missing images/audio against vocabulary.json
  - If >5 missing → hard fail, raise to user
  - Generate missing media via OpenAI/Forvo APIs
  - Wait 5 seconds for completion, then validate
  - If failures → raise to user

### Phase 3: Anki Sync Script  
- **Script**: `anki_sync.py`
- **Function**: Syncs local media and cards to Anki
- **Logic**:
  - vocabulary.json is golden source
  - Check Anki media directory and cards
  - Store missing media files via base64
  - Create missing cards with proper formatting
  - If Anki unavailable → auto-launch and retry
  - If inconsistencies → vocabulary overwrites Anki

## Key Improvements

### Flexibility
- No hardcoded data - fully dynamic processing
- Claude handles content generation via system instructions
- Scripts handle technical sync only

### Error Recovery
- Individual scripts for targeted fixes
- 5-file limit prevents token waste
- Clear failure points with user notifications

### Simplicity
- vocabulary.json as single source of truth
- No complex state management needed
- Git handles versioning and rollback

### Robustness
- Validation at script start
- Proper CardID and image formatting
- Integrated media storage pipeline

## Implementation Notes
- **Validation**: Basic schema checker for vocabulary.json
- **Timeouts**: 5-second wait for API completion
- **Backup**: Store Anki card type template as insurance
- **Environment**: Scripts handle missing packages gracefully
- **Paths**: Scripts work from any directory

## Current Status
- Como batch completed successfully with manual fixes
- Ready to implement new workflow for future batches
- Next word in queue: **tener**