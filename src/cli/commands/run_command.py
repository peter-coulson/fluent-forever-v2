"""Run command implementation."""

from pathlib import Path
from typing import Any

from src.cli.utils.output import print_error, print_success, print_warning
from src.cli.utils.validation import validate_arguments
from src.core.config import Config
from src.core.context import PipelineContext
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry


class RunCommand:
    """Execute pipeline stages."""

    def __init__(
        self,
        pipeline_registry: PipelineRegistry,
        provider_registry: ProviderRegistry,
        project_root: Path,
        config: Config,
    ):
        """Initialize command.

        Args:
            pipeline_registry: Pipeline registry
            provider_registry: Provider registry
            project_root: Project root directory
            config: CLI configuration
        """
        self.pipeline_registry = pipeline_registry
        self.provider_registry = provider_registry
        self.project_root = project_root
        self.config = config

    def execute(self, args: Any) -> int:
        """Execute run command.

        Args:
            args: Command arguments

        Returns:
            Exit code
        """
        # Validate general CLI arguments
        validation_errors = validate_arguments("run", args)
        if validation_errors:
            for error in validation_errors:
                print_error(error)
            return 1

        # Get pipeline from registry
        try:
            pipeline = self.pipeline_registry.get(args.pipeline)
        except Exception as e:
            print_error(f"Pipeline '{args.pipeline}' not found: {e}")
            return 1

        # Pipeline-specific CLI argument validation (skip for dry-run)
        if not getattr(args, "dry_run", False):
            pipeline_errors = pipeline.validate_cli_args(args)
            if pipeline_errors:
                for error in pipeline_errors:
                    print_error(error)
                return 1

        # Create execution context
        context = self._create_context(args)

        # Let pipeline populate context from CLI arguments
        pipeline.populate_context_from_cli(context, args)

        # Handle dry-run
        if getattr(args, "dry_run", False):
            print_warning(
                f"DRY RUN: Would execute stage '{args.stage}' on pipeline '{args.pipeline}'"
            )
            pipeline.show_cli_execution_plan(context, args)
            return 0

        # Execute stage
        return self._execute_pipeline_stage(pipeline, args.stage, context)

    def _create_context(self, args: Any) -> PipelineContext:
        """Create pipeline context with providers and basic configuration.

        Args:
            args: Command arguments

        Returns:
            Pipeline context
        """
        context = PipelineContext(
            pipeline_name=args.pipeline,
            project_root=self.project_root,
            config=self.config.to_dict(),
            args=vars(args),
        )

        # Add providers to context
        context.set(
            "providers",
            {
                "data": self.provider_registry.get_data_provider("default"),
                "media": self.provider_registry.get_media_provider("default"),
                "sync": self.provider_registry.get_sync_provider("default"),
            },
        )

        return context

    def _execute_pipeline_stage(
        self, pipeline: Pipeline, stage_name: str, context: PipelineContext
    ) -> int:
        """Execute pipeline stage and handle results.

        Args:
            pipeline: Pipeline instance
            stage_name: Stage to execute
            context: Pipeline context

        Returns:
            Exit code
        """
        try:
            result = pipeline.execute_stage(stage_name, context)

            if result.status.value == "success":
                print_success(result.message)
                return 0
            elif result.status.value == "partial":
                print_warning(f"Partial success: {result.message}")
                if result.errors:
                    print("Errors encountered:")
                    for error in result.errors:
                        print(f"  - {error}")
                return 0
            else:
                print_error(result.message)
                if result.errors:
                    print("Errors:")
                    for error in result.errors:
                        print(f"  - {error}")
                return 1

        except Exception as e:
            print_error(f"Error executing stage '{stage_name}': {e}")
            return 1
