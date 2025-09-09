# Structural Refactor Plan: Strip to Minimal Base

## Overview

This refactor strips the codebase to its absolute minimal essential components while preserving all critical functionality. We remove pipeline-specific implementations, old CLI commands, and preview functionality to create a clean foundation for rebuilding.

## Execution Strategy

**Test-First Approach**: For each phase, we first update tests to reflect the expected new structure, then implement changes until tests pass.

**Code Bug Priority**: When tests fail after implementation, assume it's a code bug first. Only edit tests when absolutely necessary.

## Critical vs Non-Critical Analysis

### **CRITICAL (Must Keep/Migrate)**

**API Functionality** → Migrate to Provider System:
- BaseAPIClient patterns → `providers/base/api_client.py`
- External clients (Forvo, OpenAI, Runware, Anki) → `providers/media/` & `providers/sync/`
- API response/error handling → `providers/base/`

**Configuration** → Migrate to Core:
- ConfigManager hierarchical loading → `core/config.py`
- Config schemas & validation → `core/config_validator.py`

**Generic Validation** → Migrate to Stages:
- IPA validation, media validation → `stages/validation/`
- Base validation patterns → already in `stages/base/`

**Core Infrastructure** (keep/enhance):
- Pipeline engine, providers, stages, registries

### **NON-CRITICAL (Strip/Remove)**

**Old CLI Commands**:
- `media_generate.py`, `preview_server_multi.py`, `sync_anki_multi.py`
- Preview functionality (as requested)
- Pipeline-specific CLI scripts

**Pipeline-Specific Code**:
- Vocabulary-specific validators
- Anki sync validators (move to sync stages)
- `src/sync/` directory (rebuild from scratch)

## Implementation Phases

### **Phase 1: Migration (Preserve Critical Functionality)**

#### Test Updates First:
- [ ] Update tests in `tests/unit/test_apis/` → `tests/unit/test_providers/`
- [ ] Update tests in `tests/unit/test_config/` → `tests/unit/test_core/`
- [ ] Remove vocabulary-specific test files
- [ ] Update import paths in all tests

#### Migration Steps:
- [ ] **1.1 Migrate API Clients**
  - Move `src/apis/base_client.py` → `src/providers/base/api_client.py`
  - Move `src/apis/*_client.py` → `src/providers/media/` & `src/providers/sync/`
  - Update imports throughout codebase
  - Ensure provider interface compatibility

- [ ] **1.2 Migrate Configuration**
  - Move `src/config/config_manager.py` → `src/core/config.py` 
  - Move `src/config/config_validator.py` → `src/core/config_validator.py`
  - Move `src/config/schemas.py` → `src/core/schemas.py`
  - Update all config references

- [ ] **1.3 Migrate Generic Validation**
  - Move `src/validation/ipa_validator.py` → `src/stages/validation/ipa_stage.py`
  - Move `src/validation/internal/media_validator.py` → `src/stages/validation/media_stage.py`
  - Convert validators to stage interface
  - Update imports

**Completion Criteria**: All tests passing after migration

### **Phase 2: Strip Non-Critical Components**

#### Test Updates First:
- [ ] Remove tests for deleted CLI commands
- [ ] Remove tests for pipeline-specific validation
- [ ] Remove tests for old sync system
- [ ] Update remaining tests to not reference deleted modules

#### Strip Steps:
- [ ] **2.1 Remove Old CLI Commands**
  - Delete `src/cli/media_generate.py`
  - Delete `src/cli/preview_server_multi.py`
  - Delete `src/cli/preview_server.py` 
  - Delete `src/cli/sync_anki_multi.py`
  - Delete `src/cli/regenerate_images.py`
  - Keep only `pipeline_runner.py` and `commands/` directory

- [ ] **2.2 Remove Pipeline-Specific Validation**
  - Delete `src/validation/internal/vocabulary_validator.py`
  - Delete `src/validation/anki/` (entire directory)
  - Delete `src/validation/data/` if pipeline-specific
  - Delete `src/validation/media_sync_result.py`

- [ ] **2.3 Remove Old Sync System**
  - Delete entire `src/sync/` directory
  - Remove sync-related imports from other files
  - Ensure sync functionality exists only in `src/stages/sync/` and `src/providers/sync/`

- [ ] **2.4 Remove Old Directory Structure**
  - Delete `src/apis/` (after migration complete)
  - Delete `src/config/` (after migration complete)
  - Delete `src/validation/` (after migration complete)

**Completion Criteria**: All tests passing after stripping

### **Phase 3: Clean Up Dependencies**

- [ ] **3.1 Update Imports**
  - Run find/replace for old import paths
  - Update all references to migrated modules
  - Test that core functionality still works

- [ ] **3.2 Remove Unused Utilities**
  - Audit `src/utils/` for pipeline-specific utilities
  - Keep only generic utilities used by core/providers/stages
  - Remove unused files

- [ ] **3.3 Clean Configuration**
  - Remove pipeline-specific config files from `config/`
  - Keep only generic provider configs and environment configs
  - Update config loading paths

**Completion Criteria**: All tests passing, no unused imports or files

### **Phase 4: Verification**

- [ ] **4.1 Test Core Functionality** 
  - Ensure pipeline runner works
  - Test provider system
  - Test stage system
  - Verify configuration loading

- [ ] **4.2 Update Documentation**
  - Update import examples in docs
  - Remove references to deleted CLI commands
  - Document new minimal structure

**Completion Criteria**: All functionality verified, documentation updated

## Final Structure

After completion, the codebase will have:

```
src/
├── core/                    # Universal pipeline engine + config
│   ├── pipeline.py         # Abstract pipeline definition
│   ├── stages.py           # Standard processing stages
│   ├── registry.py         # Enhanced registry system
│   ├── config.py           # Configuration management (migrated)
│   └── config_validator.py # Config validation (migrated)
├── providers/              # External service abstractions
│   ├── base/               # Base classes + API client (migrated)
│   ├── media/              # Media providers (migrated from apis)
│   ├── data/               # Data source providers
│   └── sync/               # Sync target providers (migrated from apis)
├── stages/                 # Pluggable processing stages
│   ├── base/               # Base stage classes
│   ├── claude/             # Claude interaction stages
│   ├── media/              # Media creation stages
│   ├── validation/         # Validation stages (generic only)
│   └── sync/               # Anki sync stages
├── cli/                    # Minimal CLI framework
│   ├── pipeline_runner.py  # Universal pipeline executor (keep only)
│   └── commands/           # Command plugins per pipeline
└── utils/                  # Generic utilities only
```

## Success Criteria

- ✅ All external connections (Forvo, OpenAI, Runware, Anki) preserved in provider structure
- ✅ All generic validation and configuration functionality preserved
- ✅ Pipeline-specific implementations completely removed
- ✅ Preview functionality stripped as requested
- ✅ Old CLI commands removed
- ✅ All tests passing
- ✅ Clean, minimal codebase ready for rebuilding

## Risk Mitigation

- **Test-First**: Update tests before implementation to catch regressions
- **Incremental**: Complete each phase before moving to next
- **Verification**: Extensive testing after each phase
- **Documentation**: Update docs to reflect new structure

---

**Execution Notes**: 
- Code bugs assumed first when tests fail
- Tests only edited when absolutely necessary
- Each phase completion requires all tests passing
- Preserve all critical external API functionality