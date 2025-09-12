# Stage 2: Registry Infrastructure

## Overview
Transform the provider registry from hardcoded initialization to dynamic loading with configuration injection. This stage eliminates ~80 lines of duplicate code and establishes the foundation for flexible provider management.

## Objectives
- Implement dynamic provider loading with import mapping
- Remove duplicate provider setup code across audio/image/sync types
- Establish configuration extraction and injection at registry level
- Maintain full backward compatibility with existing provider instances

## Scope Boundaries

### In Scope
- **ProviderRegistry** (`src/providers/registry.py`):
  - Add dynamic provider import mapping
  - Replace hardcoded provider setup with unified method
  - Add configuration injection at provider creation time
  - Remove duplicate initialization code

### Out of Scope
- MediaProvider base class enhancements (Stage 1 handles this)
- Concrete provider implementations (Stage 4 handles these)
- Batch processing or file validation (Stage 3 handles these)
- Error handling improvements (Stage 5 handles these)

## Current State Analysis

### Existing Registry Structure
**File**: `src/providers/registry.py`

**Current Problems**:
- ~80 lines of duplicate code for audio/image/sync provider setup
- Hardcoded if/elif chains for provider type matching
- Manual provider instantiation without configuration injection
- Repetitive error handling across provider types

### Dependency Analysis
**Requires**: Stage 1 completion (MediaProvider supports constructor config)
**Enables**: All subsequent stages by providing config-injected providers

## Detailed Implementation Plan

### 2.1 Provider Import Mapping Registry

**Add Provider Registry Mapping**:
```python
MEDIA_PROVIDER_REGISTRY = {
    "audio": {
        "forvo": ("providers.audio.forvo_provider", "ForvoProvider"),
    },
    "image": {
        "openai": ("providers.image.openai_provider", "OpenAIProvider"),
        "runware": ("providers.image.runware_provider", "RunwareProvider"),
    },
    "sync": {
        "anki": ("providers.sync.anki_provider", "AnkiProvider"),
    }
}
```

**Import Mapping Structure**:
- **Key**: Provider subtype name (matches config)
- **Value**: Tuple of (module_path, class_name)
- **Dynamic Loading**: Use importlib to load providers on demand

### 2.2 Dynamic Provider Creation Method

**New Method**: `_create_media_provider()`
```python
def _create_media_provider(self, provider_type: str, provider_name: str, config: dict[str, Any]) -> Any:
    """Dynamically create media provider instance with configuration injection.

    Args:
        provider_type: Type of provider (audio, image, sync)
        provider_name: Name of provider (openai, forvo, etc.)
        config: Full provider configuration dict

    Returns:
        Provider instance with injected configuration

    Raises:
        ValueError: If provider type/name not found in registry
        ImportError: If provider module cannot be imported
    """
    if provider_type not in MEDIA_PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider type: {provider_type}")

    if provider_name not in MEDIA_PROVIDER_REGISTRY[provider_type]:
        raise ValueError(f"Unknown {provider_type} provider: {provider_name}")

    module_path, class_name = MEDIA_PROVIDER_REGISTRY[provider_type][provider_name]

    # Dynamic import
    module = importlib.import_module(f"src.{module_path}")
    provider_class = getattr(module, class_name)

    # Extract provider-specific config (exclude registry metadata)
    provider_config = {k: v for k, v in config.items() if k not in ['type', 'pipelines']}

    # Create with configuration injection
    return provider_class(provider_config)
```

### 2.3 Unified Provider Setup Method

**Replace Duplicate Code**: `_setup_media_providers()`
```python
def _setup_media_providers(self) -> None:
    """Setup all media providers using dynamic loading and config injection."""
    provider_configs = self._extract_provider_configs()

    for provider_type in ["audio", "image", "sync"]:
        type_configs = provider_configs.get(provider_type, {})

        for provider_name, config in type_configs.items():
            try:
                provider = self._create_media_provider(provider_type, provider_name, config)
                self._register_provider_by_type(provider_type, provider_name, provider)
                logger.info(f"Registered {provider_type} provider: {provider_name}")
            except Exception as e:
                logger.error(f"Failed to create {provider_type} provider {provider_name}: {e}")
                # Continue with other providers rather than failing completely
```

### 2.4 Configuration Extraction Method

**New Method**: `_extract_provider_configs()`
```python
def _extract_provider_configs(self) -> dict[str, dict[str, dict]]:
    """Extract provider configurations organized by type.

    Returns:
        Dict structure: {provider_type: {provider_name: config}}
    """
    providers_config = {}

    for provider_type in ["audio", "image", "sync"]:
        providers_config[provider_type] = {}
        type_config = self.config.get("providers", {}).get(provider_type, {})

        for provider_name, config in type_config.items():
            if isinstance(config, dict) and config.get("type") == provider_type:
                providers_config[provider_type][provider_name] = config

    return providers_config
```

### 2.5 Registration Helper Method

**New Method**: `_register_provider_by_type()`
```python
def _register_provider_by_type(self, provider_type: str, provider_name: str, provider: Any) -> None:
    """Register provider instance in appropriate registry.

    Args:
        provider_type: Type of provider (audio, image, sync)
        provider_name: Name of provider instance
        provider: Provider instance to register
    """
    if provider_type == "audio":
        self.register_audio_provider(provider_name, provider)
    elif provider_type == "image":
        self.register_image_provider(provider_name, provider)
    elif provider_type == "sync":
        self.register_sync_provider(provider_name, provider)
    else:
        raise ValueError(f"Unknown provider type for registration: {provider_type}")
```

