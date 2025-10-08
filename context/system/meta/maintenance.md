# Context System Maintenance

## Adding New Content

### 1. Identify Appropriate Layer
- **System Layer**: High-level architecture, cross-cutting concepts, navigation
- **Module Layer**: Implementation details, technical specifications, integration points
- **Workflow Layer**: Procedures, troubleshooting, extension guides
- **Meta Layer**: Context system documentation, principles, maintenance procedures

### 2. Check for Existing Coverage
- Search existing files for related content using `grep -r "keyword" context/`
- Review authoritative sources in `system/core-concepts.md` for component definitions
- Check workflow files for existing procedures before creating new ones
- Validate no duplication exists across hierarchy levels

### 3. Follow Token Limits
- **Entry Points** (CLAUDE.md): 50-100 tokens
- **Overview Files**: 200-300 tokens
- **Detail Files**: 300-500 tokens
- **Workflow Files**: 400-600 tokens
- Use `wc -w filename.md` to verify token counts

### 4. Maintain Hierarchy
- Reference higher levels appropriately (workflows → modules → system)
- Never create downward references (system → implementation details)
- Use consistent navigation patterns: `file.md` → `detail1.md` → `detail2.md`
- Link to authoritative sources for definitions rather than duplicating

### 5. Update Navigation
- Add entry to `CLAUDE.md` if creating new major section
- Update parent overview files to include new content
- Ensure discoverability through existing navigation paths
- Test navigation flows from entry point to new content

## Modifying Existing Content

### 1. Preserve Single Source of Truth
- Identify authoritative source for information being changed
- Update only the authoritative source, never duplicates
- Propagate changes to dependent files only if they reference changed content
- Maintain consistency across all referencing files

### 2. Check Dependent References
- Search for files that reference modified content: `grep -r "modified_concept" context/`
- Update line number references if code locations change
- Verify method signatures remain accurate
- Ensure architectural descriptions reflect actual implementation

### 3. Maintain Token Compliance
- Check token count after modifications: `wc -w filename.md`
- Split content if approaching limits rather than exceeding
- Move detailed content to lower hierarchy levels if needed
- Preserve essential navigation and core concepts at appropriate levels

### 4. Validate Technical Accuracy
- Verify file path references exist: `ls path/referenced/file.py`
- Check line numbers are current: `sed -n 'Np' file.py` where N is line number
- Test referenced commands and procedures
- Ensure examples reflect current system behavior

## Regular Validation

### 1. DRY Compliance Checks
- Monthly review for content duplication: `grep -r "repeated_concept" context/`
- Identify and consolidate duplicate explanations
- Move definitions to authoritative sources
- Update references to point to single sources

### 2. Token Count Monitoring
- Automated validation using: `find context -name "*.md" -exec wc -w {} \;`
- Create alerts for files exceeding token limits
- Regular review of file sizes and content density
- Refactor oversized files by moving content to appropriate levels

### 3. Technical Accuracy Validation
- Quarterly validation of file path references
- Line number verification against current source code
- Method signature validation using code inspection
- Architecture document alignment with implementation

### 4. Navigation Testing
- Test agent navigation patterns from `CLAUDE.md` entry points
- Verify hierarchical information discovery works effectively
- Check for broken internal links and references
- Validate that new team members can navigate system effectively

## Extension Patterns

### Adding New Modules
1. Create `context/modules/new_module/overview.md` (200-300 tokens)
2. Add supporting detail files if needed (300-500 tokens each)
3. Update `context/system/core-concepts.md` with new component definitions
4. Add navigation entry to `CLAUDE.md` module section

### Adding New Workflows
1. Create `context/workflows/new_workflow.md` (400-600 tokens)
2. Reference existing components from `system/core-concepts.md`
3. Include step-by-step procedures with code examples
4. Add navigation entry to `CLAUDE.md` practical usage section

### Adding New System Concepts
1. Add definitions to `context/system/core-concepts.md` (authoritative source)
2. Update `context/system/data-flow.md` if concept affects system flow
3. Reference new concepts from relevant module and workflow files
4. Never duplicate definitions in multiple files

## Quality Control Checklist

### Pre-Commit Validation
- [ ] Token count within limits for file type
- [ ] No duplicate content across files
- [ ] All file references exist and are accurate
- [ ] Navigation paths updated appropriately
- [ ] Content follows single responsibility principle

### Monthly Review
- [ ] DRY compliance across entire context system
- [ ] Technical accuracy of all references
- [ ] Navigation effectiveness testing
- [ ] Token count distribution analysis
- [ ] Identification of content gaps or overlaps
