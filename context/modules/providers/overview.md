# Provider System Overview

## Architecture

The provider system abstracts external service integrations using pluggable components that implement abstract base classes. Providers handle all API interactions, authentication, and data transformations for external services.

## Provider Types

### Data Providers (`src/providers/base/data_provider.py:11`)
- **Purpose**: Abstract data sources (JSON, databases, memory)
- **Interface**: `load_data()`, `save_data()`, `exists()`, `list_identifiers()`
- **Implementation**: `JSONDataProvider` for local file storage

### Media Providers (`src/providers/base/media_provider.py:44`)
- **Purpose**: Audio/image generation from external APIs
- **Interface**: `generate_media()`, `get_cost_estimate()`, `supported_types`
- **Implementations**: `ForvoProvider` (audio), `OpenAIProvider` (images/audio), `RunwareProvider` (images)

### Sync Providers (`src/providers/base/sync_provider.py:47`)
- **Purpose**: Sync content to flashcard systems
- **Interface**: `sync_cards()`, `sync_templates()`, `sync_media()`, `test_connection()`
- **Implementation**: `AnkiProvider` for AnkiConnect integration

## Registry & Factory Pattern

Provider registry (`src/providers/registry.py:18`) manages instances:
- **Registration**: Type-specific dictionaries for each provider category
- **Discovery**: Name-based lookup with default fallbacks
- **Factory**: `from_config()` creates providers from configuration
- **Global Access**: `get_provider_registry()` singleton pattern

## Pipeline Integration

Providers integrate with pipelines via:
- **Context injection**: Registry passed to pipeline context
- **Stage access**: Individual stages request needed providers
- **Type safety**: Providers validate requests before processing
- **Error handling**: Graceful degradation when providers unavailable
