# Provider Registry System

## Registry Architecture

### ProviderRegistry Class (`src/providers/registry.py:20`)

Central registry managing provider instances by category:
- **Data Providers**: `_data_providers` dictionary
- **Audio Providers**: `_audio_providers` dictionary
- **Image Providers**: `_image_providers` dictionary
- **Sync Providers**: `_sync_providers` dictionary

### Registration Pattern

**Per-Category Methods:**
- `register_{type}_provider(name: str, provider: Instance)` - Store provider
- `get_{type}_provider(name: str) -> Provider | None` - Retrieve provider
- `list_{type}_providers() -> list[str]` - Enumerate registered names

**Default Naming**: Most providers registered with name `"default"` for consistent lookup

## Factory Method (`src/providers/registry.py:258`)

`from_config(config: Config) -> ProviderRegistry` creates populated registry:

### Data Provider Setup
- **Named Providers**: JSONDataProvider instances with pipeline assignments
- **Fallback**: Creates JSONDataProvider in current directory when no config

### Media Provider Setup (Optional)
- **Audio**: ForvoProvider instances with pipeline restrictions
- **Image**: RunwareProvider or OpenAIProvider instances with pipeline assignments
- **Conditional**: Only created when configuration sections present

### Sync Provider Setup (Required)
- **Named Providers**: AnkiProvider instances with configurable pipeline access
- **Validation**: Raises error for unsupported sync types

## Global Registry Pattern

### Pipeline-Filtered Access (`src/providers/registry.py:194`)
- `get_provider_registry() -> ProviderRegistry` - Global instance
- **Initialization**: Lazy-loaded on first access
- **Thread Safety**: Single global instance shared across system

### Usage in Pipelines
Filtered providers injected into pipeline context, stages access via:
```python
providers = context.get("providers")
data_provider = providers["data"]["provider_name"]
audio_provider = providers["audio"]["provider_name"]
```

## Provider Discovery

### Default Provider Pattern
Most providers registered with `"default"` name, allowing consistent lookup:
- Data: Always present (JSONDataProvider fallback)
- Audio: Optional, present when API configured
- Image: Optional, type determined by config
- Sync: Always present (AnkiProvider default)

### Provider Information (`src/providers/registry.py:162`)
`get_provider_info()` returns registry state:
- Provider counts by category
- Registered provider names
- Useful for debugging and system status

## Configuration-Based Selection

### Configuration Validation (`src/providers/registry.py:273`)
Registry factory enforces new configuration format:
- **Required Format**: `providers.{type}.{name}` with mandatory `pipelines` field
- **Old Format Rejection**: Detects and rejects legacy configurations with helpful error messages
- **Default Fallback**: Creates default providers when no configuration sections present

### Type Mapping
Configuration `type` field maps to provider classes:
- `"json"` → JSONDataProvider
- `"forvo"` → ForvoProvider
- `"runware"` → RunwareProvider
- `"openai"` → OpenAIProvider
- `"anki"` → AnkiProvider

## Extension Pattern

To register new provider types:
1. Add new category methods to ProviderRegistry
2. Update factory method with configuration mapping
3. Import provider class conditionally in factory
4. Add configuration validation and error handling
