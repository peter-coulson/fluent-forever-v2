# Provider Registry System

## Registry Architecture

### ProviderRegistry Class (`src/providers/registry.py:18`)

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

## Factory Method (`src/providers/registry.py:161`)

`from_config(config: Config) -> ProviderRegistry` creates populated registry:

### Data Provider Setup
- **Default**: JSONDataProvider with configurable base_path (`src/providers/registry.py:177`)
- **Fallback**: Creates JSONDataProvider in current directory when no config

### Media Provider Setup (Optional)
- **Audio**: ForvoProvider when `providers.audio.type = "forvo"` (`src/providers/registry.py:189`)
- **Image**: RunwareProvider or OpenAIProvider based on config type (`src/providers/registry.py:203`)
- **Conditional**: Only created when configuration sections present

### Sync Provider Setup (Required)
- **Default**: AnkiProvider when `providers.sync.type = "anki"` (`src/providers/registry.py:220`)
- **Validation**: Raises error for unsupported sync types

## Global Registry Pattern

### Singleton Access (`src/providers/registry.py:236`)
- `get_provider_registry() -> ProviderRegistry` - Global instance
- **Initialization**: Lazy-loaded on first access
- **Thread Safety**: Single global instance shared across system

### Usage in Pipelines
Registry injected into pipeline context, stages access via:
```python
data_provider = context.provider_registry.get_data_provider("default")
audio_provider = context.provider_registry.get_audio_provider("default")
```

## Provider Discovery

### Default Provider Pattern
Most providers registered with `"default"` name, allowing consistent lookup:
- Data: Always present (JSONDataProvider fallback)
- Audio: Optional, present when API configured
- Image: Optional, type determined by config
- Sync: Always present (AnkiProvider default)

### Provider Information (`src/providers/registry.py:135`)
`get_provider_info()` returns registry state:
- Provider counts by category
- Registered provider names
- Useful for debugging and system status

## Configuration-Based Selection

### Legacy Support (`src/providers/registry.py:173`)
Registry factory handles config structure migration:
- Old: `providers.data.type = "json"`
- New: Structured provider config sections
- Fallback: Default providers when config absent

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
