# Provider System Overview

## Architecture

The provider system abstracts external service integrations using pluggable components. Providers handle API interactions, authentication, and data transformations for external services like Anki, audio generation, and image creation.

## Provider Categories

### Data Providers
**Abstract data sources (JSON, databases)**
- Local file storage with JSON formatting
- Database connections and query interfaces

### Media Providers
**Audio/image generation with configuration injection pattern**
- **Configuration Injection**: Constructor-based config with fail-fast validation
- **Batch Processing**: Sequential processing with configurable rate limiting
- Text-to-speech services (Forvo)
- AI image generation (OpenAI, Runware)

### Sync Providers
**Integration with flashcard and learning systems**
- Anki card creation and synchronization
- Template management and media upload
- Bulk operations and progress tracking

## Registry & Factory Pattern

**Central provider management with dynamic loading and pipeline access control** (`src/providers/registry.py:25`):
- **Dynamic Loading**: `MEDIA_PROVIDER_REGISTRY` mapping enables runtime provider instantiation
- **Configuration Processing**: `_extract_provider_configs()` validates and organizes provider configurations by type
- Type-specific registration for each provider category
- **Pipeline Assignment System**: Named providers with configurable pipeline restrictions
- **Filtered Access**: `get_providers_for_pipeline()` returns only authorized providers
- Configuration injection with fail-fast validation and provider setup patterns
- Global singleton access for system-wide availability

## Pipeline Integration

Providers integrate seamlessly with the pipeline system:
- **Filtered Context Injection**: Only pipeline-authorized providers injected via `get_providers_for_pipeline()`
- **Access Control**: Named providers configured with `pipelines` field restrict access
- **Stage Access**: Individual stages access pre-filtered provider dict from context
- **Type Safety**: Providers validate requests and return structured results
- **Error Handling**: Graceful degradation when providers are unavailable or unauthorized

## Testing Integration

**Risk Assessment**: Provider components require risk assessment using `context/testing/meta/decision-framework.md` criteria:
- **External API Integration**: High-risk for configuration injection and authentication
- **Media Generation**: Medium-risk for data transformation and error handling
- **Registry System**: Medium-risk for provider discovery and access control

**Mock Boundaries**: Providers represent external dependencies requiring mocking strategies per `context/testing/strategy/mock-boundaries.md`:
- **Mock External APIs**: Service endpoints, authentication, network calls
- **Test Internal Logic**: Configuration processing, provider registry, access control

**Testing Strategy**: Reference `context/testing/strategy/risk-based-testing.md` for provider-specific testing approaches and scaffolding patterns.

See `context/modules/providers/` for implementation details and `context/workflows/extending-providers.md` for extension patterns.
