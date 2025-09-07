# System Architecture

Fluent Forever V2 uses a **pipeline-centric architecture** that enables seamless addition of new card types without modifying core infrastructure.

## Core Concepts

### Pipelines
Each card type is implemented as a **Pipeline** that defines:
- **Stages**: Processing steps (analysis, generation, validation, sync)
- **Data Sources**: Where card data comes from
- **Configuration**: Pipeline-specific settings
- **Anki Integration**: Note type and template mapping

### Stages
**Stages** are reusable processing components that:
- **Execute** specific operations (media generation, validation, etc.)
- **Chain Together** to create complete workflows
- **Share Context** through the pipeline execution context
- **Handle Errors** gracefully with detailed reporting

### Providers
**Providers** abstract external dependencies:
- **Data Providers**: File system, databases, APIs
- **Media Providers**: Image generation (OpenAI), audio (Forvo)
- **Sync Providers**: Anki, other spaced repetition systems

## Architecture Layers

```
┌─────────────────────┐
│       CLI Layer     │ ← Universal commands for all pipelines
├─────────────────────┤
│    Pipeline Layer   │ ← Card-type specific workflows
├─────────────────────┤
│     Stage Layer     │ ← Reusable processing components
├─────────────────────┤
│   Provider Layer    │ ← External service abstractions
├─────────────────────┤
│      Core Layer     │ ← Foundational abstractions
└─────────────────────┘
```

### Core Layer
- **Pipeline Interface**: Abstract base class for all card types
- **Stage Interface**: Common processing step abstraction
- **Context System**: Data flow between stages
- **Registry System**: Pipeline and provider discovery

### Provider Layer  
- **Data Providers**: JSON files, databases, memory (testing)
- **Media Providers**: OpenAI (images), Forvo (audio), mock (testing)
- **Sync Providers**: AnkiConnect, file export, mock (testing)

### Stage Layer
- **Generic Stages**: Media generation, validation, sync operations
- **Pipeline-Specific Stages**: Word analysis, conjugation analysis
- **Composition**: Stages can be chained and reused across pipelines

### Pipeline Layer
- **Vocabulary Pipeline**: Fluent Forever vocabulary cards
- **Conjugation Pipeline**: Verb conjugation practice
- **Template Pipeline**: Starting point for new card types

### CLI Layer
- **Universal Commands**: Same interface for all pipelines
- **Discovery**: List pipelines, stages, and capabilities
- **Execution**: Run individual stages or complete workflows

## Data Flow

```
Input (Words/Verbs) 
    ↓
[Analysis Stage] → Context Data
    ↓
[Generation Stage] → Context + Generated Content
    ↓
[Validation Stage] → Context + Validation Results  
    ↓
[Sync Stage] → Cards in Anki
```

## Extension Points

### Adding New Pipelines
1. **Implement Pipeline Interface** 
2. **Define Stages** (reuse existing + create custom)
3. **Configure Providers** 
4. **Register Pipeline**
5. **Add Configuration**

### Adding New Stages
1. **Implement Stage Interface**
2. **Define Context Requirements** 
3. **Add to Stage Registry**
4. **Create Unit Tests**

### Adding New Providers
1. **Implement Provider Interface**
2. **Add Configuration Schema**
3. **Register with Provider Registry** 
4. **Create Mock for Testing**

## Key Design Principles

### Modularity
- **Single Responsibility**: Each component has one clear purpose
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together

### Extensibility  
- **Open/Closed Principle**: Easy to extend, hard to break
- **Plugin Architecture**: New functionality added without core changes
- **Interface Segregation**: Clean, focused interfaces

### Testability
- **Dependency Injection**: All external dependencies are injectable
- **Mock Support**: Comprehensive mocking for all external services
- **Isolation**: Components can be tested independently

### Maintainability
- **Clear Interfaces**: Well-defined contracts between components
- **Consistent Patterns**: Same patterns used throughout system
- **Error Handling**: Comprehensive error handling and logging

## Technology Stack

- **Python 3.8+**: Core language
- **Flask**: Preview server framework
- **Requests**: HTTP client for external APIs  
- **JSON**: Configuration and data storage
- **pytest**: Testing framework
- **AnkiConnect**: Anki integration protocol

---

This architecture enables rapid development of new card types while maintaining system stability and user experience consistency.