# Phase 1 Pipeline Assignment Implementation Plan

## Overview
This document details the implementation plan for adding pipeline-specific provider access control to the Fluent Forever V2 system. The goal is to enable providers to be restricted to specific pipelines while maintaining backward compatibility.

## Current Architecture Analysis

### Provider Registry (`src/providers/registry.py`)
- Current state: Creates providers from config with no pipeline filtering
- Stores providers in type-specific dictionaries: `_data_providers`, `_audio_providers`, `_image_providers`, `_sync_providers`
- Has methods like `get_data_provider(name)`, `register_data_provider(name, provider)`
- `from_config()` method creates providers based on configuration

### RunCommand Context Creation (`src/cli/commands/run_command.py:125-134`)
- Currently injects all "default" providers into context
- No filtering based on pipeline name
- All pipelines get access to all providers

### Configuration System
- Current provider config structure:
```json
{
  "providers": {
    "data": {"type": "json", "base_path": "."},
    "audio": {"type": "forvo"},
    "image": {"type": "runware"},
    "sync": {"type": "anki"}
  }
}
```

## Required Changes

### 1. Configuration Schema Replacement

**New Configuration Format (Only Format Supported):**
```json
{
  "providers": {
    "data": {
      "default": {
        "type": "json",
        "base_path": ".",
        "pipelines": ["vocabulary", "conjugation"]
      }
    },
    "audio": {
      "forvo": {
        "type": "forvo",
        "pipelines": ["vocabulary"]
      },
      "elevenlabs": {
        "type": "elevenlabs",
        "pipelines": ["*"]
      }
    },
    "image": {
      "runware": {
        "type": "runware",
        "pipelines": ["vocabulary"]
      }
    },
    "sync": {
      "anki": {
        "type": "anki",
        "pipelines": ["*"]
      }
    }
  }
}
```

**Key Changes:**
- **BREAKING CHANGE**: Remove old configuration format completely
- All providers must be configured as named provider dictionaries
- **REQUIRED**: `pipelines` array must be specified for each provider
- Support "*" wildcard for all pipelines
- No backward compatibility - old configs will fail with clear error messages

### 2. Provider Registry Enhancements

**Storage Changes:**
- Add pipeline assignment storage: `_provider_pipeline_assignments: dict[str, list[str]]`
- Key format: `{provider_type}:{provider_name}` (e.g., "audio:forvo")
- Value: list of pipeline names or ["*"] for all pipelines

**New Methods:**
```python
def get_providers_for_pipeline(self, pipeline_name: str) -> dict[str, Any]:
    """Return filtered providers dict for specific pipeline"""
    return {
        "data": self._get_filtered_data_providers(pipeline_name),
        "audio": self._get_filtered_audio_providers(pipeline_name),
        "image": self._get_filtered_image_providers(pipeline_name),
        "sync": self._get_filtered_sync_providers(pipeline_name)
    }

def _get_filtered_data_providers(self, pipeline_name: str) -> dict[str, DataProvider]:
    """Filter data providers by pipeline assignment"""
    # Implementation details below

def set_pipeline_assignments(self, provider_type: str, provider_name: str, pipelines: list[str]) -> None:
    """Set pipeline assignments for a provider"""

def get_pipeline_assignments(self, provider_type: str, provider_name: str) -> list[str]:
    """Get pipeline assignments for a provider"""
```

**Updated `from_config()` Method:**
- Parse ONLY new configuration format with named providers
- Extract and store pipeline assignments from required `pipelines` field
- Fail with clear error message for old config format
- Create providers with proper pipeline assignments

### 3. RunCommand Context Injection Update

**Update `_create_context()` method (`src/cli/commands/run_command.py:125-134`):**
```python
def _create_context(self, args: Any) -> PipelineContext:
    context = PipelineContext(
        pipeline_name=args.pipeline,
        project_root=self.project_root,
        config=self.config.to_dict(),
        args=vars(args),
    )

    # Use filtered providers instead of all providers
    filtered_providers = self.provider_registry.get_providers_for_pipeline(args.pipeline)
    context.set("providers", filtered_providers)

    return context
```

### 4. Error Handling and Validation

**Configuration Validation:**
- Validate pipeline names exist in system
- Validate provider types are supported
- **REQUIRED**: Fail if `pipelines` field missing from provider config
- Validate `pipelines` array is not empty

**Runtime Error Handling:**
- Clear error messages when pipeline requests unavailable provider
- Log provider filtering decisions for debugging
- Clear error messages when old config format detected

## Implementation Approach

