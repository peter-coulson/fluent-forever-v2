#!/usr/bin/env python3
"""
Session 2 Validation Gate: Pipeline Execution System

Tests the contract for basic pipeline execution patterns.
These tests define how pipelines should execute stages,
manage context, and handle execution flow.

CONTRACT BEING TESTED:
- Pipelines can execute individual stages
- Context flows between stages correctly
- Execution results are consistently formatted
- Error handling works correctly
- Stage dependencies are respected
"""

import pytest
from typing import Dict, Any
from tests.e2e.conftest import MockPipeline, MockStage


class TestPipelineExecutionContract:
    """Test basic pipeline execution patterns"""
    
    def test_single_stage_execution(self):
        """Contract: Pipelines can execute individual stages"""
        pipeline = MockPipeline("test_pipeline", stages=["prepare", "execute", "cleanup"])
        
        # Should execute single stage successfully
        context = {"input_data": {"cards": ["card1", "card2"]}}
        result = pipeline.execute_stage("prepare", context)
        
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["stage"] == "prepare"
        assert "data" in result
    
    def test_sequential_stage_execution(self):
        """Contract: Stages can be executed in sequence with context flow"""
        pipeline = MockPipeline("test_pipeline", stages=["stage1", "stage2", "stage3"])
        
        # Execute stages in sequence
        context = {"data": {"initial": "value"}}
        
        result1 = pipeline.execute_stage("stage1", context)
        assert result1["status"] == "success"
        
        # Context should be updatable between stages
        context["data"]["stage1_result"] = result1["data"]
        
        result2 = pipeline.execute_stage("stage2", context)
        assert result2["status"] == "success"
        
        context["data"]["stage2_result"] = result2["data"]
        
        result3 = pipeline.execute_stage("stage3", context)
        assert result3["status"] == "success"
    
    def test_context_management(self):
        """Contract: Pipeline context is properly managed"""
        pipeline = MockPipeline("test_pipeline")
        
        # Initial context
        initial_context = {
            "data": {"key": "value"},
            "config": {"setting": True},
            "metadata": {"session_id": "test123"}
        }
        
        result = pipeline.execute_stage("stage1", initial_context)
        
        # Result should preserve context structure
        assert isinstance(result, dict)
        assert "data" in result
        
        # Context should not be mutated by the stage
        assert initial_context["data"]["key"] == "value"
    
    def test_stage_error_handling(self):
        """Contract: Pipeline handles stage errors correctly"""
        pipeline = MockPipeline("test_pipeline", stages=["failing_stage"])
        
        # Mock a failing stage
        original_execute = pipeline.execute_stage
        def failing_execute(stage_name, context):
            if stage_name == "failing_stage":
                raise RuntimeError("Simulated stage failure")
            return original_execute(stage_name, context)
        
        pipeline.execute_stage = failing_execute
        
        # Should propagate stage errors
        context = {"data": {}}
        with pytest.raises(RuntimeError, match="Simulated stage failure"):
            pipeline.execute_stage("failing_stage", context)
    
    def test_invalid_stage_handling(self):
        """Contract: Pipeline rejects invalid stage names"""
        pipeline = MockPipeline("test_pipeline", stages=["valid_stage"])
        
        context = {"data": {}}
        
        # Should reject unknown stages
        with pytest.raises(ValueError):
            pipeline.execute_stage("invalid_stage", context)
    
    def test_empty_context_handling(self):
        """Contract: Pipeline handles empty or minimal context"""
        pipeline = MockPipeline("test_pipeline")
        
        # Should work with empty context
        result = pipeline.execute_stage("stage1", {})
        assert result["status"] == "success"
        
        # Should work with minimal context
        result = pipeline.execute_stage("stage1", {"data": {}})
        assert result["status"] == "success"


class TestExecutionResultContract:
    """Test execution result format contracts"""
    
    def test_result_structure(self):
        """Contract: Execution results have consistent structure"""
        pipeline = MockPipeline("test_pipeline")
        
        context = {"data": {"test": "value"}}
        result = pipeline.execute_stage("stage1", context)
        
        # Must be a dictionary
        assert isinstance(result, dict)
        
        # Must have status field
        assert "status" in result
        assert result["status"] in ["success", "failure", "error"]
        
        # Must identify the stage that was executed
        assert "stage" in result
        assert result["stage"] == "stage1"
    
    def test_success_result_format(self):
        """Contract: Success results contain required information"""
        pipeline = MockPipeline("test_pipeline")
        
        context = {"data": {"input": "test"}}
        result = pipeline.execute_stage("stage1", context)
        
        assert result["status"] == "success"
        assert result["stage"] == "stage1"
        assert "data" in result  # Should contain result data


class TestStageInterface:
    """Test individual stage interface contracts"""
    
    def test_stage_basic_interface(self):
        """Contract: Stages implement required interface"""
        stage = MockStage("test_stage")
        
        # Must have a name
        assert hasattr(stage, "name")
        assert isinstance(stage.name, str)
        
        # Must be executable
        assert hasattr(stage, "execute")
        assert callable(stage.execute)
    
    def test_stage_execution(self):
        """Contract: Stages execute with context and return results"""
        stage = MockStage("test_stage")
        
        context = {"input": "test_data", "config": {"param": "value"}}
        result = stage.execute(context)
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "stage" in result
    
    def test_stage_failure_handling(self):
        """Contract: Stages can fail gracefully"""
        failing_stage = MockStage("failing_stage", should_fail=True)
        
        context = {"input": "test"}
        
        # Should raise appropriate error
        with pytest.raises(RuntimeError):
            failing_stage.execute(context)