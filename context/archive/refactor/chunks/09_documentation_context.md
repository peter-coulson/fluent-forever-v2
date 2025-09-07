# Session 9: Documentation Context System

## Mission
Organize all documentation into a logical context system that serves different audiences and maintains clear separation between operational, development, and user documentation.

## Context Files Required
- `context/refactor/refactor_summary.md` - Overall refactor plan  
- `context/refactor/completed_handoffs/08_multi_pipeline_support_handoff.md` - Multi-pipeline context
- `tests/e2e/08_documentation/` - Validation gates for this session
- All current markdown files in project root
- Documentation scattered throughout the system

## Objectives

### Primary Goal
Create a clean, organized documentation system that serves different audiences while cleaning up the cluttered home directory.

### Target Documentation Structure
```
context/
├── user/                       # User-facing documentation
│   ├── README.md              # Main user guide (replaces root README.md)
│   ├── quick_start.md         # Getting started guide
│   ├── troubleshooting.md     # Common issues and solutions
│   └── examples/              # Usage examples
│       ├── vocabulary_workflow.md
│       └── conjugation_workflow.md
├── development/               # Developer documentation  
│   ├── architecture.md        # System architecture overview
│   ├── adding_pipelines.md    # How to add new card types
│   ├── api_reference.md       # API documentation
│   ├── testing.md             # Testing strategies and guidelines
│   └── design_decisions.md    # Historical design decisions
├── operations/                # Operational guides (for Claude and power users)
│   ├── claude_guide.md        # Claude operational guide (current CLAUDE.md)
│   ├── configuration.md       # Configuration system documentation
│   ├── deployment.md          # Deployment and setup guides
│   └── maintenance.md         # System maintenance procedures
├── reference/                 # Reference materials
│   ├── cli_reference.md       # Complete CLI command reference
│   ├── configuration_reference.md # Configuration options reference
│   ├── pipeline_reference.md  # Pipeline and stage reference
│   └── provider_reference.md  # Provider API reference  
└── archive/                   # Historical/deprecated documentation
    ├── v1_migration.md        # Migration from old system
    ├── refactor/              # Refactor documentation (current folder)
    └── legacy/                # Deprecated docs
        ├── old_README.md
        └── old_design_decisions.md
```

## Implementation Requirements

### 1. Documentation Context Manager (`src/utils/docs_manager.py`)

