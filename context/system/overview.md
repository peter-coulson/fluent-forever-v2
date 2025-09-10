# System Overview

## Purpose
Pipeline-based Spanish language learning system that processes vocabulary and conjugation materials through configurable stages, integrating with Anki for spaced repetition and external services for audio/images.

## Architecture

### Core Components
- **Pipelines**: Orchestrate learning workflows (`src/core/pipeline.py:11`)
- **Stages**: Individual processing steps within pipelines (`src/core/stages.py:81`)
- **Context**: Runtime state container passed between stages (`src/core/context.py:8`)
- **Providers**: External service abstractions (Anki, Forvo, image generation) (`src/providers/registry.py:18`)
- **Config**: Environment-aware configuration system (`src/core/config.py:13`)

### Learning Workflows
- **Vocabulary**: Word → definition → audio → images → Anki cards
- **Conjugation**: Verb forms → audio → practice cards → synchronization

### External Integrations
- **Anki**: Card creation and synchronization via AnkiConnect
- **Audio**: Forvo pronunciation provider
- **Images**: RunwareProvider, OpenAI image generation
- **Data**: JSON-based vocabulary/conjugation storage

### CLI Interface
- Command-line entry point at `src/cli/`
- Pipeline selection and stage execution
- Configuration validation and dry-run support
