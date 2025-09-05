# Fluent Forever V2 - Refactor Session Prompts

Each prompt includes mandatory validation gates, todo list requirements, and handoff instructions.

---

## Session 1: E2E Test Setup

### Prompt for Session 1

**You are implementing Session 1 of the Fluent Forever V2 refactor. Your mission is to create comprehensive end-to-end tests that serve as immutable validation gates for all future refactor sessions.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/01_e2e_test_setup.md` - Your detailed instructions
- Examine `src/` directory - Current system to understand existing functionality
- Read `MULTI_CARD_SYSTEM.md` - Multi-card system documentation

#### Your Tasks (Use TodoWrite to Track):
1. **Create E2E test structure** for all 8 future sessions
2. **Build mock infrastructure** for all external dependencies  
3. **Implement comprehensive tests** covering existing and planned functionality
4. **Create test execution framework** with pytest configuration
5. **Document test contracts** and mock usage
6. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All E2E tests execute successfully in <30 seconds
- [ ] Mock infrastructure supports all planned functionality  
- [ ] Test coverage includes both success and failure scenarios
- [ ] Tests fail appropriately when contracts are broken
- [ ] All current CLI commands have equivalent test coverage
- [ ] Documentation explains what each test validates

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Run all E2E tests and confirm they pass
2. Verify test suite runs in <30 seconds total
3. Confirm mock infrastructure is comprehensive
4. Complete validation checklist from instructions
5. Create handoff document using template: `context/refactor/handoff_template.md`
6. Save handoff as: `context/refactor/completed_handoffs/01_e2e_test_setup_handoff.md`

**You cannot complete this session until all validation gates pass and the handoff document is complete.**

---

## Session 2: Core Architecture  

### Prompt for Session 2

**You are implementing Session 2 of the Fluent Forever V2 refactor. Your mission is to create the fundamental pipeline architecture and registry system that will serve as the foundation for all card types.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan  
- Read `context/refactor/chunks/02_core_architecture.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/01_e2e_test_setup_handoff.md` - Previous session context
- Examine `tests/e2e/01_core_architecture/` - Your validation gates
- Review `src/utils/card_types.py` - Current card type system to evolve

#### Your Tasks (Use TodoWrite to Track):
1. **Implement Pipeline abstraction** with clean interfaces
2. **Create Stage system** with base classes and context flow
3. **Build Registry system** for pipeline discovery and management  
4. **Implement execution Context** for data flow between stages
5. **Create exception hierarchy** for error handling
6. **Build basic CLI framework** for universal commands
7. **Create comprehensive unit tests** for all core components
8. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All Session 1 E2E tests continue to pass
- [ ] All Session 2 E2E tests pass
- [ ] Pipeline registry functionality works as specified
- [ ] Basic pipeline execution patterns work  
- [ ] Pipeline interface compliance is enforced
- [ ] Unit test coverage >90% for all core components

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all Session 1 + 2 E2E tests pass
2. Confirm unit test coverage meets requirements
3. Test CLI framework can list and inspect pipelines
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/02_core_architecture_handoff.md`

**You cannot complete this session until all validation gates pass and the handoff document explains the architecture for the next session.**

---

## Session 3: Stage System

### Prompt for Session 3

**You are implementing Session 3 of the Fluent Forever V2 refactor. Your mission is to extract common processing logic into pluggable stages that can be mixed and matched across different pipelines.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/03_stage_system.md` - Your detailed instructions  
- Read `context/refactor/completed_handoffs/02_core_architecture_handoff.md` - Core architecture context
- Examine `tests/e2e/02_stage_system/` - Your validation gates
- Review current processing scripts to extract common patterns

#### Your Tasks (Use TodoWrite to Track):
1. **Create base stage classes** for common patterns (file ops, validation, API calls)
2. **Extract Claude interaction stages** (analysis, batch, ingestion)
3. **Build media generation stages** (image, audio, combined)
4. **Implement sync stages** (templates, cards, media sync)
5. **Create validation stages** (data, IPA, media validation)
6. **Build stage registry** for dynamic stage discovery
7. **Extract existing processing logic** while maintaining functionality
8. **Create comprehensive unit tests** for all stages
9. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 3 E2E tests pass
- [ ] Stage execution works correctly
- [ ] Stage chaining executes in proper order
- [ ] Error handling propagates correctly
- [ ] All common processing patterns extracted into reusable stages

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm stages can be chained together successfully  
3. Test error handling works across stage boundaries
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/03_stage_system_handoff.md`

**You cannot complete this session until the stage library covers all major processing operations.**

---

## Session 4: Provider System

### Prompt for Session 4

