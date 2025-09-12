# Provider Implementations

## Data Providers

### JSONDataProvider (`src/providers/data/json_provider.py:15`)
- **Purpose**: Local file-based data persistence using JSON format with permission control
- **Configuration**:
  - `base_path` directory for JSON files
  - `read_only: bool` - Optional write protection (default: False)
  - `managed_files: list[str]` - Optional file access restrictions (default: None = all files)
- **Permission System**: Enforces read-only protection and file-specific access control
- **Features**: Auto-backup with timestamps, pretty-printed output
- **File Handling**: Identifier maps to `{identifier}.json`, graceful empty file handling
- **Access Validation**: Validates file access permissions on all operations
- **Thread Safety**: File-based operations, concurrent access considerations needed

## Media Providers

### ForvoProvider (`src/providers/audio/forvo_provider.py:20`)
- **Service**: Forvo pronunciation API for Spanish audio
- **Authentication**: `FORVO_API_KEY` environment variable
- **Configuration**: Country priorities for pronunciation selection (`src/providers/audio/forvo_provider.py:57`)
- **Selection Logic**: Multi-tier country grouping (MX > ES > AR/CO/PE) with vote-based ranking
- **Output**: Downloads MP3 files to `media/audio/{word}_{country}.mp3`
- **Rate Limits**: Free API with built-in retry logic

### OpenAIProvider (`src/providers/image/openai_provider.py:12`)
- **Status**: Placeholder implementation, not yet functional
- **Planned Support**: Images and audio via OpenAI API
- **Cost Structure**: $0.02 per request estimate
- **Integration**: Inherits MediaProvider interface

### RunwareProvider (`src/providers/image/runware_provider.py`)
- **Service**: Runware image generation API
- **Configuration**: Retrieved from registry factory method (`src/providers/registry.py:203`)
- **Implementation**: Referenced but not analyzed in current session

## Sync Providers

### AnkiProvider (`src/providers/sync/anki_provider.py:20`)
- **Service**: AnkiConnect local API integration
- **Connection**: HTTP to `127.0.0.1:8765`, auto-launches Anki if needed (`src/providers/sync/anki_provider.py:52`)
- **Authentication**: None required (local desktop app)
- **Configuration**: Deck name, note type, custom fields mapping (`src/providers/sync/anki_provider.py:26`)

**Sync Operations:**
- **Cards**: Bulk note creation with field mapping (`src/providers/sync/anki_provider.py:288`)
- **Templates**: Note type template updates (`src/providers/sync/anki_provider.py:370`)
- **Media**: Base64 file upload to Anki media folder (`src/providers/sync/anki_provider.py:406`)

**Field Mapping**: Front/Back/Audio/Image/IPA/Tags standard fields (`src/providers/sync/anki_provider.py:309`)

## Common Patterns

### Configuration Handling
Most providers support dual config paths:
- Legacy: `config["apis"][service_name]`
- Current: `config["providers"][type][service_name]`
- Graceful fallbacks to default values

### Error Handling
- **API Providers**: Structured APIResponse with retry logic
- **All Providers**: Return success/failure in result objects vs throwing exceptions
- **Connection Issues**: Test methods for service availability checks

### Authentication
- **Environment Variables**: Primary method for API keys
- **Graceful Degradation**: Placeholder keys for testing when env vars missing
- **Security**: No API keys logged or committed to config files

## Extension Patterns

To add new providers:
1. Inherit appropriate base class (DataProvider/MediaProvider/SyncProvider)
2. Implement required abstract methods
3. Add configuration section to config schema
4. Register in `ProviderRegistry.from_config()` (`src/providers/registry.py:161`)
5. Update factory method type mapping
