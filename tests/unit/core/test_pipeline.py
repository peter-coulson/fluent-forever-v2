"""Unit tests for Pipeline execution orchestration."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.core.exceptions import StageNotFoundError
from src.core.stages import StageResult, StageStatus

from tests.fixtures.contexts import ContextBuilder, create_test_context
from tests.fixtures.pipelines import (
    MockPipeline,
    SuccessStage,
)


class TestPipeline:
    """Test suite for Pipeline execution orchestration."""

    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline for testing."""
        return MockPipeline("test_pipeline", ["stage1", "stage2", "stage3"])

    @pytest.fixture
    def sample_context(self):
        """Create a sample context for testing."""
        return create_test_context("test_pipeline", Path("/test/root"))

    def test_execute_stage_success(self, mock_pipeline, sample_context):
        """Test successful stage execution."""
        result = mock_pipeline.execute_stage("test_stage", sample_context)

        assert result.success
        assert result.status == StageStatus.SUCCESS
        assert "test_stage" in sample_context.completed_stages
        assert sample_context.get("test_stage_executed") is True

    def test_execute_stage_failure(self, mock_pipeline, sample_context):
        """Test stage execution failure handling."""
        result = mock_pipeline.execute_stage("failure_stage", sample_context)

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert "failure_stage" not in sample_context.completed_stages
        assert result.message == "Test failure"
        assert "Intentional test failure" in result.errors

    def test_execute_stage_nonexistent_stage(self, mock_pipeline, sample_context):
        """Test execution of non-existent stage."""
        result = mock_pipeline.execute_stage("nonexistent_stage", sample_context)

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert "Stage 'nonexistent_stage' not found" in result.message

    def test_execute_phase_success(self, mock_pipeline, sample_context):
        """Test successful phase execution."""
        results = mock_pipeline.execute_phase("test_phase", sample_context)

        assert len(results) == 1
        assert results[0].success
        assert "test_stage" in sample_context.completed_stages

    def test_execute_phase_partial_failure(self, mock_pipeline, sample_context):
        """Test phase execution with partial failure."""
        # Add a phase with both success and failure stages
        mock_pipeline._phases["mixed_phase"] = [
            "test_stage",
            "failure_stage",
            "dependency_stage",
        ]

        results = mock_pipeline.execute_phase("mixed_phase", sample_context)

        # Should stop after failure_stage fails
        assert len(results) == 2
        assert results[0].success  # test_stage
        assert not results[1].success  # failure_stage
        # dependency_stage should not be executed due to fail-fast

    def test_execute_phase_nonexistent_phase(self, mock_pipeline, sample_context):
        """Test execution of non-existent phase."""
        with pytest.raises(ValueError) as exc_info:
            mock_pipeline.execute_phase("nonexistent_phase", sample_context)

        assert "Phase 'nonexistent_phase' not found" in str(exc_info.value)
        assert "Available phases: " in str(exc_info.value)

    def test_execute_phase_fail_fast_behavior(self, mock_pipeline, sample_context):
        """Test fail-fast behavior in phase execution."""
        # Create a phase with failure in the middle
        mock_pipeline._phases["fail_fast_test"] = [
            "test_stage",
            "failure_stage",
            "dependency_stage",
        ]

        results = mock_pipeline.execute_phase("fail_fast_test", sample_context)

        # Should stop after first failure
        assert len(results) == 2
        assert results[0].success
        assert not results[1].success
        # Verify third stage was not executed
        assert "dependency_stage" not in sample_context.completed_stages

    def test_get_stage_valid_stage_name(self, mock_pipeline):
        """Test getting a valid stage instance."""
        stage = mock_pipeline.get_stage("test_stage")

        assert stage is not None
        assert stage.name == "test_stage"
        assert isinstance(stage, SuccessStage)

    def test_get_stage_invalid_stage_name(self, mock_pipeline):
        """Test getting an invalid stage instance."""
        with pytest.raises(StageNotFoundError) as exc_info:
            mock_pipeline.get_stage("invalid_stage")

        assert "Stage 'invalid_stage' not found" in str(exc_info.value)

    def test_get_phase_info_existing_phase(self, mock_pipeline):
        """Test getting information about an existing phase."""
        info = mock_pipeline.get_phase_info("test_phase")

        assert info["name"] == "test_phase"
        assert info["display_name"] == "Test Phase"
        assert info["stages"] == ["test_stage"]
        assert info["stage_count"] == 1

    def test_get_phase_info_nonexistent_phase(self, mock_pipeline):
        """Test getting information about a non-existent phase."""
        info = mock_pipeline.get_phase_info("nonexistent_phase")

        assert info == {}

    def test_validate_cli_args_success(self, mock_pipeline):
        """Test successful CLI argument validation."""
        args = Mock()
        args.invalid_arg = False

        errors = mock_pipeline.validate_cli_args(args)

        assert errors == []

    def test_validate_cli_args_with_errors(self, mock_pipeline):
        """Test CLI argument validation with errors."""
        args = Mock()
        args.invalid_arg = True

        errors = mock_pipeline.validate_cli_args(args)

        assert len(errors) == 1
        assert "Invalid argument provided" in errors[0]

    def test_populate_context_from_cli(self, mock_pipeline, sample_context):
        """Test populating context from CLI arguments."""
        args = Mock()
        args.test_data = "cli_value"

        mock_pipeline.populate_context_from_cli(sample_context, args)

        assert sample_context.get("cli_populated") is True
        assert sample_context.get("test_data") == "cli_value"

    def test_show_cli_execution_plan_dry_run(
        self, mock_pipeline, sample_context, capsys
    ):
        """Test showing CLI execution plan for dry run."""
        args = Mock()
        args.stage = "test_stage"

        mock_pipeline.show_cli_execution_plan(sample_context, args)

        captured = capsys.readouterr()
        assert "Dry run for pipeline 'test_pipeline'" in captured.out
        assert "Would execute stage: test_stage" in captured.out

    def test_stage_dependency_validation(self, mock_pipeline, sample_context):
        """Test stage dependency validation during execution."""
        # Try to execute dependency_stage without its dependency completed
        result = mock_pipeline.execute_stage("dependency_stage", sample_context)

        assert not result.success
        assert "Context validation failed" in result.message
        assert "Required dependency 'test_stage' not completed" in result.errors

    def test_context_accumulation_across_stages(self, mock_pipeline, sample_context):
        """Test that context accumulates data across stage executions."""
        # Execute multiple stages and verify context accumulation
        result1 = mock_pipeline.execute_stage("test_stage", sample_context)
        assert result1.success
        assert sample_context.get("test_stage_executed") is True

        # Mark test_stage as complete manually for dependency validation
        sample_context.mark_stage_complete("test_stage")

        result2 = mock_pipeline.execute_stage("dependency_stage", sample_context)
        assert result2.success
        assert sample_context.get("dependency_stage_executed") is True

        # Verify both stages are marked complete
        assert "test_stage" in sample_context.completed_stages
        assert "dependency_stage" in sample_context.completed_stages

    def test_get_stage_info_valid_stage(self, mock_pipeline):
        """Test getting stage information for valid stage."""
        info = mock_pipeline.get_stage_info("test_stage")

        assert info["name"] == "test_stage"
        assert info["display_name"] == "Test Success Stage"
        assert info["dependencies"] == []

    def test_get_stage_info_invalid_stage(self, mock_pipeline):
        """Test getting stage information for invalid stage."""
        info = mock_pipeline.get_stage_info("invalid_stage")

        assert info == {}

    def test_pipeline_properties(self, mock_pipeline):
        """Test pipeline property access."""
        assert mock_pipeline.name == "test_pipeline"
        assert mock_pipeline.display_name == "Test Pipeline (test_pipeline)"
        assert mock_pipeline.data_file == "test_data.json"
        assert mock_pipeline.anki_note_type == "Test Note Type"
        assert "stage1" in mock_pipeline.stages

    def test_get_description(self, mock_pipeline):
        """Test pipeline description generation."""
        description = mock_pipeline.get_description()

        expected = "Test Pipeline (test_pipeline) pipeline for test_data.json"
        assert description == expected

    @patch("src.core.pipeline.get_context_logger")
    def test_execute_stage_logging(self, mock_logger, mock_pipeline, sample_context):
        """Test that stage execution produces appropriate logs."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        mock_pipeline.execute_stage("test_stage", sample_context)

        # Verify get_context_logger was called (logging was attempted)
        assert mock_logger.called
        # The actual logging calls depend on the implementation

    @patch("src.core.pipeline.get_context_logger")
    def test_execute_phase_logging(self, mock_logger, mock_pipeline, sample_context):
        """Test that phase execution produces appropriate logs."""
        mock_logger_instance = Mock()
        mock_logger.return_value = mock_logger_instance

        mock_pipeline.execute_phase("test_phase", sample_context)

        # Verify get_context_logger was called (logging was attempted)
        assert mock_logger.called

    def test_context_validation_failure_handling(self, mock_pipeline):
        """Test handling of context validation failures."""
        # Create context missing required data
        context = create_test_context()

        result = mock_pipeline.execute_stage("context_dependent_stage", context)

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert "Context validation failed" in result.message
        assert "Missing required_data in context" in result.errors

    def test_context_validation_success_path(self, mock_pipeline):
        """Test successful context validation and execution."""
        # Create context with required data
        context = ContextBuilder().with_data("required_data", "test_value").build()

        result = mock_pipeline.execute_stage("context_dependent_stage", context)

        assert result.success
        assert context.get("processed_data") == "Processed: test_value"

    def test_exception_handling_in_stage_execution(self, mock_pipeline, sample_context):
        """Test exception handling during stage execution."""
        # Mock a stage that raises an exception
        with patch.object(mock_pipeline, "get_stage") as mock_get_stage:
            mock_stage = Mock()
            mock_stage.validate_context.return_value = []
            mock_stage.execute.side_effect = RuntimeError("Test exception")
            mock_get_stage.return_value = mock_stage

            result = mock_pipeline.execute_stage("test_stage", sample_context)

            assert not result.success
            assert "Unexpected error in stage 'test_stage'" in result.message

    def test_partial_success_in_phase_execution(self, mock_pipeline, sample_context):
        """Test phase execution continues with partial success results."""
        # Create a stage that returns partial success
        partial_stage = Mock()
        partial_stage.name = "partial_stage"
        partial_stage.validate_context.return_value = []
        partial_stage.execute.return_value = StageResult.partial(
            "Partially completed", {"processed": 5, "failed": 2}
        )

        with patch.object(mock_pipeline, "get_stage") as mock_get_stage:

            def get_stage_side_effect(stage_name):
                if stage_name == "partial_stage":
                    return partial_stage
                return SuccessStage()

            mock_get_stage.side_effect = get_stage_side_effect

            # Create phase with partial success stage
            mock_pipeline._phases["partial_phase"] = ["partial_stage", "test_stage"]

            results = mock_pipeline.execute_phase("partial_phase", sample_context)

            # Both stages should execute (partial doesn't stop execution)
            assert len(results) == 2
            assert results[0].status == StageStatus.PARTIAL
            assert results[1].status == StageStatus.SUCCESS
