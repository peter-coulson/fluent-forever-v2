# Core Infrastructure Testing Context

Primary validation strategy for shared infrastructure components. Provides comprehensive testing of core system foundation.

## Scope & Boundaries

**Core Infrastructure**: Core (Pipeline engine, Stage system, Context, Config), Providers (MediaProvider, DataProvider, SyncProvider, Registry), CLI (Commands, Runner)

**Primary Validation Principle**:
- **Core infrastructure tests** provide primary validation for all shared components (providers, registries, engines, stages)
- **Shared infrastructure** comprehensively tested in core for reliable consumption
- **Component isolation** enables focused testing of infrastructure behavior

**Content Boundaries** (reference: `../meta/boundaries.md`)
- **INCLUDE**: Strategic testing decisions, component risk assessments, mock boundary choices
- **EXCLUDE**: Tactical implementation details, specific test code, coverage metrics

**Specificity Boundary**: Strategic patterns and frameworks IN, implementation syntax and file details OUT

## Success Criteria

Core testing is sufficient when:
1. **Shared infrastructure components** comprehensively validated with full test coverage
2. **Provider systems** tested with external service mocking for reliable consumption
3. **Core orchestration** patterns validated independently of business logic
4. **Component coordination** tested with strategic mocking for real interaction patterns
5. **Shared stages** validated for reuse with complete behavior coverage

## Strategic Division

**E2E Infrastructure Testing**: Complete shared component workflows with comprehensive validation:
- **Provider Integration**: Full provider workflows with mocked external services
- **CLI Infrastructure**: Command routing and core system orchestration with mock workflows

**Integration Infrastructure Testing**: Component coordination with strategic mocking:
- **Registry Systems**: Provider loading, discovery, and configuration injection
- **Context Management**: Inter-stage data flow and state handling
- **Configuration**: Environment resolution and variable substitution
- **Pipeline Engine**: Stage coordination and execution flow

**Unit Infrastructure Testing**: Individual shared component validation:
- **Provider Components**: Audio, image, sync, data provider logic with mocked externals
- **Core Components**: Pipeline engine, stage system, registry mechanisms
- **CLI Components**: Command parsing, routing, and infrastructure integration

**Shared Stage Testing**: Reusable stages (file I/O, validation, formatting)

**Component Storage**: Reusable fixtures and mocks for consistent testing patterns

## Organizational Architecture

**Test Organization**: Reference `../strategy/test-organization.md` for core infrastructure testing structure patterns.

## Expansion Structure

As implementation develops, add specificity in this order:
1. **Risk Assessment Detail** → `component-strategy.md` (component-specific patterns)
2. **Component Fixtures** → Focus on reusable mocks and test data patterns

**Reference Flow**: All expansion references strategic frameworks in `../strategy/` rather than duplicating content.
