"""Unit tests for pipeline registry."""

import pytest
from pathlib import Path
from core.registry import PipelineRegistry, get_pipeline_registry
from core.pipeline import Pipeline
from core.stages import Stage, StageResult
from core.exceptions import PipelineNotFoundError, PipelineAlreadyRegisteredError


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""
    
    def __init__(self, name="mock", display_name="Mock Pipeline"):
        self._name = name
        self._display_name = display_name
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def display_name(self) -> str:
        return self._display_name
    
    @property
    def stages(self) -> list:
        return ["stage1", "stage2"]
    
    def get_stage(self, stage_name: str) -> Stage:
        raise NotImplementedError("Mock pipeline")
    
    @property
    def data_file(self) -> str:
        return "mock.json"
    
    @property
    def anki_note_type(self) -> str:
        return "Mock"


class TestPipelineRegistry:
    """Test cases for PipelineRegistry class."""
    
    def test_registry_creation(self):
        """Test registry creation."""
        registry = PipelineRegistry()
        assert registry.list_pipelines() == []
    
    def test_pipeline_registration(self):
        """Test pipeline registration."""
        registry = PipelineRegistry()
        pipeline = MockPipeline("test", "Test Pipeline")
        
        registry.register(pipeline)
        
        assert "test" in registry.list_pipelines()
        assert registry.has_pipeline("test")
        
        retrieved = registry.get("test")
        assert retrieved is pipeline
    
    def test_duplicate_registration_error(self):
        """Test that registering duplicate pipeline raises error."""
        registry = PipelineRegistry()
        pipeline1 = MockPipeline("test", "Test Pipeline 1")
        pipeline2 = MockPipeline("test", "Test Pipeline 2")
        
        registry.register(pipeline1)
        
        with pytest.raises(PipelineAlreadyRegisteredError) as exc_info:
            registry.register(pipeline2)
        
        assert "already registered" in str(exc_info.value)
    
    def test_get_nonexistent_pipeline(self):
        """Test getting non-existent pipeline raises error."""
        registry = PipelineRegistry()
        
        with pytest.raises(PipelineNotFoundError) as exc_info:
            registry.get("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    def test_pipeline_info(self):
        """Test getting pipeline information."""
        registry = PipelineRegistry()
        pipeline = MockPipeline("test", "Test Pipeline")
        registry.register(pipeline)
        
        info = registry.get_pipeline_info("test")
        
        assert info["name"] == "test"
        assert info["display_name"] == "Test Pipeline"
        assert info["stages"] == ["stage1", "stage2"]
        assert info["data_file"] == "mock.json"
        assert info["anki_note_type"] == "Mock"
        assert "description" in info
    
    def test_get_info_nonexistent_pipeline(self):
        """Test getting info for non-existent pipeline raises error."""
        registry = PipelineRegistry()
        
        with pytest.raises(PipelineNotFoundError):
            registry.get_pipeline_info("nonexistent")
    
    def test_get_all_pipeline_info(self):
        """Test getting all pipeline information."""
        registry = PipelineRegistry()
        pipeline1 = MockPipeline("test1", "Test Pipeline 1")
        pipeline2 = MockPipeline("test2", "Test Pipeline 2")
        
        registry.register(pipeline1)
        registry.register(pipeline2)
        
        all_info = registry.get_all_pipeline_info()
        
        assert "test1" in all_info
        assert "test2" in all_info
        assert all_info["test1"]["display_name"] == "Test Pipeline 1"
        assert all_info["test2"]["display_name"] == "Test Pipeline 2"
    
    def test_has_pipeline(self):
        """Test has_pipeline method."""
        registry = PipelineRegistry()
        pipeline = MockPipeline("test", "Test Pipeline")
        
        assert not registry.has_pipeline("test")
        
        registry.register(pipeline)
        assert registry.has_pipeline("test")
        assert not registry.has_pipeline("nonexistent")


class TestGlobalRegistry:
    """Test cases for global registry functions."""
    
    def test_global_registry_singleton(self):
        """Test that global registry is a singleton."""
        registry1 = get_pipeline_registry()
        registry2 = get_pipeline_registry()
        
        assert registry1 is registry2
    
    def test_global_registry_persistence(self):
        """Test that global registry persists registrations."""
        registry = get_pipeline_registry()
        pipeline = MockPipeline("global_test", "Global Test Pipeline")
        
        # Clear any existing registrations for clean test
        if registry.has_pipeline("global_test"):
            # Reset registry for test isolation
            registry._pipelines.clear()
        
        registry.register(pipeline)
        
        # Get registry again and verify pipeline is still there
        registry2 = get_pipeline_registry()
        assert registry2.has_pipeline("global_test")
        
        # Clean up for other tests
        registry._pipelines.clear()