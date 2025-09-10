# Context System Design Plan

## Overview

This document outlines the design for a hierarchical context system optimized for Claude agents working on the Fluent Forever V2 Spanish learning system. The context system is designed to provide need-to-know information with minimal token usage while enabling efficient dynamic loading based on task requirements.

## Design Principles

### 1. Hierarchical & Need-to-Know Access
- Information organized in logical layers from general to specific
- Each level contains only what's necessary at that abstraction level
- Agents can load progressively deeper context as needed

### 2. Minimal Token Usage
- Each file focused on a single responsibility
- Concise, technical language without redundancy
- No duplicate information across files

### 3. Claude Agent Optimized
- Structure matches common agent workflows
- Clear entry points for different types of tasks
- Enables efficient context loading patterns

### 4. Single Responsibility Principle
- Each file has one clear, defined purpose
- Clear boundaries between different concerns
- Easy to maintain and update

### 5. DRY (Don't Repeat Yourself)
- Information appears in exactly one place
- Cross-references used instead of duplication
- Consistent terminology throughout

## System Architecture

### Root Entry Point
```
claude.md
```
Ultra-minimal entry point providing:
- Brief system purpose (1-2 sentences)
- Context system navigation guide
- Common entry points for different task types

### Context Directory Structure

```
context/
├── system/                    # System-level understanding
│   ├── overview.md           # High-level system purpose & architecture
│   ├── core-concepts.md      # Key abstractions (Pipeline, Stage, Provider, Context)
│   └── data-flow.md          # How data flows through the system
├── modules/                  # Module-specific details
│   ├── core/
│   │   ├── overview.md       # Core module purpose & key classes
│   │   ├── pipeline.md       # Pipeline system details
│   │   ├── stages.md         # Stage system details
│   │   ├── context.md        # Pipeline context details
│   │   └── config.md         # Configuration system
│   ├── cli/
│   │   ├── overview.md       # CLI structure & commands
│   │   ├── commands.md       # Command implementations
│   │   └── utils.md          # CLI utilities
│   ├── providers/
│   │   ├── overview.md       # Provider system architecture
│   │   ├── base.md           # Base provider interfaces
│   │   ├── implementations.md # Concrete provider implementations
│   │   └── registry.md       # Provider registry system
│   └── pipelines/
│       ├── overview.md       # Pipeline implementations overview
│       └── types.md          # Specific pipeline types (if any exist)
└── workflows/                # Task-oriented guides
    ├── common-tasks.md       # Common development & usage tasks
    ├── extending.md          # How to extend the system
    └── troubleshooting.md    # Common issues & solutions
```

## File Responsibilities

### Root Level
- **claude.md**: Minimal entry point, navigation guide, task routing

### System Level (`context/system/`)
- **overview.md**: System purpose, high-level architecture, key components
- **core-concepts.md**: Essential abstractions (Pipeline, Stage, Provider, Context)
- **data-flow.md**: How data moves through the system, execution flow

### Module Level (`context/modules/`)
Each module directory contains:
- **overview.md**: Module purpose, key classes, relationships
- **[specific].md**: Detailed information about specific components

### Workflow Level (`context/workflows/`)
- **common-tasks.md**: Frequent development operations
- **extending.md**: Adding new pipelines, stages, providers
- **troubleshooting.md**: Common issues and solutions

## Context Loading Patterns

### For Understanding System Architecture
```
claude.md → context/system/overview.md → context/system/core-concepts.md
```

### For Working with Specific Module
```
claude.md → context/modules/[module]/overview.md → context/modules/[module]/[specific].md
```

### For Implementation Tasks
```
claude.md → context/workflows/common-tasks.md → context/modules/[module]/
```

### For Debugging/Issues
```
claude.md → context/workflows/troubleshooting.md → context/modules/[module]/
```

## Token Optimization Strategies

### Content Guidelines
- Use bullet points and tables for dense information
- Avoid explanatory prose, focus on facts
- Include code locations as `file:line` references
- Use consistent terminology from the codebase

### File Size Targets
- **claude.md**: ~50-100 tokens
- **overview.md files**: ~200-300 tokens
- **specific detail files**: ~300-500 tokens
- **workflow files**: ~400-600 tokens

### Cross-Reference Pattern
Instead of duplicating information, use:
```markdown
For pipeline execution details, see: `context/modules/core/pipeline.md`
```

## System Context Overview

The Fluent Forever V2 system is a pipeline-based Spanish language learning tool that:

- Executes configurable learning workflows (vocabulary, conjugation)
- Integrates with external services (Anki, audio providers, image generation)
- Processes learning materials through staged pipelines
- Supports CLI-based interaction and automation
- Uses provider pattern for external service abstraction

### Key Components
- **Pipelines**: Learning workflow orchestrators
- **Stages**: Individual processing steps within pipelines
- **Providers**: External service integrations (Anki, audio, images, data)
- **Context**: Runtime state and configuration container
- **CLI**: Command-line interface for user interaction

## Validation Criteria

A well-designed context file should:
1. Be loadable by a Claude agent in <1 second
2. Contain only information relevant to its specific responsibility
3. Enable an agent to understand its scope without reading other files
4. Provide clear paths to deeper information when needed
5. Use <500 tokens for specific implementation details
6. Use <300 tokens for overview/navigation files

## Success Metrics

The context system succeeds when:
- Agents can understand system architecture in 2-3 file reads
- Module-specific work requires <5 context files
- New contributors can orient themselves using only context files
- Context loading time is <10% of total task time
- Zero duplication of core information across files