```python
from pathlib import Path
from typing import Dict, List, Optional
import shutil
from datetime import datetime

class DocumentationManager:
    """Manage documentation organization and context system"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.context_root = self.project_root / 'context'
    
    def organize_documentation(self) -> None:
        """Organize all documentation into context system"""
        # Create context directory structure
        self._create_context_structure()
        
        # Move existing documentation
        self._migrate_existing_docs()
        
        # Generate new documentation
        self._generate_new_docs()
        
        # Create navigation files
        self._create_navigation()
        
        # Clean up root directory
        self._cleanup_root()
    
    def _create_context_structure(self) -> None:
        """Create the context directory structure"""
        directories = [
            'user', 'user/examples',
            'development', 
            'operations',
            'reference',
            'archive', 'archive/legacy'
        ]
        
        for directory in directories:
            (self.context_root / directory).mkdir(parents=True, exist_ok=True)
    
    def _migrate_existing_docs(self) -> None:
        """Move existing documentation to appropriate context"""
        migrations = {
            'README.md': 'archive/legacy/old_README.md',
            'CLAUDE.md': 'operations/claude_guide.md',
            'DESIGN_DECISIONS.md': 'development/design_decisions.md',
            'MULTI_CARD_SYSTEM.md': 'archive/legacy/multi_card_system.md',
            'QUEUE_OPTIMIZATIONS.md': 'archive/legacy/queue_optimizations.md'
        }
        
        for source, target in migrations.items():
            source_path = self.project_root / source
            target_path = self.context_root / target
            
            if source_path.exists():
                # Add migration header
                content = self._add_migration_header(source_path.read_text(), source, target)
                target_path.write_text(content)
                print(f"Migrated {source} → context/{target}")
    
    def _add_migration_header(self, content: str, source: str, target: str) -> str:
        """Add migration header to moved documentation"""
        header = f"""<!-- 
MIGRATED DOCUMENT
Original: {source}
New Location: context/{target}
Migration Date: {datetime.now().isoformat()}
-->

"""
        return header + content
    
    def _generate_new_docs(self) -> None:
        """Generate new documentation files"""
        self._create_main_readme()
        self._create_quick_start()
        self._create_architecture_guide()
        self._create_cli_reference()
        self._create_configuration_docs()
        self._create_troubleshooting()
    
    def _create_main_readme(self) -> None:
        """Create main user README"""
        content = """# Fluent Forever V2 - Spanish Learning System

A modular card creation system for Spanish language learning using the Fluent Forever methodology.

## 🎯 What This System Does

Transform Spanish vocabulary and grammar into memorable Anki cards with:
- **Multiple Card Types**: Vocabulary, conjugations, and custom pipelines
- **Studio Ghibli Imagery**: Consistent, engaging visual style
- **Native Pronunciation**: Latin American audio from multiple sources
- **Modular Architecture**: Easy to extend with new card types

## 🚀 Quick Start

1. **Prerequisites**: Python 3.8+, Anki with AnkiConnect addon
2. **Setup**: See `context/user/quick_start.md` for detailed setup
3. **Usage**: Run `python -m cli.pipeline list` to see available pipelines

## 📖 Documentation

### For Users
- [Quick Start Guide](quick_start.md) - Get up and running in minutes
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Examples](examples/) - Workflow examples and tutorials

### For Developers  
- [Architecture Overview](../development/architecture.md) - System design and components
- [Adding Pipelines](../development/adding_pipelines.md) - How to add new card types
- [API Reference](../development/api_reference.md) - Complete API documentation

### For Operations
- [Claude Guide](../operations/claude_guide.md) - Claude operational procedures
- [Configuration](../operations/configuration.md) - System configuration guide
- [CLI Reference](../reference/cli_reference.md) - Complete command reference

## 🏗️ System Architecture

This system uses a **pipeline-centric architecture** where each card type defines its own complete processing workflow:

```
Pipeline Types:    Vocabulary → Conjugation → Grammar → Custom
Processing Stages: Analysis → Generation → Validation → Sync
External Services: OpenAI → Forvo → AnkiConnect
```

## 💡 Key Features

- **Modular Pipelines**: Each card type has its own complete workflow
- **Pluggable Components**: Stages and providers can be mixed and matched
- **Universal CLI**: Consistent commands for all card types
- **Comprehensive Testing**: E2E tests ensure reliability
- **Clean Configuration**: Hierarchical configuration system

## 📊 Current Status

- ✅ **Vocabulary Pipeline**: Complete E2E workflow for vocabulary cards
- ✅ **Conjugation Pipeline**: Verb conjugation practice cards  
- ✅ **Multi-Pipeline Support**: Multiple card types coexist cleanly
- ✅ **Universal CLI**: `python -m cli.pipeline` commands for all operations

## 🔧 Common Commands

```bash
# Discover available pipelines
python -m cli.pipeline list

# Get pipeline information
python -m cli.pipeline info vocabulary

# Run pipeline stages
python -m cli.pipeline run vocabulary --stage prepare_batch --words por,para
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer

# Preview cards
python -m cli.pipeline preview vocabulary --start-server
```

## 🤝 Contributing

See [development documentation](../development/) for:
- System architecture overview
- How to add new pipelines
- Testing guidelines
- API reference

---

**Transform Spanish learning into memorable visual experiences through modular card creation!**
"""
        
        readme_path = self.context_root / 'user' / 'README.md'
        readme_path.write_text(content)
        print("Created context/user/README.md")
    
    def _create_quick_start(self) -> None:
        """Create quick start guide"""
        content = """# Quick Start Guide

Get up and running with Fluent Forever V2 in minutes.

## Prerequisites

### Required Software
- **Python 3.8+** - Programming language runtime
- **Anki** - Spaced repetition software ([Download](https://apps.ankiweb.net/))
- **AnkiConnect Add-on** - Enables API access ([Install Guide](https://ankiweb.net/shared/info/2055492159))

### API Keys (Optional but Recommended)
- **OpenAI API Key** - For image generation (~$0.25 per 5-card batch)
- **Forvo API Key** - For native pronunciation audio

## Installation

### 1. Clone and Setup
```bash
git clone [repository-url]
cd fluent-forever-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy example configuration
cp config/core.json.example config/core.json

# Add API keys (create .env file)
echo "OPENAI_API_KEY=your-openai-key-here" > .env
echo "FORVO_API_KEY=your-forvo-key-here" >> .env
```

### 3. Test Installation
```bash
# Verify system works
python -m cli.pipeline list

# Test Anki connection
python -m cli.pipeline run vocabulary --stage sync_templates --dry-run
```

## Basic Usage

### Vocabulary Cards
```bash
# 1. Analyze words and create batch
python -m cli.pipeline run vocabulary --stage prepare_batch --words haber,ser,estar

