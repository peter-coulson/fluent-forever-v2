# Testing Context Boundaries

## Inclusion Rules

### Strategic Testing Guidance (INCLUDE)
- **Risk Classification Templates**: Criteria for assessing component risk levels
- **Test Organization Patterns**: How tests should be structured by risk category
- **Scaffolding Lifecycle Rules**: Development → production transition criteria
- **Mock Boundary Frameworks**: What to mock vs test directly decision trees
- **Test Consolidation Strategies**: "One test, multiple risks" design patterns

### Component Risk Mappings (INCLUDE - During Refactor)
- **High/Low Risk Classifications**: Applied using decision framework criteria
- **Workflow Criticality Assessment**: User workflow risk impact analysis
- **Test Strategy Assignment**: Risk level → test approach mapping

## Exclusion Rules

### Tactical Implementation Details (EXCLUDE)
- **Specific Test File Paths**: File names, directory structures, line numbers
- **Test Method Signatures**: Function names, parameter lists, assertion patterns
- **Framework Syntax**: Testing framework-specific code patterns
- **Coverage Metrics**: Test counts, percentage coverage, quantitative measures
- **Individual Test Cases**: Specific test implementations or test data

### Maintenance Implementation (EXCLUDE)
- **Test Execution Logs**: Runtime output, failure messages, debug information
- **Performance Metrics**: Test execution times, resource usage
- **Environment Configuration**: Test runner setup, CI/CD pipeline details

## Gray Area Resolution

**Test Utilities/Helpers**: Include strategic reusable patterns, exclude implementation details
**Organizational Structure**: Include high-level organization principles, exclude specific file structures
**Risk Assessment Granularity**: Include component-level decisions, exclude method-level details

## Context Domain Scope

This testing context provides **application guidance** for Risk-Based Testing principles within the specific pipeline architecture, not duplication of core testing framework concepts.

**Content Relationship**:
- **Framework-stable content** derives from Risk-Based Testing principles
- **Implementation-dynamic content** applies framework principles to pipeline components
