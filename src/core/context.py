"""Pipeline execution context for data flow between stages."""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PipelineContext:
    """Execution context passed between pipeline stages."""
    
    # Core context
    pipeline_name: str
    project_root: Path
    
    # Stage data (modified by stages during execution)
    data: Dict[str, Any] = field(default_factory=dict)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    completed_stages: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # Command arguments
    args: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get data value with default."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set data value."""
        self.data[key] = value
    
    def add_error(self, error: str) -> None:
        """Add error to context."""
        self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if context has errors."""
        return len(self.errors) > 0
    
    def mark_stage_complete(self, stage_name: str) -> None:
        """Mark a stage as completed."""
        if stage_name not in self.completed_stages:
            self.completed_stages.append(stage_name)