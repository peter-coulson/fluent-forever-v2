# Configuration System

## Config Class
**Location**: `src/core/config.py:13`

Simplified configuration management system providing JSON-based configuration loading with environment variable substitution. Handles provider settings, system configuration, and runtime environment integration.

## Configuration Loading

### Initialization
- **Default Path**: `config.json` in current working directory (`config.py:20`)
- **Custom Path**: Constructor accepts optional `config_path` parameter (`config.py:16`)
- **Graceful Degradation**: Missing config file results in empty configuration (`config.py:29-32`)

### File Loading Process
1. **File Existence Check**: Validates config file exists
2. **JSON Parsing**: Loads JSON content with error handling (`config.py:35-39`)
3. **Environment Substitution**: Processes `${VAR}` and `${VAR:default}` patterns (`config.py:45`)
4. **Recursive Processing**: Handles nested dictionaries and lists (`config.py:47-60`)

## Environment Variable Substitution

### Pattern Syntax
- **Simple**: `${VARIABLE_NAME}` - Required environment variable
- **With Default**: `${VARIABLE_NAME:default_value}` - Falls back to default if unset

### Resolution Logic
**Location**: `src/core/config.py:62-74`
- Uses regex pattern: `\$\{([^}:]+)(?::([^}]*))?\}`
- Missing variables without defaults retain original `${VAR}` syntax
- Empty string defaults supported: `${API_KEY:}`

### Substitution Scope
- **Recursive**: Processes all nested dictionaries and lists (`config.py:49-60`)
- **String Only**: Only applies to string values, preserves other data types
- **In-Place**: Modifies configuration data structure during loading

## Configuration Access Patterns

### Generic Access
- **get()** (`config.py:76`): Dot notation key access (e.g., `'providers.anki.deck_name'`)
- **to_dict()** (`config.py:103`): Return full configuration as dictionary copy

### Specialized Access Methods
- **get_provider()** (`config.py:89`): Extract provider configuration by name
- **get_system_settings()** (`config.py:96`): Extract system-level settings

## Configuration Structure

### Expected JSON Format
```json
{
  "providers": {
    "anki": {
      "deck_name": "${ANKI_DECK_NAME:Spanish Learning}",
      "api_url": "${ANKI_CONNECT_URL:http://localhost:8765}"
    },
    "openai": {
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-4"
    }
  },
  "system": {
    "data_dir": "${DATA_DIR:./data}",
    "temp_dir": "${TEMP_DIR:/tmp}"
  }
}
```

### Key Conventions
- **providers.{name}**: External service configuration sections
- **system**: Application-level settings
- Environment variables for sensitive data (API keys, URLs)
- Sensible defaults for non-sensitive configuration

## Error Handling

### File System Errors
- **Missing File**: Empty config returned, no exception (`config.py:29-32`)
- **Read Errors**: OSError caught, empty config returned (`config.py:40-42`)
- **JSON Parse Errors**: Re-raised to caller for debugging (`config.py:37-39`)

### Configuration Access
- **Invalid Keys**: Dot notation access returns provided default
- **Type Safety**: Provider/system getters validate dict return type
- **Graceful Degradation**: Invalid configurations return empty dicts rather than failing

## Integration Patterns

### Pipeline Context Integration
- Configuration loaded into `PipelineContext.config` field
- Stages access via: `context.config['providers']['service_name']`

### Class Method Alternative
- **Config.load()** (`config.py:108`): Class method factory for compatibility
- Equivalent to constructor but matches common loading patterns
