# Provider Base Classes

## Abstract Interfaces

### DataProvider (`src/providers/base/data_provider.py:13`)

Core interface for data persistence with permission system:
- `load_data(identifier: str) -> dict[str, Any]` - Load by key/filename (`src/providers/base/data_provider.py:21`)
- `save_data(identifier: str, data: dict) -> bool` - Persist data (`src/providers/base/data_provider.py:52`)
- `exists(identifier: str) -> bool` - Check data availability
- `list_identifiers() -> list[str]` - Enumerate available data
- `backup_data(identifier: str) -> str | None` - Optional backup creation

**Permission System:**
- `is_read_only: bool` - Property to check write protection status
- `managed_files: list[str]` - Property for file-specific access control
- `set_read_only(read_only: bool)` - Configure write protection
- `set_managed_files(files: list[str])` - Set file access restrictions
- `validate_file_access(identifier: str)` - Validate file access permissions (`src/providers/base/data_provider.py:145`)
- `_check_write_permission(identifier: str)` - Internal write permission validation (`src/providers/base/data_provider.py:160`)

### MediaProvider (`src/providers/base/media_provider.py:46`)

Interface for media generation with typed requests:
- `supported_types: list[str]` - Media types ("audio", "image")
- `generate_media(request: MediaRequest) -> MediaResult` - Core generation method
- `get_cost_estimate(requests: list) -> dict` - Batch cost calculation
- Convenience methods: `generate_image()`, `generate_audio()`

**Request/Result Types:**
- `MediaRequest` (`src/providers/base/media_provider.py:14`) - Type, content, params, output path
- `MediaResult` (`src/providers/base/media_provider.py:31`) - Success flag, file path, metadata, error

### SyncProvider (`src/providers/base/sync_provider.py:49`)

Interface for external system synchronization:
- `test_connection() -> bool` - Verify target availability
- `sync_cards(cards: list[dict]) -> SyncResult` - Bulk card sync
- `sync_templates(note_type: str, templates: list) -> SyncResult` - Template sync
- `sync_media(media_files: list[Path]) -> SyncResult` - Media file sync
- `list_existing(note_type: str) -> list[dict]` - Query existing data

**Request/Result Types:**
- `SyncRequest` (`src/providers/base/sync_provider.py:14`) - Target, data, parameters
- `SyncResult` (`src/providers/base/sync_provider.py:32`) - Success status, processed count, metadata

## Base Infrastructure

### BaseAPIClient (`src/providers/base/api_client.py:48`)

Shared HTTP client infrastructure:
- **Configuration**: Shared config loading and session setup (`src/providers/base/api_client.py:54`)
- **Authentication**: Environment-based API key loading (`src/providers/base/api_client.py:100`)
- **Retry Logic**: Exponential backoff with rate limiting (`src/providers/base/api_client.py:109`)
- **Error Handling**: Structured APIResponse and APIError types (`src/providers/base/api_client.py:24`)

Abstract methods providers must implement:
- `test_connection() -> bool` - Service health check
- `get_service_info() -> dict` - Service metadata/capabilities

## Provider Lifecycle

1. **Initialization**: Load configuration and authenticate
2. **Registration**: Add to appropriate registry category
3. **Validation**: Implement required abstract methods
4. **Runtime**: Process requests through interface methods
5. **Error Handling**: Return structured error responses vs exceptions
