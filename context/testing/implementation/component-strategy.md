# Component Testing Strategy

Risk-based testing assignments for current system components (reference: `../strategy/` for risk assessment frameworks).

## E2E Testing Components (High Risk - External Integration)

**Provider System**
- MediaProvider: Real API calls to Forvo, OpenAI, Runware
- SyncProvider: Real Anki integration via AnkiConnect
- External service authentication and error handling

**Complete CLI Workflows**
- End-to-end command execution: config loading → registry → context → providers → results
- Real file system operations and output generation

## Integration Testing Components (Medium Risk - Internal Coordination)

**Registry Systems**
- ProviderRegistry: Dynamic loading with mocked external services
- PipelineRegistry: Component discovery and filtering

**Configuration System**
- Environment variable resolution and provider configuration injection

**Context Management**
- Inter-stage data flow and state management patterns
- Error accumulation across component boundaries

## Unit Testing Components (Low Risk - Internal Logic)

**Core Components**
- Pipeline: Stage orchestration logic (mocked context/stages)
- Stage: Individual processing with mocked context
- Config: JSON processing and variable substitution

**CLI Commands**
- Argument parsing and validation (mocked providers)

## Mock Boundaries

**External Service Boundary**: Mock all external APIs for integration testing, use real APIs for E2E
**File System Boundary**: Mock file operations for unit testing, use real files for integration/E2E
**Environment Boundary**: Mock environment variables for unit testing, use real environment for integration/E2E

---
*Strategic foundation: Risk classification and mock boundary patterns from `../strategy/`*
