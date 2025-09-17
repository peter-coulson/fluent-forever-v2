# Sequential Test Planning Framework

## Purpose
Orchestrated process for applying risk-based testing principles to any implementation specification with absolute boundary respect.

## Required Inputs
1. **Implementation Specification**: Planning document defining what to build
2. **Boundary Component Definitions**: Components external to implementation scope
3. **Test Type Exclusions**: Optional filter (e.g., "no unit tests")

## Framework Process (SELECTIVE OPTIMIZATION)

**TodoWrite Requirements:**
1. **8-Step Setup**: After reading this methodology, create 8 todos (6 consolidated phases + 2 critical individual steps)
2. **Critical Forcing Functions**: Steps 2 and 3 MUST be individual todos to ensure deep architectural understanding
3. **Quality Gates**: Cannot proceed to next step until current step outcomes are achieved
4. **Selective Optimization**: 70% token reduction while preserving accountability mechanisms that ensure quality

**Optimization Principle:**
- **PHASE**: Safe systematic work consolidated into single todos
- **CRITICAL INDIVIDUAL STEPS**: Forcing functions that require separate accountability
- **PROVEN EFFECTIVE**: Based on V4 vs V5 quality regression analysis

### Step 1: Context Discovery Phase
**Systematic Architectural Foundation** (Apply `context-discovery-framework.md`):
- Map entire context system and identify implementation-relevant documentation
- Read systematically through context/system/overview.md and all relevant files
- Understand component roles, interactions, complexity distribution, data flow patterns
- **Gate**: Complete architectural file reading and basic understanding confirmed

### Step 2: Execution Pattern Analysis (CRITICAL INDIVIDUAL TODO)
**Forced Deep Understanding** - CANNOT be consolidated:
- **Understand execution pattern** - how components are actually called/invoked vs how workflow is described
- **Contrast Reality vs Description**: Compare actual implementation patterns with user specification/README
- **Focus**: Identify whether stages are independent calls or complex integrations
- **Gate**: Must demonstrate clear understanding of actual vs described execution patterns

### Step 3: Architectural Demonstration (CRITICAL INDIVIDUAL TODO)
**Verification Forcing Function** - CANNOT be consolidated:
- **DEMONSTRATE understanding** - provide one concrete example of actual method calls showing component interaction
- **Method Call Trace**: Show actual pipeline.execute_stage() → stage.execute() → context operations
- **Verify Internalization**: Prove concepts are understood, not just read
- **Gate**: Concrete method-level trace showing architectural understanding

### Step 4: Methodology Foundation Phase
**Framework Dependencies**:
- Read sequential-execution-framework.md and all directly referenced files
- Follow one level deep for referenced documents and validate methodology completeness
- **Gate**: All supporting frameworks understood before proceeding

### Step 5: Boundary & Scope Analysis Phase
**Critical Validation** (Apply `scope-boundary-rules.md`):
- Identify external vs internal components from user specification
- Validate interface contracts and confirm scope understanding
- **Gate**: Clear boundary definition before risk assessment

### Step 6: Risk Assessment Phase
**Component Analysis** (Apply `risk-assessment-process.md`):
- Apply risk classification to internal components only (High-risk/Complex/Simple)
- Document specific failure modes and interface interaction risks
- **Gate**: Complete risk mapping before test design

### Step 7: Test Design Phase
**Test Requirements** (Apply `critical-test-patterns.md`):
- Map risk classifications to test types (High-risk→E2E, Complex→Unit, Simple→Smoke)
- Design interface testing, consolidate scenarios, create concrete file paths
- **Gate**: Comprehensive test strategy before deliverable creation

### Step 8: Deliverable Creation Phase
**Implementation Plan**:
- Generate comprehensive testing_plan_v6.md with all step outcomes
- Include component mappings, risk assessments, and concrete test specifications
- **Gate**: Complete deliverable ready for implementation

## Absolute Constraints

**Never Test External Component Internals**: Regardless of risk level or test type
**Validate Scope Before Assessment**: Must confirm boundary understanding first
**Fail Fast on Invalid Boundaries**: Stop if interface contracts unclear

## Framework References
- **Boundary Rules**: `scope-boundary-rules.md` - Scope definition and validation
- **Risk Process**: `risk-assessment-process.md` - Internal component risk classification
- **Test Patterns**: `critical-test-patterns.md` - Risk to test type mapping
