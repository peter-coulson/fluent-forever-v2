# Provider Refactor Implementation Plan

## Overview
This document outlines a high-level implementation plan for refactoring the image and media provider system to support batch processing, unified interfaces, and proper file validation.

## Current State Analysis

### Existing Provider Structure
- **MediaProvider Base Class** (`src/providers/base/media_provider.py`):
  - Well-designed abstract interface with MediaRequest/MediaResult patterns
  - Supports single request processing with validation and logging
  - Includes cost estimation capabilities
  - Has convenience methods for image/audio generation

- **Image Providers**:
  - **OpenAI Provider** (`src/providers/image/openai_provider.py`): Placeholder implementation with cost estimation and `_download_image` method
  - **Runware Provider** (`src/providers/image/runware_provider.py`): Placeholder implementation with basic batch support and `_download_image` method

- **Audio Provider**:
  - **Forvo Provider** (`src/providers/audio/forvo_provider.py`): Fully implemented with country prioritization, API client integration, and audio download capabilities. **Contains complex fallback configuration logic and static data that needs refactoring.**

### API Research Findings

#### OpenAI DALL-E API
- **Rate Limits**: 50 images/min (community reports suggest 15 img/min for some users)
- **Best Practices**:
  - Implement exponential backoff retry logic
  - Use batch API for non-real-time tasks (50% cost savings)
  - Bundle multiple tasks per request when possible
  - Monitor usage patterns and plan for tier upgrades
  - Implement fallback strategies for rate limit scenarios

#### Runware API
- **Rate Limits**: No specific limits documented - auto-scaling architecture
- **Batch Processing**: Native multi-task support in single API calls
- **Features**:
  - Task-based system with concurrent processing
  - Webhook support for batch result delivery
  - Sync/async modes based on processing time
  - Industry-leading speeds with custom hardware optimization
  - Pay-as-you-go pricing model

## Implementation Plan

### Phase 1: Base Class Enhancements

#### 1.1 MediaProvider Base Class Updates
- **Add Batch Processing Support**:
  - `generate_batch(requests: list[MediaRequest]) -> list[MediaResult]` abstract method
  - Default implementation processes requests sequentially with rate limiting
  - Architecture designed for easy future parallel processing enhancement

- **Universal Input/Output Format**:
  - Standardize MediaRequest to include `output_path` as required field
  - Add validation for output path directory existence
  - Ensure consistent file path handling across all providers

- **Configuration Management**:
  - `_load_api_key(env_var: str) -> str` - centralized API key loading with fail-fast
  - `_load_config(provider_name: str) -> dict` - centralized configuration loading
  - Remove all fallback logic - fail immediately on missing config/keys
  - No static data in provider implementations

- **File Management and Validation**:
  - `_validate_media_file(file_path: Path, media_type: str) -> bool` - universal media file validation
  - `_ensure_output_directory(path: Path) -> None` - create output directories as needed
  - `_validate_filename(file_path: Path) -> bool` - ensure proper filename structure and extension
  - Post-processing validation that files exist at expected paths
  - Update results with validation errors if files missing/corrupted

- **Connection Testing**:
  - `test_connection() -> bool` - shared connection testing pattern
  - Provider-specific implementation via abstract method `_test_connection_impl() -> bool`

- **Rate Limiting Framework**:
  - Simple sequential rate limiting with delays between requests
  - Configurable rate limits per provider
  - Basic retry logic with exponential backoff
  - Structure ready for future advanced rate limiting algorithms

- **Abstract Method Updates**:
  - Add `_test_connection_impl() -> bool` abstract method
  - Remove `get_cost_estimate()` and `estimate_cost()` methods
  - Keep `_generate_media_impl()` and `generate_batch()` abstract methods

- **Removed for Simplicity**:
  - All cost estimation methods (can be added back later if needed)
  - Complex fallback configuration logic

#### 1.2 ImageProvider Base Class Creation
- **New Abstract Class**: `src/providers/base/image_provider.py`
- **Shared Methods**:
  - Image-specific validation logic (formats, dimensions)
  - Provider-specific generation implementations

- **Note**: Common functionality like file validation, directory creation, and filename validation should be in the MediaProvider base class since these are universal needs across all media types.

### Phase 2: Provider Implementations

#### 2.1 OpenAI Provider Refactor
- **API Integration**:
  - Implement OpenAI DALL-E 3 API calls using base class configuration methods
  - Use centralized API key loading (no fallback logic)
  - Implement `_test_connection_impl()` for provider-specific connection testing

- **Configuration**:
  - All configuration loaded via base class methods
  - No static data (model names, sizes, etc. from config)
  - Fail fast on missing API keys or configuration

- **Batch Processing**:
  - Sequential processing with simple delays between requests
  - Basic retry logic for rate limit errors
  - Simple progress tracking and error collection

- **File Management**:
  - Generate images directly to specified paths (no separate download step needed)
  - Use base class file validation methods post-generation
  - Use base class filename validation before generation

