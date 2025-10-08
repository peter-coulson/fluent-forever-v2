"""Pipeline execution context for data flow between stages."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.utils.logging_config import ICONS, get_context_logger


@dataclass
class PipelineContext:
    """Execution context passed between pipeline stages."""

    # Core context
    pipeline_name: str
    project_root: Path

    # Stage data (modified by stages during execution)
    data: dict[str, Any] = field(default_factory=dict)

    # Configuration
    config: dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    completed_stages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # Command arguments
    args: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.logger = get_context_logger("core.context", self.pipeline_name)
        self.logger.debug(f"Created context for pipeline '{self.pipeline_name}'")

    def get(self, key: str, default: Any = None) -> Any:
        """Get data value with default."""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set data value."""
        self.logger.debug(f"Setting context data: {key}")
        self.data[key] = value

    def add_error(self, error: str) -> None:
        """Add error to context."""
        self.logger.error(f"{ICONS['cross']} Context error: {error}")
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if context has errors."""
        return len(self.errors) > 0

    def mark_stage_complete(self, stage_name: str) -> None:
        """Mark a stage as completed."""
        self.logger.info(f"{ICONS['check']} Marking stage '{stage_name}' as complete")
        if stage_name not in self.completed_stages:
            self.completed_stages.append(stage_name)
