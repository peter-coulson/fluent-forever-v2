---
description: "Autonomous context system update with comprehensive analysis and execution"
---

You have full autonomy to analyze and update the context system. Think systematically and execute comprehensively.

**Phase 1: System Understanding**
Read these meta files to understand the context system:
- `context/system/meta/principles.md` - DRY compliance, hierarchy, token limits, domain boundaries
- `context/system/meta/maintenance.md` - Layer identification, update procedures, validation steps
- `context/system/overview.md` - Current architecture overview
- `CLAUDE.md` - Navigation structure

**Phase 2: Comprehensive Change Analysis**
Analyze recent changes in `src/` and `tests/` to determine ALL needed update types:
- **Structural Changes**: New modules, architectural changes, component definitions → `core-concepts.md`, `data-flow.md`, module overviews
- **Reference Changes**: File moves, method signatures, line numbers → Technical references across context files
- **Feature Changes**: New workflows, CLI commands, user-facing functionality → Workflow documentation
- **Navigation Changes**: Major additions requiring entry points → `CLAUDE.md` updates

Use the layer identification criteria from `maintenance.md` to categorize all changes upfront.

**Phase 3: Todo Planning**
Create a comprehensive TodoWrite list covering ALL identified change types. Break down into specific, actionable items following the maintenance procedures.

**Phase 4: Systematic Execution**
Execute all updates following your todo list:
- Maintain DRY compliance and token limits per meta documentation
- Use `grep -r` commands as specified in maintenance procedures
- Validate file paths and technical accuracy
- Update navigation flows as needed
- Mark todos as completed immediately after finishing each task

**Authority**: Analyze once, plan comprehensively, execute systematically. Make autonomous decisions based on the evidence from src/ and tests/ changes using the context system's own guidance.
