# Phase 2: Enhanced Data Provider System - Detailed Implementation Plan

## Overview
This document provides a detailed implementation plan for Phase 2: Enhanced Data Provider System, including specific code changes, test requirements, and migration strategies.

## Current State Analysis

### Current Data Provider Architecture
- **Base Class**: `DataProvider` (abstract base class) with methods: `load_data`, `save_data`, `exists`, `list_identifiers`, `backup_data`
- **JSON Implementation**: `JSONDataProvider` extends `DataProvider` with file-based JSON storage
- **Registry**: `ProviderRegistry` manages provider instances with pipeline-based filtering (Phase 1)
- **Configuration**: Named provider format with `pipelines` field for access control

### Key Phase 1 Features (Already Implemented)
- ✅ Pipeline assignment system (`pipelines` field in config)
- ✅ Multiple named providers per type
- ✅ Provider filtering by pipeline via `get_providers_for_pipeline()`
- ✅ Pipeline assignments stored in registry (`_provider_pipeline_assignments`)

## Implementation Areas

### 1. Data Provider Base Class Enhancement

**File**: `src/providers/base/data_provider.py`

**Changes Required**:
```python
# Add to __init__ method:
self.read_only = False
self.managed_files = []

# Add new properties and methods:
@property
def is_read_only(self) -> bool:
    """Check if provider is read-only"""
    return self.read_only

@property
def managed_files(self) -> list[str]:
    """Get list of files managed by this provider"""
    return self._managed_files

def set_read_only(self, read_only: bool) -> None:
    """Set read-only status"""
    self.read_only = read_only

def set_managed_files(self, files: list[str]) -> None:
    """Set list of files managed by this provider"""
    self._managed_files = files

def validate_file_access(self, identifier: str) -> None:
    """Validate file access permissions"""
    if self._managed_files and identifier not in self._managed_files:
        raise ValueError(f"File '{identifier}' not managed by this provider. Managed files: {self._managed_files}")

def _check_write_permission(self, identifier: str) -> None:
    """Check if write operations are allowed"""
    if self.read_only:
        raise PermissionError(f"Cannot write to '{identifier}': provider is read-only")
```

**Modified save_data method**:
```python
def save_data(self, identifier: str, data: dict[str, Any]) -> bool:
    """Save data to identifier. Return True if successful."""
    self.logger.info(f"{ICONS['file']} Saving data to {identifier}")

    # Check permissions first
    self._check_write_permission(identifier)
    self.validate_file_access(identifier)

    # Existing implementation continues...
```

### 2. JSON Provider Enhancement

**File**: `src/providers/data/json_provider.py`

**Changes Required**:
```python
def __init__(self, base_path: Path, read_only: bool = False, managed_files: list[str] = None):
    """Initialize JSON data provider

    Args:
        base_path: Directory containing JSON files
        read_only: Whether provider is read-only
        managed_files: List of file identifiers this provider manages (None = all files)
    """
    super().__init__()
    self.base_path = Path(base_path)
    self.base_path.mkdir(parents=True, exist_ok=True)

    # Set permissions and file management
    self.set_read_only(read_only)
    if managed_files is not None:
        self.set_managed_files(managed_files)
```

**Override methods for file validation**:
```python
def _load_data_impl(self, identifier: str) -> dict[str, Any]:
    """Load data from JSON file with file access validation"""
    self.validate_file_access(identifier)
    # Existing implementation continues...

def _save_data_impl(self, identifier: str, data: dict[str, Any]) -> bool:
    """Save data to JSON file with permission checking"""
    # Permission and file access checks are handled by base class save_data()
    # Existing implementation continues...
```

### 3. Registry Data Provider Management Enhancement

**File**: `src/providers/registry.py`

**Changes Required**:
```python
# Add to __init__:
self._data_provider_configs: dict[str, dict[str, Any]] = {}

# Add conflict validation:
def _validate_file_conflicts(self) -> None:
    """Validate that no files are managed by multiple data providers"""
    file_assignments = {}
    conflicts = []

    for provider_name, config in self._data_provider_configs.items():
        managed_files = config.get('files', [])
        if not managed_files:  # Skip providers that manage all files
            continue

        for file_id in managed_files:
            if file_id in file_assignments:
                conflicts.append(f"File '{file_id}' managed by both '{file_assignments[file_id]}' and '{provider_name}'")
            else:
                file_assignments[file_id] = provider_name

    if conflicts:
        raise ValueError(f"File conflicts detected: {'; '.join(conflicts)}")

# Modified register_data_provider:
def register_data_provider(self, name: str, provider: DataProvider, config: dict[str, Any] = None) -> None:
    """Register a data provider with optional configuration"""
    self._data_providers[name] = provider
    if config:
        self._data_provider_configs[name] = config
        self._validate_file_conflicts()
```

**Enhanced from_config method** to support new configuration fields:
```python
# In data provider creation loop:
files = data_config.get("files", [])
read_only = data_config.get("read_only", False)

if provider_type == "json":
    from .data.json_provider import JSONDataProvider

    base_path = Path(data_config.get("base_path", "."))
    provider = JSONDataProvider(base_path, read_only=read_only, managed_files=files)

    registry.register_data_provider(
        provider_name,
        provider,
        config={'files': files, 'read_only': read_only}
    )
```

### 4. Configuration Schema Extension

