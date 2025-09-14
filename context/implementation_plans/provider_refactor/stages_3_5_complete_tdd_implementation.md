# Stages 3-5: Complete Provider Refactor Implementation (TDD)

**CRITICAL**: This document implements a comprehensive Test-Driven Development approach to complete the provider refactor. All test modifications, legacy code removal, and implementations happen in strict TDD order.

## Overview

Complete the provider refactor using rigorous TDD methodology:
1. **TESTS FIRST**: Design and implement complete test architecture
2. **STRIP LEGACY**: Remove all legacy code patterns guided by new tests
3. **IMPLEMENT CLEAN**: Build clean implementations to satisfy final test suite
4. **BUG ASSUMPTION**: Any test failures = bugs in src/ code (tests define truth)

## TDD Implementation Rules

### Core Principles
- **Tests Define Truth**: Test suite represents desired system behavior
- **Red-Green-Refactor**: Strict adherence to TDD cycles
- **No Legacy Compatibility**: Clean slate implementation, remove all fallback logic
- **Fail-Fast**: Configuration errors caught at initialization
- **Single Responsibility**: Each method/class has one clear purpose

### Implementation Order
1. **Phase 1**: Complete test architecture (E2E → Integration → Unit)
2. **Phase 2**: Legacy code stripping guided by new test requirements
3. **Phase 3**: Clean implementation to pass all new tests
4. **Phase 4**: Bug fixing (assume bugs in src/, not tests)

## Phase 1: Complete Test Architecture

### 1.1 E2E Test Suite (`tests/integration/test_provider_workflows.py`)

Create comprehensive end-to-end tests covering complete pipeline workflows:

```python
class TestProviderWorkflows:
    """End-to-end provider workflow testing"""

    def test_complete_audio_workflow(self):
        """Test: data provider → forvo audio → anki sync"""
        # ARRANGE: Mock pipeline with real provider interactions
        # ACT: Execute complete audio generation workflow
        # ASSERT: Audio files created, metadata correct, sync successful

    def test_complete_image_workflow(self):
        """Test: data provider → openai image → file validation"""
        # ARRANGE: Mock pipeline with batch image generation
        # ACT: Execute complete image generation workflow
        # ASSERT: Images created, validated, proper metadata

    def test_batch_processing_performance(self):
        """Test: Batch processing faster than individual requests"""
        # ARRANGE: 10 requests for batch vs individual processing
        # ACT: Time both approaches
        # ASSERT: Batch processing <50% of individual request time

    def test_provider_failover_handling(self):
        """Test: System handles provider failures gracefully"""
        # ARRANGE: Mock provider failures mid-batch
        # ACT: Execute workflow with simulated failures
        # ASSERT: Partial success, error reporting, no data loss
```

### 1.2 Integration Test Suite (`tests/integration/test_providers_api.py`)

Integration tests with actual API calls (where possible):

```python
class TestProviderAPIIntegration:
    """Integration testing with real/mock APIs"""

    def test_openai_api_integration(self):
        """Test: OpenAI provider with real API calls"""
        # Uses test API key if available, mocks if not

    def test_forvo_api_integration(self):
        """Test: Forvo provider with real API calls"""
        # Tests actual pronunciation downloads

    def test_rate_limiting_compliance(self):
        """Test: Providers respect API rate limits"""
        # Tests sequential requests honor delays
```

### 1.3 Enhanced Unit Test Suite

**Replace ALL existing provider tests** with new architecture:

```python
# tests/unit/providers/base/test_media_provider_enhanced.py
class TestMediaProviderEnhanced:
    def test_batch_processing_abstract_method(self):
        """Test: generate_batch abstract method enforced"""

    def test_file_validation_framework(self):
        """Test: Universal file validation works"""

    def test_rate_limiting_framework(self):
        """Test: Rate limiting prevents API overuse"""

# tests/unit/providers/image/test_openai_provider_clean.py
class TestOpenAIProviderClean:
    def test_config_injection_validation(self):
        """Test: Config injection with fail-fast validation"""

    def test_batch_image_generation(self):
        """Test: Sequential batch processing with rate limits"""

    def test_dalle_api_integration(self):
        """Test: DALL-E API calls with proper error handling"""

# tests/unit/providers/audio/test_forvo_provider_clean.py
class TestForvoProviderClean:
    def test_simplified_config_validation(self):
        """Test: No fallback logic, clean config requirements"""

    def test_static_data_from_config(self):
        """Test: Country priorities from config, not hardcoded"""

    def test_batch_audio_processing(self):
        """Test: Multiple word requests efficiently processed"""
```

## Phase 2: Legacy Code Stripping Guide

### 2.1 Target Removal List

**File: `src/providers/audio/forvo_provider.py`**
```python
# REMOVE: Lines 27-82 - Complex config fallback logic
# REMOVE: Hardcoded country priorities and static data
# REMOVE: Multiple constructor paths and env var handling

# BEFORE (82 lines of complex logic):
def __init__(self) -> None:
    # Handle both old and new config structure
    if "apis" in self.config and "forvo" in self.config["apis"]:
        # 55+ lines of fallback logic

# AFTER (5 lines clean config injection):
def __init__(self, config: dict[str, Any] | None = None) -> None:
    super().__init__(config)
```

**File: `src/providers/image/openai_provider.py`**
```python
# REMOVE: Placeholder implementation patterns
# REMOVE: Empty validate_config() methods
# REMOVE: Legacy constructor without config injection

# BEFORE:
def __init__(self) -> None:  # No config injection
    super().__init__()

# AFTER:
def __init__(self, config: dict[str, Any] | None = None) -> None:
    super().__init__(config)
    # Real OpenAI client initialization
```

