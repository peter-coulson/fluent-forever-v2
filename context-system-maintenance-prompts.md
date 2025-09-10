# Context System Maintenance Prompts

This document contains prompts for maintaining and updating the context system for Fluent Forever V2. These prompts ensure the context system remains accurate, up-to-date, and follows DRY and single responsibility principles.

## Reference Files for Context System Understanding

Before using any prompt below, familiarize yourself with these files:
- `context-system-plan.md` - Design principles, architecture, and token limits
- `context-system-implementation.md` - Implementation strategy and session structure
- `context-system-chat-prompts.md` - Detailed prompts for creating context files

## 1. Context System Validation Prompt

Use this prompt to validate all existing context files in one comprehensive review:

```
Perform a comprehensive validation of the context system for Fluent Forever V2. Review all files in the context/ directory and claude.md against these criteria:

**Design Principles Validation:**
1. **Token Count Compliance**: Verify each file meets target limits:
   - claude.md: 50-100 tokens
   - overview.md files: 200-300 tokens
   - specific detail files: 300-500 tokens
   - workflow files: 400-600 tokens

2. **Single Responsibility**: Each file has one clear, defined purpose with no scope creep

3. **DRY Compliance**: No duplicate information across files - information appears in exactly one place

4. **Cross-Reference Accuracy**: All file references are valid and point to correct locations

5. **Technical Accuracy**: Content matches current source code in src/

**Structural Validation:**
- Hierarchical navigation works correctly (claude.md → system → modules → workflows)
- All intended files from the implementation plan exist
- Directory structure matches the designed architecture
- File naming conventions are consistent

**Content Quality:**
- Technical language is concise and accurate
- file:line references are current and correct
- Terminology is consistent across all files
- Agent navigation patterns are clear and functional

**Output Requirements:**
- List files that fail validation criteria with specific issues
- Provide token counts for each file
- Identify any information duplication
- Suggest specific corrections needed
- Validate that the system enables efficient agent navigation

Create a validation report with pass/fail status for each file and actionable recommendations for any failures.
```

## 2. Context System Reference Guide Creation Prompt

Use this prompt to create modular reference documentation that follows the same hierarchical principles as the main context system:

```
Create a modular Context System Reference Guide that follows the same design principles as the main context system. Extract and compress the essential guidance from the planning documents into the context hierarchy.

**Before starting, read these source files:**
- context-system-plan.md (for design principles, architecture, token limits)
- context-system-implementation.md (for implementation strategy and procedures)
- context-system-chat-prompts.md (for quality standards and validation approaches)

**Create these reference files:**

1. **context/system/maintenance-overview.md** (~200-300 tokens)
   - Purpose of the maintenance system
   - Navigation guide to maintenance references
   - When to use each type of maintenance operation
   - Connection to main context system navigation

2. **context/system/design-principles.md** (~300-400 tokens)
   - Core principles: Hierarchical access, minimal tokens, single responsibility, DRY
   - Token limits for each file type with rationale
   - Quality standards and validation criteria
   - Common pitfalls and how to avoid them

3. **context/workflows/maintenance.md** (~400-500 tokens)
   - When context updates are needed (triggers and indicators)
   - Step-by-step process for updating context after code changes
   - Validation workflow for ensuring principle compliance
   - Decision tree for where new information belongs

**Integration Requirements:**
- Update claude.md to include navigation path to maintenance system
- Ensure maintenance references can be found through existing navigation
- Follow the same cross-reference patterns as main context system
- Maintain token efficiency and single responsibility principles

**Output Requirements:**
- Files that integrate seamlessly with existing context hierarchy
- Clear navigation from claude.md to maintenance guidance
- Self-contained reference information following DRY principles
- Enable quick access to maintenance guidance without large document overhead

The maintenance reference should feel like a natural extension of the existing context system, not a separate documentation layer.
```

## 3. Context System Update Prompt

Use this prompt to update the context system based on code changes provided in the chat:

