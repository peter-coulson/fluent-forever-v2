# Testing Meta System Overview

## Purpose
Self-documenting framework for testing context maintenance, decision criteria, and boundary management.

## Meta System Components
- **Maintenance Models**: When and how testing context should be updated
- **Decision Frameworks**: Criteria templates for risk classification and test strategy selection
- **Boundary Definitions**: Clear inclusion/exclusion rules for testing context content
- **Update Triggers**: Change events that require testing context review

## Content Categories

### Framework-Stable Content
Derived from Risk-Based Testing principles - rarely changes:
- Risk assessment criteria templates
- Scaffolding lifecycle rules
- Mock boundary decision frameworks

### Implementation-Dynamic Content
Populated during component development - evolves with system:
- Specific component risk classifications
- Actual test organization patterns
- Workflow-specific testing approaches

## Navigation
- **Maintenance Rules**: `maintenance-model.md` - update timing and responsibility
- **Decision Criteria**: `decision-framework.md` - risk classification templates
- **Content Boundaries**: `boundaries.md` - inclusion/exclusion rules for testing context

## Implementation Structure Reference
Testing context implementation details populated during refactor:
- `../implementation/risk-mappings.md` - Component risk classifications
- `../implementation/organization-patterns.md` - Test structure patterns
- `../implementation/workflow-approaches.md` - System workflow testing strategies
