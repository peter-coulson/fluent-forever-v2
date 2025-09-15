# Component Testing Strategy

Core infrastructure component classification using three-tier risk framework (reference: `../strategy/risk-based-testing.md` for complete guidelines).

## High-Risk Components (5-10% - Comprehensive Testing)

**SyncProvider System**
- Real Anki integration via AnkiConnect - data corruption risk
- External service authentication and error handling

**Complete CLI Workflows with File Operations**
- End-to-end command execution with real file system operations
- Configuration loading and output generation - data overwrite risk

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

## Mock Boundaries

**External Service Boundary**: Mock all external APIs for integration testing, use real APIs for E2E
**File System Boundary**: Mock file operations for unit testing, use real files for integration/E2E
**Environment Boundary**: Mock environment variables for unit testing, use real environment for integration/E2E

---
*Strategic foundation: Risk classification and mock boundary patterns from `../strategy/`*
