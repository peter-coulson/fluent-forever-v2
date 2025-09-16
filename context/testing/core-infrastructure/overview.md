# Core Infrastructure Testing Context

Primary validation strategy for shared infrastructure components independent of pipeline implementations.

## Scope & Boundaries

**Core Infrastructure**: Core (Pipeline engine, Stage system, Context, Config), Providers (MediaProvider, DataProvider, SyncProvider, Registry), CLI (Commands, Runner)

**Primary Validation Principle**: Core infrastructure tests provide primary validation for all shared components with comprehensive E2E coverage through realistic workflows.

**Content Boundaries** (reference: `../meta/boundaries.md`)
- **INCLUDE**: Strategic testing decisions, component risk assessments, mock boundary choices
- **EXCLUDE**: Tactical implementation details, specific test code, coverage metrics

## Success Criteria

Core testing is sufficient when:
1. **Shared infrastructure components** comprehensively validated with full test coverage
2. **Provider systems** tested with external service mocking for reliable consumption
3. **Core orchestration** patterns validated independently of business logic
4. **Component coordination** tested with strategic mocking for real interaction patterns

## Strategic Division

**E2E Infrastructure Testing**: Primary validation approach for component coordination through complete workflows
**Unit Infrastructure Testing**: Individual shared component validation with mocked externals
**Integration Testing Decision**: Integration tests determined unnecessary - E2E approach provides sufficient component coordination validation

## Strategic Documentation

### Infrastructure-Specific Guidance
- **Component Strategy**: `component-strategy.md` - risk-based component classification and testing approaches
- **Implementation Status**: `implementation-status.md` - current unit testing implementation progress by risk tier
- **E2E Validation Patterns**: `e2e-validation-patterns.md` - comprehensive component coordination validation through complete workflows
- **Mock Boundaries**: `mock-boundaries.md` - infrastructure-specific mock decision patterns and provider system boundaries
- **Test Fixtures**: `test-fixtures.md` - strategic fixture patterns for minimal infrastructure implementations

### Reference Integration
**Framework Alignment**: References strategic frameworks in `../strategy/` (mock-boundaries.md, test-consolidation.md) rather than duplicating content.
**Risk-Based Application**: Applies Risk-Based Testing principles specifically to infrastructure-only testing scenarios.

## Organizational Architecture

**Test Organization**: Reference `../strategy/test-organization.md` for core infrastructure testing structure patterns.

## Expansion Structure

As implementation develops, add specificity through detail files referencing strategic frameworks in `../strategy/` rather than duplicating content.
