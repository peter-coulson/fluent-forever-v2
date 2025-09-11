# System Overview

## Purpose
Pipeline-based Spanish language learning system that processes vocabulary and conjugation materials through configurable stages, integrating with Anki for spaced repetition and external services for audio/images.

## System Architecture

### High-Level Design
The system follows a **modular pipeline architecture** where learning workflows are broken into discrete, configurable stages that process language learning materials.

### Learning Workflows
- **Vocabulary Pipeline**: Word → definition → audio → images → Anki cards
- **Conjugation Pipeline**: Verb forms → audio → practice cards → synchronization

### External Integrations
- **Anki**: Card creation and synchronization via AnkiConnect
- **Audio Services**: Forvo pronunciation provider, ElevenLabs, Azure Speech
- **Image Generation**: RunwareProvider, OpenAI image generation
- **Data Storage**: JSON-based vocabulary/conjugation storage

### CLI Interface
Universal command-line interface supporting:
- Pipeline discovery and execution (`cli list`, `cli run`, `cli info`)
- Stage-by-stage execution with dry-run preview
- Configuration validation and verbose output

### Key Architectural Principles
- **Modularity**: Components are loosely coupled with clear interfaces
- **Extensibility**: New pipelines, stages, and providers can be added declaratively
- **Configuration-Driven**: Behavior controlled via JSON configuration and environment variables
- **Error Resilience**: Graceful degradation and comprehensive error reporting

## Navigation
- **Core Concepts**: `context/system/core-concepts.md` - Component definitions and relationships
- **Data Flow**: `context/system/data-flow.md` - Execution patterns and state management
- **Module Details**: `context/modules/[core|providers|cli]/overview.md` - Implementation specifics
- **Practical Usage**: `context/workflows/` - Operations, extension, and troubleshooting
