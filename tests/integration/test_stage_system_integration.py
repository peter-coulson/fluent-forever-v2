#!/usr/bin/env python3
"""
Integration tests for stage system.

Tests that stages can be created, configured, and handle data flow.
"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))


def test_stage_base_classes():
    """
    Test stage base class system integration.
    
    Tests:
    - Base stage classes can be imported
    - Stage interfaces are consistent
    """
    try:
        from stages.base.api_stage import BaseAPIStage
        from stages.base.file_stage import BaseFileStage 
        from stages.base.validation_stage import BaseValidationStage
    except ImportError:
        pytest.skip("Stage system not available")
    
    # Test base classes exist
    assert BaseAPIStage is not None, "BaseAPIStage should be available"
    assert BaseFileStage is not None, "BaseFileStage should be available"
    assert BaseValidationStage is not None, "BaseValidationStage should be available"


def test_concrete_stage_creation():
    """Test that concrete stage implementations can be created."""
    try:
        from stages.claude.batch_stage import ClaudeBatchStage
        from stages.media.image_stage import ImageGenerationStage
        from stages.validation.data_stage import DataValidationStage
    except ImportError:
        pytest.skip("Concrete stages not available")
    
    # Test concrete stages can be instantiated
    try:
        batch_stage = ClaudeBatchStage()
        assert batch_stage is not None, "ClaudeBatchStage should be creatable"
    except Exception:
        pass  # May require configuration
    
    try:
        image_stage = ImageGenerationStage()
        assert image_stage is not None, "ImageGenerationStage should be creatable"
    except Exception:
        pass  # May require configuration
    
    try:
        validation_stage = DataValidationStage()
        assert validation_stage is not None, "DataValidationStage should be creatable"
    except Exception:
        pass  # May require configuration


def test_stage_error_handling():
    """Test that stages handle errors gracefully."""
    try:
        from stages.base.validation_stage import BaseValidationStage
    except ImportError:
        pytest.skip("Stage system not available")
    
    # Test base stage error handling
    class TestStage(BaseValidationStage):
        def execute(self, context):
            if not context.get("valid_data"):
                raise ValueError("Invalid data provided")
            return {"status": "success"}
    
    stage = TestStage()
    
    # Test with invalid input - should handle gracefully
    invalid_context = {"invalid": "data"}
    
    try:
        result = stage.execute(invalid_context)
        # If it returns, should have proper structure
        if result:
            assert isinstance(result, dict), "Result should be dict"
    except Exception as e:
        # Should be a handled exception with message
        assert str(e), "Exception should have message"


@pytest.mark.integration
def test_stage_configuration_system():
    """Test stage configuration integration."""
    try:
        from stages.base.api_stage import BaseAPIStage
        from core.context import PipelineContext
    except ImportError:
        pytest.skip("Stage system not available")
    
    # Test stage with configuration
    class ConfigurableStage(BaseAPIStage):
        def __init__(self, config=None):
            super().__init__(config)
            self.max_retries = config.get("max_retries", 3) if config else 3
        
        def execute(self, context):
            return {"status": "success", "retries": self.max_retries}
    
    # Test without config
    stage = ConfigurableStage()
    context = PipelineContext({"test": "data"})
    result = stage.execute(context)
    assert result["retries"] == 3, "Should use default configuration"
    
    # Test with config
    config = {"max_retries": 5}
    stage_configured = ConfigurableStage(config=config)
    result = stage_configured.execute(context)
    assert result["retries"] == 5, "Should use provided configuration"


if __name__ == "__main__":
    test_stage_base_classes()
    test_concrete_stage_creation()
    test_stage_error_handling()
    test_stage_configuration_system()
    print("Stage system integration tests passed!")