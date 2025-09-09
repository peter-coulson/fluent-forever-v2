"""Unit tests for core exceptions."""

import pytest

from core.exceptions import (
    ContextValidationError,
    PipelineAlreadyRegisteredError,
    PipelineError,
    PipelineNotFoundError,
    StageError,
    StageNotFoundError,
)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy."""

    def test_pipeline_error_base(self):
        """Test PipelineError as base exception."""
        error = PipelineError("Base pipeline error")
        assert str(error) == "Base pipeline error"
        assert isinstance(error, Exception)

    def test_pipeline_not_found_error(self):
        """Test PipelineNotFoundError inheritance."""
        error = PipelineNotFoundError("Pipeline not found")
        assert str(error) == "Pipeline not found"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_pipeline_already_registered_error(self):
        """Test PipelineAlreadyRegisteredError inheritance."""
        error = PipelineAlreadyRegisteredError("Pipeline already registered")
        assert str(error) == "Pipeline already registered"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_stage_error_inheritance(self):
        """Test StageError inheritance."""
        error = StageError("Stage error")
        assert str(error) == "Stage error"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_stage_not_found_error(self):
        """Test StageNotFoundError inheritance."""
        error = StageNotFoundError("Stage not found")
        assert str(error) == "Stage not found"
        assert isinstance(error, StageError)
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_context_validation_error(self):
        """Test ContextValidationError inheritance."""
        error = ContextValidationError("Context validation failed")
        assert str(error) == "Context validation failed"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_exception_with_args(self):
        """Test exceptions with multiple arguments."""
        error = PipelineError("Error message", "Additional info")
        # The exact string representation may vary by Python version
        assert "Error message" in str(error)

    def test_exception_raising_and_catching(self):
        """Test raising and catching exceptions."""
        # Test raising and catching specific exception
        with pytest.raises(PipelineNotFoundError) as exc_info:
            raise PipelineNotFoundError("Test pipeline not found")

        assert "Test pipeline not found" in str(exc_info.value)

        # Test catching as base exception
        with pytest.raises(PipelineError):
            raise PipelineNotFoundError("Test pipeline not found")

        # Test catching as generic exception
        with pytest.raises(PipelineNotFoundError):
            raise PipelineNotFoundError("Test pipeline not found")

    def test_stage_error_hierarchy(self):
        """Test stage error hierarchy specifically."""
        # StageNotFoundError should be caught as StageError
        with pytest.raises(StageError):
            raise StageNotFoundError("Stage not found")

        # StageError should be caught as PipelineError
        with pytest.raises(PipelineError):
            raise StageError("Stage error")
