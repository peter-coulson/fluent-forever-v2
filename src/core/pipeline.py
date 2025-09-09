"""Abstract pipeline definition and base classes."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Union

from .context import PipelineContext
from .exceptions import StageNotFoundError
from .stages import Stage, StageResult


class Pipeline(ABC):
    """Abstract base class for all card type pipelines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Pipeline identifier (e.g., 'vocabulary', 'conjugation')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable pipeline name."""
        pass

    @property
    @abstractmethod
    def stages(self) -> list[str]:
        """List of available stage names for this pipeline."""
        pass

    @abstractmethod
    def get_stage(self, stage_name: str) -> Stage:
        """Get a stage instance by name."""
        pass

    def execute_stage(self, stage_name: str, context: Union[dict[str, Any], PipelineContext]) -> StageResult:
        """Execute a specific stage with context."""
        try:
            stage = self.get_stage(stage_name)

            # Convert dictionary context to PipelineContext for backward compatibility
            if isinstance(context, dict):
                pipeline_context = PipelineContext(
                    pipeline_name=self.name, project_root=Path.cwd(), data=context
                )
            else:
                pipeline_context = context

            # Validate context for this stage
            validation_errors = stage.validate_context(pipeline_context)
            if validation_errors:
                return StageResult.failure(
                    f"Context validation failed for stage '{stage_name}'",
                    validation_errors,
                )

            # Execute the stage
            result = stage.execute(pipeline_context)

            # Mark stage as complete if successful
            if result.status.value == "success":
                pipeline_context.mark_stage_complete(stage_name)

            return result

        except StageNotFoundError as e:
            return StageResult.failure(str(e))
        except Exception as e:
            return StageResult.failure(
                f"Unexpected error in stage '{stage_name}': {str(e)}"
            )

    @property
    @abstractmethod
    def data_file(self) -> str:
        """Primary data file for this pipeline (e.g., 'vocabulary.json')."""
        pass

    @property
    @abstractmethod
    def anki_note_type(self) -> str:
        """Anki note type name for this pipeline."""
        pass

    def get_description(self) -> str:
        """Get a description of this pipeline."""
        return f"{self.display_name} pipeline for {self.data_file}"

    def get_stage_info(self, stage_name: str) -> dict[str, Any]:
        """Get information about a specific stage."""
        try:
            stage = self.get_stage(stage_name)
            return {
                "name": stage.name,
                "display_name": stage.display_name,
                "dependencies": stage.dependencies,
            }
        except StageNotFoundError:
            return {}
