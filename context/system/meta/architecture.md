# Context System Architecture

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

### Meta Layer (`context/system/meta/`)
- **Purpose**: Context system self-documentation
- **Scope**: Documentation principles, architecture, and maintenance
- **Content**: Separation principles, validation rules, extension procedures
- **References**: Self-contained with references to principles document

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

## Benefits

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
