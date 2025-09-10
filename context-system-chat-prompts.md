# Context System Chat Prompts

## Overview

This document contains specialized prompts for each chat session in the context system implementation. Each prompt is designed to create focused, high-quality context files that follow the system design principles.

## Common Context for All Chats

Before using any prompt below, provide this common context:

```
I'm implementing a hierarchical context system for Claude agents working on the Fluent Forever V2 Spanish learning system. Please read these planning documents first:

1. context-system-plan.md - System design and principles
2. context-system-implementation.md - Implementation strategy

Key principles:
- Minimal token usage (<500 tokens for implementation details, <300 for overviews)
- Single responsibility per file
- Technical, concise language
- Include file:line references where relevant
- No duplication across files
- Use bullet points and tables for dense information
```

---

## Chat 1: Foundation & System Architecture

### Preparation Files
Provide access to:
- `src/core/pipeline.py`
- `src/core/stages.py`
- `src/core/context.py`
- `src/core/config.py`
- `src/cli/commands/run_command.py`
- `src/providers/base/data_provider.py`

### Prompt
```
Create the foundation context files for the Fluent Forever V2 system. This system is a pipeline-based Spanish language learning tool that processes learning materials through configurable stages and integrates with external services like Anki.

Based on the provided source code, create these 4 files with strict adherence to token limits:

1. **claude.md** (~50-100 tokens)
   - Ultra-minimal entry point
   - 1-2 sentence system description
   - Navigation guide for common task types
   - No implementation details

2. **context/system/overview.md** (~200-300 tokens)
   - System purpose and high-level architecture
   - Key components: pipelines, stages, providers, CLI
   - Learning workflow focus (vocabulary, conjugation)
   - External integrations overview

3. **context/system/core-concepts.md** (~200-300 tokens)
   - Essential abstractions: Pipeline, Stage, Provider, Context
   - How these concepts relate to each other
   - Key interfaces and responsibilities
   - Reference specific files where concepts are defined

4. **context/system/data-flow.md** (~200-300 tokens)
   - How data moves through the system
   - Execution flow from CLI command to completion
   - Context management throughout pipeline execution
   - Provider interaction patterns

Focus on:
- Technical accuracy based on source code analysis
- Clear conceptual understanding for agents
- Efficient navigation patterns
- No redundant information between files

Each file should enable a Claude agent to understand its scope without reading other files, while providing clear paths to deeper information when needed.
```

---

## Chat 2: Core Module Deep Dive

### Preparation Files
Provide access to:
- `src/core/` (entire directory)
- Context files from Chat 1 (if completed)

### Prompt
```
Create comprehensive context documentation for the core module of the Fluent Forever V2 system. The core module contains the fundamental abstractions that power the entire system.

Analyze the provided source code and create these 5 files:

1. **context/modules/core/overview.md** (~200-300 tokens)
   - Core module purpose and scope
   - Key classes and their relationships
   - How core components work together
   - Entry points for different types of work

2. **context/modules/core/pipeline.md** (~300-500 tokens)
   - Pipeline abstract base class and interface
   - Pipeline execution lifecycle
   - Stage management and dependency handling
   - Context validation and error handling
   - Key methods and their purposes

3. **context/modules/core/stages.md** (~300-500 tokens)
   - Stage abstract base class and interface
   - Stage execution model and lifecycle
   - StageResult class and status types
   - Dependencies and validation patterns
   - How to implement new stages

4. **context/modules/core/context.md** (~300-500 tokens)
   - PipelineContext class and its role
   - Context data management and lifecycle
   - How context flows through pipeline execution
   - Context validation and state tracking

5. **context/modules/core/config.md** (~300-500 tokens)
   - Configuration system architecture
   - Environment variable substitution
   - Provider configuration patterns
   - Configuration loading and validation
   - File structure and access patterns

Requirements:
- Include specific file:line references for key concepts
- Focus on implementation patterns and interfaces
- Explain how components interact
- Provide clear guidance for extending the system
- Use technical language appropriate for developers
- Ensure each file serves a distinct purpose

These files should enable a developer to understand how to work with the core abstractions without needing to read the source code first.
```

---

## Chat 3: Provider System Analysis

### Preparation Files
Provide access to:
- `src/providers/` (entire directory)
- `src/core/registry.py`
- Context files from Chat 1 (if completed)

### Prompt
```
Create detailed context documentation for the provider system of the Fluent Forever V2 system. The provider system implements pluggable external service integrations using abstract base classes and a registry pattern.

Analyze the provided source code and create these 4 files:

1. **context/modules/providers/overview.md** (~200-300 tokens)
   - Provider system architecture and purpose
   - Types of providers: data, audio, image, sync
   - Registry pattern and factory approach
   - How providers integrate with pipelines

2. **context/modules/providers/base.md** (~300-500 tokens)
   - Abstract base classes for each provider type
   - Common interfaces and methods
   - Provider lifecycle and initialization
   - Error handling patterns
   - How to implement new provider types

3. **context/modules/providers/implementations.md** (~400-500 tokens)
   - Concrete provider implementations
   - External service integrations (Anki, Forvo, OpenAI, etc.)
   - Configuration requirements for each provider
   - API patterns and authentication
   - Data formats and transformations

4. **context/modules/providers/registry.md** (~300-400 tokens)
   - Provider registry system
   - Registration and lookup patterns
   - Default provider handling
   - Configuration-based provider selection
   - Factory methods and instantiation

Focus on:
- Abstract interfaces and implementation patterns
- External service integration approaches
- Configuration and setup requirements
- How providers are selected and used at runtime
- Extension patterns for new providers

Include specific file:line references for key interfaces. These files should help developers understand how to add new external service integrations to the system.
```

