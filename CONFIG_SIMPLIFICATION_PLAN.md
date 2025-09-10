# Config System Simplification Plan

## Current State Analysis

The existing configuration system suffers from significant over-engineering:

- **Dual Config Systems**: `ConfigManager` and `CLIConfig` with overlapping functionality
- **Complex Hierarchy**: 5-level priority system with deep merging (System→Pipeline→Provider→Environment→CLI)
- **Scattered Files**: 15+ JSON files across multiple directories (`config/`, `config/pipelines/`, `config/providers/`, `config/environments/`)
- **Tight Coupling**: Config classes directly handle provider initialization
- **Over-Engineering**: Caching, auto-discovery, complex validation for simple data

## Target Architecture

### Single Unified Configuration

Replace the entire config system with:
1. **One `config.json`** in project root
2. **Simple section-based structure** (no hierarchy merging)
3. **Environment variable substitution** using `${VAR}` syntax
4. **Decoupled initialization** - config only provides data

### New Config Class Structure

```python
class Config:
    def __init__(self, config_path: str = None)
    def get(self, key: str, default: Any = None) -> Any
    def get_provider(self, name: str) -> dict
    def get_system_settings() -> dict
```

## File Changes Required

### Files to Delete
- `src/core/config.py` (281 lines → 0)
- `src/core/config_validator.py` (107 lines → 0)
- `src/cli/config/cli_config.py` (207 lines → 0)
- Entire `config/` directory and all subdirectories

### Code to Remove from Existing Files
- **`src/providers/registry.py`**: Remove factory classes (`DataProviderFactory`, `MediaProviderFactory`, `SyncProviderFactory`) - Lines ~167-375
- **Provider `__init__.py` files**: Remove factory class imports and exports

### Files to Create
- `config.json` (root directory)
- `src/core/config.py` (new simplified version ~80 lines)

### Files to Modify

#### 1. `src/cli/pipeline_runner.py`
**Lines 98-106**: Replace complex config loading
```python
# OLD (complex)
config = CLIConfig.load(getattr(args, "config", None))
pipeline_registry = get_pipeline_registry()
provider_registry = get_provider_registry()
config.initialize_providers(provider_registry)

# NEW (simplified)
config = Config.load(getattr(args, "config", None))
provider_registry = ProviderRegistry.from_config(config)
```

#### 2. `src/providers/registry.py`
- Add class method to `ProviderRegistry` for config-based initialization
- Remove unused factory classes (`DataProviderFactory`, `MediaProviderFactory`, `SyncProviderFactory`)
- Update `__init__.py` files to remove factory exports

```python
class ProviderRegistry:
    # ... existing methods ...

    @classmethod
    def from_config(cls, config: Config) -> 'ProviderRegistry'
```

#### 3. Provider `__init__.py` files
Update to remove factory exports:
- `src/providers/data/__init__.py`: Remove `DataProviderFactory` from `__all__`
- `src/providers/media/__init__.py`: Remove `MediaProviderFactory` from `__all__`
- `src/providers/sync/__init__.py`: Remove `SyncProviderFactory` from `__all__`

#### 4. Any files importing from deleted config modules
- Update imports to use new `src.core.config.Config`
- Replace method calls with simplified API

## Provider Initialization Decoupling

### Current Problem
`CLIConfig.initialize_providers()` directly creates provider instances, violating separation of concerns.

### Solution
Add class method to `ProviderRegistry` for config-based initialization:

```python
class ProviderRegistry:
    # ... existing methods ...

    @classmethod
    def from_config(cls, config: Config) -> 'ProviderRegistry':
        """Create and populate registry from configuration"""
        registry = cls()

        # Initialize data providers
        data_config = config.get("providers.data", {})
        if data_config.get("type") == "json":
            from src.providers.data.json_provider import JSONDataProvider
            base_path = Path(data_config.get("base_path", "."))
            registry.register_data_provider("default", JSONDataProvider(base_path))

        # Initialize media providers with fallback handling
        media_config = config.get("providers.media", {})
        media_type = media_config.get("type", "openai")

        if media_type == "openai":
            from src.providers.media.openai_provider import OpenAIProvider
            try:
                registry.register_media_provider("default", OpenAIProvider())
            except Exception:
                # Fallback to mock provider
                from src.providers.media.mock_provider import MockMediaProvider
                registry.register_media_provider("default", MockMediaProvider())
        else:
            # Default to mock provider
            from src.providers.media.mock_provider import MockMediaProvider
            registry.register_media_provider("default", MockMediaProvider())

        # Initialize sync providers with fallback handling
        sync_config = config.get("providers.sync", {})
        if sync_config.get("type") == "anki":
            from src.providers.sync.anki_provider import AnkiProvider
            try:
                registry.register_sync_provider("default", AnkiProvider())
            except Exception:
                # Fallback to mock provider
                from src.providers.sync.mock_provider import MockSyncProvider
                registry.register_sync_provider("default", MockSyncProvider())
        else:
            from src.providers.sync.mock_provider import MockSyncProvider
            registry.register_sync_provider("default", MockSyncProvider())

        return registry
```

