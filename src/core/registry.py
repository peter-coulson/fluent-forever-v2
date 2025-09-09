"""Pipeline registry system for managing pipeline implementations."""

from typing import Any

from .exceptions import PipelineAlreadyRegisteredError, PipelineNotFoundError
from .pipeline import Pipeline


class PipelineRegistry:
    """Registry for managing pipeline implementations."""

    def __init__(self) -> None:
        self._pipelines: dict[str, Pipeline] = {}

    def register(self, pipeline: Pipeline) -> None:
        """Register a pipeline."""
        if pipeline.name in self._pipelines:
            raise PipelineAlreadyRegisteredError(
                f"Pipeline '{pipeline.name}' already registered"
            )

        self._pipelines[pipeline.name] = pipeline

    def get(self, name: str) -> Pipeline:
        """Get pipeline by name."""
        if name not in self._pipelines:
            raise PipelineNotFoundError(f"Pipeline '{name}' not found")

        return self._pipelines[name]

    def list_pipelines(self) -> list[str]:
        """List all registered pipeline names."""
        return list(self._pipelines.keys())

    def has_pipeline(self, name: str) -> bool:
        """Check if pipeline is registered."""
        return name in self._pipelines

    def get_pipeline_info(self, name: str) -> dict[str, Any]:
        """Get information about a pipeline."""
        if not self.has_pipeline(name):
            raise PipelineNotFoundError(f"Pipeline '{name}' not found")

        pipeline = self._pipelines[name]
        return {
            "name": pipeline.name,
            "display_name": pipeline.display_name,
            "description": pipeline.get_description(),
            "stages": pipeline.stages,
            "data_file": pipeline.data_file,
            "anki_note_type": pipeline.anki_note_type,
        }

    def get_all_pipeline_info(self) -> dict[str, dict[str, Any]]:
        """Get information about all registered pipelines."""
        return {name: self.get_pipeline_info(name) for name in self.list_pipelines()}


# Global registry instance
_global_registry = PipelineRegistry()


def get_pipeline_registry() -> PipelineRegistry:
    """Get the global pipeline registry."""
    return _global_registry
