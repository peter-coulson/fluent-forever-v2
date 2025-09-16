# Context Discovery Framework

## Purpose
Understand required dependencies before applying implementation methodologies. Prevents implementation failures due to missing dependency knowledge.

## Entry Point
**Always begin**: `context/system/overview.md`

## Method
1. **Follow Navigation**: Use documented paths to find dependency information
2. **Focus on Dependencies**: Read only what's needed for implementation requirements
3. **Validate Understanding**: Confirm dependency knowledge is complete

## Success Criteria (Create Individual Todos for Each Item)
1. **Read context/system/overview.md first** (mandatory entry point)
2. **Follow navigation paths** relevant to implementation dependencies only
3. **Understand all required dependencies** and where they sit in the repository/context
4. **Understand component roles** and configuration of critical dependent components for this implementation
5. **Understand component interactions** - their interfaces, and interaction patterns
6. **Understand execution pattern** - how components are actually called/invoked vs how workflow is described
7. **Understand complexity distribution** - which components contain business logic vs orchestration logic
8. **Understand data flow pattern** - direct method calls vs event passing vs shared state vs handoffs
9. **Validate architectural assumptions** - confirm implementation approach matches actual system patterns
10. **DEMONSTRATE understanding** - provide one concrete example of actual method calls showing component interaction

## Mandatory Validation
You MUST confirm each checkbox above before proceeding to any other methodology step. If any criteria cannot be satisfied, stop and request architectural clarification.
