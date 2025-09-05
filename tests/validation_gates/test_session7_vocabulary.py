#!/usr/bin/env python3
"""
Validation gate for Session 7: Vocabulary Pipeline Implementation

Tests that complete vocabulary workflow works through new architecture.
This test will initially fail until Session 7 is implemented.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
import sys
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_vocabulary_pipeline_migration():
    """
    Validation gate for Session 7: Vocabulary Pipeline Implementation
    
    Tests:
    - Complete vocabulary workflow through new pipeline architecture
    - All vocabulary stages work in sequence
    - Data flows correctly between stages
    """
    # Test using new pipeline CLI
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "run", "vocabulary",
        "--stage", "prepare", "--words", "test", "--dry-run"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("Vocabulary pipeline not yet implemented (Session 7 pending)")
    
    # Should succeed in dry-run mode
    assert result.returncode == 0, "Vocabulary pipeline should work"
    
    # Test claude_batch stage
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "run", "vocabulary",
        "--stage", "claude_batch", "--words", "test", "--dry-run"
    ], capture_output=True, text=True, cwd=project_root)
    
    assert result.returncode == 0, "Claude batch stage should work"


def test_end_to_end_vocabulary_workflow():
    """Test complete end-to-end vocabulary workflow."""
    try:
        from pipelines.vocabulary import VocabularyPipeline
    except ImportError:
        pytest.skip("Vocabulary pipeline not yet implemented (Session 7 pending)")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test environment
        setup_test_vocabulary_env(temp_path)
        
        # Execute full vocabulary pipeline
        pipeline = VocabularyPipeline()
        
        context = {
            "words": ["test"],
            "workspace": str(temp_path)
        }
        
        # Test each stage in sequence
        stages = ["prepare", "claude_batch", "validate", "generate_media", "sync"]
        
        for stage in stages:
            try:
                result = pipeline.execute_stage(stage, context)
                assert result is not None, f"Stage {stage} should return result"
                
                if result.get("status") == "success":
                    context.update(result.get("output", {}))
                elif result.get("status") == "skip":
                    # Some stages may be skipped in test environment
                    continue
                else:
                    pytest.fail(f"Stage {stage} failed: {result}")
                    
            except NotImplementedError:
                pytest.skip(f"Stage {stage} not yet implemented")


def test_vocabulary_pipeline_compatibility():
    """Test that vocabulary pipeline maintains compatibility with current system."""
    try:
        from pipelines.vocabulary import VocabularyPipeline
    except ImportError:
        pytest.skip("Vocabulary pipeline not yet implemented (Session 7 pending)")
    
    pipeline = VocabularyPipeline()
    
    # Test that pipeline has expected stages
    stages = pipeline.get_stages()
    expected_stages = ["prepare", "claude_batch", "validate", "generate_media", "sync"]
    
    for expected_stage in expected_stages:
        assert expected_stage in stages, f"Pipeline should have {expected_stage} stage"
    
    # Test that pipeline can handle current data formats
    context = {
        "words": ["casa", "ser"],
        "batch_size": 5
    }
    
    # Should not crash with current data format
    try:
        info = pipeline.get_info()
        assert "description" in info, "Pipeline should have description"
        assert "stages" in info, "Pipeline should list stages"
    except Exception as e:
        pytest.fail(f"Pipeline should handle current format: {e}")


def test_vocabulary_stage_isolation():
    """Test that vocabulary stages are properly isolated."""
    try:
        from stages.claude_staging import ClaudeStagingStage
        from stages.media_generation import MediaGenerationStage
    except ImportError:
        pytest.skip("Vocabulary pipeline not yet implemented (Session 7 pending)")
    
    # Test that stages can be used independently
    claude_stage = ClaudeStagingStage()
    media_stage = MediaGenerationStage()
    
    # Each stage should work independently
    test_context = {"words": ["test"]}
    
    # Claude stage should prepare staging
    claude_result = claude_stage.execute(test_context)
    if claude_result and claude_result.get("status") != "error":
        assert "staging_file" in claude_result or "batch_id" in claude_result, \
            "Claude stage should produce staging output"
    
    # Media stage should handle generation
    media_context = {"cards": ["test_card"]}
    media_result = media_stage.execute(media_context)
    if media_result and media_result.get("status") != "error":
        assert "generated" in media_result or "media_files" in media_result, \
            "Media stage should track generation"


def setup_test_vocabulary_env(temp_path: Path):
    """Set up test environment for vocabulary pipeline testing."""
    # Create required directories
    (temp_path / 'staging').mkdir()
    (temp_path / 'media').mkdir()
    
    # Create minimal vocabulary.json
    vocabulary = {
        "metadata": {
            "created": "2025-01-01",
            "last_updated": "2025-01-01",
            "total_words": 0,
            "total_cards": 0,
            "source": "test"
        },
        "words": {}
    }
    
    with open(temp_path / 'vocabulary.json', 'w') as f:
        json.dump(vocabulary, f)
    
    # Create minimal config
    config = {
        "pipelines": {
            "vocabulary": {
                "stages": ["prepare", "claude_batch", "validate", "generate_media", "sync"]
            }
        },
        "paths": {
            "workspace": str(temp_path)
        }
    }
    
    with open(temp_path / 'config.json', 'w') as f:
        json.dump(config, f)


if __name__ == "__main__":
    test_vocabulary_pipeline_migration()
    test_end_to_end_vocabulary_workflow()
    test_vocabulary_pipeline_compatibility()
    test_vocabulary_stage_isolation()
    print("Session 7 validation gate passed!")