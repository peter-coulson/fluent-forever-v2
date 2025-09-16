# Component Testing Strategy

Core infrastructure component classification using three-tier risk framework (reference: `../strategy/risk-based-testing.md` for complete guidelines).

## High-Risk Components (5-10% - Comprehensive Testing)

**CLI Pipeline Integration** (Comprehensive E2E Coverage):
- Command routing, registry discovery, execution flow validation
- Configuration loading → Provider setup → Context management → Command execution
- Error handling and recovery patterns across component boundaries

**Provider Registry System** (Comprehensive E2E Coverage):
- Dynamic loading, configuration injection, pipeline assignments
- Provider lifecycle management with external service mocking
- Registry coordination and discovery mechanisms

**Context Management** (Comprehensive E2E Coverage):
- Stage-to-stage data flow, state tracking, error accumulation
- Inter-component data passing and context integrity validation
- Pipeline execution state management and completion tracking

## Complex Components (10-15% - Good Unit Coverage)

**Core Business Logic**
- Data transformation algorithms
- Validation rule engines
- Configuration parsing and resolution logic

## Simple Components (75-85% - Smoke Tests)

**Basic Infrastructure**
- MediaProvider: API calls to Forvo, OpenAI, Runware (failures are visible)
- Registry systems: Dynamic loading and component discovery
- Pipeline: Stage orchestration logic
- Stage: Individual processing and context handling
- Context Management: Inter-stage data flow and state handling
- CLI Commands: Argument parsing and validation

## Core Infrastructure Testing Approach

**E2E Validation Strategy**: High-risk components validated through comprehensive E2E workflows rather than separate integration tests. This approach provides realistic component coordination validation while maintaining efficient test maintenance.

**Integration Testing Decision**: Integration tests were evaluated and determined unnecessary for core infrastructure. The E2E approach adequately covers component coordination scenarios that integration tests would address, with better workflow realism and lower maintenance overhead.

## Mock Boundaries

**External Service Boundary**: Mock all external APIs for E2E infrastructure testing
**File System Boundary**: Mock file operations for unit testing, use real files for E2E
**Environment Boundary**: Mock environment variables for unit testing, use real environment for E2E

---
*Strategic foundation: Risk classification and mock boundary patterns from `../strategy/`*
