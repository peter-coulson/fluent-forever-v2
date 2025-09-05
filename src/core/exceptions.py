"""Core exception hierarchy for pipeline system."""


class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


class PipelineNotFoundError(PipelineError):
    """Pipeline not found in registry."""
    pass


class PipelineAlreadyRegisteredError(PipelineError):
    """Pipeline already registered."""
    pass


class StageError(PipelineError):
    """Stage execution error."""
    pass


class StageNotFoundError(StageError):
    """Stage not found in pipeline."""
    pass


class ContextValidationError(PipelineError):
    """Pipeline context validation error."""
    pass