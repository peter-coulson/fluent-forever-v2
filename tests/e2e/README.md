# E2E Test Suite for Fluent Forever V2 Refactor

This test suite provides comprehensive end-to-end validation gates for the Fluent Forever V2 refactor project. Each test directory corresponds to a refactor session and defines immutable contracts that implementations must satisfy.

## Purpose

These E2E tests serve as:

- **Validation Gates**: Each session must pass its corresponding E2E tests to be considered complete
- **Contract Definition**: Tests define "what" the system should do, not "how" it should work
- **Regression Prevention**: Ensure that changes don't break existing functionality
- **Interface Specification**: Define stable public APIs for the refactored system

## Test Structure

```
tests/e2e/
├── conftest.py                    # Shared fixtures and mock infrastructure
├── pytest.ini                    # Test configuration
├── README.md                      # This documentation
├── 01_core_architecture/          # Session 2 validation gates
│   ├── test_pipeline_registry.py  # Pipeline registration and discovery
│   ├── test_pipeline_execution.py # Basic pipeline execution patterns
│   └── test_pipeline_interface.py # Pipeline interface compliance
├── 02_stage_system/               # Session 3 validation gates
│   ├── test_stage_execution.py    # Individual stage execution
│   ├── test_stage_chaining.py     # Stage sequencing and data flow
│   └── test_stage_error_handling.py # Error handling and recovery
├── 03_provider_system/            # Session 4 validation gates
│   ├── test_data_providers.py     # Data source abstraction
│   ├── test_media_providers.py    # Image/audio generation abstraction
│   └── test_sync_providers.py     # Anki sync abstraction
├── 04_cli_system/                 # Session 5 validation gates
│   ├── test_pipeline_runner.py    # Universal CLI pipeline execution
│   ├── test_command_discovery.py  # Pipeline and stage discovery
│   └── test_backward_compatibility.py # Old functionality via new CLI
├── 05_configuration/              # Session 6 validation gates
│   ├── test_config_loading.py     # Unified configuration loading
│   ├── test_pipeline_configs.py   # Pipeline-specific configuration
│   └── test_provider_configs.py   # Provider configuration
├── 06_vocabulary_pipeline/        # Session 7 validation gates
│   ├── test_full_vocabulary_workflow.py # Complete E2E vocabulary workflow
│   ├── test_claude_batch_integration.py # Claude staging workflow
│   ├── test_media_generation_integration.py # Media creation workflow
│   └── test_anki_sync_integration.py # Anki synchronization workflow
├── 07_multi_pipeline/             # Session 8 validation gates
│   ├── test_multiple_pipelines.py # Vocabulary + conjugation coexistence
│   ├── test_pipeline_isolation.py # Pipelines don't interfere
│   └── test_shared_resources.py   # Shared providers work across pipelines
└── 08_documentation/              # Session 9 validation gates
    ├── test_documentation_structure.py # Context system organization
    └── test_markdown_validation.py     # All markdown files valid
```

## Test Categories and Markers

Tests are categorized using pytest markers:

### Session Markers
- `@pytest.mark.session2` - Core Architecture tests
- `@pytest.mark.session3` - Stage System tests
- `@pytest.mark.session4` - Provider System tests
- `@pytest.mark.session5` - CLI System tests
- `@pytest.mark.session6` - Configuration tests
- `@pytest.mark.session7` - Vocabulary Pipeline tests
- `@pytest.mark.session8` - Multi-Pipeline tests
- `@pytest.mark.session9` - Documentation tests

### Component Markers
- `@pytest.mark.core` - Core system functionality
- `@pytest.mark.pipeline` - Pipeline-related tests
- `@pytest.mark.stage` - Stage-related tests
- `@pytest.mark.provider` - Provider-related tests
- `@pytest.mark.cli` - CLI-related tests

### Test Type Markers
- `@pytest.mark.fast` - Quick tests (< 1 second)
- `@pytest.mark.slow` - Longer tests (> 5 seconds)
- `@pytest.mark.mock` - Tests using only mocks
- `@pytest.mark.integration` - Tests requiring multiple components

## Running Tests

### Run All E2E Tests
```bash
pytest tests/e2e/
```

### Run Tests for Specific Session
```bash
pytest tests/e2e/ -m session2  # Core Architecture
pytest tests/e2e/ -m session7  # Vocabulary Pipeline
```

### Run Tests by Component
```bash
pytest tests/e2e/ -m pipeline
pytest tests/e2e/ -m provider
pytest tests/e2e/ -m cli
```

### Run Only Fast Tests
```bash
pytest tests/e2e/ -m fast
```

### Run Tests with Coverage
```bash
pytest tests/e2e/ --cov=src --cov-report=html
```

### Run Tests in Parallel (if pytest-xdist installed)
```bash
pytest tests/e2e/ -n auto
```

## Mock Infrastructure

The E2E tests use comprehensive mocking to isolate testing and ensure deterministic results:

