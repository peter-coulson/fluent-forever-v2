# Stage 3: Final Test Architecture & Base Class Enhancement

**REQUIRED READING**: First read `general_context.md` for architectural patterns and principles.

## Overview
Establish the final test architecture that represents the desired system behavior, then enhance MediaProvider base class to match these specifications. This stage creates the comprehensive test suite that guides all remaining implementation work and completely replaces legacy tests.

## Approach: Test Architecture First
Unlike Stages 1-2 which used TDD for foundational work, this stage:
1. **Designs Final Test Suite**: Creates comprehensive integration and E2E tests representing desired behavior
2. **Replaces Legacy Tests**: Removes old test patterns in favor of new architecture
3. **Implements to Tests**: Enhances base classes to satisfy the final test specifications

## Objectives
- Create final test architecture representing complete system behavior
- Replace all legacy provider tests with new architectural patterns
- Enhance MediaProvider base class to match test specifications
- Establish clean test foundation for Stage 4+ implementation

## Scope Boundaries

### In Scope
- **MediaProvider Base Class** (`src/providers/base/media_provider.py`):
  - Batch processing abstract methods and default implementations
  - File validation, directory management, and path handling
  - Rate limiting framework with configurable delays
  - Connection testing methods
  - Universal MediaRequest format with required `output_path`

- **New ImageProvider Class** (`src/providers/base/image_provider.py`):
  - Image-specific validation and processing methods
  - Inherits from MediaProvider with image specializations

### Out of Scope
- Concrete provider implementations (handled in Stage 4)
- Provider registry modifications (completed in Stage 2)
- Advanced error handling and resilience (handled in Stage 5)

## Dependencies
- **Requires**: Stage 1 (configuration injection), Stage 2 (dynamic registry)
- **Enables**: Stage 4 (provider implementations can use enhanced base classes)

## Implementation Areas

### 3.1 Batch Processing Framework
- Abstract `generate_batch()` method for provider implementations
- Default sequential processing with rate limiting
- Batch result aggregation and error collection
- Progress tracking for large batch operations

### 3.2 File Management System
- Universal file validation for all media types
- Directory creation and path management
- Filename validation and sanitization
- Post-processing file verification

### 3.3 Rate Limiting Infrastructure
- Configurable delays between requests
- Sequential processing with exponential backoff retry
- Provider-specific rate limit configuration
- Simple but extensible architecture for future enhancements

### 3.4 Connection Testing Framework
- Abstract connection testing methods
- Provider-specific implementation hooks
- Health check capabilities for provider validation

### 3.5 ImageProvider Specialization
- Image-specific file format validation
- Dimension and quality checks
- Image processing utility methods

## Testing Gateway

### Success Criteria
1. **Enhanced Base Classes**: MediaProvider and ImageProvider have full functionality
2. **Backward Compatibility**: All existing providers work with enhanced base classes
3. **Abstract Methods**: New abstract methods properly enforced for subclasses
4. **File Operations**: File validation and management work across all media types
5. **Rate Limiting**: Sequential processing with configurable delays functional
6. **Test Coverage**: Comprehensive unit tests for all new functionality

### Testing Approach
- Unit tests for each enhancement area
- Integration tests with mock provider implementations
- Performance validation for batch processing
- Backward compatibility verification with existing providers

### Validation Checklist
- [ ] Batch processing framework operational
- [ ] File validation methods work for all media types
- [ ] Rate limiting prevents API overuse
- [ ] Connection testing framework functional
- [ ] ImageProvider inherits correctly from MediaProvider
- [ ] All existing provider tests continue to pass
- [ ] New unit tests achieve >90% coverage

## Deliverables
1. **Enhanced MediaProvider Base Class**: Full batch processing and file management
2. **ImageProvider Specialization**: Image-specific functionality
3. **Comprehensive Test Suite**: Unit and integration tests for all enhancements
4. **Documentation**: Updated class documentation and usage examples

## Estimated Effort
- Implementation: 6-8 hours
- Testing: 4-6 hours
- Documentation: 2 hours
- **Total**: 12-16 hours

## Notes
- This stage provides the enhanced foundation that concrete providers will build upon
- Changes are primarily additive to maintain backward compatibility
- Focus on simple, extensible implementations that can be enhanced in future iterations
- Success enables Stage 4 providers to leverage advanced functionality
