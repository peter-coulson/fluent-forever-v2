# Test Organization Architecture

Architectural test organization patterns separating core infrastructure from pipeline-specific testing. Shared organizational guidance for both core infrastructure and pipeline testing contexts.

## Structure Overview

```
tests/
├── fixtures/             # Test data and mock implementations
│   ├── mock-providers/   # Reusable mock provider implementations
│   ├── mock-pipelines/   # Minimal pipeline implementations for core testing
│   ├── shared-stages/    # Mock implementations of shared pipeline stages
│   ├── test-data/        # Sample vocabulary, configs, expected outputs
│   └── helpers/          # Test utilities and setup functions
├── core/                 # Core infrastructure testing (infrastructure development)
│   ├── e2e/              # Complete CLI workflows with mock pipelines
│   ├── integration/      # Component coordination with mocked externals
│   └── unit/             # Individual component logic for debugging
└── pipelines/            # Pipeline-specific tests (primary validation)
    ├── vocabulary/       # Complete vocabulary pipeline testing
    │   ├── e2e/          # Full vocabulary workflows with real infrastructure
    │   ├── integration/  # Stage coordination with real infrastructure
    │   └── unit/         # Individual vocabulary stage logic
    └── conjugation/      # Complete conjugation pipeline testing
        ├── e2e/          # Full conjugation workflows with real infrastructure
        ├── integration/  # Stage coordination with real infrastructure
        └── unit/         # Individual conjugation stage logic
```

## Test Component Storage (`tests/fixtures/`)

**Mock Providers** (`tests/fixtures/mock-providers/`):
- Reusable mock implementations for MediaProvider, SyncProvider
- Deterministic test data and predictable behavior
- Error simulation for testing failure scenarios

**Mock Pipelines** (`tests/fixtures/mock-pipelines/`):
- Minimal pipeline implementations for core infrastructure testing
- Simple stage definitions for infrastructure validation
- Test workflow patterns without business logic

**Shared Stages** (`tests/fixtures/shared-stages/`):
- Mock implementations of stages shared between pipelines
- Common processing stages (file I/O, validation, formatting)
- Reusable utility stages (logging, error handling)

**Test Data** (`tests/fixtures/test-data/`):
- Sample vocabulary lists and conjugation data
- Configuration files for different test scenarios
- Expected outputs for validation

**Test Helpers** (`tests/fixtures/helpers/`):
- Common setup and teardown functions
- Assertion utilities for pipeline testing
- Environment configuration for tests

## Core Infrastructure Testing (`tests/core/`)

**Purpose**: Validate infrastructure orchestration and coordination independently of pipeline implementations.

**E2E Tests** (`tests/core/e2e/`):
- Complete CLI workflows with mock pipelines (from fixtures)
- Infrastructure orchestration: config → registry → context → execution → output
- Pipeline engine coordination with mock stages
- Error handling and recovery patterns across components

**Integration Tests** (`tests/core/integration/`):
- Component interaction with mocked external services
- Registry systems: provider loading and configuration injection
- Context management: inter-stage data flow and state handling
- Configuration system: environment resolution and variable substitution

**Unit Tests** (`tests/core/unit/`):
- Individual component logic for debugging during development
- **Stage-per-file organization** for clear component separation

**Core Component Tests**:
- Pipeline engine orchestration logic (uses mock stages from fixtures)
- Provider registry loading mechanisms (uses mock providers from fixtures)
- Configuration environment resolution and variable substitution
- CLI argument parsing and validation (mocked dependencies)

**Shared Stage Testing**:
- Stages shared between pipelines tested in core (using shared-stages fixtures)
- Pipeline-specific stages tested within respective pipeline directories

## Pipeline-Specific Testing (`tests/pipelines/`) - PRIMARY VALIDATION

**Purpose**: Primary validation of both pipeline business logic AND core infrastructure through real usage.

**Structure**: Each pipeline (vocabulary, conjugation) contains:

**E2E Tests**: Complete CLI workflows with real infrastructure
- Full command execution: config → registry → context → providers → output
- Real file system operations and provider integration
- Validates core infrastructure through actual pipeline execution

**Integration Tests**: Stage coordination and component interaction
- Pipeline stage execution with real context management
- Provider registry and configuration resolution
- Error handling and data flow validation

**Unit Tests**: Pipeline-specific stage logic
- **Stage-per-file organization** as primary unit testing approach
- Individual stage implementations and data transformation algorithms
- Domain-specific business logic and validation rules

**Pipeline-Specific Areas**: Domain-specific business logic and validation rules for each pipeline's functional requirements

**Infrastructure Coverage**: Pipeline tests validate core infrastructure components as primary testing strategy.


## Key Testing Patterns

**Testing Strategy Approach**:
- **Pipeline tests**: Primary validation of business logic using validated infrastructure
- **Core tests**: Primary validation of shared infrastructure components (three-tier risk strategy)

**Component Reuse**: Fixtures enable consistent mocking patterns across all test types

**Stage-per-file Pattern**: Default organization for unit tests, both core components and pipeline stages

**Shared Stage Strategy**: Stages used across multiple pipelines tested in core; pipeline-specific stages tested within pipelines

**Mock Boundaries**:
- **Core tests**: Use fixtures for mocked pipelines, stages, providers, and external services
- **Pipeline tests**: Use fixtures for external services only, real core infrastructure

## Implementation Priority

1. **Test Fixtures** (`tests/fixtures/`) - Reusable mocks and test data foundation
2. **Core Infrastructure Tests** (`tests/core/`) - Primary validation of shared infrastructure (three-tier strategy)
3. **Pipeline Tests** (`tests/pipelines/`) - Primary validation of business logic using validated infrastructure

**Unit Test Organization**: Stage-per-file approach for both core components and pipeline stages, enabling clear separation of concerns and focused testing of individual units.

This structure supports primary validation of shared infrastructure (core tests) and business logic validation (pipeline tests), with three-tier risk strategy applied throughout.
