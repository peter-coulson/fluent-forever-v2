<!-- 
ARCHIVED DOCUMENT
Original: CLI_COMMAND_MAPPING.md
Archived Location: context/archive/legacy/old_CLI_COMMAND_MAPPING.md
Archive Date: 2025-09-06T19:46:52.108279

This document has been archived as part of the documentation reorganization.
For current documentation, see context/README.md
-->

# CLI Command Mapping: Old to New System

This document maps all existing CLI scripts to the new universal pipeline runner commands.

## Overview

The new universal CLI system provides consistent command patterns through:
```bash
python -m cli.pipeline <command> [options]
```

## Command Mappings

### Discovery Commands

#### List Available Pipelines
```bash
# NEW
python -m cli.pipeline list
python -m cli.pipeline list --detailed
```

#### Pipeline Information
```bash
# NEW
python -m cli.pipeline info vocabulary
python -m cli.pipeline info vocabulary --stages
```

### Vocabulary Pipeline Commands

#### Prepare Claude Batch
```bash
# OLD
python -m cli.prepare_claude_batch --words por,para,con
python -m cli.prepare_claude_batch --words word1,word2 --output custom_path.json

# NEW
python -m cli.pipeline run vocabulary --stage prepare_batch --words por,para,con
python -m cli.pipeline run vocabulary --stage prepare_batch --words word1,word2 --file custom_path.json
```

#### Ingest Claude Batch
```bash
# OLD
python -m cli.ingest_claude_batch --input staging/claude_batch_*.json
python -m cli.ingest_claude_batch --input staging/batch.json --dry-run
python -m cli.ingest_claude_batch --input staging/batch.json --skip-ipa-validation

# NEW
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/claude_batch_*.json
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/batch.json --dry-run
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/batch.json --skip-validation
```

#### Media Generation
```bash
# OLD
python -m cli.media_generate --cards CardID1,CardID2,CardID3
python -m cli.media_generate --cards CardID1 --execute
python -m cli.media_generate --cards CardID1,CardID2 --no-images
python -m cli.media_generate --cards CardID1,CardID2 --no-audio
python -m cli.media_generate --cards CardID1 --max 10
python -m cli.media_generate --cards CardID1 --force-regenerate

# NEW
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1,CardID2,CardID3 --dry-run
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1 --execute
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1,CardID2 --no-images
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1,CardID2 --no-audio
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1 --max 10
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1 --force-regenerate
```

#### Anki Sync
```bash
# OLD
python -m cli.sync_anki_all
python -m cli.sync_anki_all --force-media
python -m cli.sync_anki_all --delete-extras

# NEW
python -m cli.pipeline run vocabulary --stage sync_anki --execute
python -m cli.pipeline run vocabulary --stage sync_anki --execute --force-media
python -m cli.pipeline run vocabulary --stage sync_anki --execute --delete-extras
```

#### Combined Operations
```bash
# OLD
python -m cli.run_media_then_sync --cards CardID1,CardID2 --execute
python -m cli.run_media_then_sync --cards CardID1 --no-images --execute
python -m cli.run_media_then_sync --cards CardID1 --delete-extras

# NEW
python -m cli.pipeline run vocabulary --stage media_and_sync --cards CardID1,CardID2 --execute
python -m cli.pipeline run vocabulary --stage media_and_sync --cards CardID1 --no-images --execute
python -m cli.pipeline run vocabulary --stage media_and_sync --cards CardID1 --delete-extras
```

#### Image Regeneration
```bash
# OLD
python -m cli.regenerate_images --cards CardID1,CardID2 --execute

# NEW
python -m cli.pipeline run vocabulary --stage generate_media --cards CardID1,CardID2 --execute --force-regenerate --no-audio
```

### Word Queue Management

#### Generate Word Queue
```bash
# OLD
python -m cli.generate_word_queue --count 50
python -m cli.generate_word_queue --count 100 --dry-run
python -m cli.generate_word_queue --count 25 --output my_queue.json

# NEW
python -m cli.pipeline run vocabulary --stage generate_queue --max 50
python -m cli.pipeline run vocabulary --stage generate_queue --max 100 --dry-run
python -m cli.pipeline run vocabulary --stage generate_queue --max 25 --file my_queue.json
```

#### Sync Word Queue
```bash
# OLD
python -m cli.sync_word_queue

# NEW
python -m cli.pipeline run vocabulary --stage sync_queue --execute
```

### Preview and Development

#### Preview Server
```bash
# OLD
python -m cli.preview_server --port 8000
python -m cli.preview_server_multi --port 8001

# NEW
python -m cli.pipeline preview vocabulary --start-server --port 8000
python -m cli.pipeline preview vocabulary --start-server --port 8001
```

