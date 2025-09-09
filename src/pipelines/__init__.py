"""Pipeline implementations for different card types."""

# Import registry for future use
from src.core.registry import get_pipeline_registry


def register_all_pipelines():
    """Register all available pipelines with the global registry."""
    # No pipelines currently implemented
    # This function is kept for future pipeline additions
    pass


# Auto-register when module is imported (currently no-op)
register_all_pipelines()

__all__ = ["register_all_pipelines"]
