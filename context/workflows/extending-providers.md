# Extending Providers

Patterns for adding new provider integrations to the system.

## Creating New Provider Integrations

### 1. Implement Provider Interface
Choose appropriate base class:
- **DataProvider**: For data sources
- **AudioProvider**: For audio generation
- **ImageProvider**: For image generation
- **SyncProvider**: For external service sync

**Location**: `src/providers/<type>/<provider_name>_provider.py`

### 2. Provider Implementation
```python
class CustomProvider(DataProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def fetch_data(self, query: str) -> List[Dict]:
        # Implementation here
        pass
```

### 3. Register Provider and Configure Pipeline Access
Add to `src/providers/registry.py:258` factory method and configure with named provider format:
```json
{
  "providers": {
    "data": {
      "custom_data": {
        "type": "custom_data",
        "api_key": "${CUSTOM_API_KEY}",
        "pipelines": ["vocabulary"]
      }
    }
  }
}
```

**Provider patterns**: See `context/modules/providers/base.md`

## Provider Base Classes

### DataProvider (`src/providers/base/data_provider.py:11`)
**Abstract data sources (JSON, databases, memory)**
- **Interface**: `load_data()`, `save_data()`, `exists()`, `list_identifiers()`
- **Implementation example**: `JSONDataProvider` for local file storage

### MediaProvider (`src/providers/base/media_provider.py:44`)
**Audio/image generation from external APIs**
- **Interface**: `generate_media()`, `get_cost_estimate()`, `supported_types`
- **Request/Result types**: `MediaRequest`, `MediaResult` for structured communication

### SyncProvider (`src/providers/base/sync_provider.py:47`)
**Sync content to flashcard systems**
- **Interface**: `sync_cards()`, `sync_templates()`, `sync_media()`, `test_connection()`
- **Request/Result types**: `SyncRequest`, `SyncResult` for structured operations

### BaseAPIClient (`src/providers/base/api_client.py:48`)
**Common functionality for API-based providers**
- **Configuration**: Shared config loading and session setup
- **Authentication**: Environment-based API key loading
- **Retry Logic**: Exponential backoff with rate limiting
- **Error Handling**: Structured APIResponse and APIError types

## Implementation Steps

### Provider Development Process
1. Choose appropriate base class based on functionality
2. Implement required abstract methods
3. Add configuration schema and environment variables
4. Register in `ProviderRegistry.from_config()`
5. Create unit and integration tests
6. Add documentation and examples

### Configuration Integration
- Use named provider configuration with required `pipelines` field
- Add provider-specific configuration to JSON schema
- Use environment variables for sensitive data (API keys)
- Specify pipeline assignments: `["*"]` for all pipelines or specific pipeline names
- Follow existing naming conventions

### Error Handling
- Use structured exception types from base classes
- Implement retry logic for transient failures
- Provide clear error messages with actionable guidance
- Log provider interactions for debugging

## Testing Provider Integrations

### Unit Testing
```python
def test_custom_provider():
    config = {'api_key': 'test_key'}
    provider = CustomProvider(config)
    result = provider.fetch_data('test_query')
    assert result is not None
```

### Integration Testing
- Test actual API connections (with test credentials)
- Validate request/response formats
- Check error handling and retry logic
- Test configuration loading and validation

### Mock Testing
Create mocks for external services in `tests/mocks/` for reliable unit testing

## Extension Guidelines

### API Integration Best Practices
- Implement authentication according to service requirements
- Use appropriate request timeouts and retry strategies
- Handle rate limiting gracefully
- Cache responses when appropriate

### Configuration Management
- Use environment variables for credentials
- Provide sensible defaults for non-sensitive settings
- Validate configuration on provider initialization
- Document all configuration options

### Performance Optimization
- Implement connection pooling for HTTP clients
- Use async operations where beneficial
- Cache expensive operations
- Monitor and log performance metrics

## External Service Integration

### Common Integration Patterns
1. Abstract service behind provider interface
2. Implement authentication/authorization
3. Add retry logic and error handling
4. Create provider registry entry
5. Add configuration validation

### Service-Specific Considerations
- **Audio Services**: Handle different audio formats, quality settings
- **Image Services**: Manage image dimensions, formats, generation parameters
- **Sync Services**: Handle bulk operations, incremental updates
- **Data Services**: Support different data formats, query languages