### 2.2 Test Stripping Strategy

**Remove ALL legacy tests before implementation:**
```bash
# Remove old test patterns that test implementation details
rm tests/unit/providers/audio/test_forvo_legacy.py
rm tests/unit/providers/image/test_openai_legacy.py

# Keep only tests that match new architecture
# Ensure new tests are comprehensive enough to guide implementation
```

## Phase 3: Clean Implementation Sequence

### 3.1 Stage 3: Enhanced Base Classes

**TDD Cycle: Write failing tests → Implement minimal code → Refactor**

**RED**: Write tests for enhanced MediaProvider
```python
def test_batch_processing_framework(self):
    """Test that batch processing framework exists and works"""
    # This test should fail initially
    provider = TestableMediaProvider(config)
    requests = [MediaRequest(...), MediaRequest(...)]
    results = provider.generate_batch(requests)  # Should fail - method doesn't exist
    assert len(results) == 2
```

**GREEN**: Implement minimal batch processing in MediaProvider
```python
@abstractmethod
def generate_batch(self, requests: list[MediaRequest]) -> list[MediaResult]:
    """Generate media for batch requests with rate limiting"""
    pass

def _default_batch_implementation(self, requests: list[MediaRequest]) -> list[MediaResult]:
    """Default sequential batch processing with rate limiting"""
    results = []
    for request in requests:
        if hasattr(self, '_rate_limit_delay'):
            time.sleep(self._rate_limit_delay)
        results.append(self.generate_media(request))
    return results
```

**REFACTOR**: Clean up implementation, add comprehensive error handling

### 3.2 Stage 4: Clean Provider Implementations

**OpenAI Provider Implementation:**
```python
class OpenAIProvider(ImageProvider):
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)

    def validate_config(self, config: dict[str, Any]) -> None:
        required = ["api_key", "model"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required OpenAI config key: {key}")

        valid_models = ["dall-e-2", "dall-e-3"]
        if config["model"] not in valid_models:
            raise ValueError(f"Invalid model: {config['model']}")

    def _setup_from_config(self) -> None:
        self.client = OpenAI(api_key=self.config["api_key"])
        self.model = self.config["model"]
        self._rate_limit_delay = self.config.get("rate_limit_delay", 4.0)  # 15 req/min

    def generate_batch(self, requests: list[MediaRequest]) -> list[MediaResult]:
        """Sequential batch processing with OpenAI rate limits"""
        return self._default_batch_implementation(requests)

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Generate single image using DALL-E API"""
        # Clean implementation without fallback logic
```

**Forvo Provider Implementation:**
```python
class ForvoProvider(MediaProvider):
    def validate_config(self, config: dict[str, Any]) -> None:
        required = ["api_key", "country_priorities"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required Forvo config key: {key}")

    def _setup_from_config(self) -> None:
        self.api_key = self.config["api_key"]
        self.country_priorities = self.config["country_priorities"]  # From config, not hardcoded
        self._rate_limit_delay = self.config.get("rate_limit_delay", 0.5)

    # Clean implementation - no fallback config logic, no static data
```

### 3.3 Stage 5: Production Readiness

**Error Handling and Resilience:**
- Comprehensive retry logic with exponential backoff
- Provider health monitoring
- Memory management and cleanup
- Performance monitoring

## Phase 4: Bug Resolution Protocol

### 4.1 Test Failure Investigation

When tests fail during implementation:

1. **Assumption**: Bug is in `src/` code, not tests
2. **Process**:
   - Analyze test expectation vs actual behavior
   - Fix implementation to match test specification
   - Only modify tests if specification was genuinely incorrect

### 4.2 Performance Validation

**Required Performance Improvements:**
- Batch processing: >50% faster than individual requests
- Registry initialization: <2 seconds
- Memory usage: Stable during large operations
- File operations: 100% success rate with validation

## Success Criteria

### Code Quality Metrics
- **File Size Reduction**:
  - `forvo_provider.py`: ~150 lines → ~80 lines (-45%)
  - `openai_provider.py`: ~200 lines → ~120 lines (-40%)
- **Duplicate Code**: Zero duplicate provider setup patterns
- **Configuration**: All providers use constructor injection
- **Test Coverage**: >95% for all new provider code

### Functionality Requirements
- All existing provider functionality preserved
- Batch processing operational for all provider types
- Configuration validation prevents runtime errors
- Error handling provides clear diagnostics
- Performance meets or exceeds baseline

## Implementation Commands

```bash
# Phase 1: Create test architecture
pytest tests/integration/test_provider_workflows.py -v  # Should fail initially

# Phase 2: Strip legacy tests
rm tests/unit/providers/audio/test_forvo_legacy.py
rm tests/unit/providers/image/test_openai_legacy.py

# Phase 3: Implement to pass tests
pytest tests/unit/providers/base/test_media_provider_enhanced.py -v  # RED
# Implement MediaProvider enhancements
pytest tests/unit/providers/base/test_media_provider_enhanced.py -v  # GREEN

# Phase 4: Final validation
pytest tests/unit/providers/ -v --cov=src/providers/ --cov-report=html
pytest tests/integration/ -v
```

## Final Deliverables

1. **Complete Test Architecture**: E2E, integration, and unit tests defining system behavior
2. **Clean Provider Implementations**: All providers using new architecture patterns
3. **Legacy Code Removal**: Zero fallback logic, static data, or duplicate patterns
4. **Performance Validation**: Benchmarks confirming improvements
5. **Production Readiness**: Error handling, monitoring, and resilience features

The implementation is complete when all new tests pass and performance metrics are met.
