# E2E Test Specifications for Infrastructure-Only Testing

## Overview

This document defines E2E test scenarios that validate core system infrastructure without requiring real pipeline or stage implementations. Tests focus on infrastructure coordination, CLI integration, and provider system validation using minimal test fixtures.

## Architecture Context

**Current State**: Complete core infrastructure with NO concrete pipeline implementations
- **Core**: Pipeline (abstract), PipelineRegistry, Context, Config, Stage (abstract)
- **Providers**: MediaProvider registry, audio/image/sync providers
- **CLI**: Universal pipeline runner with discovery and execution commands
- **Stages**: Abstract stage classes only (`src/stages/base/`)

**Testing Philosophy**: Risk-Based Testing with strategic mocking boundaries and scaffolding lifecycle management.

## Strategic Risk Assessment

### High-Risk Components (Comprehensive E2E Coverage)
- **CLI Pipeline Integration**: Command routing, registry discovery, execution flow
- **Provider Registry System**: Dynamic loading, configuration injection, pipeline assignments
- **Context Management**: Stage-to-stage data flow, state tracking, error accumulation

### Complex Components (Good Unit + Integration Coverage)
- **Configuration System**: Environment substitution, provider config validation
- **Logging Infrastructure**: Context-aware logging, performance monitoring

### Simple Components (Smoke Test Coverage)
- **Abstract Base Classes**: Pipeline, Stage interfaces
- **Utility Functions**: Error formatting, validation helpers

## E2E Test Scenarios

### Scenario 1: CLI Pipeline Discovery and Information Flow

**Purpose**: Validate complete CLI → Registry → Provider workflow without business logic

**Test Flow**:
1. **Setup**: Mock configuration with test pipeline and providers
2. **CLI Command**: `cli list --detailed`
3. **Validation**: Registry initialization, provider loading, output formatting
4. **CLI Command**: `cli info test_pipeline --stages`
5. **Validation**: Pipeline metadata retrieval, stage information display

**Infrastructure Validation**:
- CLI argument parsing and command routing
- Pipeline registry initialization and discovery
- Provider registry creation from configuration
- Configuration loading with environment substitution
- Logging system initialization and context handling

**Test Fixtures Required**:
- `TestPipeline` class implementing Pipeline interface
- `MockTestStage` classes with minimal validation logic
- Test configuration with provider definitions

### Scenario 2: Provider Registry Integration and Pipeline Assignment

**Purpose**: Validate provider loading, configuration injection, and pipeline filtering

**Test Flow**:
1. **Setup**: Configuration with multiple providers and pipeline assignments
2. **Registry Creation**: `ProviderRegistry.from_config()`
3. **Provider Filtering**: `get_providers_for_pipeline("test_pipeline")`
4. **Validation**: Only authorized providers returned for pipeline

**Infrastructure Validation**:
- Dynamic provider loading via registry mappings
- Configuration validation and provider instantiation
- Pipeline assignment filtering logic
- Provider configuration injection patterns
- File conflict validation for data providers

**Test Fixtures Required**:
- Mock audio/image/sync providers with configuration injection
- Test data providers with file management
- Configuration with complex provider assignments

### Scenario 3: CLI Execution Flow with Context Management

**Purpose**: Validate end-to-end stage execution infrastructure

**Test Flow**:
1. **Setup**: Test pipeline with multiple stages and dependencies
2. **CLI Command**: `cli run test_pipeline --stage test_stage --dry-run`
3. **Validation**: Context creation, stage retrieval, dry-run display
4. **CLI Command**: `cli run test_pipeline --phase test_phase --execute`
5. **Validation**: Phase execution, context flow, error handling

**Infrastructure Validation**:
- CLI argument validation and pipeline lookup
- Context creation and provider injection
- Stage execution wrapper with timing and logging
- Phase execution with fail-fast logic
- Error propagation and result aggregation

**Test Fixtures Required**:
- `TestStage` with context validation and data flow
- `TestPipeline` with phases and stage dependencies
- Mock providers for context injection

### Scenario 4: Configuration System and Environment Integration

**Purpose**: Validate configuration loading, environment substitution, and error handling

**Test Flow**:
1. **Setup**: Configuration files with environment variables
2. **Environment**: Set test environment variables
3. **Config Loading**: `Config.load()` with substitution
4. **Validation**: Environment variable replacement, nested processing
5. **Error Testing**: Invalid configuration handling

**Infrastructure Validation**:
- JSON configuration loading and parsing
- Recursive environment variable substitution
- Provider configuration validation
- Graceful degradation for missing files
- Error messaging for invalid configurations

**Test Fixtures Required**:
- Test configuration files with environment variables
- Invalid configuration files for error testing

### Scenario 5: Logging and Performance Monitoring Integration

**Purpose**: Validate logging infrastructure and performance monitoring

**Test Flow**:
1. **Setup**: Enable verbose logging mode
2. **Pipeline Execution**: Run test pipeline with stages
3. **Validation**: Context-aware logging, performance timing, icons
4. **Log Analysis**: Verify log levels, timing data, error handling

**Infrastructure Validation**:
- Logging configuration setup and environment detection
- Context-aware logger creation
- Performance monitoring decorators
- Colored console output formatting
- Test environment logging behavior

**Test Fixtures Required**:
- Test pipeline with logged operations
- Performance monitoring validation

## Mock Strategy and Implementation

### External Dependencies (MOCK)

