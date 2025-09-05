"""Unit tests for pipeline base class."""

import pytest
from pathlib import Path
from core.pipeline import Pipeline
from core.stages import Stage, StageResult, StageStatus
from core.context import PipelineContext
from core.exceptions import StageNotFoundError


class MockStage(Stage):
    """Mock stage for testing."""
    
    def __init__(self, name, success=True, validation_errors=None):
        self._name = name
        self._success = success
        self._validation_errors = validation_errors or []
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Stage"
    
    def execute(self, context: PipelineContext) -> StageResult:
        if self._success:
            return StageResult.success(f"{self._name} completed", {self._name: True})
        else:
            return StageResult.failure(f"{self._name} failed", ["Test error"])
    
    def validate_context(self, context: PipelineContext) -> list:
        return self._validation_errors


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""
    
    def __init__(self, name="mock"):
        self._name = name
        self._stages = {
            "prepare": MockStage("prepare"),
            "process": MockStage("process"),
            "finish": MockStage("finish")
        }
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Pipeline"
    
    @property
    def stages(self) -> list:
        return list(self._stages.keys())
    
    def get_stage(self, stage_name: str) -> Stage:
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Stage '{stage_name}' not found")
        return self._stages[stage_name]
    
    @property
    def data_file(self) -> str:
        return f"{self._name}.json"
    
    @property
    def anki_note_type(self) -> str:
        return f"Mock {self._name.title()}"


class TestPipeline:
    """Test cases for Pipeline base class."""
    
    def test_pipeline_properties(self):
        """Test pipeline property access."""
        pipeline = MockPipeline("test")
        
        assert pipeline.name == "test"
        assert pipeline.display_name == "Mock Test Pipeline"
        assert pipeline.stages == ["prepare", "process", "finish"]
        assert pipeline.data_file == "test.json"
        assert pipeline.anki_note_type == "Mock Test"
    
    def test_get_stage(self):
        """Test getting stage by name."""
        pipeline = MockPipeline()
        
        stage = pipeline.get_stage("prepare")
        assert stage.name == "prepare"
        
        with pytest.raises(StageNotFoundError):
            pipeline.get_stage("nonexistent")
    
    def test_execute_stage_success(self):
        """Test successful stage execution."""
        pipeline = MockPipeline()
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        result = pipeline.execute_stage("prepare", context)
        
        assert result.status == StageStatus.SUCCESS
        assert "prepare completed" in result.message
        assert "prepare" in context.completed_stages
    
    def test_execute_stage_failure(self):
        """Test failed stage execution."""
        pipeline = MockPipeline()
        pipeline._stages["prepare"] = MockStage("prepare", success=False)
        
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        result = pipeline.execute_stage("prepare", context)
        
        assert result.status == StageStatus.FAILURE
        assert "prepare" not in context.completed_stages
    
    def test_execute_stage_validation_failure(self):
        """Test stage execution with validation failure."""
        pipeline = MockPipeline()
        pipeline._stages["prepare"] = MockStage(
            "prepare", 
            validation_errors=["Missing required field"]
        )
        
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        result = pipeline.execute_stage("prepare", context)
        
        assert result.status == StageStatus.FAILURE
        assert "Context validation failed" in result.message
        assert "Missing required field" in result.errors
    
    def test_execute_nonexistent_stage(self):
        """Test executing non-existent stage."""
        pipeline = MockPipeline()
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        result = pipeline.execute_stage("nonexistent", context)
        
        assert result.status == StageStatus.FAILURE
        assert "not found" in result.message
    
    def test_get_description(self):
        """Test getting pipeline description."""
        pipeline = MockPipeline("test")
        description = pipeline.get_description()
        
        assert "Mock Test Pipeline" in description
        assert "test.json" in description
    
    def test_get_stage_info(self):
        """Test getting stage information."""
        pipeline = MockPipeline()
        
        info = pipeline.get_stage_info("prepare")
        
        assert info["name"] == "prepare"
        assert info["display_name"] == "Mock Prepare Stage"
        assert "dependencies" in info
    
    def test_get_stage_info_nonexistent(self):
        """Test getting info for non-existent stage."""
        pipeline = MockPipeline()
        
        info = pipeline.get_stage_info("nonexistent")
        
        assert info == {}