# Testing Context Maintenance Model

## Update Timing Strategy

### Framework-Stable Content (Rare Updates)
**When**: TESTING_FRAMEWORK.md principles change or major architectural shifts
**Content**: Risk assessment criteria, scaffolding lifecycle rules, mock boundary frameworks
**Trigger**: Framework document updates, system architecture changes
**Responsibility**: Context system maintainer

### Implementation-Dynamic Content (Regular Updates)
**When**: During test refactor implementation, component development, post-refactor learnings
**Content**: Component risk mappings, test organization patterns, workflow-specific approaches
**Trigger**: Component changes, new risk scenarios discovered, test structure evolution
**Responsibility**: Developer implementing tests

## Update Procedures

### During Test Refactor
1. **Component Assessment**: Apply decision framework criteria to each component as encountered
2. **Pattern Documentation**: Record test organization patterns that emerge
3. **Risk Discovery**: Update risk mappings when new scenarios identified
4. **Consolidation**: Document successful scaffolding → production transitions

### Post-Refactor Maintenance
1. **Quarterly Reviews**: Validate risk mappings against system evolution
2. **Change Triggers**: Update when components undergo architectural changes
3. **Pattern Updates**: Refine testing approaches based on maintenance experience

## Staleness Detection

**Framework Misalignment**: Testing context contradicts TESTING_FRAMEWORK.md principles
**Implementation Divergence**: Documented patterns don't match actual test structure
**Risk Classification Drift**: Components classified differently than testing approach suggests

## Content Lifecycle

**Development Phase**: Comprehensive documentation during scaffolding
**Production Phase**: Minimal essential guidance aligned with risk-based principles
