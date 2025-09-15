# Provider Refactor Implementation Prompts

**CONTEXT REQUIREMENT**: Before running any prompt, first read `context/implementation_plans/provider_refactor/general_context.md` to understand the architectural patterns and principles.

## Stage 0: Test Foundation Setup

### Prompt 0.1: Create Test Infrastructure
```
Read the Stage 0 plan in context/implementation_plans/provider_refactor/stage_0_test_foundation.md.

Implement the test infrastructure for the provider refactor:

1. Create the test directory structure as specified in section 0.1
2. Implement the ProviderTestBase class with the methods outlined in section 0.2
3. Create the MockAPIFactory with methods for OpenAI and Forvo API mocking
4. Set up the test fixtures for provider configurations

Follow the testing conventions and ensure all utilities are importable.

Test your implementation by:
- Importing the new test utilities
- Running existing tests to ensure no regressions
- Creating a simple test using the new infrastructure to verify it works

Complete deliverables checklist from section "Testing Gateway".
```

### Prompt 0.2: Validate Test Foundation
```
Validate the test foundation setup:

1. Run all existing provider tests to ensure no regressions
2. Test the new infrastructure by creating a sample test that uses:
   - ProviderTestBase as the parent class
   - MockAPIFactory for API response mocking
   - Test fixtures for configuration validation
3. Verify the testing conventions work by writing one test following the naming patterns
4. Document any issues found and resolve them

Ensure all validation checklist items from Stage 0 are complete before proceeding.
```

## Stage 1: Configuration Architecture Foundation (TDD)

### Prompt 1.1: Write Configuration Tests
```
Read context/implementation_plans/provider_refactor/stage_1_configuration_foundation.md and follow TDD approach:

RED PHASE - Write failing tests first:
1. Write tests for MediaProvider constructor accepting config parameter
2. Write tests for abstract validate_config() method enforcement
3. Write tests for _setup_from_config() method availability
4. Write tests for backward compatibility (None config parameter)

Use the test infrastructure from Stage 0 and follow the patterns in general_context.md.

Create comprehensive test cases covering:
- Valid configuration scenarios
- Invalid configuration error handling
- Missing required configuration keys
- Config validation with different provider types

Do NOT implement any provider code yet. All tests should fail initially (RED phase).
```

### Prompt 1.2: Implement Configuration Foundation
```
GREEN PHASE - Implement minimal code to pass Stage 1 tests:

Following the patterns in general_context.md, implement:
1. Update MediaProvider base class constructor to accept optional config parameter
2. Add abstract validate_config() method
3. Add _setup_from_config() method with default implementation
4. Ensure backward compatibility for existing providers

Implementation must:
- Follow the constructor pattern shown in general_context.md
- Make config parameter optional (default empty dict)
- Call validate_config() and _setup_from_config() from constructor
- Not break any existing provider instantiation

Run tests to ensure they pass (GREEN phase).
```

### Prompt 1.3: Refactor Configuration Implementation
```
REFACTOR PHASE - Clean up configuration implementation:

1. Review the implementation for code quality
2. Add comprehensive docstrings following project patterns
3. Ensure error messages are clear and helpful
4. Add type hints for all parameters and return values
5. Verify the implementation follows the patterns in general_context.md

Test that:
- All Stage 1 tests still pass
- Existing provider tests are not broken
- Code quality meets project standards
- Documentation is complete and accurate
```

## Stage 2: Registry Infrastructure (TDD)

### Prompt 2.1: Write Dynamic Registry Tests
```
Read context/implementation_plans/provider_refactor/stage_2_registry_infrastructure.md and follow TDD approach:

RED PHASE - Write failing tests for dynamic registry:
1. Test MEDIA_PROVIDER_REGISTRY structure and import mappings
2. Test _create_media_provider() with valid and invalid provider types
3. Test configuration extraction and filtering (exclude 'type', 'pipelines')
4. Test _setup_media_providers() creates all configured providers
5. Test error handling for import failures and invalid configurations
6. Test registry initialization replaces hardcoded provider setup

Use mock imports and configuration fixtures from Stage 0 infrastructure.

Create test cases covering:
- All current provider types (openai, runware, forvo)
- Configuration injection at provider creation
- Error scenarios (missing modules, invalid configs)
- Integration with existing registry methods

All tests should fail initially (RED phase).
```

### Prompt 2.2: Implement Dynamic Registry
```
GREEN PHASE - Implement dynamic registry to pass tests:

Following the detailed implementation in stage_2_registry_infrastructure.md, implement:
1. Add MEDIA_PROVIDER_REGISTRY mapping with current providers
2. Implement _create_media_provider() method using importlib
3. Implement _extract_provider_configs() method
4. Implement _register_provider_by_type() method
5. Implement _setup_media_providers() method
6. Update ProviderRegistry.from_config() to use new unified setup

Implementation must:
- Use dynamic imports with proper error handling
- Extract provider-specific config correctly
- Maintain existing provider registration interface
- Handle import errors gracefully

Run tests to ensure they pass (GREEN phase).
```

### Prompt 2.3: Remove Duplicate Registry Code
```
REFACTOR PHASE - Clean up registry implementation:

1. Remove the ~80 lines of duplicate provider setup code
2. Replace hardcoded if/elif chains with unified method calls
3. Update error handling to be consistent across provider types
4. Add comprehensive logging for provider registration
5. Ensure configuration injection works for all provider types

Validation:
- All Stage 2 tests pass
- Existing providers can still be created and registered
- Registry initialization time is acceptable
- No duplicate code remains in ProviderRegistry
- Code follows patterns in general_context.md

Test with existing configurations to ensure backward compatibility.
```

### Prompt 2.4: Integration Validation
```
Validate the complete foundation (Stages 0-2):

1. Run full provider test suite to ensure no regressions
2. Test registry creation with actual configuration files
3. Verify all provider types can be dynamically loaded
4. Test configuration injection reaches provider constructors
5. Benchmark registry initialization performance
6. Validate error handling works correctly

Create a simple integration test that:
- Uses the dynamic registry to load all provider types
- Passes configuration to providers via constructor injection
- Verifies providers receive correct configuration
- Tests the complete flow from config file to provider instance

Ensure all success criteria from Stages 1-2 are met before declaring foundation complete.
```

## Usage Instructions

### Running Prompts Sequentially
1. **Read General Context**: Always start by reading `general_context.md`
2. **Follow TDD Cycles**: RED → GREEN → REFACTOR for each implementation stage
3. **Validate at Checkpoints**: Run integration validation before proceeding
4. **Document Issues**: Note any deviations or problems encountered

### Testing Between Prompts
```bash
# After each prompt, run validation commands:
python -m pytest tests/unit/providers/refactor/ -v  # New tests
python -m pytest tests/unit/providers/ -v --ignore=tests/unit/providers/refactor/  # Existing tests
```

### Success Criteria
- All TDD cycles complete (RED → GREEN → REFACTOR)
- All tests pass consistently
- No regressions in existing functionality
- Foundation ready for Stage 3+ implementation

## Notes
- These prompts assume familiarity with the existing codebase
- Each prompt should result in working, tested code
- Do not proceed to next stage until all validation steps pass
- Stages 3+ will require custom planning based on foundation implementation results
