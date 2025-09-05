# Fluent Forever V2 - Complete System Refactor

## Overview

Transform the vocabulary-centric system into a true multi-pipeline architecture where any card type can be added seamlessly without touching core infrastructure.

## Goals

### Primary Objectives
1. **Pipeline-Centric Architecture**: Each card type defines its own complete E2E pipeline
2. **Zero-Touch Extensibility**: Adding new card types requires zero changes to core system
3. **Modular Components**: Pluggable stages, providers, and processing steps
4. **Unified CLI Experience**: All card types use consistent command patterns
5. **Clean Architecture**: Clear separation between core engine and card-specific logic

### Success Criteria
- ✅ Vocabulary pipeline works identically to current system
- ✅ Conjugation pipeline fully functional with same patterns
- ✅ New pipeline can be added in <30 minutes with template
- ✅ All CLI commands follow consistent `pipeline run <type> --stage <stage>` pattern
- ✅ Configuration consolidated into logical structure
- ✅ Documentation organized by audience and purpose

## Refactor Strategy

### Test-Driven Approach
- **Session 1**: Create comprehensive E2E tests for all planned functionality
- **Sessions 2-N**: Implement chunks, must pass E2E gates to complete
- **Validation Gates**: Each session has immutable tests that must pass
- **Progressive Coverage**: Later tests include functionality from previous sessions

### No Backwards Compatibility
- Break existing CLI commands during refactor
- Restructure file organization completely
- Focus on clean final architecture, not migration path

## Implementation Phases

### Phase 1: Foundation (Sessions 1-4)
1. **E2E Test Setup**: Create validation gates for all future work
2. **Core Architecture**: Pipeline abstractions, registry, basic CLI framework  
3. **Stage System**: Extract common processing stages into pluggable components
4. **Provider System**: Abstract external APIs and data sources

### Phase 2: Integration (Sessions 5-7)
5. **CLI Overhaul**: Replace all hardcoded scripts with pipeline runner
6. **Configuration Refactor**: Consolidate configs into unified structure
7. **Pipeline Implementation**: Migrate vocabulary to new architecture

### Phase 3: Multi-Pipeline (Sessions 8-9)
8. **Multi-Pipeline Support**: Ensure conjugation + future pipelines work
9. **Documentation Context**: Organize documentation by audience/purpose

## Architecture Vision

### Final Structure
```
src/
├── core/                    # Universal pipeline engine
│   ├── pipeline.py         # Abstract pipeline definition
│   ├── stages.py           # Standard processing stages
│   └── registry.py         # Enhanced registry system
├── pipelines/              # Card-type-specific pipelines
│   ├── vocabulary/         # Fluent Forever pipeline
│   ├── conjugation/        # Conjugation pipeline  
│   └── __template/         # Template for new pipelines
├── stages/                 # Pluggable processing stages
│   ├── claude_staging/     # Claude interaction stages
│   ├── media_generation/   # Media creation stages
│   ├── validation/         # Validation stages
│   └── sync/              # Anki sync stages
├── providers/              # External service abstractions
│   ├── media/             # Image/audio providers
│   ├── data/              # Data source providers
│   └── sync/              # Sync target providers
└── cli/                    # Generic CLI framework
    ├── pipeline_runner.py  # Universal pipeline executor
    └── commands/           # Command plugins per pipeline
```

### Target CLI Experience
```bash
# Discover available pipelines and stages
python -m cli.pipeline list
python -m cli.pipeline info vocabulary

# Execute pipeline stages  
python -m cli.pipeline run vocabulary --stage claude_batch --words por,para
python -m cli.pipeline run conjugation --stage generate_media --cards card1,card2
python -m cli.pipeline run vocabulary --stage sync_anki --execute

# Universal commands work for all pipelines
python -m cli.pipeline preview vocabulary --card-id lo_neuter_article
python -m cli.pipeline preview conjugation --card-id hablar_present_yo
```

## Quality Gates

### E2E Test Coverage
- **Core Architecture**: Pipeline creation, registration, basic execution
- **Stage System**: Stage execution, chaining, error handling
- **Provider System**: API abstraction, mock support, failover
- **CLI System**: All old functionality accessible through new commands
- **Configuration**: All configs load and validate correctly
- **Pipeline Implementation**: Full vocabulary E2E workflow
- **Multi-Pipeline**: Multiple pipelines coexist without conflict
- **Documentation**: All docs organized and accessible

### Session Completion Criteria
Each session must:
1. ✅ Pass all E2E tests for current + previous sessions
2. ✅ Create comprehensive unit tests for new functionality  
3. ✅ Complete validation checklist in session prompt
4. ✅ Create detailed handoff document for next session
5. ✅ Update documentation as needed

## Benefits

### For Developers
- **Clear Architecture**: Obvious place to add new functionality
- **Consistent Patterns**: All pipelines follow same structure
- **Easy Testing**: Mockable providers and isolated stages
- **Self-Documenting**: Pipeline definitions show complete workflow

### For Users  
- **Consistent CLI**: Same commands work for all card types
- **Predictable Behavior**: All pipelines handle errors/config similarly
- **Easy Discovery**: `pipeline list` shows what's available
- **Unified Preview**: Same preview system for all card types

### For System
- **Maintainable**: Clear separation of concerns
- **Extensible**: New pipelines require minimal code
- **Robust**: Comprehensive test coverage
- **Documented**: Organized by audience and purpose

## Risk Mitigation

### During Refactor
- **E2E Tests**: Prevent regression during major restructuring
- **Incremental Validation**: Each session has clear pass/fail criteria  
- **Handoff Documents**: Preserve implementation context between sessions
- **Todo Lists**: Keep sessions focused on specific deliverables

### Post-Refactor
- **Template Pipeline**: Makes adding new card types straightforward
- **Provider Abstraction**: Easy to switch or add external services
- **Comprehensive Tests**: Catch issues before they reach users
- **Clear Documentation**: Reduces onboarding time for new developers

---

**This refactor transforms a vocabulary tool into a general-purpose card creation engine while maintaining the quality and methodology that makes the current system effective.**