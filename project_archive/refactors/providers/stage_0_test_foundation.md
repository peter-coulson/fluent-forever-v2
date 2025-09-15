# Stage 0: Test Foundation Setup

## Overview
Prepare the testing infrastructure for TDD-driven provider refactor. This stage establishes the test structure that will guide implementation in stages 1-2 without breaking existing functionality.

## Objectives
- Set up test infrastructure for new provider patterns
- Create test utilities for mocking and validation
- Establish testing conventions for TDD approach
- Prepare test structure without modifying existing tests

## Scope Boundaries

### In Scope
- **New Test Infrastructure**:
  - Test utilities for provider configuration validation
  - Mock factories for API responses
  - Test fixtures for common provider scenarios
  - Base test classes for provider testing patterns

- **Test Organization**:
  - Create test structure for new provider patterns
  - Set up test configuration management
  - Establish mocking patterns for external APIs

### Out of Scope
- Modifications to existing provider tests (preserve for now)
- Implementation of actual provider code
- Changes to existing provider functionality

## Detailed Implementation Plan

### 0.1 Test Structure Creation

**New Test Directories**:
```
tests/unit/providers/refactor/
├── base/
│   ├── test_media_provider_config.py    # Config injection tests
│   └── test_image_provider.py           # Image provider tests
├── registry/
│   └── test_dynamic_loading.py          # Dynamic registry tests
├── fixtures/
│   ├── provider_configs.py              # Test configurations
│   └── mock_responses.py                # API response mocks
└── utils/
    ├── provider_test_base.py             # Base test classes
    └── mock_factories.py                 # Mock creation utilities
```

### 0.2 Test Utilities Development

**Provider Test Base Class** (`tests/unit/providers/refactor/utils/provider_test_base.py`):
```python
import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any

class ProviderTestBase(unittest.TestCase):
    """Base class for provider testing with common utilities."""

    def setUp(self):
        """Common setup for provider tests."""
        self.mock_config = self.get_test_config()
        self.temp_dir = self.create_temp_directory()

    def get_test_config(self) -> Dict[str, Any]:
        """Get standard test configuration."""
        return {
            "api_key": "test_api_key",
            "rate_limit_delay": 0.1,
            "max_retries": 2
        }

    def create_temp_directory(self) -> str:
        """Create temporary directory for test files."""
        # Implementation for temp directory creation
        pass

    def assert_config_validation_error(self, config: Dict[str, Any], expected_error: str):
        """Assert that config validation raises expected error."""
        # Implementation for config validation testing
        pass
```

**Mock Factories** (`tests/unit/providers/refactor/utils/mock_factories.py`):
```python
from unittest.mock import Mock
from typing import Dict, Any, List

class MockAPIFactory:
    """Factory for creating consistent API mocks."""

    @staticmethod
    def create_openai_success_response(image_urls: List[str]) -> Mock:
        """Create mock OpenAI API success response."""
        mock_response = Mock()
        mock_response.data = [Mock(url=url) for url in image_urls]
        return mock_response

    @staticmethod
    def create_openai_error_response(error_message: str) -> Mock:
        """Create mock OpenAI API error response."""
        mock_response = Mock()
        mock_response.side_effect = Exception(error_message)
        return mock_response

    @staticmethod
    def create_forvo_success_response(audio_data: bytes) -> Mock:
        """Create mock Forvo API success response."""
        # Implementation for Forvo mock responses
        pass
```

### 0.3 Test Fixtures

**Provider Configurations** (`tests/unit/providers/refactor/fixtures/provider_configs.py`):
```python
"""Test configuration fixtures for provider testing."""

VALID_OPENAI_CONFIG = {
    "api_key": "sk-test123",
    "model": "dall-e-3",
    "size": "1024x1024",
    "rate_limit_delay": 1.0
}

INVALID_OPENAI_CONFIGS = {
    "missing_api_key": {
        "model": "dall-e-3"
    },
    "invalid_model": {
        "api_key": "sk-test123",
        "model": "invalid-model"
    }
}

VALID_FORVO_CONFIG = {
    "api_key": "test_forvo_key",
    "country_priorities": ["US", "ES", "MX"],
    "format": "mp3"
}

# Additional test configurations...
```

### 0.4 Testing Conventions

**Naming Conventions**:
- Test files: `test_[component]_[aspect].py`
- Test classes: `Test[Component][Aspect]`
- Test methods: `test_[action]_[condition]_[expected_result]`

**Example**:
```python
class TestMediaProviderConfig(ProviderTestBase):
    def test_constructor_with_valid_config_succeeds(self):
        """Test that valid config creates provider successfully."""
        pass

    def test_constructor_with_invalid_config_raises_value_error(self):
        """Test that invalid config raises ValueError."""
        pass
```

### 0.5 Mock Strategy

**API Mocking Approach**:
- Mock at the HTTP client level, not the provider method level
- Use consistent response formats matching real API structures
- Include both success and error scenarios for each API call
- Provide realistic timing delays for rate limiting tests

**File System Mocking**:
- Mock file creation and validation
- Test directory creation and cleanup
- Simulate file system errors (permissions, disk space)

## Testing Gateway

### Success Criteria
1. **Test Infrastructure**: Complete test structure for new provider patterns
2. **Test Utilities**: Reusable base classes and mock factories available
3. **Test Fixtures**: Comprehensive configuration and response fixtures
4. **No Regressions**: Existing tests continue to pass unchanged
5. **Documentation**: Clear testing conventions and examples

### Validation Checklist
- [ ] New test directory structure created
- [ ] ProviderTestBase class with common utilities implemented
- [ ] MockAPIFactory with provider-specific mocks available
- [ ] Test fixtures for all provider configurations created
- [ ] Testing conventions documented with examples
- [ ] All existing tests continue to pass
- [ ] New test infrastructure can be imported and used

### Testing Commands
```bash
# Verify existing tests still pass
python -m pytest tests/unit/providers/ -v --ignore=tests/unit/providers/refactor/

# Test new infrastructure
python -c "
from tests.unit.providers.refactor.utils.provider_test_base import ProviderTestBase
from tests.unit.providers.refactor.utils.mock_factories import MockAPIFactory
print('Test infrastructure imported successfully')
"

# Run any new infrastructure tests
python -m pytest tests/unit/providers/refactor/ -v
```

## Deliverables
1. **Test Directory Structure**: Complete organization for refactor testing
2. **Test Base Classes**: Reusable utilities for provider testing
3. **Mock Factories**: Consistent API response mocking
4. **Test Fixtures**: Comprehensive configuration examples
5. **Testing Documentation**: Conventions and usage examples

## Dependencies
- No implementation dependencies
- Sets foundation for TDD in stages 1-2
- Independent of existing provider code

## Estimated Effort
- Test structure setup: 2-3 hours
- Base classes and utilities: 3-4 hours
- Fixtures and mocks: 2-3 hours
- Documentation: 1-2 hours
- **Total**: 8-12 hours

## Notes
- This stage creates testing infrastructure without touching existing code
- Establishes patterns that stages 1-2 will follow for TDD
- All utilities should be immediately usable for writing TDD tests
- Focus on making test writing efficient and consistent
