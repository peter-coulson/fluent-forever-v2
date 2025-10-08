"""Unit tests for exception hierarchy smoke tests."""


from src.core.exceptions import (
    ContextValidationError,
    PipelineAlreadyRegisteredError,
    PipelineError,
    PipelineNotFoundError,
    StageError,
    StageNotFoundError,
)


class TestExceptions:
    """Test exception hierarchy basic functionality."""

    def test_pipeline_error_instantiation(self):
        """Test PipelineError can be instantiated with message."""
        error = PipelineError("Test pipeline error")
        assert str(error) == "Test pipeline error"
        assert isinstance(error, Exception)

    def test_stage_error_instantiation(self):
        """Test StageError can be instantiated with message."""
        error = StageError("Test stage error")
        assert str(error) == "Test stage error"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_context_error_instantiation(self):
        """Test ContextValidationError can be instantiated with message."""
        error = ContextValidationError("Test context error")
        assert str(error) == "Test context error"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_stage_not_found_error_instantiation(self):
        """Test StageNotFoundError can be instantiated with message."""
        error = StageNotFoundError("Test stage not found")
        assert str(error) == "Test stage not found"
        assert isinstance(error, StageError)
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_pipeline_not_found_error_instantiation(self):
        """Test PipelineNotFoundError can be instantiated with message."""
        error = PipelineNotFoundError("Test pipeline not found")
        assert str(error) == "Test pipeline not found"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_pipeline_already_registered_error_instantiation(self):
        """Test PipelineAlreadyRegisteredError can be instantiated with message."""
        error = PipelineAlreadyRegisteredError("Test pipeline already registered")
        assert str(error) == "Test pipeline already registered"
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_exception_message_formatting(self):
        """Test exception message formatting works correctly."""
        message = "Custom error message with context"

        pipeline_error = PipelineError(message)
        stage_error = StageError(message)
        context_error = ContextValidationError(message)

        assert str(pipeline_error) == message
        assert str(stage_error) == message
        assert str(context_error) == message

    def test_exception_inheritance_hierarchy(self):
        """Test exception inheritance hierarchy is correct."""
        # Test that all specific errors inherit from PipelineError
        stage_error = StageError("test")
        context_error = ContextValidationError("test")
        stage_not_found = StageNotFoundError("test")
        pipeline_not_found = PipelineNotFoundError("test")
        pipeline_already_registered = PipelineAlreadyRegisteredError("test")

        # All should inherit from PipelineError
        assert isinstance(stage_error, PipelineError)
        assert isinstance(context_error, PipelineError)
        assert isinstance(stage_not_found, PipelineError)
        assert isinstance(pipeline_not_found, PipelineError)
        assert isinstance(pipeline_already_registered, PipelineError)

        # StageNotFoundError should inherit from StageError
        assert isinstance(stage_not_found, StageError)

        # All should inherit from base Exception
        assert isinstance(stage_error, Exception)
        assert isinstance(context_error, Exception)
        assert isinstance(stage_not_found, Exception)
        assert isinstance(pipeline_not_found, Exception)
        assert isinstance(pipeline_already_registered, Exception)
