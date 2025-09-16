# Methodologies Overview

Structured frameworks for systematic execution of complex tasks by LLMs and developers.

## Available Methodologies

### Testing Methodologies
Systematic approaches for test planning and execution:

- **Sequential Execution Framework**: `testing/sequential-execution-framework.md` - Risk-based test planning with boundary validation
- **Risk Assessment Process**: `testing/risk-assessment-process.md` - Component risk classification methodology
- **Critical Test Patterns**: `testing/critical-test-patterns.md` - Risk-to-test-type mapping framework
- **Scope Boundary Rules**: `testing/scope-boundary-rules.md` - Implementation scope validation

## Methodology Principles

### Structured Process
- **Clear Inputs**: Required information and prerequisites
- **Defined Steps**: Sequential execution with validation points
- **Explicit Constraints**: Boundaries and rules for proper execution
- **Measurable Outputs**: Specific deliverables and success criteria

### LLM Optimization
- **TodoWrite Integration**: Progress tracking for multi-step processes
- **Validation Checkpoints**: Explicit verification at each phase
- **Failure Modes**: Clear guidance for error conditions
- **Context Efficiency**: Minimal token usage while maintaining thoroughness

## Usage Patterns

### Framework Selection
Choose methodology based on task characteristics:
- **Testing Tasks**: Use testing methodologies for test planning and validation
- **Implementation Tasks**: (Future) Use implementation methodologies for code changes
- **Analysis Tasks**: (Future) Use analysis methodologies for codebase exploration

### Execution Guidelines
1. **Read Full Framework**: Understand complete process before starting
2. **Validate Inputs**: Ensure all required information is available
3. **Follow Sequence**: Execute steps in order with validation
4. **Track Progress**: Use TodoWrite for multi-step processes
5. **Document Results**: Record outcomes and lessons learned

## Extension Principles

### Adding New Methodologies
- Create domain-specific subdirectory (`implementation/`, `analysis/`)
- Follow existing token limits (400-600 tokens per file)
- Include clear inputs, steps, constraints, and outputs
- Update this overview with methodology description and navigation

### Framework Evolution
- Methodologies should be refined through actual usage
- Update based on execution experience and edge cases
- Maintain backward compatibility when possible
- Version significant changes with migration guidance
