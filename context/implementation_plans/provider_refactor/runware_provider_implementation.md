# Runware Provider Implementation Plan

## Overview

Implement a complete Runware AI image generation provider following the established TDD methodology and clean architecture patterns from the provider refactor.

## Background

Runware (runware.ai) is a high-performance AI image generation API that provides:
- Multiple model support (SD, SDXL, etc.)
- High-speed generation (~2-3s per image)
- Batch processing capabilities
- Cost-effective pricing
- RESTful API with simple authentication

## Implementation Requirements

### 1. Provider Architecture

**Base Class**: Extends `ImageProvider` (from `src/providers/base/image_provider.py`)
**Location**: `src/providers/image/runware_provider.py`

### 2. Configuration Schema

```yaml
providers:
  image:
    runware:
      api_key: "your-api-key"
      model: "runware:100@1"  # Default model
      image_size: "512x512"   # Default size
      steps: 20               # Generation steps
      guidance: 7             # CFG scale
      rate_limit_delay: 1.0   # Seconds between requests
      timeout: 30             # Request timeout
      batch_size: 4           # Max batch size
```

### 3. Core Features

#### 3.1 Configuration Validation
- **Required**: `api_key`
- **Optional**: All other parameters with sensible defaults
- **Validation**: Model format, image size format, numeric ranges
- **Fail-Fast**: Invalid config raises `ValueError` at initialization

#### 3.2 Media Generation
- **Single Request**: `generate_media(request: MediaRequest) -> MediaResult`
- **Batch Processing**: `generate_batch(requests: list[MediaRequest]) -> list[MediaResult]`
- **Rate Limiting**: Configurable delay between API calls
- **Error Handling**: Comprehensive retry logic and error mapping

#### 3.3 File Management
- **Path Generation**: `media/images/{content_hash}_{model}_{timestamp}.png`
- **Validation**: File size, format verification
- **Cleanup**: Temporary file handling

## TDD Implementation Sequence

### Phase 1: Test Architecture

#### 1.1 Unit Tests (`tests/unit/providers/image/test_runware_provider.py`)

```python
class TestRunwareProvider:
    """Comprehensive unit tests for Runware provider"""

    def test_config_injection_validation(self):
        """Test: Config injection with fail-fast validation"""
        # Valid config initialization
        # Invalid config rejection (missing api_key, invalid model, etc.)

    def test_api_key_validation(self):
        """Test: API key validation and masking in logs"""
        # Proper API key handling
        # Sensitive data protection

    def test_model_configuration(self):
        """Test: Model selection and parameter validation"""
        # Default model usage
        # Custom model validation
        # Invalid model rejection

    def test_image_generation_request_format(self):
        """Test: API request formatting and parameters"""
        # Proper request structure
        # Parameter mapping
        # Content encoding

    def test_batch_processing_implementation(self):
        """Test: Batch processing with rate limiting"""
        # Sequential processing
        # Rate limit compliance
        # Partial batch failures

    def test_error_handling_comprehensive(self):
        """Test: All error scenarios and recovery"""
        # API errors (401, 429, 500)
        # Network failures
        # Invalid responses
        # Timeout handling

    def test_file_path_generation(self):
        """Test: File path generation with proper naming"""
        # Hash-based naming
        # Special character handling
        # Path sanitization

    def test_metadata_extraction(self):
        """Test: Response metadata extraction and storage"""
        # Generation parameters
        # API response metadata
        # File information
```

#### 1.2 Integration Tests (`tests/integration/test_runware_integration.py`)

```python
class TestRunwareIntegration:
    """Integration tests with Runware API"""

    def test_real_api_integration(self):
        """Test: Real API calls with test credentials"""
        # Skip if no test API key available
        # Single image generation
        # Response validation

    def test_rate_limiting_compliance(self):
        """Test: Rate limiting prevents API overuse"""
        # Multiple rapid requests
        # Timing validation
        # No 429 errors

    def test_batch_processing_efficiency(self):
        """Test: Batch processing performance"""
        # Batch vs individual timing
        # Resource efficiency
        # Error isolation
```

### Phase 2: Implementation

#### 2.1 Core Provider (`src/providers/image/runware_provider.py`)

```python
class RunwareProvider(ImageProvider):
    """Runware AI image generation provider"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate Runware configuration"""
        required = ["api_key"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required Runware config key: {key}")

        # Validate model format
        model = config.get("model", "runware:100@1")
        if not self._is_valid_model(model):
            raise ValueError(f"Invalid Runware model format: {model}")

        # Validate image size
        size = config.get("image_size", "512x512")
        if not self._is_valid_size(size):
            raise ValueError(f"Invalid image size format: {size}")

    def _setup_from_config(self) -> None:
        """Initialize provider from config"""
        self.api_key = self.config["api_key"]
        self.model = self.config.get("model", "runware:100@1")
        self.image_size = self.config.get("image_size", "512x512")
        self.steps = self.config.get("steps", 20)
        self.guidance = self.config.get("guidance", 7)
        self._rate_limit_delay = self.config.get("rate_limit_delay", 1.0)
        self.timeout = self.config.get("timeout", 30)
        self.batch_size = self.config.get("batch_size", 4)

        # Prepare API session
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def generate_batch(self, requests: list[MediaRequest]) -> list[MediaResult]:
        """Generate images for batch requests with rate limiting"""
        # Implement chunked batch processing
        # Handle rate limiting
        # Error isolation per request

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """Generate single image using Runware API"""
        # API request formatting
        # Response handling
        # File download and validation
        # Metadata extraction
```

