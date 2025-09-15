# Risk-Based Testing Application

## Pipeline Architecture Risk Patterns

### Component Risk Assessment Framework
Apply `meta/decision-framework.md` evaluation templates to pipeline components:

**Pipeline Level**: Sequential stage execution with context flow
**Stage Level**: Individual processing units
**Provider Level**: External service integrations

Use **Impact + Detection Matrix** criteria from decision framework for pipeline-specific risk classification.

### Test Strategy Mapping

Three-tier risk classification for lean development:

**High-Risk Strategy**: Comprehensive testing - E2E primary, integration secondary, unit comprehensive
**Complex Strategy**: Good unit coverage - test all public methods with typical usage patterns and basic error cases
**Simple Strategy**: Smoke tests - component loads and basic functionality works

### Common Pipeline Risk Patterns

**Data Processing Pipelines**: Input → transformation → output → storage
- **High-Risk**: Source data corruption, synchronization failures, critical transformation logic
- **Complex**: Data transformation algorithms, validation rule engines
- **Simple**: Media generation, template processing, basic coordination

**Sequential Processing**: Multi-stage workflows with state dependencies
- **High-Risk**: State management between stages, dependency validation, error propagation
- **Complex**: Stage coordination algorithms, resource allocation logic
- **Simple**: Basic orchestration, performance monitoring, utility functions

## Implementation Priorities

### Testing Priorities Framework
1. **Three-Tier Risk Assessment**: High-risk (5-10%), Complex (10-15%), Simple (75-85%) classification
2. **Risk-Driven Coverage**: Match testing intensity to component risk and complexity
3. **High-Risk Focus**: Comprehensive testing only for critical components (data corruption, business logic)
4. **Complex Coverage**: Good unit testing for algorithms and transformation logic
5. **Simple Minimalism**: Smoke tests only for basic infrastructure and utilities

### Component Testing Guidelines

**High-Risk Components** (5-10% - external data writes, critical business logic, hard-to-debug failures):
- **Primary**: E2E tests for workflow validation
- **Secondary**: Integration tests for component interactions
- **Comprehensive**: Unit tests for all public methods and edge cases

**Complex Components** (10-15% - algorithms, transformations, validation rules):
- **Unit**: Test all public methods with typical usage patterns and basic error cases
- **Integration**: Test when component interacts with other components
- **Goal**: Enable confident refactoring of complex logic

**Simple Components** (75-85% - utilities, basic infrastructure, visible failures):
- **Smoke**: Component loads and basic functionality works
- **Minimal**: Focus on breakage detection over comprehensive coverage
- **Goal**: Catch regressions without maintenance overhead

### Workflow-Level Testing Strategy

**Critical User Workflows**: E2E tests for most common/valuable stage combinations
**Secondary Workflows**: E2E tests when convenient for debugging complex interactions
**Ad-hoc Combinations**: No dedicated tests - rely on stage-level coverage

## Application Pattern

Apply risk assessment **component-by-component** during test refactor, not system-wide pre-classification.
