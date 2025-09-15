# Troubleshooting

Common error patterns and solutions for Fluent Forever V2.

## Pipeline Execution Failures

### Stage Dependencies Not Met
**Error**: `DependencyError: Required context key 'X' not found`

**Solution**:
1. Check stage ordering in pipeline configuration
2. Verify previous stages populate required context keys
3. Review stage dependency declarations

**Debug**: Enable debug logging with `--verbose` flag or `FLUENT_FOREVER_DEBUG=true`

### Configuration Validation Errors
**Error**: `ConfigError: Invalid configuration for pipeline 'X'`

**Common Causes**: Missing configuration keys, invalid file paths, malformed JSON syntax

**Solution**:
```bash
python -m src.cli.main validate-config config/pipeline.json
```

### Memory Issues with Large Datasets
**Symptoms**: Process killed, out of memory errors

**Solutions**: Implement batch processing, reduce concurrent operations, use streaming patterns

## Provider Integration Problems

### Anki Connection Failures
**Error**: `AnkiConnectError: Could not connect to Anki`

**Diagnostics**:
1. Verify Anki is running
2. Check AnkiConnect addon installed and enabled
3. Test connection: `curl http://localhost:8765`
4. Verify `ANKI_CONNECT_URL` environment variable


### Image Generation Timeouts
**Error**: `ImageGenerationTimeout: Request exceeded maximum time`

**Solutions**: Increase timeout configuration, verify API key and quota, implement retry with exponential backoff

## CLI Usage Problems

### Command Not Found
**Error**: `Command 'X' not found`

**Solutions**: Check command registration, verify module imports, check for typos

### Invalid Arguments
**Error**: `InvalidArgument: Required argument 'X' missing`

**Diagnostics**: Use `--help` flag, check argument parsing in command implementation

### Permission Errors
**Error**: `PermissionError: Access denied to file/directory`

**Solutions**: Check file/directory permissions, verify write access to output directories

## Configuration Issues

### Environment Variable Problems
**Missing Variables**: System fails to start

**Common Issues**: `.env` file not loaded, variables not exported, incorrect variable names

### JSON Syntax Errors
**Error**: `json.JSONError: Invalid JSON syntax`

**Solutions**: Validate JSON syntax, check quotes and commas, review structure against examples

### File Path Resolution
**Error**: `FileNotFoundError: Config file not found`

**Solutions**: Use absolute paths, verify current working directory, check file permissions

## Performance Issues

### Slow Pipeline Execution
**Diagnostics**: Enable performance timing with `--verbose` flag, identify bottleneck stages via execution logs

**Optimization**: Implement caching, use concurrent processing, optimize algorithms, review stage timing logs

### Provider Rate Limiting
**Symptoms**: Intermittent failures, 429 errors

**Solutions**: Implement exponential backoff retry, reduce concurrent requests

## Data Processing Errors

### Malformed Input Data
**Error**: `DataValidationError: Invalid data format`

**Solutions**: Validate input data schema, implement data sanitization, add error recovery

### Character Encoding Issues
**Error**: `UnicodeDecodeError: Invalid character encoding`

**Solutions**: Specify encoding explicitly (`utf-8`), validate source file encoding

### Large File Processing
**Symptoms**: Long processing times, memory issues

**Solutions**: Implement streaming file processing, use chunked data processing

## Debugging Strategies

### Enable Comprehensive Logging
```bash
# Enable verbose mode with file logging
cli run vocabulary --verbose

# Or via environment variable
export FLUENT_FOREVER_DEBUG=true

# Module-specific logging levels
export FLUENT_FOREVER_STAGES_LOG_LEVEL=DEBUG
export FLUENT_FOREVER_PROVIDERS_LOG_LEVEL=INFO
export FLUENT_FOREVER_CLI_LOG_LEVEL=DEBUG

# Enable log file output
export FLUENT_FOREVER_LOG_TO_FILE=true
```

### Isolate Problem Components
1. Test individual stages separately
2. Use minimal test datasets
3. Mock external dependencies
4. Run with simplified configurations

### Performance Profiling
```bash
python -m cProfile -o profile.stats -m src.cli.main <command>
```

## Prevention Strategies

### Configuration Validation
- Validate all configuration files on startup
- Implement schema validation for JSON configs
- Test configuration changes in isolated environment

### Error Handling Patterns
- Implement comprehensive exception handling
- Provide actionable error messages
- Add context information to error reports
- Log error details for debugging

### Testing Coverage
- Unit tests for all components
- Integration tests for provider connections
- End-to-end pipeline testing
- Performance regression testing
