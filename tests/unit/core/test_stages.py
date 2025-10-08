"""Unit tests for Stage framework and validation."""

import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.core.context import PipelineContext
from src.core.stages import Stage, StageResult, StageStatus

from tests.fixtures.contexts import create_test_context


class MockStageImpl(Stage):
    """Test stage implementation for framework testing."""

    def __init__(self, name="test_stage", should_fail=False, validation_errors=None):
        super().__init__()
        self._name = name
        self._should_fail = should_fail
        self._validation_errors = validation_errors or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Test Stage ({self._name})"

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        if self._should_fail:
            return StageResult.failure("Test stage failed", ["Intentional failure"])

        context.set(f"{self._name}_executed", True)
        return StageResult.success_result("Test stage completed successfully")

    def validate_context(self, context: PipelineContext) -> list[str]:
        return self._validation_errors.copy()


class MockDependentStage(MockStageImpl):
    """Test stage with dependencies."""

    @property
    def dependencies(self) -> list[str]:
        return ["dependency1", "dependency2"]

    def validate_context(self, context: PipelineContext) -> list[str]:
        errors = super().validate_context(context)

        for dep in self.dependencies:
            if dep not in context.completed_stages:
                errors.append(f"Required dependency '{dep}' not completed")

        return errors


class MockSlowStage(MockStageImpl):
    """Test stage that takes time to execute for performance testing."""

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        time.sleep(0.1)  # Small delay for testing timing
        return super()._execute_impl(context)