```
Update the Fluent Forever V2 context system to reflect the code changes provided in this chat. Analyze the changes and update all affected context files while maintaining design principles.

**Before starting, read these context files:**
- context/system/design-principles.md (for quality standards and token limits)
- context/workflows/maintenance.md (for update procedures and decision trees)
- context/system/maintenance-overview.md (for navigation guidance)

**Required Information (provide in chat):**
- List of changed source files with brief description of changes
- Type of changes: new features, modifications, removals, or refactoring
- Any new external dependencies or integrations

**Update Process:**

1. **Impact Analysis**
   - Identify which context files need updates based on provided changes
   - Determine if new context files are needed or if existing files should be removed
   - Map source file changes to specific context file sections

2. **Context Updates**
   - Update affected context files to reflect source code changes
   - Add context for new features following established file structure
   - Remove or archive context for deprecated features
   - Ensure all file:line references remain accurate
   - Maintain token count limits for each file type

3. **Integration Validation**
   - Verify all cross-references remain valid after updates
   - Update navigation paths if file structure changed
   - Ensure hierarchical access patterns still function
   - Test that claude.md navigation reaches all updated content

4. **Quality Assurance**
   - Validate against design principles from context/system/design-principles.md
   - Check for information duplication across files
   - Verify single responsibility is maintained for each file
   - Confirm technical accuracy matches current source code

**Output Requirements:**
- List of context files modified with change summaries
- Updated token counts for all modified files
- Validation report confirming design principle compliance
- Any new navigation paths added to claude.md or overview files

This single prompt handles all types of context updates (additions, modifications, removals) based on the specific changes provided in the chat context.
```

## 4. Context System Health Check and Validation Prompt

Use this prompt to perform comprehensive health checks and validation of the context system:

```
Perform a comprehensive health check and validation of the Fluent Forever V2 context system. This audit ensures the system maintains efficiency, follows design principles, and accurately reflects the current source code.

**Before starting, read these context files:**
- context/system/design-principles.md (for validation criteria and token limits)
- context/system/maintenance-overview.md (for system structure expectations)

**Health Check Areas:**

1. **Source Code Accuracy Validation**
   - Compare all context descriptions against current source code in src/
   - Verify all file:line references are current and correct
   - Check that technical descriptions match actual implementations
   - Identify any deprecated or outdated information
   - Validate that new features in src/ have corresponding context

2. **Design Principle Compliance**
   - Measure token counts for each file against targets:
     * claude.md: 50-100 tokens
     * overview.md files: 200-300 tokens
     * detail files: 300-500 tokens
     * workflow files: 400-600 tokens
   - Verify single responsibility adherence for each file
   - Check for information duplication across files
   - Validate cross-reference accuracy and efficiency

3. **System Efficiency Analysis**
   - Calculate total token usage for common navigation paths
   - Identify files exceeding token limits and optimization opportunities
   - Assess context loading patterns for agent efficiency
   - Find redundant information that could be cross-referenced instead

4. **Structural Integrity Check**
   - Verify hierarchical navigation works from claude.md through all levels
   - Confirm all expected files from the implementation plan exist
   - Check that directory structure matches designed architecture
   - Validate that agents can efficiently find information for common tasks

**Output Requirements:**
- Health score (1-10) for each major area with specific justification
- Detailed list of files failing validation with specific issues
- Token count report for all files with target compliance status
- Source code accuracy report highlighting any mismatches
- Prioritized action plan for addressing critical issues
- Efficiency recommendations for token optimization

This comprehensive audit ensures the context system remains effective, accurate, and efficient for Claude agents.
```

## Usage Instructions

1. **Step 1**: Use prompt #1 to validate existing context files after initial implementation
2. **Step 2**: Use prompt #2 to create modular reference documentation integrated with the main context system
3. **Step 3**: Use prompt #3 to update context files when code changes occur (provide change details in chat)
4. **Step 4**: Use prompt #4 to perform comprehensive health checks and validation against source code

**Prompt Responsibilities:**
- **Prompt 1**: Initial validation after context system creation
- **Prompt 2**: Create integrated reference documentation (replaces original planning files)
- **Prompt 3**: Handle all context updates based on code changes
- **Prompt 4**: Health checks, efficiency analysis, and source code validation

This approach ensures each prompt has a single, clear responsibility while following DRY and modular principles. The maintenance system integrates seamlessly with the existing context hierarchy.
