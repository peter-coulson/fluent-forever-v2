# Session 6: Configuration Refactor

## Mission
Consolidate all configuration into a unified, hierarchical system that supports pipeline-specific settings, provider configuration, and environment-based overrides.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan
- `context/refactor/completed_handoffs/05_cli_overhaul_handoff.md` - CLI system context
- `tests/e2e/05_configuration/` - Validation gates for this session
- Current config files: `config.json`, `.env`
- CLI configuration from Session 5

## Objectives

### Primary Goal
Create a unified configuration system that supports all components while maintaining clear separation between different types of settings.

### Target Configuration Structure
```
config/
├── core.json                   # System-wide settings
├── pipelines/                  # Pipeline-specific configurations
│   ├── vocabulary.json        # Vocabulary pipeline config
│   ├── conjugation.json       # Conjugation pipeline config
│   └── _template.json         # Template for new pipelines
├── providers/                  # Provider configurations
│   ├── openai.json           # OpenAI provider settings
│   ├── forvo.json            # Forvo provider settings
│   ├── anki.json             # Anki provider settings
│   └── _template.json        # Provider config template
├── environments/              # Environment-specific overrides
│   ├── development.json      # Dev environment
│   ├── production.json       # Production environment
│   └── testing.json          # Test environment
└── cli/                       # CLI-specific configuration
    ├── defaults.json          # CLI default settings
    └── output_formats.json    # Output formatting config
```

## Implementation Requirements

### 1. Configuration System Core (`src/config/`)

#### Main Configuration Manager (`config_manager.py`)
```python
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class ConfigLevel(Enum):
    SYSTEM = "system"
    PIPELINE = "pipeline"
    PROVIDER = "provider"
    ENVIRONMENT = "environment"
    CLI = "cli"

@dataclass
class ConfigSource:
    """Configuration source information"""
    path: Path
    level: ConfigLevel
    priority: int  # Higher = more important

class ConfigManager:
    """Hierarchical configuration management"""

    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        self.config_cache: Dict[str, Dict[str, Any]] = {}
        self.sources: List[ConfigSource] = []

    def load_config(self, config_type: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration with hierarchy resolution"""
        cache_key = f"{config_type}:{name or 'default'}"

        if cache_key in self.config_cache:
            return self.config_cache[cache_key]

        config = self._merge_configurations(config_type, name)
        self.config_cache[cache_key] = config
        return config

    def _merge_configurations(self, config_type: str, name: Optional[str]) -> Dict[str, Any]:
        """Merge configurations from all applicable sources"""
        merged_config = {}

        # Load in priority order (lower priority first)
        sources = self._get_config_sources(config_type, name)

        for source in sorted(sources, key=lambda s: s.priority):
            if source.path.exists():
                try:
                    source_config = json.loads(source.path.read_text())
                    merged_config = self._deep_merge(merged_config, source_config)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Failed to load {source.path}: {e}")

        # Apply environment variable overrides
        self._apply_env_overrides(merged_config)

        return merged_config

    def _get_config_sources(self, config_type: str, name: Optional[str]) -> List[ConfigSource]:
        """Get all applicable configuration sources"""
        sources = []

        # Core system config (lowest priority)
        core_path = self.base_path / 'config' / 'core.json'
        sources.append(ConfigSource(core_path, ConfigLevel.SYSTEM, 1))

        # Type-specific config
        if config_type == 'pipeline' and name:
            pipeline_path = self.base_path / 'config' / 'pipelines' / f'{name}.json'
            sources.append(ConfigSource(pipeline_path, ConfigLevel.PIPELINE, 2))
        elif config_type == 'provider' and name:
            provider_path = self.base_path / 'config' / 'providers' / f'{name}.json'
            sources.append(ConfigSource(provider_path, ConfigLevel.PROVIDER, 2))
        elif config_type == 'cli':
            cli_path = self.base_path / 'config' / 'cli' / 'defaults.json'
            sources.append(ConfigSource(cli_path, ConfigLevel.CLI, 2))

        # Environment-specific overrides (highest priority)
        env = os.getenv('FLUENT_ENV', 'development')
        env_path = self.base_path / 'config' / 'environments' / f'{env}.json'
        sources.append(ConfigSource(env_path, ConfigLevel.ENVIRONMENT, 3))

        return sources

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides"""
        # Look for FF_ prefixed environment variables
        for env_key, env_value in os.environ.items():
            if env_key.startswith('FF_'):
                config_key = env_key[3:].lower().replace('_', '.')
                self._set_nested_config(config, config_key, env_value)

    def _set_nested_config(self, config: Dict[str, Any], key_path: str, value: str) -> None:
        """Set nested configuration value from dot notation"""
        keys = key_path.split('.')
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Try to parse value as JSON, fall back to string
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value

        current[keys[-1]] = parsed_value

    def clear_cache(self) -> None:
        """Clear configuration cache"""
        self.config_cache.clear()

# Global configuration manager
_global_config_manager: Optional[ConfigManager] = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager"""
    global _global_config_manager
    if _global_config_manager is None:
        from pathlib import Path
        _global_config_manager = ConfigManager(Path(__file__).parents[2])
    return _global_config_manager
```