**Integration Point**: `pipeline_runner.py:106`
```python
provider_registry = ProviderRegistry.from_config(config)
```

## Testing Plan

### Unit Tests

#### Core Configuration Loading
```python
def test_config_loads_default_file():
    """Test config loads from default config.json location"""

def test_config_loads_custom_path():
    """Test config loads from specified file path"""

def test_config_handles_missing_file():
    """Test config gracefully handles missing file with defaults"""

def test_config_validates_json_syntax():
    """Test config raises appropriate error for malformed JSON"""
```

#### Environment Variable Substitution
```python
def test_env_var_substitution_basic():
    """Test ${VAR} gets replaced with environment variable value"""

def test_env_var_substitution_nested():
    """Test env vars work in nested config structures"""

def test_env_var_substitution_missing():
    """Test missing env vars remain as literal ${VAR} strings"""

def test_env_var_substitution_complex():
    """Test multiple env vars in single value: '${HOST}:${PORT}'"""
```

#### Configuration Access
```python
def test_get_method_dot_notation():
    """Test config.get('providers.media.type') returns correct nested value"""

def test_get_method_with_defaults():
    """Test config.get('missing.key', 'default') returns default value"""

def test_get_provider_returns_dict():
    """Test get_provider('openai') returns provider configuration dict"""

def test_get_system_settings():
    """Test get_system_settings() returns system section as dict"""
```

#### Edge Cases
```python
def test_config_with_empty_file():
    """Test behavior with completely empty JSON file"""

def test_config_with_null_values():
    """Test handling of null values in configuration"""

def test_config_with_circular_env_vars():
    """Test detection of circular environment variable references"""

def test_config_thread_safety():
    """Test config can be safely accessed from multiple threads"""
```

### Integration Tests

#### Provider Initialization
```python
def test_provider_registry_from_config_openai():
    """Test ProviderRegistry.from_config correctly creates OpenAI provider"""

def test_provider_registry_from_config_fallback():
    """Test provider initialization falls back to mock when real provider fails"""

def test_provider_registry_from_config_missing_config():
    """Test graceful handling of missing provider configuration sections"""

def test_provider_registry_from_config_direct_creation():
    """Test that from_config method directly creates providers without factories"""

def test_provider_registry_from_config_fallback():
    """Test provider initialization falls back to mock when real provider fails"""

def test_provider_registry_from_config_missing_sections():
    """Test graceful handling of missing provider configuration sections"""
```

#### Full Pipeline Integration
```python
def test_pipeline_runner_with_new_config():
    """Test pipeline_runner.py works end-to-end with simplified config"""

def test_config_changes_reflected_in_providers():
    """Test that config changes are properly reflected in initialized providers"""
```

### Test Implementation Strategy

- **Minimal but comprehensive**: Focus on critical paths and edge cases
- **Use pytest fixtures** for test config files
- **Mock external dependencies** (file system, environment variables)
- **Test both success and failure scenarios**
- **Use temporary directories** for integration tests

### Coverage Goals
- **Unit tests**: 95% coverage of new `Config` class
- **Integration tests**: Cover critical initialization paths
- **Edge case coverage**: Handle all identified failure modes

---

## Implementation Order

1. **Read and analyze** all existing config files
2. **Create new simplified config.json** with essential data only
3. **Implement new Config class** with tests
4. **Create ProviderInitializer** with tests
5. **Update pipeline_runner.py** integration point
6. **Run integration tests** to verify functionality
7. **Delete old config files** and classes
8. **Final integration test sweep**

This plan reduces config complexity by ~90% while maintaining all functionality and improving maintainability. Additionally, removing unused factory classes from `registry.py` eliminates ~200 lines of unnecessary code.
