# Context System Principles

## Core Separation Principles

### Single Source of Truth (DRY Compliance)
Each piece of information appears in exactly one authoritative location:
- **Component Definitions**: Consolidated in `context/system/core-concepts.md`
- **File References**: Each source code reference appears in only one context file
- **Configuration Patterns**: Environment variables and configuration documented once
- **No Duplication**: Eliminated repeated explanations across files

### Single Responsibility per File
Each file has one clear, focused purpose:
- **System Files**: High-level architecture and navigation
- **Module Files**: Implementation details for specific modules
- **Workflow Files**: Practical procedures and operations
- **Extension Guides**: Domain-specific development patterns

### Hierarchical Information Architecture
Information flows unidirectionally from general to specific:
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
- Cross-references only flow downward in hierarchy
- Each level adds specificity without repeating upper-level content

### Token Count Compliance
Files must meet specific token limits based on hierarchy role:
- **CLAUDE.md**: 50-100 tokens
- **Overview files**: 200-300 tokens
- **Detail files**: 300-500 tokens
- **Workflow files**: 400-600 tokens

### Clear Domain Boundaries
Content organized by functional domain with minimal overlap:
- **System**: Architecture, concepts, data flow
- **Core**: Pipeline system, stages, context, configuration
- **Provider**: External service integrations, registry patterns
- **CLI**: Command-line interface, user interaction patterns
- **Pipeline**: Workflow implementations, stage patterns
- **Workflow**: Operations, troubleshooting, extension guides
