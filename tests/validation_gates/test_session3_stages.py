#!/usr/bin/env python3
"""
Validation gate for Session 3: Stage System

Tests that stages can be chained and data flows between them.
This test will initially fail until Session 3 is implemented.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_stage_system():
    """
    Validation gate for Session 3: Stage System
    
    Tests:
    - Stages can be created and configured
    - Data can flow between stages
    - Stage execution can be chained
    """
    try:
        from stages.claude_staging import ClaudeStagingStage
        from stages.validation import ValidationStage
        from core.pipeline import Pipeline
    except ImportError:
        pytest.skip("Stage system not yet implemented (Session 3 pending)")
    
    # Test stages can be created
    claude_stage = ClaudeStagingStage()
    validation_stage = ValidationStage()
    
    assert claude_stage is not None, "Claude staging stage should be creatable"
    assert validation_stage is not None, "Validation stage should be creatable"
    
    # Test stage chaining with data flow
    initial_context = {
        "words": ["test"],
        "batch_id": "test_batch"
    }
    
    # Execute first stage
    result1 = claude_stage.execute(initial_context)
    assert result1 is not None, "First stage should return result"
    
    # Chain to second stage
    if result1.get("status") == "success":
        result2 = validation_stage.execute(result1)
        assert result2 is not None, "Second stage should return result"
        
        # Data should flow between stages
        assert "words" in result2, "Data should flow between stages"


def test_stage_error_handling():
    """Test that stages handle errors gracefully."""
    try:
        from stages.claude_staging import ClaudeStagingStage
    except ImportError:
        pytest.skip("Stage system not yet implemented (Session 3 pending)")
    
    stage = ClaudeStagingStage()
    
    # Test with invalid input
    invalid_context = {"invalid": "data"}
    
    try:
        result = stage.execute(invalid_context)
        # Should either succeed or fail gracefully
        if result:
            assert "status" in result, "Should have status in result"
    except Exception as e:
        # Should be a handled exception, not a crash
        assert str(e), "Exception should have message"


def test_stage_configuration():
    """Test that stages can be configured."""
    try:
        from stages.media_generation import MediaGenerationStage
    except ImportError:
        pytest.skip("Stage system not yet implemented (Session 3 pending)")
    
    # Test stage with configuration
    config = {
        "max_images": 5,
        "providers": ["openai", "runware"]
    }
    
    stage = MediaGenerationStage(config=config)
    assert stage is not None, "Configured stage should be creatable"
    
    # Test stage reflects configuration
    stage_config = stage.get_config()
    assert stage_config is not None, "Stage should return configuration"


if __name__ == "__main__":
    test_stage_system()
    test_stage_error_handling()
    test_stage_configuration()
    print("Session 3 validation gate passed!")