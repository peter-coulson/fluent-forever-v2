# Unit Testing Implementation Guide

## Purpose

Executable implementation guide for developing comprehensive unit tests for the Fluent Forever V2 pipeline system. This document provides detailed, actionable specifications for implementing unit tests based on the risk-based testing strategy defined in `UNIT_TESTING_STRATEGY.md`.

## Section 1: Component Test Specifications

### High-Risk Component Implementations

#### PipelineContext (`tests/unit/core/test_context.py`)

**Risk Classification**: High-Risk - Data corruption, state management failures
**Coverage Target**: 95%+ line coverage, 100% public methods
**File Location**: `tests/unit/core/test_context.py`

**Test Methods Required**:
```python
class TestPipelineContext:
    def test_initialization_with_required_params()
    def test_initialization_with_all_params()
    def test_get_existing_key()
    def test_get_nonexistent_key_returns_none()
    def test_get_nonexistent_key_with_default()
    def test_set_new_key_value()
    def test_set_overwrite_existing_key()
    def test_mark_stage_complete_new_stage()
    def test_mark_stage_complete_duplicate_stage()
    def test_add_error_single_error()
    def test_add_error_multiple_errors()
    def test_error_accumulation_across_operations()
    def test_completed_stages_immutability()
    def test_data_isolation_between_operations()
    def test_context_state_consistency_under_errors()
    def test_deep_copy_behavior_for_mutable_data()
    def test_concurrent_access_safety()  # if threading used
```

**Mock Requirements**:
- **External**: Mock file system operations for project_root validation
- **Internal**: Test context data management directly

**Success Criteria**:
- Data integrity maintained across all operations
- Error accumulation works correctly
- Stage completion tracking accurate
- No data leakage between context instances

#### Provider Registry (`tests/unit/providers/test_registry.py`)

**Risk Classification**: High-Risk - Dynamic loading, configuration injection, access control
**Coverage Target**: 95%+ line coverage, 100% public methods
**File Location**: `tests/unit/providers/test_registry.py`

**Test Methods Required**:
```python
class TestProviderRegistry:
    def test_singleton_instance_access()
    def test_register_data_provider_success()
    def test_register_audio_provider_success()
    def test_register_image_provider_success()
    def test_register_sync_provider_success()
    def test_register_duplicate_provider_name_error()
    def test_register_invalid_provider_type_error()
    def test_get_providers_for_pipeline_authorized_only()
    def test_get_providers_for_pipeline_empty_result()
    def test_get_providers_for_pipeline_nonexistent_pipeline()
    def test_create_media_provider_success()
    def test_create_media_provider_invalid_type()
    def test_create_media_provider_missing_config()
    def test_configuration_injection_validation()
    def test_provider_access_control_enforcement()
    def test_file_conflict_validation_success()
    def test_file_conflict_validation_error()
    def test_provider_instantiation_error_handling()
    def test_configuration_processing_environment_vars()
    def test_registry_state_isolation_between_tests()
```

**Mock Requirements**:
- **External**: Mock provider class constructors, configuration files
- **Internal**: Test registry logic and access control directly

**Success Criteria**:
- Dynamic loading works for all provider types
- Access control prevents unauthorized pipeline access
- Configuration injection properly validated
- File conflicts detected and prevented

#### Configuration System (`tests/unit/core/test_config.py`)

**Risk Classification**: High-Risk - Environment substitution, validation, sensitive data
**Coverage Target**: 95%+ line coverage, 100% public methods
**File Location**: `tests/unit/core/test_config.py`

**Test Methods Required**:
```python
class TestConfig:
    def test_load_existing_config_file()
    def test_load_nonexistent_config_file_fallback()
    def test_environment_variable_substitution_simple()
    def test_environment_variable_substitution_with_default()
    def test_environment_variable_substitution_nested()
    def test_environment_variable_missing_no_default()
    def test_recursive_substitution_in_nested_objects()
    def test_recursive_substitution_in_lists()
    def test_get_provider_existing_provider()
    def test_get_provider_nonexistent_provider()
    def test_get_system_settings_access()
    def test_malformed_json_handling()
    def test_circular_environment_reference_detection()
    def test_sensitive_data_substitution_security()
    def test_configuration_validation_provider_format()
    def test_configuration_caching_behavior()
    def test_reload_configuration_on_file_change()
```