### 2.6 Registry Integration Points

**Update `from_config()` Method**:
- Remove existing hardcoded provider setup calls
- Replace with single call to `_setup_media_providers()`
- Maintain existing data provider setup (unchanged)

**Before** (to be removed):
```python
# ~80 lines of duplicate code for each provider type
if audio_provider_type == "forvo":
    # Forvo-specific setup
elif audio_provider_type == "elevenlabs":
    # ElevenLabs-specific setup
# ... repeated for image and sync providers
```

**After**:
```python
# Single unified call
self._setup_media_providers()
```

## Testing Strategy

### 2.7 Unit Test Plan

**Test File**: `tests/unit/providers/test_registry_dynamic.py`

**Test Categories**:

1. **Import Mapping Tests**:
   - Test MEDIA_PROVIDER_REGISTRY structure
   - Test all registered providers can be imported
   - Test unknown provider types/names raise appropriate errors

2. **Dynamic Provider Creation Tests**:
   - Test `_create_media_provider()` with valid configurations
   - Test configuration injection (provider receives correct config)
   - Test error handling for invalid provider types/names
   - Test import errors are properly handled

3. **Configuration Extraction Tests**:
   - Test `_extract_provider_configs()` with various config structures
   - Test filtering of registry metadata (type, pipelines)
   - Test handling of missing or malformed configurations

4. **Unified Setup Tests**:
   - Test `_setup_media_providers()` creates all configured providers
   - Test error handling continues setup despite individual failures
   - Test logging output for successful/failed provider creation

5. **Integration Tests**:
   - Test full registry initialization with dynamic loading
   - Test backward compatibility with existing configurations
   - Test provider instances are properly registered and accessible

### 2.8 Backward Compatibility Tests

**Test Approach**:
- Use existing configuration files without modification
- Verify all previously working providers still initialize
- Confirm provider instances have same public interface
- Check that registry methods return same provider instances

**Configuration Compatibility**:
- Test with current provider configurations
- Verify configuration structure requirements
- Check pipeline assignment still works correctly

## Testing Gateway

### Success Criteria
1. **Dynamic Loading**: All provider types load via import mapping
2. **Configuration Injection**: Providers receive config from registry
3. **Code Reduction**: ~80 lines of duplicate code eliminated
4. **Backward Compatibility**: All existing configurations work unchanged
5. **Error Handling**: Individual provider failures don't break registry initialization
6. **Performance**: No significant overhead from dynamic loading

### Validation Checklist
- [ ] MEDIA_PROVIDER_REGISTRY mapping covers all current providers
- [ ] `_create_media_provider()` successfully creates all provider types
- [ ] Configuration extraction filters registry metadata correctly
- [ ] Unified setup method replaces all duplicate initialization code
- [ ] All existing provider tests pass without modification
- [ ] New dynamic loading tests pass
- [ ] Registry initialization completes successfully with existing configs
- [ ] Provider instances have correct configuration injected

### Testing Commands
```bash
# Test provider registry functionality
python -m pytest tests/unit/providers/test_registry_dynamic.py -v

# Test backward compatibility with existing providers
python -m pytest tests/unit/providers/ -v

# Test full system with dynamic registry
python -m pytest tests/integration/test_provider_registry.py -v

# Verify no regressions in provider functionality
python -m pytest tests/unit/providers/audio/ tests/unit/providers/image/ -v
```

### Performance Validation
```bash
# Benchmark registry initialization time
python -c "
import time
from src.providers.registry import ProviderRegistry
start = time.time()
registry = ProviderRegistry.from_config()
end = time.time()
print(f'Registry initialization: {end-start:.3f}s')
"
```

### Rollback Strategy
If testing gateway fails:
1. **Revert Registry Changes**: Restore original hardcoded provider setup
2. **Remove Dynamic Loading**: Remove import mapping and creation methods
3. **Clean Up Tests**: Remove new test files
4. **Verify Original State**: Ensure all original functionality restored

## Deliverables
1. **Dynamic Provider Registry**: Import mapping for all provider types
2. **Unified Setup Method**: Single method replacing ~80 lines of duplicate code
3. **Configuration Injection**: Providers receive config at construction time
4. **Comprehensive Tests**: Full test coverage for dynamic loading functionality
5. **Backward Compatibility**: All existing configurations continue to work

## Dependencies
- **Requires**: Stage 1 completion (MediaProvider constructor config support)
- **Enables**: Stage 3 (base class enhancements), Stage 4 (provider implementations)

## Estimated Effort
- Analysis and Design: 2 hours
- Implementation: 4-5 hours
- Testing: 3-4 hours
- Documentation: 1 hour
- **Total**: 10-12 hours

## Risk Mitigation
- **Import Errors**: Comprehensive error handling for missing modules
- **Configuration Issues**: Graceful degradation for malformed configs
- **Backward Compatibility**: Extensive testing with existing configurations
- **Performance**: Benchmark dynamic loading vs. static initialization

## Notes
- This stage eliminates significant code duplication while maintaining functionality
- Dynamic loading enables easier addition of new providers in the future
- Configuration injection at registry level provides clean separation of concerns
- Success here enables more complex provider enhancements in later stages
