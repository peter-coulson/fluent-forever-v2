# Context Discovery Framework

## Purpose
Understand required dependencies before applying implementation methodologies. Prevents implementation failures due to missing dependency knowledge.

## Entry Point
**Always begin**: `context/system/overview.md`

## Method
1. **Context System Survey**: Systematically map ALL available documentation before reading anything
2. **Relevance Filtering**: Identify which discovered files relate to implementation scope
3. **Systematic Reading**: Read all relevant files in dependency order
4. **Validate Understanding**: Confirm architectural knowledge is complete

## Success Criteria (Supporting Critical Forcing Functions)

**Step 1 Outcomes - Foundation for Critical Steps 2 & 3:**

**Discovery & Mapping**:
- Map entire context directory structure using systematic discovery (Glob patterns)
- Identify ALL implementation-relevant documentation before reading any files
- Create complete reading plan with dependency ordering based on discovered files

**Systematic Reading**:
- Read context/system/overview.md first (mandatory entry point)
- Read systematically through all identified relevant files
- Understand all required dependencies and where they sit in the repository/context

**Basic Architectural Understanding**:
- Understand component roles and configuration of critical dependent components
- Understand component interactions - their interfaces, and interaction patterns
- Understand complexity distribution - which components contain business logic vs orchestration logic
- Understand data flow pattern - direct method calls vs event passing vs shared state vs handoffs

**Foundation Validation**:
- Validate architectural assumptions - confirm implementation approach matches actual system patterns
- Prepare for critical individual analysis in Steps 2 & 3

## Mandatory Validation
You MUST achieve ALL outcomes above within Step 1 execution before proceeding to the CRITICAL individual Steps 2 & 3. If any outcomes cannot be satisfied, stop and request architectural clarification.

**Critical Success Factors**:
- Step 1 provides the foundation knowledge needed for Steps 2 & 3 to succeed
- Steps 2 & 3 are individual todos that force deep architectural understanding that cannot be achieved through consolidation
- The combination ensures both efficiency and quality
