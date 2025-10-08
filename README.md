# Fluent Forever V2

Pipeline-based Spanish learning system for automated Anki flashcard generation with media.

## Status

⚠️ **Work in Progress**: The vocabulary pipeline is currently under development. See `context/implementation_plans/vocabulary_pipeline_planning/` for detailed architecture and progress.

## Overview

Automated vocabulary flashcard creation system that processes Spanish dictionary data through a multi-stage pipeline:

1. **Word Selection**: Rank-based or direct word input
2. **Word Processing**: Dictionary lookup, sense grouping, and queue population
3. **Media Generation**: User-prompted image generation and audio synthesis
4. **Vocabulary Sync**: Review/approval workflow (planned)
5. **Anki Sync**: Card creation and updates (planned)

## Key Features

- **Sense Grouping Algorithm**: Intelligently reduces dictionary senses to essential meanings
- **Manual Image Prompting**: Deliberate user involvement for improved memorability
- **IPA Pronunciation**: Automatic phonetic transcription from dictionary data
- **Multi-stage Pipeline**: Modular processing with checkpoint files

## Setup

### Prerequisites

- Python 3.11+
- Spanish dictionary data (`Español.jsonl` - not included)

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

1. Copy template: `cp vocabulary.json.template vocabulary.json`
2. Create media directories: `mkdir -p media/audio media/images`
3. Configure `.env` with API keys (if using media providers)

## Usage

```bash
source activate_env.sh
python -m src.cli.main run vocabulary
```

## Data Files

The system uses several JSON files for state management:

- `vocabulary.json` - Completed flashcards (not tracked)
- `word_queue.json` - Cards pending media generation
- `prompts_staging.json` - User-provided image prompts
- `Español.jsonl` - Source Spanish dictionary (not tracked)

## Project Structure

```
src/
├── core/          # Pipeline engine
├── providers/     # Dictionary, media, and AI providers
├── pipelines/     # Pipeline implementations
└── cli/           # Command-line interface
```

## Documentation

- Architecture: `context/system/overview.md`
- Testing: `context/testing/overview.md`
- Pipeline Design: `context/implementation_plans/vocabulary_pipeline_planning/`

## Data Privacy

⚠️ This repository excludes personal data:
- `vocabulary.json` - Your learning progress
- `media/` - Generated audio/images
- `Español.jsonl` - Dictionary source file

## Development

```bash
source activate_env.sh
pytest tests/
ruff check src/
```

## Acknowledgments

Based on the Fluent Forever methodology by Gabriel Wyner.
