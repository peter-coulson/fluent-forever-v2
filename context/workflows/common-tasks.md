# Common Tasks

Practical workflows for operating the Fluent Forever V2 Spanish learning system.

## Pipeline Operations

### Running Vocabulary Pipeline
```bash
python -m src.cli.main vocabulary --source <path> --target-file <output>
```

**Configuration**: Modify `config/vocabulario.yml` for content sources and Anki settings.

**Key files**:
- `src/core/pipelines/vocabulary_pipeline.py:15` - Main pipeline implementation
- `config/vocabulario.yml` - Pipeline configuration

### Running Conjugation Pipeline
```bash
python -m src.cli.main conjugation --verbs <path> --output <dir>
```

**Pre-requisites**: Conjugation data files in expected format.

For technical details, see: `context/modules/core/pipeline.md`

## Provider Configuration

### Named Provider Format (Required)
All providers must use the new named configuration format:
```json
{
  "providers": {
    "data": {
      "default": {"type": "json", "base_path": ".", "pipelines": ["*"]}
    },
    "audio": {
      "forvo": {"type": "forvo", "pipelines": ["vocabulary"]}
    },
    "sync": {
      "anki": {"type": "anki", "pipelines": ["*"]}
    }
  }
}
```

### Pipeline Assignment Control
- **Required Field**: Each provider must specify `pipelines` array
- **Wildcard Support**: Use `["*"]` for all pipelines
- **Access Control**: Providers only available to assigned pipelines

### Legacy Configuration Migration
Old configuration format no longer supported. Update existing configs using the named provider structure above.

**Provider registry**: `src/providers/registry.py:25`

For provider details, see: `context/modules/providers/implementations.md`

## Content Management

### Adding New Vocabulary
1. Create CSV/JSON file with required fields: `word`, `translation`, `context`
2. Place in configured data directory
3. Update pipeline configuration to reference new source
4. Run vocabulary pipeline

### Adding Conjugation Data
1. Format verb data as expected by conjugation stages
2. Place files in configured conjugation directory
3. Update pipeline configuration
4. Execute conjugation pipeline

**Data formats**: See existing files in `data/` directory for structure

## Testing & Validation

### Running Tests
```bash
# Full test suite
python -m pytest tests/

# Integration tests only
python -m pytest tests/integration/

# Specific pipeline tests
python -m pytest tests/test_vocabulary_pipeline.py
```

### Validating Configuration
```bash
python -m src.cli.main validate-config <config-file>
```

### Provider Health Checks
```bash
python -m src.cli.main check-providers
```

## Development Setup

### Environment Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env` file
3. Initialize provider credentials
4. Run validation tests

### Adding Learning Content
1. Identify content type (vocabulary/conjugation/custom)
2. Format data according to pipeline requirements
3. Configure pipeline YAML
4. Test with small dataset
5. Execute full pipeline

**Configuration patterns**: See `context/modules/core/config.md` for details

## Debugging Pipeline Execution

### Enable Debug Logging
Set `LOG_LEVEL=DEBUG` environment variable

### Stage-by-Stage Execution
Use `--debug` flag with CLI commands for detailed stage execution info

### Provider Testing
Test individual providers using debug commands:
```bash
python -m src.cli.main test-provider <provider-type> <provider-name>
```

For troubleshooting patterns, see: `context/workflows/troubleshooting.md`
