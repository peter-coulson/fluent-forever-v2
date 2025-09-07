# Vocabulary Workflow Example

Complete walkthrough for creating Spanish vocabulary cards using the Fluent Forever methodology.

## Overview

This example demonstrates creating vocabulary cards for the Spanish words "haber," "por," and "con" - three high-frequency words with multiple meanings.

## Prerequisites

- System installed and configured (see [Quick Start](../quick_start.md))
- Anki running with AnkiConnect addon
- API keys configured (OpenAI and Forvo recommended)

## Step 1: Environment Setup

**→ See [Quick Start Guide](../quick_start.md) for complete setup instructions**

Verify system is ready:
```bash
python -m cli.pipeline list
python -m cli.pipeline info vocabulary
```

## Step 2: Word Analysis and Batch Preparation

Analyze target words and create Claude batch:
```bash
python -m cli.pipeline run vocabulary --stage prepare_batch --words haber,por,con
```

**Output**:
```
✅ Generated batch staging file: staging/claude_batch_20241201_143022.json
📊 Batch composition:
  - haber: 3 meanings
  - por: 4 meanings  
  - con: 2 meanings
📋 Total: 9 cards (exceeds limit of 5)
⚠️  Recommendation: Split into two batches for optimal processing
```

## Step 3: Claude Integration (Automated)

If using Claude Code, the staging file will be automatically filled. Otherwise, manually complete the staging file with:

### Required Fields Per Meaning:
- **SpanishWord**: The target word
- **MeaningID**: Unique identifier for this meaning
- **MeaningContext**: Brief context description
- **MonolingualDef**: Spanish definition
- **ExampleSentence**: Spanish sentence using the word
- **GappedSentence**: Same sentence with word replaced by "_____"
- **IPA**: Pronunciation with syllable markers
- **prompt**: Studio Ghibli-style image prompt

### Example Completed Entry:
```json
{
  "SpanishWord": "haber",
  "MeaningID": "auxiliary_verb",
  "MeaningContext": "Auxiliary verb for compound tenses",
  "MonolingualDef": "Verbo auxiliar que se usa para formar los tiempos compuestos",
  "ExampleSentence": "He comido tacos esta mañana",
  "GappedSentence": "_____ comido tacos esta mañana",
  "IPA": "[e]",
  "prompt": "Teenage boy with brown hair sitting at breakfast table with empty plate and satisfied expression after finishing tacos, warm morning sunlight through kitchen window"
}
```

## Step 4: Batch Ingestion

Validate and ingest the completed batch:
```bash
# Dry run first to validate
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/claude_batch_20241201_143022.json --dry-run

# If validation passes, ingest
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/claude_batch_20241201_143022.json
```

## Step 5: Media Generation

Generate images and audio for the new cards:
```bash
# Preview what will be generated
python -m cli.pipeline run vocabulary --stage generate_media --cards haber_auxiliary_verb,por_through_via

# Execute generation
python -m cli.pipeline run vocabulary --stage generate_media --execute
```

## Step 6: Anki Synchronization

Sync templates and cards to Anki:
```bash
# Sync templates first (if changed)
python -m cli.pipeline run vocabulary --stage sync_templates --execute

# Sync cards
python -m cli.pipeline run vocabulary --stage sync_cards --execute
```

## Complete Workflow Summary

```bash
# 1. Environment setup - see Quick Start Guide

# 2. Batch preparation
python -m cli.pipeline run vocabulary --stage prepare_batch --words haber,por,con

# 3. Complete staging file (manual or Claude)
# Edit staging/claude_batch_*.json

# 4. Ingest batch
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/claude_batch_*.json

# 5. Generate media
python -m cli.pipeline run vocabulary --stage generate_media --execute

# 6. Sync to Anki
python -m cli.pipeline run vocabulary --stage sync_cards --execute
```

## Result: Learning-Ready Cards

Your vocabulary cards now feature:
- **Visual Memory Anchors**: Studio Ghibli-style images matching each meaning
- **Native Pronunciation**: High-quality audio from Latin American speakers
- **Contextual Sentences**: Examples showing words in natural usage
- **Systematic Organization**: Clean separation of meanings for memory formation

These cards are ready for spaced repetition learning in Anki!