### Phase 1A: Core Infrastructure
1. **Provider Assignment Storage**: Add pipeline assignment tracking to ProviderRegistry
2. **Configuration Parsing**: Update `from_config()` to handle ONLY new config format
3. **Filtering Logic**: Implement `get_providers_for_pipeline()` with wildcard support

### Phase 1B: Integration Points
1. **RunCommand Integration**: Update context creation to use filtered providers
2. **Breaking Change Handling**: Clear error messages for old config format
3. **Error Handling**: Add proper validation and error messages for new format

### Phase 1C: Testing and Validation
1. **Unit Tests**: Test all new functionality in isolation
2. **Integration Tests**: Test full pipeline execution with filtered providers
3. **Error Handling Tests**: Ensure old configs fail with clear messages

## Test Plan

### New Unit Tests Required

**`tests/unit/providers/test_registry.py` Additions:**

1. **Pipeline Assignment Management:**
   ```python
   def test_set_pipeline_assignments(self):
       """Test setting pipeline assignments for providers"""
       # Test setting assignments for different provider types
       # Test overwriting existing assignments

   def test_get_pipeline_assignments(self):
       """Test retrieving pipeline assignments"""
       # Test getting assignments for assigned providers
       # Test getting assignments for unassigned providers (should return ["*"])
   ```

2. **Provider Filtering:**
   ```python
   def test_get_providers_for_pipeline_with_assignments(self):
       """Test filtering providers by pipeline assignments"""
       # Register providers with specific pipeline assignments
       # Verify only assigned providers are returned for pipeline

   def test_get_providers_for_pipeline_with_wildcard(self):
       """Test wildcard "*" assignments work for all pipelines"""
       # Register providers with "*" assignment
       # Verify they appear for any pipeline

   def test_get_providers_for_pipeline_no_assignments_defaults_universal(self):
       """Test providers without assignments default to universal access"""
       # Register providers without assignments
       # Verify they appear for all pipelines (backward compatibility)
   ```

3. **Configuration Loading:**
   ```python
   def test_from_config_with_pipeline_assignments(self):
       """Test loading config with new pipeline assignment format"""
       # Test config with named providers and pipeline assignments
       # Verify providers are created and assignments stored correctly

   def test_from_config_old_format_fails(self):
       """Test old config format fails with clear error message"""
       # Test config in old format
       # Verify clear error message is provided

   def test_from_config_missing_pipelines_field_fails(self):
       """Test config missing pipelines field fails"""
       # Test config with new structure but missing pipelines field
       # Verify clear error message is provided
   ```

**`tests/unit/cli/commands/test_run_command.py` Additions:**

1. **Context Creation:**
   ```python
   def test_create_context_with_filtered_providers(self):
       """Test context creation uses filtered providers"""
       # Set up providers with specific pipeline assignments
       # Verify context only contains providers assigned to pipeline

   def test_create_context_with_no_assigned_providers(self):
       """Test context creation when no providers assigned to pipeline"""
       # Set up providers not assigned to test pipeline
       # Verify context contains empty provider dictionaries
   ```

2. **Execution with Filtering:**
   ```python
   def test_execute_with_wildcard_providers(self):
       """Test execution with wildcard-assigned providers"""
       # Set up providers with "*" assignment
       # Verify pipeline execution works normally
   ```

**New Integration Test File: `tests/integration/test_pipeline_provider_filtering.py`:**

```python
class TestPipelineProviderFiltering:
    """Integration tests for pipeline-specific provider filtering"""

    def test_end_to_end_pipeline_execution_with_filtering(self):
        """Test complete pipeline execution respects provider filtering"""
        # Create config with pipeline-specific provider assignments
        # Execute pipeline and verify only assigned providers accessible

    def test_provider_access_validation(self):
        """Test that pipelines cannot access unauthorized providers"""
        # Set up providers restricted to different pipelines
        # Attempt cross-pipeline access and verify proper error handling

    def test_configuration_loading_new_format(self):
        """Test configuration loading handles new format correctly"""
        # Load config with new provider assignment format
        # Verify registry state matches expectations
```

### Existing Tests That Need Updates

**`tests/unit/providers/test_registry.py` Required Changes:**

1. **Line 378: `test_from_config_basic_functionality()`**
   - **Issue**: Currently expects old config format and provider lookup by "default"
   - **Fix**: Completely rewrite to use only new config format
   - **Change**: Remove old format tests, use new named provider structure

2. **Line 465: `test_from_config_missing_sections()`**
   - **Issue**: Tests behavior when provider sections missing
   - **Fix**: Update to test new format and expected failures for old format
   - **Change**: Test that old format configs fail with clear error messages