---

## Chat 4: CLI & Pipeline Implementations

### Preparation Files
Provide access to:
- `src/cli/` (entire directory)
- `src/pipelines/` (entire directory, if it exists)
- Any concrete pipeline implementations found in codebase
- Context files from Chat 1 & 2 (if completed)

### Prompt
```
Create context documentation for the CLI interface and pipeline implementations of the Fluent Forever V2 system. The CLI provides the primary user interface, while specific pipeline implementations define learning workflows.

Analyze the provided source code and create these 5 files:

1. **context/modules/cli/overview.md** (~200-300 tokens)
   - CLI architecture and command structure
   - Main commands and their purposes
   - Integration with pipeline system
   - User interaction patterns

2. **context/modules/cli/commands.md** (~300-500 tokens)
   - Command implementations (run, info, list)
   - Argument parsing and validation
   - Context creation and pipeline execution
   - Error handling and user feedback
   - Dry-run functionality

3. **context/modules/cli/utils.md** (~200-300 tokens)
   - CLI utility functions and helpers
   - Output formatting and user feedback
   - Validation helpers
   - Common CLI operations

4. **context/modules/pipelines/overview.md** (~200-300 tokens)
   - Pipeline implementation structure
   - Current pipeline types (if any exist)
   - Learning workflow patterns
   - How pipelines define stages and data flow

5. **context/modules/pipelines/types.md** (~300-400 tokens)
   - Specific pipeline implementations found
   - Vocabulary, conjugation, or other learning pipelines
   - Stage definitions for each pipeline type
   - Data requirements and outputs
   - Anki integration patterns

Note: If no concrete pipeline implementations exist in src/pipelines/, focus files 4-5 on the pipeline patterns evident in the existing code and how new pipelines should be structured.

Requirements:
- Include command-line usage patterns
- Document argument structures and validation
- Show how CLI integrates with core system
- Provide guidance for adding new commands
- Include file:line references for key implementations

These files should enable understanding of user interaction patterns and guide creation of new learning workflows.
```

---

## Chat 5: Workflow & Operational Context

### Preparation Files
Provide access to:
- All source code files
- Context files from previous chats (if completed)
- Any existing test files
- Build/config files (package.json, requirements.txt, etc.)

### Prompt
```
Create workflow-oriented context documentation that helps developers and users accomplish common tasks with the Fluent Forever V2 system. These files should be practical guides that reference the technical context from previous chats.

Create these 3 task-oriented files:

1. **context/workflows/common-tasks.md** (~400-600 tokens)
   - Running existing pipelines and stages
   - Adding new learning content (vocabulary, conjugations)
   - Configuring providers (Anki, audio, images)
   - Testing and validation workflows
   - Debugging pipeline execution
   - Configuration file setup

2. **context/workflows/extending.md** (~400-600 tokens)
   - How to add new pipeline types
   - Implementing new stage types
   - Creating new provider integrations
   - Extending CLI with new commands
   - Configuration patterns for new features
   - Testing new components

3. **context/workflows/troubleshooting.md** (~400-600 tokens)
   - Common error patterns and solutions
   - Configuration issues and fixes
   - Provider integration problems
   - Pipeline execution failures
   - CLI usage problems
   - Performance considerations

Focus on:
- Practical step-by-step guidance
- Common use cases and scenarios
- Reference to relevant context files for details
- Code examples where helpful
- File locations and commands to run
- Integration patterns and best practices

These files should enable someone new to the codebase to become productive quickly by providing clear operational guidance while pointing to technical details in the module-specific context files.

Cross-reference the technical context files created in previous chats using the pattern: "For technical details, see: `context/modules/[module]/[file].md`"
```

---

## Quality Validation Prompt

Use this prompt after completing any chat session:

```
Review the context files you just created and validate them against these criteria:

1. **Token Count**: Check each file is within target limits
2. **Single Responsibility**: Each file has one clear purpose
3. **No Duplication**: Information appears in only one place
4. **Technical Accuracy**: Content matches source code analysis
5. **Agent Navigation**: Clear paths to related information
6. **Cross-References**: Proper references instead of duplication

For any files that don't meet these criteria, revise them to comply with the design principles. Provide a brief validation summary for each file created.
```

## Session Execution Notes

### Before Each Chat
1. Start fresh Claude Code session
2. Share common context and planning documents
3. Provide all specified preparation files
4. Use the exact prompt for that chat session

### After Each Chat
1. Run quality validation prompt
2. Check token counts on created files
3. Validate no information duplication
4. Ensure proper cross-referencing

### Between Sessions
1. Archive completed context files
2. Note any terminology or pattern decisions
3. Prepare file access for dependent sessions
4. Update any discovered requirements
