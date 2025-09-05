"""Stage base classes and interfaces for pipeline execution."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from dataclasses import dataclass
from enum import Enum


class StageStatus(Enum):
    """Status of stage execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of stage execution."""
    status: StageStatus
    message: str
    data: Dict[str, Any]
    errors: List[str]
    
    def __contains__(self, key: str) -> bool:
        """Support 'in' operator for backward compatibility."""
        if key == 'status':
            return True
        return hasattr(self, key)
    
    def __getitem__(self, key: str) -> Any:
        """Support dict-like access for backward compatibility."""
        if key == 'status':
            return self.status.value
        return getattr(self, key, None)
    
    @classmethod
    def success(cls, message: str, data: Dict[str, Any] = None) -> 'StageResult':
        """Create a success result."""
        return cls(
            status=StageStatus.SUCCESS,
            message=message,
            data=data or {},
            errors=[]
        )
    
    @classmethod
    def failure(cls, message: str, errors: List[str] = None) -> 'StageResult':
        """Create a failure result."""
        return cls(
            status=StageStatus.FAILURE,
            message=message,
            data={},
            errors=errors or []
        )
    
    @classmethod
    def partial(cls, message: str, data: Dict[str, Any] = None, errors: List[str] = None) -> 'StageResult':
        """Create a partial result."""
        return cls(
            status=StageStatus.PARTIAL,
            message=message,
            data=data or {},
            errors=errors or []
        )
    
    @classmethod
    def skipped(cls, message: str) -> 'StageResult':
        """Create a skipped result."""
        return cls(
            status=StageStatus.SKIPPED,
            message=message,
            data={},
            errors=[]
        )


class Stage(ABC):
    """Abstract base class for pipeline stages."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Stage identifier."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable stage name."""
        pass
    
    @abstractmethod
    def execute(self, context: 'PipelineContext') -> StageResult:
        """Execute this stage with the given context."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """List of stage names that must complete before this stage."""
        return []
    
    def validate_context(self, context: 'PipelineContext') -> List[str]:
        """Validate context has required data. Return list of errors."""
        return []