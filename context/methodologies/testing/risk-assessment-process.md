# Risk Assessment Process

## Purpose
Apply risk-based testing criteria to internal components only, excluding boundary components.

## Risk Classification (Internal Components Only)

**Reference**: Apply `../strategy/risk-based-testing.md` three-tier framework:

### High-Risk Assessment
Apply `../meta/decision-framework.md` criteria:
- Data corruption or silent failure risk
- Critical workflow dependency
- Difficult-to-debug failure modes
- High integration complexity

### Complex Assessment
- Algorithm complexity requiring edge case validation
- Business logic transformation patterns
- Validation rule engines
- Processing logic sophistication

### Simple Assessment
- Basic infrastructure with visible failures
- Utility functions with clear error patterns
- Simple orchestration logic

## Application Process

1. **Component-by-Component Review**: Apply criteria to each internal component
2. **Risk Scenario Documentation**: Record specific failure modes
3. **Classification Assignment**: Map to High-risk/Complex/Simple category
4. **Boundary Risk Analysis**: Document interface interaction risks

## Output Format

**Component Risk Map**: Internal component → risk category mapping
**Risk Scenarios**: Specific failure modes per component
**Boundary Interactions**: Interface risks between internal and external components

## Framework References
- **Risk Criteria**: `../strategy/risk-based-testing.md` - Classification guidelines
- **Decision Framework**: `../meta/decision-framework.md` - Assessment criteria
