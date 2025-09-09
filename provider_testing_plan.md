# Providers Module Testing Plan

## Overview
This document outlines the minimal set of tests required to validate the providers module functionality. Tests are organized by provider type and focus on critical edge cases and core functionality.

## Test Categories

### 1. Provider Registry (`registry.py`)

#### Core Functionality Tests
- **Register/Retrieve Providers**: Verify providers can be registered and retrieved by name
- **Provider Not Found**: Ensure `None` is returned for non-existent providers
- **Provider Info Aggregation**: Validate `get_provider_info()` returns correct counts and capabilities
- **Registry Clearing**: Test `clear_all()` removes all registered providers

#### Edge Cases
- **Duplicate Registration**: Overwriting existing providers should work without error
- **Media Provider Type Filtering**: `get_media_providers_by_type()` correctly filters by supported types

### 2. Data Providers

#### JSONDataProvider (`data/json_provider.py`)
**Core Tests:**
- **Save/Load Success**: Basic save and load operations work correctly
- **File Not Found**: Loading non-existent file returns empty dict (not error)
- **Invalid JSON**: Loading malformed JSON raises `ValueError`
- **Empty File**: Loading empty file returns empty dict
- **Backup Creation**: Backup creates timestamped copy

**Edge Cases:**
- **Permission Denied**: Save operation handles write permission errors gracefully
- **Invalid Data Types**: Non-serializable data in save returns `False`
- **Directory Creation**: Save creates parent directories when needed

#### MemoryDataProvider (`data/memory_provider.py`)
**Core Tests:**
- **In-Memory Operations**: Save, load, exists, and list work correctly
- **Data Isolation**: Changes to returned data don't affect stored data (deep copy)
- **Clear Functionality**: `clear()` removes all stored data

### 3. Media Providers

#### ForvoProvider (`media/forvo_provider.py`)
**Core Tests:**
- **Connection Test**: `test_connection()` validates API availability
- **Audio Generation Success**: Valid word request returns audio file path
- **Word Not Found**: Non-existent word returns appropriate error
- **Country Priority**: Best pronunciation selected based on configured priorities

**Edge Cases:**
- **API Rate Limiting**: Rate limit responses trigger retry logic
- **Empty Word**: Empty content parameter returns validation error
- **Invalid Media Type**: Non-audio requests return unsupported type error
- **Network Failure**: Connection errors handled with appropriate retries

#### OpenAIProvider (`media/openai_provider.py`)
**Core Tests:**
- **Supported Types**: Returns correct list of supported media types
- **Cost Estimation**: Provides reasonable cost estimates for requests
- **Placeholder Behavior**: Currently returns "not implemented" errors appropriately

#### MockMediaProvider (`media/mock_provider.py`)
**Core Tests:**
- **Success Mode**: Generates mock results with tracking
- **Failure Mode**: Configured failure returns appropriate errors
- **Request Tracking**: History methods return accurate request logs
- **Supported Types**: Configurable type support works correctly

### 4. Sync Providers

#### AnkiProvider (`sync/anki_provider.py`)
**Core Tests:**
- **Connection Test**: Validates AnkiConnect availability
- **Card Sync Success**: Cards sync to Anki with correct field mapping
- **Service Unavailable**: Graceful handling when AnkiConnect not running
- **Template Sync**: Card templates update correctly in Anki

**Edge Cases:**
- **Invalid Note Type**: Sync with non-existent note type fails appropriately
- **Media File Sync**: Base64 encoding and file storage works correctly
- **Batch Operations**: Multiple cards sync with correct success counts
- **Anki Launch**: Auto-launch attempt when service not available

### 5. Base API Client (`base/api_client.py`)

#### Core Functionality Tests
- **Retry Logic**: Failed requests retry with exponential backoff
- **Rate Limiting**: 429 responses trigger wait-and-retry behavior
- **Configuration Loading**: Config loaded once and shared across instances
- **Timeout Handling**: Requests timeout after configured duration

#### Edge Cases
- **Config Not Found**: Graceful fallback when config.json missing
- **API Key Missing**: Clear error when environment variable not set
- **Network Errors**: Connection failures trigger retries
- **Non-JSON Responses**: Binary responses handled correctly
- **Invalid JSON**: Malformed JSON responses don't crash client

### 6. Factory Classes

#### MediaProviderFactory (`registry.py`)
**Core Tests:**
- **Provider Creation**: Each supported provider type creates successfully
- **Invalid Provider**: Unknown provider names return `None`
- **Fallback Configuration**: Primary fails, fallback providers attempted in order

#### DataProviderFactory (`registry.py`)
**Core Tests:**
- **JSON Provider**: Creates with valid base path
- **Memory Provider**: Creates successfully without parameters

#### SyncProviderFactory (`registry.py`)
**Core Tests:**
- **Anki Provider**: Creates successfully
- **Mock Provider**: Creates with configurable failure mode

### 7. Context Integration (`context_helper.py`)

#### Core Tests
- **Provider Setup**: All provider types registered in context correctly
- **Provider Retrieval**: Get providers by type and name from context
- **Configuration Loading**: Config loaded from file or defaults used
- **Fallback Providers**: Multiple providers of same type available

#### Edge Cases
- **Missing Config**: Setup works with minimal default configuration
- **Provider Creation Failures**: Individual provider failures don't prevent others

### 8. Configuration Integration (`config_integration.py`)

#### Core Tests
- **Provider Initialization**: Providers created from configuration
- **Legacy Config Support**: Old configuration structure still works
- **Disabled Providers**: Providers marked as disabled are not created

## Test Execution Priority

1. **Critical Path**: Registry, Base API Client, Mock Providers
2. **Core Providers**: Data providers, basic media provider functionality
3. **External Dependencies**: Forvo, Anki, OpenAI (may require API keys/services)
4. **Integration**: Context and configuration integration

## Notes

- Mock providers should be used for testing core functionality without external dependencies
- Real API providers (Forvo, OpenAI, Anki) may need separate integration test suites
- Configuration tests should use temporary config files to avoid affecting development setup
- All file operations should use temporary directories for test isolation

This testing plan focuses on the minimum tests needed to have confidence in the providers module while avoiding over-testing implementation details.
