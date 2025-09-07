# Fluent Forever V2

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

# CRITICAL: Always activate environment first
source activate_env.sh

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