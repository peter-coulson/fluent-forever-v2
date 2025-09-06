"""
Base Stage Classes

Common base implementations for typical stage patterns:
- File operations (load/save JSON)
- API interactions (external service calls)
- Data validation (structured validation)
"""

from .file_stage import FileLoadStage, FileSaveStage
from .api_stage import APIStage
from .validation_stage import ValidationStage

__all__ = [
    'FileLoadStage',
    'FileSaveStage',
    'APIStage', 
    'ValidationStage'
]