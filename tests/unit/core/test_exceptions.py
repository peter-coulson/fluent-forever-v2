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
