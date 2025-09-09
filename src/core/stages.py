"""Stage base classes and interfaces for pipeline execution."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.context import PipelineContext


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
    data: dict[str, Any]
    errors: list[str]

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key, None)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    @property
    def success(self) -> bool:
        """Check if the result represents a successful execution."""
        return self.status == StageStatus.SUCCESS

    @classmethod
    def success_result(
        cls, message: str, data: dict[str, Any] | None = None
    ) -> "StageResult":
        """Create a success result."""
        return cls(
            status=StageStatus.SUCCESS, message=message, data=data or {}, errors=[]
        )

    @classmethod
    def failure(cls, message: str, errors: list[str] | None = None) -> "StageResult":
        """Create a failure result."""
        return cls(
            status=StageStatus.FAILURE, message=message, data={}, errors=errors or []
        )

    @classmethod
    def partial(
        cls,
        message: str,
        data: dict[str, Any] | None = None,
        errors: list[str] | None = None,
    ) -> "StageResult":
        """Create a partial result."""
        return cls(
            status=StageStatus.PARTIAL,
            message=message,
            data=data or {},
            errors=errors or [],
        )

    @classmethod
    def skipped(cls, message: str) -> "StageResult":
        """Create a skipped result."""
        return cls(status=StageStatus.SKIPPED, message=message, data={}, errors=[])


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
    def execute(self, context: "PipelineContext") -> StageResult:
        """Execute this stage with the given context."""
        pass

    @property
    def dependencies(self) -> list[str]:
        """List of stage names that must complete before this stage."""
        return []

    def validate_context(self, context: "PipelineContext") -> list[str]:
        """Validate context has required data. Return list of errors."""
        return []