**Mock Requirements**:
- **External**: Mock file system, environment variables, JSON loading
- **Internal**: Test substitution and validation logic directly

**Success Criteria**:
- Environment variable substitution accurate in all contexts
- Sensitive data properly handled
- Configuration validation prevents invalid states
- Error handling for malformed configurations

### Complex Component Implementations

#### Pipeline Execution (`tests/unit/core/test_pipeline.py`)

**Risk Classification**: Complex - Stage orchestration, phase execution logic
**Coverage Target**: 80%+ line coverage, all public methods
**File Location**: `tests/unit/core/test_pipeline.py`

**Test Methods Required**:
```python
class TestPipeline:
    def test_execute_stage_success()
    def test_execute_stage_failure()
    def test_execute_stage_nonexistent_stage()
    def test_execute_phase_success()
    def test_execute_phase_partial_failure()
    def test_execute_phase_nonexistent_phase()
    def test_execute_phase_fail_fast_behavior()
    def test_get_stage_valid_stage_name()
    def test_get_stage_invalid_stage_name()
    def test_get_phase_info_existing_phase()
    def test_get_phase_info_nonexistent_phase()
    def test_validate_cli_args_success()
    def test_validate_cli_args_with_errors()
    def test_populate_context_from_cli()
    def test_show_cli_execution_plan_dry_run()
    def test_stage_dependency_validation()
    def test_context_accumulation_across_stages()
```

**Mock Requirements**:
- **External**: Mock stage implementations (use fixtures from `tests/fixtures/pipelines.py`)
- **Internal**: Test pipeline orchestration logic directly

**Success Criteria**:
- Stage execution order correct
- Phase execution handles failures appropriately
- Context passed correctly between stages
- CLI integration works properly

#### Stage Execution Framework (`tests/unit/core/test_stages.py`)

**Risk Classification**: Complex - Performance timing, validation wrapper logic
**Coverage Target**: 80%+ line coverage, all public methods
**File Location**: `tests/unit/core/test_stages.py`

**Test Methods Required**:
```python
class TestStage:
    def test_execute_success_path()
    def test_execute_failure_path()
    def test_execute_context_validation_failure()
    def test_execute_performance_timing()
    def test_execute_logging_integration()
    def test_validate_context_success()
    def test_validate_context_with_errors()
    def test_dependencies_property_access()
    def test_stage_result_success_creation()
    def test_stage_result_failure_creation()
    def test_stage_result_partial_creation()
    def test_stage_result_skipped_creation()
    def test_context_update_on_success()
    def test_context_update_on_failure()
    def test_logger_creation_and_usage()
    def test_execution_wrapper_error_handling()
```

**Mock Requirements**:
- **External**: Mock logging system, performance timing
- **Internal**: Test execution wrapper and validation logic directly

**Success Criteria**:
- Execution wrapper handles all result types
- Performance timing accurate
- Validation logic prevents invalid execution
- Context updates reflect execution results

#### Logging System (`tests/unit/utils/test_logging_config.py`)

**Risk Classification**: Complex - Context-aware configuration, environment detection
**Coverage Target**: 80%+ line coverage, all public methods
**File Location**: `tests/unit/utils/test_logging_config.py`

**Test Methods Required**:
```python
class TestLoggingConfig:
    def test_setup_logging_console_only()
    def test_setup_logging_with_file_output()
    def test_setup_logging_test_environment_detection()
    def test_get_logging_config_default()
    def test_get_logging_config_custom_level()
    def test_get_logger_standard_logger()
    def test_get_context_logger_pipeline_specific()
    def test_log_performance_decorator()
    def test_colored_formatter_output()
    def test_performance_formatter_timing()
    def test_contextual_error_formatting()
    def test_environment_detection_accuracy()
    def test_module_specific_log_levels()
    def test_test_environment_file_logging_disabled()
```

**Mock Requirements**:
- **External**: Mock logging system, environment variables, test detection
- **Internal**: Test configuration logic and formatting directly