# 2. Fill in the staging file (or use Claude Code for automated filling)
# Edit staging/claude_batch_*.json with meanings and prompts

# 3. Ingest completed batch
python -m cli.pipeline run vocabulary --stage ingest_batch --file staging/claude_batch_*.json

# 4. Generate media and sync to Anki
python -m cli.pipeline run vocabulary --stage generate_media --execute
python -m cli.pipeline run vocabulary --stage sync_anki --execute
```

### Conjugation Cards  
```bash
# Create conjugation practice cards
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer,vivir
python -m cli.pipeline run conjugation --stage create_cards
python -m cli.pipeline run conjugation --stage generate_media --execute
python -m cli.pipeline run conjugation --stage sync_anki --execute
```

### Preview Cards
```bash
# Start preview server
python -m cli.pipeline preview vocabulary --start-server --port 8000

# Open in browser: http://127.0.0.1:8000
```

## Next Steps

- **Explore Examples**: See `examples/` for detailed workflow guides
- **Customize Configuration**: Edit files in `config/` directory
- **Add More Card Types**: Follow `../development/adding_pipelines.md`
- **Troubleshooting**: See `troubleshooting.md` for common issues

## Getting Help

- **Documentation**: Browse `context/` directory for comprehensive guides
- **Issues**: Report problems at [GitHub Issues](link-to-issues)
- **CLI Help**: Run `python -m cli.pipeline --help` for command help
"""
        
        quick_start_path = self.context_root / 'user' / 'quick_start.md'
        quick_start_path.write_text(content)
        print("Created context/user/quick_start.md")
    
    def _create_architecture_guide(self) -> None:
        """Create architecture documentation"""
        content = """# System Architecture

Fluent Forever V2 uses a **pipeline-centric architecture** that enables seamless addition of new card types without modifying core infrastructure.

## Core Concepts

### Pipelines
Each card type is implemented as a **Pipeline** that defines:
- **Stages**: Processing steps (analysis, generation, validation, sync)
- **Data Sources**: Where card data comes from
- **Configuration**: Pipeline-specific settings
- **Anki Integration**: Note type and template mapping

### Stages
**Stages** are reusable processing components that:
- **Execute** specific operations (media generation, validation, etc.)
- **Chain Together** to create complete workflows
- **Share Context** through the pipeline execution context
- **Handle Errors** gracefully with detailed reporting

### Providers
**Providers** abstract external dependencies:
- **Data Providers**: File system, databases, APIs
- **Media Providers**: Image generation (OpenAI), audio (Forvo)
- **Sync Providers**: Anki, other spaced repetition systems

## Architecture Layers

```
┌─────────────────────┐
│       CLI Layer     │ ← Universal commands for all pipelines
├─────────────────────┤
│    Pipeline Layer   │ ← Card-type specific workflows
├─────────────────────┤
│     Stage Layer     │ ← Reusable processing components
├─────────────────────┤
│   Provider Layer    │ ← External service abstractions
├─────────────────────┤
│      Core Layer     │ ← Foundational abstractions
└─────────────────────┘
```

### Core Layer
- **Pipeline Interface**: Abstract base class for all card types
- **Stage Interface**: Common processing step abstraction
- **Context System**: Data flow between stages
- **Registry System**: Pipeline and provider discovery

### Provider Layer  
- **Data Providers**: JSON files, databases, memory (testing)
- **Media Providers**: OpenAI (images), Forvo (audio), mock (testing)
- **Sync Providers**: AnkiConnect, file export, mock (testing)

### Stage Layer
- **Generic Stages**: Media generation, validation, sync operations
- **Pipeline-Specific Stages**: Word analysis, conjugation analysis
- **Composition**: Stages can be chained and reused across pipelines

### Pipeline Layer
- **Vocabulary Pipeline**: Fluent Forever vocabulary cards
- **Conjugation Pipeline**: Verb conjugation practice
- **Template Pipeline**: Starting point for new card types

### CLI Layer
- **Universal Commands**: Same interface for all pipelines
- **Discovery**: List pipelines, stages, and capabilities
- **Execution**: Run individual stages or complete workflows

## Data Flow

```
Input (Words/Verbs) 
    ↓
[Analysis Stage] → Context Data
    ↓
[Generation Stage] → Context + Generated Content
    ↓
[Validation Stage] → Context + Validation Results  
    ↓
