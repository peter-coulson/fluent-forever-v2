# Fluent Forever V2 - Spanish Learning System

A modular card creation system for Spanish language learning using the Fluent Forever methodology.

## 🎯 What This System Does

Transform Spanish vocabulary and grammar into memorable Anki cards with:
- **Multiple Card Types**: Vocabulary, conjugations, and custom pipelines
- **Studio Ghibli Imagery**: Consistent, engaging visual style
- **Native Pronunciation**: Latin American audio from multiple sources
- **Modular Architecture**: Easy to extend with new card types

## 🚀 Quick Start

1. **Prerequisites**: Python 3.8+, Anki with AnkiConnect addon
2. **Setup**: See [Quick Start Guide](quick_start.md) for detailed setup
3. **Usage**: Run `python -m cli.pipeline list` to see available pipelines

## 📖 Documentation

### For Users
- [Quick Start Guide](quick_start.md) - Get up and running in minutes
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Examples](examples/) - Workflow examples and tutorials

### For Developers  
- [Architecture Overview](../development/architecture.md) - System design and components
- [Adding Pipelines](../development/adding_pipelines.md) - How to add new card types
- [API Reference](../development/api_reference.md) - Complete API documentation

### For Operations
- [Claude Guide](../operations/claude_guide.md) - Claude operational procedures
- [Configuration](../operations/configuration.md) - System configuration guide
- [CLI Reference](../reference/cli_reference.md) - Complete command reference

## 🏗️ System Architecture

This system uses a **pipeline-centric architecture** where each card type defines its own complete processing workflow:

```
Pipeline Types:    Vocabulary → Conjugation → Grammar → Custom
Processing Stages: Analysis → Generation → Validation → Sync
External Services: OpenAI → Forvo → AnkiConnect
```

## 💡 Key Features

- **Modular Pipelines**: Each card type has its own complete workflow
- **Pluggable Components**: Stages and providers can be mixed and matched
- **Universal CLI**: Consistent commands for all card types
- **Comprehensive Testing**: E2E tests ensure reliability
- **Clean Configuration**: Hierarchical configuration system

## 📊 Current Status

- ✅ **Vocabulary Pipeline**: Complete E2E workflow for vocabulary cards
- ✅ **Conjugation Pipeline**: Verb conjugation practice cards  
- ✅ **Multi-Pipeline Support**: Multiple card types coexist cleanly
- ✅ **Universal CLI**: `python -m cli.pipeline` commands for all operations

## 🔧 Common Commands

```bash
# Discover available pipelines
python -m cli.pipeline list

# Get pipeline information
python -m cli.pipeline info vocabulary

# Run pipeline stages
python -m cli.pipeline run vocabulary --stage prepare_batch --words por,para
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer

# Preview cards
python -m cli.pipeline preview vocabulary --start-server
```

## 🤝 Contributing

See [development documentation](../development/) for:
- System architecture overview
- How to add new pipelines
- Testing guidelines
- API reference

---

**Transform Spanish learning into memorable visual experiences through modular card creation!**