### Available Mock Classes
- `MockPipeline` - Mock pipeline implementation
- `MockStage` - Mock stage implementation  
- `MockProvider` - Generic provider mock
- `MockAnkiConnect` - AnkiConnect API mock
- `MockOpenAI` - OpenAI API mock
- `MockForvo` - Forvo API mock

### Mock Fixtures
- `mock_vocabulary_data` - Sample vocabulary.json data
- `mock_conjugation_data` - Sample conjugations.json data
- `mock_config_data` - Sample config.json data
- `temp_project_dir` - Temporary project with mock files
- `mock_external_apis` - All external APIs mocked

### Using Mocks in Tests

```python
def test_pipeline_execution(mock_external_apis, temp_project_dir):
    """Test using mock infrastructure"""
    # External APIs are automatically mocked
    # Project directory is isolated
    
    # Your test code here
    pipeline = VocabularyPipeline()
    result = pipeline.execute_stage("media_gen", context)
    
    # Assertions against mock behavior
    assert mock_external_apis['openai'].requests
```

## Test Contract Guidelines

### Contract-Focused Testing
- Test **behavior**, not implementation
- Focus on **public interfaces**
- Define **expected outcomes**
- Avoid **brittle implementation details**

### Good Contract Test
```python
def test_pipeline_registration():
    """Contract: Pipelines can be registered and discovered"""
    registry = get_pipeline_registry()
    
    # Should be able to register new pipeline
    pipeline = MockPipeline()
    registry.register(pipeline)
    
    # Should be discoverable
    assert pipeline.name in registry.list_pipelines()
    assert registry.get_pipeline(pipeline.name) == pipeline
```

### Bad Contract Test
```python
def test_pipeline_internal_data_structure():
    """BAD: Tests implementation details"""
    registry = PipelineRegistry()
    
    # DON'T test internal data structures
    assert hasattr(registry, '_pipelines')
    assert isinstance(registry._pipelines, dict)
```

## Error Handling Tests

Every component should have corresponding error handling tests:

```python
def test_stage_handles_invalid_context():
    """Contract: Stages handle invalid context gracefully"""
    stage = MockStage("test_stage")
    
    # Should raise appropriate error for invalid context
    with pytest.raises(ValidationError):
        stage.execute({})  # Empty context
```

## Performance Contracts

Some tests include performance contracts:

```python
def test_single_word_processing_performance():
    """Contract: Single word processing completes quickly"""
    workflow = VocabularyWorkflow()
    
    result = workflow.process_word("casa")
    
    # Should complete within reasonable time
    assert result["processing_time"] < 5.0  # Under 5 seconds
```

## Writing New Tests

When adding new tests:

1. **Define the Contract**: Start with clear docstring describing what behavior is being tested
2. **Use Appropriate Mocks**: Isolate the component under test
3. **Test Success and Failure**: Include both happy path and error cases
4. **Add Markers**: Categorize with appropriate pytest markers
5. **Keep Tests Fast**: Use mocks to avoid slow external dependencies
6. **Make Tests Deterministic**: No random data or timing dependencies

### Test Template

```python
def test_new_functionality():
    """Contract: Clear description of expected behavior"""
    # Arrange - Set up test conditions
    component = MockComponent()
    
    # Act - Execute the behavior
    result = component.execute_operation(test_input)
    
    # Assert - Verify the contract
    assert result["status"] == "success"
    assert "expected_field" in result
```

## Integration with Refactor Sessions

Each refactor session must:

1. **Pass Previous Tests**: All tests from previous sessions must continue to pass
2. **Implement New Tests**: Make the new session's tests pass
3. **Add No Breaking Changes**: Don't break existing test contracts
4. **Document Changes**: Update this README if test structure changes

## Troubleshooting

### Common Issues

**Tests fail with import errors**: Ensure you're running from project root and environment is activated
```bash
cd /path/to/project
source activate_env.sh
pytest tests/e2e/
```

**Tests are flaky**: Check for non-deterministic behavior. All tests should be fully mocked
```bash
pytest tests/e2e/ --tb=long -v  # Get detailed failure info
```

**Tests are slow**: Check if external services are being called instead of mocks
```bash
pytest tests/e2e/ --durations=10  # Show slowest tests
```

### Getting Help

- Check test output with `-v` flag for detailed information
- Use `--tb=short` or `--tb=long` for different traceback formats
- Run individual test files to isolate issues
- Check `conftest.py` for available fixtures and mocks

## Maintenance

### Adding New Test Categories
1. Add marker to `pytest.ini`
2. Update this README
3. Add appropriate tests using the marker

### Updating Mock Infrastructure
1. Modify `conftest.py`
2. Update dependent tests
3. Document changes in this README

### Performance Monitoring
- Monitor test execution time
- Keep total suite under 30 seconds
- Use `--durations=10` to identify slow tests

---

**Remember**: These tests define immutable contracts. Once a test passes, it should continue to pass throughout the refactor. Changes to test behavior should be carefully considered and documented.