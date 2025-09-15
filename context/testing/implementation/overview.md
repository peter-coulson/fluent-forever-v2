# Testing Implementation Context

Testing strategy for existing system components (excluding pipelines which are not yet implemented).

## Scope & Boundaries

**Current System**: Core (Pipeline, Stage, Context, Config), Providers (MediaProvider, DataProvider, SyncProvider, Registry), CLI (Commands, Runner)

**Content Boundaries** (reference: `../meta/boundaries.md`)
- **INCLUDE**: Strategic testing decisions, component risk assessments, mock boundary choices
- **EXCLUDE**: Tactical implementation details, specific test code, coverage metrics

**Specificity Boundary**: Strategic patterns and frameworks IN, implementation syntax and file details OUT

## Success Criteria

Testing implementation is sufficient when:
1. **High-risk components** have E2E coverage with real external dependencies
2. **Medium-risk components** have integration coverage with strategic mocking
3. **Mock boundaries** are clearly defined and consistently applied
4. **Test consolidation** follows "one test, multiple risks" principle (reference: `../strategy/`)

## Strategic Division

**E2E Testing (High Risk)**: Complete CLI workflows, real provider integration, external service authentication
**Integration Testing (Medium Risk)**: Component interaction with mocked externals, registry/config behavior
**Unit Testing (Low Risk)**: Individual component logic with full mocking

## Expansion Structure

As implementation develops, add specificity in this order:
1. **Risk Assessment Detail** → `component-strategy.md` (component-specific patterns)
2. **Mock Boundary Specifics** → New `mock-patterns.md` (concrete boundary decisions)
3. **Consolidation Patterns** → New `test-consolidation.md` (multi-risk test designs)

**Reference Flow**: All expansion references strategic frameworks in `../strategy/` rather than duplicating content.
