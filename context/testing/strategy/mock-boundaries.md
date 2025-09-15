# Mock Boundary Strategy

## External/Uncontrolled Dependencies (MOCK)

Applies TESTING_FRAMEWORK.md mocking strategy to pipeline-specific external dependencies:

### Provider APIs
**Services**: Forvo, ElevenLabs, OpenAI, Azure Speech
- **Application**: Follow TESTING_FRAMEWORK.md external mocking guidelines
- **Pipeline Focus**: Provider integration logic, configuration injection, error handling

### Network Dependencies
**Application**: Network calls follow TESTING_FRAMEWORK.md external mocking patterns
- **Pipeline Focus**: API orchestration, retry logic, graceful degradation

### External File Systems
**Application**: External file systems follow TESTING_FRAMEWORK.md mocking guidelines
- **Pipeline Focus**: Output path handling, cleanup logic, permission management

## Internal/Controlled Systems (TEST DIRECTLY)

Applies TESTING_FRAMEWORK.md internal testing strategy to pipeline components:

### Pipeline Architecture
**Application**: Internal pipeline logic follows TESTING_FRAMEWORK.md controlled system testing
- **Pipeline Focus**: Stage execution, context flow, transformation logic

### Configuration System
**Application**: Configuration follows TESTING_FRAMEWORK.md internal testing guidelines
- **Pipeline Focus**: Pipeline configuration, validation rules, environment handling

### Local Data Operations
**Application**: Local operations follow TESTING_FRAMEWORK.md controlled testing patterns
- **Pipeline Focus**: Data integrity, JSON processing, state management

## Mock Implementation Patterns

Applies TESTING_FRAMEWORK.md reusability approach:
- **Centralized Mocks**: Pipeline provider service patterns
- **Per-Test Mocks**: Pipeline-specific scenario testing
