# Extending the System

Overview of extension patterns for adding new functionality to Fluent Forever V2.

## Extension Categories

The system supports three main extension types:

### Pipeline Extensions
**Adding new learning workflow types**
- Vocabulary, conjugation, grammar, phrase pipelines
- Custom stage sequences and data processing
- Integration with external language learning services

**Guide**: `context/workflows/extending-pipelines.md`

### Provider Extensions
**Adding new external service integrations**
- Audio providers (TTS services, pronunciation APIs)
- Image providers (AI image generation, stock photos)
- Sync providers (flashcard systems, learning platforms)
- Data providers (databases, APIs, file formats)

**Guide**: `context/workflows/extending-providers.md`

### CLI Extensions
**Adding new command-line functionality**
- Custom commands for specialized workflows
- Enhanced discovery and debugging tools
- Integration with external development tools

**Guide**: `context/workflows/extending-cli.md`

## Common Extension Patterns

### System Integration
All extensions follow consistent patterns:
- **Registry-based discovery**: Components register themselves for automatic discovery
- **Configuration-driven**: Behavior controlled via JSON configuration files
- **Provider injection**: External services abstracted through provider interfaces
- **Error resilience**: Graceful degradation and comprehensive error reporting

### Development Workflow
1. **Identify extension type**: Pipeline, provider, or CLI functionality
2. **Follow domain-specific guide**: Use appropriate extending-*.md guide
3. **Implement required interfaces**: Inherit from abstract base classes
4. **Register component**: Add to appropriate registry system
5. **Add configuration**: Create JSON configuration templates
6. **Test integration**: Unit and integration tests with mocks

### Best Practices
- **Single responsibility**: Each component has one clear purpose
- **Loose coupling**: Components interact through well-defined interfaces
- **Comprehensive testing**: Unit tests, integration tests, and mocks
- **Clear documentation**: Code comments and usage examples

## System Architecture

### Core Integration Points
Components integrate with the system through:
- **Registries**: Central discovery and management (`src/core/registry.py`, `src/providers/registry.py`)
- **Configuration**: JSON-based settings with environment variable substitution (`src/core/config.py`)
- **Context**: Shared execution state between pipeline stages (`src/core/context.py`)
- **CLI**: Universal command interface with consistent patterns (`src/cli/`)

### Extension Boundaries
Clear separation between:
- **System core**: Base classes, registries, configuration (immutable)
- **Implementations**: Specific pipelines, providers, commands (extensible)
- **Configuration**: Runtime behavior and external service settings (configurable)

See component definitions in `context/system/core-concepts.md` for detailed architectural information.