**Success Criteria**:
- Environment detection works correctly
- Logging configuration appropriate for context
- Performance timing integration functional
- Test environment behavior correct

### Simple Component Implementations

#### Exception Hierarchy (`tests/unit/core/test_exceptions.py`)

**Risk Classification**: Simple - Basic inheritance, error messages
**Coverage Target**: 60%+ line coverage, smoke tests
**File Location**: `tests/unit/core/test_exceptions.py`

**Test Methods Required**:
```python
class TestExceptions:
    def test_pipeline_error_instantiation()
    def test_stage_error_instantiation()
    def test_context_error_instantiation()
    def test_stage_not_found_error_instantiation()
    def test_configuration_error_instantiation()
    def test_validation_error_instantiation()
    def test_exception_message_formatting()
    def test_exception_inheritance_hierarchy()
```

**Mock Requirements**: None - direct instantiation testing

**Success Criteria**:
- All exception classes instantiate correctly
- Inheritance hierarchy functions properly
- Error messages formatted correctly

#### StageResult (`tests/unit/utils/test_stage_result.py`)

**Risk Classification**: Simple - Data container, factory methods
**Coverage Target**: 60%+ line coverage, smoke tests
**File Location**: `tests/unit/utils/test_stage_result.py`

**Test Methods Required**:
```python
class TestStageResult:
    def test_success_result_factory()
    def test_failure_result_factory()
    def test_partial_result_factory()
    def test_skipped_result_factory()
    def test_success_property_access()
    def test_status_property_access()
    def test_message_property_access()
    def test_data_property_access()
    def test_errors_property_access()
```

**Mock Requirements**: None - direct object testing

**Success Criteria**:
- Factory methods create correct result types
- Properties return expected values
- Result objects behave consistently

#### Pipeline Registry (`tests/unit/core/test_registry.py`)

**Risk Classification**: Simple - Basic registration, discovery
**Coverage Target**: 60%+ line coverage, smoke tests
**File Location**: `tests/unit/core/test_registry.py`

**Test Methods Required**:
```python
class TestPipelineRegistry:
    def test_singleton_access()
    def test_register_pipeline()
    def test_list_pipelines()
    def test_get_pipeline_info_existing()
    def test_get_pipeline_info_nonexistent()
    def test_has_pipeline_existing()
    def test_has_pipeline_nonexistent()
    def test_registry_isolation_between_tests()
```

**Mock Requirements**: Mock pipeline implementations from fixtures

**Success Criteria**:
- Registration and discovery work correctly
- Singleton pattern functions properly
- Pipeline information access accurate

## Section 2: Implementation Roadmap

### Phase 1: High-Risk Components (Immediate Priority)

**Week 1-2: Critical Infrastructure**
1. **Pipeline Context** (`tests/unit/core/test_context.py`)
   - Focus: Data integrity, state management, error accumulation
   - Dependencies: None - foundational component
   - Success criteria: All context operations maintain data integrity

2. **Provider Registry** (`tests/unit/providers/test_registry.py`)
   - Focus: Dynamic loading, access control, configuration injection
   - Dependencies: Configuration system (can mock initially)
   - Success criteria: Registry prevents unauthorized access and handles loading errors

3. **Configuration System** (`tests/unit/core/test_config.py`)
   - Focus: Environment substitution, validation, security
   - Dependencies: None - foundational component
   - Success criteria: All configuration operations secure and validated

### Phase 2: Complex Components (Good Coverage)

**Week 3-4: Core Logic**
1. **Pipeline Execution** (`tests/unit/core/test_pipeline.py`)
   - Focus: Stage orchestration, phase execution
   - Dependencies: Context, Stages (use mock stages from fixtures)
   - Success criteria: Pipeline execution handles all scenarios correctly

2. **Stage Framework** (`tests/unit/core/test_stages.py`)
   - Focus: Execution wrapper, validation, timing
   - Dependencies: Context, Logging (can mock logging)
   - Success criteria: Stage execution framework provides consistent behavior

3. **Logging System** (`tests/unit/utils/test_logging_config.py`)
   - Focus: Environment detection, configuration
   - Dependencies: None - utility component
   - Success criteria: Logging behaves correctly in all environments

### Phase 3: Simple Components (Smoke Tests)

