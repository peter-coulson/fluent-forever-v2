# Provider Refactor - General Context

**REQUIRED READING**: All implementation stages must reference and adhere to the principles in this document.

## Refactor Philosophy

### Clean Slate Approach
- **No Legacy Maintenance**: Once new patterns are implemented, completely remove old approaches
- **Single Source of Truth**: One way to do each operation, not multiple compatible approaches
- **Clean Final State**: No backward compatibility code, deprecated methods, or transitional patterns

### Test-Driven Development
- **Tests Define Behavior**: Write tests first to specify desired functionality
- **Red/Green/Refactor**: Follow TDD cycle religiously
- **Final Tests Only**: Don't maintain dual test suites - replace old tests completely

## Architectural Patterns

### Configuration Injection Pattern
```python
# CORRECT: Constructor injection with validation
def __init__(self, config: dict[str, Any]):
    self.config = config
    self.validate_config(config)  # Fail-fast
    self._setup_from_config()

# INCORRECT: Runtime config loading with fallbacks
def _load_config(self):
    config = load_from_file() or get_defaults() or {}
```

### Dynamic Provider Loading
```python
# CORRECT: Registry-based dynamic import
provider = self._create_media_provider(provider_type, provider_name, config)

# INCORRECT: Hardcoded if/elif chains
if provider_type == "openai":
    provider = OpenAIProvider()
elif provider_type == "runware":
    provider = RunwareProvider()
```

### Fail-Fast Validation
```python
# CORRECT: Immediate validation with clear errors
def validate_config(self, config: dict[str, Any]) -> None:
    if "api_key" not in config:
        raise ValueError("Missing required config key: api_key")

# INCORRECT: Graceful degradation with warnings
def validate_config(self, config: dict[str, Any]) -> None:
    if "api_key" not in config:
        logger.warning("No API key found, using fallback")
```

## Implementation Standards

### Error Handling
- **Explicit over Implicit**: Clear error messages over silent failures
- **Fail-Fast**: Catch configuration and setup errors at initialization
- **No Silent Fallbacks**: Don't hide errors with default behavior

### File Management
- **Path Validation**: Validate all file paths before processing
- **Directory Creation**: Ensure output directories exist before writing
- **Post-Processing Validation**: Verify files were created successfully

### API Integration
- **Rate Limiting**: Respect API limits with configurable delays
- **Connection Testing**: Provide health check capabilities
- **Retry Logic**: Implement exponential backoff for transient failures

### Code Organization
- **Single Responsibility**: Each method has one clear purpose
- **Abstract Base Classes**: Define contracts through abstract methods
- **Dependency Injection**: Pass dependencies through constructors

## Testing Principles

### Test Structure
- **Arrange/Act/Assert**: Clear test organization
- **One Assertion**: Each test verifies one behavior
- **Descriptive Names**: Test names describe the scenario being tested

### Test Coverage
- **Unit Tests**: Mock external dependencies, test logic in isolation
- **Integration Tests**: Test provider interactions with real/mock APIs
- **End-to-End Tests**: Test complete workflows through pipeline system

### Test Data
- **Deterministic**: Tests produce consistent results
- **Isolated**: Tests don't depend on external state
- **Realistic**: Test data represents actual usage patterns

## Anti-Patterns to Avoid

### Configuration Anti-Patterns
- ❌ Runtime configuration loading
- ❌ Silent fallback to defaults
- ❌ Static data embedded in code
- ❌ Environment variable checks in business logic

### Code Anti-Patterns
- ❌ Hardcoded provider type switches
- ❌ Duplicate initialization logic
- ❌ Methods with multiple responsibilities
- ❌ Exception swallowing without logging

### Testing Anti-Patterns
- ❌ Tests that depend on external services
- ❌ Tests with non-deterministic behavior
- ❌ Integration tests that test implementation details
- ❌ Tests that require manual setup or cleanup

## File Organization Standards

### Module Structure
```
src/providers/
├── base/
│   ├── media_provider.py     # Enhanced base class
│   └── image_provider.py     # Image specialization
├── audio/
│   └── forvo_provider.py     # Clean implementation
├── image/
│   ├── openai_provider.py    # Clean implementation
│   └── runware_provider.py   # Clean implementation
└── registry.py               # Dynamic loading system
```

### Test Structure
```
tests/
├── unit/providers/
│   ├── base/
│   ├── audio/
│   └── image/
└── integration/
    └── providers/
```

## Success Metrics

### Code Quality
- Zero deprecated methods or compatibility code
- Single implementation pattern for each operation
- Clear separation of concerns
- Comprehensive error handling

### Test Quality
- >95% code coverage
- All tests pass consistently
- Tests run in <30 seconds
- No external service dependencies in unit tests

### Performance
- Batch processing faster than individual requests
- Memory usage stable during large operations
- Rate limiting prevents API quota issues
- Startup time <2 seconds

## Stage-Specific Guidelines

### Stage 0-2: Foundation Building
- **Focus**: Establish core patterns with tests
- **Approach**: TDD with minimal implementation
- **Goal**: Working foundation, not complete features

### Stage 3+: Implementation to Tests
- **Focus**: Implement to satisfy final test suite
- **Approach**: Remove legacy code while implementing new patterns
- **Goal**: Clean, complete implementation matching test specifications

## Migration Strategy

### During Implementation
1. **Write tests first** for desired behavior
2. **Implement minimal code** to pass tests
3. **Remove legacy code** completely when new code is working
4. **Update documentation** to reflect new patterns only

### Validation Approach
1. **All new tests pass** with new implementation
2. **No legacy code remains** in final implementation
3. **Performance meets or exceeds** original system
4. **Documentation reflects** actual implementation only
