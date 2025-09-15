# Stage 1: Configuration Architecture Foundation (TDD)

**REQUIRED READING**: First read `general_context.md` for architectural patterns and principles.

## Overview
Using Test-Driven Development, establish the core dependency injection pattern for MediaProvider configuration. This foundational stage follows RED → GREEN → REFACTOR cycles to build the architectural pattern that all subsequent stages depend upon.

## TDD Methodology
**Reference Implementation**: Use the detailed TDD prompts in `implementation_prompts.md` for this stage.

This stage follows strict TDD:
1. **RED**: Write failing tests for configuration injection pattern
2. **GREEN**: Implement minimal code to pass tests
3. **REFACTOR**: Clean up implementation while maintaining passing tests

## Objectives
- Implement constructor-based configuration injection using TDD approach
- Establish fail-fast configuration validation framework through test specifications
- Create clean foundation that removes need for runtime configuration loading
- Maintain backward compatibility through optional constructor parameters

## Scope Boundaries

### In Scope
- **MediaProvider Base Class** (`src/providers/base/media_provider.py`):
  - Add constructor configuration parameter
  - Add abstract `validate_config()` method
  - Add `_setup_from_config()` method
  - Remove runtime configuration methods if any exist

### Out of Scope
- Concrete provider implementations (OpenAI, Runware, Forvo)
- Provider registry changes
- Batch processing enhancements
- File validation improvements

## Detailed Implementation Plan

### 1.1 MediaProvider Base Class Constructor Enhancement

**File**: `src/providers/base/media_provider.py`

**Current Constructor Pattern**:
```python
def __init__(self):
    # Current initialization
    pass
```

**New Constructor Pattern**:
```python
def __init__(self, config: dict[str, Any] = None):
    """Initialize provider with configuration.

    Args:
        config: Provider-specific configuration dict. If None, defaults to empty dict.
    """
    self.config = config or {}
    self.validate_config(self.config)
    self._setup_from_config()
```

### 1.2 Configuration Validation Framework

**Add Abstract Method**:
```python
@abstractmethod
def validate_config(self, config: dict[str, Any]) -> None:
    """Validate provider-specific configuration.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid
        KeyError: If required configuration keys are missing
    """
    pass
```

**Default Implementation Pattern**:
```python
def _setup_from_config(self) -> None:
    """Setup provider from validated config. Override if needed."""
    pass
```

### 1.3 Backward Compatibility Strategy

**Approach**: Make config parameter optional with default empty dict
- Existing providers without config continue to work
- New providers can adopt config-based initialization
- No immediate breaking changes to existing code

**Migration Path**:
1. Add optional config parameter to base class
2. Existing providers continue working unchanged
3. Future stages will update concrete providers to use config

### 1.4 Configuration Structure Guidelines

**Provider Config Format**:
```python
{
    "api_key": "${OPENAI_API_KEY}",
    "model": "dall-e-3",
    "max_retries": 3,
    "rate_limit_delay": 1.0
}
```

**Validation Examples**:
```python
# OpenAI Provider validation example
def validate_config(self, config: dict[str, Any]) -> None:
    required_keys = ["api_key"]
    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"Missing required config key: {key}")

    if "model" in config and config["model"] not in ["dall-e-2", "dall-e-3"]:
        raise ValueError(f"Invalid model: {config['model']}")
```

## TDD Testing Strategy

### Test-First Development
Following the TDD approach, this stage is driven by the test specifications in `implementation_prompts.md`.

**Test Infrastructure**: Uses the foundation established in Stage 0, including:
- `ProviderTestBase` for common testing patterns
- Configuration fixtures for various scenarios
- Mock utilities for isolated testing

**TDD Cycle Implementation**:
1. **RED Phase**: Write comprehensive failing tests for configuration injection
2. **GREEN Phase**: Implement minimal MediaProvider changes to pass tests
3. **REFACTOR Phase**: Clean up implementation while maintaining test success

### Test Coverage Areas
- Constructor configuration injection with various config scenarios
- Abstract method enforcement for validate_config()
- Backward compatibility with existing provider instantiation
- Error handling for invalid configurations
- Configuration flow from constructor through validation

### Validation Approach
- All new tests must pass before proceeding to Stage 2
- Existing provider tests must continue passing (no regressions)
- Implementation must follow patterns specified in `general_context.md`

## Testing Gateway

### Success Criteria
1. **Base Class Enhancement**: MediaProvider base class supports constructor config injection
2. **Abstract Methods**: `validate_config()` abstract method enforced for subclasses
3. **Backward Compatibility**: All existing providers continue to work unchanged
4. **Test Coverage**: New configuration framework has comprehensive unit tests
5. **No Regressions**: All existing provider tests continue to pass

### Validation Checklist
- [ ] MediaProvider constructor accepts optional config parameter
- [ ] Abstract validate_config method defined and documented
- [ ] _setup_from_config method available for subclass use
- [ ] All existing provider tests pass without modification
- [ ] New unit tests for configuration framework pass
- [ ] Documentation updated for new constructor pattern

### Testing Commands
```bash
# Run existing provider tests to ensure no regressions
python -m pytest tests/unit/providers/ -v

# Run new configuration framework tests
python -m pytest tests/unit/providers/base/test_media_provider_config.py -v

# Run full provider test suite
python -m pytest tests/unit/providers/ -v --cov=src/providers/base/
```

### Rollback Strategy
If testing gateway fails:
1. **Revert Base Class Changes**: Remove config parameter and abstract methods
2. **Remove New Tests**: Clean up test files added in this stage
3. **Verify Rollback**: Ensure all original tests pass after revert

## Deliverables
1. **Enhanced MediaProvider Base Class**: Constructor-based config injection
2. **Configuration Validation Framework**: Abstract methods and patterns
3. **Unit Tests**: Comprehensive test coverage for new functionality
4. **Documentation**: Updated base class documentation
5. **Backward Compatibility**: All existing providers work unchanged

## Dependencies
- No external dependencies
- Builds on existing MediaProvider base class
- Required by all subsequent stages

## Estimated Effort
- Implementation: 2-3 hours
- Testing: 2-3 hours
- Documentation: 1 hour
- **Total**: 5-7 hours

## Notes
- This stage establishes the foundation pattern for all provider configuration
- Changes are minimal and focused on architecture, not functionality
- Success here enables more complex changes in later stages
- Maintains system stability while introducing new patterns
