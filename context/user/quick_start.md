# Quick Start Guide

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
# Use the activation script (IMPORTANT!)
source activate_env.sh

# Copy example configuration
cp config/core.json.example config/core.json

# Add API keys (create .env file)
echo "OPENAI_API_KEY=your-openai-key-here" > .env
echo "FORVO_API_KEY=your-forvo-key-here" >> .env
```

### 3. Test Installation
```bash
# Always use activation script first
source activate_env.sh

# Verify system works
python -m cli.pipeline list

# Test Anki connection
python -m cli.pipeline run vocabulary --stage sync_templates --dry-run
```

## Basic Usage

### Vocabulary Cards
```bash
# Always activate environment first
source activate_env.sh

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
# Always activate environment first
source activate_env.sh

# Create conjugation practice cards
python -m cli.pipeline run conjugation --stage analyze_verbs --verbs hablar,comer,vivir
python -m cli.pipeline run conjugation --stage create_cards
python -m cli.pipeline run conjugation --stage generate_media --execute
python -m cli.pipeline run conjugation --stage sync_anki --execute
```

### Preview Cards
```bash
# Always activate environment first
source activate_env.sh

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

## Important Notes

### 🚨 Always Use Activation Script
**CRITICAL**: Always run `source activate_env.sh` before any Python commands. This script:
- Activates the virtual environment
- Sets PYTHONPATH correctly
- Changes to the project directory
- Displays confirmation of proper setup

**Never run Python commands without activating first!**