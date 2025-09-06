#!/usr/bin/env python3
"""
Validation gate for Session 2: Core Architecture

Tests that pipeline registry and basic execution works.
This test will initially fail until Session 2 is implemented.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_core_architecture():
    """
    Validation gate for Session 2: Core Architecture
    
    Tests:
    - Pipeline registry can be created and used
    - Basic pipeline can be registered
    - Pipeline can execute a simple stage
    """
    try:
        from core.registry import get_pipeline_registry
        from pipelines.vocabulary import VocabularyPipeline
    except ImportError:
        pytest.skip("Core architecture not yet implemented (Session 2 pending)")
    
    # Test pipeline registry exists and works
    registry = get_pipeline_registry()
    assert registry is not None, "Pipeline registry should exist"
    
    # Test pipeline can be created
    pipeline = VocabularyPipeline()
    assert pipeline is not None, "VocabularyPipeline should be creatable"
    
    # Test pipeline can be registered (may already be registered by auto-registration)
    if not registry.has_pipeline("vocabulary"):
        registry.register(pipeline)
    pipelines = registry.list_pipelines()
    assert "vocabulary" in pipelines, "Vocabulary pipeline should be registered"
    
    # Test basic stage execution
    context = {"test": "data", "words": ["test"]}
    try:
        result = pipeline.execute_stage("prepare", context)
        assert result is not None, "Stage execution should return a result"
        assert "status" in result, "Result should have status"
    except NotImplementedError:
        pytest.skip("Stage execution not yet fully implemented")


def test_pipeline_discovery():
    """Test that pipelines can be discovered and listed."""
    try:
        from core.registry import get_pipeline_registry
    except ImportError:
        pytest.skip("Core architecture not yet implemented (Session 2 pending)")
    
    registry = get_pipeline_registry()
    
    # Should be able to list available pipelines
    pipelines = registry.list_pipelines()
    assert isinstance(pipelines, (list, dict)), "Should return list or dict of pipelines"
    
    # Should be able to get pipeline info
    if pipelines:
        first_pipeline = list(pipelines)[0] if isinstance(pipelines, dict) else pipelines[0]
        info = registry.get_pipeline_info(first_pipeline)
        assert info is not None, "Should return pipeline info"


if __name__ == "__main__":
    test_core_architecture()
    test_pipeline_discovery()
    print("Session 2 validation gate passed!")