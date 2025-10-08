# Critical Test Patterns

## Purpose
Map risk classifications to test requirements, enforcing absolute boundary respect.

## Test Requirements by Risk Level

### High-Risk Components (Internal)
**Reference**: `../../testing/strategy/risk-based-testing.md` comprehensive strategy
- **E2E**: Complete workflow validation
- **Integration**: Component interaction testing
- **Unit**: All public methods and edge cases
- **Focus**: Data corruption and silent failure prevention

### Complex Components (Internal)
**Reference**: `../../testing/strategy/risk-based-testing.md` good unit coverage
- **Unit**: All public methods with typical patterns and basic errors
- **Integration**: Component interactions within scope
- **Focus**: Algorithm edge cases and refactoring support

### Simple Components (Internal)
**Reference**: `../../testing/strategy/risk-based-testing.md` smoke strategy
- **Smoke**: Component loads and basic functionality works
- **Focus**: Breakage detection with minimal maintenance

## External Boundary Testing (Regardless of Risk)

**Interface Testing Only**:
- Validate input/output contracts
- Test error propagation across boundaries
- Data format validation at interfaces
- **Never test internal algorithms or logic**

## Test Consolidation

**Multi-Risk Tests**: Single tests covering multiple risk scenarios
**Workflow Validation**: E2E tests spanning multiple components
**Interface Consolidation**: Combined boundary testing for related interfaces

## Implementation Resources

**Mock Strategy**: `../../testing/strategy/mock-boundaries.md` - External vs internal testing decisions
**Test Organization**: `../../testing/strategy/test-organization.md` - Directory structure, available fixtures (`tests/fixtures/`)

### Concrete File Specification Requirements
**Exact File Paths**: Map each test requirement to specific file paths to create/modify
**Fixture Reuse Mapping**: Identify which existing `tests/fixtures/` components to import vs create new
**Test Function Naming**: Define specific test function names and organization within files
**Directory Structure**: Specify complete folder hierarchy for new test files

## Framework References
- **Risk Strategies**: `../../testing/strategy/risk-based-testing.md` - Three-tier approaches
- **Test Consolidation**: `../../testing/strategy/test-consolidation.md` - Multi-risk patterns
