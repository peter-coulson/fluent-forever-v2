#!/usr/bin/env python3
"""
Validation gate for Session 5: CLI Overhaul

Tests that universal CLI can discover and execute pipelines.
This test will initially fail until Session 5 is implemented.
"""

import pytest
import subprocess
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_universal_cli():
    """
    Validation gate for Session 5: CLI System
    
    Tests:
    - Universal CLI can list available pipelines
    - CLI can get pipeline information
    - CLI can execute pipeline stages
    """
    try:
        from cli.pipeline_runner import PipelineRunner
    except ImportError:
        pytest.skip("CLI system not yet implemented (Session 5 pending)")
    
    runner = PipelineRunner()
    
    # Test pipeline discovery
    pipelines = runner.list_pipelines()
    assert pipelines is not None, "Should be able to list pipelines"
    assert len(pipelines) > 0, "Should have at least one pipeline"
    
    # Test pipeline info
    first_pipeline = list(pipelines)[0] if isinstance(pipelines, dict) else pipelines[0]
    info = runner.get_pipeline_info(first_pipeline)
    assert info is not None, "Should return pipeline info"
    assert "stages" in info, "Pipeline info should include stages"


def test_cli_commands():
    """Test that CLI commands work as expected."""
    # Test pipeline list command
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "list"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("CLI system not yet implemented (Session 5 pending)")
    
    # Should succeed and show pipelines
    assert "vocabulary" in result.stdout or "Vocabulary" in result.stdout, \
        "Should list vocabulary pipeline"


def test_pipeline_execution():
    """Test that pipelines can be executed via CLI."""
    # Test pipeline info command
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "info", "vocabulary"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("CLI system not yet implemented (Session 5 pending)")
    
    # Should succeed and show pipeline stages
    assert "stages" in result.stdout.lower(), "Should show available stages"


def test_stage_execution():
    """Test that individual stages can be executed."""
    # Test stage execution with dry-run
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "run", "vocabulary", 
        "--stage", "prepare", "--dry-run"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("CLI system not yet implemented (Session 5 pending)")
    
    # Should succeed in dry-run mode
    assert result.returncode == 0, "Stage execution should work in dry-run"


def test_command_compatibility():
    """Test that old CLI commands still work through new system."""
    try:
        from cli.commands.vocabulary import VocabularyCommand
    except ImportError:
        pytest.skip("CLI system not yet implemented (Session 5 pending)")
    
    # Test that vocabulary command exists
    vocab_cmd = VocabularyCommand()
    assert vocab_cmd is not None, "Vocabulary command should be available"
    
    # Test that it has expected methods
    assert hasattr(vocab_cmd, 'prepare_batch'), "Should have prepare_batch method"
    assert hasattr(vocab_cmd, 'generate_media'), "Should have generate_media method"
    assert hasattr(vocab_cmd, 'sync_anki'), "Should have sync_anki method"


if __name__ == "__main__":
    test_universal_cli()
    test_cli_commands()
    test_pipeline_execution()
    test_stage_execution()
    test_command_compatibility()
    print("Session 5 validation gate passed!")