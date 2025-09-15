# Infrastructure Mock Boundaries

Infrastructure-specific applications of mock boundary strategy for core testing without business logic dependencies.

## Infrastructure-Specific Mock Decisions

### Provider System Boundaries

**External Service APIs (MOCK)**:
- **Forvo Audio API**: Mock HTTP requests and response parsing
- **Image Provider APIs**: Mock external image service calls
- **Anki Sync Services**: Mock AnkiConnect and sync operations
- **Authentication Systems**: Mock API key validation and token handling

**Provider Infrastructure (TEST DIRECTLY)**:
- **Provider Registry**: Dynamic loading, configuration injection, pipeline filtering
- **Provider Base Classes**: MediaProvider initialization and lifecycle
- **Configuration Validation**: Provider config parsing and error handling
- **Pipeline Assignment Logic**: Provider-to-pipeline filtering and authorization

### CLI System Boundaries

**External Command Execution (MOCK)**:
- **System Commands**: Mock subprocess calls and external tool execution
- **File System Operations**: Mock external file paths and permissions
- **Environment Variables**: Mock system environment for configuration testing

**CLI Infrastructure (TEST DIRECTLY)**:
- **Command Routing**: Argument parsing and command dispatch
- **Pipeline Discovery**: Registry initialization and lookup logic
- **Output Formatting**: Result display and error messaging
- **Execution Flow**: Command lifecycle and context management

### Configuration System Boundaries

**External Environment (MOCK)**:
- **Environment Variables**: Mock system environment for substitution testing
- **File System Access**: Mock configuration file loading and validation
- **Network Configuration**: Mock external configuration sources

**Configuration Infrastructure (TEST DIRECTLY)**:
- **JSON Processing**: Configuration parsing and validation
- **Environment Substitution**: Variable replacement logic
- **Provider Configuration**: Provider setup and validation rules
- **Error Handling**: Invalid configuration detection and messaging

## Centralized Mock Patterns for Infrastructure

### Provider Mock Factory

**Standardized Provider Mocks**:
- **MockMediaProvider**: Base implementation for audio/image providers
- **MockDataProvider**: Base implementation for data sources
- **MockSyncProvider**: Base implementation for sync operations
- **Configurable Behavior**: Success/failure scenarios with consistent interfaces

**Mock Configuration Injection**:
- **Provider Registry Setup**: Consistent mock provider registration
- **Configuration Validation**: Mock config with various validation scenarios
- **Pipeline Assignment Testing**: Mock provider filtering for pipeline authorization

### Infrastructure Test Fixtures

**Pipeline Infrastructure Fixtures**:
- **TestPipeline**: Minimal concrete Pipeline implementation
- **MockTestStage**: Configurable stage behavior for infrastructure testing
- **TestContext**: Context implementation with data flow validation
- **MockProviderRegistry**: Pre-populated registry for consistent testing

**Configuration Test Fixtures**:
- **Base Configuration**: Minimal valid configuration for infrastructure testing
- **Complex Configuration**: Multi-provider, multi-pipeline scenarios
- **Invalid Configuration**: Various error conditions for validation testing
- **Environment Test Data**: Mock environment variables for substitution testing

## Mock Implementation Strategy

### Infrastructure-Only Focus

**Mock External Dependencies**:
- All provider API calls and external service interactions
- File system operations beyond local test environment
- Network requests and authentication processes
- System environment variables and external commands

**Test Infrastructure Directly**:
- Pipeline registry and discovery mechanisms
- Provider loading and configuration injection
- Context management and data flow
- CLI command routing and execution coordination
- Configuration processing and validation

### Reusability Patterns

**Centralized Infrastructure Mocks**:
- **Provider Mock Factory**: Consistent mock creation across test scenarios
- **Configuration Fixtures**: Reusable configuration patterns for infrastructure testing
- **Registry Fixtures**: Pre-configured mock registries for common test patterns

**Per-Test Customization**:
- **Error Scenario Mocks**: Specific failure conditions for edge case testing
- **Complex Configuration**: Multi-provider scenarios requiring custom setup
- **Performance Testing**: Mock behavior optimized for performance validation

## Infrastructure Risk Mitigation

### High-Risk Infrastructure Patterns

**CLI Integration Risks**:
- **Mock**: External command execution, file system operations
- **Test Directly**: Command parsing, pipeline discovery, execution flow coordination

**Provider Registry Risks**:
- **Mock**: External API calls, authentication, file system access
- **Test Directly**: Dynamic loading, configuration injection, pipeline assignment filtering

**Context Management Risks**:
- **Mock**: External data persistence, network operations
- **Test Directly**: Stage-to-stage data flow, state tracking, error accumulation

### Mock Maintenance Strategy

**Centralized Mock Evolution**:
- **Version Management**: Mock interface evolution with infrastructure changes
- **Consistency Validation**: Mock behavior alignment with real external services
- **Performance Optimization**: Mock response times optimized for test execution speed

**Infrastructure Test Stability**:
- **Mock Isolation**: Infrastructure tests independent of external service availability
- **Deterministic Behavior**: Consistent mock responses for reliable test outcomes
- **Error Simulation**: Comprehensive external failure scenario coverage

This infrastructure-specific mock strategy enables comprehensive core system validation while maintaining clear boundaries between controlled infrastructure and external dependencies.
