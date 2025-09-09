# Core Module Test Plan

## Overview
This document outlines the minimum essential tests needed to validate the core functionality of the src module. Tests are focused on critical edge cases and failure modes that could compromise system reliability.

## Test Categories

### 1. Configuration System (`src/core/config.py`)

#### Critical Edge Cases:
- **Config File Missing**: `ConfigManager` with non-existent base path
- **Malformed JSON**: Invalid JSON syntax in config files
- **Circular Dependencies**: Environment variable resolution loops (`${VAR}` → `${VAR2}` → `${VAR}`)
- **Deep Merge Conflicts**: Overlapping nested config structures
- **Environment Override Validation**: `FF_` prefix variable parsing edge cases
- **Config Source Priority**: Incorrect priority ordering between core/pipeline/provider/environment configs

#### Essential Tests:
1. `test_config_manager_missing_base_path()`
2. `test_config_manager_malformed_json_handling()`
3. `test_environment_variable_circular_resolution()`
4. `test_deep_merge_type_conflicts()`
5. `test_config_source_priority_ordering()`

### 2. Pipeline Execution (`src/core/pipeline.py`)

#### Critical Edge Cases:
- **Stage Not Found**: Pipeline requests non-existent stage
- **Context Validation Failure**: Invalid context passed to stage
- **Exception During Execution**: Unhandled exceptions in stage.execute()
- **Incomplete Context**: Missing required context data
- **Stage Success/Failure State Transitions**: Incorrect status handling

#### Essential Tests:
1. `test_pipeline_execute_nonexistent_stage()`
2. `test_pipeline_context_validation_failure()`
3. `test_pipeline_stage_execution_exception_handling()`
4. `test_pipeline_stage_completion_tracking()`

### 3. Registry System (`src/core/registry.py`)

#### Critical Edge Cases:
- **Duplicate Registration**: Same pipeline registered twice
- **Pipeline Not Found**: Get non-existent pipeline
- **Global State Corruption**: Multiple registries or state leaks
- **Registry Initialization**: Empty registry edge cases

#### Essential Tests:
1. `test_registry_duplicate_pipeline_registration()`
2. `test_registry_get_nonexistent_pipeline()`
3. `test_registry_global_state_isolation()`

### 4. Stage System (`src/core/stages.py`) - DETAILED ANALYSIS

#### StageStatus Enum
**Purpose**: Defines execution status types for pipeline stages
**Critical Tests**:
1. **Enum Values Verification**: All 4 status values exist with correct string representations
   - `StageStatus.SUCCESS == "success"`
   - `StageStatus.FAILURE == "failure"`
   - `StageStatus.PARTIAL == "partial"`
   - `StageStatus.SKIPPED == "skipped"`

#### StageResult Dataclass
**Purpose**: Encapsulates stage execution results with dict-like access

**Constructor & Properties Edge Cases**:
- **success property logic**: Only `SUCCESS` status returns `True`, all others `False`
- **Full vs minimal constructor**: All parameters vs required only

**Dict-like Access Critical Edge Cases**:
- **__contains__ method**: Existing vs non-existent attribute checks
- **__getitem__ method**: Valid access vs KeyError for missing attributes
- **get() method**: Default behavior (None) vs custom default values

**Factory Methods Critical Edge Cases**:
- **success_result()**: Message only vs with data dict vs None data handling
- **failure()**: Message only vs with errors list vs None errors handling
- **partial()**: All parameter combinations including None defaults
- **skipped()**: Ensures data={} and errors=[] are set properly

#### Stage Abstract Base Class
**Purpose**: Interface contract for all pipeline stages

**Abstract Contract Edge Cases**:
- **Cannot instantiate**: Direct `Stage()` instantiation must raise TypeError
- **Missing implementations**: Concrete class without required methods fails
- **Proper implementation**: Valid concrete class works correctly

**Required Abstract Methods/Properties**:
- **name property**: Must return string identifier
- **display_name property**: Must return human-readable name
- **execute method**: Must accept PipelineContext, return StageResult

**Default Implementation Edge Cases**:
- **dependencies property**: Empty list default behavior
- **validate_context method**: Empty error list default
- **Method overrides**: Subclass overriding defaults works properly

#### Integration Critical Edge Cases:
- **Stage execution flow**: Concrete stage executes and returns proper StageResult
- **Context validation**: Stage with validation errors vs clean validation
- **Dependencies handling**: Stage with dependencies list vs empty default

