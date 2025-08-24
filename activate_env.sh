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
echo "   python -m cli.prepare_claude_batch --words word1,word2"
echo "   python -m cli.ingest_claude_batch --input staging/file.json"
echo "   python -m cli.run_media_then_sync --cards CardID1,CardID2 --execute"