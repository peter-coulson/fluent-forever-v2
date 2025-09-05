"""Core pipeline architecture components."""

from .pipeline import Pipeline
from .stages import Stage, StageResult, StageStatus
from .context import PipelineContext
from .registry import PipelineRegistry, get_pipeline_registry
from .exceptions import (
    PipelineError,
    PipelineNotFoundError,
    PipelineAlreadyRegisteredError,
    StageError,
    StageNotFoundError,
    ContextValidationError,
)

__all__ = [
    'Pipeline',
    'Stage',
    'StageResult', 
    'StageStatus',
    'PipelineContext',
    'PipelineRegistry',
    'get_pipeline_registry',
    'PipelineError',
    'PipelineNotFoundError',
    'PipelineAlreadyRegisteredError',
    'StageError',
    'StageNotFoundError',
    'ContextValidationError',
]