# Stage 4: Clean Provider Implementation

**REQUIRED READING**: First read `general_context.md` for architectural patterns and principles.

## Overview
Implement all concrete providers to satisfy the final test architecture established in Stage 3. This stage completely replaces existing provider implementations with clean code following the established patterns, removing all legacy functionality.

## Approach: Implementation to Final Tests
This stage implements providers to satisfy the comprehensive test suite from Stage 3:
- **Test-Driven**: Final test suite defines exact behavior requirements
- **Clean Implementation**: Completely new provider code, no legacy compatibility
- **Full Cleanup**: Remove all old provider patterns and fallback logic

## Objectives
- Implement clean OpenAI Provider matching Stage 3 test specifications
- Implement clean Runware Provider using new architectural patterns
- Implement clean Forvo Provider without complex fallback logic or static data
- Remove all legacy provider code and compatibility layers
- Ensure all providers satisfy the final test suite requirements

## Scope Boundaries

### In Scope
- **OpenAI Provider** (`src/providers/image/openai_provider.py`):
  - Constructor config injection implementation
  - Batch processing using sequential requests with rate limiting
  - Connection testing and API integration
  - File management using base class methods

- **Runware Provider** (`src/providers/image/runware_provider.py`):
  - Constructor config injection implementation
  - Batch processing using native multi-task API
  - Connection testing and task-based API integration
  - File management using base class methods

- **Forvo Provider** (`src/providers/audio/forvo_provider.py`):
  - Remove complex fallback configuration logic
  - Remove static data (country priorities, language defaults)
  - Constructor config injection implementation
  - Batch processing for multiple word requests

### Out of Scope
- Base class modifications (completed in Stage 3)
- Registry changes (completed in Stage 2)
- New provider types or advanced error handling (Stage 5)

## Dependencies
- **Requires**: Stages 1-3 completion (config injection, dynamic registry, enhanced base classes)
- **Enables**: Stage 5 (error handling improvements) and production readiness

## Implementation Strategy

### 4.1 Configuration Migration Pattern
Each provider will:
- Implement `validate_config()` method with provider-specific validation
- Use `_setup_from_config()` for initialization from validated configuration
- Remove all runtime configuration loading and fallback logic
- Move static data (API endpoints, model names, etc.) to configuration

### 4.2 Batch Processing Implementation
- **OpenAI**: Sequential processing with rate limiting (15 requests/minute)
- **Runware**: Use native multi-task API with task batching
- **Forvo**: Sequential audio requests with language/country grouping

### 4.3 API Integration Updates
- Use centralized API key loading from base class
- Implement provider-specific `_test_connection_impl()` methods
- Apply base class file validation and directory management
- Leverage enhanced error handling from base class

## Testing Gateway

### Success Criteria
1. **Configuration Injection**: All providers receive and validate configuration correctly
2. **Batch Processing**: Each provider can process multiple requests efficiently
3. **API Integration**: All API calls work with proper authentication and error handling
4. **File Management**: Generated/downloaded files pass validation
5. **Backward Compatibility**: All existing functionality preserved
6. **Performance**: Batch processing shows measurable improvements over individual requests

### Testing Approach
- Unit tests for each updated provider with mocked APIs
- Integration tests with actual API calls (where possible with test credentials)
- Batch processing performance validation
- Configuration validation testing with various config scenarios
- End-to-end testing with pipeline integration

### Validation Checklist
- [ ] All providers implement required abstract methods
- [ ] Configuration validation works for each provider
- [ ] Batch processing functional for all provider types
- [ ] API integration maintains existing functionality
- [ ] File operations use base class methods correctly
- [ ] Provider-specific tests pass with new implementations
- [ ] Integration with pipeline system works correctly

## Provider-Specific Considerations

### OpenAI Provider
- Handle DALL-E API rate limits with appropriate delays
- Implement retry logic for rate limit responses
- Direct image generation to specified output paths

### Runware Provider
- Leverage task-based API architecture for efficient batch processing
- Handle both synchronous and asynchronous task processing
- Implement webhook support if beneficial for batch operations

### Forvo Provider
- Remove hardcoded country priority lists (move to config)
- Simplify language handling using configuration
- Maintain audio quality and download functionality

## Deliverables
1. **Updated Provider Implementations**: All three providers using new architecture
2. **Configuration Examples**: Sample configurations for each provider
3. **Provider-Specific Tests**: Comprehensive test coverage for updated implementations
4. **Migration Documentation**: Guide for updating provider configurations

## Estimated Effort
- OpenAI Provider: 4-6 hours
- Runware Provider: 4-6 hours
- Forvo Provider: 3-5 hours (complex refactor of existing logic)
- Testing: 6-8 hours
- Documentation: 2-3 hours
- **Total**: 19-28 hours

## Risk Mitigation
- **API Changes**: Test with actual APIs where possible, mock for unavailable services
- **Configuration Compatibility**: Provide migration path for existing configurations
- **Feature Regression**: Comprehensive testing to ensure no functionality loss
- **Performance Impact**: Benchmark new implementations against existing code

## Notes
- This stage represents the most complex implementation work in the refactor
- Success here delivers working providers with all architectural improvements
- Each provider may require different approaches based on their API characteristics
- Detailed implementation plans should be created after Stages 1-3 are complete