### 2. Configuration Schema Definitions (`src/config/schemas.py`)

```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Base provider configuration"""
    type: str
    enabled: bool = True
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}

@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    name: str
    display_name: str
    data_file: str
    anki_note_type: str
    stages: List[str]
    providers: Dict[str, str]  # stage -> provider mapping
    config: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}

@dataclass
class SystemConfig:
    """System-wide configuration"""
    project_root: str
    log_level: str = "INFO"
    cache_enabled: bool = True
    max_concurrent_requests: int = 5
    timeout_seconds: int = 300

@dataclass
class CLIConfig:
    """CLI configuration"""
    output_format: str = "table"
    show_progress: bool = True
    confirm_destructive: bool = True
    default_dry_run: bool = False
```

### 3. Default Configuration Files

#### Core System Config (`config/core.json`)
```json
{
  "system": {
    "log_level": "INFO",
    "cache_enabled": true,
    "max_concurrent_requests": 5,
    "timeout_seconds": 300
  },
  "paths": {
    "media_base": "media",
    "templates_base": "templates",
    "staging_base": "staging"
  },
  "defaults": {
    "dry_run": false,
    "backup_before_changes": true,
    "validate_before_execution": true
  }
}
```

#### Vocabulary Pipeline Config (`config/pipelines/vocabulary.json`)
```json
{
  "pipeline": {
    "name": "vocabulary",
    "display_name": "Vocabulary Cards (Fluent Forever)",
    "data_file": "vocabulary.json",
    "anki_note_type": "Fluent Forever",
    "stages": [
      "analyze_words",
      "prepare_batch",
      "ingest_batch",
      "generate_media",
      "validate_data",
      "sync_templates",
      "sync_cards"
    ]
  },
  "stage_providers": {
    "generate_media": "openai_forvo",
    "sync_templates": "anki",
    "sync_cards": "anki"
  },
  "batch_settings": {
    "cards_per_batch": 5,
    "max_meanings_per_word": 5,
    "require_prompts": true
  },
  "validation": {
    "validate_ipa": true,
    "require_all_fields": true,
    "check_media_exists": true
  }
}
```

#### OpenAI Provider Config (`config/providers/openai.json`)
```json
{
  "provider": {
    "type": "openai",
    "api_version": "v1",
    "base_url": "https://api.openai.com/v1",
    "timeout": 60,
    "max_retries": 3
  },
  "image_generation": {
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "standard",
    "style": "vivid"
  },
  "cost_limits": {
    "daily_limit_usd": 10.0,
    "warn_threshold_usd": 5.0,
    "track_usage": true
  },
  "prompts": {
    "style_prefix": "Studio Ghibli style illustration of",
    "style_suffix": "soft lighting, detailed, anime art style",
    "safety_guidelines": "family-friendly, no text, no violence"
  }
}
```

#### Anki Provider Config (`config/providers/anki.json`)
```json
{
  "provider": {
    "type": "anki",
    "connect_url": "http://localhost:8765",
    "timeout": 30,
    "max_retries": 3
  },
  "sync_settings": {
    "deck_name": "Spanish::Fluent Forever",
    "allow_duplicates": false,
    "update_existing": true,
    "backup_before_sync": true
  },
  "template_settings": {
    "update_templates": true,
    "validate_fields": true,
    "preserve_user_changes": false
  }
}
```

#### Development Environment (`config/environments/development.json`)
```json
{
  "system": {
    "log_level": "DEBUG"
  },
  "providers": {
    "openai": {
      "cost_limits": {
        "daily_limit_usd": 5.0
      }
    }
  },
  "cli": {
    "default_dry_run": true,
    "show_debug_info": true
  }
}
```

### 4. Configuration Integration