class TestStage:
    """Test suite for Stage execution framework."""

    @pytest.fixture
    def sample_context(self):
        """Create a sample context for testing."""
        return create_test_context("test_pipeline", Path("/test/root"))

    @pytest.fixture
    def success_stage(self):
        """Create a stage that succeeds."""
        return MockStageImpl("success_stage", should_fail=False)

    @pytest.fixture
    def failure_stage(self):
        """Create a stage that fails."""
        return MockStageImpl("failure_stage", should_fail=True)

    @pytest.fixture
    def validation_error_stage(self):
        """Create a stage with validation errors."""
        return MockStageImpl(
            "validation_stage", validation_errors=["Missing required field"]
        )

    def test_execute_success_path(self, success_stage, sample_context):
        """Test successful stage execution path."""
        result = success_stage.execute(sample_context)

        assert result.success
        assert result.status == StageStatus.SUCCESS
        assert result.message == "Test stage completed successfully"
        assert result.errors == []
        assert sample_context.get("success_stage_executed") is True

    def test_execute_failure_path(self, failure_stage, sample_context):
        """Test failure stage execution path."""
        result = failure_stage.execute(sample_context)

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert result.message == "Test stage failed"
        assert "Intentional failure" in result.errors

    def test_execute_context_validation_failure(
        self, validation_error_stage, sample_context
    ):
        """Test execution with context validation failure."""
        result = validation_error_stage.execute(sample_context)

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert result.message == "Context validation failed"
        assert "Missing required field" in result.errors

    def test_execute_performance_timing(self, sample_context):
        """Test that execution timing is captured."""
        slow_stage = MockSlowStage("slow_stage")

        start_time = time.time()
        result = slow_stage.execute(sample_context)
        end_time = time.time()

        duration = end_time - start_time
        assert result.success
        assert duration >= 0.1  # Should take at least 0.1 seconds

    @patch("src.utils.logging_config.get_logger")
    def test_execute_logging_integration(
        self, mock_get_logger, success_stage, sample_context
    ):
        """Test logging integration during stage execution."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Create new stage to get fresh logger
        stage = MockStageImpl("logging_test")
        stage.logger = mock_logger

        result = stage.execute(sample_context)

        assert result.success
        # Verify info logging was called for start and completion
        assert mock_logger.info.call_count >= 2

    def test_validate_context_success(self, success_stage, sample_context):
        """Test successful context validation."""
        errors = success_stage.validate_context(sample_context)

        assert errors == []

    def test_validate_context_with_errors(self, validation_error_stage, sample_context):
        """Test context validation with errors."""
        errors = validation_error_stage.validate_context(sample_context)

        assert len(errors) == 1
        assert "Missing required field" in errors[0]

    def test_dependencies_property_access(self):
        """Test dependencies property access."""
        dependent_stage = MockDependentStage("dependent_stage")

        assert dependent_stage.dependencies == ["dependency1", "dependency2"]

    def test_stage_result_success_creation(self):
        """Test successful StageResult creation."""
        result = StageResult.success_result("Success message", {"key": "value"})

        assert result.success
        assert result.status == StageStatus.SUCCESS
        assert result.message == "Success message"
        assert result.data == {"key": "value"}
        assert result.errors == []

    def test_stage_result_failure_creation(self):
        """Test failure StageResult creation."""
        result = StageResult.failure("Failure message", ["Error 1", "Error 2"])

        assert not result.success
        assert result.status == StageStatus.FAILURE
        assert result.message == "Failure message"
        assert result.data == {}
        assert result.errors == ["Error 1", "Error 2"]

    def test_stage_result_partial_creation(self):
        """Test partial StageResult creation."""
        result = StageResult.partial("Partial message", {"processed": 5}, ["Warning 1"])

        assert not result.success  # Partial is not considered success
        assert result.status == StageStatus.PARTIAL
        assert result.message == "Partial message"
        assert result.data == {"processed": 5}
        assert result.errors == ["Warning 1"]

    def test_stage_result_skipped_creation(self):
        """Test skipped StageResult creation."""
        result = StageResult.skipped("Skipped message")

        assert not result.success  # Skipped is not considered success
        assert result.status == StageStatus.SKIPPED
        assert result.message == "Skipped message"
        assert result.data == {}
        assert result.errors == []

    def test_context_update_on_success(self, success_stage, sample_context):
        """Test context update during successful execution."""
        initial_data_count = len(sample_context.data)

        result = success_stage.execute(sample_context)

        assert result.success
        assert len(sample_context.data) > initial_data_count
        assert sample_context.get("success_stage_executed") is True

    def test_context_update_on_failure(self, failure_stage, sample_context):
        """Test context state during failed execution."""
        initial_data_count = len(sample_context.data)

        result = failure_stage.execute(sample_context)

        assert not result.success
        # Context should not be updated on failure
        assert len(sample_context.data) == initial_data_count

    @patch("src.core.stages.get_logger")
    def test_logger_creation_and_usage(self, mock_get_logger):
        """Test logger creation and usage in stage."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        stage = MockStageImpl("logger_test")

        # Verify logger was created with correct name
        mock_get_logger.assert_called_once_with("stages.mockstageimpl")
        assert stage.logger == mock_logger

    def test_execution_wrapper_error_handling(self, sample_context):
        """Test execution wrapper handles implementation errors."""

        class ErrorStage(MockStageImpl):
            def _execute_impl(self, context):
                raise RuntimeError("Implementation error")

        error_stage = ErrorStage("error_stage")

        with pytest.raises(RuntimeError):
            error_stage.execute(sample_context)

    def test_stage_result_dict_like_access(self):
        """Test StageResult dict-like access methods."""
        result = StageResult.success_result("Test", {"key": "value"})

        # Test __contains__
        assert "status" in result
        assert "nonexistent" not in result

        # Test __getitem__
        assert result["status"] == StageStatus.SUCCESS
        assert result["nonexistent"] is None

        # Test get method
        assert result.get("message") == "Test"
        assert result.get("nonexistent", "default") == "default"

    def test_dependency_validation_in_context(self, sample_context):
        """Test dependency validation with context state."""
        dependent_stage = MockDependentStage("dependent_stage")

        # Without dependencies completed
        errors = dependent_stage.validate_context(sample_context)
        assert len(errors) == 2
        assert "Required dependency 'dependency1' not completed" in errors
        assert "Required dependency 'dependency2' not completed" in errors

        # With dependencies completed
        sample_context.mark_stage_complete("dependency1")
        sample_context.mark_stage_complete("dependency2")

        errors = dependent_stage.validate_context(sample_context)
        assert errors == []

    def test_stage_result_properties(self):
        """Test StageResult property access."""
        success_result = StageResult.success_result("Success")
        failure_result = StageResult.failure("Failure")
        partial_result = StageResult.partial("Partial")
        skipped_result = StageResult.skipped("Skipped")

        assert success_result.success is True
        assert failure_result.success is False
        assert partial_result.success is False
        assert skipped_result.success is False

    @patch("src.utils.logging_config.get_logger")
    def test_error_logging_on_failure(
        self, mock_get_logger, failure_stage, sample_context
    ):
        """Test error logging during stage failure."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        failure_stage.logger = mock_logger

        result = failure_stage.execute(sample_context)

        assert not result.success
        # Verify error was logged
        mock_logger.error.assert_called()

    def test_validation_errors_prevent_execution(
        self, validation_error_stage, sample_context
    ):
        """Test that validation errors prevent stage execution."""
        # Mock the _execute_impl to verify it's not called
        with patch.object(validation_error_stage, "_execute_impl") as mock_execute:
            result = validation_error_stage.execute(sample_context)

            assert not result.success
            assert result.message == "Context validation failed"
            # _execute_impl should not be called due to validation failure
            mock_execute.assert_not_called()

    def test_stage_execution_with_timing_on_error(self, sample_context):
        """Test timing is captured even when stage execution fails."""

        class TimedErrorStage(MockStageImpl):
            def _execute_impl(self, context):
                time.sleep(0.05)  # Small delay
                raise RuntimeError("Timed error")

        error_stage = TimedErrorStage("timed_error")

        start_time = time.time()
        with pytest.raises(RuntimeError):
            error_stage.execute(sample_context)
        end_time = time.time()

        duration = end_time - start_time
        assert duration >= 0.05  # Should have captured the delay

    def test_stage_display_name_property(self):
        """Test stage display name property."""
        stage = MockStageImpl("custom_stage")

        assert stage.display_name == "Test Stage (custom_stage)"

    def test_stage_name_property(self):
        """Test stage name property."""
        stage = MockStageImpl("custom_name")

        assert stage.name == "custom_name"

    def test_default_dependencies_empty(self, success_stage):
        """Test that default dependencies list is empty."""
        assert success_stage.dependencies == []

    def test_default_validate_context_no_errors(self, success_stage, sample_context):
        """Test that default validate_context returns no errors."""
        errors = success_stage.validate_context(sample_context)

        assert errors == []

    @patch("src.utils.logging_config.get_logger")
    def test_validation_error_logging(
        self, mock_get_logger, validation_error_stage, sample_context
    ):
        """Test logging of validation errors."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        validation_error_stage.logger = mock_logger

        result = validation_error_stage.execute(sample_context)

        assert not result.success
        # Verify validation error was logged
        mock_logger.error.assert_called()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "validation failed" in error_call_args.lower()

    def test_stage_result_status_enum_values(self):
        """Test StageStatus enum values are correct."""
        assert StageStatus.SUCCESS.value == "success"
        assert StageStatus.FAILURE.value == "failure"
        assert StageStatus.PARTIAL.value == "partial"
        assert StageStatus.SKIPPED.value == "skipped"
