# CLI Reference

Complete reference for all command-line interface operations.

## Universal Pipeline Commands

### List Pipelines
```bash
python -m cli.pipeline list
```
Shows all available pipelines with descriptions.

### Pipeline Information
```bash
python -m cli.pipeline info <pipeline>
```
Shows detailed information about a specific pipeline.

### Execute Pipeline Stages
```bash
python -m cli.pipeline run <pipeline> --stage <stage> [options]
```

**Common Options:**
- `--dry-run`: Show execution plan without running
- `--execute`: Execute destructive operations (media generation, sync)
- `--verbose`: Show detailed logging output

## Vocabulary Pipeline

### Word Analysis and Batch Preparation
```bash
python -m cli.pipeline run vocabulary --stage prepare_batch --words <word1,word2,...>
```

### Batch Ingestion
```bash
python -m cli.pipeline run vocabulary --stage ingest_batch --file <staging_file>
```

**Options:**
- `--skip-ipa-validation`: Skip IPA pronunciation validation

### Media Generation
```bash
python -m cli.pipeline run vocabulary --stage generate_media [options]
```

**Options:**
- `--execute`: Actually generate media (required for API calls)
- `--no-images`: Skip image generation
- `--no-audio`: Skip audio generation

### Anki Synchronization
```bash
python -m cli.pipeline run vocabulary --stage sync_cards --execute
```

## Conjugation Pipeline

### Verb Analysis
```bash
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs <verb1,verb2,...>
```

**Options:**
- `--tenses`: Specific tenses to include
- `--persons`: Specific persons to include

### Media and Sync
```bash
python -m cli.pipeline run conjugation --stage generate_media --execute
python -m cli.pipeline run conjugation --stage sync_cards --execute
```

## Preview System

### Start Preview Server
```bash
python -m cli.pipeline preview <pipeline> --start-server [--port 8000]
```

## Environment Setup

**→ See [Quick Start Guide](../user/quick_start.md)** for complete setup instructions including critical activation script usage.

## Common Issues

**→ See [Troubleshooting Guide](../user/troubleshooting.md)** for complete error solutions and diagnostic procedures.
