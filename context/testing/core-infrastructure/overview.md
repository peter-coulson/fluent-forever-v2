# Core Infrastructure Testing Context

Infrastructure testing strategy for core system components independent of pipeline implementations. Supports infrastructure development and orchestration validation.

## Scope & Boundaries

**Core Infrastructure**: Core (Pipeline engine, Stage system, Context, Config), Providers (MediaProvider, DataProvider, SyncProvider, Registry), CLI (Commands, Runner)

**Dual Strategy Principle**:
- **Core infrastructure tests** validate orchestration and coordination patterns independently
- **Pipeline tests** provide comprehensive validation through real infrastructure usage
- **Shared components** tested in core when used across multiple pipelines

**Content Boundaries** (reference: `../meta/boundaries.md`)
- **INCLUDE**: Strategic testing decisions, component risk assessments, mock boundary choices
- **EXCLUDE**: Tactical implementation details, specific test code, coverage metrics

**Specificity Boundary**: Strategic patterns and frameworks IN, implementation syntax and file details OUT

## Success Criteria

Core testing is sufficient when:
1. **Infrastructure orchestration** patterns validated independently of pipeline logic
2. **Component coordination** tested with minimal mocking for real interaction patterns
3. **Shared stages** validated for cross-pipeline reuse
4. **Mock boundaries** clearly defined for infrastructure vs external service testing
5. **Component fixtures** enable reusable testing patterns

## Strategic Division

**E2E Infrastructure Testing**: Complete CLI workflows with mock pipelines for orchestration validation

**Integration Infrastructure Testing**: Component coordination with strategic mocking:
- **Registry Systems**: Provider loading and configuration injection
- **Context Management**: Inter-stage data flow and state handling
- **Configuration**: Environment resolution and variable substitution
- **Pipeline Engine**: Stage coordination with mock stages

**Unit Infrastructure Testing**: Individual component logic for development debugging:
- **Pipeline Engine**: Orchestration logic (mocked stages)
- **CLI Commands**: Argument parsing (mocked dependencies)

**Shared Stage Testing**: Stages used across multiple pipelines (file I/O, validation, formatting)

**Component Storage**: Reusable fixtures and mocks for consistent testing patterns

## Organizational Architecture

**Test Organization**: Reference `../strategy/test-organization.md` for shared architectural patterns covering both core infrastructure and pipeline testing structure.

## Expansion Structure

As implementation develops, add specificity in this order:
1. **Risk Assessment Detail** → `component-strategy.md` (component-specific patterns)
2. **Component Fixtures** → Focus on reusable mocks and test data patterns

**Reference Flow**: All expansion references strategic frameworks in `../strategy/` rather than duplicating content.
