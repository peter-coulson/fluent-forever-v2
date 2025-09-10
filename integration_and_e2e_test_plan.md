# Integration & End-to-End Test Plan
## Fluent Forever V2 - Language Learning Materials System

### System Overview
This system is a CLI-based pipeline framework for creating language learning materials. It uses a plugin architecture with:
- **Pipelines**: Orchestrate multi-stage workflows
- **Stages**: Processing steps that can be chained together
- **Providers**: External service integrations (audio, images, data storage, Anki sync)
- **CLI**: User interface for discovering and executing pipelines

### Testing Philosophy
**Minimal but precise coverage** focusing on:
1. **Framework integrity** - Core abstractions work correctly
2. **Integration contracts** - Components connect and communicate properly
3. **External service handling** - Providers handle real-world scenarios gracefully
4. **CLI workflows** - End-to-end user experience
5. **Error resilience** - Graceful degradation and error handling

---

## Integration Tests

### 1. Provider Registry Integration
**Purpose**: Validate provider discovery, registration, and configuration-driven setup

**Test Cases**:
- `test_provider_registry_from_config()` - Load providers from config file
- `test_provider_registry_missing_config()` - Handle missing/invalid config gracefully
- `test_provider_registry_optional_providers()` - Audio/image providers are optional, data/sync required
- `test_provider_registry_invalid_provider_type()` - Fail gracefully on unsupported provider types

**Key Assertions**:
- Correct provider instances created from config
- Default providers registered when config is minimal
- Optional providers (audio/image) only created when configured
- Clear error messages for configuration problems

### 2. Pipeline-Provider Integration
**Purpose**: Validate pipeline context creation and provider access

**Test Cases**:
- `test_pipeline_context_provider_access()` - Context provides access to all registered providers
- `test_pipeline_context_missing_provider()` - Stages handle missing optional providers
- `test_pipeline_context_data_flow()` - Data flows correctly between stages via context

**Key Assertions**:
- Context contains providers from registry
- Stages can access providers through context
- Context data survives stage transitions
- Missing providers handled according to requirement level

### 3. CLI-Registry Integration
**Purpose**: Validate CLI command integration with registries

**Test Cases**:
- `test_cli_list_command_integration()` - List command shows registered pipelines
- `test_cli_info_command_integration()` - Info command shows pipeline details
- `test_cli_run_command_no_pipelines()` - Run command handles empty registry gracefully

**Key Assertions**:
- CLI commands work with real registry instances
- Commands handle empty registries gracefully
- Registry errors propagate to CLI with user-friendly messages

### 4. Configuration Integration
**Purpose**: Validate configuration loading and environment variable substitution

**Test Cases**:
- `test_config_environment_substitution()` - Environment variables resolved correctly
- `test_config_nested_provider_setup()` - Complex provider configs loaded properly
- `test_config_file_not_found()` - Missing config handled gracefully

**Key Assertions**:
- Environment variables substituted in config values
- Provider-specific configuration sections processed correctly
- System works with missing or invalid configuration files

---

## End-to-End Tests

### 1. CLI Workflow - Discovery
**Purpose**: Test complete user journey for discovering available functionality

**Scenario**: New user explores system capabilities
```bash
# Test flow:
python -m src.cli.pipeline_runner list
python -m src.cli.pipeline_runner list --detailed
python -m src.cli.pipeline_runner info vocabulary --stages
```

**Test Cases**:
- `test_e2e_discovery_workflow()` - Complete discovery journey works

**Key Assertions**:
- All commands execute without errors
- Output is properly formatted and informative
- Commands provide appropriate feedback for empty system

### 2. CLI Workflow - Error Handling
**Purpose**: Test system behavior under common error conditions

**Test Cases**:
- `test_e2e_invalid_pipeline_name()` - Friendly error for non-existent pipelines
- `test_e2e_missing_required_args()` - Clear error messages for missing CLI arguments
- `test_e2e_invalid_config_file()` - Graceful handling of config file problems

**Key Assertions**:
- Clear, actionable error messages
- Non-zero exit codes for errors
- No stack traces exposed to users

### 3. Provider Connection End-to-End
**Purpose**: Validate real external service connectivity (with mocking for reliability)

**Test Cases**:
- `test_e2e_data_provider_lifecycle()` - Full data provider workflow (save/load/exists)
- `test_e2e_provider_connection_failure()` - External service unavailable scenarios
- `test_e2e_provider_authentication_failure()` - Invalid API keys/credentials

**Key Assertions**:
- Data providers can perform full CRUD operations
- External service failures handled gracefully
- Authentication errors provide clear guidance

### 4. Mock Pipeline End-to-End
**Purpose**: Test complete pipeline execution using mock implementations

**Implementation**:
- Create `MockPipeline` with simple stages
- Create `MockStage` that uses providers
- Test full execution flow

**Test Cases**:
- `test_e2e_mock_pipeline_success()` - Complete pipeline executes successfully
- `test_e2e_mock_pipeline_stage_failure()` - Pipeline handles stage failures
- `test_e2e_mock_pipeline_dry_run()` - Dry run mode works correctly

**Key Assertions**:
- Stages execute in correct order
- Context data flows between stages
- Stage failures stop execution appropriately
- Dry run shows execution plan without side effects

---

## Test Implementation Strategy

### Test Organization
```
tests/
├── integration/
│   ├── test_provider_registry_integration.py
│   ├── test_pipeline_integration.py
│   ├── test_cli_integration.py
│   └── test_config_integration.py
├── e2e/
│   ├── test_cli_workflows.py
│   ├── test_provider_workflows.py
│   └── test_mock_pipeline.py
└── fixtures/
    ├── test_configs/
    └── mock_implementations/
```

### Key Testing Utilities

**Mock Implementations**:
- `MockPipeline` - Simple pipeline for testing framework
- `MockStage` - Stage that exercises provider interfaces
- `MockProvider` - Predictable provider for testing

**Test Fixtures**:
- Config files with various provider combinations
- Environment variable setups
- Expected output formats

**Assertions Helpers**:
- CLI output format validation
- Provider interface compliance checking
- Error message format validation

### Test Data Management
- Use temporary directories for file-based tests
- Mock external API calls for reliability
- Parameterized tests for different configuration combinations
- Clean setup/teardown for isolated tests

---

## Success Criteria

### Integration Tests Success
- All provider types can be loaded from configuration
- CLI commands work with real registry instances
- Component interfaces are correctly implemented
- Error conditions produce appropriate responses

### E2E Tests Success
- Users can discover system functionality through CLI
- Common error scenarios provide clear guidance
- Mock pipeline demonstrates full framework functionality
- External service integration patterns are validated

### Coverage Goals
- **Not maximum coverage** - **Optimal coverage**
- Focus on integration points and user workflows
- Test framework contracts, not implementation details
- Validate error handling and edge cases
- Ensure new pipelines/providers will work correctly

This test plan validates that the plugin architecture is solid and ready for concrete pipeline implementations, while ensuring users have a good experience even with an initially empty system.