3. **Line 303-332: Unsupported provider type tests**
   - **Issue**: Tests need to use new config format
   - **Fix**: Update test configs to use new named provider structure
   - **Change**: Maintain same error testing logic but with new config format

**`tests/unit/cli/commands/test_run_command.py` Required Changes:**

1. **Line 298: `test_create_context()`**
   - **Issue**: Currently assumes all providers injected as "default"
   - **Fix**: Update to verify filtered provider injection
   - **Change**: Test that context receives appropriate providers for pipeline

2. **Line 68-84: `setup_method()`**
   - **Issue**: Sets up mock providers but may need pipeline assignments
   - **Fix**: Add pipeline assignments to mock providers for filtering tests
   - **Change**: Ensure mock setup supports new filtering functionality

3. **Provider-related assertions throughout file**
   - **Issue**: Tests assume providers always available in context
   - **Fix**: Update to handle cases where providers may be filtered out
   - **Change**: Make provider access tests more robust to filtering

### Test Coverage Strategy

**Minimal Testing Principle:**
- Focus on core functionality that could break: provider filtering logic
- Test edge cases: wildcard assignments, missing assignments, empty filters
- Test integration points: config loading, context creation, pipeline execution
- Test backward compatibility: ensure existing behavior unchanged

**High-Risk Areas Requiring Extra Coverage:**
1. **Configuration Parsing**: New format vs old format handling
2. **Provider Filtering**: Correct assignment evaluation and wildcard logic
3. **Context Injection**: Filtered providers reach pipeline stages correctly
4. **Error Handling**: Clear messages when unauthorized access attempted

**Test Execution Strategy:**
1. **Unit Tests First**: Validate individual component behavior
2. **Integration Tests**: Verify components work together correctly
3. **Regression Tests**: Ensure existing functionality unchanged
4. **Error Scenario Tests**: Validate proper error handling and messages

## Configuration Migration Strategy

### Breaking Change Approach
1. **No Backward Compatibility**: Old config format completely removed
2. **Required Migration**: All existing configs must be updated to new format
3. **Clear Error Messages**: Helpful error messages guide users to correct format

### Migration Requirements
1. **Update All Configs**: Convert existing configs to named provider format
2. **Add Pipelines Field**: All providers must specify `pipelines` array
3. **Documentation**: Clear migration guide and examples

## Risk Mitigation

### Potential Issues
1. **Breaking Change Impact**: All existing configs will break
2. **Migration Complexity**: Users must update all configuration files
3. **Runtime Errors**: Pipelines may unexpectedly lose access to providers

### Mitigation Strategies
1. **Extensive Testing**: Comprehensive test coverage for all scenarios
2. **Clear Error Messages**: Helpful messages that guide users to correct format
3. **Migration Documentation**: Clear examples showing old vs new format
4. **Logging**: Debug-level logging for provider filtering decisions

## Success Criteria

### Functional Requirements
- ✅ Providers can be restricted to specific pipelines via configuration
- ✅ Wildcard "*" assigns providers to all pipelines
- ✅ Clear error messages for old configuration format
- ✅ Clear error messages when unauthorized provider access attempted
- ✅ `get_providers_for_pipeline()` returns properly filtered provider dictionary

### Non-Functional Requirements
- ✅ No performance degradation in provider lookup
- ✅ Configuration loading remains fast
- ✅ Memory usage does not significantly increase
- ✅ All tests updated to use new format
- ✅ New functionality has comprehensive test coverage

## Implementation Timeline

1. **Core Registry Changes** (Day 1): Pipeline assignment storage and filtering
2. **Configuration Updates** (Day 1): New config format parsing ONLY, remove old format support
3. **RunCommand Integration** (Day 1): Context creation with filtered providers
4. **Error Handling** (Day 2): Validation and clear error messages for new format
5. **Testing** (Day 2): Update all tests to use new format, test error handling
6. **Documentation** (Day 2): Update documentation with migration guide

## File Changes Summary

### Modified Files
- `src/providers/registry.py`: Core pipeline assignment functionality
- `src/cli/commands/run_command.py`: Filtered provider injection
- `tests/unit/providers/test_registry.py`: Additional test coverage
- `tests/unit/cli/commands/test_run_command.py`: Updated context tests

### New Files
- `tests/integration/test_pipeline_provider_filtering.py`: Integration tests for provider filtering

This plan ensures a systematic approach to implementing pipeline-specific provider access control with a clean break from the old configuration format, enabling better pipeline isolation and security.
