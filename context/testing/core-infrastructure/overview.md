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

## Infrastructure-Only Testing Patterns

### Mock Boundary Decisions for Infrastructure
**External Dependencies (MOCK)**:
- **Provider APIs**: All external service calls (Forvo, image APIs, Anki sync)
- **File System Operations**: External file operations and permissions
- **Network Dependencies**: All HTTP requests and authentication

**Internal Systems (TEST DIRECTLY)**:
- **Pipeline Infrastructure**: Registry, context management, execution flow
- **Configuration System**: JSON loading, environment substitution, validation
- **Local Data Operations**: Context data flow, stage completion tracking

### Test Fixture Strategy for Infrastructure
**Minimal Test Implementations**:
- **TestPipeline**: Concrete Pipeline with configurable stages and phases
- **MockTestStage Variants**: Success/Failure/ContextDependent/ProviderUsing stages
- **Configuration Fixtures**: Base, complex, and invalid configuration scenarios
- **MockProviderRegistry**: Pre-populated registry for consistent testing

### Component Risk Classifications
**High-Risk Components** (Comprehensive E2E Coverage):
- **CLI Pipeline Integration**: Command routing, registry discovery, execution flow
- **Provider Registry System**: Dynamic loading, configuration injection, pipeline assignments
- **Context Management**: Stage-to-stage data flow, state tracking, error accumulation

**Complex Components** (Good Unit + Integration Coverage):
- **Configuration System**: Environment substitution, provider config validation
- **Logging Infrastructure**: Context-aware logging, performance monitoring

**Simple Components** (Smoke Test Coverage):
- **Abstract Base Classes**: Pipeline, Stage interfaces
- **Utility Functions**: Error formatting, validation helpers

### Infrastructure Test Consolidation Patterns
**CLI Workflow Consolidation** (Reference: `../strategy/test-consolidation.md`):
- **Single E2E Test**: CLI → Registry → Provider → Execution flow
- **Multiple Risk Coverage**: Command routing, provider loading, context flow, error handling
- **Validation Checkpoints**: Assert infrastructure behavior at each workflow transition

**Provider Integration Consolidation**:
- **Single Integration Test**: Provider lifecycle with configuration injection
- **Multiple Risk Coverage**: Dynamic loading, config validation, pipeline filtering, error scenarios
- **Shared Mock Patterns**: Centralized provider mock factory for consistency

### Scaffolding Lifecycle Strategy for Infrastructure
**Development Phase** (Current):
- **Over-testing acceptable**: Comprehensive validation during infrastructure building
- **Detailed validation**: All infrastructure coordination patterns
- **Quick feedback**: Extensive coverage for rapid bug identification

**Production Transition** (Future):
- **Risk-based consolidation**: Eliminate tests that don't mitigate identified risks
- **Multi-risk tests**: Combine scaffolding tests following consolidation patterns
- **Maintenance reduction**: Keep only high-risk scenario coverage

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

## Strategic Documentation

### Infrastructure-Specific Guidance
- **Mock Boundaries**: `mock-boundaries.md` - infrastructure-specific mock decision patterns and provider system boundaries
- **Test Fixtures**: `test-fixtures.md` - strategic fixture patterns for minimal infrastructure implementations

### Reference Integration
**Framework Alignment**: References strategic frameworks in `../strategy/` (mock-boundaries.md, test-consolidation.md) rather than duplicating content.
**Risk-Based Application**: Applies Risk-Based Testing principles specifically to infrastructure-only testing scenarios.

## Expansion Structure

As implementation develops, add specificity in this order:
1. **Risk Assessment Detail** → `component-strategy.md` (component-specific patterns)
2. **Component Fixtures** → Expand fixture patterns in `test-fixtures.md`
3. **Mock Boundary Evolution** → Update `mock-boundaries.md` with new infrastructure patterns

**Reference Flow**: All expansion references strategic frameworks in `../strategy/` rather than duplicating content.