#### Provider Configuration (`src/providers/config.py`)
```python
from config.config_manager import get_config_manager
from providers.registry import get_provider_registry

def initialize_providers_from_config() -> None:
    """Initialize all providers from configuration"""
    config_manager = get_config_manager()
    provider_registry = get_provider_registry()

    # Load provider configurations
    openai_config = config_manager.load_config('provider', 'openai')
    forvo_config = config_manager.load_config('provider', 'forvo')
    anki_config = config_manager.load_config('provider', 'anki')

    # Create and register providers
    from providers.media.openai_provider import OpenAIMediaProvider
    from providers.media.forvo_provider import ForvoMediaProvider
    from providers.sync.anki_provider import AnkiSyncProvider
    from providers.data.json_provider import JSONDataProvider

    # Data provider
    core_config = config_manager.load_config('system')
    project_root = Path(core_config['system']['project_root'])
    data_provider = JSONDataProvider(project_root)
    provider_registry.register_data_provider('default', data_provider)

    # Media providers
    if openai_config.get('provider', {}).get('enabled', True):
        openai_provider = OpenAIMediaProvider(
            api_key=os.getenv('OPENAI_API_KEY'),
            config=openai_config
        )
        provider_registry.register_media_provider('openai', openai_provider)

    # Sync providers
    if anki_config.get('provider', {}).get('enabled', True):
        anki_provider = AnkiSyncProvider(config=anki_config)
        provider_registry.register_sync_provider('anki', anki_provider)
```

#### Pipeline Configuration (`src/pipelines/config.py`)
```python
def create_pipeline_from_config(pipeline_name: str) -> Pipeline:
    """Create pipeline instance from configuration"""
    config_manager = get_config_manager()
    pipeline_config = config_manager.load_config('pipeline', pipeline_name)

    if pipeline_name == 'vocabulary':
        from pipelines.vocabulary.vocabulary_pipeline import VocabularyPipeline
        return VocabularyPipeline(config=pipeline_config)
    elif pipeline_name == 'conjugation':
        from pipelines.conjugation.conjugation_pipeline import ConjugationPipeline
        return ConjugationPipeline(config=pipeline_config)
    else:
        raise ValueError(f"Unknown pipeline: {pipeline_name}")
```

### 5. Configuration CLI Commands

Add configuration management to CLI:

```python
# In cli/commands/config_command.py
class ConfigCommand:
    """Configuration management commands"""

    def execute(self, args) -> int:
        """Execute config command"""
        if args.action == 'show':
            return self._show_config(args)
        elif args.action == 'validate':
            return self._validate_config(args)
        elif args.action == 'init':
            return self._init_config(args)
        else:
            print(f"Unknown config action: {args.action}")
            return 1

    def _show_config(self, args) -> int:
        """Show current configuration"""
        config_manager = get_config_manager()

        if args.type and args.name:
            config = config_manager.load_config(args.type, args.name)
            print(json.dumps(config, indent=2))
        else:
            # Show all configurations
            pass

        return 0
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/05_configuration/` pass
- [ ] Hierarchical configuration loading works correctly
- [ ] Environment variable overrides function properly
- [ ] All component configurations load successfully

### Implementation Quality
- [ ] Configuration hierarchy resolves correctly
- [ ] Environment-specific overrides work
- [ ] Configuration validation prevents invalid settings
- [ ] All existing configuration preserved and migrated

### Integration Quality
- [ ] Providers initialize correctly from configuration
- [ ] Pipelines use configuration appropriately
- [ ] CLI respects configuration settings
- [ ] Configuration changes don't require code changes

## Deliverables

### 1. Unified Configuration System
- Hierarchical configuration manager
- All configuration schemas defined
- Default configurations for all components
- Environment-based overrides

### 2. Configuration Migration
- Migrate existing config.json settings
- Preserve all current functionality
- Add new configuration capabilities
- Clear configuration file organization

### 3. Integration Updates
- Update all components to use new configuration
- Provider initialization from config
- Pipeline configuration integration
- CLI configuration support

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/06_configuration_refactor_handoff.md` with:
- Overview of configuration system architecture
- Configuration file structure and hierarchy
- How components access configuration
- Migration mapping from old to new config
- Guidance for pipeline implementation session

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 6 E2E tests pass
3. ✅ All existing configuration functionality preserved
4. ✅ New hierarchical configuration system works
5. ✅ Environment overrides function correctly

### Quality Validation
- Configuration system is intuitive and well-documented
- All components can access their configuration easily
- Configuration changes don't require code modifications
- Error messages provide clear guidance for configuration issues

## Notes for Implementation

### Migration Strategy
- Create new configuration structure alongside existing
- Migrate settings incrementally
- Validate all functionality preserved
- Clean up old configuration files

### Design Principles
- **Hierarchy** - Clear precedence order for configuration sources
- **Flexibility** - Easy to override settings for different environments
- **Validation** - Prevent invalid configurations
- **Documentation** - Self-documenting configuration structure

---

**Remember: This configuration system will support all future pipelines and components. Focus on flexibility and clear hierarchy.**
