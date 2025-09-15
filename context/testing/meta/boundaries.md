# Testing Context Boundaries

## Inclusion Rules

### Strategic Testing Guidance (INCLUDE)
- **Risk Classification Templates**: Criteria for assessing component risk levels
- **Test Organization Patterns**: How tests should be structured by risk category
- **Scaffolding Lifecycle Rules**: Development → production transition criteria
- **Mock Boundary Frameworks**: What to mock vs test directly decision trees
- **Test Consolidation Strategies**: "One test, multiple risks" design patterns

### Architectural Organization (INCLUDE)
- **Test directory architecture**: Foundational organizational patterns spanning domains
- **Cross-domain structures**: Patterns shared between multiple modules/pipelines
- **Component organization principles**: Fixture patterns, reuse strategies, mock boundaries
- **Implementation sequencing**: Architectural dependency ordering and priority guidance

### Component Risk Mappings (INCLUDE - During Refactor)
- **High/Low Risk Classifications**: Applied using decision framework criteria
- **Workflow Criticality Assessment**: User workflow risk impact analysis
- **Test Strategy Assignment**: Risk level → test approach mapping

## Exclusion Rules

### Implementation Syntax (EXCLUDE)
- **Test Method Signatures**: Function names, parameter lists, assertion patterns
- **Framework-Specific Syntax**: Testing framework code patterns (pytest/unittest specific)
- **File Naming Conventions**: Specific filename patterns within architectural structure
- **Line-Level Implementation**: Actual test code, assertions, and test data
- **Coverage Metrics**: Test counts, percentage coverage, quantitative measures

### Maintenance Implementation (EXCLUDE)
- **Test Execution Logs**: Runtime output, failure messages, debug information
- **Performance Metrics**: Test execution times, resource usage
- **Environment Configuration**: Test runner setup, CI/CD pipeline details

## Gray Area Resolution

**Test Utilities/Helpers**: Include strategic reusable patterns, exclude implementation syntax
**Architectural vs Implementation**: Include foundational organizational patterns, exclude framework-specific syntax
**Risk Assessment Granularity**: Include component-level decisions, exclude method-level details

## Context Domain Scope

This testing context provides **application guidance** for Risk-Based Testing principles within the specific pipeline architecture, not duplication of core testing framework concepts.

**Content Relationship**:
- **Framework-stable content** derives from Risk-Based Testing principles
- **Implementation-dynamic content** applies framework principles to pipeline components
