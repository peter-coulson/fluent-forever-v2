#!/bin/bash
# FLUENT FOREVER V2 - Environment Activation Script
# ALWAYS use this script before running any Python commands

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH for module imports
export PYTHONPATH=$(pwd)/src

echo "✅ Environment activated:"
echo "   - Virtual environment: ACTIVE"
echo "   - PYTHONPATH: $PYTHONPATH"
echo "   - Working directory: $(pwd)"
echo ""
echo "Now you can run commands like:"
echo "   ff-sync, ff-media, ff-regen, ff-run, ff-preview"
echo "   python -m cli.commands.config_command"
echo "   ruff check src/ --fix"
echo "   pytest"
