# Provider System Overview

## Architecture

The provider system abstracts external service integrations using pluggable components. Providers handle API interactions, authentication, and data transformations for external services like Anki, audio generation, and image creation.

## Provider Categories

### Data Providers
**Abstract data sources (JSON, databases)**
- Local file storage with JSON formatting
- Database connections and query interfaces

### Media Providers
**Audio/image generation from external APIs**
- Text-to-speech services (Forvo, ElevenLabs, Azure)
- AI image generation (OpenAI, Runware)
- Media format conversion and optimization

### Sync Providers
**Integration with flashcard and learning systems**
- Anki card creation and synchronization
- Template management and media upload
- Bulk operations and progress tracking

## Registry & Factory Pattern

**Central provider management with pipeline access control** (`src/providers/registry.py:25`):
- Type-specific registration for each provider category
- **Pipeline Assignment System**: Named providers with configurable pipeline restrictions
- **Filtered Access**: `get_providers_for_pipeline()` returns only authorized providers
- Configuration-driven provider instantiation with required `pipelines` field
- Global singleton access for system-wide availability

## Pipeline Integration

Providers integrate seamlessly with the pipeline system:
- **Filtered Context Injection**: Only pipeline-authorized providers injected via `get_providers_for_pipeline()`
- **Access Control**: Named providers configured with `pipelines` field restrict access
- **Stage Access**: Individual stages access pre-filtered provider dict from context
- **Type Safety**: Providers validate requests and return structured results
- **Error Handling**: Graceful degradation when providers are unavailable or unauthorized

See `context/modules/providers/` for implementation details and `context/workflows/extending-providers.md` for extension patterns.