[Sync Stage] → Cards in Anki
```

## Extension Points

### Adding New Pipelines
1. **Implement Pipeline Interface** 
2. **Define Stages** (reuse existing + create custom)
3. **Configure Providers** 
4. **Register Pipeline**
5. **Add Configuration**

### Adding New Stages
1. **Implement Stage Interface**
2. **Define Context Requirements** 
3. **Add to Stage Registry**
4. **Create Unit Tests**

### Adding New Providers
1. **Implement Provider Interface**
2. **Add Configuration Schema**
3. **Register with Provider Registry** 
4. **Create Mock for Testing**

## Key Design Principles

### Modularity
- **Single Responsibility**: Each component has one clear purpose
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together

### Extensibility  
- **Open/Closed Principle**: Easy to extend, hard to break
- **Plugin Architecture**: New functionality added without core changes
- **Interface Segregation**: Clean, focused interfaces

### Testability
- **Dependency Injection**: All external dependencies are injectable
- **Mock Support**: Comprehensive mocking for all external services
- **Isolation**: Components can be tested independently

### Maintainability
- **Clear Interfaces**: Well-defined contracts between components
- **Consistent Patterns**: Same patterns used throughout system
- **Error Handling**: Comprehensive error handling and logging

## Technology Stack

- **Python 3.8+**: Core language
- **Flask**: Preview server framework
- **Requests**: HTTP client for external APIs  
- **JSON**: Configuration and data storage
- **pytest**: Testing framework
- **AnkiConnect**: Anki integration protocol

## Performance Considerations

- **Caching**: Configuration and data caching where appropriate
- **Batch Processing**: Efficient batch operations for media generation
- **Async Support**: Ready for async/await patterns where beneficial
- **Memory Management**: Efficient memory usage for large datasets

---

This architecture enables rapid development of new card types while maintaining system stability and user experience consistency."""
        
        arch_path = self.context_root / 'development' / 'architecture.md'
        arch_path.write_text(content)
        print("Created context/development/architecture.md")
    
    def _create_navigation(self) -> None:
        """Create navigation and index files"""
        # Create main navigation file
        nav_content = """# Documentation Navigation

Welcome to the Fluent Forever V2 documentation system. Documentation is organized by audience and purpose.

## 📚 For Users
Start here if you want to use the system to create Spanish learning cards.

- **[README](user/README.md)** - System overview and getting started
- **[Quick Start](user/quick_start.md)** - Get running in minutes
- **[Troubleshooting](user/troubleshooting.md)** - Common issues and solutions
- **[Examples](user/examples/)** - Workflow examples and tutorials

## 🛠️ For Developers  
Start here if you want to understand or extend the system.

- **[Architecture](development/architecture.md)** - System design overview
- **[Adding Pipelines](development/adding_pipelines.md)** - How to add new card types
- **[API Reference](development/api_reference.md)** - Complete API documentation
- **[Testing](development/testing.md)** - Testing strategies and guidelines

## ⚙️ For Operations
Advanced configuration and operational procedures.

- **[Claude Guide](operations/claude_guide.md)** - Claude operational procedures  
- **[Configuration](operations/configuration.md)** - System configuration
- **[Deployment](operations/deployment.md)** - Setup and deployment guides

## 📖 Reference Materials
Complete reference documentation for all system components.

- **[CLI Reference](reference/cli_reference.md)** - All CLI commands
- **[Configuration Reference](reference/configuration_reference.md)** - All config options
- **[Pipeline Reference](reference/pipeline_reference.md)** - All pipelines and stages
- **[Provider Reference](reference/provider_reference.md)** - All provider APIs

## 🗄️ Archive
Historical documentation and migration guides.

- **[Refactor Documentation](archive/refactor/)** - System refactor process
- **[Legacy Documentation](archive/legacy/)** - Previous system documentation
- **[Migration Guide](archive/v1_migration.md)** - Upgrading from v1

---

**Need help finding something?** Check the most relevant audience section above, or search within the `context/` directory.
"""
        
        nav_path = self.context_root / 'README.md'
        nav_path.write_text(nav_content)
        print("Created context/README.md navigation")
    
    def _cleanup_root(self) -> None:
        """Clean up root directory of documentation files"""
        # Move markdown files to archive
        cleanup_files = [
            'README.md', 'CLAUDE.md', 'DESIGN_DECISIONS.md', 
            'MULTI_CARD_SYSTEM.md', 'QUEUE_OPTIMIZATIONS.md'
        ]
        
        for file in cleanup_files:
            file_path = self.project_root / file
            if file_path.exists():
                # Create new root README pointing to context
                if file == 'README.md':
                    self._create_root_readme()
                
                # Remove original (already migrated)
                file_path.unlink()
                print(f"Removed {file} from root (migrated to context/)")
    
    def _create_root_readme(self) -> None:
        """Create minimal root README pointing to context"""
        content = """# Fluent Forever V2

**Spanish learning card creation system with modular pipeline architecture.**

## 📖 Documentation

All documentation has been organized in the `context/` directory:

- **[User Guide](context/user/README.md)** - Getting started, usage, examples
- **[Developer Guide](context/development/architecture.md)** - Architecture, API reference
- **[Operations Guide](context/operations/claude_guide.md)** - Configuration, deployment
- **[Complete Navigation](context/README.md)** - Full documentation index

## 🚀 Quick Start

```bash
# Install and setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Discover available pipelines
python -m cli.pipeline list

