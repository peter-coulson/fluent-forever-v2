# Testing Decision Framework

## Risk Classification Criteria

### High-Risk Component Assessment
Apply to each system component using TESTING_FRAMEWORK.md criteria:

**Impact + Detection Matrix**:
- **Database Operations**: High impact + difficult detection = MANDATORY testing
- **Data Transformation Logic**: High impact + difficult detection = MANDATORY testing
- **Silent Pipeline Failures**: High impact + difficult detection = MANDATORY testing
- **Configuration Processing**: Medium impact + difficult detection = MANDATORY testing

**Component Evaluation Template**:
1. **Data Corruption Risk?** (Pipeline stages with write operations)
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

## Application During Refactor

These criteria templates guide **component-by-component** risk assessment during test refactor implementation, not pre-emptive classification.
