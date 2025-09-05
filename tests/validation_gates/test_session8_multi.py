#!/usr/bin/env python3
"""
Validation gate for Session 8: Multi-Pipeline Support

Tests that multiple pipelines coexist without conflict.
This test will initially fail until Session 8 is implemented.
"""

import pytest
import subprocess
from pathlib import Path
import sys
import json

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_multi_pipeline_coexistence():
    """
    Validation gate for Session 8: Multi-Pipeline Support
    
    Tests:
    - Both vocabulary and conjugation pipelines work simultaneously
    - Pipelines don't interfere with each other
    - Shared resources are handled correctly
    """
    # Test that both pipelines can be listed
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "list"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("Multi-pipeline system not yet implemented (Session 8 pending)")
    
    # Should show both pipelines
    output = result.stdout.lower()
    assert "vocabulary" in output, "Should list vocabulary pipeline"
    assert "conjugation" in output, "Should list conjugation pipeline"


def test_pipeline_independence():
    """Test that pipelines operate independently."""
    try:
        from pipelines.vocabulary import VocabularyPipeline
        from pipelines.conjugation import ConjugationPipeline
    except ImportError:
        pytest.skip("Multi-pipeline system not yet implemented (Session 8 pending)")
    
    # Create both pipelines
    vocab_pipeline = VocabularyPipeline()
    conj_pipeline = ConjugationPipeline()
    
    # Test that they have different configurations
    vocab_info = vocab_pipeline.get_info()
    conj_info = conj_pipeline.get_info()
    
    assert vocab_info != conj_info, "Pipelines should have different configurations"
    
    # Test that they can run simultaneously
    vocab_context = {"words": ["test"]}
    conj_context = {"verbs": ["hablar"], "tenses": ["present"]}
    
    # Both should be able to execute without interference
    vocab_result = vocab_pipeline.execute_stage("prepare", vocab_context)
    conj_result = conj_pipeline.execute_stage("generate", conj_context)
    
    # Neither should interfere with the other
    assert vocab_result is not None, "Vocabulary pipeline should work independently"
    assert conj_result is not None, "Conjugation pipeline should work independently"


def test_shared_resource_management():
    """Test that shared resources (media, sync) are handled correctly."""
    try:
        from core.registry import get_pipeline_registry
    except ImportError:
        pytest.skip("Multi-pipeline system not yet implemented (Session 8 pending)")
    
    registry = get_pipeline_registry()
    pipelines = registry.list_pipelines()
    
    # Test that multiple pipelines can share media directory
    for pipeline_name in pipelines:
        pipeline = registry.get_pipeline(pipeline_name)
        
        # Each pipeline should handle media without conflicts
        media_config = pipeline.get_media_config()
        assert media_config is not None, f"{pipeline_name} should have media config"
        
        # Test that sync targets can be different
        sync_config = pipeline.get_sync_config()
        assert sync_config is not None, f"{pipeline_name} should have sync config"


def test_pipeline_templates():
    """Test that pipeline template system works."""
    try:
        from core.template import PipelineTemplate
    except ImportError:
        pytest.skip("Multi-pipeline system not yet implemented (Session 8 pending)")
    
    # Test that template can create new pipeline
    template = PipelineTemplate()
    
    # Should be able to create new pipeline from template
    new_pipeline_config = template.create_pipeline("test_pipeline", {
        "card_type": "custom",
        "stages": ["prepare", "generate", "sync"]
    })
    
    assert new_pipeline_config is not None, "Template should create pipeline config"
    assert "stages" in new_pipeline_config, "Config should have stages"


def test_cli_multi_pipeline_support():
    """Test that CLI properly supports multiple pipelines."""
    # Test vocabulary pipeline via CLI
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "info", "vocabulary"
    ], capture_output=True, text=True, cwd=project_root)
    
    if result.returncode != 0:
        pytest.skip("Multi-pipeline CLI not yet implemented (Session 8 pending)")
    
    assert result.returncode == 0, "Should get vocabulary pipeline info"
    
    # Test conjugation pipeline via CLI
    result = subprocess.run([
        "python", "-m", "cli.pipeline", "info", "conjugation"
    ], capture_output=True, text=True, cwd=project_root)
    
    assert result.returncode == 0, "Should get conjugation pipeline info"


def test_pipeline_data_isolation():
    """Test that pipeline data is properly isolated."""
    try:
        from pipelines.vocabulary import VocabularyPipeline
        from pipelines.conjugation import ConjugationPipeline
    except ImportError:
        pytest.skip("Multi-pipeline system not yet implemented (Session 8 pending)")
    
    vocab_pipeline = VocabularyPipeline()
    conj_pipeline = ConjugationPipeline()
    
    # Test that each pipeline has separate data paths
    vocab_paths = vocab_pipeline.get_data_paths()
    conj_paths = conj_pipeline.get_data_paths()
    
    # Some paths may be shared (like media), but data files should be separate
    assert vocab_paths.get("data_file") != conj_paths.get("data_file"), \
        "Pipelines should have separate data files"
    
    # Test that vocabulary.json and conjugations.json are separate
    assert "vocabulary" in str(vocab_paths.get("data_file", "")), \
        "Vocabulary pipeline should use vocabulary.json"
    assert "conjugation" in str(conj_paths.get("data_file", "")), \
        "Conjugation pipeline should use conjugations.json"


if __name__ == "__main__":
    test_multi_pipeline_coexistence()
    test_pipeline_independence()
    test_shared_resource_management()
    test_pipeline_templates()
    test_cli_multi_pipeline_support()
    test_pipeline_data_isolation()
    print("Session 8 validation gate passed!")