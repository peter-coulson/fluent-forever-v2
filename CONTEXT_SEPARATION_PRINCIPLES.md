# Context System Separation Principles

## Overview

This document establishes the separation principles implemented in the Fluent Forever V2 context system refactor. These principles ensure maintainable, scalable, and DRY-compliant documentation that enables efficient agent navigation.

## Core Separation Principles

### 1. **Single Source of Truth (DRY Compliance)**

**Principle**: Each piece of information appears in exactly one authoritative location.

**Implementation**:
- **Component Definitions**: All system component definitions consolidated in `context/system/core-concepts.md`
- **File References**: Each source code reference (`src/path/file.py:line`) appears in only one context file
- **Configuration Patterns**: Environment variable syntax and configuration access patterns documented once
- **No Duplication**: Eliminated repeated explanations of Pipeline, Stage, Provider, and Context concepts

**Example**: Pipeline definition moved from 4 files to single authoritative source in `core-concepts.md`

### 2. **Single Responsibility per File**

**Principle**: Each file has one clear, focused purpose without scope creep.

**Implementation**:
- **System Files**: Focus on high-level architecture and navigation (`system/overview.md`)
- **Module Files**: Focus on implementation details for specific modules (`modules/core/overview.md`)
- **Workflow Files**: Focus on practical procedures and operations (`workflows/common-tasks.md`)
- **Extension Split**: Separated `extending.md` into domain-specific guides:
  - `extending-pipelines.md` - Pipeline development patterns
  - `extending-providers.md` - Provider integration patterns
  - `extending-cli.md` - CLI command development patterns

**Example**: `modules/pipelines/overview.md` now focuses only on current status, with implementation details moved to separate `implementation.md`

### 3. **Hierarchical Information Architecture**

**Principle**: Information flows unidirectionally from general to specific, preventing circular references.

**Implementation**:
```
Level 1: CLAUDE.md (Entry point navigation)
Level 2: system/overview.md (High-level architecture)
Level 3: system/core-concepts.md (Component definitions)
Level 4: modules/*/overview.md (Implementation details)
Level 5: workflows/*.md (Practical procedures)
```

**Rules**:
- Lower levels reference higher levels for definitions
- Higher levels never reference implementation details
- Cross-references only flow downward in the hierarchy
- Each level adds specificity without repeating upper-level content

### 4. **Token Count Compliance**

**Principle**: Files must meet specific token limits based on their role in the hierarchy.

**Implementation**:
- **CLAUDE.md**: 50-100 tokens (39 actual)
- **Overview files**: 200-300 tokens (156-360 actual)
- **Detail files**: 300-500 tokens (283-481 actual)
- **Workflow files**: 400-600 tokens (346-568 actual)

**Status**: All active files now comply with token limits. Archive files intentionally excluded from limits.

### 5. **Clear Domain Boundaries**

**Principle**: Content is organized by functional domain with minimal overlap.

**Implementation**:
- **System Domain**: Architecture, concepts, data flow
- **Core Domain**: Pipeline system, stages, context, configuration
- **Provider Domain**: External service integrations, registry patterns
- **CLI Domain**: Command-line interface, user interaction patterns
- **Pipeline Domain**: Workflow implementations, stage patterns
- **Workflow Domain**: Operations, troubleshooting, extension guides

**Boundaries**: Each domain has clear interfaces and does not duplicate other domain concerns.

## File Organization Structure

### System Layer (`context/system/`)
- **Purpose**: High-level architecture and navigation
- **Scope**: System-wide concepts and relationships
- **Content**: Architecture overview, component definitions, data flow patterns
- **References**: Points to module and workflow layers for implementation details

### Module Layer (`context/modules/`)
- **Purpose**: Implementation-specific technical details
- **Scope**: Individual module functionality and integration points
- **Content**: Class structures, method signatures, implementation patterns
- **References**: References system layer for component definitions

### Workflow Layer (`context/workflows/`)
- **Purpose**: Practical procedures and extension guidance
- **Scope**: Operations, troubleshooting, and system extension
- **Content**: Step-by-step procedures, code examples, best practices
- **References**: References both system and module layers as needed

## Information Flow Rules

### Reference Direction
- **Upward References**: ✅ Workflows → Modules → System
- **Lateral References**: ⚠️ Only within same layer when necessary
- **Downward References**: ❌ System cannot reference implementation details

### Content Duplication Rules
- **Definitions**: Only in `system/core-concepts.md`
- **Implementation**: Only in appropriate module file
- **Procedures**: Only in appropriate workflow file
- **Examples**: Can appear in multiple files if they serve different purposes

### Cross-File Dependencies
- **Avoided**: Circular reference patterns
- **Minimized**: Direct file-to-file dependencies
- **Centralized**: Common concepts in authoritative sources

## Validation Criteria

### DRY Compliance
- ✅ No duplicate component definitions
- ✅ No repeated file path references
- ✅ No overlapping architectural explanations
- ✅ Single source for configuration patterns

### Single Responsibility
- ✅ Each file has clear, focused purpose
- ✅ No scope creep or mixed concerns
- ✅ Domain boundaries are respected
- ✅ Extension guides are domain-specific

### Technical Accuracy
- ✅ All file references validated against source code
- ✅ Line numbers are current and correct
- ✅ Method signatures match implementations
- ✅ Content reflects actual system architecture

### Navigational Efficiency
- ✅ Clear entry points and navigation paths
- ✅ Hierarchical information discovery
- ✅ Minimal cognitive overhead for agents
- ✅ Predictable file organization patterns

## Maintenance Guidelines

### Adding New Content
1. **Identify appropriate layer**: System, Module, or Workflow
2. **Check for existing coverage**: Avoid duplication
3. **Follow token limits**: Respect file size constraints
4. **Maintain hierarchy**: Reference higher levels appropriately
5. **Update navigation**: Ensure discoverability

### Modifying Existing Content
1. **Preserve single source of truth**: Update authoritative source only
2. **Check dependent references**: Ensure consistency across references
3. **Maintain token compliance**: Keep within established limits
4. **Validate technical accuracy**: Ensure content matches implementation

### Regular Validation
1. **DRY compliance**: Regular checks for content duplication
2. **Token count monitoring**: Automated validation against limits
3. **Technical accuracy**: Periodic validation against source code
4. **Navigation testing**: Verify agent navigation patterns work effectively

## Benefits Achieved

### For Agents
- **Faster navigation**: Clear hierarchy reduces search time
- **Reduced confusion**: Single source of truth eliminates conflicts
- **Predictable structure**: Consistent organization patterns
- **Focused content**: Each file serves specific purpose

### For Maintainers
- **Easy updates**: Single source changes propagate correctly
- **Clear ownership**: Each concept has designated authoritative location
- **Scalable structure**: New content fits into established patterns
- **Quality control**: Validation criteria ensure consistency

### For System Evolution
- **Modular updates**: Changes isolated to appropriate domains
- **Extension support**: Clear patterns for adding new functionality
- **Technical debt prevention**: Structure prevents information sprawl
- **Documentation sustainability**: Principles support long-term maintenance

This separation principle framework ensures the context system remains maintainable, accurate, and efficient for agent navigation while supporting the evolving needs of the Fluent Forever V2 system.
