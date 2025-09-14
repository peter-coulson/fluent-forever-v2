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
    def __init__(self, config):
        super().__init__(config)
```

### 3. Register Provider and Configure Pipeline Access
Add to `MEDIA_PROVIDER_REGISTRY` mapping for dynamic loading and configure with named provider format:
```json
{
  "providers": {
    "data": {
      "custom_data": {
        "type": "custom_data",
        "api_key": "${CUSTOM_API_KEY}",
        "files": ["custom_dataset", "lookups"],
        "read_only": false,
        "pipelines": ["vocabulary"]
      }
    }
  }
}
```

**Provider patterns**: See `context/modules/providers/base.md`

## Provider Base Classes

### DataProvider (`src/providers/base/data_provider.py:13`)
**Abstract data sources with permission system (JSON, databases, memory)**
- **Core Interface**: `load_data()`, `save_data()`, `exists()`, `list_identifiers()`
- **Permission System**: `is_read_only`, `managed_files`, `validate_file_access()`, `_check_write_permission()`
- **Implementation example**: `JSONDataProvider` with read-only and file access controls

### MediaProvider (`src/providers/base/media_provider.py:46`)
**Audio/image generation with configuration injection**
- **Configuration Pattern**: Constructor injection with `validate_config()` and `_setup_from_config()`
- **Core Interface**: `generate_media()`, `generate_batch()`, `get_cost_estimate()`, `supported_types`
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
- **Enhanced Data Providers**: Optional `files` array and `read_only` boolean for permission control
- Add provider-specific configuration to JSON schema
- Use environment variables for sensitive data (API keys)
- Specify pipeline assignments: `["*"]` for all pipelines or specific pipeline names
- Follow existing naming conventions

### Permission Patterns (Data Providers)
- **Read-only providers**: Set `read_only: true` for source data protection
- **File-specific providers**: Use `files` array to restrict access to specific identifiers
- **File conflict prevention**: Registry validates no overlapping file assignments
- **Permission enforcement**: Override `load_data()`, `save_data()` to call validation methods
- **Error handling**: Use `PermissionError` for read-only, `ValueError` for file access violations

### Error Handling
- Use structured exception types from base classes
- Implement retry logic for transient failures
- Provide clear error messages with actionable guidance
- Log provider interactions for debugging

## Testing Provider Integrations

### Unit Testing
Test provider methods with mock configurations and validate return values.

### Integration Testing
- Test API connections with credentials
- Validate request/response formats
- Check error handling and retry logic

### Mock Testing
Create mocks for external services in `tests/mocks/` for reliable unit testing

### Permission System Testing (Data Providers)
**Unit Tests**: Test read-only protection with `pytest.raises(PermissionError)`
**File Access Tests**: Test file restrictions with `pytest.raises(ValueError, match="not managed")`
**Registry Tests**: Test file conflict detection during provider registration
**Test Files**: See `tests/unit/providers/base/test_data_provider_permissions.py`, `tests/unit/providers/test_registry_file_conflicts.py`

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
- Cache expensive operations and monitor performance metrics

## Extension Patterns
1. Abstract service behind provider interface
2. Implement authentication/authorization
3. Add retry logic and error handling
4. Create provider registry entry
5. Add configuration validation
6. **Audio/Image/Sync Services**: Handle format-specific requirements and bulk operations
