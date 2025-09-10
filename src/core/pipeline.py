"""Abstract pipeline definition and base classes."""

from abc import ABC, abstractmethod
from typing import Any

from src.utils.logging_config import ICONS, get_context_logger, log_performance

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

    @log_performance("fluent_forever.core.pipeline")
    def execute_stage(self, stage_name: str, context: PipelineContext) -> StageResult:
        """Execute a specific stage with context."""
        logger = get_context_logger("core.pipeline", context.pipeline_name)

        logger.info(
            f"{ICONS['gear']} Executing stage '{stage_name}' in pipeline '{self.name}'"
        )

        try:
            # Before stage retrieval
            logger.debug(f"Retrieving stage '{stage_name}'...")
            stage = self.get_stage(stage_name)
            logger.debug(f"Stage '{stage_name}' retrieved successfully")

            pipeline_context = context

            # Validate context for this stage
            logger.debug("Validating context for stage execution...")
            validation_errors = stage.validate_context(pipeline_context)
            if validation_errors:
                logger.error(
                    f"{ICONS['cross']} Context validation failed for stage '{stage_name}': {validation_errors}"
                )
                return StageResult.failure(
                    f"Context validation failed for stage '{stage_name}'",
                    validation_errors,
                )

            logger.debug("Context validation passed")

            # Execute the stage
            logger.info(f"{ICONS['gear']} Starting stage '{stage_name}' execution...")
            result = stage.execute(pipeline_context)

            # Mark stage as complete if successful
            if result.status.value == "success":
                logger.info(
                    f"{ICONS['check']} Stage '{stage_name}' completed successfully"
                )
                pipeline_context.mark_stage_complete(stage_name)
            else:
                logger.error(
                    f"{ICONS['cross']} Stage '{stage_name}' failed: {result.message}"
                )

            return result

        except StageNotFoundError as e:
            logger.error(f"{ICONS['cross']} Stage '{stage_name}' not found: {str(e)}")
            return StageResult.failure(str(e))
        except Exception as e:
            logger.error(
                f"{ICONS['cross']} Unexpected error in stage '{stage_name}': {str(e)}"
            )
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

    @abstractmethod
    def validate_cli_args(self, args: Any) -> list[str]:
        """Validate CLI arguments for this pipeline.

        Args:
            args: CLI arguments

        Returns:
            List of validation error messages
        """
        pass

    @abstractmethod
    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        """Populate context from CLI arguments.

        Args:
            context: Pipeline context to populate
            args: CLI arguments
        """
        pass

    @abstractmethod
    def show_cli_execution_plan(self, context: PipelineContext, args: Any) -> None:
        """Show execution plan for dry run.

        Args:
            context: Pipeline context
            args: CLI arguments
        """
        pass
