# User Guide - Fluent Forever V2

A modular card creation system for Spanish language learning using the Fluent Forever methodology.

## 🎯 What This System Does

Transform Spanish vocabulary and grammar into memorable Anki cards with:
- **Multiple Card Types**: Vocabulary, conjugations, and custom pipelines
- **Studio Ghibli Imagery**: Consistent, engaging visual style
- **Native Pronunciation**: Latin American audio from multiple sources
- **Modular Architecture**: Easy to extend with new card types

## 🚀 Getting Started

**→ [Quick Start Guide](quick_start.md)** - Complete setup and first steps

**→ [CLI Reference](../reference/cli_reference.md)** - All available commands

## 📚 Learning Resources

### Workflow Examples
- **[Vocabulary Workflow](examples/vocabulary_workflow.md)** - Complete vocabulary card creation
- **[Conjugation Workflow](examples/conjugation_workflow.md)** - Verb conjugation practice cards

### Troubleshooting
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

## 🏗️ Understanding the System

This system uses a **pipeline-centric architecture** where each card type defines its own complete processing workflow:

```
Pipeline Types:    Vocabulary → Conjugation → Grammar → Custom
Processing Stages: Analysis → Generation → Validation → Sync
External Services: OpenAI → Forvo → AnkiConnect
```

**→ [Architecture Overview](../development/architecture.md)** - Detailed system design

## 📊 Current Card Types

- ✅ **Vocabulary Pipeline**: Complete E2E workflow for vocabulary cards
- ✅ **Conjugation Pipeline**: Verb conjugation practice cards  
- ✅ **Multi-Pipeline Support**: Multiple card types coexist cleanly

**→ [Adding New Pipelines](../development/adding_pipelines.md)** - Extend the system

---

**Transform Spanish learning into memorable visual experiences through modular card creation!**