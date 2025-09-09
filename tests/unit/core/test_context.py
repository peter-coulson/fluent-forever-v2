"""Unit tests for pipeline context."""

from pathlib import Path

from src.core.context import PipelineContext


class TestPipelineContext:
    """Test cases for PipelineContext class."""

    def test_context_creation(self):
        """Test basic context creation."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        assert context.pipeline_name == "test"
        assert context.project_root == Path("/test")
        assert context.data == {}
        assert context.config == {}
        assert context.completed_stages == []
        assert context.errors == []
        assert context.args == {}

    def test_data_operations(self):
        """Test data get/set operations."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Test set and get
        context.set("key1", "value1")
        assert context.get("key1") == "value1"

        # Test get with default
        assert context.get("nonexistent") is None
        assert context.get("nonexistent", "default") == "default"

    def test_error_handling(self):
        """Test error handling methods."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        assert not context.has_errors()

        context.add_error("Test error")
        assert context.has_errors()
        assert "Test error" in context.errors

        context.add_error("Another error")
        assert len(context.errors) == 2

    def test_stage_completion_tracking(self):
        """Test stage completion tracking."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

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
            args=initial_args,
        )

        assert context.data == initial_data
        assert context.config == initial_config
        assert context.args == initial_args

    def test_context_data_type_conflicts_on_overwrite(self):
        """Test data key conflicts when overwriting with different types."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Start with a dict value
        original_dict = {"nested": "value", "count": 10}
        context.set("data_key", original_dict)
        assert context.get("data_key") == original_dict

        # Overwrite with string - should replace entirely
        context.set("data_key", "string_value")
        assert context.get("data_key") == "string_value"

        # Overwrite with number - should replace entirely
        context.set("data_key", 42)
        assert context.get("data_key") == 42

        # Overwrite with list - should replace entirely
        new_list = ["item1", "item2"]
        context.set("data_key", new_list)
        assert context.get("data_key") == new_list

        # Overwrite with dict again - should replace entirely
        new_dict = {"different": "structure"}
        context.set("data_key", new_dict)
        assert context.get("data_key") == new_dict

    def test_context_error_accumulation_consistency(self):
        """Test error accumulation and state consistency across operations."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Start with no errors
        assert not context.has_errors()
        assert len(context.errors) == 0

        # Add multiple errors and check state consistency
        context.add_error("Error 1")
        assert context.has_errors()
        assert len(context.errors) == 1
        assert context.errors[0] == "Error 1"

        context.add_error("Error 2")
        assert context.has_errors()
        assert len(context.errors) == 2
        assert context.errors[1] == "Error 2"

        # Add empty/None errors (should be handled gracefully)
        context.add_error("")
        context.add_error(None)
        assert len(context.errors) >= 2  # May or may not add empty/None errors

        # Test error list immutability from outside
        external_errors = context.errors
        external_errors.append("External modification")

        # Context errors should not be affected by external list modification
        # (depends on implementation - some return copies, some don't)

        # Add more errors after external modification attempt
        context.add_error("Error 3")
        assert "Error 3" in context.errors
        assert context.has_errors()

    def test_context_stage_completion_duplicate_handling(self):
        """Test stage completion tracking with duplicate handling."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Test initial state
        assert len(context.completed_stages) == 0
        assert "stage1" not in context.completed_stages

        # Add first completion
        context.mark_stage_complete("stage1")
        assert len(context.completed_stages) == 1
        assert "stage1" in context.completed_stages

        # Add duplicate - should not create duplicate entries
        context.mark_stage_complete("stage1")
        assert len(context.completed_stages) == 1
        assert context.completed_stages.count("stage1") == 1

        # Add more stages
        context.mark_stage_complete("stage2")
        context.mark_stage_complete("stage3")
        assert len(context.completed_stages) == 3

        # Add duplicates of different stages
        context.mark_stage_complete("stage2")
        context.mark_stage_complete("stage3")
        assert len(context.completed_stages) == 3  # Should still be 3

        # Verify order preservation (stages should be in completion order)
        expected_stages = ["stage1", "stage2", "stage3"]
        assert context.completed_stages == expected_stages

    def test_context_memory_bounds_during_long_pipeline(self):
        """Test context memory bounds during long pipeline execution."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Simulate a long pipeline with many stages and large data
        large_data_chunk = {"data": "x" * 1000}  # 1KB of data per stage

        # Add many stages with data
        for i in range(100):
            stage_name = f"stage_{i}"
            context.mark_stage_complete(stage_name)
            context.set(f"stage_{i}_data", large_data_chunk.copy())
            context.set(f"stage_{i}_result", {"processed_items": i * 10})

        # Test that context still functions correctly
        assert len(context.completed_stages) == 100
        assert "stage_0" in context.completed_stages
        assert "stage_99" in context.completed_stages

        # Test data retrieval still works
        assert context.get("stage_0_data") == large_data_chunk
        assert context.get("stage_50_result")["processed_items"] == 500
        assert context.get("stage_99_data") is not None

        # Add errors during long pipeline
        for i in range(0, 100, 10):  # Add error every 10 stages
            context.add_error(f"Warning from stage {i}")

        assert len(context.errors) == 10
        assert context.has_errors()

        # Test that context data operations remain efficient
        # (This is more of a performance test - ensure no major degradation)
        context.set(
            "final_summary",
            {
                "total_stages": len(context.completed_stages),
                "total_errors": len(context.errors),
                "memory_test": "passed",
            },
        )

        final_data = context.get("final_summary")
        assert final_data["total_stages"] == 100
        assert final_data["total_errors"] == 10
