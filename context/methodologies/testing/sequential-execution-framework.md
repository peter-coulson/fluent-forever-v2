# Sequential Test Planning Framework

## Purpose
Orchestrated process for applying risk-based testing principles to any implementation specification with absolute boundary respect.

## Required Inputs
1. **Implementation Specification**: Planning document defining what to build
2. **Boundary Component Definitions**: Components external to implementation scope
3. **Test Type Exclusions**: Optional filter (e.g., "no unit tests")

## Framework Process (Use TodoWrite for validation)

### Step 0: Methodology Preparation
**Framework Dependencies** (Apply before any analysis):
1. **Read All Referenced Files**: Read sequential-execution-framework.md and all files it directly references
2. **Follow One Level Deep**: Read any files referenced by those direct reference files (one level only)
3. **Validate Complete Methodology**: Confirm all supporting documents loaded before proceeding
4. **Document File Dependencies**: List all methodology files loaded for transparency

### Step 1: Boundary Validation
**Critical Validation** (Apply `scope-boundary-rules.md`):
1. **List External Components**: Identify all boundary components from user input
2. **List Internal Components**: Identify components within implementation scope
3. **Validate Interface Contracts**: Confirm external components have clear interfaces
4. **Confirm Scope Understanding**: Explicitly state what will/won't be tested

### Step 2: Risk Assessment
**Component Analysis** (Apply `risk-assessment-process.md`):
1. **Internal Components Only**: Apply risk classification to internal scope only
2. **High-risk/Complex/Simple**: Categorize each internal component
3. **Document Risk Scenarios**: Record specific failure modes per component
4. **Interface Risk Analysis**: Identify boundary interaction risks

### Step 3: Critical Test Design
**Test Requirements** (Apply `critical-test-patterns.md`):
1. **Map Risk to Tests**: High-risk→E2E, Complex→Unit, Simple→Smoke
2. **Interface Testing Only**: External components get interface testing only
3. **Consolidate Tests**: Combine overlapping risk scenarios
4. **Resource Planning**: Map test requirements to concrete file paths, fixture reuse, and directory structure
5. **Apply Test Exclusions**: Remove excluded test types from requirements

## Absolute Constraints

**Never Test External Component Internals**: Regardless of risk level or test type
**Validate Scope Before Assessment**: Must confirm boundary understanding first
**Fail Fast on Invalid Boundaries**: Stop if interface contracts unclear

## Framework References
- **Boundary Rules**: `scope-boundary-rules.md` - Scope definition and validation
- **Risk Process**: `risk-assessment-process.md` - Internal component risk classification
- **Test Patterns**: `critical-test-patterns.md` - Risk to test type mapping
