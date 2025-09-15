# Testing Decision Framework

## Risk Classification Criteria

### High-Risk Categories (Mandatory Testing)
High impact AND difficult to detect failures:
- **Database overwriting** - data corruption with silent failures
- **Source data overwriting** - irreversible data loss
- **Silent pipeline logic errors** - incorrect processing without clear indicators
- **Configuration drift** - environment-specific failures
- **Uncontrolled resource consumption** - performance degradation
- **Data validation bypass** - corrupted input processing
- **Version compatibility breaks** - deployment failures
- **State corruption** - inconsistent system state

### Complex Categories (Good Unit Coverage)
Algorithms, transformations, and complex business logic:
- Data transformation algorithms
- Validation rule engines
- Parsing and processing logic
- Business calculation methods

### Simple Categories (Smoke Tests)
Basic infrastructure with visible failures:
- Pipeline errors with clear messages
- Media provider failures (visible)
- Registry loading and discovery
- CLI parsing and utilities
- Basic orchestration logic

**Testing Approach**: Reference `../strategy/risk-based-testing.md` for complete three-tier strategy guidelines.

### High-Risk Component Assessment
Apply Impact + Detection Matrix to each system component:

**Component Evaluation Template**:
1. **Data Corruption Risk?** (Components with write operations)
2. **Logic Complexity?** (Transformation algorithms, validation rules)
3. **Usage Frequency?** (Core vs edge case workflows)
4. **Integration Criticality?** (Cross-component dependencies)

### Test Strategy Selection

**High-Risk Strategy (Comprehensive Testing)**:
- Primary: E2E tests for full system validation
- Secondary: Integration tests for component interactions
- Comprehensive: Unit tests for all public methods and edge cases

**Three-Tier Strategy**: Reference `../strategy/risk-based-testing.md` for complete strategy mapping:
- **High-Risk**: Comprehensive testing (E2E primary, integration secondary, unit comprehensive)
- **Complex**: Good unit coverage (all public methods, typical usage patterns, basic errors)
- **Simple**: Smoke tests (component loads, basic functionality works)

### Mock Boundary Decisions

Apply external/internal boundary decisions per `../strategy/mock-boundaries.md` patterns:
- **Mock**: External/uncontrolled dependencies (APIs, networks, external systems)
- **Test**: Internal/controlled systems (pipeline logic, configuration, local operations)

## Decision Rules

### Coverage Requirements
Reference `../strategy/risk-based-testing.md` for complete three-tier coverage standards:
- **High-risk components** (5-10%): Mandatory comprehensive test coverage
- **Complex components** (10-15%): Good unit coverage for confident refactoring
- **Simple components** (75-85%): Smoke tests for breakage detection

### Uncertainty Handling
If risk classification unclear, raise to user for clarification

### Confidence Goals
- **Extremely confident**: No massive risk exposure (high-risk scenarios covered)
- **Quite confident**: Code is working correctly (development aids in place)

## Quality Metrics
Success is measured by **risk mitigation, not coverage percentages**. The system is adequately tested when all high-risk failure modes have explicit test coverage.

## Application During Refactor

These criteria templates guide **component-by-component** risk assessment during test refactor implementation, not pre-emptive classification.
