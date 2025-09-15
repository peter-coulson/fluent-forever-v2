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

### Low-Risk Categories (Development Aids)
Immediate detection OR minimal impact:
- Pipeline errors with clear messages
- Media provider failures (visible)
- Sync issues (detectable)
- Performance degradation (observable)
- Transient network issues (retry-able)

**Testing Approach**: Permitted but not required - useful for development velocity but should never block deployment.

### High-Risk Component Assessment
Apply Impact + Detection Matrix to each system component:

**Component Evaluation Template**:
1. **Data Corruption Risk?** (Components with write operations)
2. **Logic Complexity?** (Transformation algorithms, validation rules)
3. **Usage Frequency?** (Core vs edge case workflows)
4. **Integration Criticality?** (Cross-component dependencies)

### Test Strategy Selection

**High-Risk Strategy (Inverted Pyramid)**:
- Primary: E2E tests for full system validation
- Secondary: Integration tests for component interactions
- Minimal: Unit tests for complex transformation logic only

**Low-Risk Strategy (Traditional Pyramid)**:
- Primary: Unit tests for development velocity
- Optional: Integration/E2E when convenient for debugging

### Mock Boundary Decisions

**Mock External/Uncontrolled**:
- Provider APIs (Forvo, ElevenLabs, OpenAI)
- Network dependencies
- External file systems

**Test Internal/Controlled**:
- Pipeline execution logic
- Configuration processing
- Local data operations

## Decision Rules

### Coverage Requirements
- **High-risk scenarios**: Mandatory test coverage before production
- **Low-risk scenarios**: Permitted but not required - developer convenience tool

### Low-Risk Testing Enforcement
- **No coverage metrics** that include low-risk areas
- **No CI failures** for low-risk test gaps
- **No code review requirements** for low-risk test coverage
- **No refactor blockers** due to missing low-risk tests

### Uncertainty Handling
If risk classification unclear, raise to user for clarification

### Confidence Goals
- **Extremely confident**: No massive risk exposure (high-risk scenarios covered)
- **Quite confident**: Code is working correctly (development aids in place)

## Quality Metrics
Success is measured by **risk mitigation, not coverage percentages**. The system is adequately tested when all high-risk failure modes have explicit test coverage.

## Application During Refactor

These criteria templates guide **component-by-component** risk assessment during test refactor implementation, not pre-emptive classification.
