# Testing Framework

## Overview

Risk-Based Testing (RBT) framework optimized for pipeline systems, emphasizing minimality and maintainability while ensuring confidence in critical system operations.

## Core Principles

### 1. Risk Assessment Framework

**High Risk (Mandatory Testing):**
- High impact AND difficult to detect
- **Specific Categories:**
  - Main database overwriting
  - Source data overwriting
  - Silent pipeline logic errors
  - Configuration drift
  - Uncontrolled resource consumption
  - Data validation bypass
  - Version compatibility breaks
  - State corruption

**Low Risk (Development Aids):**
- Immediate detection OR minimal impact
- **Testing Approach:** Permitted but not required - useful for development velocity but should never block deployment
- **Examples:** Pipeline errors with clear messages, media provider failures, sync issues, performance degradation, transient network issues

### 2. Testing Tool Strategy

**Tool-to-Risk Mapping:**
- **Unit Tests:** Transformation logic, edge cases, isolated component behavior
- **Integration Tests:** Component interactions, configuration handling, cross-system validation
- **E2E Tests:** Full pipeline validation, database operations, real-world scenarios

**High-Risk Testing (Inverted Pyramid):**
- **Primary:** E2E tests for full system validation
- **Secondary:** Integration tests for component interactions
- **Minimal:** Unit tests for complex transformation logic only

**Low-Risk Testing (Traditional Pyramid):**
- **Primary:** Unit tests for quick feedback during development
- **Optional:** Integration/E2E tests when convenient for debugging

**Stage-Level Testing (Risk-Assessed):**
- **High-Risk Stages** (database writes, data transformation, critical business logic): Integration tests mandatory
- **Medium-Risk Stages** (media generation, API calls): Unit tests preferred, integration optional
- **Low-Risk Stages** (logging, simple utilities): Minimal testing, focus on development aids

**Workflow-Level Testing (Priority-Based):**
- **Critical User Workflows**: E2E tests for most common/valuable stage combinations
- **Secondary Workflows**: E2E tests when convenient for debugging complex interactions
- **Ad-hoc Combinations**: No dedicated tests - rely on stage-level coverage

**One Test, Multiple Risks:**
Prefer comprehensive tests that validate multiple risk scenarios simultaneously over numerous single-purpose tests.

### 3. Mocking Strategy

**Mock External/Uncontrolled:**
- Provider APIs (Forvo, ElevenLabs, OpenAI)
- Network calls
- External file systems
- Time/date functions

**Test Internal/Controlled:**
- Internal databases
- Local file systems
- Configuration loading logic
- Pipeline transformation logic

**Reusability Approach:**
- Centralized mocks for common external services
- Per-test mocks for specific scenarios
- LLM discretion for implementation details

### 4. Development vs Production Testing

**Scaffolding Test Strategy:**
Bridge the gap between TDD development needs and minimal production testing through temporary comprehensive validation.

**Development Phase (TDD):**
- **Comprehensive E2E tests** for every major pathway during implementation
- **Over-testing acceptable** for LLM development velocity and confidence
- **Detailed validation** of transformation logic, error handling, edge cases
- **Quick bug identification** through extensive test coverage

**Production Transition:**
- **Consolidate** successful scaffolding tests into minimal high-risk coverage
- **Aggressive pruning** - delete tests that don't mitigate high-risk scenarios
- **Maintain** only essential risk-mitigation tests for long-term maintenance

**Key Insight:** Tests that help LLMs develop good code aren't necessarily the same tests that should live in the codebase long-term.

### 5. Decision Rules

**Coverage Requirements:**
- **High-risk scenarios:** Mandatory test coverage before production
- **Low-risk scenarios:** Permitted but not required - developer convenience tool

**Low-Risk Testing Enforcement:**
- **No coverage metrics** that include low-risk areas
- **No CI failures** for low-risk test gaps
- **No code review requirements** for low-risk test coverage
- **No refactor blockers** due to missing low-risk tests

**Uncertainty Handling:**
- If risk classification unclear, raise to user for clarification

**Confidence Goals:**
- **Extremely confident:** No massive risk exposure (high-risk scenarios covered)
- **Quite confident:** Code is working correctly (development aids in place)

## Implementation Guidelines

### Testing Priorities
1. **Risk Assessment per Component**: Evaluate each stage using detection difficulty + impact + usage frequency
2. **Graduated Testing Effort**: Match testing intensity to actual risk and development needs
3. **Critical Workflow Focus**: Prioritize E2E testing for most common/valuable stage combinations
4. **Context Integration**: Test stage-to-stage data passing for critical workflows
5. Use real components for internal systems, mocks for external dependencies

### Stage Assessment Criteria
For each stage, evaluate:
1. **Data corruption risk?** (Database writes = high, logging = low)
2. **Logic complexity?** (Transformation algorithms = high, simple calls = low)
3. **Usage frequency?** (Core vocabulary processing = high, edge cases = low)
4. **Integration criticality?** (Context data dependencies, provider interactions)

### Maintenance Approach
- Minimal test count for long-term maintainability
- Regular audit to ensure tests remain aligned with risk assessment
- Remove tests that don't provide risk mitigation value

### Quality Metrics
Success is measured by risk mitigation, not coverage percentages. The system is adequately tested when all high-risk failure modes have explicit test coverage.
