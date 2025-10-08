# Provider Registry System

## Registry Architecture

### ProviderRegistry Class (`src/providers/registry.py:35`)

Central registry with dynamic loading and configuration injection:
- **Dynamic Loading**: `MEDIA_PROVIDER_REGISTRY` mapping enables runtime provider instantiation
- **Configuration Processing**: `_extract_provider_configs()` validates and organizes provider configurations
- **Data Providers**: `_data_providers` dictionary with enhanced registration
- **Audio Providers**: `_audio_providers` dictionary
- **Image Providers**: `_image_providers` dictionary
- **Sync Providers**: `_sync_providers` dictionary
- **Data Provider Configs**: `_data_provider_configs` dictionary for file conflict validation

### Registration Pattern

**Per-Category Methods:**
- `register_{type}_provider(name: str, provider: Instance, config: dict | None)` - Store provider with optional config
- `get_{type}_provider(name: str) -> Provider | None` - Retrieve provider
- `list_{type}_providers() -> list[str]` - Enumerate registered names

**Enhanced Data Provider Registration:**
- Accepts optional `config` parameter for file conflict validation
- Automatically validates file assignments via `_validate_file_conflicts()`
- Prevents overlapping file management between multiple data providers

**Default Naming**: Most providers registered with name `"default"` for consistent lookup

## Dynamic Loading System

`from_config(config: Config) -> ProviderRegistry` with dynamic provider instantiation:

### Data Provider Setup
- **Named Providers**: JSONDataProvider instances with pipeline assignments and permission control
- **Enhanced Configuration**: Supports `files` array and `read_only` boolean fields
- **File Conflict Validation**: Automatically validates provider file assignments during creation
- **Fallback**: Creates JSONDataProvider in current directory when no config

### Media Provider Setup (Dynamic)
- **Dynamic Loading**: Uses `MEDIA_PROVIDER_REGISTRY` mapping for runtime instantiation via `_create_media_provider()`
- **Configuration Injection**: Providers created with configuration injection and fail-fast validation
- **Error Handling**: Strict validation with clear error messages for unsupported provider types
- **Type Detection**: Provider class determined by `type` field in configuration

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
- **Data Provider Extensions**: Optional `files` array for file-specific access, `read_only` boolean for write protection
- **File Conflict Detection**: Validates no file overlaps between multiple data providers during initialization
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