**Week 5: Infrastructure Completion**
1. **Exception Hierarchy** (`tests/unit/core/test_exceptions.py`)
   - Focus: Basic instantiation and inheritance
   - Dependencies: None
   - Success criteria: All exceptions work as expected

2. **StageResult** (`tests/unit/utils/test_stage_result.py`)
   - Focus: Factory methods and property access
   - Dependencies: None
   - Success criteria: Result objects function correctly

3. **Pipeline Registry** (`tests/unit/core/test_registry.py`)
   - Focus: Registration and discovery
   - Dependencies: Mock pipelines from fixtures
   - Success criteria: Registry operations work correctly

## Section 3: File-by-File Implementation Plan

### High-Risk Implementation Details

#### `tests/unit/core/test_context.py`

**Implementation Strategy**: Comprehensive testing with edge cases
**Mock Strategy**: Mock file system operations, test context logic directly
**Validation Pattern**: State integrity assertions after every operation

```python
# Key implementation patterns:
# - Setup: Create context with known state
# - Action: Perform context operation
# - Assert: Verify state consistency
# - Cleanup: Ensure no side effects

@pytest.fixture
def sample_context():
    return PipelineContext(
        pipeline_name="test_pipeline",
        project_root=Path("/test/root")
    )

def test_data_isolation_between_operations(sample_context):
    # Test that data operations don't interfere
    original_data = {"key": "original"}
    sample_context.set("test_data", original_data)

    # Modify retrieved data
    retrieved = sample_context.get("test_data")
    retrieved["key"] = "modified"

    # Verify original data unchanged
    assert sample_context.get("test_data")["key"] == "original"
```

#### `tests/unit/providers/test_registry.py`

**Implementation Strategy**: Focus on dynamic loading and access control
**Mock Strategy**: Mock provider constructors, test registry logic directly
**Validation Pattern**: Access control assertions for security

```python
# Key implementation patterns:
# - Setup: Configure mock providers
# - Register: Add providers with specific configurations
# - Access: Test filtered access based on pipeline
# - Assert: Verify access control enforcement

@pytest.fixture
def mock_registry():
    registry = ProviderRegistry()
    registry.clear()  # Ensure clean state
    return registry

def test_provider_access_control_enforcement(mock_registry):
    # Register provider for specific pipeline
    config = {"pipelines": ["vocabulary"], "api_key": "test"}
    mock_registry.register_audio_provider("forvo", MockAudioProvider, config)

    # Test authorized access
    vocab_providers = mock_registry.get_providers_for_pipeline("vocabulary")
    assert "forvo" in vocab_providers["audio"]

    # Test unauthorized access
    conj_providers = mock_registry.get_providers_for_pipeline("conjugation")
    assert "forvo" not in conj_providers["audio"]
```

#### `tests/unit/core/test_config.py`

**Implementation Strategy**: Focus on environment substitution and validation
**Mock Strategy**: Mock environment variables and file operations
**Validation Pattern**: Security and substitution accuracy assertions

```python
# Key implementation patterns:
# - Setup: Mock environment and file system
# - Load: Test configuration loading and processing
# - Substitute: Test environment variable substitution
# - Assert: Verify security and accuracy

@pytest.fixture
def mock_environment(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    monkeypatch.setenv("BASE_URL", "https://api.example.com")

def test_environment_variable_substitution_security(mock_environment, tmp_path):
    config_content = {
        "providers": {
            "audio": {
                "forvo": {
                    "api_key": "${API_KEY}",
                    "base_url": "${BASE_URL}"
                }
            }
        }
    }

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_content))

    config = Config.load(config_file)
    provider_config = config.get_provider("forvo")

    # Verify substitution worked
    assert provider_config["api_key"] == "secret123"
    assert provider_config["base_url"] == "https://api.example.com"
```

### Complex Component Implementation Details

#### `tests/unit/core/test_pipeline.py`

**Implementation Strategy**: Test orchestration logic with mock stages
**Mock Strategy**: Use fixtures from `tests/fixtures/pipelines.py`
**Validation Pattern**: Execution flow and context accumulation assertions

