# Mock Boundary Strategy

## External/Uncontrolled Dependencies (MOCK)

### Provider APIs
**External Services**: Forvo, ElevenLabs, OpenAI, Azure Speech
- **Rationale**: Uncontrolled, rate-limited, cost implications
- **Mock Strategy**: Centralized provider mocks with realistic response patterns
- **Test Focus**: Provider integration logic, error handling, configuration injection

### Network Dependencies
**External Calls**: HTTP requests, API authentication
- **Rationale**: Network reliability outside system control
- **Mock Strategy**: Network layer mocking with failure simulation
- **Test Focus**: Retry logic, timeout handling, graceful degradation

### External File Systems
**External Paths**: User-specified directories, temporary file creation
- **Rationale**: Filesystem permissions, disk space outside system control
- **Mock Strategy**: Filesystem abstraction layer mocking
- **Test Focus**: Permission handling, error recovery, cleanup logic

## Internal/Controlled Systems (TEST DIRECTLY)

### Pipeline Architecture
**Core Components**: Pipeline execution, stage orchestration, context management
- **Rationale**: Internal logic, controlled environment, core business logic
- **Test Strategy**: Real component interaction testing
- **Test Focus**: Execution flow, data transformation, error propagation

### Configuration System
**Internal Config**: JSON loading, environment substitution, validation
- **Rationale**: Internal logic, deterministic behavior
- **Test Strategy**: Real configuration processing with controlled inputs
- **Test Focus**: Parsing logic, validation rules, error handling

### Local Data Operations
**Internal Storage**: JSON data files, local database operations
- **Rationale**: Controlled environment, deterministic behavior
- **Test Strategy**: Real file operations with test isolation
- **Test Focus**: Data integrity, concurrency, backup/recovery

## Mock Implementation Patterns

**Centralized Mocks**: Reusable provider mocks for common external services
**Per-Test Mocks**: Specific scenario mocking for edge case testing
