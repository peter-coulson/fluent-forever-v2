# Fluent Forever V2 - Refactor Session Prompts

Each prompt includes mandatory validation gates, todo list requirements, and handoff instructions.

---

## Session 1: Validation Gates Setup

### Prompt for Session 1

**You are implementing Session 1 of the Fluent Forever V2 refactor. Your mission is to create focused validation gates that ensure each refactor session delivers working functionality.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/01_validation_gates.md` - Your detailed instructions
- Examine `src/cli/` directory - Current CLI commands to preserve
- Review current data files: `vocabulary.json`, `config.json`

#### Your Tasks (Use TodoWrite to Track):
1. **Create baseline test** for current vocabulary system functionality
2. **Create focused validation gates** (1 simple test per future session)
3. **Set up minimal test infrastructure** with external API mocking
4. **Create test execution framework** optimized for fast feedback
5. **Document validation approach** and test purpose
6. **Complete handoff document** for next session

#### Mandatory Validation Gates (Must Pass):
- [ ] Current system baseline test validates existing functionality
- [ ] All validation gate tests run in <10 seconds total
- [ ] Tests use real implementations, not mocks (where possible)
- [ ] External APIs are mocked appropriately
- [ ] Each session gets exactly 1 focused validation test
- [ ] Tests will fail with incorrect implementations

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Run current system baseline test and confirm it passes
2. Verify validation gate tests are focused and realistic  
3. Confirm total test time is <10 seconds
4. Complete validation checklist from instructions
5. Create handoff document using template: `context/refactor/handoff_template.md`
6. Save handoff as: `context/refactor/completed_handoffs/01_validation_gates_handoff.md`

**You cannot complete this session until validation gates provide meaningful quality assurance.**

---

## Session 2: Core Architecture  

### Prompt for Session 2

**You are implementing Session 2 of the Fluent Forever V2 refactor. Your mission is to create the fundamental pipeline architecture and registry system that will serve as the foundation for all card types.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan  
- Read `context/refactor/chunks/02_core_architecture.md` - Your detailed instructions
- Read `context/refactor/completed_handoffs/01_validation_gates_handoff.md` - Previous session context
- Review `tests/validation_gates/test_session2_core.py` - Your validation gate
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
- [ ] Current system baseline test continues to pass (no regressions)
- [ ] Session 2 validation gate passes (core architecture works)
- [ ] Pipeline registry functionality works as specified
- [ ] Basic pipeline execution patterns work  
- [ ] Pipeline interface compliance is enforced
- [ ] Unit test coverage >90% for all core components

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + Session 2 validation gate pass
2. Confirm unit test coverage meets requirements
3. Test CLI framework can list and inspect pipelines
4. Complete validation checklist from instructions
5. Create handoff document: `context/refactor/completed_handoffs/02_core_architecture_handoff.md`

**You cannot complete this session until the validation gate confirms core architecture works correctly.**

---

## Session 3: Stage System

### Prompt for Session 3

**You are implementing Session 3 of the Fluent Forever V2 refactor. Your mission is to extract common processing logic into pluggable stages that can be mixed and matched across different pipelines.**

#### Required Input Files:
- Read `context/refactor/refactor_summary.md` - Overall refactor plan
- Read `context/refactor/chunks/03_stage_system.md` - Your detailed instructions  
- Read `context/refactor/completed_handoffs/02_core_architecture_handoff.md` - Core architecture context
- Review `tests/validation_gates/test_session3_stages.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 3 validation gate passes (stage system works)
- [ ] Stage execution works correctly
- [ ] Stage chaining executes in proper order
- [ ] Error handling propagates correctly
- [ ] All common processing patterns extracted into reusable stages

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session4_providers.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 4 validation gate passes (provider system works)
- [ ] All external APIs abstracted behind provider interfaces
- [ ] Mock providers support comprehensive testing
- [ ] Stages can use providers through context
- [ ] Provider registry enables dynamic configuration

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session5_cli.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 5 validation gate passes (CLI system works)
- [ ] All existing CLI functionality accessible through new commands
- [ ] Command system is consistent and extensible
- [ ] Universal pipeline runner works correctly
- [ ] Error handling provides clear debugging information

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session6_config.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 6 validation gate passes (configuration works)
- [ ] Hierarchical configuration loading works correctly
- [ ] Environment variable overrides function properly  
- [ ] All existing configuration functionality preserved
- [ ] Configuration changes don't require code changes

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session7_vocabulary.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 7 validation gate passes (vocabulary pipeline works)
- [ ] Complete vocabulary workflow functions end-to-end
- [ ] All existing vocabulary functionality preserved
- [ ] Pipeline uses configuration system correctly
- [ ] Pipeline template ready for future card types

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session8_multi.py` - Your validation gate  
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 8 validation gate passes (multi-pipeline works)
- [ ] Vocabulary and conjugation pipelines work independently
- [ ] Shared resources work correctly across pipelines
- [ ] No conflicts between pipeline operations
- [ ] CLI provides consistent experience across pipelines

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
- Review `tests/validation_gates/test_session9_docs.py` - Your validation gate
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
- [ ] Current system baseline test + all previous validation gates pass
- [ ] Session 9 validation gate passes (documentation organized)
- [ ] Documentation is organized and navigable
- [ ] Root directory is clean
- [ ] All audiences have appropriate documentation
- [ ] Navigation links work correctly

#### Session Completion Requirements:
✅ **BEFORE marking complete, you MUST:**
1. Verify baseline test + all current/previous validation gates pass
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
3. **Current system baseline + all previous validation gates** must continue to pass
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
- If validation gates fail, **stop immediately** and investigate
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