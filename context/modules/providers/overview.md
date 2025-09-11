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

**Central provider management** (`src/providers/registry.py:18`):
- Type-specific registration for each provider category
- Name-based lookup with default fallbacks
- Configuration-driven provider instantiation
- Global singleton access for system-wide availability

## Pipeline Integration

Providers integrate seamlessly with the pipeline system:
- **Context injection**: Provider registry passed to pipeline execution context
- **Stage access**: Individual stages request specific providers as needed
- **Type safety**: Providers validate requests and return structured results
- **Error handling**: Graceful degradation when providers are unavailable or misconfigured

See `context/modules/providers/` for implementation details and `context/workflows/extending-providers.md` for extension patterns.
