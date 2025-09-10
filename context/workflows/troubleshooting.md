# Troubleshooting

Common error patterns, solutions, and diagnostic approaches for Fluent Forever V2.

## Pipeline Execution Failures

### Stage Dependencies Not Met
**Error Pattern**: `DependencyError: Required context key 'X' not found`

**Solution**:
1. Check stage ordering in pipeline configuration
2. Verify previous stages populate required context keys
3. Review stage dependency declarations

**Debug**: Enable debug logging with `LOG_LEVEL=DEBUG`

### Configuration Validation Errors
**Error Pattern**: `ConfigError: Invalid configuration for pipeline 'X'`

**Common Causes**:
- Missing required configuration keys
- Invalid file paths
- Malformed YAML syntax

**Solution**:
```bash
python -m src.cli.main validate-config config/pipeline.yml
```

**Config validation**: `src/core/config.py:25`

### Memory Issues with Large Datasets
**Symptoms**: Process killed, out of memory errors

**Solutions**:
- Implement batch processing in custom stages
- Reduce concurrent operations
- Use streaming data processing patterns
- Monitor memory usage during execution

## Provider Integration Problems

### Anki Connection Failures
**Error**: `AnkiConnectError: Could not connect to Anki`

**Diagnostics**:
1. Verify Anki is running
2. Check AnkiConnect addon installed and enabled
3. Test connection: `curl http://localhost:8765`
4. Verify `ANKI_CONNECT_URL` environment variable

**Provider**: `src/providers/sync/anki_provider.py:40`

### Audio Provider API Errors
**ElevenLabs Errors**:
- `401 Unauthorized`: Check `ELEVENLABS_API_KEY`
- `429 Rate Limited`: Implement retry logic
- `400 Bad Request`: Verify audio generation parameters

**Azure Speech Errors**:
- `401`: Verify `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`
- `403`: Check subscription and quota limits

**Debug Command**:
```bash
python -m src.cli.main test-provider audio elevenlabs
```

### Image Generation Timeouts
**Error**: `ImageGenerationTimeout: Request exceeded maximum time`

**Solutions**:
- Increase timeout configuration
- Verify API key and quota
- Check network connectivity
- Implement retry with exponential backoff

**Configuration**: Provider timeout settings in YAML configs

## CLI Usage Problems

### Command Not Found
**Error**: `Command 'X' not found`

**Solutions**:
1. Check command registration in `src/cli/main.py:20`
2. Verify command module imports
3. Check for typos in command names

### Invalid Arguments
**Error**: `InvalidArgument: Required argument 'X' missing`

**Diagnostics**:
- Use `--help` flag to see required arguments
- Check argument parsing in command implementation
- Verify click decorator configuration

**CLI structure**: See `context/modules/cli/commands.md`

### Permission Errors
**Error**: `PermissionError: Access denied to file/directory`

**Solutions**:
- Check file/directory permissions
- Verify write access to output directories
- Ensure process has required filesystem permissions

## Configuration Issues

### Environment Variable Problems
**Missing Variables**: System fails to start

**Validation**:
```bash
python -c "from src.core.config import validate_environment; validate_environment()"
```

**Common Issues**:
- `.env` file not loaded
- Variables not exported in shell
- Incorrect variable names or formats

### YAML Syntax Errors
**Error**: `yaml.YAMLError: Invalid YAML syntax`

**Solutions**:
1. Validate YAML syntax with online validator
2. Check indentation (spaces vs tabs)
3. Verify quoted strings and special characters
4. Review YAML structure against examples

### File Path Resolution
**Error**: `FileNotFoundError: Config file not found`

**Solutions**:
- Use absolute paths in configuration
- Verify current working directory
- Check file permissions and existence
- Review path resolution logic

## Performance Issues

### Slow Pipeline Execution
**Diagnostics**:
1. Enable profiling: `LOG_LEVEL=DEBUG`
2. Identify bottleneck stages
3. Monitor provider response times
4. Check data processing efficiency

**Optimization Strategies**:
- Implement caching for expensive operations
- Use concurrent processing where safe
- Optimize data structures and algorithms
- Consider provider rate limits

### Provider Rate Limiting
**Symptoms**: Intermittent failures, 429 errors

**Solutions**:
- Implement exponential backoff retry
- Reduce concurrent requests
- Add request rate limiting
- Consider provider upgrade or alternatives

**Implementation**: Add retry logic in provider base classes

## Data Processing Errors

### Malformed Input Data
**Error**: `DataValidationError: Invalid data format`

**Solutions**:
1. Validate input data schema
2. Implement data sanitization
3. Add error recovery mechanisms
4. Provide clear error messages

**Data validation**: Implement in pipeline stages

### Character Encoding Issues
**Error**: `UnicodeDecodeError: Invalid character encoding`

**Solutions**:
- Specify encoding explicitly (`utf-8`)
- Validate source file encoding
- Implement encoding detection
- Add fallback encoding handling

### Large File Processing
**Symptoms**: Long processing times, memory issues

**Solutions**:
- Implement streaming file processing
- Use chunked data processing
- Add progress indicators
- Consider file format optimization

## System Integration Issues

### Database Connection Problems
**If using databases**: Connection timeouts, authentication errors

**Solutions**:
- Verify connection parameters
- Check network connectivity
- Test credentials separately
- Review connection pooling settings

### External Service Dependencies
**Symptoms**: Cascading failures, service unavailable errors

**Solutions**:
- Implement circuit breaker patterns
- Add service health checks
- Provide graceful degradation
- Cache external service responses

## Debugging Strategies

### Enable Comprehensive Logging
```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=detailed
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

### Provider Testing
Test each provider individually:
```bash
python -m src.cli.main test-provider <type> <name>
```

## Prevention Strategies

### Configuration Validation
- Validate all configuration files on startup
- Implement schema validation for YAML configs
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

For system architecture details, see:
- `context/system/overview.md`
- `context/modules/core/overview.md`
- `context/modules/providers/overview.md`
