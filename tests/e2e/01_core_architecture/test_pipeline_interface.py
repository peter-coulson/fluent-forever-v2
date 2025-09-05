#!/usr/bin/env python3
"""
Session 2 Validation Gate: Pipeline Interface Compliance

Tests the contract for pipeline abstract interface compliance.
These tests define the core interface that all pipelines must implement.

CONTRACT BEING TESTED:
- All pipelines implement required abstract methods
- Pipeline metadata is accessible and consistent
- Pipeline configuration is properly handled
- Pipeline lifecycle methods work correctly
"""

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from tests.e2e.conftest import MockPipeline


class PipelineInterface(ABC):
    """Abstract pipeline interface that all pipelines must implement"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique pipeline name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable pipeline description"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Pipeline version"""
        pass
    
    @abstractmethod
    def get_available_stages(self) -> List[str]:
        """Get list of available stages"""
        pass
    
    @abstractmethod
    def execute_stage(self, stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific stage"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate pipeline configuration"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get pipeline metadata and information"""
        pass


class TestPipelineInterfaceCompliance:
    """Test that pipelines comply with the interface contract"""
    
    def test_pipeline_has_required_properties(self):
        """Contract: Pipelines have required metadata properties"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Must have name
        assert hasattr(pipeline, 'name')
        assert isinstance(pipeline.name, str)
        assert pipeline.name != ""
        
        # Must have description
        assert hasattr(pipeline, 'description')
        assert isinstance(pipeline.description, str)
        
        # Must have version
        assert hasattr(pipeline, 'version')
        assert isinstance(pipeline.version, str)
    
    def test_pipeline_stage_methods(self):
        """Contract: Pipelines implement stage-related methods"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Must provide available stages
        stages = pipeline.get_available_stages()
        assert isinstance(stages, list)
        assert all(isinstance(stage, str) for stage in stages)
        
        # Must be able to execute stages
        if stages:
            context = {"data": {}}
            result = pipeline.execute_stage(stages[0], context)
            assert isinstance(result, dict)
    
    def test_pipeline_configuration_validation(self):
        """Contract: Pipelines validate their configuration"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Valid configuration should pass
        valid_config = {
            "enabled": True,
            "max_retries": 3,
            "timeout": 30
        }
        assert pipeline.validate_config(valid_config) is True
        
        # Invalid configuration should fail
        invalid_config = {
            "max_retries": "not_a_number",
            "timeout": -1
        }
        assert pipeline.validate_config(invalid_config) is False
    
    def test_pipeline_info_method(self):
        """Contract: Pipelines provide comprehensive information"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        info = pipeline.get_info()
        assert isinstance(info, dict)
        
        # Must contain basic metadata
        assert "name" in info
        assert "description" in info
        assert "version" in info
        assert "stages" in info
        
        # Stages should be listed
        assert isinstance(info["stages"], list)
        assert len(info["stages"]) > 0


class TestPipelineMetadata:
    """Test pipeline metadata contracts"""
    
    def test_pipeline_name_requirements(self):
        """Contract: Pipeline names follow conventions"""
        pipeline = MockEnhancedPipeline("vocabulary")
        
        # Name should be alphanumeric with underscores
        assert pipeline.name.replace("_", "").isalnum()
        
        # Name should be lowercase
        assert pipeline.name.islower()
        
        # Name should not be empty
        assert len(pipeline.name) > 0
    
    def test_pipeline_version_format(self):
        """Contract: Pipeline versions follow semantic versioning"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Version should follow x.y.z format
        version_parts = pipeline.version.split(".")
        assert len(version_parts) >= 2  # At least major.minor
        assert all(part.isdigit() for part in version_parts)
    
    def test_pipeline_description_quality(self):
        """Contract: Pipeline descriptions are meaningful"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Description should not be empty
        assert len(pipeline.description) > 0
        
        # Description should contain the pipeline name or purpose
        assert any(word in pipeline.description.lower() 
                  for word in [pipeline.name, "pipeline", "cards", "vocabulary"])


class TestPipelineLifecycle:
    """Test pipeline lifecycle contracts"""
    
    def test_pipeline_initialization(self):
        """Contract: Pipelines initialize correctly"""
        # Should be able to create pipeline
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        # Basic properties should be accessible immediately
        assert pipeline.name == "test_pipeline"
        assert len(pipeline.get_available_stages()) > 0
    
    def test_pipeline_configuration_loading(self):
        """Contract: Pipelines handle configuration loading"""
        pipeline = MockEnhancedPipeline("test_pipeline")
        
        config = {
            "enabled": True,
            "stages": {
                "stage1": {"timeout": 30},
                "stage2": {"retries": 3}
            }
        }
        
        # Should validate configuration
        assert pipeline.validate_config(config) is True
        
        # Should be able to apply configuration (if supported)
        # This is tested by checking that the pipeline doesn't crash
        info = pipeline.get_info()
        assert isinstance(info, dict)


# Mock Implementation for Interface Testing
class MockEnhancedPipeline(PipelineInterface):
    """Enhanced mock pipeline that implements the full interface"""
    
    def __init__(self, name: str):
        self._name = name
        self._stages = ["prepare", "process", "finalize"]
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return f"Test pipeline for {self._name} processing"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_available_stages(self) -> List[str]:
        return self._stages.copy()
    
    def execute_stage(self, stage_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if stage_name not in self._stages:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        return {
            "status": "success",
            "stage": stage_name,
            "pipeline": self._name,
            "data": context.get("data", {})
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration - simple validation for testing"""
        if not isinstance(config, dict):
            return False
        
        # Check for invalid values
        if "max_retries" in config:
            if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
                return False
        
        if "timeout" in config:
            if not isinstance(config["timeout"], (int, float)) or config["timeout"] <= 0:
                return False
        
        return True
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "stages": self.get_available_stages(),
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "author": "test"
            }
        }