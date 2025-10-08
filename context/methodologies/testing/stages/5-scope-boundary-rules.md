# Scope Boundary Rules

## Purpose
Define what is inside vs outside implementation scope to prevent testing duplication and maintain modular independence.

## Boundary Component Definition

**External to Implementation Scope**: Component will be implemented separately
- Test interface interactions only
- Never test internal component logic
- Component marked as boundary in user specification

**Internal to Implementation Scope**: Component within current implementation
- Apply full risk-based testing framework
- Test all internal logic and algorithms
- Component fully specified in current implementation plan

## Interface Contract Requirements

**Valid Boundary Component** must specify:
- Clear input/output method signatures
- Expected data formats and validation rules
- Error handling patterns at interface
- Dependencies and integration points

**Invalid Boundary**: Fail fast if contracts unclear
- Request boundary refinement from user
- Cannot proceed without clear interface definition
- Ambiguous responsibilities prevent clean separation

## Scope Application Rules

**External Boundary Components**:
- Test interface interactions between components only
- Validate data exchange at boundaries
- Test error propagation across interfaces
- Never test algorithms or logic within external component

**Internal Components**:
- Full testing responsibility within implementation scope
- Apply complete risk assessment process
- Test all internal interactions and dependencies

## Boundary Validation

Must explicitly confirm scope understanding:
1. List all external boundary components identified
2. List all internal components for testing
3. Confirm interface-only testing for external components
4. Validate no overlap with external component internals
