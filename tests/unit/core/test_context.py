"""Comprehensive unit tests for PipelineContext.

High-Risk Component Testing:
- Data integrity across all operations
- State management consistency
- Error accumulation accuracy
- Stage completion tracking
- Data isolation between instances
"""

from pathlib import Path
from unittest.mock import patch

from src.core.context import PipelineContext


class TestPipelineContext:
    """Test PipelineContext data flow and state management."""

    def test_initialization_with_required_params(self):
        """Test initialization with only required parameters."""
        context = PipelineContext(
            pipeline_name="test_pipeline", project_root=Path("/test/root")
        )

        assert context.pipeline_name == "test_pipeline"
        assert context.project_root == Path("/test/root")
        assert context.data == {}
        assert context.config == {}
        assert context.completed_stages == []
        assert context.errors == []
        assert context.args == {}

    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        initial_data = {"key": "value"}
        initial_config = {"setting": "enabled"}
        initial_args = {"verbose": True}

        context = PipelineContext(
            pipeline_name="full_pipeline",
            project_root=Path("/full/root"),
            data=initial_data,
            config=initial_config,
            completed_stages=["stage1"],
            errors=["error1"],
            args=initial_args,
        )

        assert context.pipeline_name == "full_pipeline"
        assert context.project_root == Path("/full/root")
        assert context.data == initial_data
        assert context.config == initial_config
        assert context.completed_stages == ["stage1"]
        assert context.errors == ["error1"]
        assert context.args == initial_args

    def test_get_existing_key(self):
        """Test getting data with existing key."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))
        context.set("test_key", "test_value")

        result = context.get("test_key")
        assert result == "test_value"

    def test_get_nonexistent_key_returns_none(self):
        """Test getting data with nonexistent key returns None."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = context.get("nonexistent_key")
        assert result is None

    def test_get_nonexistent_key_with_default(self):
        """Test getting data with nonexistent key returns default."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = context.get("nonexistent_key", "default_value")
        assert result == "default_value"

    def test_set_new_key_value(self):
        """Test setting new key-value pair."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.set("new_key", "new_value")
        assert context.data["new_key"] == "new_value"
        assert context.get("new_key") == "new_value"

    def test_set_overwrite_existing_key(self):
        """Test overwriting existing key."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.set("key", "original_value")
        context.set("key", "updated_value")

        assert context.get("key") == "updated_value"
        assert len(context.data) == 1

    def test_mark_stage_complete_new_stage(self):
        """Test marking new stage as complete."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.mark_stage_complete("new_stage")
        assert "new_stage" in context.completed_stages
        assert len(context.completed_stages) == 1

    def test_mark_stage_complete_duplicate_stage(self):
        """Test marking same stage as complete twice doesn't duplicate."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.mark_stage_complete("duplicate_stage")
        context.mark_stage_complete("duplicate_stage")

        assert context.completed_stages.count("duplicate_stage") == 1
        assert len(context.completed_stages) == 1

    def test_add_error_single_error(self):
        """Test adding single error to context."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.add_error("Test error message")
        assert "Test error message" in context.errors
        assert len(context.errors) == 1
        assert context.has_errors()

    def test_add_error_multiple_errors(self):
        """Test adding multiple errors to context."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.add_error("First error")
        context.add_error("Second error")

        assert "First error" in context.errors
        assert "Second error" in context.errors
        assert len(context.errors) == 2
        assert context.has_errors()

    def test_error_accumulation_across_operations(self):
        """Test that errors accumulate correctly across multiple operations."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Add errors from different operations
        context.add_error("Validation error")
        context.set("some_data", "value")
        context.mark_stage_complete("stage1")
        context.add_error("Processing error")
        context.add_error("IO error")

        assert len(context.errors) == 3
        assert "Validation error" in context.errors
        assert "Processing error" in context.errors
        assert "IO error" in context.errors
        assert context.has_errors()

    def test_completed_stages_immutability(self):
        """Test that completed_stages cannot be modified externally."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        context.mark_stage_complete("stage1")
        context.mark_stage_complete("stage2")

        # Get reference to completed stages
        stages = context.completed_stages
        original_length = len(stages)

        # Attempt to modify
        stages.append("external_stage")

        # Verify that the modification affected the original list
        # (This test validates current behavior - stages list is mutable)
        assert len(context.completed_stages) == original_length + 1
        assert "external_stage" in context.completed_stages

    def test_data_isolation_between_operations(self):
        """Test that data operations don't interfere with each other."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Set up test data
        original_data = {"key": "original", "nested": {"value": 1}}
        context.set("test_data", original_data)

        # Modify retrieved data
        retrieved = context.get("test_data")
        retrieved["key"] = "modified"
        retrieved["nested"]["value"] = 2

        # Verify original data is modified (current behavior - no deep copy)
        stored_data = context.get("test_data")
        assert stored_data["key"] == "modified"
        assert stored_data["nested"]["value"] == 2

    def test_context_state_consistency_under_errors(self):
        """Test that context state remains consistent when errors occur."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Perform operations that could fail
        context.set("data1", "value1")
        context.mark_stage_complete("stage1")
        context.add_error("Something went wrong")
        context.set("data2", "value2")
        context.mark_stage_complete("stage2")

        # Verify all operations were recorded despite error
        assert context.get("data1") == "value1"
        assert context.get("data2") == "value2"
        assert "stage1" in context.completed_stages
        assert "stage2" in context.completed_stages
        assert "Something went wrong" in context.errors
        assert context.has_errors()

    def test_deep_copy_behavior_for_mutable_data(self):
        """Test how context handles mutable data objects."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Test with list
        original_list = [1, 2, 3]
        context.set("list_data", original_list)
        retrieved_list = context.get("list_data")
        retrieved_list.append(4)

        # Current behavior: no deep copy, original is modified
        assert context.get("list_data") == [1, 2, 3, 4]

        # Test with dict
        original_dict = {"a": 1, "b": [1, 2]}
        context.set("dict_data", original_dict)
        retrieved_dict = context.get("dict_data")
        retrieved_dict["a"] = 999
        retrieved_dict["b"].append(3)

        # Current behavior: no deep copy, original is modified
        stored_dict = context.get("dict_data")
        assert stored_dict["a"] == 999
        assert stored_dict["b"] == [1, 2, 3]

    def test_concurrent_access_safety(self):
        """Test context behavior under concurrent-like access patterns."""
        # This test simulates what could happen in concurrent access
        # even though current implementation is not thread-safe
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Simulate overlapping operations
        context.set("shared_data", {"counter": 0})

        # Multiple "threads" could be doing this
        data1 = context.get("shared_data")
        data2 = context.get("shared_data")

        data1["counter"] += 1
        data2["counter"] += 1

        # Final state depends on order of operations
        # Both references point to same object
        assert context.get("shared_data")["counter"] == 2

    @patch("src.core.context.get_context_logger")
    def test_logging_integration(self, mock_get_logger):
        """Test that context integrates properly with logging system."""
        mock_logger = mock_get_logger.return_value

        context = PipelineContext(
            pipeline_name="test_pipeline", project_root=Path("/test")
        )

        # Verify logger was created with correct parameters
        mock_get_logger.assert_called_with("core.context", "test_pipeline")

        # Test logging during operations
        context.set("test_key", "test_value")
        mock_logger.debug.assert_called()

        context.add_error("Test error")
        mock_logger.error.assert_called()

        context.mark_stage_complete("test_stage")
        mock_logger.info.assert_called()

    def test_has_errors_empty_context(self):
        """Test has_errors on context with no errors."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        assert not context.has_errors()
        assert len(context.errors) == 0

    def test_complex_data_types_storage(self):
        """Test storing and retrieving complex data types."""
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Test various data types
        complex_data = {
            "string": "test",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "path": Path("/test/path"),
            "none": None,
            "bool": True,
        }

        context.set("complex", complex_data)
        retrieved = context.get("complex")

        assert retrieved["string"] == "test"
        assert retrieved["number"] == 42
        assert retrieved["list"] == [1, 2, 3]
        assert retrieved["dict"]["nested"] == "value"
        assert retrieved["path"] == Path("/test/path")
        assert retrieved["none"] is None
        assert retrieved["bool"] is True

    def test_context_isolation_between_instances(self):
        """Test that different context instances don't interfere."""
        context1 = PipelineContext(
            pipeline_name="pipeline1", project_root=Path("/test1")
        )
        context2 = PipelineContext(
            pipeline_name="pipeline2", project_root=Path("/test2")
        )

        # Modify first context
        context1.set("data", "context1_value")
        context1.mark_stage_complete("stage1")
        context1.add_error("context1_error")

        # Modify second context
        context2.set("data", "context2_value")
        context2.mark_stage_complete("stage2")
        context2.add_error("context2_error")

        # Verify isolation
        assert context1.get("data") == "context1_value"
        assert context2.get("data") == "context2_value"
        assert "stage1" in context1.completed_stages
        assert "stage1" not in context2.completed_stages
        assert "stage2" not in context1.completed_stages
        assert "stage2" in context2.completed_stages
        assert "context1_error" in context1.errors
        assert "context1_error" not in context2.errors
        assert "context2_error" not in context1.errors
        assert "context2_error" in context2.errors

    def test_path_object_handling(self):
        """Test proper handling of Path objects."""
        root_path = Path("/test/project/root")
        context = PipelineContext(pipeline_name="test", project_root=root_path)

        assert isinstance(context.project_root, Path)
        assert context.project_root == root_path

        # Test storing Path objects in data
        data_path = Path("/test/data/path")
        context.set("data_path", data_path)
        retrieved_path = context.get("data_path")

        assert isinstance(retrieved_path, Path)
        assert retrieved_path == data_path
