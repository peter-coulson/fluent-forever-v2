# Risk-Based Testing Application

## Pipeline Architecture Risk Patterns

### Component Risk Assessment Framework
Apply `meta/decision-framework.md` evaluation templates to pipeline components:

**Pipeline Level**: Sequential stage execution with context flow
**Stage Level**: Individual processing units
**Provider Level**: External service integrations

Use **Impact + Detection Matrix** criteria from decision framework for pipeline-specific risk classification.

### Test Strategy Mapping

Tool-to-risk mapping patterns for pipeline components:

**High-Risk Strategy**: Inverted pyramid - E2E primary, integration secondary, minimal unit
**Low-Risk Strategy**: Traditional pyramid - unit primary, integration/E2E optional

### Common Pipeline Risk Patterns

**Data Processing Pipelines**: Input → transformation → output → storage
- **High-Risk**: Source data corruption, synchronization failures, transformation logic errors
- **Medium-Risk**: Media generation, external provider coordination, template processing

**Sequential Processing**: Multi-stage workflows with state dependencies
- **High-Risk**: State management between stages, dependency validation, error propagation
- **Medium-Risk**: Stage coordination, resource allocation, performance optimization

## Implementation Priorities

### Testing Priorities Framework
1. **Risk Assessment per Component**: Evaluate each stage using detection difficulty + impact + usage frequency
2. **Graduated Testing Effort**: Match testing intensity to actual risk and development needs
3. **Critical Workflow Focus**: Prioritize E2E testing for most common/valuable stage combinations
4. **Context Integration**: Test stage-to-stage data passing for critical workflows
5. **Component Boundaries**: Use real components for internal systems, mocks for external dependencies

### Stage-Level Testing Guidelines

**High-Risk Stages** (database writes, data transformation, critical business logic):
- **Primary**: Integration tests mandatory
- **Secondary**: E2E tests for workflow validation
- **Minimal**: Unit tests for complex algorithms

**Medium-Risk Stages** (media generation, API calls):
- **Primary**: Unit tests preferred
- **Optional**: Integration tests when convenient

**Low-Risk Stages** (logging, simple utilities):
- **Minimal**: Focus on development aids
- **Optional**: Testing when useful for debugging

### Workflow-Level Testing Strategy

**Critical User Workflows**: E2E tests for most common/valuable stage combinations
**Secondary Workflows**: E2E tests when convenient for debugging complex interactions
**Ad-hoc Combinations**: No dedicated tests - rely on stage-level coverage

## Application Pattern

Apply risk assessment **component-by-component** during test refactor, not system-wide pre-classification.
