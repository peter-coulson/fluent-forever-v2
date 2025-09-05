"""Unit tests for stage system."""

import pytest
from pathlib import Path
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext


class MockStage(Stage):
    """Mock stage for testing."""
    
    def __init__(self, name="mock", display_name="Mock Stage", dependencies=None, validation_errors=None):
        self._name = name
        self._display_name = display_name
        self._dependencies = dependencies or []
        self._validation_errors = validation_errors or []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def display_name(self) -> str:
        return self._display_name
    
    @property
    def dependencies(self) -> list:
        return self._dependencies
    
    def execute(self, context: PipelineContext) -> StageResult:
        return StageResult.success("Mock execution completed", {"mock": True})
    
    def validate_context(self, context: PipelineContext) -> list:
        return self._validation_errors


class TestStageResult:
    """Test cases for StageResult class."""
    
    def test_success_result(self):
        """Test success result creation."""
        result = StageResult.success("Success message", {"key": "value"})
        
        assert result.status == StageStatus.SUCCESS
        assert result.message == "Success message"
        assert result.data == {"key": "value"}
        assert result.errors == []
    
    def test_failure_result(self):
        """Test failure result creation."""
        result = StageResult.failure("Failure message", ["error1", "error2"])
        
        assert result.status == StageStatus.FAILURE
        assert result.message == "Failure message"
        assert result.data == {}
        assert result.errors == ["error1", "error2"]
    
    def test_partial_result(self):
        """Test partial result creation."""
        result = StageResult.partial(
            "Partial message", 
            {"key": "value"}, 
            ["warning1"]
        )
        
        assert result.status == StageStatus.PARTIAL
        assert result.message == "Partial message"
        assert result.data == {"key": "value"}
        assert result.errors == ["warning1"]
    
    def test_skipped_result(self):
        """Test skipped result creation."""
        result = StageResult.skipped("Skipped message")
        
        assert result.status == StageStatus.SKIPPED
        assert result.message == "Skipped message"
        assert result.data == {}
        assert result.errors == []


class TestStage:
    """Test cases for Stage base class."""
    
    def test_stage_properties(self):
        """Test stage property access."""
        stage = MockStage(
            name="test_stage",
            display_name="Test Stage",
            dependencies=["dep1", "dep2"]
        )
        
        assert stage.name == "test_stage"
        assert stage.display_name == "Test Stage"
        assert stage.dependencies == ["dep1", "dep2"]
    
    def test_stage_execution(self):
        """Test stage execution."""
        stage = MockStage()
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        result = stage.execute(context)
        assert result.status == StageStatus.SUCCESS
        assert "Mock execution completed" in result.message
    
    def test_context_validation(self):
        """Test context validation."""
        stage = MockStage(validation_errors=["Missing required field"])
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        errors = stage.validate_context(context)
        assert errors == ["Missing required field"]
        
        # Test stage with no validation errors
        clean_stage = MockStage()
        errors = clean_stage.validate_context(context)
        assert errors == []
    
    def test_stage_defaults(self):
        """Test stage default values."""
        stage = MockStage()
        
        assert stage.dependencies == []
        
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        assert stage.validate_context(context) == []