#### 2.2 Runware Provider Refactor
- **API Integration**:
  - Implement Runware task-based API using base class configuration methods
  - Use centralized API key loading (no fallback logic)
  - Implement `_test_connection_impl()` for provider-specific connection testing

- **Configuration**:
  - All configuration loaded via base class methods
  - No static data (model names, parameters, etc. from config)
  - Fail fast on missing API keys or configuration

- **Batch Processing**:
  - Use Runware's multi-task API in sequential batches
  - Simple task result collection and validation
  - Basic error recovery for failed tasks

- **File Management**:
  - Generate images directly to specified paths using native API capabilities
  - Use base class file validation methods post-generation
  - Use base class filename validation before generation

#### 2.3 Forvo Provider Updates
- **Configuration Refactor**:
  - Use base class configuration methods (remove complex fallback logic)
  - Remove static data (country priorities, language defaults from config)
  - Implement `_test_connection_impl()` for provider-specific connection testing
  - Fail fast on missing API keys or configuration

- **Universal Format Compliance**:
  - Update to use required `output_path` parameter in MediaRequest
  - Use base class file validation methods post-download
  - Use base class filename validation before processing

- **Batch Processing**:
  - Process multiple words sequentially with rate limiting
  - Group requests by language/country based on config (not static data)
  - Simple progress tracking for vocabulary lists

### Phase 3: Architecture Enhancements

#### 3.1 Provider Registry Updates
- **Simple Provider Registration**:
  - Basic provider capability flags (batch_supported)
  - Rate limit configuration per provider
  - Structure for future fallback provider chains

#### 3.2 Configuration Management
- **Centralized Configuration**:
  - Move all configuration loading to MediaProvider base class
  - Standardized API key loading with fail-fast behavior
  - Provider-specific settings loaded via base class methods
  - Remove all static data and hardcoded values from provider implementations

#### 3.3 Error Handling and Resilience
- **Basic Error Recovery**:
  - Simple batch failure handling (continue on error)
  - Basic request retry with backoff
  - Clear error reporting and logging
  - Architecture ready for future failover mechanisms

### Phase 4: Testing and Validation

#### 4.1 Unit Testing
- **Provider-Specific Tests**:
  - Mock API responses and error conditions
  - Sequential batch processing validation
  - File validation and error scenarios
  - Basic rate limiting and retry logic

#### 4.2 Integration Testing
- **End-to-End Workflows**:
  - Sequential batch processing tests
  - File system integration testing
  - Cost estimation accuracy validation

#### 4.3 Performance Testing
- **Sequential Processing Performance**:
  - Memory usage during large batches
  - Rate limiting effectiveness
  - Provider comparison benchmarks

## Implementation Considerations

### Rate Limiting Strategy
- **OpenAI**: Sequential processing with 4-second delays (15 requests/minute)
- **Runware**: Sequential processing with minimal delays, monitor for rate limit responses
- **Forvo**: Sequential processing with delays to respect free API limits

### File Management Approach
- **Input Validation**: Validate filename structure and extensions before processing
- **Directory Management**: Ensure output directories exist before generation/download
- **Post-validation**: Verify files exist, are correct format, and meet size requirements
- **No Separate Downloads**: Image generation APIs save directly to specified paths
- **Error Recovery**: Implement retry mechanisms for failed generations

### Batch Processing Patterns
- **Sequential Processing**: Process all requests one by one with rate limiting
- **Provider-Native Batching**: Use Runware's multi-task API but process batches sequentially
- **Simple Error Handling**: Continue processing remaining items on individual failures
- **Future Extensibility**: Architecture designed to easily add parallel processing later

### Configuration Management
- **Environment Variables**: API keys and sensitive configuration
- **JSON Configuration**: Provider settings and basic rate limits
- **Simple Configuration**: Focus on essential settings, avoid over-configuration

## Success Criteria

1. **Unified Interface**: All providers follow consistent MediaRequest/MediaResult patterns
2. **Sequential Batch Processing**: Support for processing multiple requests reliably
3. **File Validation**: Reliable verification that requested files are created successfully
4. **Rate Limit Compliance**: Respect API limits with simple delays and retry logic
5. **Error Resilience**: Graceful handling of individual failures in batch processing
6. **Simplicity**: Clean, maintainable code that's easy to understand and extend
7. **Future Extensibility**: Architecture ready for parallel processing enhancements

## Risk Mitigation

1. **API Changes**: Monitor provider documentation for breaking changes
2. **Rate Limits**: Use conservative sequential processing with configurable delays
3. **File System Issues**: Simple error handling for disk space and permissions
4. **Configuration Management**: Centralized config loading with fail-fast behavior
5. **Complexity Creep**: Maintain focus on simplicity over optimization

## Future Enhancement Path

The sequential architecture is designed to easily support parallel processing:

1. **Rate Limiting**: Upgrade to token bucket algorithms with concurrent request pools
2. **Batch Processing**: Add thread/async pools for concurrent API requests
3. **Provider Optimization**: Implement provider-specific concurrent strategies
4. **Advanced Features**: WebSocket connections, streaming results, advanced retry logic

This approach ensures a solid, working foundation that can be enhanced incrementally without architectural rewrites.