#### Essential Tests:
1. `test_stage_status_enum_values()`
2. `test_stage_result_success_property_logic()`
3. `test_stage_result_dict_access_patterns()`
4. `test_stage_result_factory_methods_edge_cases()`
5. `test_stage_abstract_cannot_instantiate()`
6. `test_stage_concrete_implementation_contract()`
7. `test_stage_default_methods_behavior()`
8. `test_stage_context_integration()`

#### Test Structure:
```
tests/unit/core/test_stages.py
├── TestStageStatus (enum validation)
├── TestStageResult (dataclass functionality)
├── TestStageResultFactories (class method edge cases)
├── TestStageABC (abstract contract validation)
└── TestStageIntegration (concrete implementation testing)
```

### 5. Context Management (`src/core/context.py`)

#### Critical Edge Cases:
- **Data Key Conflicts**: Overwriting existing keys with different types
- **Error Accumulation**: Multiple errors and state consistency
- **Stage Completion Tracking**: Duplicate completions, ordering issues
- **Memory Growth**: Context data growing unbounded during pipeline execution

#### Essential Tests:
1. `test_context_data_type_conflicts_on_overwrite()`
2. `test_context_error_accumulation_consistency()`
3. `test_context_stage_completion_duplicate_handling()`
4. `test_context_memory_bounds_during_long_pipeline()`

### 6. Exception Hierarchy (`src/core/exceptions.py`)

#### Critical Edge Cases:
- **Exception Inheritance**: Proper exception catching and inheritance chain
- **Exception Context**: Error messages and context preservation
- **Exception Propagation**: Proper bubbling through pipeline layers

#### Essential Tests:
1. `test_exception_hierarchy_inheritance_chain()`
2. `test_exception_context_preservation_through_pipeline()`

### 7. Provider Integration (`src/providers/base/`)

#### Critical Edge Cases:
- **Provider Unavailability**: Required vs optional provider missing
- **API Call Failures**: Network timeouts, invalid responses, authentication failures
- **Data Provider Edge Cases**: File not found, permission errors, corrupted data
- **Provider Factory/Registry**: Provider instantiation failures

#### Essential Tests:
1. `test_api_stage_required_provider_missing()`
2. `test_api_stage_optional_provider_missing()`
3. `test_data_provider_file_access_edge_cases()`
4. `test_provider_instantiation_failures()`

## Test Implementation Priorities

### Priority 1: System Stability
- Configuration loading failures (simplified - no legacy migration)
- Pipeline execution exception handling
- Registry state corruption
- Context data integrity

### Priority 2: Data Integrity
- Context data type conflicts
- Stage result consistency
- Error accumulation accuracy
- Provider data validation

### Priority 3: Edge Case Robustness
- Malformed inputs
- Resource unavailability
- Concurrent access patterns
- Memory and performance boundaries

## Test Infrastructure Requirements

### Test Fixtures Needed:
- Mock pipeline implementations
- Mock provider implementations
- Test configuration files (valid/invalid)
- Mock stage implementations with controlled failure modes

### Test Environment:
- Isolated configuration directories
- Controlled file system access
- Mock network conditions for API testing
- Memory usage monitoring capabilities

## Coverage Goals

**Minimum Coverage Targets:**
- Configuration loading: 95% (simplified system, no legacy paths)
- Pipeline execution paths: 90%
- Registry operations: 100%
- Context operations: 95%
- Exception paths: 85%

**Focus Areas:**
- Error handling paths (often undertested)
- Edge cases in data structures
- Resource cleanup and state management
- Integration points between modules

## Configuration System Simplifications

**Removed Complexity:**
- ❌ Legacy `config.json` migration logic (~65 lines removed)
- ❌ Dual configuration path support
- ❌ Provider migration from `apis` to `providers` format
- ❌ Fallback configuration loading chains

**Simplified Test Requirements:**
- Single configuration system testing only
- Direct config directory structure validation
- No migration edge case testing needed
- Cleaner environment variable override testing

## Notes

- Tests should focus on **behavioral validation** rather than implementation details
- Each test should validate one specific edge case or failure mode
- Mock external dependencies (file system, network) for deterministic testing
- Prioritize tests that could prevent production failures
- Keep test data minimal but representative of real usage patterns
- **Simplified config system reduces test complexity by ~40%**
