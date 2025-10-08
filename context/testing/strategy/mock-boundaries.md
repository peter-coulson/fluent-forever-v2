# Mock Boundary Strategy

## External/Uncontrolled Dependencies (MOCK)

External dependencies requiring mocking:

### Provider APIs
**Services**: External APIs, third-party services, authentication-required endpoints
- **Application**: Mock external/uncontrolled dependencies
- **Pipeline Focus**: Provider integration logic, configuration injection, error handling

### Network Dependencies
**Application**: Network calls require mocking
- **Pipeline Focus**: API orchestration, retry logic, graceful degradation

### Time/Date Functions
**Application**: External time dependencies require mocking
- **Pipeline Focus**: Timestamp generation, scheduling logic, time-based workflows

### External File Systems
**Application**: External file systems require mocking
- **Pipeline Focus**: Output path handling, cleanup logic, permission management

## Internal/Controlled Systems (TEST DIRECTLY)

Internal/controlled systems tested directly:

### Pipeline Architecture
**Application**: Internal pipeline logic tested directly
- **Pipeline Focus**: Stage execution, context flow, transformation logic

### Configuration System
**Application**: Configuration system tested directly
- **Pipeline Focus**: Pipeline configuration, validation rules, environment handling

### Local Data Operations
**Application**: Local operations tested directly
- **Pipeline Focus**: Data integrity, JSON processing, state management

## Mock Implementation Patterns

### Reusability Strategy
Reusability patterns for mock implementation:
- **Centralized Mocks**: Common external services, shared provider patterns
- **Per-Test Mocks**: Specific scenarios, edge cases, error conditions
- **LLM Discretion**: Implementation details guided by maintainability and clarity

### Implementation Guidelines
- **Centralized**: Use for common external service patterns (APIs, authentication)
- **Per-Test**: Use for specific failure scenarios or edge cases
- **Hybrid**: Combine centralized base mocks with per-test customization when needed