**Provider APIs**: Mock all external service calls
```python
@pytest.fixture
def mock_forvo_api():
    with patch('src.providers.audio.forvo_provider.requests') as mock:
        mock.get.return_value.json.return_value = {"items": []}
        yield mock
```

**File System Operations**: Mock file I/O for provider testing
```python
@pytest.fixture
def mock_filesystem():
    with patch('pathlib.Path.exists'), patch('pathlib.Path.mkdir'):
        yield
```

**Network Dependencies**: Mock all HTTP requests
```python
@pytest.fixture
def mock_requests():
    with patch('requests.Session') as mock:
        yield mock
```

### Internal Systems (TEST DIRECTLY)

**Pipeline Infrastructure**: Test registry, context, execution flow directly
**Configuration System**: Test JSON loading, environment substitution directly
**Local Data Operations**: Test context data flow, stage completion tracking directly

### Centralized Mock Patterns

**Provider Mock Factory**:
```python
def create_mock_media_provider(provider_type: str, config: dict) -> MediaProvider:
    """Factory for creating consistent mock providers"""

class MockTestPipeline(Pipeline):
    """Minimal pipeline implementation for infrastructure testing"""

class MockTestStage(Stage):
    """Minimal stage implementation with configurable behavior"""
```

## Test Fixture Architecture

### Minimal Pipeline Fixtures

**TestPipeline**: Concrete Pipeline implementation
- Implements all abstract methods with test values
- Provides configurable stages and phases
- Supports context validation testing

**TestStage Variants**:
- `SuccessStage`: Always returns success
- `FailureStage`: Always returns failure with configurable errors
- `ContextDependentStage`: Tests context validation and data flow
- `ProviderUsingStage`: Tests provider access and integration

### Configuration Fixtures

**Base Configuration**: Minimal valid configuration
```json
{
  "providers": {
    "data": {
      "test_data": {"type": "json", "pipelines": ["test_pipeline"]}
    },
    "audio": {
      "test_audio": {"type": "forvo", "pipelines": ["test_pipeline"]}
    }
  }
}
```

**Complex Configuration**: Multi-provider, multi-pipeline setup
**Invalid Configuration**: Various error scenarios for validation testing

### Provider Mock Fixtures

**MockProviderRegistry**: Pre-populated registry for consistent testing
**MockProviders**: Configurable behavior for different test scenarios
**ProviderConfigFixtures**: Various configuration permutations

## Implementation Guidelines

### Test Organization

Following `context/testing/strategy/test-organization.md` patterns:

```
tests/
├── e2e/
│   ├── test_cli_pipeline_integration.py      # Scenario 1
│   ├── test_provider_registry_integration.py # Scenario 2
│   ├── test_context_execution_flow.py        # Scenario 3
│   ├── test_configuration_integration.py     # Scenario 4
│   └── test_logging_performance_integration.py # Scenario 5
├── fixtures/
│   ├── pipelines.py    # TestPipeline, TestStage implementations
│   ├── providers.py    # Mock provider factories
│   ├── configs.py      # Configuration fixtures
│   └── contexts.py     # Context and data fixtures
└── utils/
    ├── assertions.py   # Custom assertion helpers
    └── mocks.py       # Centralized mock factories
```

### Risk-Based Implementation Priority

1. **High-Risk E2E Tests** (Scenarios 1-3): Full workflow validation
2. **Complex Integration Tests**: Provider registry, configuration system
3. **Simple Smoke Tests**: Abstract interfaces, utility functions

### Scaffolding Lifecycle Strategy

**Development Phase**: Comprehensive validation during infrastructure building
- Over-testing acceptable for development velocity
- Detailed validation of all infrastructure patterns
- Quick bug identification through extensive coverage

**Production Transition**: Consolidate to risk-based minimal set
- Keep only high-risk scenario coverage
- Eliminate tests that don't mitigate identified risks
- Consolidate multiple scaffolding tests into single multi-risk tests

## Risk Assessment and Prioritization

### Critical Workflows (Must Have E2E Coverage)
1. **CLI → Registry → Provider → Execution** (Primary user workflow)
2. **Configuration Loading → Provider Setup** (System initialization)
3. **Context Flow → Stage Execution → Error Handling** (Core pipeline behavior)

### Secondary Workflows (Good Integration Coverage)
1. **Provider Assignment and Filtering** (Multi-pipeline scenarios)
2. **Performance Monitoring and Logging** (Observability)
3. **Environment Configuration Processing** (Deployment scenarios)

### Ad-hoc Scenarios (Smoke Test Coverage)
1. **Abstract Interface Compliance** (Basic functionality)
2. **Utility Function Behavior** (Helper methods)
3. **Error Message Formatting** (User experience)

## Success Criteria

Tests validate infrastructure when:

1. **Complete CLI workflows** execute without business logic dependencies
2. **Provider systems** load and filter correctly with mocked external services
3. **Context management** handles data flow and state tracking across stages
4. **Configuration system** processes environment variables and validates providers
5. **Registry coordination** manages pipeline discovery and provider assignment
6. **Error handling** propagates failures appropriately through the system
7. **Performance monitoring** captures timing and logging data correctly

## Maintenance Strategy

**Test Maintenance Costs**: Keep fixtures minimal to reduce maintenance overhead
**Mock Boundaries**: Use centralized patterns for consistent behavior
**Risk Evolution**: Update test priorities as business logic is implemented
**Scaffolding Cleanup**: Aggressive elimination when transitioning to production testing

This E2E strategy enables comprehensive infrastructure validation while maintaining the flexibility to add real pipeline implementations incrementally.