**You are implementing Session 4 of the Fluent Forever V2 refactor. Your mission is to abstract all external dependencies into pluggable providers that can be mocked, swapped, or configured independently.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/04_provider_system.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/03_stage_system_handoff.md` - Stage system context
- Examine `tests/e2e/03_provider_system/` - Your validation gates
- Review current API clients: `src/apis/`

#### Your Tasks (Use TodoWrite to Track):
1. **Create provider interfaces** (data, media, sync providers)
2. **Implement data providers** (JSON files, memory for testing)
3. **Build media providers** (OpenAI, Forvo, mock for testing)
4. **Create sync providers** (AnkiConnect, mock for testing)
5. **Build provider registry** and factory system
6. **Extract existing API logic** into provider implementations
7. **Create comprehensive mock providers** for testing
8. **Integrate providers with stage system** 
9. **Create comprehensive unit tests** for all providers
10. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 4 E2E tests pass
- [ ] All external APIs abstracted behind provider interfaces
- [ ] Mock providers support comprehensive testing
- [ ] Stages can use providers through context
- [ ] Provider registry enables dynamic configuration

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm all external dependencies abstracted behind providers
3. Test mock providers enable comprehensive testing
4. Complete validation checklist from instructions  
5. Create handoff document: `context/refactor/completed_handoffs/04_provider_system_handoff.md`

**You cannot complete this session until all external dependencies are properly abstracted.**

---

## Session 5: CLI Overhaul

### Prompt for Session 5

**You are implementing Session 5 of the Fluent Forever V2 refactor. Your mission is to replace all hardcoded CLI scripts with a universal pipeline runner that provides consistent commands for all card types.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/05_cli_overhaul.md` - Your detailed instructions  
- Read `context/refactor/completed_handoffs/04_provider_system_handoff.md` - Provider system context
- Examine `tests/e2e/04_cli_system/` - Your validation gates
- Review `src/cli/` - Current CLI scripts to replace

#### Your Tasks (Use TodoWrite to Track):
1. **Enhance pipeline runner** with comprehensive command support
2. **Implement all CLI commands** (list, info, run, preview)
3. **Create CLI configuration system** 
4. **Build output formatting utilities**
5. **Map all existing CLI functionality** to new commands
6. **Create comprehensive argument validation**
7. **Build help and discovery system**
8. **Create comprehensive unit tests** for CLI system
9. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 5 E2E tests pass
- [ ] All existing CLI functionality accessible through new commands
- [ ] Command system is consistent and extensible
- [ ] Universal pipeline runner works correctly
- [ ] Error handling provides clear debugging information

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm all existing CLI operations can be performed with new commands
3. Test command system provides consistent patterns
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/05_cli_overhaul_handoff.md`

**You cannot complete this session until all existing workflows can be completed with new commands.**

---

## Session 6: Configuration Refactor

### Prompt for Session 6

**You are implementing Session 6 of the Fluent Forever V2 refactor. Your mission is to consolidate all configuration into a unified, hierarchical system that supports pipeline-specific settings, provider configuration, and environment-based overrides.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/06_configuration_refactor.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/05_cli_overhaul_handoff.md` - CLI system context  
- Examine `tests/e2e/05_configuration/` - Your validation gates
- Review current config files: `config.json`, `.env`

#### Your Tasks (Use TodoWrite to Track):
1. **Implement configuration manager** with hierarchical loading
2. **Create configuration schemas** for all component types
3. **Build default configuration files** for all pipelines and providers
4. **Implement environment override system**
5. **Create configuration validation**
6. **Migrate existing configuration** to new structure
7. **Integrate configuration with all components**
8. **Create configuration CLI commands** 
9. **Create comprehensive unit tests** for configuration system
10. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 6 E2E tests pass
- [ ] Hierarchical configuration loading works correctly
- [ ] Environment variable overrides function properly  
- [ ] All existing configuration functionality preserved
- [ ] Configuration changes don't require code changes

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm all existing configuration functionality preserved
3. Test new hierarchical configuration system works
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/06_configuration_refactor_handoff.md`

**You cannot complete this session until the unified configuration system supports all components.**

---

## Session 7: Pipeline Implementation

### Prompt for Session 7

**You are implementing Session 7 of the Fluent Forever V2 refactor. Your mission is to implement the vocabulary pipeline using the new architecture, ensuring all existing functionality is preserved while demonstrating the new modular system.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan  
- Read `context/refactor/chunks/07_pipeline_implementation.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/06_configuration_refactor_handoff.md` - Configuration context
- Examine `tests/e2e/06_vocabulary_pipeline/` - Your validation gates
- Review current vocabulary processing logic to migrate

#### Your Tasks (Use TodoWrite to Track):
1. **Implement VocabularyPipeline class** using new architecture
2. **Create vocabulary-specific stages** (word analysis, batch creation)
3. **Build data handling components** for vocabulary.json
4. **Implement vocabulary validation stages**
5. **Create pipeline template** for future card types
6. **Register vocabulary pipeline** in global registry  
7. **Migrate all existing vocabulary functionality**
8. **Ensure backward compatibility** with existing data
9. **Create comprehensive unit tests** for vocabulary pipeline
10. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 7 E2E tests pass
- [ ] Complete vocabulary workflow functions end-to-end
- [ ] All existing vocabulary functionality preserved
- [ ] Pipeline uses configuration system correctly
- [ ] Pipeline template ready for future card types

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm complete vocabulary workflow works with new architecture
3. Test all existing vocabulary functionality preserved
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/07_pipeline_implementation_handoff.md`