#### 2.2 Helper Methods

```python
    def _is_valid_model(self, model: str) -> bool:
        """Validate Runware model format"""
        # Pattern: "runware:ID@version" or custom formats

    def _is_valid_size(self, size: str) -> bool:
        """Validate image size format"""
        # Pattern: "WIDTHxHEIGHT"

    def _make_api_request(self, prompt: str, **params) -> dict:
        """Make API request with retry logic"""
        # Request formatting
        # Retry with exponential backoff
        # Error classification

    def _download_image(self, image_url: str, file_path: Path) -> bool:
        """Download and validate generated image"""
        # Streaming download
        # File validation
        # Error handling

    def _generate_file_path(self, request: MediaRequest) -> Path:
        """Generate unique file path for image"""
        # Content-based naming
        # Special character handling
        # Directory creation
```

### Phase 3: Registry Integration

#### 3.1 Provider Registration

Add to `src/providers/registry.py`:

```python
# Import
from .image.runware_provider import RunwareProvider

# Registration in _register_default_providers
def _register_default_providers(self) -> None:
    # ... existing providers ...

    # Image providers
    self.register_provider("image", "runware", RunwareProvider)
```

#### 3.2 Configuration Schema

Update configuration templates to include Runware provider option.

### Phase 4: Error Handling & Resilience

#### 4.1 Error Classification

```python
class RunwareError(Exception):
    """Base Runware provider error"""

class RunwareAuthError(RunwareError):
    """Authentication/authorization error"""

class RunwareRateLimitError(RunwareError):
    """Rate limit exceeded error"""

class RunwareGenerationError(RunwareError):
    """Image generation failed error"""
```

#### 4.2 Retry Logic

- **Exponential Backoff**: 1s, 2s, 4s, 8s delays
- **Retry Conditions**: Network errors, 5xx responses, rate limits
- **Max Retries**: 3 attempts per request
- **Circuit Breaker**: Stop retrying on auth failures

### Phase 5: Performance Optimization

#### 5.1 Batch Processing

- **Chunk Size**: Configurable batch sizes (default: 4)
- **Parallel Downloads**: Concurrent image downloads
- **Memory Management**: Stream processing for large images

#### 5.2 Caching Strategy

- **Response Caching**: Cache successful generations (optional)
- **Rate Limit Tracking**: Track and respect API limits
- **Connection Pooling**: Reuse HTTP connections

## Testing Strategy

### Test Data Requirements

- **Test API Key**: Use test/sandbox credentials if available
- **Mock Responses**: Comprehensive API response mocks
- **Image Fixtures**: Sample generated images for validation

### Performance Benchmarks

- **Single Generation**: < 5s total time
- **Batch Processing**: 50% faster than individual requests
- **Memory Usage**: < 100MB during typical operations
- **Error Recovery**: < 1s additional delay per retry

## Success Criteria

### Functionality

- ✅ All unit tests pass (>95% coverage)
- ✅ Integration tests with real API pass
- ✅ Batch processing working efficiently
- ✅ Error handling comprehensive and robust
- ✅ File operations 100% reliable

### Performance

- ✅ Generation speed competitive with OpenAI provider
- ✅ Batch processing shows measurable improvement
- ✅ Memory usage remains stable
- ✅ Rate limiting prevents API abuse

### Code Quality

- ✅ Follows established provider patterns
- ✅ Clean, readable, well-documented code
- ✅ Comprehensive error messages
- ✅ Secure handling of API credentials
- ✅ Consistent with codebase style

## Implementation Commands

```bash
# Phase 1: Create test files
touch tests/unit/providers/image/test_runware_provider.py
touch tests/integration/test_runware_integration.py

# Phase 2: Run TDD cycles
pytest tests/unit/providers/image/test_runware_provider.py -v  # RED
# Implement provider
pytest tests/unit/providers/image/test_runware_provider.py -v  # GREEN

# Phase 3: Integration validation
pytest tests/integration/test_runware_integration.py -v

# Phase 4: Full test suite
pytest tests/ -v --cov=src/providers/image/runware_provider
```

## Notes

- **API Documentation**: https://docs.runware.ai/
- **Model Selection**: Research latest available models
- **Cost Optimization**: Implement cost tracking if needed
- **Future Features**: Support for additional Runware features (upscaling, variations, etc.)

The implementation should be complete when all tests pass and the provider integrates seamlessly with the existing pipeline system.