**Example Enhanced Configuration**:
```json
{
  "providers": {
    "data": {
      "source_data": {
        "type": "json",
        "base_path": "./data/sources",
        "files": ["spanish_dictionary", "conjugation_patterns"],
        "read_only": true,
        "pipelines": ["vocabulary"]
      },
      "working_data": {
        "type": "json",
        "base_path": "./data/working",
        "files": ["word_queue", "progress_tracking", "debug_output"],
        "read_only": false,
        "pipelines": ["vocabulary"]
      },
      "output_data": {
        "type": "json",
        "base_path": "./data/output",
        "files": ["vocabulary", "anki_cards"],
        "read_only": false,
        "pipelines": ["vocabulary"]
      }
    }
  }
}
```

## Test Requirements (Minimal but Comprehensive)

### 1. New Unit Tests

**File**: `tests/unit/providers/base/test_data_provider_permissions.py`
```python
class TestDataProviderPermissions:
    def test_read_only_property()
    def test_set_read_only()
    def test_managed_files_property()
    def test_set_managed_files()
    def test_validate_file_access_allowed()
    def test_validate_file_access_denied()
    def test_check_write_permission_allowed()
    def test_check_write_permission_denied()
    def test_save_data_read_only_raises_permission_error()
    def test_save_data_file_access_validation()
```

**File**: `tests/unit/providers/data/test_json_provider_enhanced.py`
```python
class TestJSONProviderEnhanced:
    def test_init_with_read_only_true()
    def test_init_with_read_only_false()
    def test_init_with_managed_files()
    def test_init_with_no_managed_files()
    def test_load_data_file_access_validation()
    def test_load_data_managed_file_allowed()
    def test_load_data_unmanaged_file_denied()
    def test_save_data_read_only_provider_raises_error()
    def test_save_data_write_allowed_succeeds()
    def test_save_data_unmanaged_file_denied()
```

**File**: `tests/unit/providers/test_registry_file_conflicts.py`
```python
class TestRegistryFileConflicts:
    def test_validate_file_conflicts_no_conflicts()
    def test_validate_file_conflicts_with_conflicts()
    def test_register_data_provider_with_config()
    def test_multiple_providers_same_files_raises_error()
    def test_providers_different_files_allowed()
    def test_unmanaged_providers_no_conflicts()
```

### 2. Enhanced Integration Tests

**File**: `tests/integration/test_enhanced_data_providers.py`
```python
class TestEnhancedDataProviderIntegration:
    def test_from_config_read_only_providers()
    def test_from_config_multiple_named_providers_with_files()
    def test_from_config_file_conflict_validation()
    def test_pipeline_filtering_with_multiple_named_providers()
    def test_read_only_provider_write_operations()
    def test_file_specific_access_control()
```

### 3. E2E Workflow Tests

**File**: `tests/e2e/test_phase2_workflows.py`
```python
class TestPhase2Workflows:
    def test_vocabulary_pipeline_with_multiple_data_providers()
    def test_read_only_source_data_protection()
    def test_file_segregation_workflow()
    def test_config_migration_from_phase1()
```

### 4. Current Tests Requiring Updates

**Files needing updates**:
- `tests/unit/providers/test_registry.py` - Add tests for enhanced configuration loading
- `tests/unit/providers/data/test_json_provider.py` - Add tests for new constructor parameters
- `tests/integration/test_provider_registry_integration.py` - Update config examples

**Changes needed**:
1. Add test cases for new constructor parameters in JSON provider tests
2. Update registry tests to include file conflict validation scenarios
3. Add configuration test cases for new provider format with files/read_only fields
4. Update mock providers to support new permission system

## Migration Strategy

### 1. Backward Compatibility
- All existing configurations continue to work unchanged
- Default values: `read_only=False`, `managed_files=[]` (empty = manage all files)
- No breaking changes to public APIs

### 2. Configuration Migration
```python
# Old format (still supported):
"data": {
  "default": {
    "type": "json",
    "base_path": ".",
    "pipelines": ["*"]
  }
}

# New format (enhanced):
"data": {
  "sources": {
    "type": "json",
    "base_path": "./sources",
    "files": ["dictionary"],
    "read_only": true,
    "pipelines": ["vocabulary"]
  },
  "working": {
    "type": "json",
    "base_path": "./working",
    "files": ["queue", "progress"],
    "read_only": false,
    "pipelines": ["vocabulary"]
  }
}
```

### 3. Error Handling & Validation
- Clear error messages for permission violations
- File conflict detection during provider registration
- Validation errors include specific file names and provider names

## Implementation Order

1. **Phase 2A**: Base class enhancements (permissions, file management)
2. **Phase 2B**: JSON provider constructor updates and file validation
3. **Phase 2C**: Registry file conflict validation
4. **Phase 2D**: Enhanced configuration loading
5. **Phase 2E**: Comprehensive test suite
6. **Phase 2F**: Integration testing and bug fixes

## Success Criteria

- ✅ Multiple named data providers with file-specific assignments
- ✅ Read-only data providers prevent write operations with clear errors
- ✅ File conflict validation prevents overlapping provider assignments
- ✅ All existing configurations work without changes
- ✅ Phase 1 pipeline filtering works with Phase 2 enhancements
- ✅ Comprehensive test coverage for new functionality
- ✅ All tests pass including pre-commit hooks

## Potential Issues & Mitigations

1. **File Path Conflicts**: Mitigate with thorough validation in registry
2. **Performance Impact**: File validation is O(1) lookup, minimal overhead
3. **Configuration Complexity**: Provide clear examples and validation errors
4. **Test Complexity**: Focus on minimal essential test cases, avoid over-testing edge cases

This plan ensures complete backward compatibility while adding the enhanced data provider features specified in Phase 2 requirements.
