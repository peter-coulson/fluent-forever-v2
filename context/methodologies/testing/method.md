# Sequential Test Planning Framework

## Purpose
Orchestrated process for applying risk-based testing principles to any implementation specification with absolute boundary respect.

## Required Inputs
1. **Implementation Specification**: Planning document defining what to build
2. **Boundary Component Definitions**: Components external to implementation scope
3. **Test Type Exclusions**: Optional filter (e.g., "no unit tests")

## Framework Process

**TodoWrite Requirements:** Create 8 todos (6 consolidated phases + 2 critical individual steps). Steps 2 and 3 MUST be individual todos to ensure deep architectural understanding. Quality gates prevent progression until outcomes are achieved.

### Step 1: Context Discovery Phase
**Systematic Architectural Foundation** (Apply `stages/1-context-discovery-framework.md`):
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
**Framework Dependencies** (Apply `stages/4-methodology-foundation.md`):
- Read supporting testing framework files from context/testing/strategy/
- Follow one level deep for referenced documents and validate methodology completeness
- **Gate**: All supporting frameworks understood before proceeding

### Step 5: Boundary & Scope Analysis Phase
**Critical Validation** (Apply `stages/5-scope-boundary-rules.md`):
- Identify external vs internal components from user specification
- Validate interface contracts and confirm scope understanding
- **CONSTRAINT**: Never test external component internals regardless of risk level
- **Gate**: Clear boundary definition before risk assessment

### Step 6: Risk Assessment Phase
**Component Analysis** (Apply `stages/6-risk-assessment-process.md`):
- Apply risk classification to internal components only (High-risk/Complex/Simple)
- Document specific failure modes and interface interaction risks
- **CONSTRAINT**: Validate scope before assessment, fail fast on unclear interface contracts
- **Gate**: Complete risk mapping before test design

### Step 7: Test Design Phase
**Test Requirements** (Apply `stages/7-critical-test-patterns.md`):
- Map risk classifications to test types (High-risk→E2E, Complex→Unit, Simple→Smoke)
- Design interface testing, consolidate scenarios, create concrete file paths
- **Gate**: Comprehensive test strategy before deliverable creation

### Step 8: Deliverable Creation Phase
**Implementation Plan** (Apply `stages/8-deliverable-creation.md`):
- Generate comprehensive testing_plan_v6.md with all step outcomes
- Include component mappings, risk assessments, and concrete test specifications
- **Gate**: Complete deliverable ready for implementation

## Framework References
- **Context Discovery**: `stages/1-context-discovery-framework.md` - Systematic architectural foundation
- **Methodology Foundation**: `stages/4-methodology-foundation.md` - Framework dependency validation
- **Boundary Rules**: `stages/5-scope-boundary-rules.md` - Scope definition and validation
- **Risk Process**: `stages/6-risk-assessment-process.md` - Internal component risk classification
- **Test Patterns**: `stages/7-critical-test-patterns.md` - Risk to test type mapping
- **Deliverable Creation**: `stages/8-deliverable-creation.md` - Implementation plan generation
