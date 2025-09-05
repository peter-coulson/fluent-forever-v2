#!/usr/bin/env python3
"""
Session 2 Validation Gate: Pipeline Registry System

Tests the contract for pipeline registration and discovery.
These tests define how pipelines should be registered, discovered,
and managed by the core system.

CONTRACT BEING TESTED:
- Pipelines can be registered with unique names
- Pipelines can be discovered and retrieved by name
- Registry prevents duplicate pipeline names
- Registry provides listing and introspection capabilities
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockPipeline


class TestPipelineRegistryContract:
    """Test pipeline registry basic operations"""
    
    def test_pipeline_registration(self):
        """Contract: Pipelines can be registered with the registry"""
        # This test will be implemented when the registry exists
        # For now, it defines the expected interface
        
        # Expected interface:
        # registry = get_pipeline_registry()
        # pipeline = VocabularyPipeline()
        # registry.register(pipeline)
        # assert pipeline.name in registry.list_pipelines()
        
        # Mock implementation for interface validation
        registry = MockPipelineRegistry()
        pipeline = MockPipeline("vocabulary")
        
        registry.register(pipeline)
        
        assert pipeline.name in registry.list_pipelines()
        assert registry.get_pipeline(pipeline.name) == pipeline
    
    def test_pipeline_discovery(self):
        """Contract: Registered pipelines can be discovered"""
        registry = MockPipelineRegistry()
        
        # Register multiple pipelines
        vocab_pipeline = MockPipeline("vocabulary")
        conj_pipeline = MockPipeline("conjugation")
        
        registry.register(vocab_pipeline)
        registry.register(conj_pipeline)
        
        # Should be able to discover all pipelines
        pipeline_names = registry.list_pipelines()
        assert "vocabulary" in pipeline_names
        assert "conjugation" in pipeline_names
        
        # Should be able to retrieve specific pipelines
        assert registry.get_pipeline("vocabulary") == vocab_pipeline
        assert registry.get_pipeline("conjugation") == conj_pipeline
    
    def test_duplicate_pipeline_prevention(self):
        """Contract: Registry prevents duplicate pipeline names"""
        registry = MockPipelineRegistry()
        
        pipeline1 = MockPipeline("vocabulary")
        pipeline2 = MockPipeline("vocabulary")  # Same name
        
        registry.register(pipeline1)
        
        # Should raise error when registering duplicate name
        with pytest.raises(ValueError, match="already registered"):
            registry.register(pipeline2)
    
    def test_pipeline_info_retrieval(self):
        """Contract: Registry provides pipeline information"""
        registry = MockPipelineRegistry()
        pipeline = MockPipeline("vocabulary", stages=["claude_batch", "media_gen", "sync"])
        
        registry.register(pipeline)
        
        # Should provide pipeline information
        info = registry.get_pipeline_info("vocabulary")
        assert info["name"] == "vocabulary"
        assert "stages" in info
        assert "claude_batch" in info["stages"]
    
    def test_nonexistent_pipeline_handling(self):
        """Contract: Registry handles requests for non-existent pipelines"""
        registry = MockPipelineRegistry()
        
        # Should return None for non-existent pipeline
        assert registry.get_pipeline("nonexistent") is None
        
        # Should raise error when getting info for non-existent pipeline
        with pytest.raises(KeyError):
            registry.get_pipeline_info("nonexistent")


class TestPipelineInterface:
    """Test the pipeline interface contract"""
    
    def test_pipeline_basic_interface(self):
        """Contract: All pipelines implement basic interface"""
        pipeline = MockPipeline("test_pipeline")
        
        # Must have a name
        assert hasattr(pipeline, "name")
        assert isinstance(pipeline.name, str)
        assert pipeline.name != ""
        
        # Must provide available stages
        stages = pipeline.get_available_stages()
        assert isinstance(stages, list)
        assert all(isinstance(stage, str) for stage in stages)
        
        # Must provide pipeline info
        info = pipeline.get_info()
        assert isinstance(info, dict)
        assert "name" in info
        assert "stages" in info
    
    def test_pipeline_stage_execution(self):
        """Contract: Pipelines can execute individual stages"""
        pipeline = MockPipeline("test_pipeline", stages=["stage1", "stage2"])
        
        # Should execute valid stages
        context = {"data": {"test": "value"}}
        result = pipeline.execute_stage("stage1", context)
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["stage"] == "stage1"
        
        # Should reject invalid stages
        with pytest.raises(ValueError):
            pipeline.execute_stage("invalid_stage", context)


# Mock Registry Implementation for Contract Testing
class MockPipelineRegistry:
    """Mock pipeline registry for testing contracts"""
    
    def __init__(self):
        self._pipelines: Dict[str, MockPipeline] = {}
    
    def register(self, pipeline: MockPipeline):
        if pipeline.name in self._pipelines:
            raise ValueError(f"Pipeline {pipeline.name} already registered")
        self._pipelines[pipeline.name] = pipeline
    
    def get_pipeline(self, name: str) -> MockPipeline:
        return self._pipelines.get(name)
    
    def list_pipelines(self) -> List[str]:
        return list(self._pipelines.keys())
    
    def get_pipeline_info(self, name: str) -> Dict[str, Any]:
        if name not in self._pipelines:
            raise KeyError(f"Pipeline {name} not found")
        return self._pipelines[name].get_info()