```python
# Key implementation patterns:
# - Setup: Create pipeline with mock stages
# - Execute: Run stage or phase execution
# - Validate: Check orchestration correctness
# - Assert: Verify context and result state

@pytest.fixture
def mock_pipeline():
    return MockPipeline("test_pipeline", ["stage1", "stage2"])

def test_execute_phase_fail_fast_behavior(mock_pipeline):
    # Add failing stage to pipeline
    mock_pipeline._stages.append("failure_stage")
    mock_pipeline._phases["test_phase"] = ["stage1", "failure_stage", "stage2"]

    context = PipelineContext("test_pipeline", Path("."))
    results = mock_pipeline.execute_phase("test_phase", context)

    # Verify fail-fast: only first two stages executed
    assert len(results) == 2
    assert results[0].success
    assert not results[1].success

    # Verify stage2 was not executed
    assert "stage2" not in context.completed_stages
```

#### `tests/unit/core/test_stages.py`

**Implementation Strategy**: Test execution wrapper and validation logic
**Mock Strategy**: Mock logging, test stage framework directly
**Validation Pattern**: Wrapper behavior and timing assertions

```python
# Key implementation patterns:
# - Setup: Create test stage implementation
# - Execute: Test stage execution wrapper
# - Validate: Check timing and logging
# - Assert: Verify wrapper behavior

class TestStageImpl(Stage):
    @property
    def name(self):
        return "test_stage"

    def _execute_impl(self, context):
        return StageResult.success_result("Test completed")

def test_execute_performance_timing():
    stage = TestStageImpl()
    context = PipelineContext("test", Path("."))

    start_time = time.time()
    result = stage.execute(context)
    end_time = time.time()

    # Verify timing captured (implementation detail)
    assert result.success
    # Verify execution took measurable time
    assert (end_time - start_time) >= 0
```

### Simple Component Implementation Details

#### `tests/unit/core/test_exceptions.py`

**Implementation Strategy**: Basic instantiation and inheritance testing
**Mock Strategy**: None - direct testing
**Validation Pattern**: Smoke test assertions

```python
# Simple instantiation and behavior testing
def test_exception_hierarchy_functions():
    # Test basic instantiation
    pipeline_error = PipelineError("Pipeline failed")
    stage_error = StageError("Stage failed")

    # Test inheritance
    assert isinstance(pipeline_error, Exception)
    assert isinstance(stage_error, PipelineError)

    # Test message formatting
    assert str(pipeline_error) == "Pipeline failed"
    assert str(stage_error) == "Stage failed"
```

## Infrastructure Requirements

### Fixture Development

**Required Fixtures** (extend `tests/fixtures/`):
- **Mock Providers**: Complete mock implementations for all provider types
- **Test Configurations**: Sample config files with various substitution scenarios
- **Sample Contexts**: Pre-configured context objects for testing
- **Test Utilities**: Common assertion and setup helpers

### Test Utilities

**Common Patterns** (`tests/utils/`):
- **Context Assertions**: Validate context state integrity
- **Registry Assertions**: Validate provider access control
- **Configuration Assertions**: Validate substitution accuracy
- **Mock Factories**: Consistent mock object creation

### Setup and Teardown

**Per-Test Requirements**:
- Registry cleanup between tests
- Environment variable restoration
- Temporary file cleanup
- Logger state reset

## Success Criteria

### Implementation Metrics
- **High-Risk**: 95%+ line coverage achieved
- **Complex**: 80%+ line coverage achieved
- **Simple**: 60%+ line coverage achieved
- **All Tests**: Pass consistently in CI environment

### Quality Validation
- **Framework Compliance**: All tests follow risk-based principles
- **Mock Boundaries**: External vs internal testing boundaries respected
- **Consolidation**: Multi-risk validation patterns applied where appropriate
- **Documentation**: Each test file includes clear component validation strategy

### Acceptance Criteria
- **Immediate Execution**: Developer can start with any file-specific implementation
- **Clear Guidance**: Each test specification provides complete implementation details
- **Context Integration**: Heavy reference to established testing context
- **Maintainability**: Test implementation supports long-term code evolution

This implementation guide provides the detailed, actionable specifications needed to develop comprehensive unit tests that implement the risk-based testing framework while ensuring all core components receive appropriate validation coverage.
