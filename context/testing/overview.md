# Testing Context Overview

## Purpose
Strategic testing guidance framework implementing Risk-Based Testing principles for pipeline-based language learning system.

## Domain Scope
- **Risk assessment frameworks** for system components
- **Strategic testing patterns** aligned with Risk-Based Testing principles
- **Scaffolding lifecycle management** for development → production transitions
- **Organizational guidance** for test structure and maintenance

## Architecture Layers

### Meta System (`context/testing/meta/`)
Testing context system self-documentation, maintenance models, and decision frameworks.

### Strategy Patterns (`context/testing/strategy/`)
Risk-based testing application patterns, scaffolding lifecycle rules, and mock boundary guidelines.

### Implementation Guidance (`context/testing/implementation/`)
**Populated during test refactor** - system-level testing implementation details:

**Risk Mappings** (`implementation/risk-mappings.md`):
- Actual component risk classifications applied using decision framework criteria
- Core system component assessments (pipeline engine, stage system, provider registry)
- Cross-cutting concern risk evaluations (configuration, logging, context management)

**Organization Patterns** (`implementation/organization-patterns.md`):
- Emergent test structure patterns from refactor implementation
- Risk-level to test-type mapping (high-risk → E2E primary)
- Directory organization and naming conventions that develop

**Workflow Approaches** (`implementation/workflow-approaches.md`):
- System-level workflow testing strategies (pipeline execution, provider integration)
- Cross-component integration testing patterns
- End-to-end system validation approaches

## Domain Boundaries

### System-Level Testing Context (This Context)
- **Risk-based testing framework** application to pipeline architecture
- **Strategic testing patterns** for pipeline systems generally
- **System component testing** (pipeline engine, stage system, provider registry)
- **Cross-cutting concerns** (configuration, logging, context management)

### Pipeline-Specific Testing Context (`context/modules/pipelines/`)
- **Individual pipeline testing** approaches (vocabulary, conjugation)
- **Pipeline implementation details** testing strategies
- **Pipeline-specific risk mappings** and workflow approaches
- **Same 3-file structure**: risk-mappings.md, organization-patterns.md, workflow-approaches.md

**Reference Flow**: Pipeline testing context references system testing framework (upward reference following context system principles).

## Navigation
- **Framework Foundations**: `meta/overview.md` → decision frameworks and maintenance models
- **Testing Strategy**: `strategy/overview.md` → risk-based patterns and scaffolding lifecycle
- **Implementation Details**: `implementation/` → system-level testing approaches (populated during refactor)