#### Preview Specific Cards
```bash
# NEW
python -m cli.pipeline preview vocabulary --card-id lo_neuter_article
python -m cli.pipeline preview vocabulary --card-id some_card_id --port 8001
```

### Multi-Pipeline Sync

#### Multi-Pipeline Anki Sync
```bash
# OLD
python -m cli.sync_anki_multi

# NEW
python -m cli.pipeline run vocabulary --stage sync_anki --execute
python -m cli.pipeline run conjugation --stage sync_anki --execute
```

## Command Flags Reference

### Global Flags
- `--config CONFIG`: Specify configuration file path
- `--verbose, -v`: Enable verbose output
- `--dry-run`: Show what would be done without executing (available for run command)

### Run Command Flags
- `--stage STAGE`: Required - stage to execute
- `--words WORDS`: Comma-separated word list
- `--cards CARDS`: Comma-separated card IDs
- `--file FILE`: Input/output file path
- `--execute`: Execute changes (vs dry-run)
- `--no-images`: Skip image generation
- `--no-audio`: Skip audio generation
- `--force-regenerate`: Force regeneration of existing media
- `--max NUMBER`: Maximum items to process
- `--delete-extras`: Delete extra items during sync

### Preview Command Flags
- `--card-id ID`: Specific card ID to preview
- `--port PORT`: Preview server port (default 8000)
- `--start-server`: Start preview server

### Info Command Flags
- `--stages`: Show detailed stage information

### List Command Flags
- `--detailed`: Show detailed pipeline information

## Examples

### Basic Workflow
```bash
# 1. List available pipelines
python -m cli.pipeline list

# 2. Get pipeline information
python -m cli.pipeline info vocabulary

# 3. Prepare batch
python -m cli.pipeline run vocabulary --stage prepare_batch --words hola,mundo --dry-run

# 4. Generate media
python -m cli.pipeline run vocabulary --stage generate_media --cards card1,card2 --execute

# 5. Sync to Anki
python -m cli.pipeline run vocabulary --stage sync_anki --execute
```

### Advanced Operations
```bash
# Complex media generation with options
python -m cli.pipeline run vocabulary \
    --stage generate_media \
    --cards card1,card2,card3 \
    --no-audio \
    --max 5 \
    --execute

# Preview specific card
python -m cli.pipeline preview vocabulary --card-id my_card_id --port 8001

# Full pipeline with validation
python -m cli.pipeline run vocabulary --stage prepare_batch --words test1,test2 --dry-run
python -m cli.pipeline run vocabulary --stage prepare_batch --words test1,test2
python -m cli.pipeline run vocabulary --stage generate_media --cards new_cards --execute
python -m cli.pipeline run vocabulary --stage sync_anki --execute
```

## Migration Notes

### Key Changes
1. **Consistent Interface**: All commands now use the same `pipeline run` structure
2. **Discovery**: New `list` and `info` commands for pipeline discovery
3. **Dry-Run Support**: Universal `--dry-run` flag for all operations
4. **Enhanced Preview**: Integrated preview system with server management
5. **Multi-Pipeline Ready**: Framework supports multiple pipeline types

### Benefits
- **Consistency**: Same command patterns for all operations
- **Discoverability**: Easy to find available pipelines and stages
- **Flexibility**: Rich flag support for customizing operations
- **Extensibility**: Easy to add new pipelines and stages
- **Testing**: Built-in dry-run support for safe testing

### Backward Compatibility
The old CLI commands are still available during the transition period, but the new system provides:
- Better error messages
- Consistent argument validation
- Enhanced help system
- Improved output formatting

## Stage Reference

### Vocabulary Pipeline Stages
- `prepare_batch`: Prepare words for Claude processing
- `ingest_batch`: Ingest completed Claude batch
- `generate_media`: Generate images and audio
- `sync_anki`: Sync cards to Anki
- `media_and_sync`: Combined media generation and sync
- `generate_queue`: Generate word processing queue
- `sync_queue`: Sync word queue status

### Universal Stages (all pipelines)
- `validate`: Validate pipeline data
- `preview`: Preview pipeline output
- `status`: Show pipeline status

## Help System

### Getting Help
```bash
# General help
python -m cli.pipeline --help

# Command-specific help
python -m cli.pipeline run --help
python -m cli.pipeline preview --help

# Pipeline-specific information
python -m cli.pipeline info vocabulary
python -m cli.pipeline info vocabulary --stages
```

### Built-in Documentation
The CLI system includes comprehensive help text and examples for all commands. Use `--help` with any command to see detailed usage information.