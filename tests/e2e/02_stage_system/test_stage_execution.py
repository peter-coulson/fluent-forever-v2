#!/usr/bin/env python3
"""
Session 3 Validation Gate: Stage Execution System

Tests the contract for individual stage execution.
These tests define how stages should execute, handle context,
and manage their lifecycle.

CONTRACT BEING TESTED:
- Stages can be executed independently
- Stages receive and process context correctly
- Stage results follow consistent format
- Stages handle errors appropriately
- Stage dependencies are managed correctly
"""

import pytest
from typing import Dict, Any, List
from tests.e2e.conftest import MockStage


class TestStageExecutionContract:
    """Test individual stage execution contracts"""
    
    def test_stage_basic_execution(self):
        """Contract: Stages execute with context and return results"""
        stage = MockStage("test_stage")
        
        context = {
            "input_data": {"cards": ["card1", "card2"]},
            "config": {"timeout": 30},
            "metadata": {"session_id": "test123"}
        }
        
        result = stage.execute(context)
        
        # Must return dictionary
        assert isinstance(result, dict)
        
        # Must indicate success status
        assert "status" in result
        assert result["status"] == "success"
        
        # Must identify the stage
        assert "stage" in result
        assert result["stage"] == "test_stage"
    
    def test_stage_context_processing(self):
        """Contract: Stages process context appropriately"""
        stage = MockStage("context_processor")
        
        # Rich context with various data types
        context = {
            "input_data": {
                "words": ["haber", "casa"],
                "batch_id": "batch_001"
            },
            "config": {
                "max_retries": 3,
                "timeout": 60,
                "dry_run": False
            },
            "metadata": {
                "user": "test_user",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
        
        result = stage.execute(context)
        
        # Result should contain processed output
        assert "output" in result
        
        # Original context should not be mutated
        assert context["input_data"]["words"] == ["haber", "casa"]
    
    def test_stage_error_handling(self):
        """Contract: Stages handle errors correctly"""
        failing_stage = MockStage("failing_stage", should_fail=True)
        
        context = {"input_data": {}}
        
        # Should raise appropriate exception
        with pytest.raises(RuntimeError, match="Stage failing_stage failed"):
            failing_stage.execute(context)
    
    def test_stage_with_minimal_context(self):
        """Contract: Stages work with minimal context"""
        stage = MockStage("minimal_stage")
        
        # Empty context
        result = stage.execute({})
        assert result["status"] == "success"
        
        # Context with only required fields
        minimal_context = {"input_data": {}}
        result = stage.execute(minimal_context)
        assert result["status"] == "success"
    
    def test_stage_execution_tracking(self):
        """Contract: Stage execution can be tracked"""
        stage = MockStage("trackable_stage")
        
        # Stage should track that it was executed
        assert not stage.executed
        
        stage.execute({"input_data": {}})
        
        # Should be marked as executed
        assert stage.executed
    
    def test_stage_output_format(self):
        """Contract: Stage output follows consistent format"""
        stage = MockStage("format_stage")
        
        context = {"input_data": {"test": "data"}}
        result = stage.execute(context)
        
        # Required fields
        assert "status" in result
        assert "stage" in result
        
        # Status should be valid
        assert result["status"] in ["success", "failure", "error", "skipped"]
        
        # Stage name should match
        assert result["stage"] == stage.name


class TestStageTypes:
    """Test different types of stages"""
    
    def test_data_processing_stage(self):
        """Contract: Data processing stages transform input data"""
        stage = MockDataProcessingStage("data_processor")
        
        context = {
            "input_data": {
                "words": ["haber", "casa", "comer"],
                "format": "raw"
            }
        }
        
        result = stage.execute(context)
        
        assert result["status"] == "success"
        assert "processed_data" in result
        assert len(result["processed_data"]["words"]) == 3
    
    def test_validation_stage(self):
        """Contract: Validation stages check data integrity"""
        stage = MockValidationStage("validator")
        
        # Valid data should pass
        valid_context = {
            "input_data": {
                "cards": [
                    {"CardID": "haber_aux", "SpanishWord": "haber"},
                    {"CardID": "casa_house", "SpanishWord": "casa"}
                ]
            }
        }
        
        result = stage.execute(valid_context)
        assert result["status"] == "success"
        assert result["validation_passed"] is True
        
        # Invalid data should fail validation
        invalid_context = {
            "input_data": {
                "cards": [
                    {"CardID": "", "SpanishWord": ""},  # Invalid empty fields
                ]
            }
        }
        
        result = stage.execute(invalid_context)
        assert result["status"] == "success"  # Stage executes successfully
        assert result["validation_passed"] is False  # But validation fails
    
    def test_io_stage(self):
        """Contract: I/O stages handle file operations"""
        stage = MockIOStage("file_processor")
        
        context = {
            "input_data": {
                "file_path": "/test/path/vocabulary.json",
                "operation": "read"
            }
        }
        
        result = stage.execute(context)
        
        assert result["status"] == "success"
        assert "file_data" in result
    
    def test_api_stage(self):
        """Contract: API stages handle external service calls"""
        stage = MockAPIStage("api_caller")
        
        context = {
            "input_data": {
                "endpoint": "images/generate",
                "params": {"prompt": "test image"}
            },
            "config": {
                "api_key": "test_key",
                "timeout": 30
            }
        }
        
        result = stage.execute(context)
        
        assert result["status"] == "success"
        assert "api_response" in result


class TestStageChaining:
    """Test stage execution chaining contracts"""
    
    def test_sequential_stage_outputs(self):
        """Contract: Stage outputs can be chained as inputs"""
        stage1 = MockDataProcessingStage("processor")
        stage2 = MockValidationStage("validator")
        
        # First stage processes data
        initial_context = {
            "input_data": {"words": ["haber", "casa"]}
        }
        
        result1 = stage1.execute(initial_context)
        assert result1["status"] == "success"
        
        # Second stage uses first stage's output
        chained_context = {
            "input_data": result1["processed_data"]
        }
        
        result2 = stage2.execute(chained_context)
        assert result2["status"] == "success"
    
    def test_context_accumulation(self):
        """Contract: Context can accumulate data from multiple stages"""
        stage1 = MockStage("stage1")
        stage2 = MockStage("stage2")
        
        # Start with initial context
        context = {
            "input_data": {"initial": "data"},
            "stage_results": {}
        }
        
        # Execute first stage
        result1 = stage1.execute(context)
        context["stage_results"]["stage1"] = result1
        
        # Execute second stage with accumulated context
        result2 = stage2.execute(context)
        context["stage_results"]["stage2"] = result2
        
        # Context should contain results from both stages
        assert "stage1" in context["stage_results"]
        assert "stage2" in context["stage_results"]


# Mock Stage Implementations for Testing
class MockDataProcessingStage(MockStage):
    """Mock data processing stage"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)  # Call parent to set executed flag
        
        input_data = context.get("input_data", {})
        words = input_data.get("words", [])
        
        # Simulate data processing
        processed_words = [{"word": word, "processed": True} for word in words]
        
        return {
            "status": "success",
            "stage": self.name,
            "processed_data": {
                "words": processed_words,
                "count": len(processed_words)
            }
        }


class MockValidationStage(MockStage):
    """Mock validation stage"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)
        
        input_data = context.get("input_data", {})
        
        # Simulate validation
        validation_passed = True
        validation_errors = []
        
        if "cards" in input_data:
            for card in input_data["cards"]:
                if not card.get("CardID") or not card.get("SpanishWord"):
                    validation_passed = False
                    validation_errors.append("Missing required fields")
        
        return {
            "status": "success",
            "stage": self.name,
            "validation_passed": validation_passed,
            "validation_errors": validation_errors
        }


class MockIOStage(MockStage):
    """Mock I/O stage"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)
        
        input_data = context.get("input_data", {})
        
        # Simulate file operation
        mock_file_data = {"mock": "file_content"}
        
        return {
            "status": "success",
            "stage": self.name,
            "file_data": mock_file_data,
            "operation": input_data.get("operation", "read")
        }


class MockAPIStage(MockStage):
    """Mock API stage"""
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        super().execute(context)
        
        input_data = context.get("input_data", {})
        
        # Simulate API call
        mock_response = {
            "success": True,
            "data": {"result": "mock_api_result"}
        }
        
        return {
            "status": "success",
            "stage": self.name,
            "api_response": mock_response,
            "endpoint": input_data.get("endpoint", "unknown")
        }