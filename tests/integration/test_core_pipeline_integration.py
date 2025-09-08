#!/usr/bin/env python3
"""
Integration tests for core pipeline architecture.

Tests that pipeline registry and basic execution works.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_core_architecture():
    """
    Test core pipeline architecture integration.
    
    Tests:
    - Pipeline registry can be created and used
    - Registry provides consistent interface
    """
    try:
        from core.registry import get_pipeline_registry
    except ImportError:
        pytest.skip("Core architecture not available")
    
    # Test pipeline registry exists and works
    registry = get_pipeline_registry()
    assert registry is not None, "Pipeline registry should exist"
    
    # Test registry interface
    pipelines = registry.list_pipelines()
    assert pipelines is not None, "Registry should return pipeline list"
    assert isinstance(pipelines, (list, dict)), "Should return list or dict of pipelines"


def test_pipeline_registry_methods():
    """Test that pipeline registry has expected methods."""
    try:
        from core.registry import get_pipeline_registry
    except ImportError:
        pytest.skip("Core architecture not available")
    
    registry = get_pipeline_registry()
    
    # Test registry has expected methods
    assert hasattr(registry, 'list_pipelines'), "Registry should have list_pipelines method"
    assert hasattr(registry, 'has_pipeline'), "Registry should have has_pipeline method"
    assert hasattr(registry, 'register'), "Registry should have register method"
    
    # Test method behavior
    pipelines = registry.list_pipelines()
    if pipelines and len(pipelines) > 0:
        first_pipeline = list(pipelines)[0] if isinstance(pipelines, dict) else pipelines[0]
        exists = registry.has_pipeline(first_pipeline)
        assert isinstance(exists, bool), "has_pipeline should return boolean"


@pytest.mark.integration
def test_pipeline_context_integration():
    """Test pipeline context integration with core components."""
    try:
        from core.context import PipelineContext
        from pathlib import Path
    except ImportError:
        pytest.skip("Pipeline context not available")
    
    # Test context creation and basic operations
    context = PipelineContext(
        pipeline_name="test",
        project_root=Path("."),
        data={"test": "data"}
    )
    assert context is not None, "Context should be creatable"
    
    # Test context data operations
    context.set("key", "value")
    assert context.get("key") == "value", "Context should store and retrieve data"
    
    # Test context has expected attributes
    assert hasattr(context, 'completed_stages'), "Context should have completed_stages"
    assert hasattr(context, 'add_error'), "Context should have add_error method"


if __name__ == "__main__":
    test_core_architecture()
    test_pipeline_registry_methods()
    test_pipeline_context_integration()
    print("Core pipeline integration tests passed!")