# Get detailed usage instructions
# See context/user/quick_start.md
```

## 🏗️ Architecture

Pipeline-centric system supporting multiple card types:
- **Vocabulary Pipeline**: Fluent Forever vocabulary cards  
- **Conjugation Pipeline**: Verb conjugation practice
- **Extensible**: Easy to add new card types

---

**For complete documentation, see [`context/README.md`](context/README.md)**
"""
        
        root_readme = self.project_root / 'README.md'
        root_readme.write_text(content)
        print("Created new root README.md pointing to context/")
```

### 2. Documentation Generation Scripts

Create automated documentation generation:

```python
# In src/utils/docs_generator.py

def generate_cli_reference() -> str:
    """Generate CLI reference documentation"""
    # Auto-generate from CLI help system
    pass

def generate_configuration_reference() -> str:
    """Generate configuration reference"""
    # Auto-generate from configuration schemas
    pass

def generate_api_reference() -> str:
    """Generate API reference documentation"""
    # Auto-generate from docstrings and type hints
    pass
```

### 3. Documentation Tests

Add tests to ensure documentation stays current:

```python
# In tests/documentation/test_docs_current.py

def test_cli_reference_current():
    """Test that CLI reference matches actual CLI"""
    # Compare generated reference with actual CLI help
    pass

def test_config_reference_current():
    """Test that config reference matches schemas"""
    # Compare reference with actual configuration options
    pass

def test_all_commands_documented():
    """Test that all CLI commands are documented"""
    pass
```

## Validation Checklist

### E2E Test Compliance
- [ ] All tests in `tests/e2e/08_documentation/` pass
- [ ] Documentation structure validates correctly
- [ ] All markdown files are valid
- [ ] Navigation links work correctly

### Documentation Quality  
- [ ] All audiences have appropriate documentation
- [ ] Root directory is clean and organized
- [ ] Documentation is findable and navigable
- [ ] Examples are current and functional

### Maintenance  
- [ ] Auto-generation works for reference materials
- [ ] Tests validate documentation stays current
- [ ] Migration headers preserve history
- [ ] Archive organization is logical

## Deliverables

### 1. Organized Documentation System
- Complete context directory structure
- All existing documentation migrated appropriately
- New documentation for missing areas
- Clean root directory

### 2. Navigation System
- Clear navigation for all audiences
- Index files for major sections
- Cross-references between related documents
- Search-friendly organization

### 3. Maintenance Tools
- Documentation management utilities
- Auto-generation for reference materials
- Tests to ensure documentation currency
- Migration tracking

### 4. Session Handoff Document
Create `context/refactor/completed_handoffs/09_documentation_context_handoff.md` with:
- Overview of documentation organization
- How to maintain documentation going forward
- Auto-generation capabilities
- Any final implementation notes

## Success Criteria

### Must Pass Before Session Completion
1. ✅ All previous session E2E tests continue to pass
2. ✅ All Session 9 E2E tests pass
3. ✅ Documentation is organized and navigable
4. ✅ Root directory is clean
5. ✅ All audiences have appropriate documentation

### Quality Validation
- Documentation is easy to find and follow
- Examples work correctly
- Navigation is intuitive
- Maintenance tools function properly

## Notes for Implementation

### Organization Strategy
- Group by audience first, then by topic
- Keep user-facing docs simple and example-heavy
- Make developer docs comprehensive and technical
- Preserve historical context in archive

### Maintenance Strategy
- Auto-generate reference materials where possible
- Test documentation currency automatically
- Make updating documentation part of development workflow
- Keep navigation up-to-date with system changes

---

**Remember: This documentation system will serve the project long-term. Focus on maintainability and findability.**