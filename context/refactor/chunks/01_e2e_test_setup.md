# Session 1: E2E Test Setup

## Mission
Create comprehensive end-to-end tests that serve as immutable validation gates for all future refactor sessions. These tests define the contract that each implementation must meet.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `src/` - Current system to understand existing functionality
- `MULTI_CARD_SYSTEM.md` - Multi-card system documentation

## Objectives

### Primary Goal
Create E2E test suite that validates:
1. **Current System Functionality** - Ensure existing vocabulary pipeline continues working
2. **Target Architecture Contracts** - Define interfaces that future sessions must implement  
3. **Integration Points** - Test how components interact across the system
4. **Regression Prevention** - Catch breaking changes during refactor

### Test Categories to Create

#### 1. Core Architecture Tests (`tests/e2e/01_core_architecture/`)
- `test_pipeline_registry.py` - Pipeline creation, registration, discovery
- `test_pipeline_execution.py` - Basic pipeline execution patterns
- `test_pipeline_interface.py` - Pipeline abstract interface compliance

#### 2. Stage System Tests (`tests/e2e/02_stage_system/`)
- `test_stage_execution.py` - Individual stage execution
- `test_stage_chaining.py` - Multiple stages in sequence
- `test_stage_error_handling.py` - Stage failure scenarios

#### 3. Provider System Tests (`tests/e2e/03_provider_system/`)
- `test_data_providers.py` - Data source abstraction (vocabulary.json, etc.)
- `test_media_providers.py` - Image/audio generation abstraction
- `test_sync_providers.py` - Anki sync abstraction

#### 4. CLI System Tests (`tests/e2e/04_cli_system/`)  
- `test_pipeline_runner.py` - Universal CLI pipeline execution
- `test_command_discovery.py` - Pipeline and stage discovery
- `test_backward_compatibility.py` - Old functionality accessible via new CLI

#### 5. Configuration Tests (`tests/e2e/05_configuration/`)
- `test_config_loading.py` - Unified configuration loading
- `test_pipeline_configs.py` - Pipeline-specific configuration
- `test_provider_configs.py` - Provider configuration

#### 6. Vocabulary Pipeline Tests (`tests/e2e/06_vocabulary_pipeline/`)
- `test_full_vocabulary_workflow.py` - Complete E2E vocabulary card creation
- `test_claude_batch_integration.py` - Claude staging workflow
- `test_media_generation_integration.py` - Media creation workflow
- `test_anki_sync_integration.py` - Anki synchronization workflow

#### 7. Multi-Pipeline Tests (`tests/e2e/07_multi_pipeline/`)
- `test_multiple_pipelines.py` - Vocabulary + conjugation coexistence
- `test_pipeline_isolation.py` - Pipelines don't interfere with each other
- `test_shared_resources.py` - Shared providers work across pipelines

#### 8. Documentation Tests (`tests/e2e/08_documentation/`)
- `test_documentation_structure.py` - Context system organization
- `test_markdown_validation.py` - All markdown files are valid

## Implementation Requirements

### Test Structure
```
tests/
├── e2e/                           # End-to-end tests (YOU CREATE)
│   ├── conftest.py               # Shared fixtures and utilities
│   ├── 01_core_architecture/     # Session 2 validation gates
│   ├── 02_stage_system/          # Session 3 validation gates  
│   ├── 03_provider_system/       # Session 4 validation gates
│   ├── 04_cli_system/            # Session 5 validation gates
│   ├── 05_configuration/         # Session 6 validation gates
│   ├── 06_vocabulary_pipeline/   # Session 7 validation gates
│   ├── 07_multi_pipeline/        # Session 8 validation gates
│   └── 08_documentation/         # Session 9 validation gates
├── unit/                         # Unit tests (existing)
└── integration/                  # Integration tests (existing)
```

### Test Guidelines

#### Immutable Contracts
- **DO NOT modify these tests once created** - they define the contract
- Tests should focus on **external interfaces and behavior**
- Use **mocking for external dependencies** (APIs, file system)
- Tests must be **deterministic and fast**

#### Test Patterns
```python
# Example contract test pattern
def test_pipeline_registration():
    """Contract: Pipelines can be registered and discovered"""
    registry = get_pipeline_registry()
    
    # Should be able to register new pipeline
    pipeline = MockPipeline()
    registry.register(pipeline)
    
    # Should be discoverable
    assert pipeline.name in registry.list_pipelines()
    assert registry.get_pipeline(pipeline.name) == pipeline

def test_stage_execution():
    """Contract: Stages can be executed with context"""
    stage = MockStage()
    context = PipelineContext(data={'test': 'value'})
    
    # Should execute and return result
    result = stage.execute(context)
    assert isinstance(result, StageResult)
    assert result.success is True
```

#### Mock Infrastructure
Create comprehensive mocking for:
- **AnkiConnect API** - Mock all Anki operations
- **OpenAI API** - Mock image generation
- **Forvo API** - Mock audio downloads
- **File System** - Mock data file operations
- **External Commands** - Mock any subprocess calls

## Validation Checklist

### Test Coverage Requirements
- [ ] All 8 test categories created with representative tests
- [ ] Mock infrastructure supports isolated testing
- [ ] Tests run in <30 seconds total
- [ ] Tests are deterministic (no flaky tests)
- [ ] Test documentation explains contract being validated

### Quality Gates  
- [ ] All current CLI commands have equivalent test coverage
- [ ] All existing vocabulary functionality is tested
- [ ] All planned architecture components have contract tests
- [ ] Tests include both success and failure scenarios
- [ ] Mock objects support all required test scenarios

### Documentation Requirements
- [ ] `tests/e2e/README.md` explains test structure and purpose
- [ ] Each test file has clear docstrings explaining contracts
- [ ] Mock usage documented for future developers
- [ ] Test execution instructions provided

## Deliverables

### 1. Comprehensive E2E Test Suite
- Complete test structure as outlined above
- All tests passing (using mocks as needed)
- Clear documentation of what each test validates

### 2. Mock Infrastructure
- Mock classes for all external dependencies
- Configurable mocks for different test scenarios
- Documentation on how to use mocks

### 3. Test Execution Framework
- pytest configuration optimized for E2E tests
- Test categorization and selection
- CI-ready test execution

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/01_e2e_test_setup_handoff.md` with:
- Overview of created test structure
- Mock infrastructure capabilities
- How future sessions should use these tests
- Any implementation insights for next session

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All E2E tests execute successfully
2. ✅ Test suite runs in <30 seconds
3. ✅ Mock infrastructure supports all planned functionality
4. ✅ Documentation clearly explains test contracts
5. ✅ Handoff document provides clear guidance for Session 2

### Quality Validation
- Tests fail appropriately when contracts are broken
- Mock objects behave realistically
- Test coverage includes edge cases and error scenarios
- Documentation is clear and actionable

## Notes for Implementation

### Focus Areas
- **Contract Definition** - Tests should define "what" not "how"  
- **Interface Testing** - Test public APIs that will be stable
- **Integration Points** - Test how components work together
- **Regression Prevention** - Ensure existing functionality is preserved

### Avoid
- Testing implementation details that may change
- Brittle tests that break with minor refactors
- Slow tests that depend on external services
- Tests that require manual setup or configuration

---

**Remember: These tests are the validation gates for all future sessions. They must be comprehensive, reliable, and focused on contracts rather than implementation details.**