**You cannot complete this session until the vocabulary pipeline fully demonstrates the new architecture benefits.**

---

## Session 8: Multi-Pipeline Support  

### Prompt for Session 8

**You are implementing Session 8 of the Fluent Forever V2 refactor. Your mission is to ensure the conjugation pipeline works correctly in the new architecture and validate that multiple pipelines can coexist without conflicts.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/08_multi_pipeline_support.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/07_pipeline_implementation_handoff.md` - Vocabulary pipeline context
- Examine `tests/e2e/07_multi_pipeline/` - Your validation gates  
- Review `src/utils/card_types.py` and `conjugations.json`

#### Your Tasks (Use TodoWrite to Track):
1. **Implement ConjugationPipeline class** using new architecture
2. **Create conjugation-specific stages** (verb analysis, card creation)
3. **Build conjugation data handling** components
4. **Implement conjugation validation** stages
5. **Create multi-pipeline registry** system
6. **Ensure resource isolation** between pipelines
7. **Update CLI for multi-pipeline** support
8. **Prevent conflicts** between pipeline operations
9. **Create comprehensive unit tests** for conjugation pipeline  
10. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 8 E2E tests pass
- [ ] Vocabulary and conjugation pipelines work independently
- [ ] Shared resources work correctly across pipelines
- [ ] No conflicts between pipeline operations
- [ ] CLI provides consistent experience across pipelines

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm multiple pipelines can be used simultaneously
3. Test resource sharing works without conflicts
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/08_multi_pipeline_support_handoff.md`

**You cannot complete this session until multiple pipelines coexist cleanly and demonstrate the architecture's extensibility.**

---

## Session 9: Documentation Context System

### Prompt for Session 9

**You are implementing Session 9 of the Fluent Forever V2 refactor. Your mission is to organize all documentation into a logical context system that serves different audiences and maintains clear separation between operational, development, and user documentation.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/09_documentation_context.md` - Your detailed instructions  
- Read `context/refactor/completed_handoffs/08_multi_pipeline_support_handoff.md` - Multi-pipeline context
- Examine `tests/e2e/08_documentation/` - Your validation gates
- Review all current markdown files in project root

#### Your Tasks (Use TodoWrite to Track):
1. **Create context directory structure** for all audiences
2. **Migrate existing documentation** to appropriate contexts
3. **Generate new documentation** for missing areas
4. **Create navigation and index files** 
5. **Build documentation management tools**
6. **Create auto-generation** for reference materials
7. **Add documentation currency tests**
8. **Clean up root directory** of documentation files
9. **Create new root README** pointing to context system
10. **Complete final handoff document**

#### Mandatory Validation Gates (Must Pass):
- [ ] All previous session E2E tests continue to pass
- [ ] All Session 9 E2E tests pass
- [ ] Documentation is organized and navigable
- [ ] Root directory is clean
- [ ] All audiences have appropriate documentation
- [ ] Navigation links work correctly

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify all previous + current E2E tests pass
2. Confirm documentation is easy to find and follow
3. Test examples work correctly
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/09_documentation_context_handoff.md`

**You cannot complete this session until the documentation system serves all audiences effectively and the project structure is clean.**

---

## Universal Session Rules

### For All Sessions:

#### Required TodoWrite Usage:
- **Create TodoWrite list** immediately after reading instructions
- **Mark items in_progress** before starting work (only one at a time)  
- **Mark items completed** immediately after finishing
- **Update todo list** if you discover additional work needed
- **Clean up todo list** before session completion

#### Validation Gate Protocol:
1. **Read validation gates** from your session instructions
2. **Test each gate** before marking session complete
3. **All previous session tests** must continue to pass
4. **Document any test failures** and resolution
5. **Do not proceed** until all gates pass

#### Handoff Document Requirements:
- **Use the handoff template** exactly as provided
- **Document all technical decisions** made during implementation
- **Include all challenges encountered** and their solutions
- **Provide clear guidance** for the next session
- **List all files created/modified**
- **Include verification checklist** completion

#### Error Handling:
- If E2E tests fail, **stop immediately** and investigate
- If validation gates cannot be passed, **document why** in handoff  
- If architectural changes are needed, **document rationale**
- If session cannot be completed, **mark as incomplete** and explain

#### Quality Standards:
- **Unit test coverage >90%** for all new code
- **Error messages** must be actionable
- **Code must follow** established patterns
- **Documentation must be** current and accurate

---

**Remember: Each session builds on previous work. The validation gates ensure we maintain quality and functionality throughout the refactor process.**