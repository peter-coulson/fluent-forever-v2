# Context System Value Assessment Prompt

Analyze the provided chat transcript where context system updates were performed and extract insights to evaluate the utility and cost-effectiveness of maintaining the context system. Generate a comprehensive markdown report covering the following dimensions:

## Analysis Framework

### 1. Change Classification & Complexity
- **Change Type**: Categorize each change (structural, reference, feature, navigation)
- **Change Criticality**: Rate impact on system functionality (critical/important/nice-to-have)
- **Implementation Scope**: Lines of code changed, files affected, architectural impact
- **Context Update Scope**: Number of context files updated, token count changes

### 2. Time & Token Economics
- **Implementation Time**: Time spent on actual feature/refactor implementation
- **Context Maintenance Time**: Time spent updating context documentation
- **Context Maintenance Ratio**: Context time / Implementation time
- **Token Cost**: Estimated token usage for context updates vs implementation
- **Maintenance Burden**: Frequency and complexity of required updates per change type

### 3. Value Metrics
- **Navigation Efficiency**: How context system aided task completion
- **Knowledge Transfer**: Quality of context for understanding system architecture
- **Onboarding Value**: Effectiveness for new contributors/future reference
- **Technical Debt Prevention**: How context prevented misunderstandings or errors

### 4. Cost-Benefit Analysis by Change Type
For each identified change type, extract:
- **Maintenance overhead**: Time/tokens required for context updates
- **Value delivered**: Concrete benefits observed during implementation
- **ROI assessment**: Whether maintenance cost justified by utility
- **Optimization opportunities**: Areas where context could be streamlined

### 5. Critical Insights
- **High-value context patterns**: Which documentation provided the most utility
- **Low-value maintenance**: Updates that consumed resources without clear benefit
- **Breaking points**: Where context system became counterproductive
- **Scalability concerns**: How maintenance burden scales with codebase growth

### 6. Recommendations
Based on the analysis, provide:
- **Keep/Drop/Modify recommendations** for different context components
- **Automation opportunities** to reduce manual maintenance
- **Threshold guidelines** for when context updates are worthwhile
- **Streamlining strategies** to maintain value while reducing cost

## Output Requirements

Generate a structured markdown report with:
- Executive summary with key findings
- Detailed analysis for each framework dimension
- Data tables with quantitative metrics where available
- Specific recommendations with rationale
- Cost-benefit matrix by change type and criticality

Focus on actionable insights that will inform decisions about the context system's future role in the development workflow.
