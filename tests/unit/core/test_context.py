"""Unit tests for pipeline context."""

import pytest
from pathlib import Path
from core.context import PipelineContext


class TestPipelineContext:
    """Test cases for PipelineContext class."""
    
    def test_context_creation(self):
        """Test basic context creation."""
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        assert context.pipeline_name == "test"
        assert context.project_root == Path("/test")
        assert context.data == {}
        assert context.config == {}
        assert context.completed_stages == []
        assert context.errors == []
        assert context.args == {}
    
    def test_data_operations(self):
        """Test data get/set operations."""
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        # Test set and get
        context.set("key1", "value1")
        assert context.get("key1") == "value1"
        
        # Test get with default
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"
    
    def test_error_handling(self):
        """Test error handling methods."""
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        assert not context.has_errors()
        
        context.add_error("Test error")
        assert context.has_errors()
        assert "Test error" in context.errors
        
        context.add_error("Another error")
        assert len(context.errors) == 2
    
    def test_stage_completion_tracking(self):
        """Test stage completion tracking."""
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test")
        )
        
        assert "stage1" not in context.completed_stages
        
        context.mark_stage_complete("stage1")
        assert "stage1" in context.completed_stages
        
        # Should not duplicate
        context.mark_stage_complete("stage1")
        assert context.completed_stages.count("stage1") == 1
    
    def test_context_with_initial_data(self):
        """Test context creation with initial data."""
        initial_data = {"key": "value"}
        initial_config = {"setting": "value"}
        initial_args = {"arg": "value"}
        
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("/test"),
            data=initial_data,
            config=initial_config,
            args=initial_args
        )
        
        assert context.data == initial_data
        assert context.config == initial_config
        assert context.args == initial_args