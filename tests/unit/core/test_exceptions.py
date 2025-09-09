"""Unit tests for core exceptions."""

import pytest
from src.core.exceptions import (
    ContextValidationError,
    PipelineAlreadyRegisteredError,
    PipelineError,
    PipelineNotFoundError,
    StageError,
    StageNotFoundError,
)


class TestPipelineExceptions:
    """Test cases for pipeline exception hierarchy."""

    def test_base_pipeline_error(self):
        """Test base PipelineError."""
        error = PipelineError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_pipeline_not_found_error(self):
        """Test PipelineNotFoundError."""
        error = PipelineNotFoundError("Pipeline not found")
        assert str(error) == "Pipeline not found"
        assert isinstance(error, PipelineError)

    def test_pipeline_already_registered_error(self):
        """Test PipelineAlreadyRegisteredError."""
        error = PipelineAlreadyRegisteredError("Already registered")
        assert str(error) == "Already registered"
        assert isinstance(error, PipelineError)

    def test_stage_error(self):
        """Test StageError."""
        error = StageError("Stage error")
        assert str(error) == "Stage error"
        assert isinstance(error, PipelineError)

    def test_stage_not_found_error(self):
        """Test StageNotFoundError."""
        error = StageNotFoundError("Stage not found")
        assert str(error) == "Stage not found"
        assert isinstance(error, StageError)
        assert isinstance(error, PipelineError)

    def test_context_validation_error(self):
        """Test ContextValidationError."""
        error = ContextValidationError("Context invalid")
        assert str(error) == "Context invalid"
        assert isinstance(error, PipelineError)

    def test_exception_raising(self):
        """Test exceptions can be raised and caught."""
        with pytest.raises(PipelineNotFoundError):
            raise PipelineNotFoundError("Test")

        with pytest.raises(PipelineError):
            raise StageNotFoundError("Test")  # Should be caught as base class

    def test_exception_context_preservation_through_pipeline(self):
        """Test exception context and messages are preserved through pipeline layers."""
        from pathlib import Path

        from src.core.context import PipelineContext
        from src.core.pipeline import Pipeline
        from src.core.stages import Stage, StageResult

        class ContextPreservingStage(Stage):
            def __init__(self, name, error_to_raise=None):
                self._name = name
                self._error_to_raise = error_to_raise

            @property
            def name(self) -> str:
                return self._name

            @property
            def display_name(self) -> str:
                return f"Context Preserving {self._name}"

            def execute(self, context):
                if self._error_to_raise:
                    raise self._error_to_raise
                return StageResult.success_result("Success")

        class TestPipeline(Pipeline):
            def __init__(self):
                self._stages = {
                    "failing_stage": ContextPreservingStage(
                        "failing", StageNotFoundError("Original context message")
                    )
                }

            @property
            def name(self) -> str:
                return "test_pipeline"

            @property
            def display_name(self) -> str:
                return "Test Pipeline"

            @property
            def stages(self) -> list:
                return list(self._stages.keys())

            def get_stage(self, stage_name: str):
                if stage_name not in self._stages:
                    raise StageNotFoundError(
                        f"Stage '{stage_name}' not found in pipeline"
                    )
                return self._stages[stage_name]

            @property
            def data_file(self) -> str:
                return "test.json"

            @property
            def anki_note_type(self) -> str:
                return "Test"

            def validate_cli_args(self, args):
                return []

            def populate_context_from_cli(self, context, args):
                pass

            def show_cli_execution_plan(self, context, args):
                pass

        pipeline = TestPipeline()
        context = PipelineContext("test", Path("/tmp"))

        # Test that exception context is preserved through pipeline execution
        result = pipeline.execute_stage("failing_stage", context)

        # The pipeline should catch the exception and convert to failure result
        assert result.status.value == "failure"

        # The original exception message should be preserved in some form
        assert "Original context message" in str(
            result.message
        ) or "StageNotFoundError" in str(result.message)

        # Test with ContextValidationError
        validation_error = ContextValidationError(
            "Validation failed: missing required field 'input'"
        )
        pipeline._stages["validation_stage"] = ContextPreservingStage(
            "validation", validation_error
        )

        result2 = pipeline.execute_stage("validation_stage", context)
        assert result2.status.value == "failure"
        assert "Validation failed" in str(
            result2.message
        ) or "ContextValidationError" in str(result2.message)

        # Test with PipelineAlreadyRegisteredError
        registry_error = PipelineAlreadyRegisteredError(
            "Pipeline 'test' is already registered"
        )
        pipeline._stages["registry_stage"] = ContextPreservingStage(
            "registry", registry_error
        )

        result3 = pipeline.execute_stage("registry_stage", context)
        assert result3.status.value == "failure"
        assert "already registered" in str(
            result3.message
        ).lower() or "PipelineAlreadyRegisteredError" in str(result3.message)
